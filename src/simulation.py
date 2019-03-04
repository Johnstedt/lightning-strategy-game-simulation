"""
python3 -m pip install -U matplotlib
python3 -m pip install networkx pylightning
"""
import networkx as nx
import json
import sys
import numpy
import random

from attachment_policies import AttachmentPolicies
import plot
from heapq import heappush, heappop
from itertools import count


def dijkstra_multisource(G, source, target=None, weight=None):
	"""Uses Dijkstra's algorithm to find shortest weighted paths

	THIS METHOD IS MODIFIED TO HANDLE LIQUIDITY CONSTRAINS

	Parameters
	----------
	G : NetworkX graph

	source : non-empty iterable of nodes
		Starting nodes for paths. If this is just an iterable containing
		a single node, then all paths computed by this function will
		start from that node. If there are two or more nodes in this
		iterable, the computed paths may begin from any one of the start
		nodes.

	weight: function
		Function with (u, v, data) input that returns that edges weight

	pred: dict of lists, optional(default=None)
		dict to store a list of predecessors keyed by that node
		If None, predecessors are not stored.

	paths: dict, optional (default=None)
		dict to store the path list from source to each node, keyed by node.
		If None, paths are not stored.

	target : node label, optional
		Ending node for path. Search is halted when target is found.

	cutoff : integer or float, optional
		Depth to stop the search. Only return paths with length <= cutoff.

	Returns
	-------
	distance : dictionary
		A mapping from node to shortest distance to that node from one
		of the source nodes.

	Raises
	------
	NodeNotFound
		If any of `sources` is not in `G`.

	Notes
	-----
	The optional predecessor and path dictionaries can be accessed by
	the caller through the original pred and paths objects passed
	as arguments. No need to explicitly return pred or paths.

	"""
	weight = _weight_function(G, weight)
	cutoff = None
	pred = None
	sources = [source]
	paths = {source: [source] for source in sources}  # dictionary of paths

	G_succ = G._succ if G.is_directed() else G._adj

	push = heappush
	pop = heappop
	dist = {}  # dictionary of final distances
	seen = {}
	# fringe is heapq with 3-tuples (distance,c,node)
	# use the count c to avoid comparing nodes (may not be able to)
	c = count()
	fringe = []
	for source in sources:
		if source not in G:
			raise nx.NodeNotFound("Source {} not in G".format(source))
		seen[source] = 0
		push(fringe, (0, next(c), source))
	while fringe:
		(d, _, v) = pop(fringe)
		if v in dist:
			continue  # already searched this node.
		dist[v] = d
		if v == target:
			break
		for u, e in G_succ[v].items():
			cost = weight(v, u, e)
			if cost is None:
				continue
			vu_dist = dist[v] + cost
			if cutoff is not None:
				if vu_dist > cutoff:
					continue
			if u in dist:
				if vu_dist < dist[u]:
					raise ValueError('Contradictory paths found:',
									 'negative weights?')
			elif u not in seen or vu_dist < seen[u]:
				seen[u] = vu_dist
				push(fringe, (vu_dist, next(c), u))
				if paths is not None:
					paths[u] = paths[v] + [u]
				if pred is not None:
					pred[u] = [v]
			elif vu_dist == seen[u]:
				if pred is not None:
					pred[u].append(v)

	# The optional predecessor and path dictionaries can be accessed
	# by the caller via the pred and paths objects passed as arguments.
	(length, path) = dist
	return path


def _weight_function(G, weight):
	"""Returns a function that returns the weight of an edge.

	The returned function is specifically suitable for input to
	functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

	Parameters
	----------
	G : NetworkX graph.

	weight : string or function
		If it is callable, `weight` itself is returned. If it is a string,
		it is assumed to be the name of the edge attribute that represents
		the weight of an edge. In that case, a function is returned that
		gets the edge weight according to the specified edge attribute.

	Returns
	-------
	function
		This function returns a callable that accepts exactly three inputs:
		a node, an node adjacent to the first one, and the edge attribute
		dictionary for the eedge joining those nodes. That function returns
		a number representing the weight of an edge.

	If `G` is a multigraph, and `weight` is not callable, the
	minimum edge weight over all parallel edges is returned. If any edge
	does not have an attribute with key `weight`, it is assumed to
	have weight one.

	"""
	if callable(weight):
		return weight
	# If the weight keyword argument is not callable, we assume it is a
	# string representing the edge attribute containing the weight of
	# the edge.
	if G.is_multigraph():
		return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
	return lambda u, v, data: data.get(weight, 1)


def create_node(settings):

	rand_id = '%066x' % random.randrange(16**66)

	return {

		# Usual attributes as per rpc, mostly not relevant
		'last_timestamp': 1544034959,
		'globalfeatures': '',
		'nodeid': rand_id,
		'alias': 'johnstedt',
		'color': '000000',
		'global_features': '',
		'addresses': [{'port': 9735, 'address': '73.33.112.94', 'type': 'ipv4'}],

		# Simulation attributes
		'attachment_policy': settings['attachment_policy'],

		'profits': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
		'total_profits': 0,
		"base_fee": random.randint(100, 1501),
		"fee_per_millionth": random.randint(500, 1501)
	}


class SimulationOperator:

	__g = None
	__routing_table = None
	__env = None

	def __init__(self):

		if len(sys.argv) == 1:
			print("SUPPLY ARGS PLZ")
			exit(0)

		self.__g = nx.DiGraph()
		self.__attachment = AttachmentPolicies()

		for i in range(1, len(sys.argv)):
			if sys.argv[i] == "-preset":
				print(sys.argv[i+1])
				if sys.argv[i+1] == "test":
					self.simulate("presets/test.json")
			if sys.argv[i] == "-file":
				print(sys.argv[i+1])

	def simulate(self, sim_file):
		self.__env = json.loads(open(sim_file, "r").read())
		print(json.dumps(self.__env, indent=2))

		self.build_environment()

		self.__routing_table, _ = nx.floyd_warshall_predecessor_and_distance(self.__g)
		print("routing table")

		self.print_alive_nodes()

		for i in range(self.__env['environment']['time_steps']):
			print("ITERATION ", i)
			self.reset_day(i)
			for j in range(self.__env['environment']['payments_per_step']):
				self.route_payments_all_to_all(i)

			self.network_probability_node_creation()
			self.check_for_bankruptcy()

		self.print_profit_table()

		self.print_alive_nodes()

		#self.betweenness_centrality()

	def build_environment(self):

		for n in range(0, self.__env['environment']['initial_nodes']):
			settings = numpy.random.choice(self.__env['routing_nodes'], p=[i['initial_distribution'] for i in self.__env['routing_nodes']])
			node = create_node(settings)
			self.__attachment.attach(self.__g, node, 5)

		return True

	def route_payments_all_to_all(self, day):

		source = 0
		dest = 0
		while source == dest:
			source = random.sample(self.__g.nodes, 1)[0]
			dest = random.sample(self.__g.nodes, 1)[0]

		routers = nx.reconstruct_path(source, dest, self.__routing_table)

		if not self.is_path_liquid(routers, 1000):  # If shortest path isn't liquid, create another one.
			print("NOT LIQUID")
			routers = self.create_liquid_route(source, dest)

		self.offset_liquidity(routers, 1000)
		routers.remove(source)
		routers.remove(dest)
		for n in routers:
			self.__g.nodes[n]['profits'][day % 10] += (self.__g.nodes[n]["base_fee"] / 1000)  # TODO: MOVE TO CHANNEL
			self.__g.nodes[n]['total_profits'] += (self.__g.nodes[n]["base_fee"] / 1000)

	def is_path_liquid(self, routers, amount):
		previous = None
		for n in routers:
			if previous is not None:
				if self.__g.get_edge_data(previous, n)["satoshis"] < amount:
					return False

			previous = n

		return True

	def offset_liquidity(self, routers, amount):  # TODO: ADD FEE
		previous = None
		for n in routers:
			if previous is not None:
				self.__g.get_edge_data(previous, n)["satoshis"] = self.__g.get_edge_data(previous, n)["satoshis"] - amount
				self.__g.get_edge_data(n, previous)["satoshis"] = self.__g.get_edge_data(n, previous)["satoshis"] + amount

			previous = n

		return True

	def create_liquid_route(self, source, target):
		#nodes = nx.dijkstra_path(self.__g, source, target, weight="base_fee_millisatoshi")
		nodes = dijkstra_multisource(self.__g, source, target, weight="base_fee_millisatoshi")
		print(nodes)
		return True

	def network_probability_node_creation(self):
		albert = 0
		randoms = 0
		for n in self.__g.nodes:
			if self.__g.nodes[n]['attachment_policy'] == "barabasi_albert":
				albert += 1
			else:
				randoms += 1

		settings = numpy.random.choice([{"attachment_policy": "barabasi_albert"}, {"attachment_policy": "random"}], p=[albert/len(self.__g.nodes), randoms/len(self.__g.nodes)])
		node = create_node(settings)
		self.__attachment.attach(self.__g, node, 5)

	def reset_day(self, day):
		for n in self.__g.nodes:
			self.__g.nodes[n]['profits'][day % 10] = 0

	def check_for_bankruptcy(self):
		changed = False
		remove = []

		for node in self.__g.nodes:

			if sum(self.__g.nodes[node]['profits']) < 10:
				print(self.__g.nodes[node]['nodeid'], " Went bankrupt with method: ", self.__g.nodes[node]['attachment_policy'])
				remove.append(node)
				changed = True
		if changed:
			for n in remove:
				self.__attachment.remove_all_barabasi(n)
				self.__g.remove_node(n)

		self.__routing_table, _ = nx.floyd_warshall_predecessor_and_distance(self.__g, weight="base_fee_millisatoshi")

	def betweenness_centrality(self):
		#l = sorted(nx.betweenness_centrality(self.__g, normalized=False).items())

		l2 = sorted(nx.edge_betweenness_centrality(self.__g, normalized=False, weight="base_fee_millisatoshi").items(), key=lambda x: x[1])

		self.fast_price_function(last_edge)

	def price_function(self, last_edge):
		edge_data = self.__g.get_edge_data(last_edge[0][0], last_edge[0][1])
		plot_list = []

		fee_range = range(10, 1500, 1)

		for fee in fee_range:
			edge_data["base_fee_millisatoshi"] = fee
			self.__g.add_edge(last_edge[0][0], last_edge[0][1], **edge_data)
			all_pair = sorted(nx.edge_betweenness_centrality(self.__g, normalized=False, weight="base_fee_millisatoshi").items(), key=lambda x: x[1])
			bc = [edge[1] for edge in all_pair if edge[0][0] == last_edge[0][0] and edge[0][1] == last_edge[0][1]][0]
			if bc == 0:
				break
			plot_list.append(fee*bc)
			print(fee, " ", bc, " ", fee * bc)

		plot.plot_fee_curve(range(10, 10+len(plot_list)), plot_list)

	def fast_price_function(self, e, algorithm='johnson'):
		"""

		Fast function to find the optimal price for a given edge e.

		1. Calculate the shortest path from all-to-all vertices without going through $C$ with either Floyd-Warshall or
			Johnson. Default is Johnson
		2. Calculate shortest path from $C$ source to all explicitly going through $C$ with Dijkstra.
		3. Compare difference between all-to-all cost with all-to-$V$-to-all, producing a cumulative summation over the
			difference.
		4. Maximizing fee * cumulative difference.

		Plots the given fee * cumulative difference over fee curve.
		"""

		e_data = self.__g.get_edge_data(e[0][0], e[0][1])

		# Remove edge e
		self.__g.remove_edge(e[0][0], e[0][1])

		# Floyd or Johnson
		if algorithm == 'johnson':
			all_pair_shortest_path = nx.floyd_warshall(self.__g, weight="base_fee_millisatoshi")
		else:
			all_pair_shortest_path = nx.johnson(self.__g, weight="base_fee_millisatoshi")

		# remove all edges from e source, Add edge e
		edges = list(self.__g.out_edges(e[0][0]))   # get all edges of source

		for rm in edges:
			self.__g.remove_edge(rm[0], rm[1])

		e_data["base_fee_millisatoshi"] = 0
		self.__g.add_edge(e[0][0], e[0][1], **e_data)

		# Compute single source dijkstras from e source over e.
		edge_to_all = nx.single_source_dijkstra_path_length(self.__g, e[0][0], weight="base_fee_millisatoshi")

		path_price_difference = []
		for source in all_pair_shortest_path:
			for destination in all_pair_shortest_path[source]:
				# SOURCE TO V TO DESTINATION
				if source != destination != e[0][0]:
					diff = (all_pair_shortest_path[source][e[0][0]] + edge_to_all[destination]) - all_pair_shortest_path[source][destination]
					if diff < 0:  # TODO: WHAT TO DO WITH TIES?
						path_price_difference.append(-diff)

		fee_range = range(1, 1500, 1)
		plot_list = []
		for r in fee_range:
			plot_list.append(len([p for p in path_price_difference if p >= r]) * r)
		plot.plot_fee_curve(fee_range, plot_list)

	def print_alive_nodes(self):
		albert = 0
		random = 0
		for n in self.__g.nodes:
			if self.__g.nodes[n]['attachment_policy'] == "barabasi_albert":
				albert += 1
			else:
				random += 1
		print("Barabasi nodes: ", albert, " Random nodes: ", random)

	def print_profit_table(self):
		list2 = []
		for n in self.__g.nodes:
			list2.append(self.__g.nodes[n])

		list2 = sorted(list2, key=lambda k: k['total_profits'])
		cum_albert = 0
		cum_random = 0
		for n in list2:
			print(n['attachment_policy'], " ", n['total_profits'])
			if n['attachment_policy'] == "barabasi_albert":
				cum_albert += n['total_profits']
			else:
				cum_random += n['total_profits']

		print("BARABASI TOTAL: ", cum_albert, " RANDOM TOTAL: ", cum_random)


if __name__ == "__main__":
	SimulationOperator()

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
		self.is_path_liquid(routers, 1)
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

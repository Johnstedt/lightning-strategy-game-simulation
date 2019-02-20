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
		"base_fee": random.randint(500, 1501),
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

		self.print_alive_nodes()

		"""for i in range(self.__env['environment']['time_steps']):
			print("ITERATION ", i)
			self.reset_day(i)
			for j in range(self.__env['environment']['payments_per_step']):
				self.route_payments_all_to_all(i)

			self.network_probability_node_creation()
			self.check_for_bankruptcy()

		self.print_profit_table()

		self.print_alive_nodes()"""

		self.betweeness_centrality()

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
		routers.remove(source)
		routers.remove(dest)
		for n in routers:
			self.__g.nodes[n]['profits'][day % 10] += (self.__g.nodes[n]["base_fee"] / 1000)  # TODO: MOVE TO CHANNEL
			self.__g.nodes[n]['total_profits'] += (self.__g.nodes[n]["base_fee"] / 1000)

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

	def betweeness_centrality(self):
		l = sorted(nx.betweenness_centrality(self.__g, normalized=False).items())
		print(json.dumps(l, indent=2))
		l2 = sorted(nx.edge_betweenness_centrality(self.__g, normalized=False, weight="base_fee_millisatoshi").items(), key=lambda x: x[1])
		print(json.dumps(l2, indent=2))
		last_edge = l2[len(l2)-1]

		print(last_edge)
		print(last_edge[0][0])

		print(self.__g.get_edge_data(last_edge[0][0], last_edge[0][1]))

		self.price_function(last_edge)

	def price_function(self, last_edge):
		edge_data = self.__g.get_edge_data(last_edge[0][0], last_edge[0][1])
		for fee in range(500, 1500, 10):
			#edge_data["base_fee_millisatoshi"] = fee
			#self.__g.add_edge(last_edge[0][0], last_edge[0][1], **edge_data)
			all_pair = sorted(nx.edge_betweenness_centrality(self.__g, normalized=False, weight="base_fee_millisatoshi").items(), key=lambda x: x[1])
			print([edge[1] for edge in all_pair if edge[0][0] == last_edge[0][0] and edge[0][1] == last_edge[0][1]])

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

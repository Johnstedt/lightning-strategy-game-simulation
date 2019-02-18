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

		'profits': 0
	}


def create_channel():
	return {
		'base_fee_millisatoshi': 1000,
		'satoshis': 200000,
		'destination': '0270685ca81a8e4d4d01beec5781f4cc924684072ae52c507f8ebe9daf0caaab7b',
		'short_channel_id': '1457217x64x0',
		'public': True,
		'last_update': 1550232803,
		'source': '02e5f5706e2d152a6acc67c646a83bb1c947b8ea98ad1f123272113612641add2a',
		'delay': 144,
		'message_flags': 1,
		'channel_flags': 1,
		'fee_per_millionth': 1,
		'flags': 257,
		'active': True
	}


class SimulationOperator:

	__g = None
	__routing_table = None
	__env = None

	def __init__(self):

		if len(sys.argv) == 1:
			print("SUPPLY ARGS PLZ")
			exit(0)

		self.__g = nx.Graph()
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

		for i in range(self.__env['environment']['time_steps']):
			print("ITERATION ", i)
			for j in range(self.__env['environment']['payments_per_step']):
				self.route_payments_all_to_all()

			self.check_for_bancrupcy(i)
		self.print_profit_table()

		self.print_alive_nodes()

	def build_environment(self):

		for n in range(0, self.__env['environment']['initial_nodes']):
			settings = numpy.random.choice(self.__env['routing_nodes'], p=[i['initial_distribution'] for i in self.__env['routing_nodes']])
			node = create_node(settings)
			self.__attachment.attach(self.__g, node, 5)

		return True

	def route_payments_all_to_all(self):

		source = 0
		dest = 0
		while source == dest:
			source = random.sample(self.__g.nodes, 1)[0]
			dest = random.sample(self.__g.nodes, 1)[0]

		routers = nx.reconstruct_path(source, dest, self.__routing_table)
		routers.remove(source)
		routers.remove(dest)
		for n in routers:
			self.__g.nodes[n]['profits'] += 1

	def print_alive_nodes(self):
		albert = 0
		random = 0
		for n in self.__g.nodes:
			if self.__g.nodes[n]['attachment_policy'] == "barabasi_albert":
				albert += 1
			else:
				random += 1
		print("Barabasi nodes: ", albert, " Random nodes: ", random)

	def check_for_bancrupcy(self, steps):
		changed = False
		remove = []
		for node in self.__g.nodes:

			if self.__g.nodes[node]['profits'] - steps <= 0:
				print(self.__g.nodes[node]['nodeid'], " Went bankrupt with method: ", self.__g.nodes[node]['attachment_policy'])
				remove.append(node)
				changed = True
		if changed:
			for n in remove:
				self.__g.remove_node(n)

			self.__routing_table, _ = nx.floyd_warshall_predecessor_and_distance(self.__g)

	def print_profit_table(self):
		list2 = []
		for n in self.__g.nodes:
			list2.append(self.__g.nodes[n])

		list2 = sorted(list2, key=lambda k: k['profits'])
		cum_albert = 0
		cum_random = 0
		for n in list2:
			print(n['attachment_policy'], " ", n['profits'])
			if n['attachment_policy'] == "barabasi_albert":
				cum_albert += n['profits']
			else:
				cum_random += n['profits']

		print("BARABASI TOTAL: ", cum_albert, " RANDOM TOTAL: ", cum_random)


if __name__ == "__main__":
	SimulationOperator()

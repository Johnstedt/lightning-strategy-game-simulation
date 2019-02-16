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
		'attachment_policy': settings['attachment_policy']
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
		env = json.loads(open(sim_file, "r").read())
		print(json.dumps(env, indent=2))

		self.build_environment(env)
		self.generate_all_shortest_paths()

	def build_environment(self, env):

		for n in range(0, env['environment']['initial_nodes']):
			settings = numpy.random.choice(env['routing_nodes'], p=[i['initial_distribution'] for i in env['routing_nodes']])
			node = create_node(settings)
			self.__attachment.attach(self.__g, node, 5)

		return True

	def generate_all_shortest_paths(self, cutoff=10):

		if cutoff < 1:
			cutoff = 10

		print(len(self.__g.edges))
		print(len(self.__g.nodes))

		all_pair_shortest_paths = nx.all_pairs_shortest_path(self.__g, cutoff=cutoff)
		print(all_pair_shortest_paths)
		for item in all_pair_shortest_paths:

			print(item[1])


if __name__ == "__main__":
	SimulationOperator()

"""
python3 -m pip install -U matplotlib
python3 -m pip install networkx pylightning
"""

import networkx as nx

import json
import sys


class SimulationOperator:

	__nodes = None

	def __init__(self):

		if len(sys.argv) == 1:
			"SUPPLY ARGS"
			exit(0)

		for i in range(1, len(sys.argv)):
			if sys.argv[i] == "-preset":
				print(sys.argv[i+1])
				if sys.argv[i+1] == "test":
					self.build_environment("presets/test.json")
			if sys.argv[i] == "-file":
				print(sys.argv[i+1])

	def build_environment(self, sim_file):

		env = json.loads(open(sim_file, "r").read())
		print(env)

		g = g = nx.Graph()

		for n in range(0, env['environment']['initial_nodes']):


		return True

	def create_node(self):
		return {}

if __name__ == "__main__":
	SimulationOperator()

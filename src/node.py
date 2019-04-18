"""
python3 -m pip install -U matplotlib
python3 -m pip install networkx pylightning
"""

import networkx as nx

import plot
from lightning_ops import LightningOperator


class NodeOperator:

	__lightning = None

	def __init__(self):

		lightning = LightningOperator("mainnet")

		g = nx.Graph()

		lightning.populate_graph(g)

		print("NODES: ", len(g.nodes))
		print("EDGES: ", len(g.edges))

		#plot.plot_robustness_random([g], 10)
		plot.plot_robustness_coordinated([g], 7)

		#print(g.edg['02a78ed15da84d0ecdcefff5905bd7287ff587b7abd9a46cf0a04d31c3336a9b4e'])

		#plot.plot_graph(g)

		#ba = nx.barabasi_albert_graph(20000, 5)
		#ba2 = nx.barabasi_albert_graph(40000, 5)
		#ba3 = nx.barabasi_albert_graph(200000, 5)

		#ergy = nx.erdos_renyi_graph(2000, 0.002)

		#nx.write_gexf(g, "plots/mainnet.gexf")

		#plot.plot_degree_distribution([ba3, ba2, ba, g], [2.9, 1.9])


if __name__ == "__main__":
	NodeOperator()

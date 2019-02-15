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

		lightning = LightningOperator()

		g = nx.Graph()

		lightning.populate_graph(g)

		print(g.edges[0])
		print(g.nodes[0])

		plot.plot_graph(g)

		ba = nx.barabasi_albert_graph(20000, 5)
		ba2 = nx.barabasi_albert_graph(40000, 5)
		ba3 = nx.barabasi_albert_graph(200000, 5)

		plot.plot_degree_distribution([ba3, ba2, ba, g], [2.9, 1.9])


if __name__ == "__main__":
	NodeOperator()

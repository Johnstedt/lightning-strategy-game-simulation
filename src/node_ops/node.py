"""
python3 -m pip install -U matplotlib
"""
import math

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy
from lightning_ops import LightningOperator


class NodeOperator:

	__lightning = None

	def __init__(self):

		"""lightning = LightningOperator()

		g = nx.Graph()

		lightning.populate_graph(g)
		print(len(g.edges))
		print(len(g.nodes))

		pos = nx.spring_layout(g)
		nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size=1)
		nx.draw_networkx_edges(g, pos, edge_color="black")
		plt.savefig('network.png')"""

		ba = nx.barabasi_albert_graph(2000, 5, seed=1)
		ba2 = nx.barabasi_albert_graph(4000, 5, seed=1)
		ba3 = nx.barabasi_albert_graph(6000, 5, seed=1)
		nx.draw(ba, with_labels=True)
		plt.savefig('ba_scale_free.png')

		plt.clf()

		plt.plot([50, 60, 30, 40], [1, 2, 3, 4])
		plt.ylabel('some numbers')
		plt.savefig('this_is_plot.png')

		t1 = np.arange(0.0, 5.0, 0.1)
		t2 = np.arange(0.0, 5.0, 0.02)

		plt.figure(1)
		plt.subplot(211)
		plt.plot(t1, t1**2, 'k', t2, t2**9, 'bo')
		plt.savefig("one_func.png")

		plt.subplot(212)
		plt.plot(t2, np.cos(2*np.pi*t2), 'r--')
		plt.savefig("two_func.png")

		plt.clf()

		k = np.arange(15, 200, 0.1)

		plt.plot(k, 200*self.P(k, 1.9), 'r--')
		plt.plot(k, 200*self.P(k, 2.9), 'b--')
		plt.savefig("sf.png")
		list_to_plot = []

		for n in ba.nodes:
			list_to_plot.append(len(list(ba.neighbors(n))))

		list_to_plot.sort(reverse=True)

		plt.loglog(list_to_plot, np.arange(0.001, 1, 999/1000 / len(ba.nodes)))

		list_to_plot = []

		for n in ba2.nodes:
			list_to_plot.append(len(list(ba2.neighbors(n))))

		list_to_plot.sort(reverse=True)

		plt.loglog(list_to_plot, np.arange(0.001, 1, 999/1000 / len(ba2.nodes)))

		list_to_plot = []

		for n in ba3.nodes:
			list_to_plot.append(len(list(ba3.neighbors(n))))

		list_to_plot.sort(reverse=True)

		plt.loglog(list_to_plot, np.arange(0.001, 1, 999/1000 / len(ba3.nodes)))
		
		plt.savefig("scale_free.png")

	def P(self, k, y):
		return k**(-y)

	def p(self, k, y, ko):
		return self.euler_beta(k, y) / self.euler_beta(ko, y - 1)

	@staticmethod
	def euler_beta(x, y):
		return scipy.special.gamma(x) * scipy.special.gamma(y) / scipy.special.gamma(x + y)


if __name__ == "__main__":
	NodeOperator()

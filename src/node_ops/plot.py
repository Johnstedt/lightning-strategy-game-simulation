import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy

def plot_graph(g, num=''):

	pos = nx.spring_layout(g)
	nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size=1)
	nx.draw_networkx_edges(g, pos, edge_color="black")
	plt.savefig('plots/graph_visual{}.png'.format(num))
	plt.clf()

	return True


def plot_degree_distribution(graphs, reference):

	k = np.arange(8, 500, 0.1)

	colors = ['r--', 'b--', 'y--']
	colors_b = ['ro', 'bo', 'yo']

	i = 0
	for r in reference:
		plt.plot(k, 2000*p(k, r), colors[i % 3])
		i += 1

	j = 0
	for g in graphs:
		list_to_plot = []

		g_dist = [0] * 5000
		for n in g.nodes:
			g_dist[len(list(g.neighbors(n)))] += 1
			list_to_plot.append(len(list(g.neighbors(n))))

		pk = []
		k = []
		i = 0
		for n in range(1, 500):
			if g_dist[n] != 0:
				k.append(n)
				pk.append(g_dist[n] / len(g.nodes))
				#print(i, " ", (g_dist[n] / len(g.nodes)))
				i += 1

		plt.loglog(k, pk, colors_b[j % 3])
		j += 1

	plt.ylim([0.0000001, 1])
	plt.savefig("plots/scale_free.png")
	return True


def p(k, y):
	return k**(-y)

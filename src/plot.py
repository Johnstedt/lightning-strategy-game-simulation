import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy

import edges as e


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


def plot_fee_curve(fee, profits):

	plt.plot(fee, profits, 'b')
	plt.savefig("plots/fee_curve")


def p(k, y):
	return k**(-y)


def plot_explainable_ln():

	g = nx.DiGraph()
	g.add_node(1)
	g.add_node(2)
	g.add_node(3)
	g.add_node(4)
	g.add_node(5)
	g.add_node(6)
	g.add_node(7)

	g.add_edge(1, 2, weight=5)
	g.add_edge(2, 1, weight=2)

	g.add_edge(1, 3, weight=4)
	g.add_edge(3, 1, weight=9)

	g.add_edge(1, 7, weight=4)
	g.add_edge(7, 1, weight=9)

	g.add_edge(2, 8, weight=1)
	g.add_edge(8, 2, weight=4)

	g.add_edge(6, 8, weight=6)
	g.add_edge(8, 6, weight=7)

	g.add_edge(6, 5, weight=8)
	g.add_edge(5, 6, weight=3)

	g.add_edge(7, 4, weight=3)
	g.add_edge(4, 7, weight=6)

	g.add_edge(8, 1, weight=3)
	g.add_edge(1, 8, weight=2)

	g.add_edge(6, 2, weight=1)
	g.add_edge(2, 6, weight=2)

	#pos = nx.spring_layout(g)
	#nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size=90)
	#nx.draw_networkx_edges(g, pos, edge_color="black")

	ba = nx.barabasi_albert_graph(25, 3)

	pos = nx.circular_layout(g)
	labels = nx.get_edge_attributes(g, 'weight')
	nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)

	#nx.draw_networkx_edges(g, pos)
	nx.draw_circular(g)
	plt.savefig('plots/circular.png')
	nx.draw_random(g)
	plt.savefig('plots/random.png')
	nx.draw_spectral(g)
	plt.savefig('plots/spectral.png')
	plt.clf()
	nx.write_gexf(g, "graph_data/show.gexf")

	G = nx.path_graph(3)
	bb = nx.betweenness_centrality(G, normalized=False)
	nx.set_node_attributes(G, bb, name='betweenness')
	bb = nx.betweenness_centrality(ba, normalized=False)
	nx.set_node_attributes(ba, bb, name='betweenness')
	nx.write_gexf(ba, "plots/barabasi_centrality.gexf")


def save_graph(graph, file_name):
	#initialze Figure
	plt.figure(num=None, figsize=(20, 20), dpi=80)
	plt.axis('off')
	fig = plt.figure(1)
	pos = nx.spring_layout(graph)
	nx.draw_networkx_nodes(graph, pos)
	nx.draw_networkx_edges(graph, pos)
	nx.draw_networkx_labels(graph, pos)

	cut = 1.00
	xmax = cut * max(xx for xx, yy in pos.values())
	ymax = cut * max(yy for xx, yy in pos.values())
	plt.xlim(0, xmax)
	plt.ylim(0, ymax)

	plt.savefig(file_name, bbox_inches="tight")
	pylab.close()
	del fig


if __name__ == "__main__":
	plot_explainable_ln()

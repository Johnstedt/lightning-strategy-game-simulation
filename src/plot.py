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


def plot_degree_distribution(graphs, references):

	k = np.arange(8, 500, 0.1)

	colors = ['r--', 'b--', 'y--']
	colors_b = ['ro', 'bo', 'yo']

	i = 0
	for r in references:
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
				i += 1

		plt.loglog(k, pk, colors_b[j % 3])
		j += 1

	plt.ylim([0.0000001, 1])
	plt.savefig("plots/scale_free.png")
	return True


def p(k, y):
	return k**(-y)


def plot_survival_history(histories, references):

	k = np.arange(0, len(histories), 1)

	colors = ['r--', 'b--', 'y--']
	colors_b = ['r-', 'b-', 'y-']

	i = 0
	for r in references:
		plt.plot(k, 2000*p(k, r), colors[i % 3])
		i += 1

	j = 0
	for h in histories:
		print(h)
		plt.plot(k, h[1], colors_b[i % 3])
		i += 1

	plt.savefig("plots/survival_history.png")
	return True


def plot_fee_curve(fee, profits):

	fig, ax = plt.subplots()
	fig.subplots_adjust(left=0.2)
	plt.plot(fee, profits, 'b')
	ax.set_xlabel("Fee")
	ax.set_ylabel("Betweenness centrality * fee")
	plt.savefig("plots/fee_curve")


def write_to_file(graph, name):
	nx.write_gexf(graph, name)


if __name__ == "__main__":
	print("Should not be called directly")

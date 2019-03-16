import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy
import statistics

def plot_graph(g, num=''):

	pos = nx.spring_layout(g)
	nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size=1)
	nx.draw_networkx_edges(g, pos, edge_color="black")
	plt.savefig('plots/graph_visual{}.png'.format(num))
	plt.clf()

	return True


def plot_degree_distribution(graphs, references, name, axis="log", x=500, labels=["a", "a", "a"],
							function_labels=["a", "a", "a"]):

	k = np.arange(0, x, 1)

	colors = ['r--', 'b--', 'y--']
	colors_b = ['ro', 'bo', 'yo']

	fig, ax = plt.subplots()
	#fig.subplots_adjust(left=0.2)
	ax.set_xlabel("$k$")
	ax.set_ylabel("$P(k)$")

	i = 0
	#for r in references:
	#	plt.plot(k, 2000*p(k, r), colors[i % 3])
	#	i += 1

	for r in references:
		ylist = list(map(r, k))
		plt.plot(k, ylist, colors[i % 3], label=function_labels[i])
		i += 1

	j = 0
	for g in graphs:
		list_to_plot = []

		g_dist = [0] * 5000
		for n in g.nodes:
			#print(len(list(g.neighbors(n))))
			g_dist[len(list(g.neighbors(n)))] += 1
			list_to_plot.append(len(list(g.neighbors(n))))

		pk = []
		k = []
		i = 0
		for n in range(1, x):
			if g_dist[n] != 0:
				k.append(n)
				pk.append(g_dist[n] / len(g.nodes))
				i += 1
		#print(pk)
		if axis == "log":
			plt.loglog(k, pk, colors_b[j % 3])
		else:
			plt.plot(k, pk, colors_b[j % 3], label=labels[j])
			ax.legend()
		j += 1

	#plt.ylim([0.0001, 1])

	plt.savefig("plots/{}_degree_distribution.png".format(name))
	return True


def p(k, y):
	return k**(-y)


def plot_survival_history(histories, references):

	k = np.arange(0, len(next(iter(histories.values()))), 1)

	fig, ax = plt.subplots()
	fig.subplots_adjust(left=0.2)
	ax.set_xlabel("$Days$")
	ax.set_ylabel("$Population$")

	colors = ['r--', 'b--', 'y--']
	colors_b = ['r-', 'b-', 'y-']

	i = 0
	for r in references:
		plt.plot(k, 2000*p(k, r), colors[i % 3])
		i += 1

	j = 0
	for h in histories:
		print(histories[h])
		plt.plot(k, histories[h], colors_b[i % 3], label=h)
		i += 1

	ax.legend()

	plt.savefig("plots/survival_history.png")
	return True


def plot_multiple_histories(histories):

	colors = ['r', 'b', 'y']
	colors_b = ['r--', 'b--', 'y--']
	plt.clf()
	fig, ax = plt.subplots()
	ax.set_xlabel("$Days$")
	ax.set_ylabel("$Average Population$")

	datasets = [[[0]*len(histories) for _ in range(len(next(iter(histories[0].values()))))] for _ in range(len(histories[0]))]
	labels = []
	history = 0
	for n in histories:
		i = 0
		for h in n:
			if history == 0:
				labels.append(h)
			j = 0
			for val in n[h]:
				datasets[i][j][history] = val
				j += 1
			i += 1
		history += 1

	print(datasets)

	""" fig1, ax1 = plt.subplots()
	ax1.set_title('Box Plot')
	ax1.boxplot(datasets[0], positions=[1, 3, 5, 7, 9], widths=0.6)
	ax1.boxplot(datasets[1], positions=[2, 4, 6, 8, 10], widths=0.6)

	ax1.set_xticklabels([0, 1, 2, 3, 4, 5])
	ax1.set_xticks([0, 1.5, 3.5, 5.5, 7.5, 9.5])

	plt.savefig("plots/box_plot.png")"""

	p_color = 0
	for populations in datasets:
		std = []
		mean = []
		for days in populations:
			mean.append(statistics.mean(days))
			std.append(statistics.standard_deviation(days))

		plt.plot(range(len(mean)), mean, colors[p_color], label=labels[p_color])
		plt.plot(range(len(mean)), [sum(x) for x in zip(mean, std)], colors_b[p_color], label="{} +/- $\sigma$".format(labels[p_color]))
		plt.plot(range(len(mean)), [x-y for (x, y) in zip(mean, std)], colors_b[p_color])
		p_color += 1

	ax.legend()
	plt.savefig("plots/histories_deviation.png")


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

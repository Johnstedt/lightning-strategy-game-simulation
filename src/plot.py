import networkx as nx
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import random
import scipy
import statistics
from mpl_toolkits import mplot3d


def plot_graph(g, num=''):

	pos = nx.spring_layout(g)
	nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size=1)
	nx.draw_networkx_edges(g, pos, edge_color="black")
	plt.savefig('plots/graph_visual{}.png'.format(num))
	plt.clf()

	return True


def plot_degree_distribution(graphs, references, name, axis="log", x=500, labels=["a", "a", "a"],
							function_labels=["a", "a", "a"]):

	k = np.arange(1, x, 1)

	colors = ['g--', 'r--', 'b--', 'y--']
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
			plt.loglog(k, pk, colors_b[j % 3], label=labels[j])
		else:
			plt.plot(k, pk, colors_b[j % 3], label=labels[j])
			print(pk)
		ax.legend()
		j += 1

	plt.ylim([0.0001, 1])

	plt.savefig("plots/{}_degree_distribution.png".format(name))
	return True


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


def plot_robustness_random(graphs, it, directory):

	fig1, ax1 = plt.subplots()

	box = []

	for num in range(1, it):
		current = []
		for t in range(100):
			for g in graphs:
				c = g.copy()
				for rm in range(int(len(g.nodes)*0.10*num)):
					node = random.choice(list(c.nodes))
					c.remove_node(node)
				giant = max(nx.connected_component_subgraphs(c), key=len)
			#	print("NODES length: ", len(c.nodes), " Giant component: ", len(giant.nodes),
			#		" kvot: ", len(giant.nodes)/len(c.nodes))
				current.append(len(giant.nodes)/len(c.nodes))
		box.append(current)

	flierprops = dict(marker='o', markerfacecolor='black', markersize=3,
					  linestyle='none', markeredgecolor='black')
	boxes = sns.boxplot(data=box, flierprops=flierprops)

	for i, b in enumerate(boxes.artists):
		b.set_edgecolor('black')
		b.set_facecolor('white')

		# iterate over whiskers and median lines
		for j in range(6*i, 6*(i+1)):
			ax1.lines[j].set_color('black')

	ax1.set_ylabel("Fraction of Giant component")
	ax1.set_xlabel("Percentage of nodes removed")
	perc = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%"]
	ax1.set_xticklabels(perc[:it])

	plt.savefig("plots/{}/robustness_random.png".format(directory))


def plot_robustness_coordinated(graphs, it, directory):
	fig1, ax1 = plt.subplots()

	box = []

	for num in range(1, it):
		current = []

		for g in graphs:
			c = g.copy()

			targets = []
			for n in c.nodes:
				targets.append((n, len(c.edges(n))))

			targets.sort(key=lambda x: x[1], reverse=True)

			for rm in range(int(len(g.nodes)*0.05*num)):
				c.remove_node(targets[rm][0])

			giant = max(nx.connected_component_subgraphs(c), key=len)
			print("NODES length: ", len(c.nodes), " Giant component: ", len(giant.nodes),
				  " kvot: ", len(giant.nodes)/len(c.nodes))
			current.append(len(giant.nodes)/len(c.nodes))
		box.append(current[0])

	flierprops = dict(marker='o', markerfacecolor='black', markersize=3,
				  linestyle='none', markeredgecolor='black')

	#boxes = sns.boxplot(data=box, flierprops=flierprops)
	print(box)

	plt.plot(range(len(box)), box, "black")
	"""	for i, b in enumerate(boxes.artists):
		b.set_edgecolor('black')
		b.set_facecolor('white')

		# iterate over whiskers and median lines
		for j in range(6*i, 6*(i+1)):
			boxes.lines[j].set_color('black') """

	ax1.set_ylabel("Fraction of Giant component")
	ax1.set_xlabel("Percentage of nodes removed")
	perc = ["5%", "10%", "15%", "20%", "25%", "30%", "35%", "40%", "45%", "50%", "55%", "60%", "65%", "70%", "75%", "80%", "85%", "90%", "95%"]
	ax1.set_xticklabels(["0%","5%", "10%", "15%", "20%", "25%", "30%", "35%", "40%", "45%", "50%"])

	plt.savefig("plots/{}/robustness_coordinated.png".format(directory))
	return box


def plot_path_length(g, directory):

	fig1, ax1 = plt.subplots()
	fig1.subplots_adjust(left=0.15)
	hist = []
	am = {}

	table = nx.floyd_warshall(g)

	for n in list(table.values()):
		#print(n.values())
		for k in list(n.values()):
			#hist[int(k)] = hist.get(int(k), 0) + 1
			if k < 10000:
				if int(k) != 0:
					hist.append(k)
					am[int(k)] = am.get(int(k), 0) + 1

	plt.hist(hist, len(am.values())-1, facecolor='blue', edgecolor='darkblue', alpha=0.75, align='left')
	ax1.set_xlabel("Path length")
	ax1.set_ylabel("Paths")
	plt.savefig("plots/{}/histogram_shortest_path".format(directory))
	print("AVERAGE: ", sum(hist)/len(hist))


def plot_wealth_distribution(graphs, directory):

	fig1, ax1 = plt.subplots()
	# fig1.subplots_adjust(left=0.15)

	colors = ['ro', 'bo', 'go', 'co', 'mo', 'yo', 'ko']

	profits = {}

	for g in graphs:

		for n in g.nodes:
			if g.nodes[n]["public"]:
				profit = sum(g.nodes[n]["profits"])
				if g.nodes[n]['name'] not in profits:
					profits[g.nodes[n]['name']] = []
				profits[g.nodes[n]['name']].append(profit)

	i = 0
	for n in profits:
		profits[n].sort(reverse=True)
		ax1.plot(range(len(profits[n])), profits[n], colors[i], label=n)
		i += 1

	ax1.set_ylabel("Profits(satoshi)")
	ax1.set_xlabel("Nodes")
	ax1.legend()
	plt.savefig("plots/{}/wealth_distribution_path".format(directory))


def plot_wealth_distribution_in(graphs, directory):

	fig1, ax1 = plt.subplots()
	# fig1.subplots_adjust(left=0.15)

	colors = ['ro', 'bo', 'go', 'co', 'mo', 'yo', 'ko']

	profits = {}
	color = []

	j = 0
	for g in graphs:
		for n in g.nodes:
			if g.nodes[n]["public"]:
				profit = sum(g.nodes[n]["profits"])
				if g.nodes[n]['name'] not in profits:
					profits[g.nodes[n]['name']] = j
					j += 1
				color.append((profit, g.nodes[n]['name']))

#	color = normalize_list(color)
	color.sort(reverse=True, key=lambda x: x[0])

	i = 0

	used = []

	for c in color:
		if c[1] not in used:
			ax1.plot(i, c[0], colors[profits[c[1]]], label=c[1])
			used.append(c[1])
		else:
			ax1.plot(i, c[0], colors[profits[c[1]]])
		i += 1

	#x = np.arange(len(color))
	#ax1.plot(x, pareto(x, 1, 1.1), label="Pareto")

	print("total: ", sum([x for (x, y) in color]))
	print("top 20: ", sum([x for (x, y) in color][:int(len(color)*0.2)]))
	print("fraction:", sum([x for (x, y) in color][:int(len(color)*0.2)]) / sum([x for (x, y) in color]))

	f = open("plots/{}/matthew_principle_fraction".format(directory), "w+")
	f.write("total: {}".format(sum([x for (x, y) in color])))
	f.write("top 20: {}".format(sum([x for (x, y) in color][:int(len(color)*0.2)])))
	f.write("fraction: {}".format(sum([x for (x, y) in color][:int(len(color)*0.2)]) / sum([x for (x, y) in color])))

	for name in profits.keys():
		print("NAOM: ", name)
		f.write("Strategy: {}, average earnings: {} ".format(name, sum([x for (x, y) in color if y == name]) / len([x for (x, y) in color if y == name])))

	ax1.set_ylabel("Profits(satoshi)")
	ax1.set_xlabel("Nodes")
	ax1.legend()
	plt.savefig("plots/{}/wealth_distribution_same".format(directory))


def plot_multiple_histories(histories, directory):

	colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
	colors_b = ['r--', 'b--', 'g--', 'c--', 'm--', 'y--', 'k--']
	plt.clf()
	fig, ax = plt.subplots()
	ax.set_xlabel("$Days$")
	ax.set_ylabel("$Average Population$")

	#print(histories)

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

	#print(datasets)

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

		plt.plot(range(len(mean)), mean, colors[p_color % 7], label=labels[p_color % 7])
		plt.plot(range(len(mean)), [sum(x) for x in zip(mean, std)], colors_b[p_color % 7], label="{} +/- $\sigma$".format(labels[p_color % 7]))
		plt.plot(range(len(mean)), [x-y for (x, y) in zip(mean, std)], colors_b[p_color % 7])
		p_color += 1

	ax.legend()
	plt.savefig("plots/{}/histories_deviation.png".format(directory))


def plot_price_dimensions(dim, base, prop):

	print(dim)
	fig = plt.figure()
	ax = plt.axes(projection='3d')

	Z = np.array(dim)
	X, Y = np.meshgrid(range(10000, 1350000, 10000), range(10000, 700000, 100000))

	# Set up the axes with gridspec
	#fig = plt.figure(figsize=(6, 6))
	#grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2)

	#ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='bone', edgecolor='none')
	#ax.contour3D(X, Y, Z, 50, cmap='viridis')

	#main_ax = fig.add_subplot(grid[:-1, 1:], projection='3d')
	ax.set_xlabel('$F_{base}(mS)$')
	ax.set_ylabel('$F_{proportional}(\mu S)$')
	ax.set_zlabel('Revenue(kS)')
	#y_hist = fig.add_subplot(grid[:-1, 0], sharey=main_ax)
	#x_hist = fig.add_subplot(grid[-1, 1:], sharex=main_ax)

	#plt.show()
	plt.savefig("plots/price_dimensional_con.png")

	ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
	                cmap='viridis', edgecolor='none')

	print("BASE")
	print(base)

	#x_hist.plot(list(range(10000, 1350000, 10000)), base)

	#x_hist.invert_yaxis()

	print("PROP")
	print(prop)
	print(list(range(10000, 700000, 100000)))
	#y_hist.plot(list(range(10000, 700000, 100000)), prop)
	#plt.show()
	#y_hist.invert_xaxis()

	#plt.show()

	ax.view_init(60, 35)
	plt.savefig("plots/price_dimensional_bird_con.png")
	ax.plot_wireframe(X, Y, Z, color="black")
	#plt.show()
	plt.savefig("plots/price_dimensional_wire.png")


def f(x, y):
	return np.sin(np.sqrt(x ** 2 + y ** 2))


def pareto(x, k, a):
	return a * k**a / (x**a+1)


def normalize_list(l):
	max_val = max([x for (x, y) in l])
	min_val = min([x for (x, y) in l])
	return [((x - min_val) / (max_val - min_val), y) for (x, y) in l]


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
	g = nx.erdos_renyi_graph(1000, 0.004)
	g2 = nx.erdos_renyi_graph(1000, 0.004)
	g3 = nx.erdos_renyi_graph(1000, 0.004)
	g4 = nx.erdos_renyi_graph(1000, 0.004)
	g5 = nx.erdos_renyi_graph(1000, 0.004)
	g6 = nx.erdos_renyi_graph(1000, 0.004)
	g7 = nx.erdos_renyi_graph(1000, 0.004)
	g8 = nx.erdos_renyi_graph(1000, 0.004)
	g9 = nx.erdos_renyi_graph(1000, 0.004)
	g10 = nx.erdos_renyi_graph(1000, 0.004)

	ba = nx.barabasi_albert_graph(800, 2)
	ba2 = nx.barabasi_albert_graph(1000, 2)
	ba3 = nx.barabasi_albert_graph(1000, 2)
	ba4 = nx.barabasi_albert_graph(1000, 2)
	ba5 = nx.barabasi_albert_graph(1000, 2)

	#plot_robustness_coordinated([g, g2, g3, g4, g5, g6, g7, g8, g9, g10], 5)
	#plot_robustness_coordinated([ba, ba2, ba3, ba4, ba5])
	plot_path_length(g)
	print("Should not be called directly")
	print(len(g5.edges))

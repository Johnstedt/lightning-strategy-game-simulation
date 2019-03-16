import networkx as nx

import plot
import strategies.attachment_strategies as attachment
import simulation
import numpy
import random
import operator as op
from functools import reduce


def erdos_renyi():
	g = nx.erdos_renyi_graph(10000, 0.0005)
	return g


def barabasi_albert():
	g = nx.barabasi_albert_graph(10000, 5)
	return g


def callaway_hopcroft():
	g = nx.MultiGraph()
	for n in range(10000):
		node = simulation.create_node({"attachment_strategy": "ambiguous"})
		callaway_hopcraft_attachment(g, node, 0.8)
	return g


def callaway_hopcraft_attachment(g, n, p):

	g.add_node(n["nodeid"], **n)

	if random.random() < p:
		source = [i for i in random.sample(g.nodes, 1)]   # May be edge to oneself
		dest = ([i for i in random.sample(g.nodes, 1)])

		channels = [attachment.create_channel(g.nodes[source[0]], dest[0])]
		g.add_edges_from(zip(source, dest, channels))

		channels = [attachment.create_channel(g.nodes[dest[0]], source[0])]
		g.add_edges_from(zip(dest, source, channels))


def random_strategy_g():
	g = nx.Graph()
	for n in range(10000):
		node = simulation.create_node({"attachment_strategy": "ambiguous"})
		random_attachment(g, node, 1)
	return g


def random_attachment(g, n, m):

	if m >= len(g.nodes):
		g.add_node(n["nodeid"], **n)
		return False

	targets = random.sample(g.nodes(), m)
	g.add_node(n["nodeid"], **n)

	channels = [attachment.create_channel(n, target_id) for target_id in targets]
	g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

	channels = [attachment.create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
	g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

	return True


def plot_all_topologies():
	plot.plot_degree_distribution([erdos_renyi(), callaway_hopcroft(), random_strategy_g()],
									[lambda x: binomial_func(x, 10000, 0.0005), lambda x: callaway_func(x, 0.8)], "random_topology",
									labels=["Erdős–Rényi", "Callaway_Hopcraft et al.", "random"],
									function_labels=["ER True distribution", "CH True distribution"],
									axis="lin", x=23)
	#plot.plot_degree_distribution([erdos_renyi(), barabasi_albert(), random_strategy_g(), callaway_hopcroft()], [2.9], "topology")
	return True


def callaway_func(x, delta):
	"""
	\[p(k) = \dfrac{(2\delta)^k}{1 + 2\delta^{k+1}} \]

	"""
	return (2*delta)**x / ((1 + (2*delta))**(x+1))


def binomial_func(x, n, p):
	"""
	\[p(k) = {n-1 \choose k} p^k(1-p)^{n-1-k} \]
	"""
	return ncr(n-1, x) * (p**x) * ((1-p)**(n-1-x))


def ncr(n, r):
	r = min(r, n-r)
	numer = reduce(op.mul, range(n, n-r, -1), 1)
	denom = reduce(op.mul, range(1, r+1), 1)
	return numer / denom


if __name__ == "__main__":
	plot_all_topologies()
	print("Ok")


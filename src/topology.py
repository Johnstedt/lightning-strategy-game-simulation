import networkx as nx

import plot


def erdos_renyi():
	g = nx.erdos_renyi_graph(2000, 0.00250125)
	return g


def barabasi_albert():
	g = nx.barabasi_albert_graph(2000, 5)
	return g


def plot_all_topologies():
	plot.plot_degree_distribution([erdos_renyi(), barabasi_albert()], [2.9], "topology")
	return True


if __name__ == "__main__":
	plot_all_topologies()
	print("Ok")


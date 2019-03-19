import plot
import simulation
import networkx as nx

def create_price_model():

	test = []

	#for i in range(10):
	history, g = simulation.simulate("presets/price.json")
	test.append(g)
	price = []

	for transaction_size in range(10, 13, 1):
		for e in g.edges:
			data = g.get_edge_data(e[0], e[1])
			g.remove_edge(e[0], e[1])
			data["price"] = data["base_fee_millisatoshi"]
			#print(data["weight"])
			g.add_edge(e[0], e[1], **data)
		#	print(g.get_edge_data(e[0], e[1]))
		print("PRICES FOR SIZE: ", transaction_size)
		price.append(betweenness_centrality(g))

	plot.plot_price_dimensions(price)
	#plot.plot_multiple_histories(test)


def betweenness_centrality(g):
	"""
	Select node based on centrality.
	"""
	l2 = sorted(nx.edge_betweenness_centrality(g, normalized=False, weight="base_fee_millisatoshi").items(),
				key=lambda x: x[1])
	last_edge = l2[len(l2) - 1]
	return fast_price_function(g, last_edge)


def price_function(g, last_edge):
	"""

	Naive price function, use fast_price_function instead.

	Calculates the optimal price by iterating over each fee with the betweenness centrality algorithm.

	"""
	edge_data = g.get_edge_data(last_edge[0][0], last_edge[0][1])
	plot_list = []

	fee_range = range(10, 1500, 1)

	for fee in fee_range:
		edge_data["base_fee_millisatoshi"] = fee
		g.add_edge(last_edge[0][0], last_edge[0][1], **edge_data)
		all_pair = sorted(
			nx.edge_betweenness_centrality(g, normalized=False, weight="base_fee_millisatoshi").items(),
			key=lambda x: x[1])
		bc = [edge[1] for edge in all_pair if edge[0][0] == last_edge[0][0] and edge[0][1] == last_edge[0][1]][0]
		if bc == 0:
			break
		plot_list.append(fee * bc)
		print(fee, " ", bc, " ", fee * bc)

	plot.plot_fee_curve(range(10, 10 + len(plot_list)), plot_list)


def fast_price_function(g, e, algorithm='johnson'):
	"""

	Fast function to find the optimal price for a given edge e.

	1. Calculate the shortest path from all-to-all vertices without going through $C$ with either Floyd-Warshall or
		Johnson. Default is Johnson
	2. Calculate shortest path from $C$ source to all explicitly going through $C$ with Dijkstra.
	3. Compare difference between all-to-all cost with all-to-$V$-to-all, producing a cumulative summation over the
		difference.
	4. Maximizing fee * cumulative difference.

	Plots the given fee * cumulative difference over fee curve.
	"""

	e_data = g.get_edge_data(e[0][0], e[0][1])

	# Remove edge e
	g.remove_edge(e[0][0], e[0][1])

	# Floyd or Johnson
	if algorithm == 'johnson':
		all_pair_shortest_path = nx.floyd_warshall(g, weight="price")
	else:
		all_pair_shortest_path = nx.johnson(g, weight="price")

	# remove all edges from e source, Add edge e
	edges = list(g.out_edges(e[0][0]))  # get all edges of source

	for rm in edges:
		g.remove_edge(rm[0], rm[1])

	e_data["price"] = 0
	g.add_edge(e[0][0], e[0][1], **e_data)

	# Compute single source dijkstras from e source over e.
	edge_to_all = nx.single_source_dijkstra_path_length(g, e[0][0], weight="price")

	path_price_difference = []
	for source in all_pair_shortest_path:
		for destination in all_pair_shortest_path[source]:
			# SOURCE TO V TO DESTINATION
			if source != destination != e[0][0]:
				diff = (all_pair_shortest_path[source][e[0][0]] + edge_to_all[destination]) - all_pair_shortest_path[source][destination]
				if diff < 0:  # TODO: WHAT TO DO WITH TIES?
					path_price_difference.append(-diff)

	fee_range = range(1, 1500, 15)
	plot_list = []

	#print(path_price_difference)


	for r in fee_range:
		plot_list.append(len([p for p in path_price_difference if p >= r]) * r)
	#plot.plot_fee_curve(fee_range, plot_list)
	print(plot_list)

	return plot_list


if __name__ == "__main__":
	create_price_model()

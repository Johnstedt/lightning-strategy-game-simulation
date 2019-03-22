import plot
import simulation
import networkx as nx


def create_price_model():

	test = []

	#for i in range(10):
	history, g = simulation.simulate("presets/price.json")
	test.append(g)

	price = []

	selected_edge = betweenness_centrality(g)

	for p in range(1, 100, 10):
		sum_over_volume = []
		for transaction_size in range(10, 100, 1):
			for e in g.edges:
				data = g.get_edge_data(e[0], e[1])
				g.remove_edge(e[0], e[1])
				data["price"] = data["base_fee_millisatoshi"] + (data["fee_per_millionth"] * transaction_size)
				g.add_edge(e[0], e[1], **data)

			data2 = g.get_edge_data(selected_edge[0][0], selected_edge[0][1])
			g.remove_edge(selected_edge[0][0], selected_edge[0][1])

			data2["price"] = data2["base_fee_millisatoshi"] + (p * transaction_size)
			g.add_edge(selected_edge[0][0], selected_edge[0][1], **data2)

			if len(sum_over_volume) == 0:
				sum_over_volume = fast_price_function(g, selected_edge, (p * transaction_size))
			else:
				sum_over_volume = [x + y for x, y in zip(sum_over_volume, fast_price_function(g, selected_edge, (p * transaction_size)))]
			print(sum_over_volume)

		price.append(sum_over_volume)

	plot.plot_price_dimensions(price)

	base, prop = retrieve_optimal_price(price)

	prop_curve = []
	for n in price:
		prop_curve.append(n[base])

	base_curve = price[prop]

	print("BASE CURVE")
	print(base_curve)
	print("Normalize list")
	print(normalize_list(base_curve))

	print("PROPORTIONAL CURVE")
	print(prop_curve)
	print("Normalize")
	print(normalize_list(prop_curve))


def betweenness_centrality(g):
	"""
	Select node based on centrality.
	"""
	l2 = sorted(nx.edge_betweenness_centrality(g, normalized=False, weight="base_fee_millisatoshi").items(),
				key=lambda x: x[1])
	last_edge = l2[len(l2) - 1]
	return last_edge


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


def fast_price_function(g, e, proportional, algorithm='johnson'):
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
	edges_data = []

	for rm in edges:
		edges_data.append(g.get_edge_data(rm[0], rm[1]))
		g.remove_edge(rm[0], rm[1])

	temp_price = e_data["price"]
	e_data["price"] = proportional
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

	fee_range = range(1, 3000, 30)
	plot_list = []

	e_data["price"] = temp_price
	for i, add in enumerate(edges):
		g.add_edge(add[0], add[1], **edges_data[i])

	for r in fee_range:
		plot_list.append(len([p for p in path_price_difference if p >= r]) * r * proportional)
	#plot.plot_fee_curve(fee_range, plot_list)

	return plot_list


def retrieve_optimal_price(dim):
	base_max = 0
	prop_max = 0
	max_profit = 0
	for i, prop in enumerate(dim):
		for j, base in enumerate(prop):
			if base > max_profit:
				max_profit = base
				base_max = j
				prop_max = i

	return base_max, prop_max


def normalize_list(l):
	tot = sum(l)
	return [x / tot for x in l]


if __name__ == "__main__":
	create_price_model()

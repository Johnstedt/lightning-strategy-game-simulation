import random
import networkx as nx
import simulation


def rebalance_channels(g, day):
	"""
	Add different strategies here.
	First only close and open
	"""
	# Channel close
	close = []

	for n in g.nodes:
		if g.nodes[n]["rebalance_strategy"]["name"] == "sanity_check":
			continue
		else:
			cycles = find_cycles(g, n, [], 3)

			for cycle in cycles:
				cap = get_capacity(g, cycle)

				if g.nodes[n]["rebalance_strategy"]["name"] == "linear_displacement":
					score, size = get_linear_value(g, cycle, cap)
				else:
					score, size = get_edge_bias_value(g, cycle, cap, g.nodes[n]["rebalance_strategy"]["scale"])

				fee = get_fee(g, cycle, size)
				print((size * 2 / fee))
				if (size * 2 / fee) > g.nodes[n]["rebalance_strategy"]["ratio"]:
					print("HAPPENED")
					simulation.offset_liquidity(g, cycle, size)
					cycle.remove(source)
					simulation.pay_routers(g, cycle, day, size)

	return True


def get_capacity(g, cycle):
	least = 0
	previous = None
	for n in cycle:
		if previous is not None:
			if least == 0:
				least = g.get_edge_data(previous, n)["satoshis"]
			elif g.get_edge_data(previous, n)["satoshis"] < least:
				least = g.get_edge_data(previous, n)["satoshis"]

		previous = n

	return least


def get_linear_value(g, cycle, cap):
	out_channel = g.get_edge_data(cycle[0], cycle[1])["satoshis"] + g.get_edge_data(cycle[1], cycle[0])["satoshis"]
	out_to_balanced = g.get_edge_data(cycle[0], cycle[1])["satoshis"] - out_channel/2

	in_channel = g.get_edge_data(cycle[len(cycle)-1], cycle[len(cycle)-2])["satoshis"] + g.get_edge_data(cycle[len(cycle)-2], cycle[len(cycle)-1])["satoshis"]
	in_to_balanced = in_channel/2 - g.get_edge_data(cycle[len(cycle)-1], cycle[len(cycle)-2])["satoshis"]

	if out_to_balanced < in_to_balanced:
		if cap > out_to_balanced:
			return out_to_balanced, out_to_balanced
		else:
			return cap, cap
	else:
		if cap > in_to_balanced:
			return in_to_balanced, in_to_balanced
		else:
			return cap, cap


def get_edge_bias_value(g, cycle, cap, scale):

	out_channel = g.get_edge_data(cycle[0], cycle[1])["satoshis"] + g.get_edge_data(cycle[1], cycle[0])["satoshis"]
	out_to_balanced = g.get_edge_data(cycle[0], cycle[1])["satoshis"] - out_channel/2

	bias_out = 1 - g.get_edge_data(cycle[0], cycle[1])["satoshis"] / out_channel  # Percent from edge

	in_channel = g.get_edge_data(cycle[len(cycle)-1], cycle[len(cycle)-2])["satoshis"] + g.get_edge_data(cycle[len(cycle)-2], cycle[len(cycle)-1])["satoshis"]
	in_to_balanced = in_channel/2 - g.get_edge_data(cycle[len(cycle)-1], cycle[len(cycle)-2])["satoshis"]

	bias_in = g.get_edge_data(cycle[len(cycle)-1], cycle[len(cycle)-2])["satoshis"] / in_channel  # Percent from edge

	if out_to_balanced < in_to_balanced:
		if cap > out_to_balanced:
			return out_to_balanced * (1 + 0.5-bias_out)**scale * (1 + 0.5-bias_in)**scale, out_to_balanced
		else:
			return cap * (1 + 0.5-bias_out)**scale * (1 + 0.5-bias_in)**scale, cap
	else:
		if cap > in_to_balanced:
			return in_to_balanced * (1 + 0.5-bias_out)**scale * (1 + 0.5-bias_in)**scale, in_to_balanced
		else:
			return cap * (1 + 0.5-bias_out)**scale * (1 + 0.5-bias_in)**scale, cap


def find_cycles(g, node, path, depth):
	"""
	Finds all cycles for a node within a defined depth.
	"""

	path.append(node)

	if len(path) != 1:
		if path[0] == node:
			return [path]

	if depth == 0:
		return False

	paths = []
	for l in g.successors(node):
		val = find_cycles(g, l, path.copy(), depth - 1)
		if val:
			paths = paths + val

	return paths


def get_fee(g, route, size):
	previous = None
	fee = 0
	for n in route:
		if previous is not None:
			fee += (g.get_edge_data(previous, n)["base_fee_millisatoshi"]) + (g.get_edge_data(previous, n)["fee_per_millionth"] * size)
		previous = n

	return fee

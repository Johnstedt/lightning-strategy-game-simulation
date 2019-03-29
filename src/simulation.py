"""
python3 -m pip install -U matplotlib
python3 -m pip install networkx pylightning
"""
import networkx as nx
import json
import sys
import numpy
import random

import attachment_strategies as attachment
import plot
import routing
from collections import OrderedDict


def create_node(settings, buf):
	rand_id = '%066x' % random.randrange(16 ** 66)

	return {
		'name': settings['name'],
		# Usual attributes as per rpc, mostly not relevant
		'last_timestamp': 1544034959,
		'globalfeatures': '',
		'nodeid': rand_id,
		'alias': 'johnstedt',
		'color': '000000',
		'global_features': '',
		'addresses': [{'port': 9735, 'address': '73.33.112.94', 'type': 'ipv4'}],

		# Simulation attributes
		'attachment_strategy': settings['attachment_strategy'],
		'price_strategy': settings['price_strategy'],
		'timing_strategy': settings['timing_strategy'],
		'price_model': settings['price_model'],

		'profits': [buf / 10 for n in range(10)],
		'total_profits': 0,
		"base_fee": random.randint(10, 1501),
		"fee_per_millionth": random.randint(1, 100),
		"funding": 30000
	}


def if_main():
	if len(sys.argv) == 1:
		print("SUPPLY ARGS PLZ")
		exit(0)

	for i in range(1, len(sys.argv)):
		if sys.argv[i] == "-preset":
			print(sys.argv[i + 1])
			if sys.argv[i + 1] == "test":
				simulate(json.loads(open("presets/test.json", "r").read()))
		if sys.argv[i] == "-file":
			print(sys.argv[i + 1])


def simulate(env):

	print(json.dumps(env, indent=2))

	g = nx.DiGraph()

	build_environment(env, g)

	print_alive_nodes(g, env)

	history = OrderedDict()
	for node in env["routing_nodes"]:
		history[node["name"]] = [0] * (env['environment']['time_steps'])

	for day in range(env['environment']['time_steps']):
		print("Day: ", day)
		add_survival_history(g, history, day)
		reset_day(g, day)
		for j in range(env['environment']['payments_per_step']):
			route_payments_all_to_all(g, day)

		network_probability_node_creation(g, env)
		check_for_bankruptcy(g, env)
		attachment.manage_channels(g, env)

	print_profit_table(g, env)

	print_alive_nodes(g, env)
	plot.plot_survival_history(history, [])

	return history, g


def build_environment(env, g):

	if env['environment']['initial_mode'] == "stochastic":

		for n in range(0, env['environment']['initial_nodes']):
			settings = numpy.random.choice(env['routing_nodes'],
											p=[i['initial_distribution'] for i in env['routing_nodes']])
			node = create_node(settings, env['environment']['start_buf'])
			attachment.attach(g, node, 5, env)

	else:   # Exact
		nodes = []
		for n in env['routing_nodes']:
			for i in range(int(env['environment']['initial_nodes'] * n['initial_distribution'])):
				nodes.append(create_node(n, env['environment']['start_buf']))

		while len(nodes) > 0:
			selected = random.choice(nodes)
			attachment.attach(g, selected, 5, env)
			nodes.remove(selected)

	return True


def add_survival_history(g, history, day):

	for n in g.nodes:
		history[g.nodes[n]['name']][day] += 1


def route_payments_all_to_all(g, day):

	size = random.randint(1, 100)  # TODO set to sensible value

	source = 0
	dest = 0
	while source == dest:
		source = random.sample(g.nodes, 1)[0]
		dest = random.sample(g.nodes, 1)[0]

	routers = create_liquid_route(g, source, dest, size)
	if not routers:
		return
	else:
		offset_liquidity(g, routers, size)
		routers.remove(source)
		pay_routers(g, routers, day, size)


def is_path_liquid(g, routers, amount):
	previous = None
	for n in routers:
		if previous is not None:
			if g.get_edge_data(previous, n)["satoshis"] < amount:
				return False

		previous = n

	return True


def offset_liquidity(g, routers, amount):  # TODO: ADD FEE
	previous = None
	for n in routers:
		if previous is not None:
			g.get_edge_data(previous, n)["satoshis"] = g.get_edge_data(previous, n)["satoshis"] - amount
			g.get_edge_data(n, previous)["satoshis"] = g.get_edge_data(n, previous)["satoshis"] + amount

		previous = n


def pay_routers(g, routers, day, size):
	previous = None
	for n in routers:
		if previous is not None:
			g.nodes[previous]['profits'][day % 10] += (
				g.get_edge_data(previous, n)["base_fee_millisatoshi"]) + (g.get_edge_data(previous, n)["fee_per_millionth"] * size)

			g.get_edge_data(previous, n)["last_10_fees"][day % 10] += \
				(g.get_edge_data(previous, n)["base_fee_millisatoshi"]) + (g.get_edge_data(previous, n)["fee_per_millionth"] * size)

			g.nodes[previous]['total_profits'] += (
				g.get_edge_data(previous, n)["base_fee_millisatoshi"]) + (g.get_edge_data(previous, n)["fee_per_millionth"] * size)

		previous = n

	return True


def create_liquid_route(g, source, target, liquidity):
	try:
		nodes = routing.dijkstra_liquid_path(g, source, target, liquidity)
	except nx.exception.NetworkXNoPath:
		return False
	return nodes


def network_probability_node_creation(g, env):

	nodes = OrderedDict()
	for node in env["routing_nodes"]:
		nodes[node["name"]] = 0

	for n in g.nodes:
		nodes[g.nodes[n]['name']] += 1

	for node in env["routing_nodes"]:
		nodes[node["name"]] = nodes[node["name"]] / len(g.nodes)

	settings = numpy.random.choice(env["routing_nodes"],  # Verify this works
								p=list(nodes.values()))
	node = create_node(settings, env["environment"]["start_buf"])
	attachment.attach(g, node, 5, env)


def reset_day(g, day):
	for n in g.nodes:
		g.nodes[n]['profits'][day % 10] = 0


def check_for_bankruptcy(g, env):
	changed = False
	remove = []

	for node in g.nodes:

		if sum(g.nodes[node]['profits']) < env['environment']['bankruptcy']:
			print(g.nodes[node]['nodeid'], " Went bankrupt with method: ",
				g.nodes[node]['name'])
			remove.append(node)
			changed = True
	if changed:
		for n in remove:
			g.remove_node(n)


def print_alive_nodes(g, env):
	nodes = OrderedDict()
	for node in env["routing_nodes"]:
		nodes[node["name"]] = 0

	for n in g.nodes:
		nodes[g.nodes[n]['name']] += 1

	s = ""
	for key in nodes:
		s = s + key + ': ' + str(nodes[key]) + '\n'

	print(s)


def print_profit_table(g, env):
	sorted_profit = []
	for n in g.nodes:
		sorted_profit.append(g.nodes[n])

	sorted_profit = sorted(sorted_profit, key=lambda k: k['total_profits'])

	nodes = OrderedDict()
	for node in env["routing_nodes"]:
		nodes[node["name"]] = 0

	for n in sorted_profit:
		print(n['name'], " ", n['total_profits'])
		nodes[n['name']] += n['total_profits']

	s = ""
	for key in nodes:
		print(key)
		print(str(nodes[key]))

		s = s + key + ': ' + str(nodes[key]) + '\n'

	print(s)


if __name__ == "__main__":
	if_main()

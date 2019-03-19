"""
python3 -m pip install -U matplotlib
python3 -m pip install networkx pylightning
"""
import networkx as nx
import json
import sys
import numpy
import random

import strategies.attachment_strategies as attachment
import plot
import routing


def create_node(settings):
	rand_id = '%066x' % random.randrange(16 ** 66)

	return {

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

		'profits': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
		'total_profits': 0,
		"base_fee": random.randint(10, 1501),
		"fee_per_millionth": random.randint(1, 10),
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
				simulate("presets/test.json")
		if sys.argv[i] == "-file":
			print(sys.argv[i + 1])


def simulate(sim_file):
	env = json.loads(open(sim_file, "r").read())
	print(json.dumps(env, indent=2))

	g = nx.DiGraph()

	build_environment(env, g)

	routing_table, _ = nx.floyd_warshall_predecessor_and_distance(g)

	print_alive_nodes(g)

	history = {"barabasi_albert": [0] * (env['environment']['time_steps']),  # TODO make abstract
				"random": [0] * (env['environment']['time_steps'])}

	for i in range(env['environment']['time_steps']):
		print("Day: ", i)
		add_survival_history(g, history, i)
		reset_day(g, i)
		for j in range(env['environment']['payments_per_step']):
			route_payments_all_to_all(g, i, routing_table)   # TODO CHANGE i to day

		network_probability_node_creation(g)
		routing_table = check_for_bankruptcy(g, env)
		attachment.manage_channels(g)

	print_profit_table(g)

	print_alive_nodes(g)
	plot.plot_survival_history(history, [])

	return history, g


def build_environment(env, g):

	if env['environment']['initial_mode'] == "stochastic":

		for n in range(0, env['environment']['initial_nodes']):
			settings = numpy.random.choice(env['routing_nodes'],   # TODO option for exact start
											p=[i['initial_distribution'] for i in env['routing_nodes']])
			node = create_node(settings)
			attachment.attach(g, node, 5)

	else:   # Exact
		nodes = []
		for n in env['routing_nodes']:
			for i in range(int(env['environment']['initial_nodes'] * n['initial_distribution'])):
				nodes.append(create_node(n))

		while len(nodes) > 0:
			selected = random.choice(nodes)
			attachment.attach(g, selected, 5)
			nodes.remove(selected)

	return True


def add_survival_history(g, history, day):
	for n in g.nodes:
		if g.nodes[n]['attachment_strategy'] == "barabasi_albert":
			history["barabasi_albert"][day] += 1
		else:
			history["random"][day] += 1


def route_payments_all_to_all(g, day, routing_table):
	source = 0
	dest = 0
	while source == dest:
		source = random.sample(g.nodes, 1)[0]
		dest = random.sample(g.nodes, 1)[0]

	routers = nx.reconstruct_path(source, dest, routing_table)

	if not is_path_liquid(g, routers, 1000):  # If shortest path isn't liquid, create another one.
		routers = create_liquid_route(g, source, dest, 1000)
		if not routers:
			return

	offset_liquidity(g, routers, 1000)
	routers.remove(source)
	pay_routers(g, routers, day)


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


def pay_routers(g, routers, day):
	previous = None
	for n in routers:
		if previous is not None:
			g.nodes[previous]['profits'][day % 10] += (
				g.get_edge_data(previous, n)["base_fee_millisatoshi"])
			g.get_edge_data(previous, n)["last_10_fees"][day % 10] += \
				(g.get_edge_data(previous, n)["base_fee_millisatoshi"])
			g.nodes[previous]['total_profits'] += (
				g.get_edge_data(previous, n)["base_fee_millisatoshi"])

		previous = n

	return True


def create_liquid_route(g, source, target, liquidity):
	try:
		nodes = routing.dijkstra_liquid_path(g, source, target, liquidity, weight="base_fee_millisatoshi")
	except nx.exception.NetworkXNoPath:
		return False
	return nodes


def network_probability_node_creation(g):
	albert = 0
	randoms = 0
	for n in g.nodes:
		if g.nodes[n]['attachment_strategy'] == "barabasi_albert":   # TODO abstract
			albert += 1
		else:
			randoms += 1

	settings = numpy.random.choice([{"attachment_strategy": "barabasi_albert"}, {"attachment_strategy": "random"}],
								   p=[albert / len(g.nodes), randoms / len(g.nodes)])
	node = create_node(settings)
	attachment.attach(g, node, 5)


def reset_day(g, day):
	for n in g.nodes:
		g.nodes[n]['profits'][day % 10] = 0


def check_for_bankruptcy(g, env):
	changed = False
	remove = []

	for node in g.nodes:

		if sum(g.nodes[node]['profits']) < env['environment']['bankruptcy']:
			print(g.nodes[node]['nodeid'], " Went bankrupt with method: ",
				g.nodes[node]['attachment_strategy'])
			remove.append(node)
			changed = True
	if changed:
		for n in remove:
			g.remove_node(n)

	routing_table, _ = nx.floyd_warshall_predecessor_and_distance(g, weight="base_fee_millisatoshi")
	return routing_table


def print_alive_nodes(g):
	albert = 0
	random = 0
	for n in g.nodes:
		if g.nodes[n]['attachment_strategy'] == "barabasi_albert":
			albert += 1
		else:
			random += 1
	print("Barabasi nodes: ", albert, " Random nodes: ", random)


def print_profit_table(g):
	list2 = []
	for n in g.nodes:
		list2.append(g.nodes[n])

	list2 = sorted(list2, key=lambda k: k['total_profits'])
	cum_albert = 0
	cum_random = 0
	for n in list2:
		print(n['attachment_strategy'], " ", n['total_profits'])
		if n['attachment_strategy'] == "barabasi_albert":
			cum_albert += n['total_profits']
		else:
			cum_random += n['total_profits']

	print("BARABASI TOTAL: ", cum_albert, " RANDOM TOTAL: ", cum_random)


if __name__ == "__main__":
	if_main()

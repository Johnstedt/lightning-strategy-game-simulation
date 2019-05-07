import random
import price_strategies
import rebalancing_strategies
import numpy


def create_channel(node, destination, public):

	if not node["public"]:
		base = 100000000
		prop = 100000000
	else:
		base, prop = price_strategies.get_price_by_strategy(node['price_strategy'], path=node["price_model"])

	return {
		'base_fee_millisatoshi': base,
		'satoshis': node['allocation_strategy'],
		'public': public,
		'destination': destination,
		'source': node['nodeid'],
		'fee_per_millionth': prop,
		'active': True,

		'last_10_fees': [n * (node["allocation_strategy"]/node["original_funding"]) for n in node["profits"]],

		#'last_update': 1550232803,
		#'delay': 144,
		#'message_flags': 1,
		#'channel_flags': 1,
		#'flags': 257,
		#'short_channel_id': '1457217x64x0',
	}


def attach(g, n, m, env, day):
	switch(n['attachment_strategy'])(g, n, m, env, day)

	return True


def barabasi_albert(g, n, m, env, day):

		if m >= len([k for k in g.edges if g.edges[k]["public"]]):
			random_strategy(g, n, m, env, day)
			return False

		targets = [i[0] for i in random.sample([k for k in g.edges if g.edges[k]["public"]], m)]

		g.add_node(n["nodeid"], **n)

		channels = [create_channel(n, target_id, n['public']) for target_id in targets]
		g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

		channels = [create_channel(g.nodes[target_id], n['nodeid'], n['public']) for target_id in targets]
		g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

		for s in range(m):
			reduce_funding(g, n["nodeid"], env)
			remove_profit(g, n["nodeid"], env['environment']['fee'], day)

		return True


def random_strategy(g, n, m, env, day):

	if m >= len(g.nodes):
		targets = g.nodes()
	else:
		targets = random.sample([k for k in g.nodes() if g.nodes[k]["public"]], m)

	g.add_node(n["nodeid"], **n)

	channels = [create_channel(n, target_id, n['public']) for target_id in targets]
	g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

	channels = [create_channel(g.nodes[target_id], n['nodeid'], n['public']) for target_id in targets]
	g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

	for s in range(m):
		reduce_funding(g, n["nodeid"], env)
		remove_profit(g, n["nodeid"], env['environment']['fee'], day)

	return True


def hassan_islam_haque(g, n, m, env, day):

	if m >= len(g.edges):
		random_strategy(g, n, m, env, day)
		return False

	neighbor = [i[0] for i in random.sample([k for k in g.edges if g.edges[k]["public"]], m)]

	g.add_node(n["nodeid"], **n)

	targets = [random.sample([k for k in g.successors(nk) if g.nodes[k]["public"]], 1)[0] for nk in neighbor]

	channels = [create_channel(n, target_id, n['public']) for target_id in targets]
	g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

	channels = [create_channel(g.nodes[target_id], n['nodeid'], n['public']) for target_id in targets]
	g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

	for s in range(m):
		reduce_funding(g, n["nodeid"], env)
		remove_profit(g, n["nodeid"], env['environment']['fee'], day)

	return True


def inverse_barabasi_albert(g, n, m, env, day):

	if m >= len(g.edges):
		random_strategy(g, n, m, env, day)
		return False

	sum_n = 0
	for new in g.nodes:
		if g.nodes[new]["public"] and len(list(g.edges(new))) != 0:
			sum_n += 1 / len(list(g.edges(new)))

	targets = [i for i in numpy.random.choice([k for k in g.nodes if g.nodes[k]["public"] and len(list(g.edges(k))) != 0], m,
											p=[1/len(list(g.edges(new)))/sum_n for new in g.nodes if g.nodes[new]["public"] and len(list(g.edges(new))) != 0])]

	g.add_node(n["nodeid"], **n)

	channels = [create_channel(n, target_id, n['public']) for target_id in targets]
	g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

	channels = [create_channel(g.nodes[target_id], n['nodeid'], n['public']) for target_id in targets]
	g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

	for s in range(m):
		reduce_funding(g, n["nodeid"], env)
		remove_profit(g, n["nodeid"], env['environment']['fee'], day)

	return True


def reduce_funding(g, n, env):
	if g.nodes[n]['funding'] > (2*env['environment']['fee'] + g.nodes[n]["allocation_strategy"]):
		g.nodes[n]['funding'] -= (2*env['environment']['fee'] + g.nodes[n]["allocation_strategy"])
		return True
	else:
		return False


def close_channel(g, f, s):
	if g.has_edge(f, s):
		g.nodes[f]["funding"] += g.get_edge_data(f, s)["satoshis"]
		g.remove_edge(f, s)
	if g.has_edge(s, f):
		g.nodes[s]["funding"] += g.get_edge_data(s, f)["satoshis"]
		g.remove_edge(s, f)

	return True


def manage_channels(g, env, day):
	"""
	Add different strategies here.
	First only close and open
	"""
	# Channel close
	close = []

	for e in g.edges:
		if g.nodes[e[0]]["timing_strategy"]["name"] == "sanity_check":
			continue

		if g.get_edge_data(e[0], e[1])["satoshis"] == 0:
			close.append((e[0], e[1]))
		elif g.nodes[e[0]]["timing_strategy"]["name"] == "close_avg_bankruptcy":
			if sum(g.get_edge_data(e[0], e[1])["last_10_fees"]) / g.get_edge_data(e[0], e[1])["satoshis"] < get_bankruptcy(g.nodes[e[0]], env) / g.nodes[e[0]]["original_funding"]:
				close.append((e[0], e[1]))
		else:
			if sum(g.get_edge_data(e[0], e[1])["last_10_fees"]) / g.get_edge_data(e[0], e[1])["satoshis"] < get_bankruptcy(g.nodes[e[0]], env) / g.nodes[e[0]]["original_funding"] * g.nodes[e[0]]["timing_strategy"]["scale"]:
				close.append((e[0], e[1]))

	for f, s in close:
		close_channel(g, f, s)

	# Open channel
	for n in g.nodes:
		while g.nodes[n]["funding"] > (2*env['environment']['fee'] + g.nodes[n]["allocation_strategy"]):
			switch(g.nodes[n]['attachment_strategy'])(g, g.nodes[n], 1, env, day)
			remove_profit(g, n, 2*env['environment']['fee'], day)

	return True


def get_bankruptcy(node, env):

	return node['original_funding'] * env["environment"]["risk_premium"] / 36.5 + node['original_funding'] * env["environment"]["risk_premium"] / 36.5 + env["environment"]["operational_cost"] / 36.5


def remove_profit(g, node, fee, day):
	g.nodes[node]['profits'][day % 10] -= fee
	g.nodes[node]['total_profits'] -= fee


def switch(policy):
	return {
		"barabasi_albert": barabasi_albert,
		"random": random_strategy,
		"hassan_islam_haque": hassan_islam_haque,
		"inverse_barabasi_albert": inverse_barabasi_albert
	}[policy]

import random
import price_strategies


def create_channel(node, destination):

	base, prop = price_strategies.get_price_by_strategy(node['price_strategy'], path=node["price_model"])

	return {
		'base_fee_millisatoshi': base,
		'satoshis': 5000,
		'public': True,
		'destination': destination,
		'source': node['nodeid'],
		'fee_per_millionth': prop,
		'active': True,

		'last_10_fees': [node['profits'][0] / 5 for n in range(10)],

		#'last_update': 1550232803,
		#'delay': 144,
		#'message_flags': 1,
		#'channel_flags': 1,
		#'flags': 257,
		#'short_channel_id': '1457217x64x0',
	}


def attach(g, n, m, env):
	switch(n['attachment_strategy'])(g, n, m, env)

	return True


def barabasi_albert(g, n, m, env):

		if m >= len(g.edges):
			random_strategy(g, n, m, env)
			return False

		g.add_node(n["nodeid"], **n)

		targets = [i[0] for i in random.sample(g.edges, m)]

		channels = [create_channel(n, target_id) for target_id in targets]
		g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

		channels = [create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
		g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

		return True


def random_strategy(g, n, m, env):

	if m >= len(g.nodes):
		g.add_node(n["nodeid"], **n)
		return False

	targets = random.sample(g.nodes(), m)
	g.add_node(n["nodeid"], **n)

	channels = [create_channel(n, target_id) for target_id in targets]
	g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

	channels = [create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
	g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

	for s in range(m):
		reduce_funding(g, n["nodeid"], env)

	return True


def reduce_funding(g, n, env):
	if g.nodes[n]['funding'] > (2*env['environment']['fee'] + 5000):
		g.nodes[n]['funding'] -= (2*env['environment']['fee'] + 5000)  # TODO Allocation strategy
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


def manage_channels(g, env):
	"""
	Add different strategies here.
	First only close and open
	"""
	# Channel close
	close = []

	for e in g.edges:
		if g.nodes[e[0]]["timing_strategy"] == "sanity_check":
			continue

		if g.get_edge_data(e[0], e[1])["satoshis"] == 0:
			close.append((e[0], e[1]))
		else:
			if sum(g.get_edge_data(e[0], e[1])["last_10_fees"]) / g.get_edge_data(e[0], e[1])["satoshis"] < 0.5:
				close.append((e[0], e[1]))

	for f, s in close:
		close_channel(g, f, s)

	# Open channel
	for n in g.nodes:
		if g.nodes[n]["funding"] > 5000:
			switch(g.nodes[n]['attachment_strategy'])(g, g.nodes[n], 1, env)

	return True


def switch(policy):
	return {
		"barabasi_albert": barabasi_albert,
		"random": random_strategy
	}[policy]

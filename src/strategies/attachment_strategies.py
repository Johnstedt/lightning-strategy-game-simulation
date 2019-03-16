import random


def create_channel(node, destination):
	return {
		'base_fee_millisatoshi': node['base_fee'],
		'satoshis': 5000,
		'public': True,
		'destination': destination,
		'source': node['nodeid'],
		'fee_per_millionth': node['fee_per_millionth'],
		'active': True,

		'last_10_fees': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],

		#'last_update': 1550232803,
		#'delay': 144,
		#'message_flags': 1,
		#'channel_flags': 1,
		#'flags': 257,
		#'short_channel_id': '1457217x64x0',
	}


def attach(g, n, m):
	switch(n['attachment_strategy'])(g, n, m)

	return True


def barabasi_albert(g, n, m):

		if m >= len(g.edges):
			random_strategy(g, n, m)
			return False

		g.add_node(n["nodeid"], **n)

		targets = [i[0] for i in random.sample(g.edges, m)]

		channels = [create_channel(n, target_id) for target_id in targets]
		g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

		channels = [create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
		g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

		return True


def random_strategy(g, n, m):

	if m >= len(g.nodes):
		g.add_node(n["nodeid"], **n)
		return False

	targets = random.sample(g.nodes(), m)
	g.add_node(n["nodeid"], **n)

	channels = [create_channel(n, target_id) for target_id in targets]
	g.add_edges_from(zip([n["nodeid"]] * m, targets, channels))

	channels = [create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
	g.add_edges_from(zip(targets, [n["nodeid"]] * m, channels))

	return True


def manage_channels(g):
	"""
	Add different strategies here.
	First only close and open
	"""
	# Channel close
	for e in g.edges:
		print(e[0])
		#print(g.get_edge_data(e[0], e[1]))
	# exit(1)
	# if sum(e['last_10_fees']) < 20:
	# g.remove_edge(e)
	#		return True

	return True


def switch(policy):
	return {
		"barabasi_albert": barabasi_albert,
		"random": random_strategy
	}[policy]

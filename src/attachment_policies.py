import random


def create_channel(node, destination):

	return {
		'base_fee_millisatoshi': node['base_fee'],
		'satoshis': 5000,
		'destination': destination,
		'short_channel_id': '1457217x64x0',
		'public': True,
		'last_update': 1550232803,
		'source': node['nodeid'],
		'delay': 144,
		'message_flags': 1,
		'channel_flags': 1,
		'fee_per_millionth': node['fee_per_millionth'],
		'flags': 257,
		'active': True,
		'last_10_fees': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
	}


class AttachmentPolicies:

	__barabasi_nodes = None

	def __init__(self):
		self.__barabasi_nodes = []

	def attach(self, g, n, m):

		self.switch(n['attachment_policy'])(g, n, m)

		return True

	def remove_all_barabasi(self, rm):

		self.__barabasi_nodes = [y for y in self.__barabasi_nodes if y != rm]

	def barabasi_albert(self, g, n, m):

		if m >= len(self.__barabasi_nodes):
			self.random(g, n, m)
			return False

		g.add_node(n["nodeid"], **n)

		targets = [self.__barabasi_nodes[i] for i in random.sample(range(len(self.__barabasi_nodes)), m)]

		channels = [create_channel(n, target_id) for target_id in targets]
		g.add_edges_from(zip([n["nodeid"]]*m, targets, channels))

		channels = [create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
		g.add_edges_from(zip(targets, [n["nodeid"]]*m, channels))

		self.__barabasi_nodes.extend(targets)

		self.__barabasi_nodes.extend([n["nodeid"]]*m)

		return True

	def random(self, g, n, m):

		if m >= len(g.nodes):
			g.add_node(n["nodeid"], **n)
			return False

		targets = random.sample(g.nodes(), m)
		g.add_node(n["nodeid"], **n)

		channels = [create_channel(n, target_id) for target_id in targets]
		g.add_edges_from(zip([n["nodeid"]]*m, targets, channels))

		channels = [create_channel(g.nodes[target_id], n['nodeid']) for target_id in targets]
		g.add_edges_from(zip(targets, [n["nodeid"]]*m, channels))

		self.__barabasi_nodes.extend(targets)

		return True

	def manage_channels(self, g):
		"""
		Add different strategies here.
		First only close and open
		"""
		# Channel close
		#for e in g.edges:
			#print(e)
			#exit(1)
			#if sum(e['last_10_fees']) < 20:
				#g.remove_edge(e)
		#		return True

		return True

	def switch(self, policy):
		return {
			"barabasi_albert": self.barabasi_albert,
			"random": self.random
		}[policy]

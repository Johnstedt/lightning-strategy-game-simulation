import random


class AttachmentPolicies:

	__barabasi_nodes = None

	def __init__(self):
		self.__barabasi_nodes = []

	def attach(self, g, n, m):

		self.switch(n['attachment_policy'])(g, n, m)

		return True

	def barabasi_albert(self, g, n, m):

		if m >= len(self.__barabasi_nodes):
			self.random(g, n, m)
			return False

		g.add_node(n["nodeid"], **n)

		targets = [self.__barabasi_nodes[i] for i in random.sample(range(len(self.__barabasi_nodes)), m)]
		g.add_edges_from(zip([n["nodeid"]]*m, targets))

		self.__barabasi_nodes.extend(targets)

		self.__barabasi_nodes.extend([n["nodeid"]]*m)

		return True

	def random(self, g, n, m):

		if m >= len(g.nodes):
			g.add_node(n["nodeid"], **n)
			return False

		targets = random.sample(g.nodes(), m)
		g.add_node(n["nodeid"], **n)

		g.add_edges_from(zip([n["nodeid"]]*m, targets))
		self.__barabasi_nodes.extend(targets)

		return True

	def switch(self, policy):
		return {
			"barabasi_albert": self.barabasi_albert,
			"random": self.random
		}[policy]

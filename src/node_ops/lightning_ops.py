import time
from os.path import expanduser

from lightning import LightningRpc


class LightningOperator:

	rpc_interface = None

	def __init__(self):

		self.rpc_interface = LightningRpc(expanduser("~")+"/.lightning/lightning-rpc")

		print(type(self.rpc_interface.getinfo()))

		self.rpc_interface.connect("03b6384db3982ba0f87bec1155633de02296b650b08290d8c9e811da3a07bcf595@83.8.67.65:9735")

		print(self.rpc_interface.listpeers())

	def populate_graph(self, graph):

		print("Attempt RPC-call to download nodes and channels from the lightning network")
		nodes = []
		print(self.rpc_interface)
		try:
			while len(nodes) == 0:
				peers = self.rpc_interface.listpeers()["peers"]
				if len(peers) < 1:
					time.sleep(2)
				nodes = self.rpc_interface.listnodes()["nodes"]
		except ValueError as e:
			print("Cannot download nodes from the network, are you connected to a peer?")
			print("RPC error: " + str(e))
			return False

		print("Number of nodes found: {}".format(len(nodes)))

		for node in nodes:
			graph.add_node(node["nodeid"], **node)

		"""
		Grab the channels
		"""
		if len(graph.nodes) == 0:
			print("Cannot download channels if nodes do not exist. ")
			return False

		try:

			channels = self.rpc_interface.listchannels()["channels"]
			print("Number of retrieved channels: {}".format(len(channels)))
		except ValueError as e:
			print("Cannot download channels from the network, are you connected to a peer?")
			print("RPC error: " + str(e))
			return False

		for channel in channels:
			graph.add_edge(channel["source"], channel["destination"], **channel)

		return True

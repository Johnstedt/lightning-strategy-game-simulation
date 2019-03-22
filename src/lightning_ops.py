import time
from os.path import expanduser

from lightning import LightningRpc


class LightningOperator:

	rpc_interface = None
	__network = None

	def __init__(self, network):

		self.__network = network

		if self.__network == "mainnet":
			self.rpc_interface = LightningRpc(expanduser("~")+"/.mainnet/lightning-rpc")


			self.rpc_interface.connect("02f6725f9c1c40333b67faea92fd211c183050f28df32cac3f9d69685fe9665432@104.198.32.198:9735")
			#self.rpc_interface.connect("030fe6f75d41d7112afee0f6f0e230095d9036abf19c7f88f416cc7b9ab9e9ef3e@203.206.164.188:9735")
			#self.rpc_interface.connect("03abf6f44c355dec0d5aa155bdbdd6e0c8fefe318eff402de65c6eb2e1be55dc3e@52.15.79.245:9735")
			#self.rpc_interface.connect("03cb7983dc247f9f81a0fa2dfa3ce1c255365f7279c8dd143e086ca333df10e278@46.28.204.21:9735")
			#self.rpc_interface.connect("03e50492eab4107a773141bb419e107bda3de3d55652e6e1a41225f06a0bbf2d56@35.172.33.197:9735")


		else:
			self.rpc_interface = LightningRpc(expanduser("~")+"/.lightning/lightning-rpc")

			self.rpc_interface.connect("03236a685d30096b26692dce0cf0fa7c8528bdf61dbf5363a3ef6d5c92733a3016@50.116.3.223:9734")
			#self.rpc_interface.connect("03782bb858e1ec9c0a4a5ac665ed658c97ced02e723eafc3c56137ab4e2e3caebf@52.8.119.71:9736")
			#self.rpc_interface.connect("02ec66fb12dd5d4943d63e7a1a35d063aec015e1c8b89cee6c9f2db3faf0f6687f@3.93.159.131:19735")
			#self.rpc_interface.connect("0218b92d19de937ef740154d20d3a6f37c44e6381ca72b95789295073664cfdd36@5.95.80.47:9735")


		print(type(self.rpc_interface.getinfo()))

		print(self.rpc_interface.listpeers())

	def isMainnet(self):
		return __network == "mainnet"

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
			graph.add_node(node["nodeid"], object=node)

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

		i = 0
		j = 0
		for channel in channels:

			if (j % 1000) == 0:
				print(j)

			j += 1

			if channel["source"] not in graph.nodes:
				print(channel["source"], "not in list")
				i += 1

			if channel["destination"] not in graph.nodes:
				print(channel["destination"], "not in list")
				i += 1

			graph.add_edge(channel["source"], channel["destination"], **channel)

		print("NOT IN: ", i)
		return True

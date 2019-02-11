from os.path import expanduser

from lightning import LightningRpc


class LightningOperator:

	__lightning = None

	def __init__(self):

		rpc_interface = LightningRpc(expanduser("~")+"/.lightning/lightning-rpc")

		print(type(rpc_interface.getinfo()))

		rpc_interface.connect("03b6384db3982ba0f87bec1155633de02296b650b08290d8c9e811da3a07bcf595@83.8.67.65:9735")

		print(rpc_interface.listpeers())



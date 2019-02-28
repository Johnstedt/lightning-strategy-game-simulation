import heapq
from operator import itemgetter
import random


def select_mesh_invoking_network_candidates(self, graph,  k=3):
	"""
		generates a set of nodes that are not well connected
		for this the start end end nodes of longest paths are retrieved
	"""
	result = set()

	if k < 3:
		k = 3

	candidates = heapq.nlargest(3*k, self.__generate_all_shortest_paths(graph), key=itemgetter(0))

	for _, path in candidates:
		result.add(path[0])
		result.add(path[-1])

	print("IMPROVE_NETWORK: Found {} candidates which are currently bad connected".format(len(result)))
	if len(result) <= k:
		return list(result)
	print("IMPROVE_NETWORK: Sample {} items from the candidates as was requested".format(k))
	tmp = list(result)
	random.shuffle(tmp)
	return tmp[0:k]


def __find_all_shortest_paths(self, graph, cutoff=10):
	"""
	nx has built in support for floyd Warshall
	finds all shortest paths in graph

	generates all shortest paths and yields each item, the format of the output is
	(len, [src, n1,...,n_{m-2}, dest])
	"""

	all_pair_shortest_paths = graph.all_pairs_shortest_path(self.G, cutoff=cutoff)
	for item in all_pair_shortest_paths:
		from_node = item[0]
		paths = item[1]
		for destination, path in paths.items():
			yield (len(path), path)

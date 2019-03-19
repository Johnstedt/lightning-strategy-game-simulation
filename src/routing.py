import networkx as nx
import json
import sys
import numpy
import random

from heapq import heappush, heappop
from itertools import count


def dijkstra_liquid_path(G, source, target, liquidity, weight=None):
	"""Uses Dijkstra's algorithm to find shortest weighted paths.

	THIS METHOD IS MODIFIED TO HANDLE LIQUIDITY CONSTRAINS.
	Stolen from networkx.
	"""

	weight = _weight_function(G, weight)
	cutoff = None
	pred = None
	sources = [source]
	paths = {source: [source] for source in sources}  # dictionary of paths

	G_succ = G._succ if G.is_directed() else G._adj

	push = heappush
	pop = heappop
	dist = {}  # dictionary of final distances
	seen = {}
	# fringe is heapq with 3-tuples (distance,c,node)
	# use the count c to avoid comparing nodes (may not be able to)
	c = count()
	fringe = []
	for source in sources:
		if source not in G:
			raise nx.NodeNotFound("Source {} not in G".format(source))
		seen[source] = 0
		push(fringe, (0, next(c), source))

	while fringe:
		(d, _, v) = pop(fringe)
		if v in dist:
			continue  # already searched this node.
		dist[v] = d
		if v == target:
			break
		for u, e in G_succ[v].items():
			cost = weight(v, u, e)
			if cost is None:
				continue

			if G.get_edge_data(v, u)['satoshis'] < liquidity:
				continue

			vu_dist = dist[v] + cost
			if cutoff is not None:
				if vu_dist > cutoff:
					continue
			if u in dist:
				if vu_dist < dist[u]:
					raise ValueError('Contradictory paths found: negative weights?')
			elif u not in seen or vu_dist < seen[u]:
				seen[u] = vu_dist
				push(fringe, (vu_dist, next(c), u))
				if paths is not None:
					paths[u] = paths[v] + [u]
				if pred is not None:
					pred[u] = [v]
			elif vu_dist == seen[u]:
				if pred is not None:
					pred[u].append(v)

	# The optional predecessor and path dictionaries can be accessed
	# by the caller via the pred and paths objects passed as arguments.

	try:
		val = (dist[target], paths[target])
	except KeyError:
		raise nx.NetworkXNoPath("No path to {}.".format(target))

	(length, path) = val

	return path


def _weight_function(G, weight):
	"""Returns a function that returns the weight of an edge.

	The returned function is specifically suitable for input to
	functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

	Parameters
	----------
	G : NetworkX graph.

	weight : string or function
		If it is callable, `weight` itself is returned. If it is a string,
		it is assumed to be the name of the edge attribute that represents
		the weight of an edge. In that case, a function is returned that
		gets the edge weight according to the specified edge attribute.

	Returns
	-------
	function
		This function returns a callable that accepts exactly three inputs:
		a node, an node adjacent to the first one, and the edge attribute
		dictionary for the eedge joining those nodes. That function returns
		a number representing the weight of an edge.

	If `G` is a multigraph, and `weight` is not callable, the
	minimum edge weight over all parallel edges is returned. If any edge
	does not have an attribute with key `weight`, it is assumed to
	have weight one.

	"""
	if callable(weight):
		return weight
	# If the weight keyword argument is not callable, we assume it is a
	# string representing the edge attribute containing the weight of
	# the edge.
	if G.is_multigraph():
		return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
	return lambda u, v, data: data.get(weight, 1)


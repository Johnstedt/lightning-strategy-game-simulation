# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 16:45:04 2018

@author: Utilisateur
"""
import networkx as nx
import matplotlib
import edges as e

G = nx.DiGraph()
edg = [(1, 2), (1, 2), (1, 2)]
G.add_edges_from(edg)
pos = nx.spring_layout(G)
for i in range(len(edg)):
    e.draw_networkx_multi_edges(G, pos, edgelist=[edg[i]], width=int(10*(i+1)), alpha=1/(i+1), arrows=True, rad=0.3*i)

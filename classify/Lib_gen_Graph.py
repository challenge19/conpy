#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2014 szs <shenzhesi@mail.bnu.edu.cn>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  该程序用于产生各类常见的网络类型

import numpy as np
import random
import networkx as nx
def find_node(p,plist):
	# p, random number
	# plist, 轮盘赌概率
	b,=np.where(plist>=p)
	return b[0]
def scale_free_static(N,K,alpha,beta,directed=True):
	""" generate scale free graph with static model
	Args:
		N: node number
		K: average degree, will add N*K edges
		alpha: indegree power index
		beta: outdegree power index
		directed: if directed graph, default True
	Returns:
		g: Graph, networkx graph
	"""
	if directed:
		g = nx.DiGraph()
		g.add_nodes_from(range(N))
		M = int(N*K)
		IN = [(1.0*i)**(-alpha) for i in xrange(1,N+1)]
		SIN = sum(IN)
		OUT = [(1.0*i)**(-beta) for i in xrange(1,N+1)]
		SOUT = sum(OUT)
		IN = np.array([sum(IN[:i+1])/SIN for i in xrange(N)])
		OUT = np.array([sum(OUT[:i+1])/SOUT for i in xrange(N)])
		edge = set([])
		while len(edge)<M:
			#~ print len(edge)
			pin = random.random()
			pout = random.random()
			ein = find_node(pin,IN)
			eout = find_node(pout,OUT)
			if eout != ein:
				edge.add((eout,ein))
		#~ print edge
		g.add_edges_from(list(edge))
	else:
		beta = alpha
		g = nx.Graph()
		g.add_nodes_from(range(N))
		M = int(N*K)
		IN = [(1.0*i)**(-alpha) for i in xrange(1,N+1)]
		SIN = sum(IN)
		IN = np.array([sum(IN[:i+1])/SIN for i in xrange(N)])
		OUT = IN
		edge = set([])
		while len(edge)<M:
			pin = random.random()
			pout = random.random()
			ein = find_node(pin,IN)
			eout = find_node(pout,OUT)
			if ein != eout:
				#~ 
				if (eout,ein) not in edge and (ein,eout) not in edge:
					edge.add((eout,ein))
		g.add_edges_from(list(edge))
	return g


def continuous_BA(N,m):
	# N num of nodes, add m edges each step
	import random
	import networkx as nx
	m0 = int(m)
	m1 = m-m0
	ns = m0 + 1*(random.random()<m1)
	g = nx.complete_graph(ns)
	nc = [i for i in xrange(ns)] * ns
	for node in xrange(ns,N):
		em = m0 + 1*(random.random()<m1)
		em = min(em,len(g.nodes()))
		cb = {}
		lnc = len(nc)
		i = 0
		while len(cb) < em:
			i = random.randint(0,lnc-1)
			cb[nc[i]]=1
			i += 1
		for i in cb:
			g.add_edge(node,i)
		nc = nc + cb.keys() + [node]*(em)
		g.add_node(node)
	return g 

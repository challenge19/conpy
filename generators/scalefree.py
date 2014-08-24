# -*- coding: utf-8 -*-
"""
Generate for random scale free graph

@author: szs
"""

__author__ = """Zhesi Shen (shenzhesi@mail.bnu.edu.cn)"""

__all__ = ['continuous_ba' ,
                 'static' ]

import random
import numpy as np
import networkx as nx

def continuous_ba(n, m, seed=None):
    """Return a scale free random graph.

    Parameters
    ----------
    n : int
        The number of nodes.
    m : float
        Number of added edges each step.
    seed : int, optional
        Seed for random number generator (default=None). 
    
    Returns
    ----------
    g : Graph
        A NetworkX Graph
    
    """
    
    if not seed is None:
        random.seed(seed)
    
    m0 = int(m)
    m1 = m-m0
    ns = m0 + 1*(random.random()<m1)
    g = nx.complete_graph(ns)
    nc = [i for i in xrange(ns)] * ns
    for node in xrange(ns,n):
        em = m0 + 1*(random.random()<m1)
        em = min(em,len(g.nodes()))
        cb = {}
        lnc = len(nc)
        i = 0
        while len(cb) < em:
            i = random.randint(0,lnc-1)
            cb[nc[i]]=1
            i += 1
        g.add_edges_from([(node, i) for i in cb])
#        for i in cb:
#            g.add_edge(node,i)
        nc = nc + cb.keys() + [node]*(em)
        g.add_node(node)
    return g


def find_node(p,plist):
    # p, random number
    # plist, 轮盘赌概率
    b,=np.where(plist>=p)
    return b[0]
def static(N,K,alpha_in,alpha_out,directed=True):
    """ generate scale free graph with static model
        
    Parameters
    -----------
    N : int
        The number of nodes.
    K : float
        The average degree, will add N*K edges
    alpha_in : float
        The indegree power index
    alpha_out : float
        The outdegree power index
    directed: bool, optional (default=True)
        If True return directed graph.
    
    Returns
    ----------
    g : Graph
        A NetworkX graph or directed graph
    
    """
    
    if directed:
        g = nx.DiGraph()
        g.add_nodes_from(range(N))
        M = int(N*K)
        IN = [(1.0*i)**(-alpha_in) for i in xrange(1,N+1)]
        SIN = sum(IN)
        OUT = [(1.0*i)**(-alpha_out) for i in xrange(1,N+1)]
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
        alpha_out = alpha_in
        g = nx.Graph()
        g.add_nodes_from(range(N))
        M = int(N*K)
        IN = [(1.0*i)**(-alpha_in) for i in xrange(1,N+1)]
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

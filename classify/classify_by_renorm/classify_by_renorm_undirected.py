# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 14:24:07 2014

Classify undirected graph by renorm.
@author: szs
"""

__authors__ = "Zhesi Shen(shenzhesi@mail.bnu.edu.cn)\n"


__all__ = ['find_intermittent_nodes_undirected',
           'find_redundant_nodes_undirected',
           'find_critical_nodes_undirected',
           'classify_undirected_graph']

import networkx as nx
import random

import sys 
sys.path.append("..")
from classify_by_add_node import find_critical_nodes_undirected

def add_weight(g, random_weight=False):

    h = g.copy()
    for (u,v) in g.edges():
        if random_weight:
            h.add_edge(u, v, weight=random.random()+1)
        else:
            h.add_edge(u, v, weight=1.0)
    return h
    
def get_weight(g, x, s):
    try:
        return g[x][s]['weight']
    except:
        try:
            #~ print 1
            return g[s][x]['weight']
        except:
            #~ print 2
            return 0.0

def rm_leaf(g, node):
    h = g.copy()
    
    nb = h.neighbors(node)[0]
    nbnb = h.neighbors(nb)
    nbnb.remove(node)
    edge = [nb, node]
    h.remove_nodes_from(edge)

    return [(node,nbnb,'x')], h

def turn_2_leaf(g):
    h = g.copy()
    h2 = [i for i in h if h.degree(i) > 1]
    if len(h2) == 0:
        return h
    s = random.choice(h2)

    ##  处理每个degree > 1的节点
    # 处理形如 [(x, i), (x, j), (y, i), (y, k)] 的情况
            
    neighbors_of_s = h.neighbors(s)
    
    # choose the first as x node
    if s in neighbors_of_s:
        x = s
    else:
        x = neighbors_of_s[0]
    #~ print x,i, h[x][i]
    w_x = [(x, i) for i in h] + [(i, x) for i in h]

    # the left node are  y_all
    y_all = neighbors_of_s
    y_all.remove(x)

    for y in y_all:
        w_y = set([(y, i) for i in h] + [(i, y) for i in h] +w_x)
        w_y = {(u, v): get_weight(h, u, v) for u,v in w_y }
        ## add new link (y, j), or change link weight if j == k
            ## calculate new weight
        wys = w_y[(y, s)]
        for i in h:
            w_y[(y, i)] = round(w_y[(y, i)] - 1.0*w_y[(x,i)]*wys/w_y[(x, s)], 8)

        wsy = w_y[(s, y)]
        for i in h:
            w_y[(i, y)] = round(w_y[(i, y)] - 1.0*w_y[(i, x)]*wsy/w_y[(s, x)], 8)
        for i in h:
            if 1e-15 < w_y[(y, i)] or w_y[(y, i)] < -1e-15:
                h.add_edge(y, i, weight=w_y[(y, i)])
            else:
                try:
                    h.remove_edge(y, i)
                except:
                    continue
    return h
    
def find_leaf(g):
    return [i for i in g if len(g.neighbors(i)) == 1]

def rm_edge(g):
    h = g.copy()
    
    leaf = find_leaf(h)
    if len(leaf) > 0:
        node = random.choice(leaf)
        ed, h = rm_leaf(h, node)
    else:
        h = turn_2_leaf(h)
        leaf = find_leaf(h)
        if len(leaf) == 0:
            return [], h
        node = random.choice(leaf)
        ed, h = rm_leaf(h, node)
        
    return ed,h
    
def get_tree(g, cut):
    h = g.copy()
    if g.number_of_nodes() == 1:
        node = g.nodes()[0]     
        if g.number_of_edges() == 0:
            cut += [(node,[],'i')]
    else:
        ed, h = rm_edge(h)
        cut += ed
        components = nx.connected_component_subgraphs(h)
        for gi in components:
            cut =  get_tree(gi, cut)
    return cut

def get_ni(cut):
    ni = []
    unknow = cut[:]
    flag = 1
    while flag:
        flag = 0
        un = []
        for i in unknow:
            node, nb, state = i
            if state == 'i':
                ni.append(node)
                flag = 1
            else:
                if node not in ni:
                    for j in nb:
                        if j in ni:
                            ni.append(node)
                            flag = 1
                            break
                    else:
                        un.append(i)
        unknow = un[:]
    return ni
            
        
def find_intermittent_nodes_undirected(g):
    """ return node_int """
    tree = []
    node_cri = find_critical_nodes_undirected(g)    
    for gi in nx.connected_component_subgraphs(g):
        tree += get_tree(gi,[])
    node_int = []
    for i in xrange(len(tree)):
        node,nb,_ = tree[i]
        if node in node_cri:
            tree[i] = (node, nb, 'c')
    node_int = get_ni(tree)
    return node_int

def find_redundant_nodes_undirected(g):
    """ return node_red """
    
    node_int = find_intermittent_nodes_undirected(g)
    node_cri = find_critical_nodes_undirected(g)
    node_red = list(set(g.nodes()) - set(node_int) - set(node_cri))
    return node_red



def classify_undirected_graph(g):
    """ return (node_cri, node_int, node_red) """
    
    node_int = find_intermittent_nodes_undirected(g)
    node_cri = find_critical_nodes_undirected(g)
    if len(node_cri) == 0 and len(node_int) == 0:
        node_int = g.nodes()
    node_red = list(set(g.nodes()) - set(node_int) - set(node_cri))
    return (node_cri, node_int, node_red)



def test():
    import classify_by_add_node as can
#    from package import Lib_struct_renorm as lsr 
    g = nx.Graph()
    g = nx.erdos_renyi_graph(100, 0.02)
#    g = nx.path_graph(16)
    """
    g.add_edges_from([(0, 1), 
                      (0, 2),
                      (0, 3),
                      (2, 4),
                      (2, 5),
                      (4, 5),
                      (3, 3)])
    """
    g = add_weight(g, 1)
    nre = can.find_redundant_nodes_undirected(g)
    nc, ni, nr = classify_undirected_graph(g)
    print nr
    print nre
    
    return 0
    
if __name__ == '__main__':
    test()

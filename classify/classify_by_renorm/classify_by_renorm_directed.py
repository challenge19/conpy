# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 14:24:07 2014

Classify directed graph by renorm.
@author: szs
"""

__authors__ = "Zhesi Shen(shenzhesi@mail.bnu.edu.cn)\n"


__all__ = ['find_intermittent_nodes_directed',
           'find_redundant_nodes_directed',
           'find_critical_nodes_directed',
           'classify_directed_graph']

import networkx as nx
import random

import sys 
sys.path.append("..")
from classify_by_add_node import find_critical_nodes_directed

def add_weight(g, random_weight=False):
    import random
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
    
    x = h.predecessors(node)[0]             # x = predecessor_of_i
    
    # remove edge (x, j)
    successors_of_x = h.successors(x)
    successors_of_x.remove(node)
    for xs in successors_of_x:         # remove edges from x to x's successors
        h.remove_edge(x, xs)
    # add edge (x, m), (x, n)
    successors_of_i = h.successors(node)
    for m in successors_of_i:           #  add edges from x to i's successors
        h.add_edge(x, m, weight=h[node][m]['weight'])
        #~ print ps,jss
    
    h.remove_node(node)

    return (node,successors_of_x,'x'), h

def turn_2_leaf(g):
    h = g.copy()
    h2 = [i for i in h if h.in_degree(i) > 1]
    i = random.choice(h2)

    ##  处理每个degree > 1的节点
    # 处理形如 [(x, i), (x, j), (y, i), (y, k)] 的情况
            
    predecessors_of_i = h.predecessors(i)
    
    # choose the first as x node
    x = predecessors_of_i[0]
    #~ print x,i, h[x][i]
    weight_edge_xi = h[x][i]['weight']
    successors_of_x = h.successors(x)
    # the left node are  y_all
    y_all = predecessors_of_i[1:]
    for y in y_all:
        
        weight_edge_yi = h[y][i]['weight']
        successors_of_y = h.successors(y)
        
        """
        #~ if len(ys) < len(xs):
            #~ xs,ys = ys, xs
            #~ x,y = y,x
        """
        
        ## add new link (y, j), or change link weight if j == k
        for j in successors_of_x:
            weight_edge_xj = h[x][j]['weight']
            
            try:
                weight_edge_yj = h[y][j]['weight']
            except:
                weight_edge_yj = 0.0
            
            ## calculate new weight, if 0 remove the link
            try:
                new_weight_edge_yj = weight_edge_yj - 1.0*weight_edge_yi*weight_edge_xj/weight_edge_xi
                #~ new_weight_edge_yj = round(new_weight_edge_yj, 10)
            except:
                print weight_edge_yi, h.edges(data=True)
                raise SystemExit
            
            #~ print y,j,new_weight_edge_yj
            if 1e-10 < new_weight_edge_yj or new_weight_edge_yj < -1e-10:
                h.add_edge(y, j, weight=new_weight_edge_yj)
            else:
                try:
                    h.remove_edge(y,j)
                except:
                    continue
        # remove link (y ,i)
        try:
            h.remove_edge(y, i)
        except:
            continue
    return h
    
def find_leaf(g):
    return [i for i in g if g.in_degree(i) == 1]

def rm_edge(g):
    h = g.copy()
    
    leaf = find_leaf(h)
    if len(leaf) > 0:
        node = random.choice(leaf)
        ed, h = rm_leaf(h, node)
    else:
        h = turn_2_leaf(h)
        leaf = find_leaf(h)
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
        cut += [ed]
        components = nx.weakly_connected_component_subgraphs(h)
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
            
        
def find_intermittent_nodes_directed(g):
    tree = []
    node_cri = find_critical_nodes_directed(g)    
    for gi in nx.weakly_connected_component_subgraphs(g):
        tree += get_tree(gi,[])
    node_int = []
    for i in xrange(len(tree)):
        node,nb,_ = tree[i]
        if node in node_cri:
            tree[i] = (node, nb, 'c')
    node_int = get_ni(tree)
    return node_int

def find_redundant_nodes_directed(g):
    node_int = find_intermittent_nodes_directed(g)
    node_cri = find_critical_nodes_directed(g)
    node_red = list(set(g.nodes()) - set(node_int) - set(node_cri))
    return node_red



def classify_directed_graph(g):
    """ return (node_cri, node_int, node_red) """
    
    
    node_int = find_intermittent_nodes_directed(g)
    node_cri = find_critical_nodes_directed(g)
    node_red = list(set(g.nodes()) - set(node_int) - set(node_cri))
    return (node_cri, node_int, node_red)



def test():
    import classify_by_add_node as can
#    from package import Lib_struct_renorm as lsr 
    g = nx.Graph()
    g = nx.erdos_renyi_graph(100, 0.04, directed=True)
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
    nre = can.find_redundant_nodes_directed(g)
    nc, ni, nr = classify_directed_graph(g)
    print nre
    print set(nr) - set(nre)
    print set(nre) - set(nr)
    
    return 0
    
if __name__ == '__main__':
    test()

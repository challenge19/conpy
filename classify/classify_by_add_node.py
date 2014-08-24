#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2014 szs <shenzhesi@mail.bnu.edu.cn>
#  

#  
#  
import numpy as np
import networkx as nx
from Lib_cal_control import *

## ------------ directed -----------------------##
def classify_directed_graph(g):
    node_cri = find_critical_nodes_directed(g)
    node_red = find_redundant_nodes_directed(g)
    node_int = list(set(g.nodes()) - set(node_cri) - set(node_red))
    return (node_cri, node_int, node_red)


def find_critical_nodes_directed(g):
    node_cri = [i for i in g if g.in_degree(i) == 0]
    return node_cri

def find_redundant_nodes_directed(g):
    unmatched_nodes = find_unmatch_nodes(g)
    n_unmatched = len(unmatched_nodes)
    Nd = max(1,n_unmatched)
    matched_nodes = [i for i in g.nodes() if i not in unmatched_nodes]
    redundant_nodes = []
    for i in matched_nodes:
        h = g.copy()
        h.add_edge('add',i)
        unmatch = find_unmatch_nodes(h)
        if len(unmatch) > Nd:
            redundant_nodes.append(i)
    #~ print redundant_nodes
    return redundant_nodes

def find_intermittent_nodes_directed(g):
    node_cri = find_critical_nodes_directed(g)
    node_red = find_redundant_nodes_directed(g)
    node_int = list(set(g.nodes()) - set(node_cri) - set(node_red))
    return node_int
    

## ------------- undirected ---------------- ##

def classify_undirected_graph(g):
    node_cri = find_critical_nodes_undirected(g)
    node_red = find_redundant_nodes_undirected(g)
    node_int = list(set(g.nodes()) - set(node_cri) - set(node_red))
    return (node_cri, node_int, node_red)

def find_critical_nodes_undirected(g):
    node_cri = [i for i in g if g.degree(i) == 0]
    return node_cri

def find_redundant_nodes_undirected(g):
    redundant_nodes = []
    nodes = g.nodes()
    node_cri = find_critical_nodes_undirected(g)
    
    G2 = np.transpose(nx.adjacency_matrix(g))
    G2 = np.array(G2)
    
    a=np.linalg.eigvalsh(G2)
    evals = [0 if abs(ar) < 1e-12 else round(ar,12) for ar in a]
    ce = {i:evals.count(i) for i in evals}
    ces = sorted(ce.items(),key=lambda e:e[1],reverse=True)
    eig = ces[0][0]
    try:
        num0=ce[0]
        eig = 0
    except:
        num0 = -1
    if eig == 1.0:
        eig = ces[1][0]
    
    N=len(nodes)
    I=np.identity(N)
    G3=(eig*I-G2)
    non_c=(i for i in nodes if i not in node_cri)
    
    rank_G = mranksvd(G3)
    G5 = np.zeros((N,N+1))
    G5[:N,:N]=G3
    for i in non_c:
        G5[i,N]=1
        rank_G_add=mranksvd(G5)
        G5[i,N]=0
        if rank_G==rank_G_add:
            redundant_nodes.append(i)
    return redundant_nodes

def find_intermittent_nodes_undirected(g):
    node_cri = find_critical_nodes_undirected(g)
    node_red = find_redundant_nodes_undirected(g)
    node_int = list(set(g.nodes()) - set(node_cri) - set(node_red))
    return node_int
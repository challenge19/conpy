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
#  
import numpy as np
import networkx as nx

#import StructuralRenorm.package.Lib_struct_renorm as lsr

def add_weight(g, random_weight=False):
    import random
    h = g.copy()
    for (u,v) in g.edges():
        if random_weight:
            h.add_edge(u, v, weight=random.random()+1)
        else:
            h.add_edge(u, v, weight=1.0)
    return h


def cal_Nd(g):
    lg = lsr.rm_weighted_leaf(g)
    rn1 = lg.number_of_nodes()
    lg = lsr.rm_weighted_2nd(lg)
    rn2 =  lg.number_of_nodes()
    return max(1, rn2)

def cal_nr_byrenorm(G):
    h = lsr.add_weight(G, 1)
    h = h.to_directed()
    Nd = cal_Nd(h)
    nc = [i for i in G if G.degree(i) == 0]
    nr = []
    for i in h:
        if i in nc:
            continue
        ch = h.copy()
        ch.add_edge(1000, i, weight=1.0)
        nd = cal_Nd(ch)
        if Nd != nd:
            nr.append(i)
    return nr

def mranksvd(A,tol=1e-12):
    s=np.linalg.svd(A,compute_uv=0)
    #~ print s
    mrow,mcol = A.shape
    s = np.abs(s)
    #~ print s.shape
    nn = np.sum(s<tol)
    #~ print m,la-nn 
    return mrow-nn


def cal_exact_Nd_simple(H, random_weight=False):
    """return (Nd, N-Rank) """
    G = H.copy()
    N = H.number_of_nodes()
    try:
        G2 = nx.adjacency_matrix(G, weight = 'weight')
        #~ print 'weight'
    except:
        G2 = nx.adjacency_matrix(G)
    if random_weight:
        G2 = np.array(G2)*np.random.random((N, N))
    rank_G = mranksvd(G2)
    return max(1, N-rank_G), N-rank_G

def find_unmatch_nodes(G):
    match=[]
    nodes = G.nodes()
    g = nx.DiGraph()
    gg = nx.DiGraph()
    p0 =['+'+str(i) for i in nodes]
    m0 = ['-'+str(i) for i in nodes]
    for ed in G.edges():
        ed1,ed2 = ed
        g.add_edge('+'+str(ed1),'-'+str(ed2),capacity=1.0)
    source = 'source'
    sink = 'sink'
    for i in p0:
        #~ print p0
        g.add_edge(source,i,capacity=1.0)
    for i in m0:
        g.add_edge(i,sink,capacity=1.0)
    flow,F = nx.ford_fulkerson(g,source,sink)
    for i in F:
        if i not in [sink,source]:
            for j in F[i]:
                if j not in [sink,source]:
                    #~ print i,j,F[i][j]
                    if F[i][j] > 0:
                        match.append(int(j[1:]))
    #~ print len(set(match))
    unmatch = set(nodes)
    unmatch = unmatch - set(match)
    #~ print unmatch
    return unmatch

def find_redundant_nodes(G):
    unmatched_nodes = find_unmatch_nodes(G)
    lunmatched = len(unmatched_nodes)
    Nd = max(1,lunmatched)
    matched_nodes = [i for i in G.nodes() if i not in unmatched_nodes]
    redundant_nodes = []
    for i in matched_nodes:
        h = G.copy()
        h.add_edge(10000+i,i)
        unmatch = find_unmatch_nodes(h)
        if len(unmatch) > Nd:
            redundant_nodes.append(i)
    #~ print redundant_nodes
    return len(redundant_nodes)


def find_exact_redundant_nodes_dir(G):
    exact_redundant_nodes = []
    nodes = G.nodes()
    ecn = find_exact_critical_nodes(G)
    G2 = np.transpose(nx.adjacency_matrix(G))
    G2 = np.array(G2)*np.random.random((len(nodes),len(nodes)))
    a=np.linalg.eigvals(G2)
    evals = []
    len_a=len(a)
    for i in xrange(len_a):
        ar,ai = a[i].real,a[i].imag
        if abs(ar) < 1e-12:
            ar = 0
        if abs(ai) < 1e-12:
            ai = 0
            evals.append(round(ar,12))
        else:
            evals.append(round(ar,12) + round(ai,12)*1j)
    G_mi_num=[]
    dic2={}
    evals = list(set(evals))
    I=np.identity(len_a)
    G_mi_num = {}
    for i in evals:
        B=(i*I-G2)
        b=mranksvd(B)
        dim=len_a-b
        G_mi_num[i] = dim
    Ge = sorted(G_mi_num.items(),key=lambda e:e[1],reverse=True)
    eig = Ge[0][0]
    #~ print len(evals),G_mi_num[eig]
    try:
        n0 = G_mi_num[0]
        if Ge[0][1] == 1:
            eig = 0
    except:
        n0 = -1
    #~ n0 = len_a - mranksvd(G2)
    N=len(G2)
    I=np.identity(N)
    G3=(eig*I-G2)
    G4=np.transpose(G3)
    non_c=(i for i in nodes if i not in ecn)
    #~ print ecn,len(non_c)
    exact_redundant_nodes=[]
    rank_G = mranksvd(G3)
    G5 = np.zeros((N,N+1))
    G5[:N,:N]=G4
    for i in non_c:
        G5[i,N]=1
        rank_G_add=mranksvd(G5)
        G5[i,N]=0
        if rank_G==rank_G_add:
            exact_redundant_nodes.append(i)
    #~ print exact_redundant_nodes
    return len(exact_redundant_nodes),n0


def find_exact_redundant_nodes_undir(G,Nr=True):
    exact_redundant_nodes = []
    nodes = G.nodes()
    ecn = find_exact_critical_nodes(G)
    G2 = np.transpose(nx.adjacency_matrix(G))
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
    if not Nr:
        return 0,num0
    if eig == 1.0:
        eig = ces[1][0]
    N=len(nodes)
    I=np.identity(N)
    G3=(eig*I-G2)
    non_c=(i for i in nodes if i not in ecn)
    exact_redundant_nodes=[]
    rank_G = mranksvd(G3)
    G5 = np.zeros((N,N+1))
    G5[:N,:N]=G3
    for i in non_c:
        G5[i,N]=1
        rank_G_add=mranksvd(G5)
        G5[i,N]=0
        if rank_G==rank_G_add:
            exact_redundant_nodes.append(i)
    return len(exact_redundant_nodes),num0


def find_exact_critical_nodes(G):
    # find critical nodes
    A = nx.adjacency_matrix(G)
    Nrow,Ncol= A.shape
    sA = np.sum(A,0)
    ex_cri_nodes = [i for i in xrange(Nrow) if sA[0,i] == 0]
    return ex_cri_nodes



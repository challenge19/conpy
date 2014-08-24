#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import networkx as nx
import numpy as np
import random
import Lib_gen_Graph as lig
import Lib_cal_control as lcc
import classify_by_add_node as can
import classify_by_renorm.classify_by_renorm_undirected as cru
#import StructuralRenorm.package.Lib_struct_renorm as lsr


import os
def cal_undirected(t,j,N):
    print N,j,t,os.getpid()
    #~ G = lig.scale_free_static(N,j,0.5,0.5,directed=False)
    #~ G = lig.continuous_BA(N,j)
    G = nx.erdos_renyi_graph(N,np.log(N)*j/N)
    G = lcc.add_weight(G, 1)
    #~ _, rk = lcc.cal_exact_Nd_simple(G)
    nc, ni, nr = 0,0,0
    #~ nc, ni, nr = can.classify_undirected_graph(G)
    #~ nc, ni, nr = len(nc), len(ni), len(nr)
    #~ print nc, ni, nr
    nc, ni, nr = cru.classify_undirected_graph(G)
    nc, ni, nr = len(nc), len(ni), len(nr)
    return (j,1.0*nc/N,1.0*nr/N,1.0*ni/N)


def cal_directed(t,j,N):
    print N,j,t,os.getpid()
    #~ G = lig.scale_free_static(N,j,0.5,0.5,directed=False)
    #~ G = lig.continuous_BA(N,j)
    G = nx.erdos_renyi_graph(N,np.log(N)*j/N, directed=True)
#    G = lic.add_weight(G, 1)
    nc, ni, nr = 0,0,0
    nc, ni, nr = can.classify_directed_graph(G)
    nc, ni, nr = len(nc), len(ni), len(nr)    
    return (j,1.0*nc/N,1.0*nr/N,1.0*ni/N)




def cal_multiprocess():
    from multiprocessing import Pool    
    pool = Pool(4)
    simtime = 100
    for N in [100]:
        for y in xrange(50):
            #~ results = [pool.apply_async(cal_classification,(x,j,N)) for j in np.arange(0.1, 0.5, 0.05)]
            results = [pool.apply_async(cal_undirected,(x,j,N)) for j in np.arange(0.1, 1.5, 0.1) for x in xrange(simtime)]
            roots = [r.get() for r in results]
            #~ with open('degree-redundant-UNDIR.txt-ba'+str(N),'a') as f:
            with open('renorm-weighted-degree-nr-UNDIR.txt-er'+str(N),'a') as f:
                for ak,nc, nr, ni in roots:
                    print>>f, ak, nc, nr, ni
    
if __name__ == '__main__':
    while 1:
        print cal_undirected(1, 0.5, 100)
    #~ cal_multiprocess()

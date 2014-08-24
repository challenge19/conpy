import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
#a = np.loadtxt('degree-nr-DIR.txt-sf400')

def read_data(fname, id_name):
    d = pd.read_table(fname, sep=' ', header=None, names = id_name)
    d = d.groupby('k').mean()
    return d

def plot_data(gt, n):
    plt.plot([0.1, 1.5], [1.0/n]*2, 'k')
    fname = 'weighted-degree-nr-UNDIR.txt-%s%s'%(gt, n)
    if os.path.isfile('./%s'%fname):
        d = read_data(fname, ['k', 'nd', 'nr', 'n0'])
        d['nr'].plot(marker='o', lw=0, zorder=10, label = 'nr-ad-%s'%n)
    else:
        print 'file not exist'
    
    fname = 'renorm-weighted-degree-nr-UNDIR.txt-%s%s'%(gt, n)
    if os.path.isfile('./%s'%fname):
        d = read_data(fname, ['k', 'nd', 'nr', 'n0', 'rk'])
        d['nr'].plot(marker='o', lw=0, zorder=10, label = 'nr-rn-%s'%n)
        d['rk'].plot(marker='o', lw=0, zorder=10, label = 'rk-%s'%n)
    else:
        print 'file not exist'

#~ plot(200)
#~ plot1(200)
#~ plotr(200)
plot_data('er', 100)
plot_data('er', 200)
plt.legend(loc='best')
plt.show()

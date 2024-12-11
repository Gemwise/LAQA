import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
import scipy.io as scio

os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/delay_h264_h265_sim")
data_1 = scio.loadmat("./4k_0.02_0.5_all_265/mean_delay.mat")
p1080 = data_1['mean_delay'][0]
k2 = data_1['mean_delay'][2]
k4 = data_1['mean_delay'][1]


def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    color = 'red'
    if label == '1080P':
        color = '#2F7FC1'
    elif label == '2K':
        color = '#96C37D'
    else:
        color = '#D8383A'
    return plt.plot(x, y, label=label, *args, **kwargs,linewidth=1.5,color=color) if plot else (x, y)

with plt.style.context(['science','grid']):
    fig, ax = plt.subplots() 
    ax.set(xlabel='Transport Latency$(ms)$')    
    ax.set(ylabel='CDF $F(x)$')
    cdf(p1080,"1080P")
    cdf(k2,"2K")
    cdf(k4,"4K")
    plt.autoscale(tight = True)
    plt.ylim(0,1.0)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('./Delay.pdf',format='pdf',dpi=300)


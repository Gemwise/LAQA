import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
import seaborn as sns
from scipy import stats
import scipy.io as scio


os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation")
os.chdir("./result/265_all_hn_decode")
da = scio.loadmat("mean_QoE_metrics.mat")
nod = da['mean_QoE_metrics'][3]
k4 = da["mean_QoE_metrics"][1]

qoe = [np.mean(nod),np.mean(k4)]

qal = scio.loadmat("mean_qualities.mat")
nod_q = qal['mean_qualities'][3]
k4_q = qal['mean_qualities'][1]

quality = [np.mean(nod_q),np.mean(k4_q)]

var_da = scio.loadmat("mean_variance.mat")
nod_v = var_da['mean_variance'][3]
k4_v = var_da['mean_variance'][1]

var = [np.mean(nod_v),np.mean(k4_v)]


decode = scio.loadmat("mean_decode_delay.mat")['mean_decode_delay'][1]
deco = np.mean(decode)
 
trans_da = scio.loadmat("mean_delay.mat") 
nod_trans = trans_da['mean_delay'][3]
k4_trans = trans_da['mean_delay'][1]

trans = [np.mean(nod_trans),np.mean(k4_trans)-deco]




with plt.style.context(['science','grid']):
    x = np.arange(3)
    n4k = [quality[0],var[0],qoe[0]]
    k4 = [quality[1],var[1],qoe[1]]
    bar_with = 0.3
    tick_label = ['Quality','Variance','QoE']
    plt.bar(x,n4k,bar_with,align='center',color = '#96C37D',label = 'w/o Decoding Latency')
    plt.bar(x+bar_with,k4,bar_with,align='center',color = '#D8383A',label = 'w/   Decoding Latency')
    plt.ylabel("The impact of decoding latency")
    plt.xticks(x+bar_with/2,tick_label)
    for i in range(3):
        formatted_x = f'{n4k[i]:.2f}'
        plt.annotate(formatted_x,(i,n4k[i]),ha = 'center', fontweight='bold')
    for i in range(3):
        formatted_x = f'{k4[i]:.2f}'
        plt.annotate(formatted_x,(i+bar_with,k4[i]),ha = 'center', fontweight='bold')
    

    plt.legend(loc='best')
    plt.tight_layout()
    os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/sim_part/")
    plt.savefig("nodecode3"+'.pdf',format='pdf',dpi=300)


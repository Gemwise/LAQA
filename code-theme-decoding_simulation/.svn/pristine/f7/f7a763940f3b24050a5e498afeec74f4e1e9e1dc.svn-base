#%% import
import numpy as np
import matplotlib.pyplot as plt 

font = {'family': 'serif',
        'serif': 'Times New Roman',
        'weight': 'normal'}
plt.rc('font', **font)

import scienceplots
import os
import csv
from scipy import stats

os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/size2level")

data1 = [6,8,12,18,30,47,59,76,96,123]
data2 = [5,7,10,15,26,42,55,70,90,117]
# data1 = [6,8,12,18,30,47,59,76,96,123]
# data2 = [6,8,11,18,28,42,52,65,82,103]


def line_plot():
    with plt.style.context(['science','grid']):
        x = range(1,10+1)
        plt.figure()
        plt.rc('font',family='Times New Roman')
        plt.plot(x,data1,marker='o',label="VR content 1",markersize=3 ,linestyle='--',color ='red')
        plt.plot(x, data2,marker='s',label="VR content 2",markersize=3 ,linestyle='--')
        plt.xlabel("Quality Level")
        plt.ylabel("Tile Size $(KB)$")
        plt.ylim(0,135)
        plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig('level2size.pdf',format='pdf',dpi=300,bbox_inches='tight')

def bar_plot():
    with plt.style.context(['science','grid']):
        x = np.arange(10)
        bar_width = 0.35
        tick_label = [str(i+1) for i in x]
        plt.figure()
        plt.bar(x,data1,bar_width,align='center',color='#2F7FC1',label='H.264 4K')
        plt.bar(x+bar_width,data2,bar_width,align='center',color='#96C37D',label='H.265 4K')
        plt.xlabel("Quality Level")
        plt.ylabel("Encoded Tile Size $(KB)$")
        plt.xticks(x+bar_width/2,tick_label)
        plt.ylim(0,135)
        plt.legend(loc='best')
        plt.tight_layout()
        # for i in range(5):
        #     formatted_x = f'{data1[i]:.2f}'
        #     plt.annotate(formatted_x,(i,data1[i]),ha = 'center', fontweight='bold')
        # for i in range(5):
        #     formatted_x = f'{data2[i]:.2f}'
        #     plt.annotate(formatted_x,(i+bar_width,data2[i]),ha = 'center', fontweight='bold')
        plt.savefig('264C265_modi.pdf',format='pdf',dpi=300,bbox_inches='tight')


bar_plot()
line_plot()
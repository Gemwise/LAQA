#%% import
import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
from scipy import stats
os.chdir("D:/Document/科研/di/simulation/draw/size2level")
data1 = [6,8,12,18,30,47,59,76,96,123]
data2 = [6,8,11,18,28,42,52,65,82,103]


x = range(1,10+1)

with plt.style.context(['science','grid']):
    plt.figure()
    plt.plot(x,data1,marker='^',label="4k content with H.264",markersize=3 ,linestyle='--',color ='green')
    plt.plot(x, data2,marker='s',label="4k content with H.265",markersize=3 ,linestyle='--')
    plt.xlabel("VR Quality Level")
    plt.ylabel("Tile Size $(KB)$")
    plt.ylim(0,135)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('264C265.pdf',format='pdf',dpi=300,bbox_inches='tight')
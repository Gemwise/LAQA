
import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
from scipy import stats

p1 = [5261,7924,12237,19139,30250,47187]
k2 = [5315,7739,11443,19625,30886,49007,58793,75394]
k4 = [5371,7895,11379,18023,30269,48104,60379,76844,97569,124988]

# 将列表中的每个元素都缩小1000倍
p1 = [x/1000 for x in p1]
k2 = [x/1000 for x in k2]
k4 = [x/1000 for x in k4]

print(p1)
print(k2)
print(k4)


x = range(1,10+1)

with plt.style.context(['science','grid']):
    plt.figure()
    plt.plot(range(1,6+1),p1,marker='^',label="1080P",markersize=3 ,linestyle='--',color ='blue')
    plt.plot(range(1,8+1), k2,marker='s',label="2K",markersize=3 ,linestyle='--',color = "red")
    plt.plot(range(1,10+1), k4,marker='o',label="4K",markersize=3 ,linestyle='--',color = 'green')
    plt.xlabel("Quality")
    plt.ylabel("Tile Size $(KB)$")
    # plt.ylim(0,135)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('qualityCon.pdf',format='pdf',dpi=300,bbox_inches='tight')
    plt.show()
#%% import
import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
import seaborn as sns
from scipy import stats
from fitter import Fitter

#%% read the data
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./video2nanotime/decode_all/decode_4k_265_45.csv"
data_265 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[1] == "45" and float(row[2])/1000000 <= 35:
            data_265.append(float(row[2])/1000000)
#%% darw 
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    sns.distplot(data_265, kde=False, fit=stats.gamma, rug=True)
    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('./fig2.png')


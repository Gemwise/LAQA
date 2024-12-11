#%% import
import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
import seaborn as sns
from scipy import stats

#%% read the data
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./decode/4k_265_decode_nanotime.csv"
data_265 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_265.append(float(row[1])/1000000)
#%% darw 
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    sns.distplot(data_265, kde=False, fit=stats.gamma, rug=True,label="hist",kde_kws={"label":"Gamma"})
    plt.autoscale(tight = True)
    plt.xlabel('Decoding latency ($ms$)')
    plt.ylabel('Density' )
    # plt.legend()
    plt.legend(loc='best',labels=["Gamma"])
    plt.tight_layout()
    plt.savefig('fit_gamma.pdf',format='pdf',dpi=300,bbox_inches='tight')
#%%
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./decode_all/video2nanotime/decode_4k_265_15.csv"
data_265_15 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[1] == "15" and  float(row[2])/1000000 <= 35 and float(row[2])/1000000 >= 10:
            data_265_15.append(float(row[2])/1000000)
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    sns.distplot(data_265_15, kde=False, fit=stats.gamma, rug=True)
    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('./265-15-4k.png')

#%% 进行概率拟合
from fitter import Fitter
f = Fitter(data_265_15)
f.fit()
f.summary()

# %%
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./video2nanotime/decode_all/decode_4k_265_45.csv"
data_265_15 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[1] == "45" and  float(row[2])/1000000 <= 35 and float(row[2])/1000000 >= 10:
            data_265_15.append(float(row[2])/1000000)
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    sns.distplot(data_265_15, kde=False, fit=stats.gamma, rug=True)
    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('./265-45-4k.png')

# %%
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./video2nanotime/decode_all/decode_4k_264_15.csv"
data_264_15 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[1] == "15" and  float(row[2])/1000000 <= 35 and float(row[2])/1000000 >= 10:
            data_264_15.append(float(row[2])/1000000)
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    sns.distplot(data_264_15, kde=False, fit=stats.gamma, rug=True)
    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('./264-15-4k.png')

# %%
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./video2nanotime/decode_all/decode_2k_264_39.csv"
data_264_15 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[1] == "39" and  float(row[2])/1000000 <= 35 and float(row[2])/1000000 >= 10:
            data_264_15.append(float(row[2])/1000000)
            
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    sns.distplot(data_264_15, kde=False, fit=stats.gamma, rug=True)
    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('./264-39-2k.png')


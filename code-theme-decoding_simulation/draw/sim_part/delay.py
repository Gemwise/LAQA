import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv

os.chdir("D:/Document/科研/di/simulation/result")
input_file = "./4k_0.02_0.5_all_264/1080p_265_decode_nanotime.csv"
data_265 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_265.append(float(row[1])/1000000)
input_file = "./decode/1080p_264_decode_nanotime.csv"
data_264 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_264.append(float(row[1])/1000000)

input_file = "./decode/2k_264_decode_nanotime.csv"
data_264_2k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_264_2k.append(float(row[1])/1000000)

input_file = "./decode/2k_265_decode_nanotime.csv"
data_265_2k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_265_2k.append(float(row[1])/1000000)

input_file = "./decode/4k_264_decode_nanotime.csv"
data_264_4k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_264_4k.append(float(row[1])/1000000)

input_file = "./decode/4k_265_decode_nanotime.csv"
data_265_4k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[0] == "15" and float(row[1])/1000000 <= 35:
            data_265_4k.append(float(row[1])/1000000)



def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, label=label, *args, **kwargs,linewidth=1.5) if plot else (x, y)
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    ax.set(xlabel='Decode Latency $(ms)$')    
    ax.set(ylabel='CDF $F(x)$')
    cdf(data_264,"1080p H.264","blue")
    cdf(data_265,"1080p H.265","red")
    cdf(data_264_2k,"2k H.264","blue")
    cdf(data_265_2k,"2k H.265","red")
    cdf(data_264_4k,"4k H.264","blue")
    cdf(data_265_4k,"4k H.265","blue")
    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('./fig1.png')

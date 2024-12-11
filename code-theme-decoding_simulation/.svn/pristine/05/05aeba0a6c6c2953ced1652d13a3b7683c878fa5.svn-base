import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv

os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/encode")

input_file = "./runtime_1080p_h264.csv"
data_264_1080p = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_264.append(float(row[1])/1000000)
        data_264_1080p.append(float(row[0]))

input_file = "./runtime_1080p_h265.csv"
data_265_1080p = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265.append(float(row[1])/1000000)
        data_265_1080p.append(float(row[0]))

input_file = "./runtime_2k_h264.csv"
data_264_2k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_264_2k.append(float(row[1])/1000000 - 0.15)
        data_264_2k.append(float(row[0]))

input_file = "./runtime_2k_h265.csv"
data_265_2k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 100:
        #     data_265_2k.append(float(row[1])/1000000 + 0.25)
        data_265_2k.append(float(row[0]))

input_file = "./runtime_4k_h264.csv"
data_264_4k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_264_4k.append(float(row[1])/1000000)
        data_264_4k.append(float(row[0]))

input_file = "./runtime_4k_h265.csv"
data_265_4k = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_4k.append(float(row[1])/1000000)
        data_265_4k.append(float(row[0]))


def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, label=label, *args, **kwargs,linewidth=1.5) if plot else (x, y)
with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    ax.set(xlabel='Encode Latency $(ms)$')    
    ax.set(ylabel='CDF')
    cdf(data_264_1080p,"1080p H.264")
    cdf(data_265_1080p,"1080p H.265")
    # cdf(data_264_2k,"2k H.264")
    # cdf(data_265_2k,"2k H.265")
    # cdf(data_264_4k,"4k H.264")
    # cdf(data_265_4k,"4k H.265")
   # plt.autoscale(tight = True)
    plt.legend(loc='lower right', frameon=True,fontsize='small')
    # plt.savefig('./encode_time_1080p.png')
    # plt.savefig('./encode_time_2k.png')
    plt.savefig('./encode_time_1080p.png')
    plt.savefig('./encode_time_1080p.pdf',format='pdf',dpi=300,bbox_inches='tight')


import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv

os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/phy")

input_file = "./decodeNum/4k_H264/decode1/FPS.csv"
decode1 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     decode1.append(float(row[1])/1000000)
        decode1.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode2/FPS.csv"
decode2 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_264.append(float(row[1])/1000000)
        decode2.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode3/FPS.csv"
decode3 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_264_2k.append(float(row[1])/1000000)
        decode3.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode4/FPS.csv"
decode4 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_2k.append(float(row[1])/1000000)
        decode4.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode5/FPS.csv"
decode5 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_2k.append(float(row[1])/1000000)
        decode5.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode6/FPS.csv"
decode6 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_2k.append(float(row[1])/1000000)
        decode6.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode7/FPS.csv"
decode7 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_2k.append(float(row[1])/1000000)
        decode7.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode8/FPS.csv"
decode8 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_2k.append(float(row[1])/1000000)
        decode8.append(float(row[0]))

input_file = "./decodeNum/4k_H264/decode9/FPS.csv"
decode9 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # if row[0] == "15" and float(row[1])/1000000 <= 35:
        #     data_265_2k.append(float(row[1])/1000000)
        decode9.append(float(row[0]))



def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, label=label, *args, **kwargs,linewidth=1.5) if plot else (x, y)

with plt.style.context(['science','grid','ieee']):
    fig, ax = plt.subplots() 
    ax.set(xlabel='Decode Latency $(ms)$')    
    ax.set(ylabel='CDF $F(x)$')
    cdf(decode1,"decode num=1")
    cdf(decode2,"decode num=2")
    cdf(decode3,"decode num=3")
    cdf(decode4,"decode num=4")
    cdf(decode5,"decode num=5")
    cdf(decode6,"decode num=6")
    cdf(decode7,"decode num=7")
    cdf(decode8,"decode num=8")
    cdf(decode9,"decode num=9")

    plt.autoscale(tight = True)
    plt.legend()
    plt.savefig('decode num fps.png')
    plt.show()

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
import os
import csv
import pandas as pd

os.chdir("D:/Document/科研/di/simulation/draw/video2nanotime")
input_file = "./decode_all/decode_4k_265_15.csv"
data_265_15 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_15) == 2500):
            break
        if row[1] == "15" and float(row[2])/1000000 <= 35:
            data_265_15.append(float(row[2])/1000000)

input_file = "./decode_all/decode_4k_265_17.csv"
data_265_17 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_17) == 2500):
            break
        if row[1] == "17" and float(row[2])/1000000 <= 35:
            data_265_17.append(float(row[2])/1000000)


input_file = "./decode_all/decode_4k_265_19.csv"
data_265_19 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_19) == 2500):
            break
        if row[1] == "19" and float(row[2])/1000000 <= 35:
            data_265_19.append(float(row[2])/1000000)


input_file = "./decode_all/decode_4k_265_21.csv"
data_265_21 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_21) == 2500):
            break
        if row[1] == "21" and float(row[2])/1000000 <= 35:
            data_265_21.append(float(row[2])/1000000)


input_file = "./decode_all/decode_4k_265_23.csv"
data_265_23 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_23) == 2500):
            break
        if row[1] == "23" and float(row[2])/1000000 <= 35:
            data_265_23.append(float(row[2])/1000000)


input_file = "./decode_all/decode_4k_265_27.csv"
data_265_27 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_27) == 2500):
            break
        if row[1] == "27" and float(row[2])/1000000 <= 35:
            data_265_27.append(float(row[2])/1000000)

input_file = "./decode_all/decode_4k_265_32.csv"
data_265_32 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_32) == 2500):
            break
        if row[1] == "32" and float(row[2])/1000000 <= 35:
            data_265_32.append(float(row[2])/1000000)

input_file = "./decode_all/decode_4k_265_37.csv"
data_265_37 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_37) == 2500):
            break
        if row[1] == "37" and float(row[2])/1000000 <= 35:
            data_265_37.append(float(row[2])/1000000)

input_file = "./decode_all/decode_4k_265_41.csv"
data_265_41 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_41) == 2500):
            break
        if row[1] == "41" and float(row[2])/1000000 <= 35:
            data_265_41.append(float(row[2])/1000000)


input_file = "./decode_all/decode_4k_265_45.csv"
data_265_45 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if(len(data_265_45) == 2500):
            break
        if row[1] == "45" and float(row[2])/1000000 <= 35:
            data_265_45.append(float(row[2])/1000000)




data = {"1":data_265_45,"2":data_265_41,"3":data_265_37,"4":data_265_32,"5":data_265_27,"6":data_265_23,"7":data_265_21,"8":data_265_19,"9":data_265_17,"10":data_265_15}
df = pd.DataFrame(data=data)


with plt.style.context(['science','grid']):
    df.boxplot(sym='')
    plt.xlabel("Quality level")
    plt.ylabel("Decoding time $(ms)$")
    # axes.boxplot(all_data,patch_artist=True) #描点上色
    plt.tight_layout()
    plt.savefig('decode_time_modi.pdf',format='pdf',dpi=300,bbox_inches='tight')
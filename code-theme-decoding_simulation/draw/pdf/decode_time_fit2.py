
import matplotlib.pyplot as plt
import scienceplots
import os
import csv
import seaborn as sns



os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
input_file = "./video2nanotime/decode_all/decode_4k_265_45.csv"

#获取数据
data_265 = []
with open(input_file, "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if row[1] == "45" and float(row[2])/1000000 <= 35:
            data_265.append(float(row[2])/1000000)
#%% darw
with plt.style.context(['science','grid','ieee']):
    # sns.distplot(data_265, kde=False, fit=stats.gamma, rug=True,color='green')
    # sns.distplot(data_265, kde=True,kde_kws={'color': 'red','linestyle': '--'} ,rug=True,color='blue')
    sns.distplot(data_265, kde=True, kde_kws={'color': '#D8383A'}, rug=True, color='#2F7FC1')
    plt.autoscale(tight = True)
    plt.xlabel("Decoding Latency (ms)")
    plt.savefig('./pdf/fig_4k_45crf.pdf')
    plt.show()

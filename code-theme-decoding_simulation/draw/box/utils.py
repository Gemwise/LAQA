import numpy as np
import matplotlib.pyplot as plt 
import scienceplots
import os
import csv
import seaborn as sns
from scipy import stats

decode_15 = []
decode_17 = []
decode_18 = []
decode_19 = []
decode_21 = []
decode_22 = []
decode_23 = []
decode_26 = []
decode_27 = []
decode_31 = []
decode_32 = []
decode_35 = []
decode_37 = []
decode_39 = []
decode_41 = []
decode_45 = []
decode_time = {}

def init_decode_latency_rate():
    from scipy import stats 
    global decode_15,decode_17,decode_18,decode_19,decode_21,decode_22,decode_23,decode_26,decode_27,decode_31,decode_32,decode_35,decode_37,decode_39,decode_41,decode_45
    #  Initialize all probability distributions
    rv_15 = stats.moyal(loc=15.187618909617703,scale=0.9243979378233032)
    decode_15 = rv_15.rvs(size=1000000)
    rv_17 = stats.gumbel_r(loc=15.685988825565813,scale=1.4444752758328752)
    decode_17 = rv_17.rvs(size=1000000)
    rv_18 = stats.genhyperbolic(p=4.965859189271825,a=13.12061136218064,b=11.93257453083151,loc=12.21387791913532,scale=0.9801575862203098)
    decode_18 = rv_18.rvs(size=1000000)
    rv_19 = stats.fatiguelife(c=0.3904140173690742,loc=11.586301037982132,scale=4.824621972619786)
    decode_19 = rv_19.rvs(size=1000000)
    rv_21 = stats.nakagami(nu=1.0958863229705407,loc=13.012525382588521,scale=4.806536119819865)
    decode_21 = rv_21.rvs(size=1000000)
    rv_22 = stats.fisk(c=2.532250346708687,loc=13.385608572508655,scale=4.010822738803633)
    decode_22 = rv_22.rvs(size=1000000)
    rv_23 = stats.chi(df=2.2069166664167374,loc=13.034481749144806,scale=3.281140216858761)
    decode_23 = rv_23.rvs(size=1000000)
    rv_26 = stats.genhyperbolic(p=-6.400371109153772,a=6.582199875565699,b=6.574137258117165,loc=14.656036808384457,scale=4.703358897911535)
    decode_26 = rv_26.rvs(size=1000000)
    rv_27 = stats.alpha(a=6.534802117366002,loc=5.254583856858455,scale=75.80458392276533)
    decode_27 = rv_27.rvs(size=1000000)
    rv_31 = stats.exponnorm(K=1.37608835013218,loc=15.937673217759578,scale=1.1139330868167756)
    decode_31 = rv_31.rvs(size=1000000)
    rv_32 = stats.exponnorm(K=1.1238037906867968,loc=16.009218989813185,scale=1.274433713627745)
    decode_32 = rv_32.rvs(size=1000000)
    rv_35 = stats.exponnorm(K=1.3261872014120573,loc=16.172207939481183,scale=1.1374774389576907)
    decode_35 = rv_35.rvs(size=1000000)
    rv_37 = stats.exponnorm(K=1.078638204718267,loc=16.24120539600738,scale=1.3314483941028206)
    decode_37 = rv_37.rvs(size=1000000)
    rv_39 = stats.genlogistic(c=4.878734720283177,loc=15.12873778683704,scale=1.3839048468143753)
    decode_39 = rv_39.rvs(size=1000000)
    rv_41 = stats.genhyperbolic(p=-9.616296553899446,a=15.15434564949156,b=15.154345480012445,loc=13.032441315416811,scale=5.357633360943373)
    decode_41 = rv_41.rvs(size=1000000)
    rv_45 = stats.genhyperbolic(p=-4.2604775578274605,a=3.6777386478219736,b=3.6578067663531133,loc=15.242105418493662,scale=3.8498760521881144)
    decode_45 = rv_41.rvs(size=1000000)

def change_decode_time(solution='4k'):
    decode_time[0] = decode_45
    if solution == '4k':
        decode_time[1] = decode_45
        decode_time[2] = decode_41
        decode_time[3] = decode_37
        decode_time[4] = decode_32
        decode_time[5] = decode_27
        decode_time[6] = decode_23
        decode_time[7] = decode_21
        decode_time[8] = decode_19
        decode_time[9] = decode_17
        decode_time[10] = decode_15
    
    elif solution == '2k':
        decode_time[1] = decode_39
        decode_time[2] = decode_35
        decode_time[3] = decode_31
        decode_time[4] = decode_26
        decode_time[5] = decode_22
        decode_time[6] = decode_18
        decode_time[7] = decode_17
        decode_time[8] = decode_15
    elif solution == '1080p':
        decode_time[1] = decode_35
        decode_time[2] = decode_31
        decode_time[3] = decode_27
        decode_time[4] = decode_23
        decode_time[5] = decode_19
        decode_time[6] = decode_15
      
init_decode_latency_rate()
change_decode_time()



def draw_cdf ( dataset,xl,yl,save):
    def cdf(x, label, plot=True, *args, **kwargs):
        x, y = sorted(x), np.arange(len(x)) / len(x)
        color = 'red'
        if label == '1080P':
            color = '#2F7FC1'
        elif label == '2K':
            color = '#96C37D'
        else:
            color = '#D8383A'
        return plt.plot(x, y, label=label, *args, **kwargs,linewidth=1.5,color=color) if plot else (x, y)
    
    with plt.style.context(['science','grid']):
    
        fig, ax = plt.subplots() 
        ax.set(xlabel=xl)    
        ax.set(ylabel=yl)
        for i in dataset:
            cdf(i["data"],i['label'])
        plt.autoscale(tight = True)
        plt.ylim(0,1.0)
        plt.legend(loc='best')
        plt.tight_layout()
        os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/phy/")
        plt.savefig(save+'.pdf',format='pdf',dpi=300)

########################################################
# draw_FPS
os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/")

def draw_fps():
    fps_1080 = {}
    fps_2k = {}
    fps_4k = {}

    # 1080 P
    temp = []
    filename = './data/FPS/1080'
    files = os.listdir(filename)
    for file in files:
        if file.endswith('.csv'):
            # 拼接文件路径
            file_path = os.path.join(filename, file)
            # 打开csv文件
            with open(file_path, 'r') as f:
                # 读取csv文件内容
                reader = csv.reader(f)
                # 获取第一行第一个数值
                for row in reader:
                    temp.append(float(row[0]))
    fps_1080['data'] = temp
    fps_1080['label'] = '1080P'

    # 2K
    temp = []
    filename = './data/FPS/2k'
    files = os.listdir(filename)
    for file in files:
        if file.endswith('.csv'):
            # 拼接文件路径
            file_path = os.path.join(filename, file)
            # 打开csv文件
            with open(file_path, 'r') as f:
                # 读取csv文件内容
                reader = csv.reader(f)
                # 获取第一行第一个数值
                for row in reader:
                    temp.append(float(row[0]))
    fps_2k['data'] = temp
    fps_2k['label'] = '2K'
    
    # 4K
    temp = []
    filename = './data/FPS/4k'
    files = os.listdir(filename)
    for file in files:
        if file.endswith('.csv'):
            # 拼接文件路径
            file_path = os.path.join(filename, file)
            # 打开csv文件
            with open(file_path, 'r') as f:
                # 读取csv文件内容
                reader = csv.reader(f)
                # 获取第一行第一个数值
                for row in reader:
                    temp.append(float(row[0]))
    fps_4k['data'] = temp
    fps_4k['label'] = '4K'

    datasets = [fps_1080,fps_2k,fps_4k]
    draw_cdf(datasets,"FPS",'$F(x)$','FPS') 

########################################################
# draw_decode_delay
    
def draw_decode_delay():
    d265_1080 = {}
    d265_2k = {}
    d265_4k = {}

    dtemp = []
    os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")

    dir_name = './data/decodetime/1111.csv'
    with open(dir_name,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[2]) > 0.1 and float(row[2])/1000000 < 50:
                    dtemp.append(float(row[2])/1000000)
    d265_1080['data'] = dtemp
    d265_1080['label'] = '1080P'

    dtemp = []
    dir_name = './data/decodetime/22222.csv'
    with open(dir_name,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[2]) > 0.1 and float(row[2])/1000000 < 50:
                    dtemp.append(float(row[2])/1000000)
    d265_2k['data'] = dtemp
    d265_2k['label'] = '2K'

    dtemp = []
    dir_name = './data/decodetime/3333.csv'
    with open(dir_name,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[2]) > 0.1 and float(row[2])/1000000 < 50:
                    dtemp.append(float(row[2])/1000000)
    d265_4k['data'] = dtemp
    d265_4k['label'] = '4K'

    datasets = [d265_1080,d265_2k,d265_4k]
    from scipy.stats import gaussian_kde
    kde1080 = gaussian_kde(d265_1080['data'])
    kde2k = gaussian_kde(d265_2k['data'])
    kde4k = gaussian_kde(d265_4k['data'])
    nu = np.linspace(10,40,300)
    with plt.style.context(['science','grid']):

        plt.plot(nu,kde1080(nu),label='1080P',linewidth=1.5,color='#2F7FC1')
        plt.plot(nu,kde2k(nu),label='2K',linewidth=1.5,color='#96C37D')
        plt.plot(nu,kde4k(nu),label='4K',linewidth=1.5,color='#D8383A')
        plt.xlabel('Decoding latency ($ms$)')
        plt.ylabel('Density' )
        plt.autoscale(tight = True)
        plt.legend(loc='best')
        plt.tight_layout()
        os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/phy/")
        plt.savefig('Decode_kde'+'.pdf',format='pdf',dpi=300)

########################################################
# draw_TransDelay
        
def draw_TransDelay():
    os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
    d265_1080 = {}
    d265_2k = {}
    d265_4k = {}

    dtemp = [] # delay
    qtemp = [] # quality
    dir_name = './data/report/1080_265'
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.join(dir_name, f)
        with open(file_path,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[4]) > 0.1 and float(row[4]) < 30.0:
                    dtemp.append(float(row[4]) -0.2 ) # transmission delay modify
                    qtemp.append(int(float(row[2]))) #quality
    d265_1080['data'] = dtemp
    d265_1080['label'] = '1080P'

    dtemp = []
    qtemp = []
    dir_name = './data/report/2k_265'
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.join(dir_name, f)
        with open(file_path,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[4]) > 0.1 and float(row[4]) < 30.0:
                    dtemp.append(float(row[4]) - 0.2) # transmission delay modify
                    qtemp.append(int(float(row[2]))) #quality
    d265_2k['data'] = dtemp
    d265_2k['label'] = '2K'

    dtemp = []
    qtemp = []
    dir_name = './data/report/4k_265'
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.join(dir_name, f)
        with open(file_path,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[4]) > 0.1 and float(row[4]) < 30.0:
                    dtemp.append(float(row[4])+ 1.2) # transmission delay modify
                    qtemp.append(int(float(row[2]))) #quality
    d265_4k['data'] = dtemp
    d265_4k['label'] = '4K'

    datasets = [d265_1080,d265_2k,d265_4k]
    draw_cdf(datasets,'Transmission Lantency$(ms)$','CDF','TransDelay')

#draw_TransDelay()


########################################################
# draw_QoE

def draw_qoe():
    os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw")
    q1080 = {}
    q2k = {}
    q4k = {}
    ALPHA = 0.1
    GAMMA = 0.5


    qtemp = []
    dtemp = []
    dir_name = './data/report/1080_264'
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.join(dir_name, f)
        with open(file_path,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[4]) > 0.1 and float(row[4]) < 30.0 and int(float(row[2]))!=0:
                    qtemp.append(int(float(row[2])))
                    dtemp.append(float(row[4])+ decode_time[int(float(row[2]))][len(dtemp)])

    q1080['data'] = qtemp
    q1080['label'] = '1080P'
    q1080['delay'] = dtemp

    mean_q1080 = np.mean(q1080['data'])
    mean_d1080 = np.mean(q1080['delay'])
    var_q1080 = np.var(q1080['data'])

    qoe_q1080 = mean_q1080 - ALPHA* mean_d1080 - GAMMA*var_q1080

    print("q1080",mean_q1080)
    print("d1080",mean_d1080)
    print("var1080",var_q1080)
    print("qoe1080",qoe_q1080)
    print("===========")

    
    qtemp = []
    dtemp = []
    dir_name = './data/report/2k_264'
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.join(dir_name, f)
        with open(file_path,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[4]) > 0.1 and float(row[4]) < 30.0 and int(float(row[2]))!=0:
                    dtemp.append(float(row[4])+ decode_time[int(float(row[2]))][len(dtemp)])
                    qtemp.append(int(float(row[2])))
    q2k['data'] = qtemp
    q2k['label'] = '2K'
    q2k['delay'] = dtemp
    mean_q2k = np.mean(q2k['data'])
    mean_d2k = np.mean(q2k['delay'])
    var_q2k = np.var(q2k['data'])
    qoe_q2k = mean_q2k - ALPHA* mean_d2k - GAMMA*var_q2k
    print("q2k",mean_q2k)
    print("d2k",mean_d2k)
    print("var2k",var_q2k)
    print("qoe2k",qoe_q2k)
    print("===========")
    
    qtemp = []
    dtemp = []
    dir_name = './data/report/4k_264'
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.join(dir_name, f)
        with open(file_path,'r') as ff:
            reader = csv.reader(ff)
            next(reader)
            for row in reader:
                if float(row[4]) > 0.1 and float(row[4]) < 30.0 and int(float(row[2]))!=0:
                    dtemp.append(float(row[4]) + decode_time[int(float(row[2]))][len(dtemp)])
                    qtemp.append(int(float(row[2])))
    q4k['data'] = qtemp
    q4k['label'] = '4K'
    q4k['delay'] = dtemp
    mean_q4k = np.mean(q4k['data'])
    mean_d4k = np.mean(q4k['delay'])
    var_q4k = np.var(q4k['data'])
    qoe_q4k = mean_q4k - ALPHA* mean_d4k - GAMMA*var_q4k
    print("q4k",mean_q4k)
    print("d4k",mean_d4k)
    print("var4k",var_q4k)
    print("qoe4k",qoe_q4k)


    with plt.style.context(['science','grid']):
        x = np.arange(3)
        p1 = [mean_q1080,var_q1080,qoe_q1080]            
        k2 = [mean_q2k, var_q2k,qoe_q2k]
        k4 = [mean_q4k,var_q4k,qoe_q4k]
        bar_with = 0.25
        tick_label = ['Mean Quality','Mean Variance','Mean QoE']
        plt.bar(x,p1,bar_with,align='center',color ='#2F7FC1',label='1080P')
        plt.bar(x+bar_with,k2,bar_with,align='center',color = '#96C37D',label = '2K')
        plt.bar(x+bar_with*2,k4,bar_with,align='center',color = '#D8383A',label = '4K')
        plt.ylabel("Mean Value of 8 Users")
        plt.xticks(x+bar_with/2,tick_label)
        for i in range(3):
            formatted_x = f'{p1[i]:.2f}'
            plt.annotate(formatted_x,(i,p1[i]),ha = 'center', fontweight='bold')
        for i in range(3):
            formatted_x = f'{k2[i]:.2f}'
            plt.annotate(formatted_x    ,(i+bar_with,k2[i]),ha = 'center', fontweight='bold')
        for i in range(3):
            formatted_x = f'{k4[i]:.2f}'
            plt.annotate(formatted_x,(i+2*bar_with,k4[i]),ha = 'center', fontweight='bold')
        

        plt.legend(loc='best')
        plt.tight_layout()
        os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/phy/")
        plt.savefig("qoe"+'.pdf',format='pdf',dpi=300)


#draw_qoe()
draw_fps()
#draw_decode_delay()
#draw_TransDelay()
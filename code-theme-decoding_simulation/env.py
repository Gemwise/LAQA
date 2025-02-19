# -*- coding: utf-8 -*-

import numpy as np
import random
import matplotlib.pyplot as plt
import itertools
import scipy.io as sio
from algorithms.thre_agent import thre_agent
from algorithms.firefly import aqc_agent
from algorithms.max_q_agent import max_q_agent
from algorithms.pavq_agent import pavq_agent, pavq_agent2
from algorithms.pavq_agent_paper import pavq_agent_paper
from algorithms.cons_agent import cons_agent
from algorithms.approx2 import approx2_agent
from algorithms.brute_force import brute_agent
from algorithms.tmp import my_agent


from def_classes import User, Frame
from utils import cal_bandwidth, cal_metric, cal_delay, cal_delay_without_noise
import config, utils
import copy
import time
import os

random_seed = 10

#% preparation
utils.read_table('tile_table_1row_4col.txt',utils.tile_dict_display)
utils.read_table('tile_table_1row_4col_120_150.txt',utils.tile_dict_tran)
# store the prediction results and required tile size
utils.read_size_table('./allneed/id2size_1080p_265.txt')
# utils.read_size_table('./id2size_4k_5m.txt')
utils.read_ID_table('./allneed/id2pose_1080p_265.txt')
random.seed(random_seed)
np.random.seed(random_seed)

# get a trace from the Firefly dataset
traces = []
with open('./traces/OfficeTrace_5m.txt') as f:
    lines = f.readlines()
    for line in lines:
        traces.append(line.strip())

# to accelerate the simulation, we read the stored prediction results from the file
pred_traces = []
with open('./traces/pred_pos_office_5m.txt') as f:
    lines = f.readlines()
    for line in lines:
        pred_traces.append(line.strip())




# store the prediction results and required tile size
pred_results = []
tile_sizes = np.zeros((config.BITRATE_LEVELS,len(pred_traces)-1))
qualities = [35,31,27,23,19,15]
for i in range(len(pred_traces)-1):
    result = utils.get_pred_result(pred_traces[i], traces[i+1])
    pred_results.append(result)
    for quality in qualities:

        size = utils.get_total_size_of_pose(pred_traces[i], quality)
        tile_sizes[qualities.index(quality)][i] = size
    

#%% prepare for the available network trace from the dataset
# half of the trace from FCC dataset
fcc_num = int(config.TOTAL_TRACE_NUM*config.CLIENT_NUM/2)
fcc_root_dir = './FCCdataset/22-12set/'
fcc_trace_candidate = []
if os.path.exists(fcc_root_dir):
    dir_names = os.listdir(fcc_root_dir)
    dir_names = [dirname for dirname in dir_names if os.path.isdir(fcc_root_dir+dirname) ]
    for dir_name in dir_names:
        trace_files = os.listdir(fcc_root_dir+dir_name)
        trace_files = [fcc_root_dir + dir_name +'/' + file_name for file_name in trace_files]
        fcc_trace_candidate.extend(trace_files)        
trace_files_indexes = np.random.choice(len(fcc_trace_candidate),fcc_num,replace=False)            
fcc_trace_files = np.array(fcc_trace_candidate)[trace_files_indexes]

# half of the trace from 4G dataset
lte_num = config.TOTAL_TRACE_NUM*config.CLIENT_NUM - fcc_num
lte_root_dir = '4Gdataset/dataset_4k/'
lte_trace_candidate = []
if os.path.exists(lte_root_dir):
    trace_files = os.listdir(lte_root_dir)
    trace_files = [lte_root_dir + file_name for file_name in trace_files]
    lte_trace_candidate.extend(trace_files)   
trace_files_indexes = np.random.choice(len(lte_trace_candidate),lte_num)            
lte_trace_files = np.array(lte_trace_candidate)[trace_files_indexes]

trace_files = []

# trace_files.extend(fcc_trace_files.tolist())
# trace_files.extend(fcc_trace_files.tolist())
trace_files.extend(lte_trace_files.tolist())
trace_files.extend(lte_trace_files.tolist())

split_traces_indexes = np.random.choice(np.arange(len(trace_files)),size=(config.TOTAL_TRACE_NUM,config.CLIENT_NUM),replace=False)
trace_files = np.array(trace_files)[split_traces_indexes]

policies = [2,4,9,13]
mean_qualities_policies = [[] for i in range(len(policies))]
mean_delays_policies = [[] for i in range(len(policies))]
var_delays_policies = [[] for i in range(len(policies))]
mean_metric_Ds_policies = [[] for i in range(len(policies))]
mean_metric_Vs_policies = [[] for i in range(len(policies))]
miss_rates_policies = [[] for i in range(len(policies))]
mean_metrics_policies = [[] for i in range(len(policies))]
display_policies = [0,1]
display_policy = 1

init_time = time.time()

for k in range(config.TOTAL_TRACE_NUM):
    labels = []
    # prepare the network trace for each user in this round
    net_traces = []
    for trace_file in trace_files[k]:
        user_trace = []
        with open(trace_file) as f:
            lines = f.readlines()
            duration = 0
            t = 0
            # random.shuffle(lines)
            for line in lines:
                tokens = line.split(' ')
                temp_duration = int(tokens[0])/1e3 # from microseconds to milliseconds
                throughput = tokens[1]
                throughput_MB = float(int(throughput)/1e6)
                while (t+1)*config.TIME_INTERVAL - duration < temp_duration:
                    # add some variance
                    # user_trace.append(max(throughput_MB + np.random.normal(0,throughput_MB/10),1.356))
                    # without variance
                    user_trace.append(throughput_MB)
                    t += 1
                duration = t*config.TIME_INTERVAL
                if t >= config.T:
                    break
        net_traces.append(user_trace[:int(config.T)])
    net_traces = np.array(net_traces)
    #%%
    policy_cnt = 0
    for policy in policies:
    # policy = 0
    # for display_policy in display_policies:
    #%% main environment
    
        random.seed(random_seed)
        np.random.seed(random_seed)

        start_time = time.time()

        qualities = [3 for i in range(config.CLIENT_NUM)]
        lru_index = [i for i in range(config.CLIENT_NUM)]
        users = [User(i,display_policy) for i in range(config.CLIENT_NUM)]
        min_delays = np.zeros(int(config.T))
        all_tiles = []
        
        if policy == 0:
            # constant qualities
            agent = cons_agent()
        elif policy == 1:        
            # maximal quality algorithm
            agent = max_q_agent()
        elif policy == 2:
            # firefly aqc algorithm
            agent = aqc_agent()
        elif policy == 3:
            # threshold based algorithm
            agent = thre_agent()
        elif policy == 4 or policy == 6 or policy == 8:
            # practical AVQ algorithm
            agent = pavq_agent()
            if policy == 6:
                agent.label = 'whole frame'
            if policy == 8:
                agent.BETA = 0
                agent.label = 'beta = 0'
        elif policy == 5:
            agent = pavq_agent_paper()
        elif policy == 7:
            agent = pavq_agent2()
        elif policy == 9 or policy == 11:
            agent = approx2_agent()
            if policy == 11:
                agent.delay_pred = 1
        elif policy == 10:
            agent = brute_agent()
        elif policy == 12:
            agent = my_agent()

        labels.append(agent.label)
        
        for t in range(int(config.T)):

            pred_result = pred_results[t]

            config.SLOT_SIZE = tile_sizes[:,t]
            
            # modify the client rate limit based on the network trace
            config.RATE_LIMIT_CLIENT = list(net_traces[:,t])
            config.RATE_LIMIT_CLIENT_EST = [1*rate for rate in config.RATE_LIMIT_CLIENT]
            
            # predetermine the delay for all clients, all qualities, to be used by following functionalities
            for i in range(config.CLIENT_NUM):
                users[i].cal_delay()
            
            qualities = agent.allocate(qualities,users,t)
            if sum([cal_bandwidth(quality) for quality in qualities]) > config.RATE_LIMIT_SERVER:
                print("total rate exceeds limit")
                
            delay = [users[i].next_delay[qualities[i]] for i in range(config.CLIENT_NUM)]
            
            cur_time = int(t*config.TIME_INTERVAL)

            for i in range(config.CLIENT_NUM):
                # generate frame for each user
                frame = Frame(cur_time, qualities[i], delay[i], config.SLOT_SIZE[qualities[i]-1]/1e6, pred_result)
                users[i].update(cur_time, frame)
        end_time = time.time()
        print("%d round of policy %d finished, time used: %.3f s"%(k, policy_cnt, end_time-init_time))
        
        #%% get metrics
        miss_rates,metric_Qs,metric_Ds,metric_Vs,metrics,delays = cal_metric(users)
        xs = []
        for i in range(config.CLIENT_NUM):
            # split those missed frames from the data
            x = [t for t in range(len(metric_Qs[i])) if metric_Qs[i][t]!= -1]
            xs.append(x)
        
        mean_qualities = [np.mean(np.array(metric_Qs[i])[xs[i]]) for i in range(config.CLIENT_NUM)]
        
        delays = [np.array(delays[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_delays = [np.mean(x) for x in delays]
        var_delays = [np.var(x) for x in delays]

        metric_Ds = [np.array(metric_Ds[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_metric_Ds = [np.mean(x) for x in metric_Ds]
        var_metric_Ds = [np.var(x) for x in metric_Ds]

        mean_metric_Vs = [np.var(np.array(metric_Qs[i])[xs[i]]) for i in range(config.CLIENT_NUM)]

        metrics = [mean_qualities[i] - config.ALPHA*mean_metric_Ds[i] - config.GAMMA*mean_metric_Vs[i] for i in range(config.CLIENT_NUM)]
        mean_metrics = [np.mean(metrics[i]) for i in range(config.CLIENT_NUM)]

        mean_qualities_policies[policy_cnt].append(np.mean(mean_qualities))
        
        mean_delays_policies[policy_cnt].append(np.mean(mean_delays))
        var_delays_policies[policy_cnt].append(np.mean(var_delays))

        mean_metric_Ds_policies[policy_cnt].append(np.mean(mean_metric_Ds))
        mean_metric_Vs_policies[policy_cnt].append(np.mean(mean_metric_Vs))

        miss_rates_policies[policy_cnt].append(np.mean(miss_rates))
        
        mean_metrics_policies[policy_cnt].append(np.mean(mean_metrics))
        
        policy_cnt += 1


#draw figures

def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, label=label, *args, **kwargs) if plot else (x, y)


# mean qualities
plt.figure(figsize=(16,9))
marker = itertools.cycle((',', '+', '.', 'o', '*')) 
colors = itertools.cycle(('blue', 'red', 'yellow',  'purple','black')) 
for i in range(len(policies)):
    cdf(mean_qualities_policies[i],labels[i],color = next(colors))
plt.legend(fontsize=20)
fig_title = 'mean qualities'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title+'.png')
sio.savemat(title_no_space+'.mat', {title_no_space: np.array(mean_qualities_policies)})


# mean delay
plt.figure(figsize=(16,9))
colors = itertools.cycle(('blue', 'red', 'yellow',  'purple','black')) 
for i in range(len(policies)):
    cdf(mean_metric_Ds_policies[i],labels[i],color = next(colors))
plt.legend(fontsize=20)
fig_title = 'mean delay' #'mean synchronization performance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title+'.png')
sio.savemat(title_no_space+'.mat', {title_no_space: mean_metric_Ds_policies})


# mean variance
plt.figure(figsize=(16,9))
colors = itertools.cycle(('blue', 'red', 'yellow',  'purple','black')) 
for i in range(len(policies)):
    cdf(mean_metric_Vs_policies[i],labels[i],color = next(colors))
plt.legend(fontsize=20)
fig_title = 'mean variance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title+'.png')
sio.savemat(title_no_space+'.mat', {title_no_space: mean_metric_Vs_policies})


# mean QoE metrics
plt.figure(figsize=(16,9))
colors = itertools.cycle(('blue', 'red', 'yellow','purple','black')) 
mean_value = np.mean(mean_metrics_policies,axis=1)
median_value = np.median(mean_metrics_policies,axis=1)
percent_value = np.percentile(mean_metrics_policies,95,axis=1)
for i in range(len(policies)):
    cdf(mean_metrics_policies[i],labels[i]+"\n mean: %.3f, median: %.3f, 95%%: %.3f"%(mean_value[i],median_value[i],percent_value[i]),color = next(colors))
plt.legend(fontsize=20)
fig_title = 'mean QoE metrics'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title+'.png')
sio.savemat(title_no_space+'.mat', {title_no_space: mean_metrics_policies})

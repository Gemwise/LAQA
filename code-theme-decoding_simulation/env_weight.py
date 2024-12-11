# -*- coding: utf-8 -*-
"""
Created on Wed April 13 10:19:44 2023
@author: liangH
"""
import csv
import pickle

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
from algorithms.approx2_u import approx2_u_agent
from algorithms.brute_force import brute_agent
from def_classes import User, Frame
from utils import cal_bandwidth, cal_metric
import config, utils
import time
import os
from tqdm import tqdm

os.chdir("E:/lyq/02-myWork/1.decoding/codes/code-theme-decoding_simulation")


def save_data(policies, data_dict, base_filename, file_type='txt'):
    """
    保存数据到文件，支持多种文件类型。

    :param policies: 策略列表
    :param data_dict: 数据字典，键是数据名称，值是数据列表
    :param base_filename: 文件名的基础部分
    :param file_type: 文件类型，支持 'txt', 'csv', 'pkl'
    """
    for policy in policies:
        for data_name, data_list in data_dict.items():
            filename = f'{base_filename}_{policy}_{data_name}.{file_type}'
            if file_type == 'txt':
                with open(filename, 'w') as file:
                    file.write(f"{policy}: {data_list[policies.index(policy)]}\n")
            elif file_type == 'csv':
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Metric'])
                    for metric in data_list[policies.index(policy)]:
                        writer.writerow([metric])
            elif file_type == 'pkl':
                with open(filename, 'wb') as file:
                    pickle.dump(data_list[policies.index(policy)], file)
            else:
                raise ValueError("Unsupported file type. Use 'txt', 'csv', or 'pkl'.")


random_seed = 1

#%% preparation 
utils.read_table('tile_table_1row_4col.txt', utils.tile_dict_display)
utils.read_table('tile_table_1row_4col_120_150.txt', utils.tile_dict_tran)
# store the prediction results and required tile size
utils.read_size_table('./allneed/id2size_1080p_265.txt')
# utils.read_size_table('./id2size_4k_5m.txt')
utils.read_ID_table('./allneed/id2pose_1080p_265.txt')

# utils.read_for_10pose("./id2pose_5m_10.txt")
# utils.read_for_10size("./id2size_4k_5m_10.txt")
utils.read_for_10pose("./allneed/id2pose_4k_265.txt")
utils.read_for_10size("./allneed/id2size_4k_265.txt")
utils.read_for_8pose("./allneed/id2pose_2k_265.txt")
utils.read_for_8size("./allneed/id2size_2k_265.txt")
random.seed(random_seed)
np.random.seed(random_seed)

traces = []
with open('./traces/OfficeTrace_1.txt') as f:
    lines = f.readlines()
    for line in lines:
        traces.append(line.strip())

# to accelerate the simulation, we read the stored prediction results from the file
pred_traces = []
with open('./traces/pred_pos_office_1.txt') as f:
    lines = f.readlines()
    for line in lines:
        pred_traces.append(line.strip())

# get all the traces need
fcc_num = int(config.TOTAL_TRACE_NUM * config.CLIENT_NUM / 2)
fcc_root_dir = './FCCdataset/22-12set/'
fcc_trace_candidate = []
if os.path.exists(fcc_root_dir):
    dir_names = os.listdir(fcc_root_dir)
    dir_names = [dirname for dirname in dir_names if os.path.isdir(fcc_root_dir + dirname)]
    for dir_name in dir_names:
        trace_files = os.listdir(fcc_root_dir + dir_name)
        trace_files = [fcc_root_dir + dir_name + '/' + file_name for file_name in trace_files]
        fcc_trace_candidate.extend(trace_files)
trace_files_indexes = np.random.choice(len(fcc_trace_candidate), fcc_num, replace=True)
fcc_trace_files = np.array(fcc_trace_candidate)[trace_files_indexes]

# half of the trace from 4G dataset
lte_num = config.TOTAL_TRACE_NUM * config.CLIENT_NUM - fcc_num
lte_root_dir = '4Gdataset/dataset_4k/'
lte_trace_candidate = []
if os.path.exists(lte_root_dir):
    trace_files = os.listdir(lte_root_dir)
    trace_files = [lte_root_dir + file_name for file_name in trace_files]
    lte_trace_candidate.extend(trace_files)
trace_files_indexes = np.random.choice(len(lte_trace_candidate), lte_num)
lte_trace_files = np.array(lte_trace_candidate)[trace_files_indexes]

#开始选择取出对应文件
trace_files = []

trace_files.extend(fcc_trace_files.tolist())
trace_files.extend(lte_trace_files.tolist())

# 2d array(100*15)
split_traces_indexes = np.random.choice(np.arange(len(trace_files)), size=(config.TOTAL_TRACE_NUM, config.CLIENT_NUM),
                                        replace=False)
# list: 1500 net trace file path
trace_files = np.array(trace_files)[split_traces_indexes]

policies = [12]
config.FFMPEG = "265"
mean_qualities_policies = [[] for i in range(len(policies))]
mean_delays_policies = [[] for i in range(len(policies))]
var_delays_policies = [[] for i in range(len(policies))]
mean_metric_Ds_policies = [[] for i in range(len(policies))]
mean_metric_Vs_policies = [[] for i in range(len(policies))]
miss_rates_policies = [[] for i in range(len(policies))]
mean_metrics_policies = [[] for i in range(len(policies))]

mean_metrics_decode_policies = [[] for i in range(len(policies))]
mean_metrics_trans_policies = [[] for i in range(len(policies))]

init_time = time.time()

# add for decode time init
utils.init_decode_latency_rate()

# 外层循环
# for k in range(config.TOTAL_TRACE_NUM):

granularity_10 = config.TOTAL_TRACE_NUM - 90
granularity_20 = config.TOTAL_TRACE_NUM - 80
granularity_50 = config.TOTAL_TRACE_NUM - 50
granularity_100 = config.TOTAL_TRACE_NUM - 0

granularity = granularity_100
# gamma范围和粒度
start = 0.01
stop = 1.0
decimal_places = 4
gamma_range = np.round(np.linspace(start, stop, granularity), decimal_places)  # variance gama; trans alpf
# 改为进度条模式
for k in tqdm(range(granularity), desc="Round Processing", unit=" round", leave=True):
    # for k in range(1):
    config.GAMMA = np.round(gamma_range[k], decimal_places)
    # config.ALPHA = np.round(gamma_range[k], 3)

    labels = []
    # prepare the network trace for each user in this round
    net_traces = []
    # for trace_file in trace_files[k]:  # 2dim (100,15)
    for trace_file in trace_files[1]:  # 2dim (100,15) 固定就一种
        user_trace = []
        with open(trace_file) as f:
            lines = f.readlines()
            duration = 0
            t = 0
            for line in lines:
                tokens = line.split(' ')
                temp_duration = int(tokens[0]) / 1e3  # from microseconds to milliseconds
                throughput = tokens[1]
                throughput_MB = float(int(throughput) / 1e6)
                while (t + 1) * config.TIME_INTERVAL - duration < temp_duration:
                    user_trace.append(throughput_MB)
                    t += 1
                duration = t * config.TIME_INTERVAL
                if t >= config.T:
                    break
        net_traces.append(user_trace[:int(config.T)])
    net_traces = np.array(net_traces)

    policy_cnt = 0
    config.BITRATE_LEVELS = 6  # quality L = 6
    config.DECODE = True  # 考虑 decoding time
    for policy in policies:

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
            config.BITRATE_LEVELS = 10
            agent = approx2_agent()
            agent.label = '4k'
        elif policy == 13:
            config.BITRATE_LEVELS = 8
            agent = approx2_agent()
            agent.label = '2k'
        elif policy == 14:
            # config.DECODE = False
            config.BITRATE_LEVELS = 10
            agent = approx2_u_agent()
            agent.label = '4k_u'
        labels.append(agent.label)

        if policy == 13:
            utils.change_decode_time('2k')
            tmp_id2pose = utils.id2pose
            tmp_pose2id = utils.pose2id
            tmp_id2size = utils.id2size
            utils.id2size = utils.id2size_8
            utils.id2pose = utils.id2pose_8
            utils.pose2id = utils.pose2id_8
            pred_results = []
            tile_sizes = np.zeros((config.BITRATE_LEVELS, len(pred_traces) - 1))
            qualities = [38, 34, 30, 26, 22, 18, 17, 15]

            for i in range(len(pred_traces) - 1):
                result = utils.get_pred_result(pred_traces[i], traces[i + 1])
                pred_results.append(result)
                for quality in qualities:
                    size = utils.get_total_size_of_pose(pred_traces[i], quality)
                    tile_sizes[qualities.index(quality)][i] = size
            utils.id2size = tmp_id2size
            utils.id2pose = tmp_id2pose
            utils.pose2id = tmp_pose2id

        elif policy == 12 or policy == 14:
            utils.change_decode_time('4k')
            tmp_id2pose = utils.id2pose
            tmp_pose2id = utils.pose2id
            tmp_id2size = utils.id2size

            utils.id2size = utils.id2size_10
            utils.id2pose = utils.id2pose_10
            utils.pose2id = utils.pose2id_10
            pred_results = []
            tile_sizes = np.zeros((config.BITRATE_LEVELS, len(pred_traces) - 1))
            qualities = [43, 39, 35, 31, 27, 23, 21, 19, 17, 15]
            for i in range(len(pred_traces) - 1):
                result = utils.get_pred_result(pred_traces[i], traces[i + 1])
                pred_results.append(result)
                for quality in qualities:
                    size = utils.get_total_size_of_pose(pred_traces[i], quality)
                    tile_sizes[qualities.index(quality)][i] = size
            utils.id2size = tmp_id2size
            utils.id2pose = tmp_id2pose
            utils.pose2id = tmp_pose2id

        else:
            utils.change_decode_time('1080p')
            pred_results = []
            tile_sizes = np.zeros((config.BITRATE_LEVELS, len(pred_traces) - 1))
            qualities = [35, 31, 27, 23, 19, 15]
            for i in range(len(pred_traces) - 1):
                result = utils.get_pred_result(pred_traces[i], traces[i + 1])
                pred_results.append(result)
                for quality in qualities:
                    size = utils.get_total_size_of_pose(pred_traces[i], quality)
                    tile_sizes[qualities.index(quality)][i] = size

        random.seed(random_seed)
        np.random.seed(random_seed)
        start_time = time.time()
        qualities = [3 for i in range(config.CLIENT_NUM)]  # initially, all qualities is 3
        users = [User(i, 1) for i in range(config.CLIENT_NUM)]

        # for t in range(int(config.T)):
        # 改为进度条模式
        for t in tqdm(range(config.T - 9500), desc="Processing Data", unit="item", leave=False):
            # prediction result
            pred_result = pred_results[t]

            config.SLOT_SIZE = tile_sizes[:, t]

            # modify the client rate limit based on the network trace
            # config.RATE_LIMIT_CLIENT = list(net_traces[:, t])
            config.RATE_LIMIT_CLIENT = [2 * x for x in net_traces[:, t]]  # 4K 数据集中带宽放大
            config.RATE_LIMIT_CLIENT_EST = [1 * rate for rate in config.RATE_LIMIT_CLIENT]

            # predetermine the delay for all clients, all qualities, to be used by following functionalities
            for i in range(config.CLIENT_NUM):
                users[i].cal_delay(t)

            qualities = agent.allocate(qualities, users)
            if sum([cal_bandwidth(quality) for quality in qualities]) > config.RATE_LIMIT_SERVER:
                print("total rate exceeds limit")

            delay = [users[i].next_delay[qualities[i]] for i in range(config.CLIENT_NUM)]

            cur_time = int(t * config.TIME_INTERVAL)
            for i in range(config.CLIENT_NUM):
                # generate frame for each user
                frame = Frame(cur_time, qualities[i], delay[i], config.SLOT_SIZE[qualities[i] - 1] / 1e6, pred_result,
                              delay[i] - utils.decode_time[qualities[i]][t], utils.decode_time[qualities[i]][t])
                users[i].update(cur_time, frame)
        end_time = time.time()
        # print("Time used: %.3f s"%(end_time-start_time))
        # print("%d round of policy %d finished, time used: %.3f s" % (k, policy_cnt, end_time - init_time))

        # get metrics :(2,quality) (4,variance)
        miss_rates, metric_Qs, metric_Ds, metric_Vs, metrics, delays, decode_d, trans_d = cal_metric(users)
        xs = []
        for i in range(config.CLIENT_NUM):
            # split those missed frames from the data
            x = [t for t in range(len(metric_Qs[i])) if metric_Qs[i][t] != -1]
            xs.append(x)

        # save quality
        mean_qualities = [np.mean(np.array(metric_Qs[i])[xs[i]]) for i in range(config.CLIENT_NUM)]
        # print("qualities:", np.round(mean_qualities))

        delays = [np.array(delays[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_delays = [np.mean(x) for x in delays]
        var_delays = [np.var(x) for x in delays]
        # print("mean delay: ",mean_delays)
        # print("variance of delays: ",var_delays)
        metric_Ds = [np.array(metric_Ds[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_metric_Ds = [np.mean(x) for x in metric_Ds]
        mean_metric_trans_d = [np.mean(x) for x in trans_d]  # transimission
        mean_metric_decode_d = [np.mean(x) for x in decode_d]  # decoding
        var_metric_Ds = [np.var(x) for x in metric_Ds]

        mean_metric_Vs = [np.var(np.array(metric_Qs[i])[xs[i]]) for i in range(config.CLIENT_NUM)]

        # recalculate the metrics over the whole time horizon
        metrics = [mean_qualities[i] - config.ALPHA * mean_metric_Ds[i] - config.GAMMA * mean_metric_Vs[i] for i in
                   range(config.CLIENT_NUM)]
        mean_metrics = [np.mean(metrics[i]) for i in range(config.CLIENT_NUM)]
        mean_metrics_sum = sum(mean_metrics)
        # print("mean QoE:", np.round(mean_metrics, 2))
        # print("SUM QoE:", np.round(mean_metrics_sum, 2))
        mean_qualities_policies[policy_cnt].append(np.round(np.mean(mean_qualities), 2))  # quality
        mean_delays_policies[policy_cnt].append(np.mean(mean_delays))
        var_delays_policies[policy_cnt].append(np.mean(var_delays))
        mean_metric_Ds_policies[policy_cnt].append(np.mean(mean_metric_Ds))

        mean_metrics_decode_policies[policy_cnt].append(np.round(np.mean(mean_metric_decode_d), 2))  # decoding
        mean_metrics_trans_policies[policy_cnt].append(np.round(np.mean(mean_metric_trans_d), 2))  # transimission

        mean_metric_Vs_policies[policy_cnt].append(np.round(np.mean(mean_metric_Vs), 2))  # variance
        miss_rates_policies[policy_cnt].append(np.mean(miss_rates))

        mean_metrics_policies[policy_cnt].append(np.mean(mean_metrics))

        policy_cnt += 1

# 保存到本地
# 将数据放入字典
data_dict = {
    'mean_metrics_trans': mean_metrics_trans_policies,
    'mean_metrics_decode': mean_metrics_decode_policies,
    'mean_qualities': mean_qualities_policies,
    'mean_metric_Vs': mean_metric_Vs_policies
}
# 保存数据到不同类型的文件
save_data(policies, data_dict, 'output', file_type='txt')


# save_data(policies, data_dict, 'output', file_type='csv')


# draw CDF figure
def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    return plt.plot(x, y, label=label, *args, **kwargs) if plot else (x, y)


plt.figure(figsize=(16, 9))
marker = itertools.cycle((',', '+', '.', 'o', '*'))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))

# quality
for i in range(len(policies)):
    cdf(mean_qualities_policies[i], labels[i], color=next(colors))

plt.legend(fontsize=20)
fig_title = 'mean qualities'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: np.array(mean_qualities_policies)})

plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
for i in range(len(policies)):
    cdf(mean_metric_Ds_policies[i], labels[i], color=next(colors))
plt.legend(fontsize=20)
fig_title = 'mean delay'  #'mean synchronization performance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metric_Ds_policies})

#decoding
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
for i in range(len(policies)):
    cdf(mean_metrics_decode_policies[i], labels[i], color=next(colors))
plt.legend(fontsize=20)
fig_title = 'mean decode delay'  #'mean synchronization performance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metrics_decode_policies})

#transimission
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
for i in range(len(policies)):
    cdf(mean_metrics_trans_policies[i], labels[i], color=next(colors))
plt.legend(fontsize=20)
fig_title = 'mean trans delay'  #'mean synchronization performance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metrics_trans_policies})

# plt.figure(figsize=(16,9))
# colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple')) 
# for i in range(len(policies)):
#     cdf(miss_rates_policies[i],labels[i],color = next(colors))
# plt.legend(fontsize=20)
# fig_title = 'missed frame rate'
# title_no_space = '_'.join(fig_title.split(' '))
# plt.title(fig_title)
# plt.savefig(fig_title+'.png')
# sio.savemat(title_no_space+'.mat', {title_no_space: miss_rates_policies})

# variance
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
for i in range(len(policies)):
    cdf(mean_metric_Vs_policies[i], labels[i], color=next(colors))
plt.legend(fontsize=20)
fig_title = 'mean variance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metric_Vs_policies})

plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
mean_value = np.mean(mean_metrics_policies, axis=1)
median_value = np.median(mean_metrics_policies, axis=1)
percent_value = np.percentile(mean_metrics_policies, 95, axis=1)
for i in range(len(policies)):
    cdf(mean_metrics_policies[i],
        labels[i] + "\n mean: %.3f, median: %.3f, 95%%: %.3f" % (mean_value[i], median_value[i], percent_value[i]),
        color=next(colors))
plt.legend(fontsize=20)
fig_title = 'mean QoE metrics'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metrics_policies})

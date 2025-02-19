
import numpy as np
import random
import matplotlib.pyplot as plt
import itertools
import scipy.io as sio

from algorithms.approx2 import approx2_agent
from algorithms.rl_ctr_ddpg import RL_CTRL
from def_classes import User, Frame
from utils import cal_bandwidth, cal_metric
import config
import utils
import time
import os
import psutil

def cdf(x, label, plot=True, *args, **kwargs):
    """
    计算并绘制给定数据的累积分布函数（CDF）。

    参数:
    - x: 一个包含数据的列表或数组，数据将被用于计算CDF。
    - label: 用于图例的标签，表示数据集的标识。
    - plot: 一个布尔值，指示是否绘制CDF图形。如果为True，将绘制图形；如果为False，将返回x和y值。
    - *args, **kwargs: 其他参数，这些参数将传递给matplotlib的plot函数用于自定义图形的绘制。

    返回:
    - 如果plot为True，则返回matplotlib的plot函数调用的结果，允许进一步自定义图形。
    - 如果plot为False，则返回一个元组(x, y)，其中x是排序后的数据列表，y是对应的CDF值列表。
    """
    x, y = sorted(x), np.arange(len(x)) / len(x)  # 对x进行排序，并计算对应的CDF值
    return plt.plot(x, y, label=label, *args, **kwargs) if plot else (x, y)  # 根据plot参数决定是绘制图形还是返回x和y值


def write_rewards_to_file(rewards, file_path):
    # 检查文件是否存在，如果不存在则创建
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass  # 创建空文件

    with open(file_path, 'w') as file:
        for reward_i in rewards:
            file.write(f"{reward_i}\n")


def load_network_traces(trace_files, config_Time, config_T, k):
    """
    从给定的trace文件列表中读取网络吞吐量数据，并返回一个二维数组。

    参数:
    - trace_files: 一个列表，包含所有trace文件的路径。
    - config: 包含配置参数的模块或类，例如TOTAL_TRACE_NUM, TIME_INTERVAL, T等。
    - k: 用于从trace_files中选择特定组文件的索引。

    返回:
    - net_traces: 一个二维数组，其中每一行代表一个用户在不同时间点上的网络吞吐量（以MB为单位）。
    """
    net_traces = []
    for trace_file in trace_files[k]:  # 假设trace_files是一个二维列表，k用于选择特定的行
        user_trace = []
        with open(trace_file) as f:
            lines = f.readlines()
            duration = 0
            t = 0
            for line in lines:
                tokens = line.split(' ')
                temp_duration = int(tokens[0]) / 1e3  # 从微秒转换为毫秒
                throughput = tokens[1]
                throughput_MB = float(int(throughput) / 1e6)
                while (t + 1) * config_Time - duration < temp_duration:
                    user_trace.append(throughput_MB)
                    t += 1
                duration = t * config_Time
                if t >= config_T:
                    break
        net_traces.append(user_trace[:int(config_T)])
    net_traces = np.array(net_traces)
    return net_traces


def save_rewards_to_file(episode_rewards, filename):
    """
    将QoE数据写入文件。

    参数:
    - episode_rewards: 包含QoE数据的集合。
    - file_name: 目标文件名，数据将被写入到这个文件中。
    """
    with open(filename, 'w') as file:
        for reward_i in episode_rewards:
            file.write(f"{reward_i}\n")
    print(f"Rewards saved to {filename}")


def plot_rewards(filename, fig_name):
    """
        从文件中读取QoE数据并绘制图形。

        参数:
        - file_name: 包含QoE数据的文件名。
        """
    rewards = np.loadtxt(filename)
    plt.plot(rewards)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    figure_title = fig_name
    plt.title(figure_title)
    plt.savefig(figure_title + '.png')
    plt.show()


def process_rewards(episode_rewards, file_name, fig_name):
    """
    处理QoE数据：将其写入文件，然后从文件中读取并绘制图形。

    参数:
    - episode_rewards: 包含QoE数据的集合。
    - file_name: 目标文件名，数据将被写入到这个文件中，也从这里读取数据进行绘图。
    """
    # 将QoE数据写入文件
    save_rewards_to_file(episode_rewards, file_name)

    # 从文件中读取数据并绘制图形
    plot_rewards(file_name, fig_name)


def get_cpu_memory_usage(interval):
    # 获取当前进程的 PID
    pid = psutil.Process()
    cpu_percent = pid.cpu_percent(interval=interval)
    memory_info = pid.memory_info()
    memory_usage_mb = memory_info.rss / (1024 * 1024)
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory_usage_mb:.2f} MB")


# preparation
utils.read_table('./tile_table_1row_4col.txt', utils.tile_dict_display)
utils.read_table('./tile_table_1row_4col_120_150.txt', utils.tile_dict_tran)
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
random_seed = 1
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

trace_files = []

trace_files.extend(fcc_trace_files.tolist())
trace_files.extend(lte_trace_files.tolist())

# 2d array(100*15)
split_traces_indexes = np.random.choice(np.arange(len(trace_files)), size=(config.TOTAL_TRACE_NUM, config.CLIENT_NUM),
                                        replace=False)
# list: 1500 net trace file path
trace_files = np.array(trace_files)[split_traces_indexes]

policies = [15]
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

# add for decode time init
utils.init_decode_latency_rate()

# algorithm start
print(f"CLIENT_NUM: {config.CLIENT_NUM}")

do_time = time.time()
QoE_epispde_set = []
file_name_esisode = 'episode_reward.txt'
random_indice = random.sample(range(config.TOTAL_TRACE_NUM), 1)[0]
net_traces = load_network_traces(trace_files, config.TIME_INTERVAL, config.T, random_indice)
NUM_EPISODE = 10  # TODO
NUM_STEP = config.T-9000  # TODO
STEP_INTERVAL = 10
labels = []  # algorithm name
for episode in range(NUM_EPISODE):
    policy_cnt = 0

    for policy in policies:
        init_time = time.time()
        agent = None

        if policy == 13:
            config.BITRATE_LEVELS = 8
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

        elif policy == 12 or policy == 14 or policy == 15:
            config.BITRATE_LEVELS = 10
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

        if policy == 15:
            agent = RL_CTRL(NUM_EPISODE, NUM_STEP, STEP_INTERVAL)
        labels.append(agent.label)

        initial_state = agent.reset()

        episode_reward = 0
        # QoE_step_set = [] # TODO
        qualities = [config.QUALITY_BASE for i in range(config.CLIENT_NUM)]
        users = [User(i, 1) for i in range(config.CLIENT_NUM)]

        for step in range(int(NUM_STEP)):
            train_start = time.time()
            # prediction result
            pred_result = pred_results[step]

            # modify the client rate limit based on the network trace
            config.SLOT_SIZE = tile_sizes[:, step]
            # config.RATE_LIMIT_CLIENT = list(net_traces[:, step])
            config.RATE_LIMIT_CLIENT = [2 * rate for rate in net_traces[:, step]]
            config.RATE_LIMIT_CLIENT_EST = [1 * rate for rate in config.RATE_LIMIT_CLIENT]

            for i in range(config.CLIENT_NUM):
                users[i].cal_delay(step)
            # ---ddpg start----
            # input state
            state = agent.get_state_vector(qualities, users)
            action = agent.allocate(state, episode, step)
            qualities = action

            '''
            total_bandwidth_current_qualities = sum([cal_bandwidth(quality) for quality in qualities])
            if total_bandwidth_current_qualities > config.RATE_LIMIT_SERVER:
                print(f"all client total rate {total_bandwidth_current_qualities} MB/s exceeds server limit {config.RATE_LIMIT_SERVER}")
            '''

            delay = [users[i].next_delay[qualities[i]] for i in range(config.CLIENT_NUM)]

            cur_time = int(step * config.TIME_INTERVAL)
            for i in range(config.CLIENT_NUM):
                # generate frame for each user
                size = config.SLOT_SIZE[qualities[i] - 1] / 1e6
                trans_delay = delay[i] - utils.decode_time[qualities[i]][step]
                decode_delay = utils.decode_time[qualities[i]][step]
                frame = Frame(cur_time, qualities[i], delay[i], size, pred_result, trans_delay, decode_delay)
                users[i].update(cur_time, frame)

            next_state, reward, done = agent.step(action, users)

            agent.ddpg_agent.replay_buffer.add(state, action, reward, next_state, done)

            episode_reward += reward

            if step % STEP_INTERVAL == 0:
                agent.ddpg_agent.train()
                train_end = time.time()
                print("doing (%d/%d episode -> step:%d) of policy %s, reward:%.2f, runtime: %.3f s"
                      % (episode + 1, NUM_EPISODE,
                         step + 1, agent.label,
                         reward,
                         train_end - train_start))
            # ---ddpg end----

        end_time = time.time()
        QoE_num_step = np.round(episode_reward / NUM_STEP, 2)
        QoE_epispde_set.append(QoE_num_step)
        print("%d round of policy %s finished, mean reward: %0.3f, round time: %.3f s" % (
            (episode + 1), agent.label, QoE_num_step, end_time - init_time))

        write_rewards_to_file(QoE_epispde_set, file_name_esisode)
        print(f"Rewards written to {file_name_esisode} at iteration {episode + 1}")

        # get metrics
        print("%d round of policy %s get metrics" % ((episode + 1), agent.label))
        miss_rates, metric_Qs, metric_Ds, metric_Vs, metrics, delays, decode_d, trans_d = cal_metric(users)
        xs = []
        for i in range(config.CLIENT_NUM):
            # split those missed frames from the data
            x = [t for t in range(len(metric_Qs[i])) if metric_Qs[i][t] != -1]
            xs.append(x)

        # quality for  users
        user_qualities = [np.array(metric_Qs[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_qualities = [np.mean(x) for x in user_qualities]
        # print(f"{config.CLIENT_NUM} client mean quality:{np.round(mean_qualities, 2)}")

        # delays for  users
        delays = [np.array(delays[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_delays = [np.mean(x) for x in delays]
        # print("mean delay: ", np.round(mean_delays, 2))

        var_delays = [np.var(x) for x in delays]
        # print("variance of delays: ", np.round(var_delays, 2))

        metric_Ds = [np.array(metric_Ds[i])[xs[i]] for i in range(config.CLIENT_NUM)]
        mean_metric_Ds = [np.mean(x) for x in metric_Ds]

        mean_metric_trans_d = [np.mean(x) for x in trans_d]
        mean_metric_decode_d = [np.mean(x) for x in decode_d]
        var_metric_Ds = [np.var(x) for x in metric_Ds]
        mean_metric_Vs = [np.var(np.array(metric_Qs[i])[xs[i]]) for i in range(config.CLIENT_NUM)]

        # recalculate the metrics over the whole time horizon
        metrics = [mean_qualities[i] - config.ALPHA * mean_metric_Ds[i] - config.GAMMA * mean_metric_Vs[i] for i in
                   range(config.CLIENT_NUM)]
        mean_metrics = [np.mean(metrics[i]) for i in range(config.CLIENT_NUM)]
        # print(f"{config.CLIENT_NUM} client mean QoE:{np.round(mean_metrics, 2)}")
        # print(f"clients mean QoE: {np.round(sum(mean_metrics) / config.CLIENT_NUM, 2)}")

        mean_qualities_policies[policy_cnt].append(np.mean(mean_qualities))
        mean_delays_policies[policy_cnt].append(np.mean(mean_delays))
        var_delays_policies[policy_cnt].append(np.mean(var_delays))
        mean_metric_Ds_policies[policy_cnt].append(np.mean(mean_metric_Ds))
        mean_metrics_decode_policies[policy_cnt].append(np.mean(mean_metric_decode_d))
        mean_metrics_trans_policies[policy_cnt].append(np.mean(mean_metric_trans_d))
        mean_metric_Vs_policies[policy_cnt].append(np.mean(mean_metric_Vs))
        miss_rates_policies[policy_cnt].append(np.mean(miss_rates))
        mean_metrics_policies[policy_cnt].append(np.mean(mean_metrics))

        policy_cnt += 1

end_time = time.time()
print(f"all {NUM_EPISODE} round finished, total time: {np.round(end_time - do_time, 3)}s, "
      f"mean QoE {np.round(np.mean(QoE_epispde_set), 3)}")


# draw CDF figure
print("draw CDF figure")

globa_decimal = 2
# 1.qualities
plt.figure(figsize=(16, 9))
marker = itertools.cycle((',', '+', '.', 'o', '*'))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
# Convert it to a NumPy array
mean_qualities_policies = np.array(mean_qualities_policies)
for i in range(len(policies)):
    cdf(mean_qualities_policies[i], labels[i], color=next(colors))
    print(f"policy {labels[i]} mean quality: {np.round(mean_qualities_policies[i].mean(), globa_decimal)}")

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
fig_title = 'mean delay'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metric_Ds_policies})


# 2.decoding
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
# Convert it to a NumPy array
mean_metrics_decode_policies = np.array(mean_metrics_decode_policies)
for i in range(len(policies)):
    cdf(mean_metrics_decode_policies[i], labels[i], color=next(colors))
    print(f"policy {labels[i]} decoding: {np.round(mean_metrics_decode_policies[i].mean(), globa_decimal)}")

plt.legend(fontsize=20)
fig_title = 'mean decode delay'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metrics_decode_policies})

# 3.transimission
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
# Convert it to a NumPy array
mean_metrics_trans_policies = np.array(mean_metrics_trans_policies)
for i in range(len(policies)):
    cdf(mean_metrics_trans_policies[i], labels[i], color=next(colors))
    print(f"policy {labels[i]} trans: {np.round(mean_metrics_trans_policies[i].mean(), globa_decimal)}")

plt.legend(fontsize=20)
fig_title = 'mean trans delay'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metrics_trans_policies})


# 4.variance
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
# Convert it to a NumPy array
mean_metric_Vs_policies = np.array(mean_metric_Vs_policies)
for i in range(len(policies)):
    cdf(mean_metric_Vs_policies[i], labels[i], color=next(colors))
    print(f"policy {labels[i]} Variance: {np.round(mean_metric_Vs_policies[i].mean(), globa_decimal)}")

plt.legend(fontsize=20)
fig_title = 'mean variance'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metric_Vs_policies})


# mean QoE
plt.figure(figsize=(16, 9))
colors = itertools.cycle(('blue', 'red', 'yellow', 'black', 'purple', 'pink', 'green', 'magenta'))
# mean_value = np.mean(mean_metrics_policies, axis=1)
# median_value = np.median(mean_metrics_policies, axis=1)
# percent_value = np.percentile(mean_metrics_policies, 95, axis=1)
# Convert it to a NumPy array
mean_metrics_policies = np.array(mean_metrics_policies)
for i in range(len(policies)):
    cdf(mean_metrics_policies[i], labels[i], color=next(colors))
    print(f"policy {labels[i]} QoE: {np.round(mean_metrics_policies[i].mean(), globa_decimal)}")
plt.legend(fontsize=20)
fig_title = 'mean QoE metrics'
title_no_space = '_'.join(fig_title.split(' '))
plt.title(fig_title)
plt.savefig(fig_title + '.png')
sio.savemat(title_no_space + '.mat', {title_no_space: mean_metrics_policies})

file_name = 'all_rewards.txt'
fig_name = 'all_rewards'
process_rewards(QoE_epispde_set, file_name, fig_name)

# file_name = 'step_rewards.txt'
# fig_name = 'step_rewards'
# process_rewards(QoE_step_set, file_name, fig_name)

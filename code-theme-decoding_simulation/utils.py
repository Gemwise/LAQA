
import numpy as np
import config

tile_dict_display = {}
tile_dict_tran = {}
id2pose = {}
pose2id = {}
id2size = {}
#add for more levels tile quality
id2pose_10 = {}
pose2id_10 = {}
id2size_10 = {}


def read_for_10pose(filename):
    with open(filename) as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            strs = line.split(" ")
            videoID = int(strs[0])
            pose = strs[1].strip()
            id2pose_10[videoID] = pose
            pose2id_10[pose] = videoID
            cnt += 1
    print(str(cnt) + " 10 levels ids read.")


def read_for_10size(filename):
    with open(filename) as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            strs = line.split(",")
            videoID = int(strs[0])
            size = int(strs[1])
            id2size_10[videoID] = size
            cnt += 1
    print(str(cnt) + " 10 levels id sizes read.")


id2pose_8 = {}
pose2id_8 = {}
id2size_8 = {}


def read_for_8pose(filename):
    with open(filename) as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            strs = line.split(" ")
            videoID = int(strs[0])
            pose = strs[1].strip()
            id2pose_8[videoID] = pose
            pose2id_8[pose] = videoID
            cnt += 1
    print(str(cnt) + " 8 levels ids read.")


def read_for_8size(filename):
    with open(filename) as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            strs = line.split(",")
            videoID = int(strs[0])
            size = int(strs[1])
            id2size_8[videoID] = size
            cnt += 1
    print(str(cnt) + " 8 levels id sizes read.")


# read table for tiles
def read_table(filename, tileDict):
    with open(filename) as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if i % 2 == 1:
                tokens = lines[i].split(',')
                tiles = [int(float(tile)) for tile in tokens]
                tileDict[lines[i - 1].strip()] = tiles


# read tile ID table corresponding to the pose
def read_ID_table(filename):
    with open(filename) as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            strs = line.split(" ")
            videoID = int(strs[0])
            pose = strs[1].strip()
            id2pose[videoID] = pose
            pose2id[pose] = videoID
            cnt += 1
    print(str(cnt) + " ids read.")


# read the tile size table for each tile
def read_size_table(filename):
    with open(filename) as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            strs = line.split(",")
            videoID = int(strs[0])
            size = int(strs[1])
            id2size[videoID] = size
            cnt += 1
    print(str(cnt) + " id sizes read.")


# get the float value of orientation from the string
def get_ori(recv_str):
    if ',' in recv_str:
        coor = recv_str.split(",")
    else:
        coor = recv_str.split(" ")
    orientations = np.zeros(2)
    for i in range(2):
        orientations[i] = float(coor[i + 2])
    return orientations


# get the position index from the float value
def get_pos_index(recv_str):
    granular = 5
    if ',' in recv_str:
        posStr = recv_str.split(",")
    else:
        posStr = recv_str.split(" ")
    positions = np.zeros(2)
    for i in range(2):
        positions[i] = cal_pos(float(posStr[i]), granular)
    pos = str(int(positions[0])) + "," + str(int(positions[1]))
    return pos


# get the videoID given the pose
def get_videoID(indexPos, tileID, quality):
    pose = indexPos + "," + str(tileID) + "," + str(quality)
    videoID = pose2id[pose]
    return videoID


def get_total_size_of_pose(pose, quality):
    total_size = 0
    index_pos = get_pos_index(pose)
    ori = get_ori(pose)
    if ori[0] > 90:
        ori[0] = 90
    if ori[0] < -90:
        ori[0] = -90
    coor = "(" + str(int(cal_angle(ori[0]))) + "," + str(int(cal_angle(ori[1]))) + ",0)"
    tiles = tile_dict_tran[coor]
    for tile_id in tiles:
        videoID = get_videoID(index_pos, tile_id, quality)
        total_size += id2size[videoID]
    return total_size


def get_pred_result(predPose, realPose):
    result = 1

    # requested tiles use real pose
    request_tiles = []
    index_pos = get_pos_index(realPose)
    ori = get_ori(realPose)
    if ori[0] > 90:
        ori[0] = 90
    if ori[0] < -90:
        ori[0] = -90
    coor = "(" + str(int(cal_angle(ori[0]))) + "," + str(int(cal_angle(ori[1]))) + ",0)"
    tiles = tile_dict_display[coor]
    for tile_id in tiles:
        videoID = get_videoID(index_pos, tile_id, 15)
        request_tiles.append(videoID)

    # get transmitted tiles use predicted pose
    trans_tiles = []
    index_pos = get_pos_index(predPose)
    ori = get_ori(predPose)
    if ori[0] > 90:
        ori[0] = 90
    if ori[0] < -90:
        ori[0] = -90
    coor = "(" + str(int(cal_angle(ori[0]))) + "," + str(int(cal_angle(ori[1]))) + ",0)"
    tiles = tile_dict_tran[coor]
    for tile_id in tiles:
        videoID = get_videoID(index_pos, tile_id, 15)
        trans_tiles.append(videoID)

    # detect whether all requested tiles are transmitted 
    for tileID in request_tiles:
        if tileID not in trans_tiles:
            result = 0
            break
    return result


# filter non-empty data in the dataset
def find_data(data):
    candidate = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j].shape[1] != 0:
                candidate.append([i, j])
    return candidate


def cal_angle(degree):
    result = (degree + 180) % 360 - 180
    return result


def cal_pos(pos, granular):
    return int(pos / granular) * granular


def cal_bandwidth(quality):
    tile_size = config.SLOT_SIZE[quality - 1]
    bandwidth = tile_size / (config.TIME_INTERVAL * 1e3)  #unit: MB/s
    return bandwidth


def cal_delay(size, rate, limit):
    if (rate >= limit):
        print("The transmission rate exceeds the limit")
        print("rate: %.3f limit: %.3f" % (rate, limit))
        return 100
    # keep the unit of size and rate unified (e.g., MB and MB/s)
    return max(size * 1000 / (limit - rate), 0)  # max(size*1000/(limit-rate)+np.random.normal(5),0) # unit: ms


def cal_delay_without_noise(size, rate, limit):
    if (rate >= limit):
        return 100
    # keep the unity of size and rate unified (e.g., MB and MB/s)
    return max(size * 1000 / (limit - rate), 0)  # unit: ms


def modi_quality(total_budget, qualities, index, tiles, flag):
    rate_client = cal_bandwidth(tiles, qualities[index])
    total_budget += rate_client
    qualities[index] += flag
    rate_client = cal_bandwidth(tiles, qualities[index])
    total_budget -= rate_client
    return total_budget, rate_client


def lru_update(lru_index):
    index = lru_index[0]
    del lru_index[0]
    lru_index.append(index)
    return index


def cal_metric(users):
    all_metric_Qs = []
    all_metric_Ds = []
    all_metric_Vs = []
    metrics = []
    miss_rates = []
    delays = []
    decode_delays = []
    trans_delays = []

    for user in users:

        miss_cnt = 0
        metric_Q_set = []
        metric_D_set = []
        metric_V_set = []
        metric_set = []
        delay_set = []
        trans_delay_set = []
        decode_delay_set = []

        for t in range(len(user.frame_show)):
            cur_frame = user.frame_show[t]
            if (cur_frame == 0):
                # miss_cnt += 1
                metric_Q_set.append(-1)
                metric_D_set.append(-1)
                metric_V_set.append(-1)
                delay_set.append(-1)
                trans_delay_set.append(-1)
                decode_delay_set.append(-1)
            else:
                if cur_frame.pred_flag == 1:
                    cur_quality = cur_frame.quality_level
                else:
                    # print('test not enter') # this branch should not be entered based on the metric policy
                    cur_quality = 0
                    miss_cnt += 1

                cur_delay = cur_frame.delay
                cur_decode = cur_frame.decode_delay
                cur_trans = cur_frame.trans_delay

                cur_metric_D = cur_delay

                metric_Q_set.append(cur_quality)
                metric_D_set.append(cur_metric_D)
                metric_V_set.append(user.var_set[t])
                trans_delay_set.append(cur_trans)
                decode_delay_set.append(cur_decode)

                metric = cur_quality - config.ALPHA * cur_metric_D - config.GAMMA * (
                            cur_quality - user.dynamic_mean) ** 2
                metric_set.append(metric)
                delay_set.append(cur_delay)

        delays.append(delay_set)
        metrics.append(metric_set)

        display = [frame for frame in user.frame_show if frame != 0]
        miss_rates.append((len(user.frame_pool) - len(display) + miss_cnt) / (len(user.frame_pool)))
        all_metric_Qs.append(metric_Q_set)  # quality
        all_metric_Ds.append(metric_D_set)
        all_metric_Vs.append(metric_V_set)  # variance
        decode_delays.append(decode_delay_set)  # decoding
        trans_delays.append(trans_delay_set)  # tranmission
    return miss_rates, all_metric_Qs, all_metric_Ds, all_metric_Vs, metrics, delays, decode_delays, trans_delays



'''
@brief  为H.265编码格式初始化一组解码延迟的概率分布，并为每个分布生成一个随机样本数组。
这些数组可以在程序的其他部分被使用，以便根据这些概率分布模拟解码延迟。   
'''
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


def init_decode_latency_rate():
    from scipy import stats
    global decode_15, decode_17, decode_18, decode_19, decode_21, decode_22, decode_23, decode_26, decode_27, decode_31, decode_32, decode_35, decode_37, decode_39, decode_41, decode_45
    #  Initialize all probability distributions
    if config.FFMPEG == "265":
        rv_15 = stats.moyal(loc=15.187618909617703, scale=0.9243979378233032)
        decode_15 = rv_15.rvs(size=config.T)
        rv_17 = stats.gumbel_r(loc=15.685988825565813, scale=1.4444752758328752)
        decode_17 = rv_17.rvs(size=config.T)
        rv_18 = stats.genhyperbolic(p=4.965859189271825, a=13.12061136218064, b=11.93257453083151,
                                    loc=12.21387791913532, scale=0.9801575862203098)
        decode_18 = rv_18.rvs(size=config.T)
        rv_19 = stats.fatiguelife(c=0.3904140173690742, loc=11.586301037982132, scale=4.824621972619786)
        decode_19 = rv_19.rvs(size=config.T)
        rv_21 = stats.nakagami(nu=1.0958863229705407, loc=13.012525382588521, scale=4.806536119819865)
        decode_21 = rv_21.rvs(size=config.T)
        rv_22 = stats.fisk(c=2.532250346708687, loc=13.385608572508655, scale=4.010822738803633)
        decode_22 = rv_22.rvs(size=config.T)
        rv_23 = stats.chi(df=2.2069166664167374, loc=13.034481749144806, scale=3.281140216858761)
        decode_23 = rv_23.rvs(size=config.T)
        rv_26 = stats.genhyperbolic(p=-6.400371109153772, a=6.582199875565699, b=6.574137258117165,
                                    loc=14.656036808384457, scale=4.703358897911535)
        decode_26 = rv_26.rvs(size=config.T)
        rv_27 = stats.alpha(a=6.534802117366002, loc=5.254583856858455, scale=75.80458392276533)
        decode_27 = rv_27.rvs(size=config.T)
        rv_31 = stats.exponnorm(K=1.37608835013218, loc=15.937673217759578, scale=1.1139330868167756)
        decode_31 = rv_31.rvs(size=config.T)
        rv_32 = stats.exponnorm(K=1.1238037906867968, loc=16.009218989813185, scale=1.274433713627745)
        decode_32 = rv_32.rvs(size=config.T)
        rv_35 = stats.exponnorm(K=1.3261872014120573, loc=16.172207939481183, scale=1.1374774389576907)
        decode_35 = rv_35.rvs(size=config.T)
        rv_37 = stats.exponnorm(K=1.078638204718267, loc=16.24120539600738, scale=1.3314483941028206)
        decode_37 = rv_37.rvs(size=config.T)
        rv_39 = stats.genlogistic(c=4.878734720283177, loc=15.12873778683704, scale=1.3839048468143753)
        decode_39 = rv_39.rvs(size=config.T)
        rv_41 = stats.genhyperbolic(p=-9.616296553899446, a=15.15434564949156, b=15.154345480012445,
                                    loc=13.032441315416811, scale=5.357633360943373)
        decode_41 = rv_41.rvs(size=config.T)
        rv_45 = stats.genhyperbolic(p=-4.2604775578274605, a=3.6777386478219736, b=3.6578067663531133,
                                    loc=15.242105418493662, scale=3.8498760521881144)
        decode_45 = rv_41.rvs(size=config.T)


decode_time = {}


def change_decode_time(solution='4k'):
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


def get_decode_latency_rates(quality, solution_rate='4k'):
    from scipy import stats
    if quality == 15:
        rv = stats.moyal(loc=15.187618909617703, scale=0.9243979378233032)
        data = rv.rvs(size=1000)
        latency = data
        return latency

# -*- coding: utf-8 -*-


import config
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
from utils import cal_bandwidth
import utils

np.random.seed(10)


class Network:
    # simulate M/M/1 queue, poisson arrival, poisson service
    def __init__(self):
        self.pkt_size = config.PKT_SIZE
        self.buffer = 0
        self.buffer_size = 1e26  #unlimited
        self.next_input = 0
        self.next_output = 0
        self.drop_flag = 0

    def arrival(self):
        if self.buffer < self.buffer_size:
            self.buffer += 1
        else:
            self.drop_flag = 1

    def departure(self):
        self.buffer = max(self.buffer - 1, 0)

    def network_slot(self, tile_size, input_rate, output_rate):
        # input: tile size: Byte, input rate: MB/s, output rate: MB/s
        # calculate the next service time only when there is packet in buffer
        arrival_times = []
        service_times = []
        time = 0
        total_input_pkt_num = int(tile_size / self.pkt_size) + 1
        input_cnt = 0
        output_cnt = 0
        self.next_input = np.random.exponential(scale=(self.pkt_size / (input_rate * 1024)))
        #self.next_output = np.random.exponential(scale=(self.pkt_size/(output_rate*1024)))
        self.next_output = 1e26
        next_trigger = min(self.next_input, self.next_output)
        # while (time+next_trigger < config.TIME_INTERVAL and output_cnt < total_input_pkt_num):
        while (output_cnt < total_input_pkt_num):
            if self.next_input <= self.next_output:
                # new packet comes
                if self.buffer == 0:
                    # if no packets in buffer before, generate the service time for current packet
                    self.next_output = np.random.exponential(scale=(self.pkt_size / (output_rate * 1024)))
                else:
                    # else, minus the arrival time of current packet
                    self.next_output -= self.next_input
                # generate the arrival time for next packet
                self.next_input = np.random.exponential(scale=(self.pkt_size / (input_rate * 1024)))
                if input_cnt < total_input_pkt_num:
                    self.arrival()
                    input_cnt += 1
                    arrival_times.append(time + next_trigger)
            else:
                # new packet serviced
                if self.buffer != 0:
                    # only can be served when there is pakcet in buffer
                    output_cnt += 1
                    service_times.append(time + next_trigger)
                    self.departure()
                    self.next_input -= self.next_output
                    if self.buffer == 0:
                        # no packet remains in buffer, wait for next arrival packet
                        self.next_output = 1e26
                    else:
                        # generate the service time for next packet
                        self.next_output = np.random.exponential(scale=(self.pkt_size / (output_rate * 1024)))
                else:
                    print("something wrong")
            time += next_trigger
            next_trigger = min(self.next_input, self.next_output)
        print("tile sent time used: %.3f ms" % time)
        return arrival_times, service_times


# # test the M/M/1 queue, check with formula, match or not
# a_net = Network()
# arrival_rate = 5.5
# service_rate = 5.6
# tile_num = 1e6
# arrival_times,service_times = a_net.network_slot(tile_num*config.PKT_SIZE,arrival_rate,service_rate)    
# response_times = np.array(service_times) - np.array(arrival_times)
# target_mean = config.PKT_SIZE/(service_rate*1024-arrival_rate*1024)   
# print("mean response time calculated: %.3f"%np.mean(response_times))
# print("expected response time: %.3f"%(target_mean))

# network buffer class operates on frame level, add the remain time for last frame of current frame as delay
class FrameNetwork:
    def __init__(self):
        self.frame_in_buffer = []

    def gene_delay_for_frame(self, size, arrival_rate, service_rate):
        mean_service_time = size * 1000 / (service_rate - arrival_rate + 0.0001)  # to avoid over zero
        # return min(np.random.exponential(scale=mean_service_time),30)
        return mean_service_time

    def delay_new_frame(self, frame_size, arrival_rate, service_rate):
        delay = self.gene_delay_for_frame(frame_size, arrival_rate, service_rate)
        if len(self.frame_in_buffer) == 0:
            # all frames have already been sent
            return delay
        else:
            remain_delay = self.frame_in_buffer[-1].delay_remain
            if remain_delay > 0:
                #return remain_delay + delay
                # return max(delay,remain_delay) # inherit delay
                return delay  # do not consider accumulation
            else:
                return delay

    def update(self, frame):
        # add the new frame on transmission
        self.frame_in_buffer.append(frame)
        # if buffer is full
        if len(self.frame_in_buffer) > config.BUFFER_LIMIT:
            # clear the first frame
            # del self.buffer[0]
            # clear half of the old frames
            for k in range(int(len(self.frame_in_buffer) / 2)):
                del self.frame_in_buffer[0]
        for frame in self.frame_in_buffer:
            # delay minus consumed time
            frame.delay_remain -= config.TIME_INTERVAL
            # if some tiles have been transmitted, update the frame status to ready
            if (frame.delay_remain <= 0):
                # set the status to ready
                frame.ready_flag = 1


class Frame:
    def __init__(self, init_time, quality, delay, size, pred_result, trans_delay=0, decode_delay=0):
        self.start_time = init_time
        self.display_time = -1
        self.quality_level = quality
        self.size = size
        self.delay = delay
        self.delay_remain = delay
        self.ready_flag = 0
        self.pred_flag = pred_result
        self.trans_delay = trans_delay
        self.decode_delay = decode_delay


class User:
    def __init__(self, num, display_policy):
        self.id = num
        self.TARGET_FPS = config.TARGET_FPS
        self.TIME_INTERVAL = config.TIME_INTERVAL
        self.frame_show = []
        self.frame_pool = {}  # 注意 这里是字典，和其他成员的类型不同
        self.dynamic_var = 0
        self.dynamic_mean = 0
        self.mean_quality_paper = 0
        self.estimated_delay = 0
        self.display_num = 0
        self.pred_fail_num = 0
        self.dev_delay = 0
        self.est_pred = 1
        self.time_slot = 0
        self.var_set = []  # 存放所有的方差
        self.train_x = []
        self.train_y = []
        polynomial_features = PolynomialFeatures(degree=5)
        linear_regression = LinearRegression()
        self.delay_model = Pipeline([("polynomial_features", polynomial_features),
                                     ("linear_regression", linear_regression)])
        self.display_policy = display_policy
        self.network_buffer = FrameNetwork()
        self.next_delay = {}  # 注意 这里是字典，和其他成员的类型不同

    def cal_delay(self, timeslot=1):
        """
        calculate the delay for all possible qualities based on current network buffer
        :param timeslot:
        :return:
        """
        quality = 1

        while quality <= config.BITRATE_LEVELS:
            rate = cal_bandwidth(quality)  # Mbytes/S
            if rate > config.RATE_LIMIT_CLIENT[self.id]:
                self.next_delay[quality] = 500  # 可能表示一个高延迟值，表示当前质量级别不可行。
            if quality not in self.next_delay:
                if config.DECODE:
                    self.next_delay[quality] = (
                            self.network_buffer.delay_new_frame(config.SLOT_SIZE[quality - 1] / 1e6,
                                                                rate,
                                                                config.RATE_LIMIT_CLIENT[self.id]) +
                            utils.decode_time[quality][timeslot])
                else:
                    self.next_delay[quality] = (
                        self.network_buffer.delay_new_frame(config.SLOT_SIZE[quality - 1] / 1e6,
                                                            rate,
                                                            config.RATE_LIMIT_CLIENT[self.id]))
            quality += 1

    def update(self, cur_time, frame):
        self.time_slot += 1
        cnt = self.time_slot  # count of passed frames
        # update the mean and variance of quality
        if frame.pred_flag == 1:
            quality = frame.quality_level
        else:
            quality = 0

        # for delay prediction
        if config.DELAY_PRED:
            self.train_x.append(frame.size * 1000 / config.TIME_INTERVAL)
            self.train_y.append(frame.delay)
            self.delay_model.fit(np.array(self.train_x).reshape(-1, 1), np.array(self.train_y))

        self.dynamic_var = (cnt - 1) * self.dynamic_var / cnt + (quality - self.dynamic_mean) ** 2 / (cnt + 1)
        self.dynamic_mean = (quality + cnt * self.dynamic_mean) / (cnt + 1)

        # 加权平均的变体, 这里的权重不仅取决于数据点的数量，还取决于时间间隔
        self.mean_quality_paper = (self.mean_quality_paper + config.GAMMA * (quality - self.mean_quality_paper) /
                                   (int(cur_time / config.TIME_INTERVAL) + 1 + config.GAMMA))

        self.var_set.append(self.dynamic_var)
        # 预测成功率        
        self.est_pred = (frame.pred_flag + cnt * self.est_pred) / (cnt + 1)
        # 查看池子大小是否 超过0
        if len(self.network_buffer.frame_in_buffer) > 0:
            del self.network_buffer.frame_in_buffer[0]
        self.frame_show.append(frame)
        self.display_num += 1

        # update network buffer
        self.network_buffer.update(frame)
        self.next_delay = {}

        self.frame_pool[frame.start_time] = frame

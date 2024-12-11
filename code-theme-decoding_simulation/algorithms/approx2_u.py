# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 10:19:17 2021

@author: chenj
"""

from utils import cal_bandwidth, cal_delay_without_noise
import numpy as np
import config 


class approx2_u_agent():
    def __init__(self):
        self.CLIENT_NUM = config.CLIENT_NUM
        self.BITRATE_LEVELS = config.BITRATE_LEVELS
        self.ALPHA = config.ALPHA
        self.BETA = config.BETA
        self.GAMMA = config.GAMMA
        self.RESERVE = 0 # 0.75*total_budget/CLIENT_NUM
        # gap to judge whether the total budget is approximate to 0
        self.gap = 1
        self.TIME_INTERVAL = config.TIME_INTERVAL
        self.TILE_SIZE = config.TILE_SIZE
        self.lru_index = [i for i in range(config.CLIENT_NUM)]
        self.label = '2 approximation'
        self.mu = 0
        self.step_size = 0.00
        self.hist_mu = []
        self.time_slot = 0
        self.delay_pred = 0
        
    #%% gradient descent algorithm
    def allocate(self,prev_qualities,users):
        self.time_slot += 1
        bandwidth_clients = [rate for rate in config.RATE_LIMIT_CLIENT_EST]

        # predict the delay for all possible rate
        if self.delay_pred == 1:
            # when the number of delays is small, only collect data without delay prediction
            if self.time_slot < 500:
                pred_delays = np.zeros((self.CLIENT_NUM,config.BITRATE_LEVELS))
            else:
                pred_delays = [[] for i in range(self.CLIENT_NUM)]
                for i in range(self.CLIENT_NUM):
                    bands = [cal_bandwidth(j+1) for j in range(config.BITRATE_LEVELS)]
                    delays = users[i].delay_model.predict(np.array(bands).reshape(-1,1))
                    pred_delays[i] = delays
        
        # density greedy algorithm
        d_qualities = [1 for i in range(self.CLIENT_NUM)]
        u_index = [i for i in range(self.CLIENT_NUM)]
        
        d_improve = 0
        while u_index:
            obj_incre = np.zeros(len(u_index))
            density = np.zeros(len(u_index))
            for i in range(len(u_index)):
                index = u_index[i]
                rate_high = cal_bandwidth(d_qualities[index]+1)
                rate_low = cal_bandwidth(d_qualities[index])
                
                if self.delay_pred == 0:
                    delay_portion = users[index].next_delay[d_qualities[index]+1]\
                        - users[index].next_delay[d_qualities[index]]
                else:
                    delay_portion = pred_delays[index][d_qualities[index]] - pred_delays[index][d_qualities[index]-1]
                
                old_mean = users[index].dynamic_mean
                var_portion = users[index].est_pred * (self.time_slot-1) * ((d_qualities[index]+1 - old_mean)**2 - (d_qualities[index] - old_mean)**2)/self.time_slot
                obj_incre[i] = users[index].est_pred - self.ALPHA*delay_portion \
                              - self.GAMMA*var_portion
                density[i] = obj_incre[i]/(rate_high-rate_low)

            # ----------------------------------------------------------------
            # 公平性修正
            # 从直接选取最大density 到 从较低质量的预选中 进行选择
            
            # 原来的处理
            # old_max_index1 = np.argmax(density)
            #max_index = np.argmax(density)
            #max_user_index = u_index[max_index]
            
            # 修正后
            
            #找出预先决策的 最小质量等级

            new_u_index = []
            new_desity = []

            min_quality = np.min(d_qualities)
            for i in range(len(u_index)):
                if abs(d_qualities[i] - min_quality) <= config.BITRATE_LEVELS/2:
                    new_u_index.append(u_index[i])
                    new_desity.append(density[i])

            max_index = new_u_index[np.argmax(new_desity)]
            max_user_index = u_index[max_index]
            # if old_max_index1 != max_index:
                # print(111);
            # print("changed max index" + str(max_index) + "change max u index"+str(max_user_index) )

            # 修正完成，未与上下文变量发生冲突与变换

            if density[max_index]<=0 :
                u_index = []
            else:
                d_qualities[max_user_index] += 1
                cur_rates = [cal_bandwidth(quality) for quality in d_qualities]
                if cur_rates[max_user_index] >= bandwidth_clients[max_user_index] or \
                    sum(cur_rates)>config.RATE_LIMIT_SERVER:
                    d_qualities[max_user_index] -= 1
                    u_index.remove(max_user_index)
                else:
                    d_improve += obj_incre[max_index]
                    # TODO: delete the potential violated client, accelerate
                    if d_qualities[max_user_index] == config.BITRATE_LEVELS:
                        u_index.remove(max_user_index)
                
        
        # value greedy algorithm
        v_qualities = [1 for i in range(self.CLIENT_NUM)]
        u_index = [i for i in range(self.CLIENT_NUM)]
        
        v_improve = 0
        while u_index:
            obj_incre = np.zeros(len(u_index))
            for i in range(len(u_index)):
                index = u_index[i]
                rate_high = cal_bandwidth(v_qualities[index]+1)
                rate_low = cal_bandwidth(v_qualities[index])
                
                if self.delay_pred == 0:
                    delay_portion = users[index].next_delay[v_qualities[index]+1]\
                        - users[index].next_delay[v_qualities[index]]
                else:
                    delay_portion = pred_delays[index][v_qualities[index]] - pred_delays[index][v_qualities[index]-1]
                    
                old_mean = users[index].dynamic_mean
                var_portion = users[index].est_pred * (self.time_slot-1) * ((v_qualities[index]+1 - old_mean)**2 - (v_qualities[index] - old_mean)**2)/self.time_slot
                 
                obj_incre[i] = users[index].est_pred - self.ALPHA*delay_portion \
                               - self.GAMMA*var_portion
                        # ----------------------------------------------------------------
            # 公平性修正
            # 从直接选取最大density 到 从较低质量的预选中 进行选择
            
            # 原来的处理
            # old_max_index2= np.argmax(obj_incre)
            # max_index = np.argmax(obj_incre)
            # max_user_index = u_index[max_index]
            
            # 修正后
            
            #找出预先决策的 最小质量等级

            new_u_index = []
            new_obj_incre = []

            min_quality = np.min(d_qualities)
            for i in range(len(u_index)):
                if abs(d_qualities[i] - min_quality) <= config.BITRATE_LEVELS/2:
                    new_u_index.append(u_index[i])
                    new_obj_incre.append(obj_incre[i])

            max_index = new_u_index[np.argmax(new_obj_incre)]
            max_user_index = u_index[max_index]

            # if old_max_index2 != max_index:
                # print(222);
            # print("changed max index" + str(max_index) + "change max u index"+str(max_user_index) )

            # 修正完成，未与上下文变量发生冲突与变换
            if obj_incre[max_index]<=0 :
                u_index = []
            else:
                v_qualities[max_user_index] += 1
                cur_rates = [cal_bandwidth(quality) for quality in v_qualities]
                if cur_rates[max_user_index] >= bandwidth_clients[max_user_index] or \
                    sum(cur_rates)>config.RATE_LIMIT_SERVER :
                    v_qualities[max_user_index] -= 1
                    u_index.remove(max_user_index)
                else:
                    v_improve += obj_incre[max_index]
                    if v_qualities[max_user_index] == config.BITRATE_LEVELS:
                        u_index.remove(max_user_index)
                
        if v_improve>d_improve:
            # value greedy better
            
            return v_qualities
        else:
            # density greedy better
            return d_qualities
"""
@File    : code-theme-decoding_simulation
@Name    : rl_ctr_ddpg.py
@Author  : lyq
@Date    : 2024/11/15 上午11:51
@Envi    : PyCharm
@Description:  文件描述
"""

import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque

import config
from utils import cal_bandwidth

# 判断是否使用 GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

if torch.cuda.is_available():
    print(f"{device}:{torch.cuda.is_available()}")
    print("device_count:", torch.cuda.device_count())
    print("current_device:", torch.cuda.current_device())
    print("device_name:", torch.cuda.get_device_name(0))


# Actor 和 Critic 网络
class Actor(nn.Module):
    def __init__(self, state_dim, action_dim, max_action, hidden_dim):
        super(Actor, self).__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_dim)
        self.max_action = max_action

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        # action = torch.tanh(self.fc3(x)) * self.max_action # 动作通常是连续的，使用 tanh 函数将其限制在 [-1, 1]
        action = torch.sigmoid(self.fc3(x)) * self.max_action  # 动作通常是连续的，使用 sigmoid 函数将其限制在 [0, 1]
        return action


class Critic(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim):
        super(Critic, self).__init__()
        self.fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)

    def forward(self, state, action):
        x = torch.cat([state, action], 1)  # 将状态和动作拼接在一起，形成一个整体输入
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        q_value = self.fc3(x)
        return q_value


# Replay Buffer
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=int(capacity))

    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        # 将各个特征转换为 numpy 数组，并确保形状符合要求
        states = np.array(states)  # 维度为 (batch_size, num_features)
        next_states = np.array(next_states)  # 维度为 (batch_size, num_features)
        actions = np.array(actions)  # 维度为 (batch_size, action_dim)
        rewards = np.array(rewards)  # 维度为 (batch_size, 1)
        dones = np.array(dones)  # 维度为 (batch_size, 1)

        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)


class DDPG_Agent:
    def __init__(self, **kwargs):

        # 从 kwargs 中读取并赋值参数，提供默认值以防止缺少参数
        self.state_dim = kwargs.get('state_dim')
        self.action_dim = kwargs.get('action_dim')
        self.max_action = kwargs.get('max_action')
        self.hidden_dim = kwargs.get('hidden_dim')  # 假设隐藏层默认维度为 64
        self.memory_size = kwargs.get('MEMORY_SIZE')  # 假设默认记忆大小为 10000
        self.batch_size = kwargs.get('BATCH_SIZE')  # 假设默认记忆大小为 64
        self.lr_actor = kwargs.get('LR_ACTOR')  # 假设默认 Actor 学习率为 0.001
        self.lr_critic = kwargs.get('LR_CRITIC')  # 假设默认 Critic 学习率为 0.001
        self.gamma = kwargs.get('GAMMA')  # 假设默认 Critic 学习率为 0.001
        self.tau = kwargs.get('TAU')  # 假设默认 Critic 学习率为 0.001

        self.actor = Actor(self.state_dim, self.action_dim, self.max_action, self.hidden_dim).to(device)
        self.actor_target = Actor(self.state_dim, self.action_dim, self.max_action, self.hidden_dim).to(device)
        self.actor_target.load_state_dict(self.actor.state_dict())

        self.critic = Critic(self.state_dim, self.action_dim, self.hidden_dim).to(device)
        self.critic_target = Critic(self.state_dim, self.action_dim, self.hidden_dim).to(device)
        self.critic_target.load_state_dict(self.critic.state_dict())

        self.actor_optimizer = optim.Adam(self.actor.parameters(), self.lr_actor)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), self.lr_critic)

        self.replay_buffer = ReplayBuffer(self.memory_size)

    def select_action(self, state):
        # 计算状态，经过 Actor 网络得到连续动作
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        continuous_actions = self.actor(state).cpu().data.numpy().flatten()  # 假设连续输出是一个 6 维向量

        # 将连续动作映射到离散动作集合 q ∈ {1, 2, ..., L}
        L = self.max_action  # 假设离散动作集合为 {1, 2, 3, 4}
        max_action = self.max_action  # 假设 max_action 是已知的最大动作值
        # 对每个动作维度进行离散化
        discrete_actions = []
        for action in continuous_actions:
            # 将连续动作值缩放到 [0, L-1]，并取整
            discrete_action = np.round((action / max_action) * (L - 1))
            # 确保动作值在合法范围内
            discrete_action = np.clip(discrete_action, 0, L - 1)
            # 映射到离散集合 {1, 2, ..., L}
            discrete_actions.append(int(discrete_action + 1))

        return np.array(discrete_actions)

    def train(self):
        if len(self.replay_buffer) <= self.batch_size:
            return

        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)

        # 转换为 PyTorch 张量并移动到 GPU（如果可用）
        states = torch.FloatTensor(states).to(device)  # 维度为 [batch_size, state_dim]
        actions = torch.FloatTensor(actions).to(device)  # 维度为 [batch_size, action_dim]
        rewards = torch.FloatTensor(rewards).reshape(-1, 1).to(device)  # 维度为 [batch_size, 1]
        next_states = torch.FloatTensor(next_states).to(device)  # 维度为 [batch_size, state_dim]
        dones = torch.FloatTensor(dones).reshape(-1, 1).to(device)  # 维度为 [batch_size, 1]

        # Target Critic Q value
        next_actions = self.actor_target(next_states)
        target_q = self.critic_target(next_states, next_actions.detach())  # 不执行
        target_q = rewards + (1 - dones) * self.gamma * target_q  # 计算 Target Critic的 Q value

        # 计算Critic的损失  ：MSE
        current_q = self.critic(states, actions)  # 当前 critic Q value
        critic_loss = nn.MSELoss()(current_q, target_q)
        # update Critic
        self.critic_optimizer.zero_grad()  # 清除上一步的梯度
        critic_loss.backward()  # 计算梯度
        self.critic_optimizer.step()  # 更新 critic 参数

        # update Actor 策略梯度的方式
        actor_loss = -self.critic(states, self.actor(states)).mean()
        self.actor_optimizer.zero_grad()
        actor_loss.backward()  # 计算梯度
        self.actor_optimizer.step()  # 更新 actor 参数
        # print(f"actor_loss: {actor_loss.item():.3f}, critic_loss: {critic_loss.item():.3f}")
        print(f"actor_loss: {actor_loss.item():.3f}")
        # Target networks update
        for param, target_param in zip(self.actor.parameters(), self.actor_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)


# User 类，确保随机初始值
class Client:
    def __init__(self):
        self.dynamic_var = np.random.uniform(0, 10)  # 动态变量，随机初始化为 [0, 10] 之间的浮点数
        self.dynamic_mean = np.random.uniform(0, 10)  # 估计的延迟，随机初始化为 [0, 10] 之间的浮点数
        self.mean_quality_paper = np.random.uniform(0, 10)  # 下一时隙的 qualit mean，随机初始化为 [0, 10] 之间的浮点数


class RL_CTRL:
    def __init__(self, num_episode, num_step, step_interval):
        # 初始化环境参数，包括带宽、质量、延迟等

        self.label = 'ddpg'
        self.users = None
        self.prev_qualities = None
        self.time_slot = 0
        self.client_num = config.CLIENT_NUM
        self.RATE_LIMIT_SERVER = config.RATE_LIMIT_SERVER
        self.RATE_LIMIT_CLIENT = config.RATE_LIMIT_CLIENT  # 会被更新
        self.RATE_LIMIT_CLIENT_EST = config.RATE_LIMIT_CLIENT_EST  # 会被更新
        self.max_quality_level = config.BITRATE_LEVELS
        self.ALPHA = config.ALPHA
        self.GAMMA = config.GAMMA
        self.safety_margin = config.SAFETY_MARGIN
        self.delay_pred = config.DELAY_PRED
        self.TIME_INTERVAL = config.TIME_INTERVAL
        self.TILE_SIZE = config.TILE_SIZE
        self.bandwidth_clients = [rate * self.safety_margin for rate in self.RATE_LIMIT_CLIENT]

        # 添加随机噪声的部分为 ε-greedy 策略
        self.num_episode = num_episode
        self.curren_episode = None
        self.num_step = num_step
        self.curren_step = None
        self.step_interval = step_interval
        self.epsilon_start = 1.0  # 起始的 epsilon 值，探索概率较高
        self.epsilon_end = 0.02  # 最终的 epsilon 值，探索概率降低
        self.epsilon_decay = self.num_episode * self.num_step / self.step_interval * 0.5

        # 初始化DDPG网络参数
        self.LR_ACTOR = 1e-4
        self.LR_CRITIC = 1e-3
        self.GAMMA = 0.99
        self.BATCH_SIZE = 64
        self.MEMORY_SIZE = 100000  # 1e5
        self.TAU = 5e-3
        self.HIDDEN_DIM = 64
        self.state_dim = self.client_num * 5  # 5个 state
        self.action_dim = self.client_num  # 如有6个客户端，每个动作表示对一个客户端的质量选择
        self.max_action = self.max_quality_level

        params = {
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'max_action': self.max_action,
            'hidden_dim': self.HIDDEN_DIM,
            'MEMORY_SIZE': self.MEMORY_SIZE,
            'LR_ACTOR': self.LR_ACTOR,
            'LR_CRITIC': self.LR_CRITIC,
            'BATCH_SIZE': self.BATCH_SIZE,
            'GAMMA': self.GAMMA,
            'TAU': self.TAU
        }
        self.ddpg_agent = DDPG_Agent(**params)

    def reset(self):
        # 初始化每个客户端的状态信息
        self.users = [
            Client()  # 使用 User 类实例化用户对象，并为每个用户设置随机初始值
            for _ in range(self.client_num)
        ]
        # 初始化上一个时隙的质量等级（随机初始化为 1到 4 之间的整数）
        self.prev_qualities = np.random.randint(1, self.max_quality_level, size=self.client_num)

        # 获取状态向量
        return self.get_state_vector(self.prev_qualities, self.users)

    def get_state_vector(self, prev_qualities, users):
        # 抽象状态构建逻辑为一个函数
        dynamic_vars = [users[i].dynamic_var for i in range(self.client_num)]
        dynamic_mean = [users[i].dynamic_mean for i in range(self.client_num)]
        mean_quality = [users[i].mean_quality_paper for i in range(self.client_num)]
        bandwidths = [cal_bandwidth(quality) for quality in prev_qualities]

        # 将所有特征合并为一个输入状态向量
        state_vector = np.concatenate([
            prev_qualities,
            bandwidths,
            dynamic_vars,
            dynamic_mean,
            mean_quality
        ])

        return state_vector

    def allocate(self, state_vector, curren_episode, current_step):

        self.curren_episode = curren_episode
        self.curren_step = current_step

        # 增加noise探索
        epsilon = np.interp(x=self.curren_episode * self.num_step + self.curren_step,
                            xp=[0, self.epsilon_decay],
                            fp=[self.epsilon_start, self.epsilon_end])
        random_sample = random.random()
        if random_sample <= epsilon:
            # 探索：选择一个随机离散动作
            actions = np.random.choice(range(1, self.max_quality_level + 1), size=self.action_dim)
        else:
            # 利用：使用 Actor 网络选择动作
            actions = self.ddpg_agent.select_action(state_vector)

        return actions

    def step(self, actions, users):
        # 根据输入动作，更新状态，计算奖励，返回下一状态和奖励
        # 执行动作后，根据逻辑更新状态
        next_state = self.get_state_vector(actions, users)
        reward = self.calculate_reward(actions, users)
        done = False

        return next_state, reward, done

    def calculate_reward(self, actions, users):
        pred_delays = []
        self.time_slot += 1
        self.RATE_LIMIT_CLIENT_EST = config.RATE_LIMIT_CLIENT_EST
        self.bandwidth_clients = [rate * self.safety_margin for rate in self.RATE_LIMIT_CLIENT_EST]
        self.users = users
        v_improve = 0  # 总改进
        penalty = 0  # 总惩罚
        selected_qualities = actions

        # predict the delay for all possible rate
        if self.delay_pred:
            # when the number of delays is small, only collect data without delay prediction
            if self.time_slot < 500:
                pred_delays = np.zeros((self.client_num, self.max_quality_level))
            else:
                pred_delays = [[] for i in range(self.client_num)]
                for i in range(self.client_num):
                    bands = [cal_bandwidth(j + 1) for j in range(self.max_quality_level)]
                    delays = self.users[i].delay_model.predict(np.array(bands).reshape(-1, 1))
                    pred_delays[i] = delays

        # 遍历每个客户端计算改进量和惩罚项
        for index in range(len(selected_qualities)):
            # 计算延迟变化
            # min(self.max_quality_level, selected_qualities[index])，避免pred_delays[index]数组index越界
            delay_portion = pred_delays[index][min(self.max_quality_level - 1, selected_qualities[index])]

            # 计算抖动变化
            old_mean = self.users[index].dynamic_mean
            var_portion = (self.users[index].est_pred * (self.time_slot - 1)
                           * ((selected_qualities[index] + 1 - old_mean) ** 2
                           - (selected_qualities[index] - old_mean) ** 2) / self.time_slot)
            # 质量增益奖励
            quality_reward = self.users[index].est_pred - self.ALPHA * delay_portion - self.GAMMA * var_portion
            if quality_reward > 0:
                v_improve += quality_reward  # 增加正向奖励

            # 带宽限制惩罚
            cur_rate = cal_bandwidth(selected_qualities[index])
            if cur_rate > self.bandwidth_clients[index] or sum(
                    [cal_bandwidth(q) for q in selected_qualities]) > config.RATE_LIMIT_SERVER:
                penalty += 10  # 惩罚过度使用带宽

        # 总奖励为改进减去惩罚
        reward = v_improve - penalty
        return reward

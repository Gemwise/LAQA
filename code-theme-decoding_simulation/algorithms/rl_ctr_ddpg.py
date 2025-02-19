"""
@File    : code-theme-decoding_simulation
@Name    : rl_ctr_ddpg.py
@Author  : lyq
@Date    : 2024/11/15 上午11:51
@Envi    : PyCharm
@Description:
"""

import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque

import config
from utils import cal_bandwidth


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

if torch.cuda.is_available():
    print(f"{device}:{torch.cuda.is_available()}")
    print("device_count:", torch.cuda.device_count())
    print("current_device:", torch.cuda.current_device())
    print("device_name:", torch.cuda.get_device_name(0))



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
        # action = torch.tanh(self.fc3(x)) * self.max_action
        action = torch.sigmoid(self.fc3(x)) * self.max_action
        return action


class Critic(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim):
        super(Critic, self).__init__()
        self.fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)

    def forward(self, state, action):
        x = torch.cat([state, action], 1)
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


        states = np.array(states)  #  (batch_size, num_features)
        next_states = np.array(next_states)  # (batch_size, num_features)
        actions = np.array(actions)  # (batch_size, action_dim)
        rewards = np.array(rewards)  # (batch_size, 1)
        dones = np.array(dones)  # (batch_size, 1)

        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)


class DDPG_Agent:
    def __init__(self, **kwargs):


        self.state_dim = kwargs.get('state_dim')
        self.action_dim = kwargs.get('action_dim')
        self.max_action = kwargs.get('max_action')
        self.hidden_dim = kwargs.get('hidden_dim')
        self.memory_size = kwargs.get('MEMORY_SIZE')
        self.batch_size = kwargs.get('BATCH_SIZE')
        self.lr_actor = kwargs.get('LR_ACTOR')
        self.lr_critic = kwargs.get('LR_CRITIC')
        self.gamma = kwargs.get('GAMMA')
        self.tau = kwargs.get('TAU')

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

        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        continuous_actions = self.actor(state).cpu().data.numpy().flatten()


        L = self.max_action
        max_action = self.max_action

        discrete_actions = []
        for action in continuous_actions:

            discrete_action = np.round((action / max_action) * (L - 1))

            discrete_action = np.clip(discrete_action, 0, L - 1)

            discrete_actions.append(int(discrete_action + 1))

        return np.array(discrete_actions)

    def train(self):
        if len(self.replay_buffer) <= self.batch_size:
            return

        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)


        states = torch.FloatTensor(states).to(device)
        actions = torch.FloatTensor(actions).to(device)
        rewards = torch.FloatTensor(rewards).reshape(-1, 1).to(device)
        next_states = torch.FloatTensor(next_states).to(device)
        dones = torch.FloatTensor(dones).reshape(-1, 1).to(device)

        # Target Critic Q value
        next_actions = self.actor_target(next_states)
        target_q = self.critic_target(next_states, next_actions.detach())
        target_q = rewards + (1 - dones) * self.gamma * target_q


        current_q = self.critic(states, actions)  # critic Q value
        critic_loss = nn.MSELoss()(current_q, target_q)
        # update Critic
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # update Actor
        actor_loss = -self.critic(states, self.actor(states)).mean()
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        # print(f"actor_loss: {actor_loss.item():.3f}, critic_loss: {critic_loss.item():.3f}")
        print(f"actor_loss: {actor_loss.item():.3f}")
        # Target networks update
        for param, target_param in zip(self.actor.parameters(), self.actor_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)


# User
class Client:
    def __init__(self):
        self.dynamic_var = np.random.uniform(0, 10)
        self.dynamic_mean = np.random.uniform(0, 10)
        self.mean_quality_paper = np.random.uniform(0, 10)


class RL_CTRL:
    def __init__(self, num_episode, num_step, step_interval):


        self.label = 'ddpg'
        self.users = None
        self.prev_qualities = None
        self.time_slot = 0
        self.client_num = config.CLIENT_NUM
        self.RATE_LIMIT_SERVER = config.RATE_LIMIT_SERVER
        self.RATE_LIMIT_CLIENT = config.RATE_LIMIT_CLIENT
        self.RATE_LIMIT_CLIENT_EST = config.RATE_LIMIT_CLIENT_EST
        self.max_quality_level = config.BITRATE_LEVELS
        self.ALPHA = config.ALPHA
        self.GAMMA = config.GAMMA
        self.safety_margin = config.SAFETY_MARGIN
        self.delay_pred = config.DELAY_PRED
        self.TIME_INTERVAL = config.TIME_INTERVAL
        self.TILE_SIZE = config.TILE_SIZE
        self.bandwidth_clients = [rate * self.safety_margin for rate in self.RATE_LIMIT_CLIENT]


        self.num_episode = num_episode
        self.curren_episode = None
        self.num_step = num_step
        self.curren_step = None
        self.step_interval = step_interval
        self.epsilon_start = 1.0
        self.epsilon_end = 0.02
        self.epsilon_decay = self.num_episode * self.num_step / self.step_interval * 0.5

        self.LR_ACTOR = 1e-4
        self.LR_CRITIC = 1e-3
        self.GAMMA = 0.99
        self.BATCH_SIZE = 64
        self.MEMORY_SIZE = 100000  # 1e5
        self.TAU = 5e-3
        self.HIDDEN_DIM = 64
        self.state_dim = self.client_num * 5
        self.action_dim = self.client_num
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

        self.users = [
            Client()
            for _ in range(self.client_num)
        ]

        self.prev_qualities = np.random.randint(1, self.max_quality_level, size=self.client_num)


        return self.get_state_vector(self.prev_qualities, self.users)

    def get_state_vector(self, prev_qualities, users):

        dynamic_vars = [users[i].dynamic_var for i in range(self.client_num)]
        dynamic_mean = [users[i].dynamic_mean for i in range(self.client_num)]
        mean_quality = [users[i].mean_quality_paper for i in range(self.client_num)]
        bandwidths = [cal_bandwidth(quality) for quality in prev_qualities]


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


        epsilon = np.interp(x=self.curren_episode * self.num_step + self.curren_step,
                            xp=[0, self.epsilon_decay],
                            fp=[self.epsilon_start, self.epsilon_end])
        random_sample = random.random()
        if random_sample <= epsilon:

            actions = np.random.choice(range(1, self.max_quality_level + 1), size=self.action_dim)
        else:

            actions = self.ddpg_agent.select_action(state_vector)

        return actions

    def step(self, actions, users):

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
        v_improve = 0
        penalty = 0
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


        for index in range(len(selected_qualities)):

            delay_portion = pred_delays[index][min(self.max_quality_level - 1, selected_qualities[index])]


            old_mean = self.users[index].dynamic_mean
            var_portion = (self.users[index].est_pred * (self.time_slot - 1)
                           * ((selected_qualities[index] + 1 - old_mean) ** 2
                           - (selected_qualities[index] - old_mean) ** 2) / self.time_slot)

            quality_reward = self.users[index].est_pred - self.ALPHA * delay_portion - self.GAMMA * var_portion
            if quality_reward > 0:
                v_improve += quality_reward


            cur_rate = cal_bandwidth(selected_qualities[index])
            if cur_rate > self.bandwidth_clients[index] or sum(
                    [cal_bandwidth(q) for q in selected_qualities]) > config.RATE_LIMIT_SERVER:
                penalty += 10


        reward = v_improve - penalty
        return reward

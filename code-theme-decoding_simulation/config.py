"""
@File    : code-theme-decoding_simulation
@Name    : config1.py
@Author  : lyq
@Date    : 2024/11/16 12:38
@Envi    : PyCharm 
@Description:  files details
"""

import numpy as np

# parameter for AR model
PRED_WIND = 20
DIM = 3
# 标志位 做对比实验
FFMPEG = '265'
DECODE = True
DELAY_PRED = True  # 传输延迟预测
SAFETY_MARGIN = 0.9  # 网络安全盈余

CLIENT_NUM = 15

TOTAL_TRACE_NUM = 100
QUALITY_BASE = 1  # initially, all client qualities is 1
BUFFER_LIMIT = 5000
BITRATE_LEVELS = 10
TARGET_FPS = 60
TIME_INTERVAL = int(1000 / TARGET_FPS) - 1
T = int(1e4)
PKT_SIZE = 1400
'''
Mbps 是兆比特每秒（Megabits per second）
MBps 兆字节每秒（Megabytes per second）
4K 60fps H.265 约在40Mbps到100Mbps之间,取一个中间值为60Mbps, CLIENT_NUM = 15
60 Mbps×15=900 Mbps
比特（bit）和字节（byte）之间的关系是8比特等于1字节:
将Mbps转换为MBps（兆字节每秒）: 1Mbps = 1/8 MBps
60 Mbps=60÷8=7.5 MBps
900 Mbps=900÷8=112.5 MBps
'''
RATE_LIMIT_CLIENT = [4.51, 5.41, 3.81, 8.01, 3.21]  # unit: MB/s
RATE_LIMIT_CLIENT_EST = [SAFETY_MARGIN * rate for rate in RATE_LIMIT_CLIENT]
RATE_LIMIT_SERVER = CLIENT_NUM * 10  # unit: MB/s,  7.5
# available tile combination
TILES_POOL = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 1, 2], [1, 2, 3], [2, 3, 0], [3, 0, 1]]

TILE_BASE = np.array([3300, 4000, 2500, 1500])
TILE_SIZE = [TILE_BASE * (i) for i in range(BITRATE_LEVELS + 1)]
SLOT_SIZE = [0 for i in range(BITRATE_LEVELS)]

# base delay for each client, consider the transmission and propogation delay and application-level processing
# different delay for each client
np.random.seed(10)
DELAY_BASE = np.zeros(CLIENT_NUM)
# hyperparameters
ALPHA = 0.02  # tranmission
BETA = 0.05  # decoding
GAMMA = 0.5  # variance

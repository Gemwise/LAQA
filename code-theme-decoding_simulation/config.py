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

FFMPEG = '265'
DECODE = True
DELAY_PRED = True
SAFETY_MARGIN = 0.9

CLIENT_NUM = 15

TOTAL_TRACE_NUM = 100
QUALITY_BASE = 1  # initially, all client qualities is 1
BUFFER_LIMIT = 5000
BITRATE_LEVELS = 10
TARGET_FPS = 60
TIME_INTERVAL = int(1000 / TARGET_FPS) - 1
T = int(1e4)
PKT_SIZE = 1400

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

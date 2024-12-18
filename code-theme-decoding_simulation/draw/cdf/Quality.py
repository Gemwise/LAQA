import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.io as scio
import scienceplots

os.chdir("E:/lyq/02-myWork/1.decoding/codes/code-theme-decoding_simulation/result")
data_1 = scio.loadmat("./265_all_hn_decode/mean_qualities.mat")
p1 = data_1['mean_qualities'][0]
k2 = data_1['mean_qualities'][2]
k4 = data_1['mean_qualities'][1]


def cdf(x, label, plot=True, *args, **kwargs):
    x, y = sorted(x), np.arange(len(x)) / len(x)
    color = 'red'
    if label == '1080P':
        color = '#2F7FC1'
    elif label == '2K':
        color = '#96C37D'
    else:
        color = '#D8383A'
    return plt.plot(x, y, label=label, *args, **kwargs, linewidth=1.5, color=color) if plot else (x, y)


with plt.style.context(['science', 'grid']):
    fig, ax = plt.subplots()
    ax.set(xlabel='Quality level')
    ax.set(ylabel='CDF $F(x)$')
    cdf(p1, "1080P")
    cdf(k2, "2K")
    cdf(k4, "4K")
    plt.autoscale(tight=True)
    plt.ylim(0, 1.0)
    plt.legend(loc='best')
    plt.tight_layout()
    os.chdir("E:/lyq/02-myWork/1.decoding/codes/code-theme-decoding_simulation/draw/cdf")
    plt.savefig('./Quality11.pdf', format='pdf', dpi=300, bbox_inches='tight')
    plt.show()

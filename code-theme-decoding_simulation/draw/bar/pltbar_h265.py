import matplotlib.pyplot as plt
import numpy as np
import os

# 获取当前脚本所在的目录路径
current_directory = os.path.dirname(os.path.abspath(__file__))
# 切换到当前目录
os.chdir(current_directory)

# 数据
categories = ['1080P', '2K', '4K']  # 类别 H.265
values1 = [16.93, 17.77, 18.67]  # 数据集1 Decode
values2 = [1.15, 1.50, 2.27]  # 数据集2 Encode
values3 = [1.36,1.47, 2.76]  # 数据集3 Transport

# 设置X轴类别间距
bar_width = 0.25  # 柱状图宽度
spacing = 0.1  # 类别间距

# 计算X轴偏移量
x = np.arange(len(categories))

# 绘图
plt.bar(x, values1, width=bar_width, label='Decode')
plt.bar(x , values2, width=bar_width, bottom=values1, label='Encode')
plt.bar(x , values3, width=bar_width, bottom=[i+j for i, j in zip(values1, values2)], label='Transport')

# 设置X轴刻度标签
plt.xticks(x , categories)

# 图表标签和标题
plt.xlabel('H.265')
plt.ylabel('Latency(ms)')
#plt.title('Stacked Bar Chart')

for i, (v1, v2, v3) in enumerate(zip(values1, values2, values3)):
    total_height = v1 + v2 + v3
    plt.text(i, v1/2, str(v1), ha='center')
    # plt.text(i, (v1 + v2), str(v2), ha='center')
    # plt.text(i, (total_height), str(v3), ha='center')
# 图例
plt.legend(loc='upper left', frameon=True,fontsize='small')

# 显示图表
plt.savefig('./Delay_composition_265.pdf',format='pdf',dpi=300)
plt.show()

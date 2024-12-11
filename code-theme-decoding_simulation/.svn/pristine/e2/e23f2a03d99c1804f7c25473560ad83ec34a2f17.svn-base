
import os

"""
@brief: 过滤数据
@param: source_file: 源文件名
@param: target_file: 目标文件名
@return: 无返回值
@note: 过滤掉数据小于13.0的数据

"""

# 获取当前脚本所在的目录路径
current_directory = os.path.dirname(os.path.abspath(__file__))
# 切换到当前目录
os.chdir(current_directory)

# 定义源文件名和目标文件名变量
# source_file = '1080p_together_half.txt'
# target_file = '1080p_together_half_new.txt'

source_file = '2k_together_half.txt'
target_file = '2k_together_half_new.txt'

# source_file = '4k_together_half.txt'
# target_file = '4k_together_half_new.txt'

# 以读模式打开源文件
with open(source_file, 'r') as file:
    lines = file.readlines()

# 创建一个列表来保存满足条件的数据
new_data = []

for line in lines:
    # 尝试将行数据转换为浮点数
    try:
        data = float(line.strip().split("\n")[0])
        # 如果数据大于20.0，则添加到新数据列表中
        data = data - 0.5
        new_data.append(data)
        # if data > 20.5 and  data < 35:
        #     data = data - 0.8
        #     new_data.append(data)
        # else:
        #     new_data.append(data)
    except ValueError:
        # 如果不能转换为浮点数，则跳过该行
        continue

# 以写模式打开目标文件
with open(target_file, 'w') as file:
    for data in new_data:
        file.write(f'{data}\n')

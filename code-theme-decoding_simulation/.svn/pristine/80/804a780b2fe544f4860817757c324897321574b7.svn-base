import matplotlib.pyplot as plt
import numpy as np
import scienceplots
import os
import csv
import pandas as pd

os.chdir("E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/box")

# folder_path = 'E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/box/decodeNum/1080p_H264_phone/fps'  # 替换为实际的文件夹路径
folder_path = 'E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/box/decodeNum/1080p_H264_PICO/fps'  # 替换为实际的文件夹路径
csv_files = []
min_row_count = float('inf')
data_dict = {}
counter = 1

# 遍历目录下的文件夹和文件
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(os.path.join(root, file))

# 统计CSV文件数量
csv_file_count = len(csv_files)
print("CSV文件数量:", csv_file_count)


# 读取每个CSV文件并找出数据行数最少的文件
for file_path in csv_files:
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader)
        
        if row_count < min_row_count:
            min_row_count = row_count
            min_row_file = file_path

# 打印数据行数最少的文件
print("数据行数最少的文件：", min_row_file)
print("最少的数据行数：", min_row_count)

# 读取每个CSV文件，仅读取最少行数的行，并保存到不同的列表中
for file_path in csv_files:
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        rows_to_read = min_row_count
        data_list = []

        for i, row in enumerate(reader):
            if i >= rows_to_read:
                break

            # 处理每行数据
            data_list.append(float(row[0]))
        
        # 保存数据列表到字典中，以数字序号作为键
        data_dict[counter] = data_list
        counter += 1
'''
        # 保存数据列表到字典中，以文件名作为键
        file_name = os.path.basename(file_path)
        data_dict[file_name] = data_list
'''


# 打印每个CSV文件的数据列表
for file_name, data_list in data_dict.items():
    print(f"文件名：{file_name}")
    for row in data_list:
        print(row)
    print()

#画出箱线图
df = pd.DataFrame(data = data_dict)


with plt.style.context(['science','grid']):
    df.boxplot(sym='')
    plt.xlabel("Number of Decoders")
    plt.ylabel("FPS ")
    # axes.boxplot(all_data,patch_artist=True) #描点上色
    plt.tight_layout()
    plt.savefig('box_decode_num_fps.pdf',format='pdf',dpi=300,bbox_inches='tight')
    plt.show()


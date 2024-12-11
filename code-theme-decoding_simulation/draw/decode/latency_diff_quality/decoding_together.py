# 使用Python的os模块和open函数来合并文件
import os
import random

# 定义要合并的文件列表  1080P
file_list_base = [
    "./decode_1080p_265_15.txt",
    "./decode_1080p_265_19.txt",
    "./decode_1080p_265_23.txt",
    "./decode_1080p_265_27.txt",
    "./decode_1080p_265_31.txt",
    "./decode_1080p_265_35.txt",
]

# 定义输出文件名
output_file = "1080p_together.txt"

# 初始化行数计数器
total_lines = 0

# 使用循环逐个读取文件
for file in file_list_base:
    # 使用os.path.basename获取文件名
    filename = os.path.basename(file)

    # 打印当前处理的文件名
    print(f"正在处理文件：{filename}")

    # 使用open函数以读模式打开当前文件
    with open(file, 'r') as infile:
        # 计算文件中的行数
        lines = sum(1 for line in infile)

        # 更新总行数计数器
        total_lines += lines

        # 打印当前文件的行数
        print(f"{filename} 有 {lines} 行")

# 打印总行数
print(f"总共有 {total_lines} 行")

# 使用open函数以写模式打开输出文件
with open(output_file, 'w') as outfile:
    for file in file_list_base:
        # 使用open函数以读模式打开当前文件
        with open(file, 'r') as infile:
            # 将当前文件的内容写入输出文件
            outfile.write(infile.read())

# 使用open函数以读模式打开输出文件
with open(output_file, 'r') as infile:
    # 计算输出文件中的行数
    output_lines = sum(1 for line in infile)

    # 打印输出文件的行数
    print(f"{output_file} 有 {output_lines} 行")


# 定义要读取的文件列表 2K
file_list_simple = [
    "./decode_2k_265_15.txt",
    "./decode_2k_265_17.txt",
    "./decode_2k_265_18.txt",
    "./decode_2k_265_22.txt",
    "./decode_2k_265_26.txt",
    "./decode_2k_265_31.txt",
    "./decode_2k_265_35.txt",
    "./decode_2k_265_39.txt",
]

# 定义输出文件名
output_file = "2k_together.txt"
# 初始化行数计数器
total_lines_simple = 0

# 使用循环逐个读取简单文件列表中的每个文件
for file in file_list_simple:
    # 使用os.path.basename获取文件名
    filename = os.path.basename(file)

    # 打印当前处理的文件名
    print(f"正在处理文件：{filename}")

    # 使用open函数以读模式打开当前文件
    with open(file, 'r') as infile:
        # 计算文件中的行数
        lines = sum(1 for line in infile)

        # 更新总行数计数器
        total_lines_simple += lines

        # 打印当前文件的行数
        print(f"{filename} 有 {lines} 行")

# 打印总行数
print(f"总共有 {total_lines_simple} 行")

# 使用open函数以写模式打开输出文件
with open(output_file, 'w') as outfile:
    # 将每个文件的内容写入输出文件
    for file in file_list_simple:
        with open(file, 'r') as infile:
            outfile.write(infile.read())

# 使用open函数以读模式打开输出文件
with open(output_file, 'r') as infile:
    # 计算输出文件中的行数
    output_lines_simple = sum(1 for line in infile)

    # 打印输出文件的行数
    print(f"{output_file} 有 {output_lines_simple} 行")

# 定义要读取的文件列表 4K
file_list_full = [
    "./decode_4k_265_15.txt",
    "./decode_4k_265_17.txt",
    "./decode_4k_265_19.txt",
    "./decode_4k_265_21.txt",
    "./decode_4k_265_23.txt",
    "./decode_4k_265_27.txt",
    "./decode_4k_265_32.txt",
    "./decode_4k_265_37.txt",
    "./decode_4k_265_41.txt",
    "./decode_4k_265_45.txt",
]

# 定义输出文件名
output_file = "4k_together.txt"
# 初始化行数计数器
total_lines_full = 0

# 使用循环逐个读取简单文件列表中的每个文件
for file in file_list_full:
    # 使用os.path.basename获取文件名
    filename = os.path.basename(file)

    # 打印当前处理的文件名
    print(f"正在处理文件：{filename}")

    # 使用open函数以读模式打开当前文件
    with open(file, 'r') as infile:
        # 计算文件中的行数
        lines = sum(1 for line in infile)

        # 更新总行数计数器
        total_lines_full += lines

        # 打印当前文件的行数
        print(f"{filename} 有 {lines} 行")

# 打印总行数
print(f"总共有 {total_lines_full} 行")

# 使用open函数以写模式打开输出文件
with open(output_file, 'w') as outfile:
    # 将每个文件的内容写入输出文件
    for file in file_list_full:
        with open(file, 'r') as infile:
            outfile.write(infile.read())

# 使用open函数以读模式打开输出文件
with open(output_file, 'r') as infile:
    # 计算输出文件中的行数
    output_lines_full = sum(1 for line in infile)

    # 打印输出文件的行数
    print(f"{output_file} 有 {output_lines_full} 行")


'''
这个代码会分别抽取 1080p_together.txt, 2k_together.txt, 和 4k_together.txt 里的文件内容的一半，
并保存为新的txt文档，文件名为原文件名加上 _half.txt 后缀。
'''
def random_half_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    random.shuffle(lines)
    half_lines = lines[:len(lines) // 2]

    new_file_path = os.path.splitext(file_path)[0] + '_half.txt'
    with open(new_file_path, 'w') as f:
        f.writelines(half_lines)

    return new_file_path

# 抽取1080p文件内容的一半
new_file_path_1080p = random_half_file('1080p_together.txt')
print(f"新1080p文件路径: {new_file_path_1080p}")

# 抽取2k文件内容的一半
new_file_path_2k = random_half_file('2k_together.txt')
print(f"新2k文件路径: {new_file_path_2k}")

# 抽取4k文件内容的一半
new_file_path_4k = random_half_file('4k_together.txt')
print(f"新4k文件路径: {new_file_path_4k}")

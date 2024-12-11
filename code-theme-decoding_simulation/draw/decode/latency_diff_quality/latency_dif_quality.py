import os
import pandas as pd


# folder_path = "E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/video2nanotime/decode_all"  # 指定文件夹路径
def check_row(row):
    return len(row) == 4


def main():
    folder_path = "E:/lyq/02-myWork/01-ICCC/ICCC_CODES/simulation/draw/video2nanotime/decode_all"  # 指定文件夹路径
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    result_dict = {}

    for file in csv_files:
        file_path = os.path.join(folder_path, file)

        # 读取CSV文件并跳过第一行
        df = pd.read_csv(file_path, header=None, skiprows=1)

        # 过滤不符合格式的行
        df = df[df.apply(check_row, axis=1)]

        # 统计第3列（索引为2）的平均值
        avg_value = (df.iloc[:, 2] / 1000000).mean().round(2)

        # 提取前500个元素并将它们缩小1000000倍，保留两位小数
        column_data = df.iloc[:500, 2] / 1000000  # us-->ms
        column_data = column_data.round(2)

        # 提取文件名，不包括后缀
        file_name_no_ext = os.path.splitext(file)[0]

        # 将数据保存到txt文件中
        column_data.to_csv(f'{file_name_no_ext}.txt', header=False, index=False, sep='\t')

        # 将结果存储在字典中
        result_dict[file] = avg_value

    # 打印结果
    for file, avg in result_dict.items():
        print(f"{file}: 平均值为 {avg}")


if __name__ == "__main__":
    main()


import csv
import pickle

def save_data(policies, data_dict, base_filename, file_type='txt'):
    """
    保存数据到文件，支持多种文件类型。

    :param policies: 策略列表
    :param data_dict: 数据字典，键是数据名称，值是数据列表
    :param base_filename: 文件名的基础部分
    :param file_type: 文件类型，支持 'txt', 'csv', 'pkl'
    """
    for policy in policies:
        for data_name, data_list in data_dict.items():
            filename = f'{base_filename}_{policy}_{data_name}.{file_type}'
            if file_type == 'txt':
                with open(filename, 'w') as file:
                    file.write(f"{policy}: {data_list[policies.index(policy)]}\n")
            elif file_type == 'csv':
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Metric'])
                    for metric in data_list[policies.index(policy)]:
                        writer.writerow([metric])
            elif file_type == 'pkl':
                with open(filename, 'wb') as file:
                    pickle.dump(data_list[policies.index(policy)], file)
            else:
                raise ValueError("Unsupported file type. Use 'txt', 'csv', or 'pkl'.")

# 示例数据
policies = ['policy1', 'policy2', 'policy3']

mean_metrics_trans_policies = [[] for _ in range(len(policies))]
mean_metrics_decode_policies = [[] for _ in range(len(policies))]
mean_qualities_policies = [[] for _ in range(len(policies))]
mean_metric_Vs_policies = [[] for _ in range(len(policies))]

# 填充示例数据
for i in range(len(policies)):
    mean_metrics_trans_policies[i] = [i * j for j in range(5)]
    mean_metrics_decode_policies[i] = [i * j for j in range(5)]
    mean_qualities_policies[i] = [i * j for j in range(5)]
    mean_metric_Vs_policies[i] = [i * j for j in range(5)]

# 将数据放入字典
data_dict = {
    'mean_metrics_trans': mean_metrics_trans_policies,
    'mean_metrics_decode': mean_metrics_decode_policies,
    'mean_qualities': mean_qualities_policies,
    'mean_metric_Vs': mean_metric_Vs_policies
}

# 保存数据到不同类型的文件
save_data(policies, data_dict, 'output', file_type='txt')
save_data(policies, data_dict, 'output', file_type='csv')
save_data(policies, data_dict, 'output', file_type='pkl')



# 从文本文件读取
for policy in policies:
    for data_name in data_dict.keys():
        filename = f'output_{policy}_{data_name}.txt'
        with open(filename, 'r') as file:
            line = file.readline()
            parts = line.strip().split(': ')
            metrics = list(map(float, parts[1].strip('[]').split(',')))
            print(f"Policy: {policy}, Data: {data_name}, Metrics: {metrics}")


# 从CSV文件读取
for policy in policies:
    for data_name in data_dict.keys():
        filename = f'output_{policy}_{data_name}.csv'
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # 读取表头
            metrics = [float(row[0]) for row in reader]
            print(f"Policy: {policy}, Data: {data_name}, Metrics: {metrics}")
import sys


def openreadtxt(file_name):
    quality = []
    delay = []
    varQuality = []

    with open(file_name, 'r') as file_data:
        for row in file_data:
            tmp_list = row.strip("\n").split(',')  # 去除首尾换行符，按‘,'切分每行的数据

            quality.append(tmp_list[1])
            delay.append(tmp_list[4])
            varQuality.append(tmp_list[5]) #我给改成带宽

    return quality, delay, varQuality


def openwritetxt(quality, delay, varQuality):


    file_quality = open('quality.txt', mode='w')
    file_delay = open('delay.txt', mode='w')
    file_varQuality = open('varQuality.txt', mode='w')

    sum = 0
    for i in range(len(quality)):
        file_quality.writelines(quality[i] + '\n')
        sum += int(quality[i])
    file_quality.close()

    mean_qualities = sum / len(quality)
    print("mean_qualities:",sum,len(quality),'%.4f' %mean_qualities)

    sum = 0.0
    for i in range(len(delay)):
        file_delay.writelines(delay[i] + '\n')
        sum += float(delay[i])
    file_delay.close()

    mean_delay = sum / len(delay)
    print("mean_delay:",sum,len(delay),'%.4f' %mean_delay)

    sum = 0.0
    for i in range(len(varQuality)):
        file_varQuality.writelines(varQuality[i] + '\n')
        sum += float(varQuality[i])
    file_varQuality.close()

    mean_varQuality= sum / len(varQuality)
    print("mean_varQuality:",sum, len(varQuality), '%.4f' % mean_varQuality)

    return mean_qualities,mean_delay,mean_varQuality



# calculate the QOE over the whole time horizon
# QOE = cur_quality - config.ALPHA*cur_metric_D - config.GAMMA*user.var_set[t]
def calculateQOE(mean_qualities,mean_delay,mean_varQuality):
    ALPHA = 0.1
    GAMMA = 0.5

    QOE = mean_qualities - ALPHA*mean_delay - GAMMA*mean_varQuality
    print("QOE=",'%0.4f' % QOE)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_folder = sys.argv[1].strip()
        print('%s' %input_folder)
    else:
        print("format: input_folder")
        sys.exit()

    quality, delay, varQuality = openreadtxt(input_folder)
    mean_qualities,mean_delay,mean_varQuality = openwritetxt(quality, delay, varQuality)
    calculateQOE(mean_qualities,mean_delay,mean_varQuality)


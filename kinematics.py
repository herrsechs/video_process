import os
import re
import numpy as np

SPEED_DIR = 'E:/video/kinematic/speed'
ACC_DIR = 'E:/video/kinematic/fwd_force'
STATISTIC_PATH = 'E:/video/kinematic/statistic.txt'


def get_file_data(file_obj):
    """
    Read all the line in a file and return a list of file data
    :param file_obj: file object
    :return: list
    """
    res = []
    for line in file_obj.readlines():
        try:
            res.append(float(line))
        except ValueError, e:
            print e.message
    return res


def make_statistic_file():
    """
    Merge speed and acceleration data into 6-d vector,
    including speed_max, speed_mean, speed_std, acc_min, acc_mean, acc_std.
    Write them into STATISTIC_PATH
    :return: 
    """
    num_pt = re.compile(r'\d+')
    out = open(STATISTIC_PATH, 'w')

    for f in os.listdir(SPEED_DIR):
        speed_file = open(os.path.join(SPEED_DIR, f), 'r')
        acc_file = open(os.path.join(ACC_DIR, f), 'r')

        speed_list = np.array(get_file_data(speed_file))
        acc_list = np.array(get_file_data(acc_file))

        stat_list = [speed_list.max(), speed_list.mean(), speed_list.std(),
                     acc_list.min(), acc_list.mean(), acc_list.std()]

        str_stat = str(stat_list).strip('[').strip(']')
        match = num_pt.search(f)
        if match:
            num = match.group()
            out.write(num + ',' + str_stat + '\n')


def merge_statistic_cnn(stat_path, cnn_path, label_path, out_path):
    """
    Merge data in statistic file and cnn feature vector file, 
    write them into one file
    :param stat_path: kinematic statics file 
    :param cnn_path: cnn feature vector file 
    :param label_path: video label file
    :param out_path: output file
    :return: 
    """
    stat_f = open(stat_path, 'r')
    cnn_f = open(cnn_path, 'r')
    label_f = open(label_path, 'r')
    out_f = open(out_path, 'w')

    stat_dict = dict()
    for line in cnn_f.readlines():
        line = line.strip('\n')
        ls = line.split(',')
        if 'e' in ls[1] or 'e' in ls[2] or 'e' in ls[3] or 'e' in ls[4]:
            continue
        stat_dict[ls[0]] = ','.join(ls[1:])

    for line in stat_f.readlines():
        line = line.strip('\n')
        ls = line.split(',')
        if ls[0] in stat_dict:
            stat_dict[ls[0]] = stat_dict[ls[0]] + ',' + ','.join(ls[1:])

    for line in label_f.readlines():
        line = line.strip('\n').strip('\r')
        ls = line.split(',')
        pt = re.compile(r'[0-9]+')
        evn = pt.search(ls[0]).group()
        if evn in stat_dict:
            stat_dict[evn] = stat_dict[evn] + ',' + ls[1]

    for (k, v) in stat_dict.items():
        vs = v.split(',')
        v = v.replace(',,', ',')
        if len(vs) >= 11:
            out_f.write(k + ',' + v + '\n')

    stat_f.close()
    cnn_f.close()
    out_f.close()


if __name__ == '__main__':
    merge_statistic_cnn(STATISTIC_PATH, 'E:/video/kinematic/feature.txt',
                        'E:/video/kinematic/label.txt', 'E:/video/kinematic/vector.txt')

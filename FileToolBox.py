# coding=utf-8
import os
import sys
import shutil
import xlrd
import xlwt
import numpy as np
import re


def extract_file_name(path, output, key_word):
    f = open(output, 'w')
    for file_name in os.listdir(path):
        if key_word in file_name:
            f.write(file_name + '\n')


def extract_event_number(path, output):
    num = 0
    f = open(output, 'w')
    for parent, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if 'Event' in filename:
                num += 1
                name = filename.split('Event')[1]
                name = name.split('.')[0]
                p = r'[0-9]+'
                pattern = re.compile(p)
                name = pattern.findall(name)[0]

                f.write(name + "\n")
    print num


def match_level(road_dict, address):
    for key, val in road_dict.items():
        if key in address:
            return val


def extract_road_level(road_level_path, address_path, target_path):
    rf = open(road_level_path)
    d = dict()
    for line in rf.readlines():
        arr = line.split('\t')
        if len(arr[0]) > 0:
            d[arr[0]] = arr[1]
    rf.close()

    af = open(address_path)
    out = open(target_path, 'w')
    for line in af.readlines():
        arr = line.split(',')
        level = match_level(d, arr[1])
        if level is None:
            level = '无\n'
        out.write(arr[0] + '  ' + level)
    af.close()
    out.close()


def move_files(name_list, src_path, target_path):
    """
    提取名称列表中的所有文件，并放到指定路径下
    :param name_list: 名称列表文件
    :param src_path: 
    :param target_path: 
    :return: 
    """
    names_file = open(name_list, 'r')
    names = []
    for line in names_file:
        names.append(line.strip('\n'))

    num = 0
    for parent, dirnames, filenames in os.walk(src_path):
        for filename in filenames:
            arr = filename.split('Event')
            if len(arr) > 1 and '-' in arr[1]:
                ev_num = arr[1].split('-')[0]
                if ev_num in names:
                    names.remove(ev_num)
                    try:
                        shutil.copyfile(parent + '/' + filename, target_path + '/' + filename)
                        # print filename + " has been moved"
                    except Exception, e:
                        # print e
                        num = num + 1
                        print filename.decode('gbk') # .encode('utf8').replace('•' , '·')
                        print 'Something wrong with ' + parent + '/' + filename
                else:
                    print ev_num + 'is not in the list'

    print num
    names_file.close()


def trim_filename(src):
    for filename in os.listdir(src):
        arr = filename.split('Event')
        if len(arr) > 1:
            os.rename(src + '/' + filename, src + '/' + arr[1])


def extract_gps_data(src, target1, target2):
    for filename in os.listdir(src):
        f = open(src + '/' + filename, 'r')
        out1 = open(target1 + '/' + filename, 'w')
        out2 = open(target2 + '/' + filename, 'w')
        for line in f.readlines():
            if 'lon' in line:
                out1.write(line.strip('lon '))
            elif 'lat' in line:
                out2.write(line.strip('lat '))
        out1.close()
        out2.close()


def extract_force_data(src, target1, target2):
    for filename in os.listdir(src):
        f = open(src + '/' + filename, 'r')
        out1 = open(target1 + '/' + filename, 'w')
        out2 = open(target2 + '/' + filename, 'w')
        for line in f.readlines():
            if 'fwd' in line:
                out1.write(line.strip('fwd '))
            elif 'lat' in line:
                out2.write(line.strip('lat '))
        out1.close()
        out2.close()


def write_excel_file(src, target, sheet_name):
    wbk = xlwt.Workbook()
    ws = wbk.add_sheet(sheet_name)

    row = 0
    for filename in os.listdir(src):
        f = open(src + '/' + filename, 'r')

        ws.write(row, 0, filename.strip('.txt'))
        col = 1
        for line in f.readlines():
            ws.write(row, col, line)
            col = col + 1
        f.close()
        row = row + 1
    wbk.save(target)


def change_label(src, target, old, new):
    f = open(src, 'r')
    out = open(target, 'w')
    for line in f.readlines():
        line = line.strip('\n')
        new_line = line
        arr = line.split(' ')
        if arr[1] == old:
            new_line = arr[0] + ' ' + new
        out.write(new_line + '\n')
    f.close()
    out.close()


def parse_pred(label_path, pred_path):
    table = np.zeros((3, 3))
    label_file = open(label_path, 'r')
    pred_file = open(pred_path, 'r')
    label = dict()
    for line in label_file.readlines():
        lines = line.split()
        label[lines[0]] = lines[1]

    for line in pred_file.readlines():
        lines = line.split()
        if lines[0] not in label:
            continue
        col = int(lines[1])
        row = int(label[lines[0]])
        table[row, col] = table[row, col] + 1

    print table
    print (table[0, 0] + table[1, 1] + table[2, 2]) / np.sum(table)


def matching_label(name_list_path, label_path, output):
    names = open(name_list_path, 'r')
    label_file = open(label_path, 'r')
    out = open(output, 'w')
    label_dict = dict()
    for line in label_file.readlines():
        label = line.split(' ')[1]
        number = line.split('_')[0].strip('Event')
        label_dict[number] = label

    for line in names.readlines():
        name = line.split('.')[0]
        if name not in label_dict:
            print '%s is not found' % name
            continue
        out.write(line.strip('\n') + ' ' + label_dict[name])


def read_risk_level(src, output):
    src_f = open(src, 'r')
    out_f = open(output, 'w')
    for line in src_f.readlines():
        if 'Near Collision' in line or 'Possible Collision' in line:
            out_f.write('1\n')
        elif 'Collision' in line:
            out_f.write('2\n')
        else:
            out_f.write('0\n')


import xml.dom.minidom as dom


def travel_xml(path):
    d = dom.parse(path)
    root = d.documentElement

    obj_list = root.getElementsByTagName('object')
    box_list = []
    for obj in obj_list:
        name_node = obj.getElementsByTagName('name')[0]
        name = name_node.childNodes[0].data
        bndbox = obj.getElementsByTagName('bndbox')[0]
        xmin = bndbox.getElementsByTagName('xmin')[0].childNodes[0].data
        ymin = bndbox.getElementsByTagName('ymin')[0].childNodes[0].data
        xmax = bndbox.getElementsByTagName('xmax')[0].childNodes[0].data
        ymax = bndbox.getElementsByTagName('ymax')[0].childNodes[0].data
        box_list.append([name, int(xmin), int(ymin), int(xmax), int(ymax)])
    return box_list


def extract_horizon(src, output):
    f = open(output, 'w')
    for parent, dirnames, filenames in os.walk(src):
        names = []
        horizon = None
        for filename in filenames:
            if 'Event' in filename:
                name = filename.split('Event')[1]
                name = name.split('.')[0]
                p = r'[0-9]+'
                pattern = re.compile(p)
                name = pattern.findall(name)[0]
                names.append(name)

            if '.jpg' in filename and 'horizon' in filename and horizon is None:
                print parent + ' ' + filename
                horizon = filename.split(',')[1][0:3]

        for n in names:
            if horizon is None:
                print 'No horizon file exists in %s ' % parent
                break
            f.write(n + ' ' + horizon + '\n')


def match_label(src_path, label_path, output):
    """
    
    :param src_path: video path 
    :param label_path: label file path
    :param output: video names and labels 
    :return: 
    """
    label_f = open(label_path, 'r')
    out_f = open(output, 'w')
    label_dict = {}
    for line in label_f.readlines():
        lines = line.split(' ')
        label_dict[lines[0]] = lines[1]

    for file_name in os.listdir(src_path):
        evn = file_name.strip('.jpg')
        if evn not in label_dict:
            print '%s is not in the label file.' % evn
            continue
        out_f.write(file_name + ' ' + label_dict[evn])


def move_file(src, out):
    for parent, dirnames, filenames in os.walk(src):
        for filename in filenames:
            if '.dce' in filename and 'DELETE' not in filename:
                shutil.copyfile(parent + '/' + filename, out + '/' + filename)


if __name__ == '__main__':
    # move_file('E:/video/group/group3/feedback/2015.6.1-2015.8.23', 'E:/video/dce')
    # match_label('E:/video/merge/stitch/', 'E:/video/merge/label.txt', 'E:/video/merge/stitch_label.txt')
    # extract_horizon('E:/video/group/group3', 'E:/video/group/group3/horizon.txt')
    travel_xml('D:/PedestrianDetection/xml/xml/batch1/FILE0006/FILE0006MOV65.xml')
    # read_risk_level('D:/Research_IMPORTANT/data/risk.txt',
    #                 'D:/Research_IMPORTANT/data/risk_level.txt')
    # matching_label('D:/Research_IMPORTANT/video/feedback/output_number.txt',
    #                'D:/Research_IMPORTANT/video/output/train_val.txt',
    #                'D:/Research_IMPORTANT/video/feedback/train_val.txt')
    # move_files('D:/Research_IMPORTANT/video/output/event.txt',
    #           'D:/Research_IMPORTANT/data/video/unclassified',
    #           'D:/Research_IMPORTANT/video/output/FINAL_TRAIN_DATA1')
    # trim_filename('D:/Research_IMPORTANT/video/output/FINAL_TRAIN_DATA1')
    # write_excel_file('D:/Research_IMPORTANT/video/output/direction',
    #                  'D:/Research_IMPORTANT/video/output/direction.xls',
    #                  'Direction')
    # extract_gps_data('D:/Research_IMPORTANT/video/output/gps',
    #                  'D:/Research_IMPORTANT/video/output/gps_lon',
    #                  'D:/Research_IMPORTANT/video/output/gps_lat')
    # extract_force_data('D:/Research_IMPORTANT/video/output/force',
    #                    'D:/Research_IMPORTANT/video/output/fwd_force',
    #                    'D:/Research_IMPORTANT/video/output/lat_force')
    # change_label('D:/Research_IMPORTANT/video/labels/3label_val.tmp1.txt',
    #              'D:/Research_IMPORTANT/video/labels/3label_val.txt',
    #              '3', '2')
    # extract_road_level('D:/Research_IMPORTANT/video/roadlevel/road.txt',
    #                    'D:/Research_IMPORTANT/video/output/address.txt',
    #                    'D:/Research_IMPORTANT/video/output/road_level.txt')
    # parse_pred('D:/bishe/paper/experiment/val.txt', 'D:/bishe/paper/experiment/pred.txt')
    # extract_event_number('D:/Research_IMPORTANT/video/group', 'D:/Research_IMPORTANT/video/evn.txt')
    # extract_file_name('D:/Research_IMPORTANT/video/feedback/merge/merge',
    #                   'D:/Research_IMPORTANT/video/feedback/output_number.txt', '.jpg')

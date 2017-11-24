# coding=utf-8
import os
import sys
import shutil
import xlrd
import xlwt
import numpy as np
import re
import cv2


def extract_file_name(path, output, key_word):
    f = open(output, 'w')
    for parent, dirnames, filenames in os.walk(path):
        for file_name in filenames:
            if key_word in file_name:
                f.write(file_name + ' ' + parent[-1] + '\n')


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
    for parent, dirnames, filenames in os.walk(src):
        for filename in filenames:
            p = r'[0-9]+'
            pattern = re.compile(p)
            name = re.findall(pattern, filename)[0]
            try:
                os.rename(parent + '/' + filename, src + '/' + name + '.dce')
            except WindowsError, e:
                print e.message


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
        if not 'ride' in name:
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
            if '.jpg' in filename and 'DELETE' not in filename:
                shutil.copyfile(parent + '/' + filename, out + '/' + filename)

class kdata:
    def __init__(self):
        self.spd = ''
        self.fwd = ''
        self.lat = ''


def stitch_kinematic_data(speed_folder, fwd_folder, lat_folder, out_path):
    kdata_dict = dict()
    p = r'[0-9]+'
    pattern = re.compile(p)
    for fname in os.listdir(speed_folder):
        f = open(speed_folder + '/' + fname, 'r')
        evn = pattern.findall(fname)[0]
        kd = kdata()
        for line in f.readlines():
            kd.spd += line.strip('\n') + ','
        kdata_dict[evn] = kd

    for fname in os.listdir(fwd_folder):
        f = open(fwd_folder + '/' + fname, 'r')
        evn = pattern.findall(fname)[0]
        if evn not in kdata_dict:
            continue
        kd = kdata_dict[evn]
        for line in f.readlines():
            kd.fwd += line.strip('\n') + ','
        kdata_dict[evn] = kd

    for fname in os.listdir(lat_folder):
        f = open(lat_folder + '/' + fname, 'r')
        evn = pattern.findall(fname)[0]
        if evn not in kdata_dict:
            continue
        kd = kdata_dict[evn]
        for line in f.readlines():
            kd.lat += line.strip('\n') + ','
        kdata_dict[evn] = kd

    out = open(out_path, 'w')
    for key, kd in kdata_dict.items():
        out.write(key + ',' + kd.spd + ',' + kd.fwd + ',' + kd.lat + '\n')


def find_missing_files(name_list_path, file_path, out, suffix='.jpg'):
    """
    Find missing files in motion images according to event number list
    :param name_list_path: path of name list file 
    :param file_path: folder path of videos or dces or motion images
                       OR name list file of event number
    :param out: output file path of missing file name list
    :param suffix: suffix of target file, like .dce, .jpg or .txt
    :return: 
    """

    path1 = name_list_path
    path2 = file_path
    f = open(path1, 'r')
    name_list = []
    for line in f.readlines():
        name_list.append(line.strip())
    f.close()

    file_list = []
    if os.path.isdir(path2):
        for file_name in os.listdir(path2):
            file_list.append(file_name.strip(suffix))
    elif os.path.exists(path2):
        with open(path2, 'r') as f2:
            for line in f2.readlines():
                pt = re.compile(r'[0-9]+')
                evn = pt.findall(line)[0]
                file_list.append(evn)

    missing = []
    for name in name_list:
        if name not in file_list:
            missing.append(name)

    with open(out, 'w') as o:
        for evn in missing:
            o.write(evn + '\n')


def move_files_with_name_list(src, out, name_list_file, suffix='.jpg'):
    """
    Move files from src to out according to the name list file
    Example:
    move_files_with_name_list('E:/video/categorization/avi/road_type/highway/',
                              'E:/car_speed_reconstruction/success_video',
                              'E:/car_speed_reconstruction/filelist.txt',
                              '_front.avi', '.jpg')
    :param src: source path  
    :param out: output path
    :param name_list_file: file path of name list 
    :param suffix: file name suffix
    :return: None
    """
    nlf = open(name_list_file, 'r')
    name_list = []
    for line in nlf.readlines():
        name_list.append(line.strip() + suffix)
        name_list.append(line.strip() + 'inv' + suffix)

    for parent, dirnames, filenames in os.walk(src):
        for f in filenames:
            if f in name_list:
                shutil.copyfile(parent + '/' + f, out + '/' + f)


def prepare_data_for_digits():
    # Prepare data for digits
    non_conflict_file = 'E:/video/categorization/motion_profile/crash_type/nonconflict.txt'
    critical_incident_file = 'E:/video/categorization/motion_profile/danger_level/critical-incident.txt'
    near_crash_file = 'E:/video/categorization/motion_profile/danger_level/near-crash.txt'
    crash_file = 'E:/video/categorization/motion_profile/danger_level/crash.txt'
    endwise_file = 'E:/video/categorization/motion_profile/crash_type/endwise.txt'
    src_path = 'E:/video/total_motion_profile/total_inv'
    tmp = 'E:/video/total_motion_profile/tmp'
    out_path = 'E:/video/total_motion_profile/endwise_12s_for_digits/'

    move_files_with_name_list(src_path, tmp, endwise_file, '.jpg')
    move_files_with_name_list(tmp, out_path + '/1', critical_incident_file, '.jpg')
    move_files_with_name_list(tmp, out_path + '/2', near_crash_file, '.jpg')
    move_files_with_name_list(tmp, out_path + '/3', crash_file, '.jpg')
    move_files_with_name_list(src_path, out_path + '/0', non_conflict_file, '.jpg')


def extract_pedestrian_with_xml():
    xml_folder = 'E:/ped_data/xml/0018-00216-xml/CCHN_0018_229730_46_130718_0907_00216_Front/'
    img_folder = 'E:/ped_data/xml/0018-00216-frame/'
    out_folder = 'E:/ped_data/xml/0018-00216-out/'
    for f in os.listdir(xml_folder):
        num = 0
        box_list = travel_xml(xml_folder + f)
        img = cv2.imread(img_folder + f.strip('.xml') + '.jpg')
        for l in box_list:
            patch = img[l[2]:l[4], l[1]:l[3], :]
            cv2.imwrite(out_folder + f + str(num) + '.jpg', patch)
            num += 1


def extract_xml_bbox():
    annotation_path = "D:/course/pattern_recognition/assignment2/Annotations"
    with open("D:/course/pattern_recognition/assignment2/info.txt", 'w') as out:
        for f in os.listdir(annotation_path):
            box_list = travel_xml(os.path.join(annotation_path, f))
            if box_list is None:
                continue
            out.write('images/' + f.strip('.xml') + '.jpg ' + str(len(box_list)))
            for box in box_list:
                out.write(' ' + str(box[1]) + ' ' + str(box[2]) + ' ' + str(box[3]) + ' ' + str(box[4]))
            out.write('\n')

if __name__ == '__main__':
    pass

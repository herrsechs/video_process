# coding=utf-8
import os
import sys
import shutil


def MoveFiles(name_list, src_path, target_path):
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

if __name__ == '__main__':
    # MoveFiles('D:/Research_IMPORTANT/video/output/event.txt',
    #           'D:/Research_IMPORTANT/data/video/unclassified',
    #           'D:/Research_IMPORTANT/video/output/FINAL_TRAIN_DATA1')
    trim_filename('D:/Research_IMPORTANT/video/output/FINAL_TRAIN_DATA1')
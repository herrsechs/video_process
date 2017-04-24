import cv2
import os
import sys
import numpy as np
import shutil

VIDEO_PATH = 'video1.avi'
TOP_H = 510
BOTTOM_H = 568

FWD_L = 140
FWD_R = 350

LAT_L = 400
LAT_R = 600

TIME_L = 700
TIME_R = 910

SPEED_L = 980
SPEED_R = 1220


def extractText(video, path, video_name):
    number = 1
    while(1):
        ret, frame = video.read()
        if ret is True:
            print 'Extract ' + str(number) + 'th frame...'
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = gray[TOP_H:BOTTOM_H, :]
            fwd = gray[:, FWD_L:FWD_R]
            lat = gray[:, LAT_L:LAT_R]
            time_img = gray[:, TIME_L:TIME_R]
            speed = gray[:, SPEED_L:SPEED_R]

            cv2.imwrite(video_name + '/' + video_name +
                        '_fwd_' + str(number) + '.jpg', fwd)
            cv2.imwrite(video_name + '/' + video_name +
                        '_lat_' + str(number) + '.jpg', lat)
            cv2.imwrite(video_name + '/' + video_name +
                        '_time_' + str(number) + '.jpg', time_img)
            cv2.imwrite(video_name + '/' + video_name +
                        '_speed_' + str(number) + '.jpg', speed)
            number = number + 1
        else:
            break
    print 'Done! ' + str(number-1) + " frames have been extracted"


def readFrames(video, path, video_name):
    number = 1
    while(1):
        ret, frame = video.read()
        if ret is True:
            cv2.imwrite(path + '/' + video_name + '_frame_' + 
                        str(number) + '.jpg', frame)
            number = number + 1
        else:
            break
    print 'Done! ' + str(number-1) + " frames have been extracted"


def cropFrames(video, unitsize, path, video_name, trim_video=False, offset=0):
    frame_width = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    frame_height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    frame_center = frame_height / 2 + offset
    if trim_video:
        frame_width = frame_width - 100
    area = [int(frame_center), int(frame_center+unitsize), 0, int(frame_width)]
    number = 1
    if not os.path.exists(path + '/crop' + str(offset)):
        os.mkdir(path + '/crop' + str(offset))

    while(1):
        ret, frame = video.read()
        if ret is True:
            cv2.imwrite(path + '/crop' + str(offset) + '/' + video_name + '_crop_frame_' +
                        str(number) + '.jpg', 
                        frame[area[0]:area[1], area[2]:area[3]])

            number = number + 1
        else:
            break
    print 'Done! ' + str(number-1) + " frames have been extracted"
    return number


def stitchFrames(number, unitsize, step, path, video_name, offset=0):
    if step > unitsize:
        print "Step should be smaller than the unit size"
    im = cv2.imread(path + '/crop' + str(offset) + '/' + video_name + '_crop_frame_1.jpg')
    blank_img = np.zeros((number * step, int(im.shape[1]), 3), np.uint8)
    s1 = 0
    s2 = s1 + step
    for i in range(1, number):
        img = cv2.imread(path + '/crop' + str(offset) + '/' + video_name +
                         '_crop_frame_' + str(number-i) + '.jpg')
        blank_img[s1:s2, :] = img[0:step, :]
#        os.remove(path + '/crop/' + video_name + '_crop_frame_' +
#                  str(number-i) + '.jpg')
        s1 += step
        s2 += step

    if not os.path.exists(path + '/motion' + str(offset)):
        os.mkdir(path + '/motion' + str(offset))

    cv2.imwrite(path + '/motion' + str(offset) + '/' + video_name + '_motion_profile_' +
                str(offset) + '.jpg', blank_img)


# def imgVerticalMean(path):
#     img = cv2.imread(path)
#     gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     img_mean = np.mean(gimg, axis=0)
#     mean_array = img_mean.copy()
#     for i in range(img.shape[0] - 1):
#         mean_array = np.vstack((mean_array, img_mean))
#     cv2.imwrite(path, mean_array)


# def batchComputeVMean(number, path, name_base):
#     for i in range(1, number):
#         img_path = path + '/' + name_base + '_' + str(i) + '.jpg'
#         print img_path
#         imgVerticalMean(img_path)


def makeMotionProfile(path, video_name, offset=0):
    try:
        cap = cv2.VideoCapture(path + '/' + video_name)
    except:
        print 'Error when loading video file'
        return
    unitsize = 20
    number = cropFrames(cap, unitsize, path, video_name.strip('.avi'), trim_video=True, offset=offset)
    stitchFrames(number, unitsize, 10, path, video_name.strip('.avi'), offset=offset)


def batchMakeMotionProfile(path, offset=0):
    for parent, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if '.avi' in filename:
                makeMotionProfile(path, filename, offset)


def walkDir(root):
    for parent, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if 'front' in filename:
                shutil.move(filename, './front/' + filename)
            elif 'rear' in filename:
                shutil.move(filename, './rear/' + filename)


function_maps = {'-r': readFrames, '-c': cropFrames}


def extractFilesName(file_path, output_path, key):
    f = open(output_path, 'w')
    for filename in os.listdir(file_path):
        if key in filename:
            f.write(filename.split('-')[0] + '\n')

    f.close()


def batchResizeImage(path):
    for filename in os.listdir(path):
        if '.jpg' in filename:
            img = cv2.imread(path + '/' + filename)
            resized_image = cv2.resize(img, (256, 256))
            cv2.imwrite(path + '/' + filename, resized_image)


def batchRGB2Gray(path):
    for filename in os.listdir(path):
        if '.jpg' in filename:
            img = cv2.imread(path + '/' + filename)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(path + '/' + filename, gray)


def deleteFiles(path, key):
    for filename in os.listdir(path):
        if key in filename:
            os.remove(path + '/' + filename)


def findMissingLines(path1, path2, output):
    f1 = open(path1, 'r')
    f2 = open(path2, 'r')
    f1_content = []
    f2_content = []

    for line in f1:
        f1_content.append(line.strip('\n'))
    for line in f2:
        f2_content.append(line.split('_')[0])

    missing = []
    for line in f1_content:
        if line not in f2_content:
            missing.append(line + '\n')

    out = open(output, 'w')
    out.writelines(missing)
    out.close()
    f2.close()
    f1.close()


def extractBeforeImg(src, target):
    for filename in os.listdir(src):
        if '.jpg' in filename:
            img = cv2.imread(src + '/' + filename)
            img = img[0:240, :]
            cv2.imwrite(target + '/' + filename, img)


def extractAfterImg(src, target):
    for filename in os.listdir(src):
        if '.jpg' in filename:
            img = cv2.imread(src + '/' + filename)
            img = img[-160:, :]
            cv2.imwrite(target + '/' + filename, img)


def main():
    action = sys.argv[1]
    video_path = sys.argv[2]
    video_name = video_path.split('/')[-1].split('.')[0]

    if len(sys.argv) > 3:
        target_path = sys.argv[3]
    else:
        target_path = video_name
        if not os.path.exists(target_path):
            os.mkdir(target_path)

    try:
        cap = cv2.VideoCapture(video_path)
    except:
        print 'Error when loading video file'
        return

    if action in function_maps:
        function_maps[action](cap, target_path, video_name)
    else:
        print 'Bad command! ' + action + ' is not defined!'


if __name__ == '__main__':
    # batchMakeMotionProfile('D:/Research_IMPORTANT/video/output/feedback', offset=150)
    # extractFilesName('D:/Research_IMPORTANT/video/output/feedback/motion50',
    #                  'D:/Research_IMPORTANT/video/output/feedback/filenames50.txt')
    # batchResizeImage('D:/Research_IMPORTANT/video/output/train')
    # deleteFiles('D:/Research_IMPORTANT/video/output/feedback', 'rear')
    # findMissingLines('D:/Research_IMPORTANT/video/output/filename1.txt',
    #                  'D:/Research_IMPORTANT/video/output/filenames0.txt',
    #                  'D:/Research_IMPORTANT/video/output/missing.txt')
    # batchRGB2Gray('D:/Research_IMPORTANT/video/output/gray_test')
    # batchRGB2Gray('D:/Research_IMPORTANT/video/output/gray_train')
    # extractBeforeImg('D:/Research_IMPORTANT/video/output/feedback/motion50',
    #                 'D:/Research_IMPORTANT/video/output/beforeimg')
    extractFilesName('D:/Research_IMPORTANT/video/output/FINAL_TRAIN_DATA',
                     'D:/Research_IMPORTANT/video/output/FINAL_TRAIN_DATA/event.txt',
                     '-')

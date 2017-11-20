import cv2
import os
import sys
import numpy as np
import shutil
import re


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

horizon = {
    '003': 141,
    '011': 200,
    '025': 273,
    '035': 110,
    '059': 126,
    '116': 267,
    '118': 142,
    '157': 170,
    '171': 186,
    '190': 165,
    '209': 172,
    '212': 171,
    '227': 179,
    '235': 164,
    '255': 181,
    '266': 177,
    '292': 141,
    '309': 184,
    '323': 182,
    '507': 140,
    '515': 132,
    '552': 134,
    '558': 173,
    '561': 180,
    '581': 138,
    '863': 182,
    '990': 184,
    '992': 120
}


def extract_text(video, video_name):
    number = 1
    while 1:
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
    if not os.path.exists(path):
        os.mkdir(path)

    number = 0
    while(1):
        ret, frame = video.read()
        if ret is True:
            cv2.imwrite(path + '/' + video_name + '_frame_' + 
                        str(number) + '.jpg', frame)
            number = number + 1
        else:
            break
    print 'Done! ' + str(number-1) + " frames have been extracted"


def crop_frames(video_path, out_path, start_y=0, end_y=0, video_name='video'):
    """
        Crop frames between startY and endY
        Return the number of cropped frames
    :param video_path:
    :param out_path:
    :param start_y:
    :param end_y:
    :param video_name:
    :return:
    """
    video = cv2.VideoCapture(video_path)
    frame_width = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    frame_height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    if start_y == 0 and end_y == 0:
        end_y = frame_height
    area = [int(start_y), int(end_y), 0, int(frame_width)]
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    number = 1
    while 1:
        ret, frame = video.read()
        if ret is True:
            cv2.imwrite(out_path + '/' + video_name + '_crop_frame_' +
                        str(number) + '.jpg',
                        frame[area[0]:area[1], area[2]:area[3]])

            number = number + 1
        else:
            break

    video.release()
    print 'Done! ' + str(number - 1) + " frames have been extracted"
    return number


def cropFrames(video, unitsize, path, video_name, trim_video=False, offset=0):
    """
    
    :param video: VideoCapture of the video file being processed
    :param unitsize: 
    :param path: 
    :param video_name: 
    :param trim_video: 
    :param offset: 
    :return: 
    """
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


def stitch_mean_frames(number, src_path, out_path, video_name, dist):
    """
    Compute mean image of each cropped frame in a video, 
    and stitch them together.
    Return the path of the stitched image.
    :param number: 
    :param src_path: 
    :param out_path: 
    :param video_name: 
    :param dist: near, mid or far
    :return: 
    """
    im = cv2.imread(src_path + '/' + video_name + '_crop_frame_1.jpg')
    blank_img = np.zeros((number, int(im.shape[1]), 3), np.uint8)
    for i in range(1, number):
        img = cv2.imread(src_path + '/' + video_name + '_crop_frame_' + str(i) + '.jpg')
        blank_img[i - 1, :, 0] = np.mean(img[:, :, 0], axis=0)
        blank_img[i - 1, :, 1] = np.mean(img[:, :, 1], axis=0)
        blank_img[i - 1, :, 2] = np.mean(img[:, :, 2], axis=0)

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    output = out_path + '/' + video_name + '_' + dist + '.jpg'
    cv2.imwrite(output, blank_img)
    return output


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


def extract_files_name(file_path, output_path, key):
    f = open(output_path, 'w')
    for filename in os.listdir(file_path):
        if key in filename:
            env_num = filename.split('.')[0]
            f.write(env_num + '\n')
    f.close()



def batch_resize_image_same_ratio(path, ratio):
    """
    Resize images to make them in a same height/width ratio
    :param path: 
    :param ratio: width/height 
    :return: 
    """
    for filename in os.listdir(path):
        if '.jpg' in filename:
            img = cv2.imread(path + '/' + filename)
            height = img.shape[0]
            width = int(height * ratio)
            resized_image = cv2.resize(img, (width, height))
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
        f2_content.append(line.strip('\n'))

    missing = []
    number = 0
    for line in f1_content:
        if line not in f2_content:
            number += 1
            missing.append(line + '\n')

    print 'Missing: %i' % number
    out = open(output, 'w')
    out.writelines(missing)
    out.close()
    f2.close()
    f1.close()


def extract_before_img(src, target):
    for filename in os.listdir(src):
        if '.jpg' in filename:
            img = cv2.imread(src + '/' + filename)
            img = img[0:36, :]
            cv2.imwrite(target + '/' + filename, img)


def extractAfterImg(src, target):
    for filename in os.listdir(src):
        if '.jpg' in filename:
            img = cv2.imread(src + '/' + filename)
            img = img[-160:, :]
            cv2.imwrite(target + '/' + filename, img)


def blur_image(src):
    img = cv2.imread(src)
    res = cv2.medianBlur(img, 21)
    cv2.imwrite(src, res)


def batch_blur_image(root):
    for filename in os.listdir(root):
        if '.jpg' in filename:
            blur_image(root + '/' + filename)


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


def merge_motion(near, mid, far, output):
    """
    Merge near, mid, far motion profile into one.
    Convert them into gray image, and make color inversion.
    Put near image into red channel, mid into blue channel, far into green channel.
    :param near: 
    :param mid: 
    :param far: 
    :param output: 
    :return: 
    """
    near_img = cv2.imread(near, 0)
    mid_img = cv2.imread(mid, 0)
    far_img = cv2.imread(far, 0)

    inv_near_img = 255 - near_img
    inv_mid_img = 255 - mid_img
    inv_far_img = 255 - far_img

    merge_img = cv2.merge([inv_near_img, inv_mid_img, inv_far_img])
    cv2.imwrite(output, merge_img)


def get_merge_motion(video_path, output_path, video_name, horizon_h):
    """
    Get merge motion from a video.
    :param video_path: 
    :param output_path: 
    :return: 
    """
    v = cv2.VideoCapture(video_path)
    h = v.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    v.release()
    pos = [horizon_h, int(0.2*(h-horizon_h) + horizon_h), int(0.5*(h-horizon_h) + horizon_h), h]

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    crop_near_frames_path = output_path + '/near'
    crop_mid_frames_path = output_path + '/mid'
    crop_far_frames_path = output_path + '/far'

    near_number = crop_frames(video_path, crop_near_frames_path, pos[2], pos[3], video_name)
    mid_number = crop_frames(video_path, crop_mid_frames_path, pos[1], pos[2], video_name)
    far_number = crop_frames(video_path, crop_far_frames_path, pos[0], pos[1], video_name)

    near_img_path = stitch_mean_frames(near_number, crop_near_frames_path, output_path + '/merge_near',
                                       video_name, 'near')
    mid_img_path = stitch_mean_frames(mid_number, crop_mid_frames_path, output_path + '/merge_mid',
                                      video_name, 'mid')
    far_img_path = stitch_mean_frames(far_number, crop_far_frames_path, output_path + '/merge_far',
                                      video_name, 'far')

    if not os.path.exists(output_path + '/merge/'):
        os.mkdir(output_path + '/merge/')
    merge_motion(near_img_path, mid_img_path, far_img_path, output_path + '/merge/' +
                 video_name + '.jpg')


def batch_get_merge_motion_by_car_id(src_path, output_path):
    """
    Get the merge motion of all the videos under src path
    :param src_path: 
    :param output_path: 
    :return: 
    """
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for file_name in os.listdir(src_path):
        car_id = file_name.split('Event')[0][-3:]
        if car_id not in horizon:
            print 'Invalid car id: %s' % car_id
            continue
        get_merge_motion(src_path + '/' + file_name, output_path, file_name, horizon[car_id])


def batch_get_merge_motion_by_horizon_txt(src_path, output_path, horizon_path):
    """
    Example:
    batch_get_merge_motion_by_horizon_txt('E:/video/total_videos/', 'E:/video/total_motion_profile/',
                                          'E:/video/group_total_videos/horizon.txt')
    :param src_path: src folder which contains videos
    :param output_path: output folder for merge motion images
    :param horizon_path: path to horizon txt
    :return: None
    """
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    horizon_map = {}
    horizon_f = open(horizon_path, 'r')
    for line in horizon_f.readlines():
        evn = line.split(' ')[0]
        h = line.split(' ')[1].strip('\n')
        horizon_map[evn] = h

    for file_name in os.listdir(src_path):
        # if 'Event' not in file_name:
        #     print '%s has no event number' % file_name
        #     continue
        # evn = file_name.split('.')[0].split('Event')[1]
        p = r'[0-9]+'
        pattern = re.compile(p)
        evn = pattern.findall(file_name)[0]
        if evn not in horizon_map:
            print '%s is not in horizon map' % evn
            continue
        get_merge_motion(src_path + '/' + file_name, output_path, evn, int(horizon_map[evn]))


def stitch_near_mid_far_motion(near_path, mid_path, far_path, out_path):
    for file_name in os.listdir(near_path):
        near_img = cv2.imread(near_path + '/' + file_name)
        mid_img = cv2.imread(mid_path + '/' + file_name)
        far_img = cv2.imread(far_path + '/' + file_name)
        if mid_img is None or far_img is None:
            print '%s is invalid' % file_name

        blank_img = np.zeros((int(near_img.shape[0] + mid_img.shape[0] + far_img.shape[0]), int(near_img.shape[1]), 3),
                             np.uint8)
        h1 = int(near_img.shape[0])
        h2 = int(mid_img.shape[0])
        blank_img[0:h1, :, :] = near_img
        blank_img[h1:(h1 + h2), :, :] = mid_img
        blank_img[(h1 + h2):, :, :] = far_img
        cv2.imwrite(out_path + '/' + file_name, blank_img)


def trim_evn_file_name(path, out_path):
    for file_name in os.listdir(path):
        # if 'Event' not in file_name:
        #     print '%s has no event number' % file_name
        #     continue
        # evn = file_name.split('.')[0].split('Event')[1]
        p = r'[0-9]+'
        pattern = re.compile(p)
        evn = pattern.findall(file_name)[0]
        if not os.path.exists(out_path + '/' + evn + '.jpg'):
            os.rename(path + '/' + file_name, out_path + '/' + evn + '.jpg')


def add_file_name_suffix(path, sfx):
    for file_name in os.listdir(path):
        name = file_name.split('.')[0]
        os.rename(path + '/' + file_name, path + '/' + name + sfx + '.jpg')


def inverse_image(src, out):
    """
    Take inverse images under src folder
    Example:
    inverse_image('E:/video/motion_profile_data/all', 'E:/video/motion_profile_data/all_inv')
    :param src: source path of images
    :param out: output path
    :return: 
    """
    for file_name in os.listdir(src):
        img = cv2.imread(os.path.join(src, file_name))
        inv_img = 255 - img
        if not os.path.exists(out):
            os.mkdir(out)
        cv2.imwrite(os.path.join(out, file_name.strip('.jpg') + 'inv.jpg'), inv_img)


def merge_motion_from_far_mid_close(close_path, mid_path, far_path, output_path):
    for file_name in os.listdir(close_path):
        p = r'[0-9]+'
        pattern = re.compile(p)
        evn = pattern.findall(file_name)[0]
        merge_motion(near=close_path + '/' + file_name,
                     mid=mid_path + '/' + evn + '_mid.jpg',
                     far=far_path + '/' + evn + '_far.jpg',
                     output=output_path + '/' + evn + '.jpg')



def generate_label_file(src_path, out, label=0):
    """
    
    :param src_path: the source path of the data  
    :param out: path of the output label file
    :return: 
    """
    out_f = open(out, 'w')
    for parents, dirnames, filenames in os.walk(src_path):
        for f in filenames:
            if '.jpg' not in f:
                continue
            out_f.write(f + ' ' + str(label) + '\n')


def crop_image(src, out, width1=None, height1=None, width2=None, height2=None):
    img = cv2.imread(src)
    if width1 is None:
        width1 = 0
    if height1 is None:
        height1 = 0
    if width2 is None:
        width2 = img.shape[1]
    if height2 is None:
        height2 = img.shape[0]
    crop_img = img[height1:height2, width1:width2]
    cv2.imwrite(out, crop_img)


if __name__ == '__main__':
    inverse_image('E:/video/total_motion_profile/total', 'E:/video/total_motion_profile/total_inv')

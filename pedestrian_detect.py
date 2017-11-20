import os
import cv2
from FileToolBox import travel_xml


def crop_pedestrian_with_xml(xml_path, img_path, out_path, same_ratio=False):
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for file_name in os.listdir(xml_path):
        box_list = travel_xml(xml_path + '/' + file_name)
        names = file_name.split('.')[0]
        names = names.split('MOV')
        img_name = names[0] + '_frame_' + names[1] + '.jpg'
        img = cv2.imread(img_path + '/' + img_name)

        i = 0
        for box in box_list:
            xmin, ymin, xmax, ymax = box[1:5]
            if same_ratio:
                x_center = xmin + 0.5 * (xmax - xmin)
                width = ymax - ymin
                xmin = int(x_center - 0.35 * width)
                xmax = int(x_center + 0.35 * width)
                xmin = xmin if xmin > 0 else 1
                xmax = xmax if xmax < img.shape[1] else img.shape[1] - 1

            pimg = img[ymin:ymax, xmin:xmax]
            cv2.imwrite(out_path + '/' + names[0] + names[1] + str(i) + '.jpg', pimg)
            i += 1


def crop_ped_background(xml_path, img_path, out_path):
    """

    :param xml_path: 
    :param img_path: 
    :param out_path: 
    :return: 
    """
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for file_name in os.listdir(xml_path):
        box_list = travel_xml(xml_path + '/' + file_name)
        img = cv2.imread(os.path.join(img_path, file_name.strip('.xml') + '.jpg'))
        if len(box_list) == 0:
            continue
        i = 0
        box = box_list[0]
        ped_xmin, ymin, ped_xmax, ymax = box[1:5]
        width = ymax - ymin
        xmin = 1
        xmax = int(xmin + 0.7 * width)
        while 1:
            if xmax >= img.shape[1]:
                break
            elif ped_box_check(xmin, xmax, box_list):
                xmin += int(0.7 * width)
                xmax += int(0.7 * width)
                continue

            bg_img = img[ymin:ymax, xmin:xmax]
            cv2.imwrite(os.path.join(out_path, file_name + str(i) + '.jpg'), bg_img)
            i += 1
            xmin += int(0.7 * width)
            xmax += int(0.7 * width)


def ped_box_check(xmin, xmax, box_list):
    """
    Check if cross with the pedestrian box when cropping background 
    :param xmin: bg x1
    :param xmax: bg x2
    :param box_list: list of pedestrian box 
    :return: True: crossed
              False: Not crossed
    """
    for b in box_list:
        ped_xmin, ped_xmax = b[1], b[3]
        if ped_xmin < xmin < ped_xmax or ped_xmin < xmax < ped_xmax:
            return True
    return False


def parse_box_list(box_list_str):
    """
    Parse box list string into list object
    :param box_list_str: 
    :return: [list] coordinates of prediction box
    """
    box_list_str = box_list_str[2:len(box_list_str)-2]
    if len(box_list_str) == 0:
        return []
    box = []
    box_str = ''
    print box_list_str
    begin_add = False
    for i in box_list_str:
        if i == '[':
            begin_add = True
            continue
        elif i == ']':
            b_list = map(lambda a: int(a), box_str.split(','))
            box.append(b_list)
            box_str = ''
            begin_add = False
            continue

        if begin_add:
            box_str += i

    return box


def add_box(frame_path, file_path, out_path):
    """
    Add rectangle to pedestrian in video frame according to prediction result.
    :param frame_path: path of video frames 
    :param file_path: path of box list files
    :param out_path: path of images with box on pedestrian
    :return: 
    """
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    box_list_dict = dict()
    box_list_file = open(file_path, 'r')
    for line in box_list_file.readlines():
        if len(line) < 1:
            continue
        frame_name, box_list = line.split('.jpg')
        frame_number = int(frame_name.split('.mp4')[1])
        for i in range(frame_number, frame_number+10):
            box_list_dict[str(i) + '.jpg'] = parse_box_list(box_list)

    for f in os.listdir(frame_path):
        if f in box_list_dict:
            b_list = box_list_dict[f]

            img = cv2.imread(frame_path + '/' + f)
            if len(b_list) != 0:
                for box in b_list:
                    cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (128, 255, 128), 2)
            cv2.imwrite(out_path + '/' + f, img)


def write_video(frame_path, out_path):
    out = cv2.VideoWriter(out_path, cv2.cv.FOURCC('x', 'v', 'i', 'd'), 14, (480, 356))
    result = os.listdir(frame_path)

    for f in sorted(result, key=lambda x: int(x.strip('.jpg').split('_')[-1])):
        frame = cv2.imread(frame_path + '/' + f)
        out.write(frame)


if __name__ == '__main__':
    box_file_folder = 'E:/ped_data/xml/box'
    frame_path = 'E:/ped_data/xml/frame_with_box'
    # for f in os.listdir(box_file_folder):
    #     add_box('E:/ped_data/frames/ge00060',
    #             os.path.join(box_file_folder, f),
    #             frame_path)
    write_video(frame_path, 'E:/ped_data/box_video/test.avi')

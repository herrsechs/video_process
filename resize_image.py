import cv2
import os


def multi_resize(img_folder, level, resizes):
    """
    Resize images with several new sizes
    :param img_folder: path of images to be processed 
    :param level: integer list, divide images into several groups based on size
                   (in descend order)
                   number of level should be one less than resizes
    :param resizes: new sizes of images. list of tuple
    :return: None
    """
    for f in os.listdir(img_folder):
        if '.jpg' in f:
            img = cv2.imread(os.path.join(img_folder, f))
            h = img.shape[0]
            for i in range(len(level)):
                if h > level[i]:
                    res = cv2.resize(img, resizes[i])
                    break
                elif i == len(level) - 1:
                    res = cv2.resize(img, resizes[i+1])
            cv2.imwrite(os.path.join(img_folder, f), res)


if __name__ == '__main__':
    multi_resize('E:/ped_data/xml/0018-00216-out/background', [50, 30], [(50, 100), (25, 50), (15, 30)])

import moviepy.editor as ed
import csv
import os


def get_sub_clip(src, out, time):
    video = ed.VideoFileClip(src)
    start_t = time - 20 if time > 20 else 1
    end_t = time + 10 if time < video.duration - 10 else video.duration
    clip = video.subclip(start_t, end_t)
    result = ed.CompositeVideoClip([clip, ])
    result.write_videofile(out)


def parse_csv(src):
    try:
        csv_f = open(src, 'r')
        f = csv.reader(csv_f)
        time_list = []
        for row in f:
            if row[0] == 'vtti.file_id':
                continue
            t = int(row[1]) / 10
            time_list.append(t)
        return time_list
    except:
        print src + " doesn't exist."
        return []


def extract_clip(video_folder, csv_folder, out_folder):
    for f in os.listdir(video_folder):
        driver_id = f.split('_')[1]
        video_name = f[:-4]
        csv_name = video_name + '.csv'

        out_path = out_folder + '/' + driver_id + '/' + video_name
        if not os.path.exists(out_folder):
            os.mkdir(out_folder)
        if not os.path.exists(out_folder + '/' + driver_id):
            os.mkdir(out_folder + '/' + driver_id)
        if not os.path.exists(out_path):
            os.mkdir(out_path)

        t_list = parse_csv(csv_folder + '/' + driver_id + '/' + csv_name)
        for t in t_list:
            get_sub_clip(video_folder + '/' + f, out_path + '/' + str(t) + '.mp4', t)


if __name__ == '__main__':
    extract_clip('E:/free_driving_data/video', 'E:/free_driving_data/DrivingID',
                 'E:/free_driving_data/clip')
    # get_sub_clip('E:/free_driving_data/CCHN_0007_229729_46_130425_0421_00054_Front.mp4',
    #              'E:/free_driving_data/clip.mp4', 17)
    # parse_csv('E:/free_driving_data/DrivingID/0007/CCHN_0007_229729_46_130425_0421_00054.csv')

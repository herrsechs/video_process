import math
import os


def cross_ratio(a, b, c, d):
    """
    Compute cross ratio of a,b,c,d
    Example:
    cr = cross_ratio([246, 227], [250, 223], [269, 211], [270, 212])
    :param a: a[0] = x, a[1] = y
    :param b: 
    :param c: 
    :param d: 
    :return: 
    """
    ac = math.sqrt((a[0] - c[0])**2 + (a[1] - c[1])**2)
    bd = math.sqrt((b[0] - d[0])**2 + (b[1] - d[1])**2)
    ad = math.sqrt((a[0] - d[0])**2 + (a[1] - d[1])**2)
    bc = math.sqrt((b[0] - c[0])**2 + (b[1] - c[1])**2)
    if ad == 0 or bc == 0:
        return 0

    return ac * bd / (ad * bc)


def parse_coordinate(src, out_path):
    """
    Parse coordinate file and get the coordinate of A,B,C,D
    Source file template:
    Time  Cord_A    Cord_B    Cord_C    Cord_D   Duration Distance
    3    (365,177) (371,183) (364,177) (369,185) 1        0.8
    Example:
    evn = '7754'
    parse_coordinate('E:/car_speed_reconstruction/success/' + evn + '/' + evn + '.txt',
                     'E:/car_speed_reconstruction/success/' + evn + '/speed.txt')
    :param src: 
    :return: 
    """
    f = open(src, 'r')
    out = open(out_path, 'w')
    for line in f.readlines():
        line = line.strip('\n')
        words = line.split(' ')
        t = words[0]
        cords = []
        for w in words[1:5]:
            w = w.strip('(')
            w = w.strip(')')
            ws = w.split(',')
            cords.append([int(ws[0]), int(ws[1])])
        durt = float(words[5])
        dist = float(words[6])
        sign = 0
        if words[7] == '-':
            sign = -1
        elif words[7] == '+':
            sign = 1
        cr = cross_ratio(cords[0], cords[1], cords[2], cords[3])
        if cr < 1.1:
            data = str(t) + ' ' + '0'
            print data
            out.write(data + '\n')
            continue
        else:
            data = str(t) + ' ' + str(math.sqrt(cr/(cr-1)) * dist * sign / durt)
            print data
            out.write(data + '\n')


def real_speed_calc(evn, fv_file, sv_file, out_path):
    """
    Calculate real speed according to subjective vehicle speed
    :param evn
    :param fv_file: relative speed file of front vehicle
    :param sv_file: 
    :param out_path: 
    :return: 
    """
    fv_f = open(fv_file, 'r')
    sv_f = open(sv_file, 'r')
    out = open(out_path, 'w')
    related_speed_dict = dict()
    for line in fv_f.readlines():
        lines = line.split(' ')
        if len(lines) < 1:
            continue
        related_speed_dict[lines[0]] = lines[1]

    t = 0
    data = evn + '\t'
    spd_data = evn + '\t'
    for line in sv_f.readlines():
        sv_speed = float(line)/3.6
        if str(t) in related_speed_dict:
            spd = sv_speed + float(related_speed_dict[str(t)])
            if spd < 0:
                data += str(sv_speed) + '\t'
            else:
                data += str(spd) + '\t'
        else:
            data += str(sv_speed) + '\t'
        spd_data += str(sv_speed) + '\t'
        t += 1
    # print data
    print spd_data


def travel_folder(fv_folder, sv_folder, out_path):
    for sub_f in os.listdir(fv_folder):
        if 'xlsx' in sub_f:
            continue
        evn = sub_f.split('_')[0]
        sv_f = os.path.join(sv_folder, 'Event' + evn + '.dce.txt')
        fv_f = os.path.join(fv_folder, sub_f, 'speed.txt')
        real_speed_calc(evn, fv_f, sv_f, out_path)


if __name__ == '__main__':
    travel_folder('E:/car_speed_reconstruction/success',
                  'E:/video/kinematic/speed',
                  'E:/car_speed_reconstruction/out.txt')
    # evn = '4822'
    # parse_coordinate('E:/car_speed_reconstruction/success/' + evn + '_front1/' + evn + '.txt',
    #                  'E:/car_speed_reconstruction/success/' + evn + '_front1/speed.txt')

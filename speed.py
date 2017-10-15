import math


def cross_ratio(a, b, c, d):
    """
    Compute cross ratio of a,b,c,d
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


def parse_coordinate(src):
    """
    Parse coordinate file and get the coordinate of A,B,C,D
    Source file template:
    Time  Cord_A    Cord_B    Cord_C    Cord_D   Duration Distance
    3    (365,177) (371,183) (364,177) (369,185) 1        0.8
    :param src: 
    :return: 
    """
    f = open(src, 'r')
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
            print str(t) + ' ' + '0'
            continue
        else:
            print str(t) + ' ' + str(math.sqrt(cr/(cr-1)) * dist * sign / durt)


if __name__ == '__main__':
    parse_coordinate('E:/car_speed_reconstruction/highway/liu/4103_front/4103.txt')
    # cr = cross_ratio([246, 227], [250, 223], [269, 211], [270, 212])
    # print cr
    # l = 2.5
    # if cr > 1:
    #     print math.sqrt(cr/(cr-1)) * l

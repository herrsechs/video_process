if __name__ == '__main__':
    f = open('E:/Qrepdata/data.txt', 'r')
    for line in f:
        lines = line.split(',')
        print lines

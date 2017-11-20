from sklearn.datasets.base import Bunch
from pandas import read_csv
from sklearn import preprocessing, metrics
from sklearn.feature_selection import chi2
from sklearn import svm
import numpy as np
import mord
import matplotlib.pyplot as plt
CSV_PATH = 'E:/video/kinematic/vector.csv'


def trim_file(src, target):
    f = open(src, 'r')
    out = open(target, 'w')
    for line in f.readlines():
        lines = line.split('/')
        out.write(lines[-1])
    f.close()
    out.close()


def classify(pred, thred, target):
    f = open(pred, 'r')
    out = open(target, 'w')
    for line in f.readlines():
        arr = line.split(' ')
        p = float(arr[1].strip('\n'))
        label = 0
        if p < thred[0]:
            label = 0
        elif p < thred[1]:
            label = 1
        else:
            label = 2
        out.write(arr[0] + ' ' + str(label) + '\n')
    out.close()
    f.close()


def calc_accuracy(pred, val):
    f = open(val, 'r')
    val_dict = {}
    for line in f.readlines():
        arr = line.split(' ')
        val_dict[arr[0]] = arr[1].strip('\n')

    pred_f = open(pred, 'r')
    correct = 0
    for line in pred_f.readlines():
        arr = line.split(' ')
        lb = arr[1].strip('\n')
        if arr[0] not in val_dict:
            continue
        val_lb = val_dict[arr[0]]
        if lb == val_lb:
            correct = correct + 1

    accuracy = float(correct) / float(len(val_dict))
    print 'accuracy: ' + str(accuracy)
    f.close()
    pred_f.close()
    return accuracy


def main_search_thred():
    max_accu = 0
    max_thred1 = 0
    max_thred2 = 0
    for thred1 in range(1, 100):
        f_thred1 = float(thred1) / 100.0
        for thred2 in range(thred1, 101):
            f_thred2 = float(thred2) / 100.0
            print 'threshold: ' + str(f_thred1) + ', ' + str(f_thred2)
            classify('D:/Research_IMPORTANT/video/output/trimmed_pred.txt', [f_thred1, f_thred2],
                     'D:/Research_IMPORTANT/video/output/final_pred.txt')
            accu = calc_accuracy('D:/Research_IMPORTANT/video/output/final_pred.txt',
                                 'D:/Research_IMPORTANT/video/labels/3label_val.txt')
            if accu > max_accu:
                max_accu = accu
                max_thred1 = f_thred1
                max_thred2 = f_thred2

    print 'Max accuracy: ' + str(max_accu) + ' threshold: ' + str(max_thred1) + ', ' + str(max_thred2)


def draw_acc_matrix(label, pred, start_idx):
    """
    Print accuracy matrix like this:
    [[ 294.   22.    0.    0.]
     [  25.  156.    0.    0.]
     [   2.   21.    7.    0.]
     [   0.    0.    2.    0.]]
     
    :param label: label array [pandas series]
    :param pred: prediction arrcy [numpy ndarray]
    :param start_idx: start index of test sample
    :return: 
    """
    acc_matrix = np.zeros((4, 4))
    for k, v in label.iteritems():
        num = k - start_idx
        acc_matrix[v, pred[num]] += 1
    print acc_matrix


def order_logit_regression():
    data = read_csv(CSV_PATH)
    bunch = Bunch(data=data.iloc[:, 1:-1], target=data.iloc[:, -1])
    d = bunch.data

    train_len = int(0.75 * d.shape[0])
    trainX, trainY = d.ix[:train_len-1, :], bunch.target[:train_len]
    testX, testY = d.ix[train_len:, :], bunch.target[train_len:]

    clf1 = mord.LogisticAT(alpha=0.5)
    clf1.fit(trainX, trainY)
    pred = clf1.predict(testX)
    draw_acc_matrix(testY, pred, train_len)
    print 'Accuracy of LogisticAT: %s' % metrics.accuracy_score(testY, pred)
    print 'Mean absolute error of LogisticAT: %s' % \
          metrics.mean_absolute_error(pred, testY)

    clf2 = mord.LogisticIT(alpha=0.5)
    clf2.fit(trainX, trainY)
    pred2 = clf2.predict(testX)
    draw_acc_matrix(testY, pred2, train_len)
    print 'Accuracy of LogisticIT: %s' % metrics.accuracy_score(testY, pred2)
    print 'Mean absolute error of LogisticIT: %s' % \
          metrics.mean_absolute_error(pred2, testY)

    clf3 = mord.LogisticSE(alpha=0.5)
    clf3.fit(trainX, trainY)
    pred3 = clf3.predict(testX)
    draw_acc_matrix(testY, pred3, train_len)
    print 'Accuracy of LogisticSE: %s' % metrics.accuracy_score(testY, pred3)
    print 'Mean absolute error of LogisticSE: %s' % \
          metrics.mean_absolute_error(pred3, testY)


def svm_classification():
    data = read_csv(CSV_PATH)
    bunch = Bunch(data=data.iloc[:, 1:-1], target=data.iloc[:, -1])
    d = bunch.data

    train_len = int(0.75 * d.shape[0])
    trainX, trainY = d.ix[:train_len - 1, :], bunch.target[:train_len]
    testX, testY = d.ix[train_len:, :], bunch.target[train_len:]

    clf = svm.SVC(C=0.5, kernel='rbf', gamma=5, decision_function_shape='ovr')
    clf.fit(trainX, trainY)

    pred = clf.predict(testX)
    draw_acc_matrix(testY, pred, train_len)
    print 'Accuracy of SVM: %s' % metrics.accuracy_score(testY, pred)
    print 'Mean absolute error of SVM: %s' % \
           metrics.mean_absolute_error(pred, testY)


def acc_plot():
    d = read_csv(CSV_PATH)

    class3 = d[d.label == 3]
    class2 = d[d.label == 2]
    class1 = d[d.label == 1]
    acc_data3 = class3.loc[:, 'min_acc']
    acc_data2 = class2.loc[:, 'min_acc']
    acc_data1 = class1.loc[:, 'min_acc']
    y3 = acc_data3.ix[:]
    y2 = acc_data2.ix[:]
    y1 = acc_data1.ix[:]
    x1 = np.linspace(0, len(y1)-1, len(y1), dtype=np.int16)
    x2 = np.linspace(len(y1), len(y1) + len(y2) - 1, len(y2), dtype=np.int16)
    x3 = np.linspace(len(x2) + len(x1), len(x1) + len(x2) + len(y3) - 1, len(y3), dtype=np.int16)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, xlim=(0, x3[-1]+10), ylim=(-3, 0.5))
    ax.plot(x1, y1, 'g+', label='critical incident')
    ax.plot(x2, y2, 'b+', label='near crash')
    ax.plot(x3, y3, 'r+', label='crash')
    plt.legend(loc='lower left')
    plt.show()


def acc_plot2():
    d = read_csv(CSV_PATH)
    # d = d[d.label != 0]
    # d = d.sort_values(by='min_acc')
    d = d.loc[:, ['min_acc', 'label']]
    x1, y1, x2, y2, x3, y3, x4, y4 = [], [], [], [], [], [], [], []
    num = 0
    for (k, v) in d.iterrows():
        if int(v['label']) == 0:
            x1.append(num)
            y1.append(v['min_acc'])
        elif int(v['label']) == 1:
            x2.append(num)
            y2.append(v['min_acc'])
        elif int(v['label']) == 2:
            x3.append(num)
            y3.append(v['min_acc'])
        elif int(v['label']) == 3:
            x4.append(num)
            y4.append(v['min_acc'])
        num += 1

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, xlim=(0, 1530), ylim=(-3, 0.5))
    ax.plot(x1, y1, 'go', label='non-conflict')
    ax.plot(x2, y2, 'b.', label='critical incident')
    ax.plot(x3, y3, 'y*', label='near crash')
    ax.plot(x4, y4, 'r+', label='crash')
    plt.legend(loc='lower left')
    plt.show()


if __name__ == '__main__':
    acc_plot2()

from sklearn.datasets.base import Bunch
from pandas import read_csv
from sklearn import preprocessing, metrics
from sklearn.feature_selection import chi2
import mord
CSV_PATH = 'D:/bishe/DataProcessing/data_after.csv'


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

if __name__ == '__main__':
    # trim_file('D:/Research_IMPORTANT/video/output/pred.txt',
    #           'D:/Research_IMPORTANT/video/output/trimmed_pred.txt')
    # features = ('weather', 'illumi', 'speed1', 'speed2', 'speed3', 'speed4', 'speed5', 'speed6',
    #             'fwd1', 'fwd2', 'fwd3', 'fwd4', 'fwd5', 'fwd6', 'fwd7', 'fwd8', 'fwd9', 'fwd10',
    #             'fwd11', 'fwd12', 'fwd13', 'fwd14', 'fwd15', 'fwd16', 'fwd17', 'fwd18''lat', 'road', 'label')

    # d.loc[:, 'weather'] = preprocessing.scale(d.ix[:, 'weather'])
    # d.loc[:, 'illumi'] = preprocessing.scale(d.ix[:, 'illumi'])
    # d.loc[:, 'speed'] = preprocessing.scale(d.ix[:, 'speed'])
    # d.loc[:, 'fwd'] = preprocessing.scale(d.ix[:, 'fwd'])
    # d.loc[:, 'lat'] = preprocessing.scale(d.ix[:, 'lat'])
    # d.loc[:, 'road'] = preprocessing.scale(d.ix[:, 'road'])
    # le = preprocessing.LabelEncoder()
    # le.fit(bunch.target)
    # bunch.target = le.transform(bunch.target)
    #
    # d.loc[d.Infl == 'Low', 'Infl'] = 1
    # d.loc[d.Infl == 'Medium', 'Infl'] = 2
    # d.loc[d.Infl == 'High', 'Infl'] = 3
    #
    # d.loc[d.Cont == 'Low', 'Cont'] = 1
    # d.loc[d.Cont == 'Medium', 'Cont'] = 2
    # d.loc[d.Cont == 'High', 'Cont'] = 3
    #
    # le = preprocessing.LabelEncoder()
    # le.fit(d.loc[:, 'Type'])
    # d.loc[:, 'type_encoded'] = le.transform(d.loc[:, 'Type'])

    data = read_csv(CSV_PATH)
    bunch = Bunch(data=data.iloc[:, 2:-1], target=data.loc[:, 'label'])
    d = bunch.data

    trainX, trainY = d.ix[:599, :], bunch.target[:600]
    testX, testY = d.ix[600:, :], bunch.target[600:]

    clf1 = mord.LogisticAT(alpha=0.8)
    clf1.fit(trainX, trainY)
    pred = clf1.predict(testX)
    print 'Accuracy of LogisticAT: %s' % metrics.accuracy_score(testY, pred)
    print 'Mean absolute error of LogisticAT: %s' % \
          metrics.mean_absolute_error(pred, testY)

    clf2 = mord.LogisticIT(alpha=0.5)
    clf2.fit(trainX, trainY)
    pred2 = clf2.predict(testX)
    print 'Accuracy of LogisticIT: %s' % metrics.accuracy_score(testY, pred2)
    print 'Mean absolute error of LogisticIT: %s' % \
          metrics.mean_absolute_error(pred2, testY)

    clf3 = mord.LogisticSE(alpha=0.5)
    clf3.fit(trainX, trainY)
    pred3 = clf3.predict(testX)
    print 'Accuracy of LogisticSE: %s' % metrics.accuracy_score(testY, pred3)
    print 'Mean absolute error of LogisticSE: %s' % \
          metrics.mean_absolute_error(pred3, testY)


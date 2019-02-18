from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn import cluster
import matplotlib.pyplot as plt
import numpy as np
import xlrd, xlwt


def sigmoid(x):
    # 直接返回sigmoid函数
    return 1. / (1. + np.exp (-x))


def tanh(x):
    # 调用tanh函数
    return (np.exp (x) - np.exp (-x)) / (np.exp (x) + np.exp (-x))


def plot_sigmoid():
    # 读取数据
    a = []
    b = []
    data = []
    euro = []
    wb = xlrd.open_workbook (r'C:/Users/SOD/Desktop/test2.xlsx')
    sheet = wb.sheet_by_index (1)
    nrows = sheet.nrows
    for i in range (1, nrows):
        day = sheet.cell (i, 2).value
        price = sheet.cell (i, 3).value
        data.append (day)
        euro.append (price)
    # 计算sigmoid/Tanh函数值并排序
    data = np.array (data) / 90
    for x in data:
        #        y = sigmoid (x)
        y = tanh (x)
        #        print(x,y)
        a.append (x)
        b.append (y)
    #    print (sorted (a))
    #    print (sorted (b))
    return euro, b, a


# 计算加权平均值
def findWeightMean():
    num = plot_sigmoid ()
    weightmean = np.average (num[0], weights=num[1])
    return weightmean


# 计算有价数据
def findDataSet():
    dataSet = []
    dataMet = plot_sigmoid ()[0]
    weightMean = findWeightMean ()
    for i in dataMet:
        if i < weightMean:
            dataSet.append (i)
        else:
            dataSet = dataSet
#    print ("计算出有价数据集为：", dataSet)
    return dataSet


# 调用K-Means算法对有价数据进行分类
def K_Means():
    dataSet = np.array (findDataSet ())
    data = dataSet.reshape ((len (dataSet), 1))
    # 聚类为3类型
    estimator = KMeans (n_clusters=3)
    res = estimator.fit_predict (data)
    # 预测类别标签结果
    lable_pred = estimator.labels_
    # 各个类别的聚类中心值
    centroids = (estimator.cluster_centers_).T
    # 计算最优推荐节点
    sort_centroids = sorted (centroids)
    best_centroids = (sort_centroids[0] + sort_centroids[1]) / 2
    second_centroids = (sort_centroids[1] + sort_centroids[2]) / 2
    last_centroids = (sort_centroids[2] + findWeightMean ()) / 2

    print ("加权均值为：", findWeightMean())
    print ("预测的标签结果为：", lable_pred)
    print ("预测的中心质点为：", centroids)
    print ("最优推荐节点为：", best_centroids)
    print ("次优推荐节点为：", second_centroids)
    print ("最后推荐节点为：", last_centroids)


if __name__ == '__main__':
    plt.plot (sorted (plot_sigmoid ()[2]), sorted (plot_sigmoid ()[1]))
    plt.show ()
    K_Means ()
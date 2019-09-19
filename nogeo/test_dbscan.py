#-*- coding:utf-8 -*-
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#数据集：每三个是一组分别是西瓜的编号，密度，含糖量
data = """
1,0.697,0.46,2,0.774,0.376,3,0.634,0.264,4,0.608,0.318,5,0.556,0.215,
6,0.403,0.237,7,0.481,0.149,8,0.437,0.211,9,0.666,0.091,10,0.243,0.267,
11,0.245,0.057,12,0.343,0.099,13,0.639,0.161,14,0.657,0.198,15,0.36,0.37,
16,0.593,0.042,17,0.719,0.103,18,0.359,0.188,19,0.339,0.241,20,0.282,0.257,
21,0.748,0.232,22,0.714,0.346,23,0.483,0.312,24,0.478,0.437,25,0.525,0.369,
26,0.751,0.489,27,0.532,0.472,28,0.473,0.376,29,0.725,0.445,30,0.446,0.459"""

#数据处理 dataset是30个样本（序号，密度，含糖量）的列表
a = data.replace('\n','').split(',')
dataset = [[float(a[i+1]),float(a[i+2])] for i in range(0, len(a)-2, 3)]
dataset=pd.DataFrame(dataset,columns=['x','y'])
# 加一个权重，代表栅格内的采样点数
dataset['weight']=2

#计算欧几里得距离,a,b分别为两个元组
def dist(a, b):
    return math.sqrt((a[1]-b[1])**2 + (a[2]-b[2])**2)

#原型算法
def DBSCAN(dataset, e, Minpts):
    D = [(i,dataset.iloc[i,0],dataset.iloc[i,1]) for i in range(0, dataset.shape[0])]
    #1,初始化：核心对象集合T,聚类簇数k,聚类集合C, 未聚类集合P,
    T = set(); k = 0; C = []; P = set(D)
    for d in D:
        if len([ i for i in D if dist(d, i) <= e]) >= Minpts:
            T.add(d)
    #2,当T集合中存在样本时执行：每次取出一个核心对象生成一个簇
    while len(T):
        #保存当前未聚类集合
        P_old = P
        #从T中随机选一个核心对象o，作为种子
        o = list(T)[np.random.randint(0, len(T))]
        #初始化一个队列Q：由密度可达而不断扩张
        Q = []; Q.append(o)
        #从P中删除o 
        P = P - set(o)
        #3，当Q中存在样本时执行：每次取出队首，生成一个新的密度可达域,扩展Q
        while len(Q):
            #取出队首样本q 
            q = Q[0]
            Q.remove(q)
            #如果q为核心对象，则扩展Q
            Nq = [i for i in D if dist(q, i) <= e]
            if len(Nq) >= Minpts:
                #S为q拓展的新的密度直达域（不包括q本身）
                S = P & set(Nq)
                #扩展Q
                Q += (list(S))
                #更新未聚类集合
                P = P - S

        k += 1
        #生成第k个簇
        Ck = list(P_old - P)
        #更新核心对象：减去本次生成簇Ck里的核心对象
        T = T - set(Ck)
        C.append(Ck)

    #边界点集合：set(C)-T
    #噪声点集合：D-set(C)
    cluster_dict={}
    for cluster in range(0,len(C)):
        for c in C[cluster]:
            cluster_dict[c[0]]=cluster    
    y_pred = [-1 if i not in cluster_dict else cluster_dict[i] for i in range(dataset.shape[0])]
    return y_pred

# 只算核心点的简化算法
def DBSCAN_kuki(dataset, e, Minpts):
    # 先转成tuple类型，便于后面set操作
    D = [(i,dataset.iloc[i,0],dataset.iloc[i,1]) for i in range(0, dataset.shape[0])]
    #1,初始化：核心对象集合T,聚类簇数k,聚类集合C, 未聚类集合P,
    T = set(); k = 0; C = []; P = set(D)
    for d in D:
        if len([ i for i in D if dist(d, i) <= e]) >= Minpts:
            T.add(d)
    #2,当T集合中存在样本时执行：每次取出一个核心对象生成一个簇
    while len(T):
        #保存当前未聚类集合
        P_old = P
        #从T中随机选一个核心对象o，作为种子
        o = list(T)[np.random.randint(0, len(T))]
        #初始化一个队列Q：由密度可达而不断扩张
        Q = []; Q.append(o)
        #从P中删除o 
        P = P - set(o)
        #3，当Q中存在样本时执行：每次取出队首，生成一个新的密度可达域,扩展Q
        while len(Q):
            #取出队首样本q 
            q = Q[0]
            Q.remove(q)
            #如果q为核心对象，则扩展Q
            Nq = [i for i in D if dist(q, i) <= e]
            if len(Nq) >= Minpts:
                #S为q拓展的新的密度直达域（不包括q本身）
                S = P & set(Nq)
                #扩展Q
                Q += (list(S))
                #更新未聚类集合
                P = P - S

        k += 1
        #生成第k个簇
        Ck = list(P_old - P)
        #更新核心对象：减去本次生成簇Ck里的核心对象
        T = T - set(Ck)
        C.append(Ck)

    #边界点集合：set(C)-T
    #噪声点集合：D-set(C)
    cluster_dict={}
    for cluster in range(0,len(C)):
        for c in C[cluster]:
            cluster_dict[c[0]]=cluster    
    y_pred = [-1 if i not in cluster_dict else cluster_dict[i] for i in range(dataset.shape[0])]
    return y_pred

#考虑栅格权重的算法
def DBSCAN_grid(dataset, e, Minpts):
    # 先转成tuple类型，便于后面set操作
    D = [(i,dataset.iloc[i,0],dataset.iloc[i,1],dataset.iloc[i,2]) for i in range(0, dataset.shape[0])]
    #1,初始化：核心对象集合T,聚类簇数k,聚类集合C, 未聚类集合P,
    T = set(); k = 0; C = []; P = set(D)
    for d in D:
        # i[3]为栅格的权重，即栅格内的采样点数
        if sum([i[3] for i in D if dist(d, i) <= e]) >= Minpts:
            T.add(d)
    #2,当T集合中存在样本时执行：每次取出一个核心对象生成一个簇
    while len(T):
        #保存当前未聚类集合
        P_old = P
        #从T中随机选一个核心对象o，作为种子
        o = list(T)[np.random.randint(0, len(T))]
        #初始化一个队列Q：由密度可达而不断扩张
        Q = []; Q.append(o)
        #从P中删除o 
        P = P - set(o)
        #3，当Q中存在样本时执行：每次取出队首，生成一个新的密度可达域,扩展Q
        while len(Q):
            #取出队首样本q 
            q = Q[0]
            Q.remove(q)
            #如果q为核心对象，则扩展Q
            Nq = [i for i in D if dist(q, i) <= e]
            #Nq的栅格点总数
            Nq_sum = sum([i[3] for i in Nq])
            if Nq_sum >= Minpts:
                #S为q拓展的新的密度直达域（不包括q本身）
                S = P & set(Nq)
                #扩展Q
                Q += (list(S))
                #更新未聚类集合
                P = P - S

        k += 1
        #生成第k个簇
        Ck = list(P_old - P)
        #更新核心对象：减去本次生成簇Ck里的核心对象
        T = T - set(Ck)
        C.append(Ck)

    #边界点集合：set(C)-T
    #噪声点集合：D-set(C)
    cluster_dict={}
    for cluster in range(0,len(C)):
        for c in C[cluster]:
            cluster_dict[c[0]]=cluster    
    y_pred = [-1 if i not in cluster_dict else cluster_dict[i] for i in range(dataset.shape[0])]
    return y_pred

#画图
def draw(dataset,y_pred):
    colValue = ['r', 'y', 'g', 'b', 'c', 'k', 'm']
    for i in range(len(y_pred)):
        if y_pred[i]==-1:
            plt.scatter(dataset.iloc[i,0], dataset.iloc[i,1], marker='o', color=colValue[y_pred[i]%len(colValue)])
        else:
            plt.scatter(dataset.iloc[i,0], dataset.iloc[i,1], marker='x', color=colValue[y_pred[i]%len(colValue)])

    plt.legend(loc='upper right')
    plt.show()
    

y1 = DBSCAN(dataset, 0.11, 6)
y2 = DBSCAN_kuki(dataset, 0.11, 6)
y3 = DBSCAN_grid(dataset, 0.08, 6)
draw(dataset,y1)
draw(dataset,y2)
draw(dataset,y3)
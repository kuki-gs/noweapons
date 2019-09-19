#-*- coding:utf-8 -*-
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN


#计算欧几里得距离的平方,a,b分别为两个元组
def dist2(a, b):
    #return math.sqrt(math.pow(a[1]-b[1], 2)+math.pow(a[2]-b[2], 2))
    return math.pow(a[1]-b[1], 2) + math.pow(a[2]-b[2], 2)


'''
只包括核心点的简化算法
输入：含经纬度的df类型
输出：列表，cluster编号
'''
def DBSCAN_kuki(dataset, e, Minpts):
    # 先转成tuple类型，便于后面set操作
    D = [(i,dataset.iloc[i,0],dataset.iloc[i,1]) for i in range(0, dataset.shape[0])]
    #1,初始化：核心对象集合T,聚类簇数k,聚类集合C, 未聚类集合P,
    T = set(); k = 0; C = []; P = set(D)
    for d in D:
        if len([ i for i in D if dist2(d, i) <= e**2]) >= Minpts:
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
            Nq = [i for i in D if dist2(q, i) <= e**2]
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

'''
栅格密度聚类算法：只输出核心点的简化算法，每个栅格带有权重
输入：含经纬度、权重的df类型，dataset.iloc[i,0],dataset.iloc[i,1],dataset.iloc[i,2]
输出：列表，cluster编号
'''
def DBSCAN_grid(dataset, e, Minpts):
    # 先转成tuple类型，便于后面set操作
    D = [(i,dataset.iloc[i,0],dataset.iloc[i,1],dataset.iloc[i,2]) for i in range(0, dataset.shape[0])]
    #1,初始化：核心对象集合T,聚类簇数k,聚类集合C, 未聚类集合P,
    T = set(); k = 0; C = []; P = set(D)
    for d in D:
        # i[3]为栅格的权重，即栅格内的点数
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



"""
input:data类型DataFrame, 最起码包含['LONGITUDE', 'LATITUDE']]；TAC为；eps = 0.0005在北纬三十度约等于50米；noise_percent搜参用噪点比例；minPts_stop搜参用
output:pd.DataFrame,聚类成功的点，噪音被过滤掉
"""
def dbscan_cluster(data, TAC, eps=0.0005, noise_percent=0.87,  minPts_stop=25):
    x = data.loc[:, ['wgs_lon', 'wgs_lat']]
    success = 0
    for minPts in range(1, 300, 1):
        percent = 0
        y_pred = DBSCAN(eps=eps, min_samples=minPts).fit_predict(x)
        #y_pred = DBSCAN_kuki(x, eps, minPts)
        df_y_pred = pd.DataFrame(y_pred)
        count_nosie = df_y_pred[df_y_pred[0] < 0].count()
        percent = count_nosie / (df_y_pred[0].count())

        df_dbscan_result = pd.concat([pd.DataFrame(data.values, columns=data.columns), pd.DataFrame(y_pred, columns=['cluster'])],axis=1)

        if float(percent) > 0.87:  # minpts的参数搜索
            success = 1
            break
        elif (float(percent) > 0.82) & (minPts > minPts_stop):
            success = 1
            break
    if success == 1:
        print(percent[0])
        print("eps=%d,minPts=%d时,噪音点数量=%d" % (eps * 10000, minPts, count_nosie))
        return df_dbscan_result
    else:
        print('无法收敛')
        return None




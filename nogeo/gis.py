# -*- coding: utf-8 -*-
import math
import pandas as pd
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

'''
经纬度转平面直角坐标，米勒投影
输入输出：均为带有经度、纬度或x、y坐标的列表
'''
def GPS_to_XY(gps):
    L = 6381372 * math.pi * 2 # 地球周长  
    W = L # 平面展开后，x轴等于周长  
    H = L / 2 # y轴约等于周长一半  
    mill = 0.65 # 米勒投影中的一个常数，范围大约在正负2.3之间  
    x = gps[0] * math.pi / 180 # 将经度从度数转换为弧度  
    y = gps[1] * math.pi / 180 # 将纬度从度数转换为弧度  
    y = 1.25 * math.log(math.tan(0.25 * math.pi + 0.4 * y),10) # 米勒投影的转换  
    # 弧度转为实际距离  
    #x = (W / 2) + (W / (2 * math.pi)) * x
    x = (W / (2 * math.pi)) * x
    #y = (H / 2) - (H / (2 * mill)) * y
    y = (H / (2 * mill)) * y
    return [int(x),int(y)]


'''
经纬度转平面直角坐标，Mercator投影
输入输出：均为带有经度、纬度或x、y坐标的列表
参数说明：
X：水平直角坐标，单位为米(m);
Y：纵向直角坐标，单位为米(m);
B：纬度，单位为弧度(rad);
L：经度，单位为弧度(rad);
Bo：投影基准纬度，Bo =0，单位为弧度((rad);
Lo：坐标原点的经度，Lo =0，单位为弧度(rad);
a：地球椭球体长半轴，a=6378137.0000，单位为米(m);
b：地球椭球体短半轴，b=6356752.3142，单位为米(m);
e：第一偏心率；
e’：第二偏心率。
N-卯酉圈曲率半径，单位为米（m）=a**2/b / math.sqrt(1+e2**2 * math.cos(B0)**2)。
K=N(B0)*math.cos(B0)
'''


def GPS_to_XY2(gps):
    B0 =0
    L0 =0
    a=6378137.000
    b=6356752.314
    e1=math.sqrt(a**2-b**2)/a
    e2=math.sqrt(a**2-b**2)/b
    K=a**2/b*math.cos(B0)/math.sqrt(1 + e2**2 * math.cos(B0)**2)
    
    B=gps[1]*math.pi/180
    L=gps[0]*math.pi/180
    x=K*(L-L0)
    y=K*math.log(math.tan(math.pi/4+B/2) * math.pow((1-e1*math.sin(B))/(1+e1*math.sin(B)),e1/2))
    return [int(x),int(y)]

'''
GCJ2WGS:GCJ经纬度转换成GWS格式的经纬度
输入输出：均为带有经度、纬度的列表
'''
def gcj2gws(location):
# location格式如下：locations[1] = "113.923745,22.530824"
    lon = float(location[0])
    lat = float(location[1])
    a = 6378245.0 # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323 #克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324 # 圆周率
# 以下为转换公式
    x = lon - 105.0
    y = lat - 35.0
# 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x));
    dLon += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0;
    dLon += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0;
    dLon += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0;
#纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x));
    dLat += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0;
    dLat += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0;
    dLat += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0;
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI);
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI);
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return [wgsLon,wgsLat]

'''
转换df类型经纬度
输入：类型dataframe，包含字段LONGITUDE和LATITUDE
输出：在输入基础上增加2列wgs_lon和wgs_lat
'''
def gcj2wgs_for_df(data_with_gcj):

    list_gcj = data_with_gcj[['LONGITUDE','LATITUDE']].values.tolist()
    list_wgs = list(map(gcj2gws,list_gcj))     
    data_with_gcj=pd.concat([data_with_gcj.reset_index(level=0).drop(['index'],axis=1),pd.DataFrame(list_wgs,columns=["wgs_lon","wgs_lat"])],axis=1)    
    return  data_with_gcj


"""
生成tac为单位的kml文件
输入：data类型df，包含字段wgs_lon、wgs_lat、ECI、RSRP、SINR以及TAC、tac_cluster；district_name区县名字, path_result保存路径
输出：kml节点，包含采样点集合的cluser的图层节点
"""
def gen_kml_tac(data, district_name, path_result):
    # 创建谷歌图层文件
    list_tac = sorted(data['跟踪区'].astype(int).drop_duplicates().tolist())
    for tac in list_tac:
        df_tac_data = data[data['跟踪区'] == tac]
        list_cluster = sorted(df_tac_data['tac_cluster'].drop_duplicates().tolist())
        for cluster in list_cluster: 
            df_cluster_data = df_tac_data[df_tac_data['tac_cluster'] == cluster]
            # 如果是tac中的第一个cluster，则创建一个tac文件夹，并添加第一个cluster节点
            if cluster == list_cluster[0]:
                kml_tac = KML.Folder(KML.name("跟踪区=" + str(tac)),
                                      gen_kml_cluster(df_cluster_data, cluster))  
            # 添加后面的cluster
            else:
                kml_tac.append(gen_kml_cluster(df_cluster_data, cluster))
        
        # 如果是第一个tac，创建kml文件，并添加第一个tac节点
        if tac == list_tac[0]:
            kml_doc= KML.Document(KML.name(district_name), kml_tac)
        else:
            kml_doc.append(kml_tac)

    etree_doc = etree.tostring(etree.ElementTree(kml_doc), pretty_print=True)
    # 
    with open(path_result + district_name + '.kml', 'wb') as fp:
        fp.write(etree_doc)    

"""
生成一个包含采样点集合的cluser的kml图层节点
pykml是在python2下写的，在导入以后，有些地方可能会出错，所以需要修改pykml，主要是一些print格式有问题
输入：类型df，包含字段wgs_lon、wgs_lat、ECI、RSRP、SINR
输出：kml节点，包含采样点集合的cluser的图层节点
"""

def gen_kml_cluster(data,cluster_name):

    lon=data['wgs_lon']
    lat=data['wgs_lat']

    if len(lon)!=len(lat):
        print ('lon != lat nums，请检查数据的经纬度信息')
        sys.exit(0)
    # 创文件夹，添加第一个点
    kml_cluster=KML.Folder(KML.name(str(cluster_name)),
                        KML.styleUrl("#m_ylw-pushpin"),
                        KML.Placemark(KML.styleUrl("#m_ylw-pushpin"),
                                     KML.description('ECI:'+str(int(data["ECI"].iloc[0])),
                                                     'SINR:'+str(round(data["SINR"].iloc[0],1)),
                                                     'RSRP:'+str(round(data["RSRP"].iloc[0],1))),
                                     KML.Point(KML.styleUrl("#m_ylw-pushpin"),
                                               KML.coordinates(str(lon.iloc[0])+','+str(lat.iloc[0])+',0'))))
    # 添加后面的采样点
    for i in range(1,len(lon)):
        kml_cluster.append(KML.Placemark(KML.description('ECI:'+str(int(data["ECI"].iloc[i])),
                                                      'SINR:'+str(round(data["SINR"].iloc[i], 1)),
                                                      'RSRP:'+str(round(data["RSRP"].iloc[i], 1))),
                                      KML.Point(KML.coordinates(str(lon.iloc[i])+','+str(lat.iloc[i])+',0'))))
        #        print etree.tostring(etree.ElementTree(kml_file ),pretty_print=True)
    return kml_cluster

def gen_kml_enb(data_wgs,level=3):#level1=tac，level2=enb,level3=cell,如果data_wgs数据已经包含，所以gongcan_l表就不需要了
    data_wgs = data_wgs[['p_day', 'CELL_RSRP', 'CELL_SINR', 'CELL_CELLID', 'eNBID', '区县', '频段', '站型', '方位角', 'wgs_lon',
                         'wgs_lat']]
    data_wgs["ECI"] = data_wgs["CELL_CELLID"]

    # print(data_wgs.head())
#     data_wgs=pd.merge(data_wgs,gongcan_l[['ECI','eNBID','跟踪区']],left_on='CELL_CELLID',right_on="ECI",how="left")
    data_wgs.dropna(inplace=True)

    cell_list=data_wgs.CELL_CELLID.astype(int).drop_duplicates()#用于获得这些小区的共站同方向小区，然后再取其覆盖采样点生成google地图文件
    cell_list=cell_list.to_list()

    ENB_list=data_wgs.eNBID.astype(int).drop_duplicates().to_list()
    # import os
    # filename = os.path.basename(file_csv)
    for i,ENB in enumerate(ENB_list):
        ENB_data=data_wgs[data_wgs['eNBID']==ENB]
        classify_list=ENB_data['CELL_CELLID'].drop_duplicates().to_list()
#         classify_list=sorted(list(classify_list))

        for j,clas in enumerate(classify_list):#这里按照ENB输出点，所以用ENB——list替代了cell_list
            point_data=ENB_data[ENB_data['CELL_CELLID']==clas]
            if j==0:#clas==classify_list[0]:
                cell_kml=KML.Folder(KML.name("ENB:"+str(ENB)),
                                     gen_kml_point(point_data,clas))#加个document根目录，append的时候避免树结构错乱
            else:
                cell_kml.append(gen_kml_point(point_data,clas))
        if i==0:
            ENB_kml=KML.Folder(KML.name('_反向覆盖小区采样点'+str(ENB)),cell_kml)
        else:
            ENB_kml.append(cell_kml)
    return ENB_kml
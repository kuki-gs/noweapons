# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from nogeo import gen_kml_tac,dbscan_cluster
from dataPreprocess.dataPreprocess import data_preprocess
import folium
from folium import plugins

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.serif'] = ['SimHei']

'''
计算目标tac的质差聚类
输入：input_tacs目标tac,df_samples采样点,plot_open=False画图开启
输出：result在df_samples基础上增加tac_cluster簇编号，过滤噪点
'''
def calc_cluster(input_tacs,df_samples,plot_open=False):
    # 调用聚类函数,按照tac聚类
    result = pd.DataFrame()    
    for tac in input_tacs:  
        if tac not in df_samples['跟踪区'].values:
            print("当前TCA=%d" % (tac), "源数据中查无选择的tac")
        else:
            print("当前TCA=%d" % (tac))
            data = df_samples[df_samples['跟踪区'] == float(tac)]
            print (data.info())
            print("当前TAC的数据的数量：", data.shape)
            
            # 聚类
            y = dbscan_cluster(data, tac, eps=0.0005)
            # 过滤掉噪点
            y = y[y["cluster"] >= 0]  
        
            # 画图
            if plot_open==True:
                plt.rcParams['figure.figsize'] = (8.0, 4.0)
                plt.scatter(data["wgs_lon"], data["wgs_lat"], marker='.', s=4, c="b")
                plt.scatter(y['wgs_lon'], y['wgs_lat'], marker='o', s=6, c="R")
            
                plt.title("TAC=%d" % tac)
                plt.show()            
            
            result = result.append(y, ignore_index=True)
            print("输出数据的数量：", result.shape, "\n\t", result.head())
    
    # cluster编号
    result["tac_cluster"] = result["跟踪区"].astype(int).astype(str) + "_" + result["cluster"].astype(str)
    result = result[['RSRP', 'SINR', 'ECI', '跟踪区', '区县', 'samples_of_tac',
                     'wgs_lon', 'wgs_lat', 'tac_cluster']]    
    return result

def calc_cluster_web(input_tacs,df_samples):
    # 调用聚类函数,按照tac聚类
    tac=input_tacs[0]
    if tac not in df_samples['跟踪区'].values:
        print("当前TCA=%d" % (tac), "源数据中查无选择的tac")
        return None
    else:
        print("当前TCA=%d" % (tac))
        data = df_samples[df_samples['跟踪区'] == float(tac)]
        print (data.info())
        print("当前TAC的数据的数量：", data.shape)
        
        # 聚类
        y = dbscan_cluster(data, tac, eps=0.0005)
        # 过滤掉噪点
        y = y[y["cluster"] >= 0]  
        y.reset_index(inplace=True)
        # to web
        map_nb = folium.Map(location=y.loc[0,['wgs_lat','wgs_lon']].tolist(),zoom_start=10,
                             tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                             attr='&copy; <a href="http://ditu.amap.com/">高德地图</a>')    

            
        #marker_cluster_data = plugins.MarkerCluster().add_to(map_nb)
        marker_cluster_y = plugins.MarkerCluster().add_to(map_nb)
        #for name,row in data.iterrows(): 
            #folium.Marker([row["wgs_lat"], row["wgs_lon"]],color='blue').add_to(map_nb) #逐行读取经纬度，数值，并且打点
        for name,row in y.iterrows(): 
            folium.Marker([row["wgs_lat"], row["wgs_lon"]],color='red').add_to(map_nb) #逐行读取经纬度，数值，                并且打点
        
        
        #map_nb.save(path_result+'cluster_{}.html'.format(tac))                  
    
        return map_nb

if __name__ == '__main__':
    '''
    输入：目标tac
    '''
    input_district='余姚'
    input_tacs=[22344]       
    '''
    '''
    path_data_shouting = "./dataset/shouting_nb_05.csv"
    path_data_migu = "./dataset/migu_nb_05.csv"
    path_data_gongcan = './dataset/工参_yy.xlsx'
    path_result = "./dataset/result/"
 
    
    #调用数据处理函数
    df_samples,df_gongcan = data_preprocess(path_data_shouting, path_data_migu, path_data_gongcan)
    
    df_gongcan = df_gongcan[df_gongcan['跟踪区'].isin(input_tacs)]
    # 电平过滤
    df_samples = df_samples[(df_samples['SINR'] < 3) & (df_samples['RSRP'] < -95)]
    # 合并
    df_samples = pd.merge(df_samples, df_gongcan[['ECI' ,'ENB' ,'跟踪区','区县']], how='left', on=['ECI']).dropna(axis=0)
    # 统计tac的采样点数量，如果某个tac的数据量太少则从数据中过滤掉
    df_tac_count = df_samples['跟踪区'].value_counts()
    df_tac_count = df_tac_count.reset_index()
    df_tac_count.columns = ['跟踪区', 'samples_of_tac']
    df_samples = pd.merge(df_samples, df_tac_count, how='left', on=['跟踪区'])
    df_samples = df_samples[df_samples['samples_of_tac'] > 200]
    
    result = calc_cluster(input_tacs,df_samples,True)
    # 聚类结果输出
    result.to_csv(path_result + input_district + "_"  + '聚类.csv', encoding="gbk", index=False)
    # 生成图层文件
    gen_kml_tac(result, input_district, path_result)

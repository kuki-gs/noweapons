# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nogeo import get_convexhull,is_point_inside_polygon,plotPoints,showPoints,plotPolygons,showPolygons,plotTriangles
from dataPreprocess.dataPreprocess import data_preprocess,find_sites_around_sameband,find_cells_sametac
from scipy.spatial import Delaunay
from flask import Flask,request,render_template
import folium
from folium import plugins
from DemoOverCoverage import calc_over_coverage_web
from DemoCluster import calc_cluster_web
from DemoOverlapping import calc_overlapping_web
from flask_socketio import SocketIO

# The choice to use threading is intentional to simplify deployment.
# At the moment it is not recommended to build full-duplex systems inside CTFd.
socketio = SocketIO()
app = Flask(__name__,static_url_path='/static/',template_folder='templates')


def overcover(eci=103014145):

    '''
    输入：目标基站
    '''
    #input_cells = [103014145]
    input_cells=[eci]
    '''
    '''
    
    path_data_shouting = "./dataset/shouting_nb_05.csv"
    path_data_migu = "./dataset/migu_nb_05.csv"
    path_data_gongcan = './dataset/工参_yy.xlsx'
    path_result = "./dataset/result/"


    #调用数据处理函数
    df_samples,df_gongcan = data_preprocess(path_data_shouting, path_data_migu, path_data_gongcan)
    df_worse_cell = df_gongcan[df_gongcan["ECI"].isin(input_cells)]#只取部分F1频点的站展示
    
    #调用最近邻区查找函数，使用德罗内三角形的方法
    df_worse_cell = find_sites_around_sameband(df_worse_cell, df_gongcan, plot_open=False)#绘制hight_load_cell的前5个小区的enb对应的邻站图，可参考输文件
    #df_worse_cell.to_csv(path_result+"最近邻站.csv",encoding="gbk")
    
    #df_worse_cell = df_worse_cell[df_worse_cell["sites_around"] != ""]
    df_worse_cell = df_worse_cell.reset_index()
    # df_worse_cell[['ECI' ,'ENB' ,'经度', '纬度', '频段' ,'方位角', 'sites_around']]
    
    map_nb = calc_over_coverage_web(df_worse_cell,df_gongcan,df_samples)
    #df_worse_cell.to_csv(path_result+"过覆盖率.csv",encoding="gbk")    
    #print(map_nb._repr_html_())
    
    return map_nb._repr_html_()


def cluster(tac=22344):

    '''
    输入：目标tac
    '''
    input_district='余姚'
    #input_tacs=[22344]     
    input_tacs=[tac]
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
    
    map_nb = calc_cluster_web(input_tacs,df_samples)

    return map_nb._repr_html_()

def overlapping(eci=103014149):
    '''
    输入：目标基站
    '''
    #input_cells = [103014149]
    input_cells = [eci]
    path_data_shouting = "./dataset/shouting_nb_05.csv"
    path_data_migu = "./dataset/migu_nb_05.csv"
    path_data_gongcan = './dataset/工参_yy.xlsx'
    path_result = "./dataset/result/"

    
    #调用数据处理函数
    df_samples,df_gongcan = data_preprocess(path_data_shouting, path_data_migu, path_data_gongcan)
    
    df_worse_cell = df_gongcan[df_gongcan["ECI"].isin(input_cells)]#只取部分F1频点的站展示
    # 对采样点根据电平过滤一下['p_day', 'wgs_lon', 'wgs_lat', 'MNET_TYPE', 'RSRP', 'SINR', 'ECI'] 
    df_samples = df_samples[df_samples['RSRP'].astype(float) >= -95]
    #调用最近邻区查找函数，使用德罗内三角形的方法，异频
    #df_worse_cell = find_cells_around(df_worse_cell, df_gongcan)
    # 同tac距离较近小区
    df_worse_cell = find_cells_sametac(df_worse_cell,df_gongcan,distance=0.005)
    #df_worse_cell.to_csv(path_result+"最近邻站.csv",encoding="gbk")
    
    df_worse_cell = df_worse_cell.reset_index()
    # df_worse_cell[['ECI' ,'ENB' ,'经度', '纬度', '频段' ,'类型','方位角', 'sites_around']]

    map_nb = calc_overlapping_web(df_worse_cell,df_gongcan,df_samples)    
    return map_nb._repr_html_()

@app.route('/', methods=['GET','POST'])
def index():
    func = request.args.get('func')
    if request.args.get('tac') != None:
        tac = int(request.args.get('tac'))
    if request.args.get('eci') != None:
        eci = int(request.args.get('eci'))
    if func == "cluster":
        map_nb=cluster(tac)
    elif func == "overcover":
        map_nb=overcover(eci)
    elif func == "overlapping":
        map_nb=overlapping(eci)
    else:
        map_nb = folium.Map(location=[31,121],zoom_start=10,
                             tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                             attr='&copy; <a href="http://ditu.amap.com/">高德地图</a>')._repr_html_()   
    return render_template('index.html',map_nb=map_nb)
    
        
if __name__ == '__main__':

    app.run(debug=True, threaded=True,host="127.0.0.1", port=55555)
    #socketio.run(app, debug=True, host="127.0.0.1", port=55555)
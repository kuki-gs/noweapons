# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nogeo import get_convexhull,is_point_inside_polygon,plotPoints,showPoints,plotPolygons,showPolygons,plotTriangles
from dataPreprocess.dataPreprocess import data_preprocess,find_sites_around_sameband
from scipy.spatial import Delaunay
import folium
from folium import plugins

'''
计算质差小区的过覆盖率，采用三角剖分算法
输入：df_worse_cell质差小区清单,df_gongcan工参表,df_samples采样点,plot_open=False画图开启
输出：df_worse_cell质差小区清单增加字段over_coverage
'''
def calc_over_coverage(df_worse_cell,df_gongcan,df_samples,plot_open=False):
    df_worse_cell['over_coverage'] = ''
    for cell_index in range(df_worse_cell.shape[0]):
        if df_worse_cell['sites_around'].iloc[cell_index] != '':
            eci = df_worse_cell['ECI'].iloc[cell_index]
            enb = df_worse_cell['ENB'].iloc[cell_index]
            # 取出周边站点，关联工参
            sites_around = df_worse_cell['sites_around'].iloc[cell_index]
            sites_gongcan = df_gongcan[df_gongcan['ENB'].isin(sites_around)]
            sites_gongcan = sites_gongcan[['ENB', '经度', '纬度', '频段']]
            sites_gongcan = sites_gongcan.drop_duplicates(subset=['ENB'],keep='first')
            # 周边站点凸包，顶点逆时针排序
            ch = get_convexhull(sites_gongcan[["经度", "纬度"]].astype(float).values.tolist()) 
            # 计算过覆盖率
            def is_inside(p):
                return is_point_inside_polygon(p,ch)
            samples = df_samples[df_samples["ECI"]==eci]
            list_samples = samples[['wgs_lon','wgs_lat']].values.tolist()
            over_cover = list(map(is_inside,list_samples))
            df_worse_cell.loc[cell_index,'over_coverage'] = 1-sum(over_cover)/len(over_cover)
            '''
            if plot_open==True:
                # 画图        
                location = df_worse_cell.loc[cell_index,['经度','纬度']].tolist()
                plotPoints(location,style='ro')
                plotPolygons(ch,style='k--')
                plt.scatter(samples["wgs_lon"], samples["wgs_lat"], marker='.', s=4, c="b")
                plt.title("The main cell is:%d"%eci)
                plt.show() 
            '''
   
            if plot_open==True:
                location_m = df_worse_cell.loc[cell_index,['经度','纬度']].tolist()
                points = ch.points + [location_m]
                points = np.array(points)
                tri = Delaunay(points) 
                plotTriangles(points, tri.simplices)
                plt.scatter(samples["wgs_lon"], samples["wgs_lat"], marker='.', s=4, c="b")
                plotPoints(location_m,style='ro')
                plt.title("The main cell is:%d"%eci)
                plt.show()                    
                
    return df_worse_cell

def calc_over_coverage_web(df_worse_cell,df_gongcan,df_samples):
    cell_index=0
    # to web
    location_m = df_worse_cell.loc[cell_index,['经度','纬度']].tolist()
    map_nb = folium.Map(location=[location_m[1],location_m[0]],zoom_start=10,
                         tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                         attr='&copy; <a href="http://ditu.amap.com/">高德地图</a>')    
    marker_m = folium.Marker(
        location=[location_m[1],location_m[0]],
        icon=folium.Icon(color='red', icon='info-sign')
    )
    marker_m.add_to(map_nb)     
    if df_worse_cell['sites_around'].iloc[cell_index] != '':
        eci = df_worse_cell['ECI'].iloc[cell_index]
        enb = df_worse_cell['ENB'].iloc[cell_index]
        # 取出周边站点，关联工参
        sites_around = df_worse_cell['sites_around'].iloc[cell_index]
        sites_gongcan = df_gongcan[df_gongcan['ENB'].isin(sites_around)]
        sites_gongcan = sites_gongcan[['ENB', '经度', '纬度', '频段']]
        sites_gongcan = sites_gongcan.drop_duplicates(subset=['ENB'],keep='first')
        # 周边站点凸包，顶点逆时针排序
        ch = get_convexhull(sites_gongcan[["经度", "纬度"]].astype(float).values.tolist()) 
        # 计算过覆盖率
        def is_inside(p):
            return is_point_inside_polygon(p,ch)
        samples = df_samples[df_samples["ECI"]==eci]
        list_samples = samples[['wgs_lon','wgs_lat']].values.tolist()
        over_cover = list(map(is_inside,list_samples))

        poly_m=[[i[1],i[0]] for i in ch.points]
        poly_m = poly_m + [poly_m[0]]
    
        ls = folium.PolyLine(locations=poly_m,
                            color='red')
        ls.add_to(map_nb)    
        
        marker_cluster = plugins.MarkerCluster().add_to(map_nb)
        for name,row in samples.iterrows(): 
            folium.Marker([row["wgs_lat"], row["wgs_lon"]]).add_to(map_nb) #逐行读取经纬度，数值，并且打点
    #map_nb.save(path_result+'overcover_{}.html'.format(eci))       
    return map_nb
    

"""
计算质差小区的过覆盖率，采用三角剖分算法
"""
#导入数据
if __name__== '__main__':
    
    '''
    输入：目标基站
    '''
    input_cells = [103014145]
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

    df_worse_cell = calc_over_coverage(df_worse_cell,df_gongcan,df_samples,plot_open=True)
    df_worse_cell.to_csv(path_result+"过覆盖率.csv",encoding="gbk")
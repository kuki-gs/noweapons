# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nogeo import get_convexhull,get_convexhull_cross,convex_polygon_area,plotPoints,showPoints,plotPolygons,showPolygons
from dataPreprocess.dataPreprocess import data_preprocess,find_cells_around,find_cells_sametac
import folium
from folium import plugins
'''
计算邻区对于主小区的共覆盖度，其中邻区根据三角剖分寻找
输入：df_worse_cell质差小区清单,df_gongcan工参表,df_samples采样点,plot_open=False画图开启
输出：result字段['ECI_M','ECI_N','AREA_M','共覆盖度']
'''
def calc_overlapping(df_worse_cell,df_gongcan,df_samples,plot_open=True):
    result = pd.DataFrame(columns=['ECI_M','BAND_M','ECI_N','BAND_N','CH_M','CH_N','CH_CROSS','AREA_M','共覆盖度'])
    for cell_index in range(df_worse_cell.shape[0]):    
        eci_m = df_worse_cell['ECI'].iloc[cell_index]
        if df_worse_cell['cells_around'].iloc[cell_index] != '':
            #['p_day', 'wgs_lon', 'wgs_lat', 'MNET_TYPE', 'CELL_RSRP', 'CELL_SINR', 'CELL_CELLID']
            samples_m = df_samples[df_samples["ECI"]==eci_m]
            if samples_m.shape[0]<3:
                result=result.append({'ECI_M':eci_m,'BAND_M':None,'ECI_N':None,'BAND_N':None,'CH_M':None,'CH_N':None,'CH_CROSS':None,'AREA_M':None,'共覆盖度':None},ignore_index=True)
                continue
            else:                
                ch_m = get_convexhull(samples_m[["wgs_lon", "wgs_lat"]].astype(float).values.tolist()) 
                area_m = convex_polygon_area(ch_m)
                # 取出周边站点，关联工参
                cells_around = df_worse_cell['cells_around'].iloc[cell_index]
                cells_gongcan = df_gongcan[df_gongcan['ECI'].isin(cells_around)]
                cells_gongcan = cells_gongcan[['ECI','ENB', '经度', '纬度', '频段']]
                cells_gongcan = cells_gongcan.drop_duplicates(subset=['ECI'],keep='first')
                cells_gongcan.reset_index(inplace=True)
                for i in range(cells_gongcan.shape[0]):
                    eci_n = cells_gongcan['ECI'].iloc[i]
                    samples_n = df_samples[df_samples["ECI"]==eci_n]
                    if samples_n.shape[0]<3:
                        result=result.append({'ECI_M':eci_m,'BAND_M':df_worse_cell['频段'].iloc[cell_index],
                                              'ECI_N':eci_n,'BAND_N':cells_gongcan['频段'].iloc[i],'CH_M':ch_m.points,'CH_N':0,'CH_CROSS':0,
                                              'AREA_M':area_m,'共覆盖度':0},ignore_index=True)
                    else:
                        ch_n = get_convexhull(samples_n[["wgs_lon", "wgs_lat"]].astype(float).values.tolist()) 
                        ch_cross = get_convexhull_cross(ch_m,ch_n)
                        if ch_cross==None:
                            result=result.append({'ECI_M':eci_m,'BAND_M':df_worse_cell['频段'].iloc[cell_index],
                                                  'ECI_N':eci_n,'BAND_N':cells_gongcan['频段'].iloc[i],'CH_M':ch_m.points,'CH_N':ch_n.points,'CH_CROSS':0,
                                                  'AREA_M':area_m,'共覆盖度':0},ignore_index=True)
                        else:
                            area_cross = convex_polygon_area(ch_cross)
                            cross_rate = area_cross/area_m
                            result=result.append({'ECI_M':eci_m,'BAND_M':df_worse_cell['频段'].iloc[cell_index],
                                                  'ECI_N':eci_n,'BAND_N':cells_gongcan['频段'].iloc[i],'CH_M':ch_m.points,'CH_N':ch_n.points,'CH_CROSS':ch_cross.points,
                                                  'AREA_M':area_m,'共覆盖度':cross_rate},ignore_index=True)
                            if plot_open==True:
                                if cross_rate>0.5:
                                    location_n = cells_gongcan.loc[i,['经度','纬度']].tolist()
                                    plotPoints(location_n,style='go')
                                    plotPolygons(ch_n,style='g--')   
                                    plotPolygons(ch_cross,style='b')   
                                
                if plot_open==True:
                    location_m = df_worse_cell.loc[cell_index,['经度','纬度']].tolist()
                    plotPoints(location_m,style='ro')
                    plotPolygons(ch_m,style='r--')     
                    plt.title("The main cell is:%d"%eci_m)
                    plt.show()
        else:
            result=result.append({'ECI_M':eci_m,'BAND_M':0,'ECI_N':0,'BAND_N':0,'CH_M':0,'CH_N':0,'CH_CROSS':0,'AREA_M':0,'共覆盖度':0},ignore_index=True)
    return result

def calc_overlapping_web(df_worse_cell,df_gongcan,df_samples):
    cell_index=0  
    eci_m = df_worse_cell['ECI'].iloc[cell_index]
    # to WEB
    location_m = df_worse_cell.loc[cell_index,['经度','纬度']].tolist()
    map_nb = folium.Map(location=[location_m[1],location_m[0]],zoom_start=10,
                         tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                         attr='&copy; <a href="http://ditu.amap.com/">高德地图</a>')
    marker_m = folium.Marker(
        location=[location_m[1],location_m[0]],
        icon=folium.Icon(color='red', icon='info-sign')
    )
    marker_m.add_to(map_nb)    
    if df_worse_cell['cells_around'].iloc[cell_index] != '':
        samples_m = df_samples[df_samples["ECI"]==eci_m]
        if samples_m.shape[0]<3:
            return None
        else:                
            ch_m = get_convexhull(samples_m[["wgs_lon", "wgs_lat"]].astype(float).values.tolist()) 
            area_m = convex_polygon_area(ch_m)
                     
            poly_m=[[i[1],i[0]] for i in ch_m.points]
            poly_m = poly_m + [poly_m[0]]

            ls_m = folium.PolyLine(locations=poly_m,
                                color='red')
            ls_m.add_to(map_nb)                    
            # 取出周边站点，关联工参
            cells_around = df_worse_cell['cells_around'].iloc[cell_index]
            cells_gongcan = df_gongcan[df_gongcan['ECI'].isin(cells_around)]
            cells_gongcan = cells_gongcan[['ECI','ENB', '经度', '纬度', '频段']]
            cells_gongcan = cells_gongcan.drop_duplicates(subset=['ECI'],keep='first')
            cells_gongcan.reset_index(inplace=True)
            for i in range(cells_gongcan.shape[0]):
                eci_n = cells_gongcan['ECI'].iloc[i]
                samples_n = df_samples[df_samples["ECI"]==eci_n]
                if samples_n.shape[0]<3:
                    continue
                else:
                    ch_n = get_convexhull(samples_n[["wgs_lon", "wgs_lat"]].astype(float).values.tolist()) 
                    ch_cross = get_convexhull_cross(ch_m,ch_n)
                    if ch_cross!=None:

                        area_cross = convex_polygon_area(ch_cross)
                        cross_rate = area_cross/area_m
                        
                        location_n = cells_gongcan.loc[i,['经度','纬度']].tolist()
                        marker_n = folium.Marker(
                            location=[location_n[1],location_n[0]],
                            icon=folium.Icon(color='green', icon='info-sign')
                        )
                        marker_n.add_to(map_nb)                     
                        poly_n=[[i[1],i[0]] for i in ch_n.points]
                        poly_n = poly_n + [poly_n[0]]
        
                        ls_n = folium.PolyLine(locations=poly_n,
                                            color='green')
                        ls_n.add_to(map_nb)  
                        poly_cross=[[i[1],i[0]] for i in ch_cross.points]
                        poly_cross = poly_cross + [poly_cross[0]]
        
                        ls_cross = folium.PolyLine(locations=poly_cross,
                                            color='blue')
                        ls_cross.add_to(map_nb)                                     
                            
            
    return map_nb

"""
主要是输出目标小区的邻站，进而可以输出最近邻小区（可结合方位角和距离计算最近邻区）
"""
#导入数据
if __name__== '__main__':
    '''
    输入：目标基站
    '''
    input_cells = [103014150]
    '''
    '''    
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

    result = calc_overlapping(df_worse_cell,df_gongcan,df_samples,plot_open=True)
    result.to_csv(path_result+"共覆盖率.csv",encoding="gbk")


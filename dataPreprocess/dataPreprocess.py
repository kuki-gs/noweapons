# -*- coding: utf-8 -*-
import math
import pandas as pd
import numpy as np
from nogeo import gcj2wgs_for_df,Delaunay_kuki
from scipy.spatial import Delaunay
'''
输出：
df_samples=['p_day', 'wgs_lon', 'wgs_lat', 'MNET_TYPE', 'RSRP', 'SINR', 'ECI', '经度', '纬度', '数据源']
worse_cell=['ECI' ,'ENB' ,'跟踪区','区县','经度', '纬度', '频段' ,'类型','方位角']
gongcan=['ECI' ,'ENB' ,'跟踪区','区县','经度', '纬度', '频段', '类型','方位角']
'''
def data_preprocess(path_data_shouting="",path_data_migu="",path_data_gongcan=""):
    """
    :param path_data_shouting: 手厅文件路径，csv格式
    :param path_data_migu: 咪咕文件路径，csv格式
    :param path_data_gongcan: 工参路径，xlsx格式
    :return:df_samples，DataFrame格式;hight_load_cell包含[ECI ，ENB ，经度 ，纬度 ，频段 ，方位角]
    """

    # 用户数据读入及处理
    st_data = pd.read_csv(path_data_shouting, encoding="gbk")
    migu_data = pd.read_csv(path_data_migu, encoding="gbk")

    # 手厅数据处理
    st_data = st_data[st_data['MNET_TYPE'] == 'LTE']
    st_data_wgs = gcj2wgs_for_df(st_data)  # 将手厅的经纬度转成wgs格式的
    st_data_wgs = st_data_wgs[['p_day', 'wgs_lon', 'wgs_lat', 'MNET_TYPE', 'CELL_RSRP', 'CELL_SINR', 'CELL_CELLID']]
    st_data_wgs.columns = ['p_day', 'wgs_lon', 'wgs_lat', 'MNET_TYPE', 'RSRP', 'SINR', 'ECI']
    # 咪咕数据处理
    migu_data =migu_data[['p_day', 'longitude', 'latitude', 'network_type', 'cell_signal_strength', 'sinr', 'CELL_CELLID']]
    migu_data.dropna(subset=['longitude', 'latitude', 'cell_signal_strength', 'sinr'], axis=0, inplace=True)

    # 将咪咕和手厅数据合并
    st_data_wgs["数据源"] = "ST"
    migu_data["数据源"] = "Migu"
    migu_data.columns = st_data_wgs.columns
    df_samples = pd.concat([st_data_wgs, migu_data], ignore_index=True, axis=0)
    # 去除异常记录
    df_samples = df_samples[df_samples['ECI'].notnull()]  
    df_samples = df_samples[df_samples['wgs_lon'].notnull()]
    df_samples = df_samples[df_samples['wgs_lat'].notnull()]      


    # 导入工参信息表
    gongcan = pd.read_excel(path_data_gongcan ,sheet_name=0 ,header=0)
    gongcan = gongcan[['ECI' ,'eNBID' ,'跟踪区','区县', '经度', '纬度', '频段', '类型','方位角']]
    gongcan.rename(columns = {'eNBID':'ENB'},inplace = True)
    gongcan = gongcan.dropna(subset=["经度" ,"纬度"])
    gongcan['ENB'] = gongcan['ENB'].astype(int)
    df_samples = pd.merge(df_samples, gongcan[['ECI', '经度', '纬度']], on='ECI', how='inner')
    # 滤除过远采样点
    df_samples["mht_dis"] = (abs((df_samples["wgs_lon"].astype(float) - df_samples["经度"])) +
                           abs((df_samples["wgs_lat"].astype(float) - df_samples["纬度"])))
    std_temp = df_samples.groupby('ECI')['mht_dis'].std().reset_index()
    std_temp.columns = ['ECI', 'mht_std']
    std_temp['mht_std'].fillna(std_temp['mht_std'].mean(), inplace=True)
    df_samples = pd.merge(df_samples, std_temp[['ECI', 'mht_std']], on='ECI', how='left')
    # 数据预处理，3倍标准差过滤
    df_samples = df_samples[df_samples["mht_dis"] <= 3 * df_samples["mht_std"]]  
    df_samples = df_samples.drop(['mht_dis','mht_std'],axis = 1)
    return df_samples,gongcan

"""
查找质差小区的同频周边基站
param: target_cell: 目标小区信息，DataFrame格式，可以包含多个小区的信息
return: 增加字段sites_around目标小区的最近邻站点，同站名的小区除第一个小区外都是空值
"""
def find_sites_around_sameband(target_cells,gongcan,plot_open=False):

    target_cells['sites_around'] = ''
    # 遍历target_cells中的小区
    for cell_index_target in range(0, target_cells.shape[0]):
        Current_ECI = target_cells['ECI'].iloc[cell_index_target]
        Current_ENB = target_cells['ENB'].iloc[cell_index_target]

        # 以当前小区同频基站（去重）为分析对象
        sites_sameband = gongcan[gongcan["频段"] == target_cells['频段'].iloc[cell_index_target]]

        
        sites_sameband = sites_sameband.drop_duplicates(subset=['ENB'],keep='first')
        if sites_sameband.shape[0]==0:
            print('目标小区频段有误')
            target_cells['sites_around'].iloc[cell_index] = ''
            continue
        
        sites_sameband.reset_index(inplace=True)
        #gongcan_sameband.rename(columns={'index': "原序号"}, inplace=True)

        # 对同频基站网络建立德罗内三角网
        
        #tri = Delaunay_kuki(sites_sameband[["经度", "纬度"]].values) 
        tri = Delaunay(sites_sameband[["经度", "纬度"]].values) 
        # 获得以当前基站的所有三角形，其中包括的其他顶点即为最近站点
        df_tri = pd.DataFrame(tri.simplices)  # 三角形顶点list，以索引为标识,这个索引是sites_sameband的索引
        # 获得当前基站在sites_sameband中的索引
        site_index_sameband = sites_sameband[sites_sameband["ENB"] == Current_ENB]
        site_index_sameband = site_index_sameband.index.tolist()[0]
        # 包含当前基站的所有三角形索引
        list_tri_index = df_tri[(df_tri[0] == site_index_sameband) | (df_tri[1] == site_index_sameband) | (df_tri[2] == site_index_sameband)].index.tolist()
        # 取出三角形的顶点，及周边基站索引
        list_site_index_around = np.array(df_tri.iloc[list_tri_index, :]).flatten().tolist()  # 主小区及周边邻区的在表（gc_list）的索引表
        list_site_index_around = list(set(list_site_index_around))
        # 根据索引从sites_sameband中取出ENB
        list_site_around = sites_sameband['ENB'].iloc[list_site_index_around]
        list_site_around = list_site_around.tolist()
        list_site_around.remove(Current_ENB)
        target_cells['sites_around'].iloc[cell_index_target] = list_site_around
        #1.2.3绘制当前小区的三角剖分图
        if plot_open==True:
            print("当前小区是：", Current_ECI)
            m_gc_list = sites_sameband[["经度", "纬度"]].iloc[list_site_index_around].values
            tri_m = Delaunay(m_gc_list)
            center = np.sum(m_gc_list[tri_m.simplices], axis=1) / 3.0
            color = np.array([(x) ** 2 + (y) ** 2 for x, y in center])

            plt.figure()  # figsize=(7, 3))
            plt.tripcolor(m_gc_list[:, 0], m_gc_list[:, 1], tri_m.simplices.copy(), facecolors=color, edgecolors='b')
            # Delete ticks, axis and background
            plt.tick_params(labelbottom='off', labelleft='off', left='off', right='off', bottom='off', top='off')
            ax = plt.gca()
            ax.spines['right'].set_color('none')
            ax.spines['bottom'].set_color('none')
            ax.spines['left'].set_color('none')
            ax.spines['top'].set_color('none')  # Save picture plt.savefig('Delaunay.png', transparent=True, dpi=600)
            plt.show()
        else:
            continue
    return target_cells

"""
查找质差小区的周边小区：需要更新成根据共站信息表去搜索
param: target_cell: 目标小区信息，DataFrame格式，可以包含多个小区的信息
return: 增加字段cells_around
"""
def find_cells_around(target_cells,gongcan):

    target_cells['cells_around'] = ''
    # 遍历target_cells中的小区
    for cell_index_target in range(0, target_cells.shape[0]):
        Current_ECI = target_cells['ECI'].iloc[cell_index_target]
        Current_ENB = target_cells['ENB'].iloc[cell_index_target]

        # 以当前小区同频基站（去重）为分析对象
        sites_share = gongcan[gongcan["频段"] == target_cells['频段'].iloc[cell_index_target]]
      
        sites_share = sites_share.drop_duplicates(subset=['ENB'],keep='first')
        if sites_share.shape[0]==0:
            print('目标小区频段有误')
            target_cells['cells_around'].iloc[cell_index] = ''
            continue
        
        sites_share.reset_index(inplace=True)
        #gongcan_sameband.rename(columns={'index': "原序号"}, inplace=True)

        # 对同频基站网络建立德罗内三角网
        tri = Delaunay(sites_share[["经度", "纬度"]].values) 
        # 获得以当前基站的所有三角形，其中包括的其他顶点即为最近站点
        df_tri = pd.DataFrame(tri.simplices)  # 三角形顶点list，以索引为标识,这个索引是sites_sameband的索引
        # 获得当前基站在sites_sameband中的索引
        site_index = sites_share[sites_share["ENB"] == Current_ENB]
        site_index = site_index.index.tolist()[0]
        # 包含当前基站的所有三角形索引
        list_tri_index = df_tri[(df_tri[0] == site_index) | (df_tri[1] == site_index) | (df_tri[2] == site_index)].index.tolist()
        # 取出三角形的顶点，及周边基站索引
        list_site_index_around = np.array(df_tri.iloc[list_tri_index, :]).flatten().tolist()  # 主小区及周边邻区的在表（gc_list）的索引表
        list_site_index_around = list(set(list_site_index_around))
        # 根据索引从sites_gongcan中取出ENB
        list_site_around = sites_share['ENB'].iloc[list_site_index_around]
        list_site_around = list_site_around.tolist()
        # 从周边基站中关联到小区
        list_cell_around = gongcan[gongcan['ENB'].isin(list_site_around)]
        '''
        if sameband==True:
            list_cell_around = list_cell_around[list_cell_around['频段'] == target_cells['频段'].iloc[cell_index_target]]
        else:
            list_cell_around = list_cell_around[list_cell_around['频段'] != target_cells['频段'].iloc[cell_index_target]]        
        '''

        list_cell_around = list_cell_around['ECI'].values.tolist()
        if Current_ECI in list_cell_around:
            list_cell_around.remove(Current_ECI)
        if len(list_cell_around)>0:
            target_cells['cells_around'].iloc[cell_index_target] = list_cell_around
        else:
            target_cells['cells_around'].iloc[cell_index_target] = ''

    return target_cells

"""
查找质差小区的周边小区：同tac
param: target_cell: 目标小区信息，DataFrame格式，可以包含多个小区的信息
return: 增加字段cells_around
"""
def find_cells_sametac(target_cells,gongcan,distance=0.01):
    target_cells['cells_around'] = ''
    # 遍历target_cells中的小区
    for cell_index_target in range(0, target_cells.shape[0]):
        Current_ECI = target_cells['ECI'].iloc[cell_index_target]
        Current_ENB = target_cells['ENB'].iloc[cell_index_target]
        tac = target_cells['跟踪区'].iloc[cell_index_target]
        
        cells_sametac = gongcan[gongcan['跟踪区']==tac]
        cells_sametac = cells_sametac[cells_sametac['ECI']!=Current_ECI]
        cells_sametac = cells_sametac[['ECI' ,'经度', '纬度']].values.tolist()
        
        m = target_cells[['经度', '纬度']].iloc[cell_index_target].values.tolist()
        def is_near(n):
            dist=math.sqrt((m[0]-n[1])**2 + (m[1]-n[2])**2)
            if dist<distance:
                return True
            else:
                return False
            
        list_cells_sametac = list(filter(is_near, cells_sametac))
        list_cells_sametac = [p[0] for p in list_cells_sametac]
        if len(list_cells_sametac)>0:
            target_cells['cells_around'].iloc[cell_index_target] = list_cells_sametac
        else:
            target_cells['cells_around'].iloc[cell_index_target] = ''
    return target_cells
        
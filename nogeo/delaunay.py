#!/usr/bin/env python
# coding: utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nogeo.shapes import  Polygon
from nogeo.spatial import cross_prod,in_circle,in_triangle,third_vertex_of_tri,tri_contains_v,find_edge



'''
跑的太慢，还是用官方的
'''
class Delaunay_kuki(object):

    #增加三角形：
    def add_tri(self,va,vb,vc):
        self.triangles = np.append(self.triangles,[[va,vb,vc]],axis=0)
    
    #删除三角形：
    def remove_tri(self,va,vb,vc):
        for i in range(len(self.triangles)):
            if tri_contains_v(self.triangles[i],va) and tri_contains_v(self.triangles[i],vb) and tri_contains_v(self.triangles[i],vc):
                self.triangles = np.delete(self.triangles,i,0)        
                break
                 
    #增加边：
    def add_edge(self,vi,vd):
        self.edges = np.append(self.edges,[[vi,vd]],axis=0)    
    
    #删除边：
    def remove_edge(self,va,vb):
        for i in range(len(self.edges)):
            if ((self.edges[i][0]==va).all() and (self.edges[i][1]==vb).all()) or ((self.edges[i][0]==vb).all() and (self.edges[i][1]==va).all()):
                self.edges = np.delete(self.edges,i,0)
                break
    
    #删除三角形：根据顶点
    def remove_tri_by_v(self,vi):
        remove_list=[]
        for i in range(len(self.triangles)):
            if tri_contains_v(self.triangles[i],vi):
                remove_list.append(i)
        self.triangles = np.delete(self.triangles,remove_list,0)
                
    #删除边：根据顶点
    def remove_edge_by_v(self,vi):
        remove_list=[]
        for i in range(len(self.edges)):
            if (self.edges[i][0]==vi).all() or (self.edges[i][1]==vi).all():
                remove_list.append(i)
        self.edges = np.delete(self.edges,remove_list,0)
                
    #找点vi在内部或边上的三角形
    def find_triangle(self, vi):
        for tri in self.triangles:
            res=in_triangle(tri, vi)
            if res>=0:
                return True,tri
        return False,None
    
    #找包含边vavb，且vi在外部的三角形的第3个顶点
    def find_vertex(self, va, vb, vi):
        for tri in self.triangles:
            res,vd = third_vertex_of_tri(tri,va,vb)
            if res and in_triangle(tri, vi)==-1:
                return True,vd
        return False,None    

            
    #四边形对角线测试
    def flip_test(self, va, vb, vi):
        # 找包含边vavb，且vi在外部的三角形的第3个顶点vd
        res,vd = self.find_vertex(va, vb, vi)
        if res:
            # 如果vi在三角形vavbvd内部
            if in_circle(va, vb, vd, vi)<0:
                # 交换四边形vavbvdvi的对角线，断vavb，连vdvi
                self.remove_edge(va,vb)
                self.remove_tri(va,vb,vd)
                self.remove_tri(va, vb, vi)
                self.add_edge(vi,vd)
                self.add_tri(va, vd, vi)
                self.add_tri(vd, vb, vi)
                self.flip_test(va, vd, vi)
                self.flip_test(vd, vb, vi)

    #插入离散点
    def insert_v(self, vi):
        #1.find the triangle vavbvc which contains vi
        res,tri = self.find_triangle(vi)
        res = in_triangle(tri, vi)
        #2.if vi located at the interior of tri(va,vb,vc)
        if res>0: 
            #3.then add triangle vavbvi, vbvcvi and vcvavi into DT
            va=tri[0]
            vb=tri[1]
            vc=tri[2]
            self.add_edge(va,vi)
            self.add_edge(vb,vi)
            self.add_edge(vb,vi)
            self.add_edge(vc,vi)              
            self.add_tri(va,vb,vi)
            self.add_tri(vb,vc,vi)
            self.add_tri(vc,va,vi)
            self.remove_tri(va,vb,vc)
            self.flip_test(va, vb, vi)
            self.flip_test(vb, vc, vi)
            self.flip_test(vc, va, vi)
        #4.else if (vi located at one edge (E.g. edge vavb) of vavbvc) 
        elif res==0: 
            #5.then add triangle vavivc, vivbvc, vavdvi and vivdvb into DT (here, d is the third vertex of triangle which contains edge vavb)   
            #5.1 先找到包含vi的边，设为vavb
            res,i=find_edge(tri,vi)
            #5.2 再找包含边vavb的三角形vavbvd，且该三角形不包含vc
            va=tri[i]
            vb=tri[(i+1)%3]
            vc=tri[(i+2)%3]
            res,vd = self.find_vertex(va,vb,vc)
            #5.3 如果找到三角形vavbvd，新边vcvi和vdvi将三角形vavbvc和vavbvd分成4个新三角形
            if res:
                self.add_edge(vd,vi)
                self.add_edge(vc,vi)                
                self.add_tri(va,vc,vi)
                self.add_tri(vc,vb,vi)
                self.add_tri(vb,vd,vi)
                self.add_tri(vd,va,vi)
                self.remove_tri(va,vb,vc)
                self.remove_tri(va,vb,vd)
                self.flip_test(va,vc,vi)
                self.flip_test(vc,vb,vi)
                self.flip_test(vb,vd,vi)
                self.flip_test(vd,va,vi)
            #5.4 如果没找到三角形vavbvd，边vcvi将三角形vavbvc分成2个新三角形
            else:
                self.add_edge(vc,vi)  
                self.add_tri(va,vc,vi)
                self.add_tri(vc,vb,vi)
                self.remove_tri(va,vb,vc)
                self.flip_test(va,vc,vi)
                self.flip_test(vc,vb,vi)                
    
    def __init__(self, points_list):
        
        if len(points_list) <= 3:
            raise ValueError("Polygon must have at least three vertices.")
        #1,构造一个足够大的三角形abc，可以包围输入点集
        M=np.max(abs(points_list))
        a=np.array([0, 3*M]) 
        b=np.array([-3*M,-3*M]) 
        c=np.array([3*M, 0])
        #2,根据构造的三角形abc初始化三角形矩阵和边矩阵
        self.triangles = np.array([[a,b,c]])
        self.edges = np.array([[a,b],
                               [b,c],
                               [c,a]])
        #3,将点集逐个插入
        for vi in points_list:
            self.insert_v(vi)
            '''
            print('vi=',vi)
            print('triangles=',self.triangles)
            print('edges=',self.edges)     
            '''
        #4,删除初始三角形abc以及相关的边
        self.remove_edge_by_v(a)
        self.remove_edge_by_v(b)
        self.remove_edge_by_v(c)
        self.remove_tri_by_v(a)
        self.remove_tri_by_v(b)
        self.remove_tri_by_v(c) 
        
        self.simplices=np.zeros(self.triangles.shape[0:2])
        for tri_ind in range(len(self.triangles)):
            for v_ind in range(3):
                for p_ind in range(len(points_list)):
                    if (self.triangles[tri_ind,v_ind]==points_list[p_ind]).all():
                        self.simplices[tri_ind,v_ind]=p_ind
        
        self.simplices=self.simplices.astype(np.int32)



# test
'''
if __name__ == '__main__':  
    #points_list = np.random.rand(10,2)
    points_list=np.array([[1,1],[0,-0],[-1,1],[-1,0]])
    de=Delaunay(points_list)
    print('triangles=',de.triangles)
    print('simplices=',de.simplices)
    print('edges=',de.edges)
    
    
    # In[9]:
    
    
    # draw
    
    
    # In[10]:
    
    
    width = 100
    height = 100
    pointNumber = 20
    points = np.zeros((pointNumber, 2))
    points[:, 0] = np.random.randint(0, width, pointNumber)
    points[:, 1] = np.random.randint(0, height, pointNumber)
    
    # Use scipy.spatial.Delaunay for Triangulation，对比
    de=Delaunay(points)
    #de2=sp.Delaunay(points)
    # Plot Delaunay triangle with color filled
    center = np.sum(points[de.simplices.astype(np.int32)], axis=1)/3.0
    color = np.array([(x - width/2)**2 + (y - height/2)**2 for x, y in center])
    plt.figure(figsize=(6, 4))
    plt.tripcolor(points[:, 0], points[:, 1], de.simplices.copy(), facecolors=color, edgecolors='k')
    
    
    # Delete ticks, axis and background
    plt.tick_params(labelbottom='off', labelleft='off', left='off', right='off',
                    bottom='off', top='off')
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['top'].set_color('none')
    
    plt.show()
    # Save picture
    #plt.savefig('Delaunay.png', transparent=True, dpi=600)
    

'''


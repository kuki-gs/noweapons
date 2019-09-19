#!/usr/bin/env python
# coding: utf-8

from nogeo.shapes import Polygon, base_point
from nogeo.spatial import is_point_inside_polygon, get_seg_cross
import math

# 凸包
# input: list of Point  
# output: Polygon in CCW
def get_convexhull(point_list):

    # 逆时针
    def ccw(points):
        return (points[1][0] - points[0][0]) * (points[2][1] - points[0][1]) > (points[1][1] - points[0][1]) * (points[2][0] - points[0][0])

    #point_list = list(map(lambda p:[p.x,p.y], point_list))
    n = len(point_list)  #Total Length
    point_list.sort() 

    #Valid Check:
    if n < 3:
        return None


    upper_hull = point_list[0:1]
    for i in range(2, n):
        upper_hull.append(point_list[i])
        while len(upper_hull) >= 3 and  not ccw(upper_hull[-3:]):
            del upper_hull[-2]


    lower_hull = [point_list[-1], point_list[-2]]
    for i in range(n - 3, -1, -1):  
        lower_hull.append(point_list[i])
        while len(lower_hull) >= 3 and  not ccw(lower_hull[-3:]):
            del lower_hull[-2]

    upper_hull.extend(lower_hull[1:-1])
    if len(upper_hull)<3:
        return None
    else:
        return Polygon(upper_hull)



# 凸包的交集
# input: Polygon
# output: point list
def get_convexhull_cross(polygon_p,polygon_q):
    cross_point=[]
    # 1,互相包含的点
    for point in polygon_p.points:
        if is_point_inside_polygon(point,polygon_q):
            cross_point.append(point)

    for point in polygon_q.points:
        if is_point_inside_polygon(point,polygon_p):
            cross_point.append(point)
    # 2，边的交点
    edge_of_polygon_p = [[polygon_p.points[i],polygon_p.points[(i+1)%polygon_p.n]] for i in range(polygon_p.n)]
    edge_of_polygon_q = [[polygon_q.points[i],polygon_q.points[(i+1)%polygon_q.n]] for i in range(polygon_q.n)]

    for edge_p in edge_of_polygon_p:
        for edge_q in edge_of_polygon_q:
            # print("两个多边形的边是：",edge_p,edge_q)
            cross_on_edge=get_seg_cross(edge_p[0],edge_p[1],edge_q[0],edge_q[1])
            # print("交集的边是：",cross_on_edge)
            cross_point.extend(cross_on_edge)
    # 3，去重
    cross_point=[(i[0],i[1]) for i in cross_point]
    cross_point=list(set(cross_point))   
    cross_point=[[i[0],i[1]] for i in cross_point]
    if len(cross_point)==0:
        return None
    else:
        return get_convexhull(cross_point)


def vector_angle(point, base_poin):
    # 相对于基点的极角
    #    p1=point
    #    p0=base_poin
    # point应该是一个点不是点集
    if (point[0] == base_poin[0]):
        if (point[1] == base_poin[1]):  # 同一个点
            return -1  # 只是做个标记，说明该点是和基点相同，便于排序
        else:
            return math.pi / 2
    #    point[1]-base_poin[1])/(point[0]-base_poin[0])
    else:
        theta = math.atan((point[1] - base_poin[1]) / (point[0] - base_poin[0]))
    if theta > 0:
        return theta
    else:
        return math.pi + theta  # 返回的是弧度


def convex_polygon_area(convex_polygon):
    # convex_polygon是凸多边形见函数def convexHull(point_list)
    points = convex_polygon.points

    # 1.将多边形的顶点按照逆时针排序
    # 1.1获得基点（纵坐标最小，纵坐标相同时，横坐标最小）,经度为横坐标纬度为纵坐标
    #    p=sorted(points,key=(lambda x:x[0]))
    p_base = base_point(points)

    #    points.remove(p_base)
    #    print("未排序的点集是：",points)
    #     #1.2逆时针排序
    p_angle = []

    for i in range(len(points)):
        p_angle.append({"index": i, "angel": vector_angle(points[i], p_base)})
    p_angle.sort(key=lambda x: (x.get('angel')))
    #    print("排序后向量的极角：",p_angle)
    p_out = []
    for i in range(0, len(p_angle)):
        p_out.append(points[p_angle[i]["index"]])
    #    print("排序后的点集是：",p_out)
    # 1.3计算面积
    area = 0.0
    for i in range(len(p_out) - 2):
        #        print("当前第{}个三角形面积".format(i+1))
        p0 = p_out[0]
        p1 = p_out[i + 1]
        p2 = p_out[i + 2]
        #        print (tri_area(p0,p1,p2))
        area += tri_area(p0, p1, p2)
    return area


def tri_area(p0, p1, p2):  # 逆时针
    # p0是基点,采用向量叉积的方法求三角形面积，三角形的定点按照固定的方向。

    vector1 = (p1[0] - p0[0], p1[1] - p0[1])
    vector2 = (p2[0] - p0[0], p2[1] - p0[1])
    #    print("向量1是：",vector1)
    area = (vector1[0] * vector2[1] - vector2[0] * vector1[1]) / 2
    return area
'''
if __name__ == '__main__':       
    polygon_p=Polygon([[0,0],[0,1],[1,1],[1,0]])
    #polygon_q=Polygon([[-0.5,0],[1,1.5],[1,0]])
    polygon_q=Polygon([[-1,0],[0.5,1.5],[0.5,0.5],[0,0]])
    cross=get_convexhull_cross(polygon_p,polygon_q)
    
    
    #凸包后逆时针
    print(cross)
'''

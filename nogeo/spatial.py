#!/usr/bin/env python
# coding: utf-8
import numpy as np
import math


'''
#数据结构说明


#点
point=[x,y]
points=[point,point]

#边
seg=[point,point]
segs=[seg,seg]

#三角形
triangle=[point,point,point]
triangles=[triangle,triangle]

'''

'''
1,点的运算
'''


'''
2，向量运算
'''
# 叉乘的重要性质：右手法则
'''
    若 P × Q > 0 , 则P 在Q的顺时针方向
    若 P × Q < 0 , 则P 在Q的逆时针方向（与性质1等价）
    若 P × Q = 0 , 则P 与Q共线，但可能同向也可能反向
'''
# input：point
# output：标量
def cross_prod(p, q): 
    return p[0]*q[1]-q[0]*p[1]


# 逆时针
# input:points
def is_ccw(A, B, C):
    # AC在AB的逆时针方向
    return cross_prod([C[0]-A[0],C[1]-A[1]], [B[0]-A[0],B[1]-A[1]])<0


# 向量夹角顺时针v1->v2
#v1=[1,2]
#v2=[2,3]
def Angle2D(v1, v2):
    theta1 = math.atan2(v1[1],v1[0])
    theta2 = math.atan2(v2[1],v2[0])
    dtheta = theta2 - theta1
    while dtheta > math.pi:
        dtheta -= math.pi*2
    while dtheta < -math.pi:
        dtheta += math.pi*2

    return dtheta
# 快速排斥试验
# input：points of segment
# output：Ture or False
def is_rect_overlap(p1,p2,q1,q2): 
    return min(p1[0],p2[0]) <= max(q1[0],q2[0]) and min(q1[0],q2[0]) <= max(p1[0],p2[0]) and min(p1[1],p2[1]) <= max(q1[1],q2[1]) and min(q1[1],q2[1]) <= max(p1[1],p2[1])
    
# 点是否在线段上
# 1，点在以线段为对角线的矩形内；2，(P−S1)×(S2−S1)=0
def is_point_on_segment(p,s1,s2):
    return p[0]<=max(s1[0],s2[0]) and p[0]>=min(s1[0],s2[0]) and p[1]<=max(s1[1],s2[1]) and p[1]>=min(s1[1],s2[1]) and cross_prod([p[0]-s1[0],p[1]-s1[1]], [s2[0]-s1[0],s2[1]-s1[1]])==0

# 线段是否交叉
'''
如果两线段相交，则两线段必然相互跨立对方。
如P1P2跨立Q1Q2 ，
则 矢量 (P1−Q1) 和(P2−Q1)位于矢量(Q2−Q1) 的两侧，则两块面积方向相反，即(P1−Q1)×(Q2−Q1)∗(P2−Q1)×(Q2−Q1)<0 
如Q1Q2跨立P1P2 ，
则 矢量 (Q1−P1) 和(Q2−P1)位于矢量(P2−P1) 的两侧，则两块面积方向相反，即(Q1−P1)×(P2−P1)∗(Q2−P1)×(P2−P1)<0 
''' 
def is_seg_cross(p1,p2,q1,q2):
    if not is_rect_overlap(p1,p2,q1,q2): 
        return False
    # P1P2跨立Q1Q2
    cp1 = cross_prod([p1[0]-q1[0],p1[1]-q1[1]], [q2[0]-q1[0],q2[1]-q1[1]])*cross_prod([p2[0]-q1[0],p2[1]-q1[1]], [q2[0]-q1[0],q2[1]-q1[1]])
    # Q1Q2跨立P1P2
    cp2 = cross_prod([q1[0]-p1[0],q1[1]-p1[1]], [p2[0]-p1[0],p2[1]-p1[1]])*cross_prod([q2[0]-p1[0],q2[1]-p1[1]], [p2[0]-p1[0],p2[1]-p1[1]])
    if cp1 < 0 and cp2 < 0:
        return True
    else:
        return False
# 求线段的交点
# input：edge_p，edge_q
# output：交点的list
def get_seg_cross(p1,p2,q1,q2):
    result=[]
    # 1,快速排斥实验
    if not is_rect_overlap(p1,p2,q1,q2): 
        return result
    # 2，跨立实验
    # P1P2跨立Q1Q2
    cp1 = cross_prod([p1[0]-q1[0],p1[1]-q1[1]], [q2[0]-q1[0],q2[1]-q1[1]])*cross_prod([p2[0]-q1[0],p2[1]-q1[1]], [q2[0]-q1[0],q2[1]-q1[1]])
    # Q1Q2跨立P1P2
    cp2 = cross_prod([q1[0]-p1[0],q1[1]-p1[1]], [p2[0]-p1[0],p2[1]-p1[1]])*cross_prod([q2[0]-p1[0],q2[1]-p1[1]], [p2[0]-p1[0],p2[1]-p1[1]])

    # q,p相离
    if cp1 > 0 or cp2 > 0:
        return result

    # q，p交叉
    elif cp1 < 0 and cp2 < 0:
        xa,ya = p1[0],p1[1]
        xb,yb = p2[0],p2[1]
        xc,yc = q1[0],q1[1]
        xd,yd = q2[0],q2[1]
        #判断两条直线是否相交，矩阵行列式计算
        a = np.matrix(
            [
                [xb-xa,-(xd-xc)],
                [yb-ya,-(yd-yc)]
            ]
        )
        delta = np.linalg.det(a)

        #求两个参数lambda和miu
        c = np.matrix(
            [
                [xc-xa,-(xd-xc)],
                [yc-ya,-(yd-yc)]
            ]
        )
        d = np.matrix(
            [
                [xb-xa,xc-xa],
                [yb-ya,yc-ya]
            ]
        )
        lamb = np.linalg.det(c)/delta
        miu = np.linalg.det(d)/delta
        x = xc + miu*(xd-xc)
        y = yc + miu*(yd-yc)
        result.append([x,y])  
        return result

    # q,p共线重合或T形交叉，返回重合的点
    else:
        for p in [p1,p2]:
            if is_point_on_segment(p,q1,q2):
                result.append(p)
        for q in [q1,q2]:
            if is_point_on_segment(q,p1,p2):
                result.append(q)
        return result




'''
3，多边形运算
'''

# 点是否在多边形内部（不包含边界）
def is_point_inside_polygon(p,polygon):

    angle=0;
    v1=[0,0]
    v2=[0,0]

    for i in range(polygon.n):
        v1[0] = polygon.points[i][0] - p[0]
        v1[1] = polygon.points[i][1] - p[1]
        v2[0] = polygon.points[(i+1)%polygon.n][0] - p[0]
        v2[1] = polygon.points[(i+1)%polygon.n][1] - p[1]
        angle += Angle2D(v1,v2)
        
        # debug
        '''
        print(i,polygon.points[i].x,polygon.points[i].y)
        print(Angle2D(v1,v2)*180/math.pi)
        print(angle*180/math.pi)
        '''

    if abs(angle) < math.pi:
        return False
    else:
        return True
    
# 点是否在多边形内部--射线算法（不包含边界）
def is_point_inside_polygon2(p,polygon):
    # 水平射线
    ray = [p,[0,p[1]]]
    cross = 0
    for i in range(polygon.n):
        # 多边形的边
        edge = [polygon.points[i],polygon.points[(i+1) % polygon.n]]
        if is_seg_cross(ray[0],ray[1],edge[0],edge[1]):
            cross = cross+1
    # 交点的奇偶
    if cross%2 == 1:
        return True
    else:
        return False
        

# 点d在三角形abc的内接圆内外
# input: points in CCW
# output: 0:在边上 >0:在外部  <0:在内部
def in_circle(a, b, c, d):
    #规定ac在ab的CCW方向，否则结果符号相反
    if cross_prod(c-a, b-a)>0:
        b,c=c,b
    va = np.array([a[0],a[1],a[0]**2+a[1]**2])
    vb = np.array([b[0],b[1],b[0]**2+b[1]**2])
    vc = np.array([c[0],c[1],c[0]**2+c[1]**2])
    vd = np.array([d[0],d[1],d[0]**2+d[1]**2])
    m=np.array([vb-va,vb-vc,vb-vd])
    return np.linalg.det(m)

# 点p在三角形内外
# input: tri, p
# output: 0:在边上，1:在内部，-1:在外部
def in_triangle(tri, p):

    # If convex, use CCW-esque algorithm
    e=[cross_prod(tri[i]-p,tri[(i+1)%3]-p) for i in range(3)]

    # 在内部
    if (e[0]>0 and e[1]>0 and e[2]>0) or (e[0]<0 and e[1]<0 and e[2]<0):
        return 1  
    # 在边上
    for i in range(3):
        if e[i]==0:
            if p[0]<=max([tri[i][0],tri[(i+1)%3][0]]) and p[0]>=min([tri[i][0],tri[(i+1)%3][0]]) and p[1]<=max([tri[i][1],tri[(i+1)%3][1]]) and p[1]>=min([tri[i][1],tri[(i+1)%3][1]]):
                return 0
    return -1

# 已知三角形的2个顶点，求第3个顶点
# input: tri,va,vb
# output: True or False，the third vertex or None
def third_vertex_of_tri(tri,va,vb):
    #np.array->list->tuple->list->set
    set_v=set([tuple(va.tolist()),tuple(vb.tolist())])
    #np.array->list->element to tuple->list->set
    set_t=set([tuple(e) for e in tri.tolist()])
    if set_v.issubset(set_t):
        return True,np.array(list(set_t-set_v)[0])
    else:
        return False,None

# 三角形包含顶点   
# input: tri,vi
# output: True or False
def tri_contains_v(tri,vi):
    if ((tri[0]==vi).all() or (tri[1]==vi).all() or (tri[2]==vi).all()):
        return True
    else:
        return False   

# 找包含点p的三角形的边
# input: tri,p
# output: True or False, the vertex index or None
def find_edge(tri,p):
    for i in range(3):
        if cross_prod(tri[i]-p,tri[(i+1)%3]-p)==0:    
            return True,i
    return False,None
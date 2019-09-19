#!/usr/bin/env python
# coding: utf-8

import numpy as np
import math
from nogeo.spatial import is_ccw

'''
1,点
'''
# class Point
def base_point(P_list):
    #查找基准点（纵坐标最小，纵坐标相同时，横坐标最小）
    #P_lis不是重复的点集set(P_list)
    k=0#假设k点P_list[k][0]是第一个点

    for i in range(0,len(P_list)):
        if (P_list[i][1]<P_list[k][1])|((P_list[i][1]==P_list[k][1]) and (P_list[i][0]<P_list[k][0])):
            k=i#k值是宗族表最小的那个点的序号
    return P_list[k]
class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __rmul__(self, c):
        return Point(c * self.x, c * self.y)

    def close(self, that, epsilon=0.01):
        return self.dist(that) < epsilon

    def dist(self, that):
        return math.sqrt(self.sqrDist(that))

    def sqrDist(self, that):
        dx = self.x - that.x
        dy = self.y - that.y
        return dx * dx + dy * dy

    def np(self):
        """Returns the point's Numpy point representation"""
        return [self.x, self.y]
'''
2，线
'''
#class Line
class Line(object):

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        if p1.x == p2.x:
            self.slope = None
            self.intercept = None
            self.vertical = True
        else:
            self.slope = float(p2.y - p1.y) / (p2.x - p1.x)
            self.intercept = p1.y - self.slope * p1.x
            self.vertical = False

    def __str__(self):
        if self.vertical:
            return "x = " + str(self.p1.x)
        return "y = " + str(self.slope) + "x + " + str(self.intercept)

    def __eq__(self, other):
        if self.vertical != other.vertical:
            return False

        if self.vertical:
            return self.p1.x == other.p1.x

        return self.slope == other.slope and self.intercept == other.intercept

    def atX(self, x):
        if self.vertical:
            return None

        return Point(x, self.slope * x + self.intercept)

    def sqrDistance(self, p):
        numerator = float(self.p2.x - self.p1.x) * (self.p1.y - p.y) - \
            (self.p1.x - p.x) * (self.p2.y - self.p1.y)
        numerator *= numerator
        denominator = float(self.p2.x - self.p1.x) * (self.p2.x - self.p1.x) + \
            (self.p2.y - self.p1.y) * (self.p2.y - self.p1.y)
        return numerator / denominator

    def distance(self, p):
        """Returns the distance of p from the line"""
        return sqrt(self.sqrDistance(p))

    def intersection(self, that):
        if that.slope == self.slope:
            return None

        if self.vertical:
            return that.atX(self.p1.x)
        elif that.vertical:
            return self.atX(that.p1.x)

        x = float(self.intercept - that.intercept) / (that.slope - self.slope)
        return self.atX(x)

    def midpoint(self):
        x = float(self.p1.x + self.p2.x) / 2
        y = float(self.p1.y + self.p2.y) / 2
        return Point(x, y)

'''
3,多边形
'''
# class Polygon: points in CCW or CW
class Polygon(object):

    def __init__(self, points_list):
        if len(points_list) < 3:
            # raise ValueError("Polygon must have at least three vertices.")
            print("多边形点数少于三个，请注意")

        self.points = points_list
        self.n = len(points_list)

    def __str__(self):
        s = ""
        for point in self.points:
            if s:
                s += " -> "
            s += str(point)
        return s

    def is_convex(self):
        target = None
        for i in range(self.n):
            # Check every triplet of points
            A = self.points[i % self.n]
            B = self.points[(i + 1) % self.n]
            C = self.points[(i + 2) % self.n]

            if not target:
                target = is_ccw(A, B, C)
            else:
                if is_ccw(A, B, C) != target:
                    return False

        return True

    def is_ccw(self):
        """Returns True if the points are provided in CCW order."""
        return is_ccw(self.points[0], self.points[1], self.points[2])
    
    
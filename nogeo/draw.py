# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

'''
point=[1,2] or point=[[1,2]]
points=[[1,2],[2,3]]
polygons=[polygon1,polygon2]
'''
def plotPoints(points, style='bo'):
    if type(points) == list:
        if not type(points[0]) == list:
            points = [points]

    points = np.array(points)
    plt.plot(points[:, 0], points[:, 1], style)


def showPoints(points, style='bo'):
    plotPoints(points, style=style)
    plt.show()


def plotPolygons(polygons, style='g-'):
    if not type(polygons) == list:
        polygons = [polygons]
    for polygon in polygons:
        points = polygon.points + [polygon.points[0]]
        plotPoints(points, style=style)


def showPolygons(polygons, style='g-'):
    plotPolygons(polygons, style=style)
    plt.show()
    
def plotTriangles(points, simplices):
    width = 100
    height = 100

    # Plot Delaunay triangle with color filled
    center = np.sum(points[simplices.astype(np.int32)], axis=1)/3.0
    color = np.array([(x - width/2)**2 + (y - height/2)**2 for x, y in center])
    #plt.figure(figsize=(6, 4))
    plt.tripcolor(points[:, 0], points[:, 1], simplices.copy(), facecolors=color, edgecolors='k')

    
    
    # Delete ticks, axis and background
    plt.tick_params(labelbottom='off', labelleft='off', left='off', right='off',
                    bottom='off', top='off')
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['top'].set_color('none')
    
    # Save picture
    #plt.savefig('Delaunay.png', transparent=True, dpi=600)    
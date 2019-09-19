# noweapons 无线网优三种武器
## 1，覆盖密度聚类算法
*  算法原理：DBSCAN+噪点比例调参法。
*  算法优点：对于连续、高密度的连片质差点，自动聚类成簇，其特性尤其适用于覆盖问题区域聚焦定位。自动调参应对不同采样点数量级场景。
## 2，过覆盖快速检测算法
*  算法原理：通过目标区域德罗内三角剖分，得到目标基站的周围邻站及多边形覆盖边界，计算采样点在边界多边形内外的比例，得到过覆盖度。
*  算法优点：传统方法依赖覆盖距离和方向的经验判断，对工参准确度要求较高；本模型简化了过覆盖的判决，无需使用方向角，计算快速。
## 3，共覆盖负荷均衡算法
*  算法原理：1，对目标小区的采样点进行凸包建模，以获得较准确的小区覆盖范围。2，计算目标小区和邻近小区凸包的重叠面积，得到共覆盖度。3，将高于共覆盖度门限的小区集合成共覆盖簇，在簇内根据小区利用率等指标，进行负荷均衡评估。
*  算法优点：与传统共站同向负荷均衡相比，扩展了参与负荷均衡的小区范围，最大程度提升均衡效果。
![main](https://github.com/kuki-gs/noweapons/blob/master/noweapons.jpg)

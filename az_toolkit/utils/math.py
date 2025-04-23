import math
import numpy as np


def calculate_distance(point1, point2):
    """
    计算两个点之间的欧几里得距离。

    :param point1: 第一个点 (x1, y1)
    :param point2: 第二个点 (x2, y2)
    :return: 两个点之间的距离
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    
def bezier_curve(x, y):
    NumPoint = len(x) - 1
    t = []
    for i in np.arange(0, 1.01, 0.01):
        t.append(i)
    t = np.asarray(t)
    temp_num = np.power(1-t, NumPoint)
    fx = temp_num * x[0]
    fy = temp_num * y[0]
    for j in range(NumPoint):
        j = j + 1
        weight = np.power(1-t, NumPoint - j)*np.power(t, j)
        m = np.math.factorial(NumPoint) / (np.math.factorial(j) * np.math.factorial(NumPoint - j))
        weight = m * weight
        fx = fx + weight * x[j]
        fy = fy + weight * y[j]
    return fx, fy


if __name__ == '__main__':
    pos = []
    x = pos[:, 0]
    y = pos[:, 1]
    # 使用 np.polyfit 对数据进行三次多项式拟合
    p = np.polyfit(y, x, 3)
    # 使用 Bezier 曲线平滑 x 和 y 数据，生成一条更平滑的曲线
    x, y = bezier_curve(x, y)

    # 计算 y 坐标的中心值（上下界的中间点），可以理解为曲线在垂直方向上的 "重心"
    cen_y = 0.5 * (min(y) + max(y))
    # 找到与中心 y 最近的点
    min_idx = np.argmin(abs(cen_y - y))
    # 获取对应的 x 坐标
    cen_x = x[min_idx]

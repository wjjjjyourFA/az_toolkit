import math


def calculate_distance(point1, point2):
    """
    计算两个点之间的欧几里得距离。

    :param point1: 第一个点 (x1, y1)
    :param point2: 第二个点 (x2, y2)
    :return: 两个点之间的距离
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

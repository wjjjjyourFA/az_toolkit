from math import comb

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline


def bezier_curve(x, y, num_samples=100, mode=2):
    """
    生成贝塞尔曲线
    :param x: 控制点 x 坐标 (list 或 ndarray)
    :param y: 控制点 y 坐标
    :param num_samples: 采样点数量
    :return: (fx, fy) 曲线上的点
    """
    fx = np.array([], dtype=float)
    fy = np.array([], dtype=float)

    if mode == 1:
        # way 1
        # 设定曲线的阶数 n。如果有 len(x) 个控制点，那么阶数是 n = len(x) - 1。x 和 y 应该长度相同。
        NumPoint = len(x) - 1
        t = []
        for i in np.arange(0, 1.01, 0.01):
            t.append(i)
        t = np.asarray(t)

        # 先计算第 0 项的伯恩斯坦基函数
        temp_num = np.power(1 - t, NumPoint)
        # 用这项初始化曲线的 x、y
        fx = temp_num * x[0]
        fy = temp_num * y[0]

        for j in range(NumPoint):
            j = j + 1
            weight = np.power(1 - t, NumPoint - j) * np.power(t, j)
            m = np.math.factorial(NumPoint) / (np.math.factorial(j) * np.math.factorial(NumPoint - j))
            weight = m * weight
            fx = fx + weight * x[j]
            fy = fy + weight * y[j]
    elif mode == 2:
        # way 2
        x = np.array(x)
        y = np.array(y)
        n = len(x) - 1
        t = np.linspace(0, 1, num_samples)

        # 初始化输出数组
        fx = np.zeros_like(t, dtype=float)
        fy = np.zeros_like(t, dtype=float)

        for j in range(n + 1):
            weight = comb(n, j) * (t ** j) * ((1 - t) ** (n - j))
            fx += weight * x[j]
            fy += weight * y[j]

    return fx, fy


def polyfit_points(x, y, degree=3, num_samples=101):
    """
    多项式拟合并返回采样点
    """
    p = np.polyfit(x, y, degree)  # 多项式系数
    x_sample = np.linspace(min(x), max(x), num_samples)
    y_sample = np.polyval(p, x_sample)  # 对采样点求值
    return x_sample, y_sample


def bspline_curve(x, y, k=3, num_samples=100):
    """
    B样条曲线拟合并采样 (基于参数 t 避免重复自变量问题)
    Parameters
    ----------
    x, y : array-like
        控制点坐标
    num_samples : int
        采样点数
    k : int
        样条曲线阶数 (1=线性, 2=二次, 3=三次)

    Returns
    -------
    fx, fy : ndarray
        拟合后曲线上的采样点坐标
    """
    x = np.array(x)
    y = np.array(y)

    # 参数化 (保证严格单调)
    t = np.linspace(0, 1, len(x))

    # 使用 y 作为自变量，拟合 x=f(y)
    # 在参数 t 上分别拟合 x(t), y(t)
    spl_x = make_interp_spline(t, x, k=k)
    spl_y = make_interp_spline(t, y, k=k)

    t_new = np.linspace(0, 1, num_samples)
    fx = spl_x(t_new)
    fy = spl_y(t_new)

    return fx, fy


def show_curve(points, curve_points=None, center_point=None, labels=None, title="Curve Visualization"):
    """
    通用曲线显示函数
    :param points: 控制点，形如 N×2 数组或列表 [[x0,y0], [x1,y1], ...]
    :param curve_points: 拟合曲线点 (fx, fy)，可以是 None
    :param labels: ['Control Points', 'Curve'] 标签列表，可选
    :param title: 图表标题
    """
    points = np.array(points)
    x_ctrl = points[:, 0]
    y_ctrl = points[:, 1]

    plt.figure(figsize=(6, 4))

    # 绘制控制点
    if labels is not None and len(labels) > 0:
        plt.plot(x_ctrl, y_ctrl, 'ro--', label=labels[0])
    else:
        plt.plot(x_ctrl, y_ctrl, 'ro--', label="Control Points")

    # 绘制曲线
    if curve_points is not None:
        fx, fy = curve_points
        if labels is not None and len(labels) > 1:
            plt.plot(fx, fy, 'b-', label=labels[1])
        else:
            plt.plot(fx, fy, 'b-', label="Curve")

    # 中心点（如果有，就在同一个图上继续画）
    if center_point is not None:
        plt.plot(center_point[0], center_point[1], 'gs', markersize=8, label="Center Point")

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(title)
    plt.legend()
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':
    pos = np.array([
        [0, 0],
        [1, 2],
        [2, 2],
        [4, 0],
        [5, 3],
        [5, 5],
    ])
    x = pos[:, 0]
    y = pos[:, 1]

    """ 使用 np.polyfit 对数据进行三次多项式拟合 """
    # fx, fy = polyfit_points(x, y, degree=3)
    # show_curve(np.column_stack((x, y)), [fx, fy])

    """ 使用 Bezier 曲线平滑 x 和 y 数据，生成一条更平滑的曲线 """
    # fx, fy = bezier_curve(x, y)
    # show_curve(np.column_stack((x, y)), [fx, fy])

    """ 使用 np.polyfit 对数据进行三次多项式拟合 """
    fx, fy = bspline_curve(x, y, k=3, num_samples=100)
    # show_curve(np.column_stack((x, y)), [fx, fy])

    """ 计算所需要方向的 "重心" """
    # 曲线在垂直方向上的 "重心"
    # cen_y = 0.5 * (min(fy) + max(fy))
    # cen_idx = np.argmin(abs(fy - cen_y))
    # cen_x = fx[cen_idx]

    # 曲线在水平方向上的 "重心"
    cen_x = 0.5 * (min(fx) + max(fx))
    cen_idx = np.argmin(abs(fx - cen_x))
    cen_y = fy[cen_idx]

    show_curve(np.column_stack((x, y)), [fx, fy], [cen_x, cen_y])

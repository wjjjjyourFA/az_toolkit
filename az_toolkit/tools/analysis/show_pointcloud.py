import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def AxisEqual3D(ax):
    """ 设置一个3D坐标轴的比例，使得在所有三个维度 (x, y, z) 上的尺度相同
    根据当前坐标轴的范围来调整每个轴的限制，使得图形在3D空间中保持比例一致，避免某个维度的尺寸过大或过小。
    """
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:, 1] - extents[:, 0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize / 2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)


def plot_pointcloud(pc_np, birds_view=False, color=None, size=1.0, ax=None, cmap=cm.jet, is_equal_axes=True,
                    elev=-45, azim=-90):
    """ 用于绘制 3D 点云（point cloud）数据
    matplotlib 的 Axes3D 类
    :param pc_np: 3xN
    :param birds_view:
    :param color:
    :param size:
    :param ax:
    :param cmap:
    :param is_equal_axes:
    :return:
    """
    if ax is None:
        fig = plt.figure(figsize=(9, 9))
        ax = Axes3D(fig)

    if type(color) == np.ndarray:
        ax.scatter(pc_np[0, :], pc_np[1, :], pc_np[2, :], s=size, c=color, cmap=cmap, edgecolors='none')
    else:
        ax.scatter(pc_np[0, :], pc_np[1, :], pc_np[2, :], s=size, c=color, edgecolors='none')

    if is_equal_axes:
        AxisEqual3D(ax)
    if birds_view:
        ax.view_init(elev=0, azim=-90)
    else:
        ax.view_init(elev=elev, azim=azim)
    # ax.invert_yaxis()

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
    return ax

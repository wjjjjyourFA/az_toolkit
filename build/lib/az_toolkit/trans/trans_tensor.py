import numpy as np

import torch


def check_numpy_to_torch(x):  # from common_utils.py
    """ 确保输入是 PyTorch 张量。如果输入是 NumPy 数组，则将其转换为 PyTorch 张量 """
    if isinstance(x, np.ndarray):
        return torch.from_numpy(x).float(), True
    return x, False


def rotate_points_along_z(points, angle):  # from common_utils.py
    """
    Args:
        points: (B, N, 3 + C)
        angle: (B), angle along z-axis, angle increases x ==> y
    Returns:

    """
    points, is_numpy = check_numpy_to_torch(points)
    angle, _ = check_numpy_to_torch(angle)

    cosa = torch.cos(angle)
    sina = torch.sin(angle)
    zeros = angle.new_zeros(points.shape[0])
    ones = angle.new_ones(points.shape[0])
    rot_matrix = torch.stack((
        cosa, sina, zeros,
        -sina, cosa, zeros,
        zeros, zeros, ones
    ), dim=1).view(-1, 3, 3).float()
    points_rot = torch.matmul(points[:, :, 0:3], rot_matrix)
    points_rot = torch.cat((points_rot, points[:, :, 3:]), dim=-1)
    return points_rot.numpy() if is_numpy else points_rot


# 调用静态方法，不需要实例化类
def boxes_to_corners_3d(box3d):  # from box_utils.py
    """
        7 -------- 4
       /|         /|
      6 -------- 5 .
      | |        | |
      . 3 -------- 0
      |/         |/
      2 -------- 1
    Args:
        box3d: (N, 7) [x, y, z, dx, dy, dz, heading], (x, y, z) is the box center

    Returns:
        从3D盒子的参数（中心坐标、尺寸、方向）计算出对应的8个角点坐标
    """
    box3d, is_numpy = check_numpy_to_torch(box3d)

    template = box3d.new_tensor((
        [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
        [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1],
    )) / 2

    corners3d = box3d[:, None, 3:6].repeat(1, 8, 1) * template[None, :, :]
    corners3d = rotate_points_along_z(corners3d.view(-1, 8, 3), box3d[:, 6]).view(-1, 8, 3)
    corners3d += box3d[:, None, 0:3]

    return corners3d.numpy() if is_numpy else corners3d
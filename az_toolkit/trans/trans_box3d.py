import numpy as np


def box_7d_obtain_corners(points):
    """ 1x8 中心点坐标 x,y,z, 框的长宽高, 框的方向 """
    box_7d = points.reshape([1, 8]).copy()
    # 提取中心坐标
    # center_x, center_y, center_z = box_7d[1:4]
    cen_p = box_7d[:, 1:4]
    # 定义未旋转的 8 个顶点相对于中心的偏移量
    delta_xyz = 0.5 * box_7d[:, 4:7]

    ''' projecting box3d into image '''
    # way 1
    # p1 = np.stack(
    #     [cen_p[0, 0] + delta_xyz[0, 0], cen_p[0, 1] + delta_xyz[0, 1], cen_p[0, 2] - delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p2 = np.stack(
    #     [cen_p[0, 0] + delta_xyz[0, 0], cen_p[0, 1] + delta_xyz[0, 1], cen_p[0, 2] + delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p3 = np.stack(
    #     [cen_p[0, 0] + delta_xyz[0, 0], cen_p[0, 1] - delta_xyz[0, 1], cen_p[0, 2] + delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p4 = np.stack(
    #     [cen_p[0, 0] + delta_xyz[0, 0], cen_p[0, 1] - delta_xyz[0, 1], cen_p[0, 2] - delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p5 = np.stack(
    #     [cen_p[0, 0] - delta_xyz[0, 0], cen_p[0, 1] + delta_xyz[0, 1], cen_p[0, 2] - delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p6 = np.stack(
    #     [cen_p[0, 0] - delta_xyz[0, 0], cen_p[0, 1] - delta_xyz[0, 1], cen_p[0, 2] + delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p7 = np.stack(
    #     [cen_p[0, 0] - delta_xyz[0, 0], cen_p[0, 1] + delta_xyz[0, 1], cen_p[0, 2] + delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # p8 = np.stack(
    #     [cen_p[0, 0] - delta_xyz[0, 0], cen_p[0, 1] - delta_xyz[0, 1], cen_p[0, 2] - delta_xyz[0, 2]]).reshape(
    #     1,
    #     -1)
    # corner_point = np.concatenate([cen_p, p1, p2, p3, p4, p5, p6, p7, p8],
    #                               axis=0)

    # way 2
    # 定义每个角点在 X、Y、Z 轴上的偏移量
    offsets = np.array([
        [1, 1, -1],  # p1
        [1, 1, 1],   # p2
        [1, -1, 1],  # p3
        [1, -1, -1], # p4
        [-1, 1, -1], # p5
        [-1, -1, 1], # p6
        [-1, 1, 1],  # p7
        [-1, -1, -1] # p8
    ])

    # 省去旋转的计算

    # 通过将偏移量与 delta_xyz 相乘并加上中心点，计算所有角点
    corner_points = cen_p + (delta_xyz * offsets)

    # 将中心点和角点合并成一个数组
    corner_points = np.vstack([cen_p, corner_points])

    return corner_points, cen_p


def box_24d_obtain_corners(points):
    """ 1x25 返回 3D BOX 角点和中心点 """
    tmp = points.reshape([1, 25]).copy()  # label p1:[x,y,z] p2:[x,y,z]

    ''' projecting box3d into image '''
    p1 = (tmp[0, 1:4]).reshape(1, -1)
    p2 = (tmp[0, 4:7]).reshape(1, -1)
    p3 = (tmp[0, 7:10]).reshape(1, -1)
    p4 = (tmp[0, 10:13]).reshape(1, -1)
    p5 = (tmp[0, 13:16]).reshape(1, -1)
    p6 = (tmp[0, 16:19]).reshape(1, -1)
    p7 = (tmp[0, 19:22]).reshape(1, -1)
    p8 = (tmp[0, 22:25]).reshape(1, -1)
    center_point = (p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8) / 8
    corner_points = np.concatenate([p1, p2, p3, p4, p5, p6, p7, p8],
                                  axis=0)

    return corner_points, center_point


def convert_box_7d_2_24d(box_7d):
    # 提取类别信息
    category = box_7d[0]
    # 提取中心坐标
    center_x, center_y, center_z = box_7d[1:4]
    # 提取尺寸
    dx, dy, dz = box_7d[4:7]
    # 提取方向角
    heading = box_7d[7]

    # 定义未旋转的 8 个顶点相对于中心的偏移量
    half_dx = dx / 2
    half_dy = dy / 2
    half_dz = dz / 2

    vertices = np.array([
        [-half_dx, -half_dy, -half_dz],
        [half_dx, -half_dy, -half_dz],
        [half_dx, half_dy, -half_dz],
        [-half_dx, half_dy, -half_dz],
        [-half_dx, -half_dy, half_dz],
        [half_dx, -half_dy, half_dz],
        [half_dx, half_dy, half_dz],
        [-half_dx, half_dy, half_dz]
    ])

    # 定义旋转矩阵
    rotation_matrix = np.array([
        [np.cos(heading), -np.sin(heading), 0],
        [np.sin(heading), np.cos(heading), 0],
        [0, 0, 1]
    ])

    # 旋转顶点
    rotated_vertices = np.dot(vertices, rotation_matrix.T)

    # 将顶点平移到中心位置
    translated_vertices = rotated_vertices + np.array([center_x, center_y, center_z])

    # 展平顶点坐标
    flattened_vertices = translated_vertices.flatten()

    # 组合类别信息和顶点坐标
    box_24d = np.concatenate(([category], flattened_vertices))

    return box_24d


def convert_box_24d_2_7d(box_24d):
    # 提取类别信息
    category = box_24d[0]
    # 提取8个顶点坐标
    points = box_24d[1:25].reshape(8, 3)
    # 计算中心坐标
    center_x = np.mean(points[:, 0])
    center_y = np.mean(points[:, 1])
    center_z = np.mean(points[:, 2])
    # 计算尺寸
    dx = np.max(points[:, 0]) - np.min(points[:, 0])
    dy = np.max(points[:, 1]) - np.min(points[:, 1])
    dz = np.max(points[:, 2]) - np.min(points[:, 2])
    # 计算方向角（heading）
    # 这里假设通过顶点坐标计算方向角，通常可以通过两个相对的顶点来确定
    # 例如，计算x轴方向的向量和y轴方向的向量，然后使用这两个向量来确定朝向
    vector_x = points[1] - points[0]
    vector_y = points[3] - points[0]
    heading = np.arctan2(vector_y[1], vector_x[1])

    box_7d = np.zeros(8)
    box_7d[0] = category
    box_7d[1:4] = np.array([center_x, center_y, center_z])
    box_7d[4:7] = np.array([dx, dy, dz])
    box_7d[7] = heading

    return box_7d

import numpy as np


def project_to_image(pts_3d, p_matrix, model=1):
    """ Project 3d points to image plane.

    Usage: pts_2d = projectToImage(pts_3d, p_matrix)
      input: pts_3d:   nx3 matrix
             p_matrix: 3x4 projection matrix
      output: pts_2d:  nx2 matrix

      p_matrix(3x4) dot pts_3d_extended(4xn) = projected_pts_2d(3xn)
      => normalize projected_pts_2d(2xn)

      <=> pts_3d_extended(nx4) dot p_matrix'(4x3) = projected_pts_2d(nx3)
          => normalize projected_pts_2d(nx2)
    """

    if model == 1:
        """ pts_2d = p⋅pts_3d_extendT """
        n = np.ones((pts_3d.shape[0], 1))
        pts_3d_extend = np.concatenate((pts_3d, n), axis=1)

        pts_2d = np.dot(p_matrix, np.transpose(pts_3d_extend))
        # n X 3
        pts_2d = np.transpose(pts_2d)

    elif model == 2:
        """ pts_2d = pts_3d_extend⋅pT """
        n = pts_3d.shape[0]
        # pts_3d_extend = np.hstack((pts_3d[:, 0].reshape(n, 1),
        #                            pts_3d[:, 1].reshape(n, 1),
        #                            pts_3d[:, 2].reshape(n, 1),
        #                            np.ones((n, 1))))
        pts_3d_extend = np.hstack((pts_3d, np.ones((n, 1))))

        # pts_3d_extend = np.hstack((-pts_3d[:, 1].reshape(n, 1),
        #                            pts_3d[:, 0].reshape(n, 1),
        #                            pts_3d[:, 2].reshape(n, 1),
        #                            np.ones((n, 1))))

        pts_2d = np.dot(pts_3d_extend, np.transpose(p_matrix))  # nx3

    # print(('pts_3d_extend shape: ', pts_3d_extend.shape))

    """ n X 3 """
    # pts_2d[:, 0] /= pts_2d[:, 2]
    # pts_2d[:, 1] /= pts_2d[:, 2]
    pts_2d = pts_2d[:, :2] / pts_2d[:, 2:3]


    """ pts_2d 的组成
     投影后的结果 pts_2d 的每一行包含 3 个值 [u,v,z]:
        u: 投影到图像平面的水平坐标。
        v: 投影到图像平面的垂直坐标。
        z: 深度值 (距离相机的距离)，即点的深度信息。"""
    return pts_2d


def proj_uv(image, lidar, calib_p):
    # n X 3
    pts_2d = project_to_image(lidar, calib_p)

    x = pts_2d[:, 0].astype(np.int32).reshape((-1, 1))
    y = pts_2d[:, 1].astype(np.int32).reshape((-1, 1))
    z = pts_2d[:, 2].astype(np.int32).reshape((-1, 1))

    image_uv = np.concatenate((x, y), axis=1)
    index = ((image_uv[:, 0] > 0) & (image_uv[:, 0] < image.shape[1]) &
             (image_uv[:, 1] > 0) & (image_uv[:, 1] < image.shape[0]) &
             (z[:, 0] > 0))
    image_uv = image_uv[index, :]

    return index, image_uv

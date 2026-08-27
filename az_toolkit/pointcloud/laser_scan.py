import logging

import numpy as np


class LaserScan:
    """ Class that contains LaserScan with x,y,z,r """
    EXTENSIONS_SCAN = ['.bin', '.txt', '.pcd']

    def __init__(self, auto=False, height=64, width=1024, fov_up=3.0, fov_down=-25.0):
        self.auto = auto
        self.proj_H = height
        self.proj_W = width
        self.proj_fov_up = fov_up
        self.proj_fov_down = fov_down
        self.reset()

        """ data """
        self.points = None
        self.remissions = None
        self.proj_range = None
        self.unproj_range = None
        self.proj_xyz = None
        self.proj_remission = None
        self.proj_idx = None
        self.proj_x = None
        self.proj_y = None
        self.proj_mask = None

    def reset(self):
        """ Reset scan members. """
        self.points = np.zeros((0, 3), dtype=np.float32)  # [m, 3]: x, y, z    点云
        self.remissions = np.zeros((0, 1), dtype=np.float32)  # [m ,1]: remission  反射强度

        # projected range image - [H,W] range (-1 is no data)
        self.proj_range = np.full((self.proj_H, self.proj_W), -1,
                                  dtype=np.float32)

        # unprojected range (list of depths for each point)
        self.unproj_range = np.zeros((0, 1), dtype=np.float32)

        # projected point cloud xyz - [H,W,3] xyz coord (-1 is no data)
        self.proj_xyz = np.full((self.proj_H, self.proj_W, 3), -1,
                                dtype=np.float32)

        # projected remission - [H,W] intensity (-1 is no data)
        self.proj_remission = np.full((self.proj_H, self.proj_W), -1,
                                      dtype=np.float32)

        # projected index (for each pixel, what I am in the pointcloud)
        # [H,W] index (-1 is no data)
        self.proj_idx = np.full((self.proj_H, self.proj_W), -1,
                                dtype=np.int32)

        # for each point, where it is in the range image
        self.proj_x = np.zeros((0, 1), dtype=np.int32)  # [m, 1]: x
        self.proj_y = np.zeros((0, 1), dtype=np.int32)  # [m, 1]: y

        # mask containing for each pixel, if it contains a point or not
        self.proj_mask = np.zeros((self.proj_H, self.proj_W),
                                  dtype=np.int32)  # [H,W] mask

    def size(self):
        """ Return the size of the point cloud. """
        return self.points.shape[0]

    def __len__(self):
        return self.size()

    def open_scan(self, filename):
        """ Open raw scan and fill in attributes """
        # reset just in case there was an open structure
        self.reset()

        # check filename is string
        if not isinstance(filename, str):
            raise TypeError("Filename should be string type, "
                            "but was {type}".format(type=str(type(filename))))

        # check extension is a laserscan
        if not any(filename.endswith(ext) for ext in self.EXTENSIONS_SCAN):
            raise RuntimeError("Filename extension is not valid scan file.")

        # if all goes well, open pointcloud
        scan = np.fromfile(filename, dtype=np.float32)
        point_num = scan.shape[0] // 4
        scan = scan[:4 * point_num]
        scan = scan.reshape((-1, 4))

        # put in attribute
        points = scan[:, 0:3]  # get xyz
        remissions = scan[:, 3]  # get remission
        self.set_points(points, remissions)
        return points, remissions

    def set_points(self, points, remissions=None):
        """ Set scan attributes (instead of opening from file) """
        # reset just in case there was an open structure
        self.reset()

        # check scan makes sense
        if not isinstance(points, np.ndarray):
            raise TypeError("Scan should be numpy array")

        # check remission makes sense
        if remissions is not None and not isinstance(remissions, np.ndarray):
            raise TypeError("Remissions should be numpy array")

        # put in attribute
        self.points = points  # get xyz
        if remissions is not None:
            self.remissions = remissions  # get remission
        else:
            self.remissions = np.zeros((points.shape[0]), dtype=np.float32)

        # if projection is wanted, then do it and fill in the structure
        if self.auto:
            self.do_range_projection()
            logging.warning("Warning: You have enabled automatic tasks! in LaserScan !")

    def do_range_projection(self):
        """ Project a pointcloud into a spherical projection image.projection.
            Function takes no arguments because it can be also called externally
            if the value of the constructor was not set (in case you change your
            mind about wanting the projection)
        """
        # laser parameters  # 计算总视野（弧度）
        fov_up = self.proj_fov_up / 180.0 * np.pi  # field of view up in rad          # 上视野（弧度）
        fov_down = self.proj_fov_down / 180.0 * np.pi  # field of view down in rad        # 下视野（弧度）
        fov = abs(fov_down) + fov_up  # get field of view total in rad   # 总视野（弧度）

        # get depth of all points  # 计算每个点到原点的距离--球面
        depth = np.linalg.norm(self.points, 2, axis=1)  # 计算每个点的欧几里得距离

        # ensure depth is not zero to avoid division by zero
        """ 存在零点 """
        depth = np.where(depth == 0, 1e-6, depth)  # Replace zero depth with a very small value

        # get scan components
        scan_x = self.points[:, 0]
        scan_y = self.points[:, 1]
        scan_z = self.points[:, 2]

        # get angles of all points
        yaw = -np.arctan2(scan_y, scan_x)  # 水平角
        pitch = np.arcsin(scan_z / depth)  # 俯仰角

        # get projections in image coords
        """ yaw-pitch坐标系，转坐标原点至左上角，然后规范化，适应不同的雷达参数 """
        proj_x = 0.5 * (yaw / np.pi + 1.0)  # in [0.0, 1.0]
        # proj_y = 1.0 - (pitch + abs(fov_down)) / fov       # in [0.0, 1.0]
        proj_y = (fov_up - pitch) / fov  # equal to this  # in [0.0, 1.0]

        # scale to image size using angular resolution
        """ 规范化后，再乘以投影图像的宽高，就得到了这个点投影到距离图像的坐标
        映射到 TargetRangeSize 图像大小 """
        proj_x *= self.proj_W  # in [0.0, W]
        proj_y *= self.proj_H  # in [0.0, H]

        # round and clamp for use as index
        """ 将浮点数的坐标值转换为整数，以便用于图像的像素坐标
        限制最小值，限制最大值，不删除任何点 """
        proj_x = np.floor(proj_x)
        proj_x = np.minimum(self.proj_W - 1, proj_x)
        proj_x = np.maximum(0, proj_x).astype(np.int32)  # in [0,W-1]
        # store a copy in orig order
        self.proj_x = np.copy(proj_x)

        proj_y = np.floor(proj_y)
        proj_y = np.minimum(self.proj_H - 1, proj_y)
        proj_y = np.maximum(0, proj_y).astype(np.int32)  # in [0,H-1]
        # store a copy in original order
        self.proj_y = np.copy(proj_y)

        # copy of depth in original order
        self.unproj_range = np.copy(depth)

        # order in decreasing depth
        """ 按深度递减顺序对数据进行排序，确保较远的点先被处理，
        这样在投影到图像时，较近的点会覆盖较远的点。
        浮点数转换的整数，作为图像像素坐标，可能存在同个坐标对应了多个点 """
        indices = np.arange(depth.shape[0])  # points_num = depth.shape[0]
        order = np.argsort(depth)[::-1]
        depth = depth[order]
        indices = indices[order]
        points = self.points[order]
        remission = self.remissions[order]
        proj_y = self.proj_y[order]
        proj_x = self.proj_x[order]

        """ 健壮性检查，原有的depth零点bug，导致引用超出范围，20240611 已解决，可以注释 """
        proj_y = np.maximum(0, proj_y).astype(np.int32)  # in [0,H-1]
        proj_x = np.maximum(0, proj_x).astype(np.int32)  # in [0,H-1]

        # assing to images
        self.proj_range[proj_y, proj_x] = depth
        self.proj_xyz[proj_y, proj_x] = points
        self.proj_remission[proj_y, proj_x] = remission
        self.proj_idx[proj_y, proj_x] = indices
        # -1 is the empty sentinel; original point index 0 is valid.
        self.proj_mask = (self.proj_idx >= 0).astype(np.uint8)

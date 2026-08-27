from az_toolkit.pointcloud.laser_scan import LaserScan
from az_toolkit.utils.trans_box3d import *

try:
    # 先尝试导入运行目录下的 custom_config.py
    from custom_config import CustomConfig as Cfg
except ImportError:
    # 如果没有，就导入工具包里的 custom_config.py
    from az_toolkit.custom_config.default_config import CustomConfig as Cfg


class RangeImageCreator:
    """ spherical projection: """

    def __init__(self):
        self.fov_up = Cfg.fov_up
        self.fov_down = Cfg.fov_down
        self.proj_H = Cfg.TargetRangeSize[0]
        self.proj_W = Cfg.TargetRangeSize[1]
        self.show_image = []
        self.save_image = []
        self.points_lidar = []
        self.dpi = 10
        self.scan = LaserScan(
            auto=False,  # auto --> self.scan.do_range_projection()
            height=Cfg.TargetRangeSize[0],
            width=Cfg.TargetRangeSize[1],
            fov_up=self.fov_up,
            fov_down=self.fov_down
        )
        self.max_point = 230400  # RS128

    def load_lidar_data_to_scan(self, filename):  # -> read-data()
        """ load lidar points
        default lidar.bin is cm
        lidar.pcd is m """
        scan = []
        with open(filename) as f:
            while True:
                tmp = f.readline()
                if not tmp:
                    break
                b = [int(i) for i in tmp.split()]
                if b[0] == 0 and b[1] == 0 and b[2] == 0:
                    continue
                scan.append(b)
            scan = np.stack(scan, axis=0)

            x = scan[:, :1] / 100.
            y = scan[:, 1:2] / 100.
            z = scan[:, 2:3] / 100.
            scan = np.hstack((x, y, z, scan[:, 3:4]))
            # scan = np.hstack((y, -x, z, scan[:, 3:4]))

        points = scan[:, 0:3]  # get xyz
        remissions = scan[:, 3]  # get remission
        self.scan.set_points(points, remissions)

        return True

    def load_points_to_scan(self, points):
        """ default lidar.bin is cm
                lidar.pcd is m """
        x = points[:, :1] / 100.
        y = points[:, 1:2] / 100.
        z = points[:, 2:3] / 100.
        points = np.hstack((x, y, z, points[:, 3:4]))
        # 将原始的 (x, y, z) 坐标系转换为 (y, -x, z) 坐标系
        # Right Front Up to Front Left Up
        # points = np.hstack((y, -x, z, points[:, 3:4]))

        _points = points[:, 0:3]  # get xyz
        _remissions = points[:, 3]  # get remission
        self.scan.set_points(_points, _remissions)

        return True

    def get_scan_result(self):
        if not self.scan.auto:  # auto is False
            self.scan.do_range_projection()

        # 获取存储投影数据的tensor，大小为range图的H*W
        proj_range = self.scan.proj_range
        proj_xyz = self.scan.proj_xyz
        proj_remission = self.scan.proj_remission
        proj_mask = self.scan.proj_mask
        return proj_range, proj_xyz, proj_remission, proj_mask, self.scan.points

    def project_range(self, points):
        self.load_points_to_scan(points)

        proj_range, proj_xyz, proj_remission, proj_mask, _ = self.get_scan_result()

        return proj_range, proj_xyz, proj_remission, proj_mask  # , _points, _remissions

    def project_range_KITTI(self, points):
        x = points[:, :1]
        y = points[:, 1:2]
        z = points[:, 2:3]
        points = np.hstack((x, y, z, points[:, 3:4]))

        _points = points[:, 0:3]  # get xyz
        _remissions = points[:, 3]  # get remission
        self.scan.set_points(_points, _remissions)

        proj_range, proj_xyz, proj_remission, proj_mask, _ = self.get_scan_result()

        return proj_range, proj_xyz, proj_remission, proj_mask, points

    """ 后处理部分 """

    def get_range_image(self):
        range_image = (255 * (abs(self.scan.proj_xyz) / Cfg.MaxDis)).astype(np.uint8)
        return range_image

    def get_range_image_color(self):
        # 获取并归一化投影图（shape: H x W x 3）
        proj = abs(self.scan.proj_xyz) / Cfg.MaxDis

        # 转成 [0, 255] 范围的 float 图像
        show_im = 255.0 * proj
        # 确保只取前三个通道，并 copy 一份
        # show_im = show_im[:, :, :3].copy()

        # 分通道线性增强亮度（根据你给的公式）
        show_im[:, :, 0] = show_im[:, :, 0] * 11.47 + 10.88
        show_im[:, :, 1] = show_im[:, :, 1] * 6.91 + 0.23
        show_im[:, :, 2] = show_im[:, :, 2] * 0.86 + (-1.04)

        # 限制范围到 [0, 255] 并转为 uint8，适配显示
        range_image = np.clip(show_im, 0, 255).astype(np.uint8)

        return range_image

    def get_range_feature(self):
        range_feature = np.concatenate([self.scan.proj_range.reshape(self.proj_H, self.proj_W, 1),
                                        self.scan.proj_xyz,
                                        self.scan.proj_remission.reshape(self.proj_H, self.proj_W, 1)],
                                       axis=2)
        return range_feature

    def cal_position(self, points):
        fov_up = self.fov_up / 180.0 * np.pi  # field of view up in rad
        fov_down = self.fov_down / 180.0 * np.pi  # field of view down in rad
        fov = abs(fov_down) + abs(fov_up)  # get field of view total in rad

        # get depth of all points
        depth = np.linalg.norm(points, 2, axis=1)
        depth = np.maximum(depth, 1e-10)  # 将零值替换为一个非常小的数

        # get scan components
        scan_x = points[:, 0]
        scan_y = points[:, 1]
        scan_z = points[:, 2]

        # get angles of all points
        yaw = -np.arctan2(scan_y, scan_x)
        pitch = np.arcsin(scan_z / depth)

        # get projections in image coords
        proj_x = 0.5 * (yaw / np.pi + 1.0)  # in [0.0, 1.0]
        proj_y = 1.0 - (pitch + abs(fov_down)) / fov  # in [0.0, 1.0]

        # scale to image size using angular resolution
        proj_x *= self.proj_W  # in [0.0, W]
        proj_y *= self.proj_H  # in [0.0, H]

        # round and clamp for use as index
        proj_x = np.floor(proj_x)
        proj_x = np.minimum(self.proj_W - 1, proj_x)
        proj_x = np.maximum(0, proj_x).astype(np.int32)  # in [0,W-1]

        proj_y = np.floor(proj_y)
        proj_y = np.minimum(self.proj_H - 1, proj_y)
        proj_y = np.maximum(0, proj_y).astype(np.int32)  # in [0,H-1]
        return proj_x, proj_y

    """ 后处理部分 """

    def ProjLidarObj2RangeList8Point(self, _result, match_object=None):
        """
        主要用于投影 3D 框到 2D rangeImage 图像。
        过滤掉不符合要求的条目（大小不符合阈值），并将这些条目置零。
        在传入 match_object 的情况下，更新并返回 match_object。
        返回值包含 rangeImage_box 和更新后的 match_object 或 _result。
        result : 1x25 的数组 包含了 3D Box 每个顶点的坐标
        """
        rangeImage_box = []
        """ 已改成使用索引 """
        # if match_object is not None:
        #     """ 只画选中了的框 """
        #     # mask = (np.zeros(match_object.shape[0], dtype=np.bool_))
        #     # mask[:] = True
        #     mask = np.ones(match_object.shape[0], dtype=bool)  # 直接初始化 True

        """ 索引 """
        # 预分配布尔数组以存储无效索引
        # invalid_mask = np.zeros(len(_result))
        # _invalid_mask_ = []
        _invalid_mask_ = np.zeros(len(_result), dtype=bool)  # 直接用布尔值

        for i in range(0, len(_result)):
            corner_point, _ = box3d_24d_obtain_corners(_result[i])
            x, y = self.cal_position(corner_point)  # xyz 2 range_image_uv

            # minx = int(np.max([0, np.min(x[1:])]))
            # maxx = int(np.min([self.proj_W, np.max(x[1:])]))
            # miny = int(np.max([0, np.min(y[1:])]))
            # maxy = int(np.min([self.proj_H, np.max(y[1:])]))
            minx, maxx = np.clip([np.min(x[1:]), np.max(x[1:])], 0, self.proj_W)
            miny, maxy = np.clip([np.min(y[1:]), np.max(y[1:])], 0, self.proj_H)

            """ 在画面中太大的框，认为是错误的 """
            if abs(minx - maxx) > 0.25 * Cfg.TargetRangeSize[1] or \
                abs(miny - maxy) > 0.25 * Cfg.TargetRangeSize[0]:
                # 将不符合要求的条目置为零
                # _result[i] = np.zeros_like(_result[i])
                # # invalid_mask[i] = 1
                # _invalid_mask_.append(i)
                _result[i].fill(0)  # 直接置零
                _invalid_mask_[i] = True  # 记录无效索引
                continue

            rangeImage_box.append([minx, miny, maxx, maxy, 0, x, y])  # position of rangeimage, centerp.topp

        ''' removing the invalid line '''
        if match_object is not None:
            """ 假设 _invalid_mask_ 为 [2, 5, 7]，mask 初始值为 [True, True, True, True, True, True, True, True]，
            那么执行 mask[_invalid_mask_] = False 后，mask 将变成 [True, True, False, True, True, False, True, False]。 """
            # mask[_invalid_mask_] = False
            # new_match_object = match_object[mask, :]
            # 直接用布尔索引筛选
            new_match_object = match_object[~_invalid_mask_]
            return rangeImage_box, new_match_object
        else:
            return rangeImage_box, _result

    def ProjLidarObj2RangeList8point_eval(self, _result):
        """
        ProjLidarObj2RangeList8Point 类似功能，但目标是评估数据。
        返回无效数据的索引（invalid_mask），而不是修改或过滤原始数据。
        保留所有条目在 rangeImage_box 中，无论条目是否无效。
        """
        num_objects = len(_result)
        rangeImage_box = np.zeros((num_objects, 7), dtype=object)  # 预分配
        # invalid_mask = np.zeros(len(_result))
        invalid_mask = np.zeros(num_objects, dtype=bool)  # 直接用布尔值

        for i in range(0, len(_result)):
            corner_point, _ = box3d_24d_obtain_corners(_result[i])
            x, y = self.cal_position(corner_point)

            # minx = int(np.max([0, np.min(x[1:])]))
            # maxx = int(np.min([self.proj_W, np.max(x[1:])]))
            # miny = int(np.max([0, np.min(y[1:])]))
            # maxy = int(np.min([self.proj_H, np.max(y[1:])]))
            minx, maxx = np.clip([np.min(x[1:]), np.max(x[1:])], 0, self.proj_W)
            miny, maxy = np.clip([np.min(y[1:]), np.max(y[1:])], 0, self.proj_H)

            # invalid 序号暂时没有发挥作用
            # 用continue跳过会导致数据idx不匹配
            if abs(minx - maxx) > 0.25 * Cfg.TargetRangeSize[1] or \
                abs(miny - maxy) > 0.25 * Cfg.TargetRangeSize[0]:
                # print("abs(minx - maxx):", abs(minx - maxx))
                invalid_mask[i] = True
                # continue

            # position of rangeimage, centerp.top
            # rangeImage_box.append([minx, miny, maxx, maxy, 0, x, y])
            rangeImage_box[i] = [minx, miny, maxx, maxy, 0, x, y]

        return rangeImage_box, invalid_mask

    def ProjLidarObj2RangeList1CenterHW(self, _result):
        """
        将 box3d 的框转换到 rangeImage 图像
        result : 1x8 的数组 包含了 3D Box 中心坐标以及对应的边界框尺寸
        """
        # rangeImage_box = []
        num_objects = len(_result)
        rangeImage_box = np.zeros((num_objects, 5), dtype=object)  # 预分配
        for i in range(0, len(_result)):
            ''' projecting box3d into image '''
            corner_point, _ = box3d_7d_obtain_corners(_result[i])

            x, y = self.cal_position(corner_point)

            # minx = int(np.max([0, np.min(x[1:])]))
            # maxx = int(np.min([self.proj_W, np.max(x[1:])]))
            # miny = int(np.max([0, np.min(y[1:])]))
            # maxy = int(np.min([self.proj_H, np.max(y[1:])]))
            minx, maxx = np.clip([np.min(x[1:]), np.max(x[1:])], 0, self.proj_W)
            miny, maxy = np.clip([np.min(y[1:]), np.max(y[1:])], 0, self.proj_H)

            # position of rangeimage, centerp.top
            # rangeImage_box.append([minx, miny, maxx, maxy, 0])
            rangeImage_box[i] = [minx, miny, maxx, maxy, 0]

        return rangeImage_box

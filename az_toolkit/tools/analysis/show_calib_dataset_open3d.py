#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import open3d as o3d
from mpl_toolkits.mplot3d import Axes3D
from open3d import *

from az_toolkit.config import GLOBAL_CONFIG
from az_toolkit.custom_config.default_config import CustomConfig as Cfg
from az_toolkit.pointcloud.range_image_creator import *
from az_toolkit.utils.color import color
from az_toolkit.utils.load_box2d import *
from az_toolkit.utils.load_box3d import *
from az_toolkit.utils.plot_box2d import *


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


def custom_draw_geometry(pcd, LineSets):
    """ o3d.geometry.LineSet 是 Open3D 提供的一个几何对象，用于表示线的集合。一个 LineSet 通常包括：
    点的集合 (points)：定义线段的端点。
    线的索引集合 (lines)：定义哪些点通过线段连接起来。
    线的颜色 (colors)（可选）：为线段定义颜色。
    """
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd)
    for i in range(0, len(LineSets)):
        vis.add_geometry(LineSets[i])

    vis.run()
    vis.destroy_window()


class ShowLabelByHand:
    def __init__(self, root, args):
        self.prefix = root + f"/matched"
        self.prefixRead = self.prefix + args.ReadFolderName
        self.idx = 0
        self.LidarPath = os.path.join(self.prefixRead, 'lidar')
        self.ImagePath = os.path.join(self.prefixRead, 'undistort_image')
        self.LidarBoxPath = os.path.join(self.prefixRead, 'result_unmatched/box3d')
        self.ImageBoxPath = os.path.join(self.prefixRead, 'result_unmatched/box2d')
        self.MatchDataPath = os.path.join(self.prefixRead, 'result_unmatched/match')
        self.mkdir_folder()

        """ data """
        self.ImageName = None
        self.image = None
        self.input_image = None
        self.LidarName = None
        self.lidar = None
        self.input_lidar = None
        self.LidarNameList = None
        self.check_files()

        self.range_image = None
        self.lidar_result_file = None
        self.image_result_file = None
        self.image_seg_file = None

        """ processor """
        self.ranger = None
        self.current_sImgBox_idx = -1  # SelectImgBox
        self.current_sRangeBox_idx = -1  # SelectRangeBox
        # box3d: (N, 8)[label, {x, y, z} * 8]
        self.LidarBox = None
        self.LidarBox_RangeImage = None
        self.ImageBox = None
        self.Unmatched3DBox = None
        self.UnmatchedBox = None
        self.MatchObject = None
        self.MatchName = None  # .npy

        """ show """
        self.vis = None
        self.pcd = None
        self.box_list = []

    def mkdir_folder(self):
        ensure_dir(self.LidarPath)
        ensure_dir(self.ImagePath)
        ensure_dir(self.MatchDataPath)

    def check_files(self):
        self.LidarNameList = load_data_file_sort(self.LidarPath, ".bin")
        # self.LidarNameList = load_data_file_sort(self.LidarPath, ".txt")

    def init_cv(self):
        cv2.namedWindow('Image', cv.WINDOW_GUI_NORMAL)
        cv2.resizeWindow('Image', int(Cfg.ImageSize[1] / 3), int(Cfg.ImageSize[0] / 3))
        cv2.moveWindow('Image', 0, 0)
        cv.namedWindow('RangeImage', cv.WINDOW_GUI_NORMAL)
        cv2.resizeWindow('RangeImage', int(Cfg.TargetRangeSize[1]), int(Cfg.TargetRangeSize[0]))
        cv2.moveWindow('RangeImage', 0, int(Cfg.ImageSize[0] / 3) + 40)
        cv2.namedWindow('MergeImage', cv.WINDOW_GUI_NORMAL)
        ''' resize in ShowMerger '''
        cv2.resizeWindow('MergeImage',
                         int(Cfg.TargetImageSize[1] + Cfg.TargetRangeSize[1]),
                         int(Cfg.TargetImageSize[0]))
        cv2.moveWindow('MergeImage',
                       0,
                       int(Cfg.ImageSize[0] / 3) + int(Cfg.TargetRangeSize[0]) + 80)

    def show_cv(self, _image, _range, _merge):
        cv.imshow('RangeImage', _range)
        cv.imshow('Image', _image)
        cv.imshow("MergeImage", _merge)
        # cv2.waitKey(1)

    def init_vis(self):
        '''-------Initializing the 3d visualizer-------'''
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        # 添加坐标轴
        axis = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=10.0,  # 坐标轴长度
            origin=[0, 0, 0]  # 坐标轴原点
        )
        self.vis.add_geometry(axis)
        # 渲染选项
        render_option = self.vis.get_render_option()
        render_option.point_size = 4
        render_option.background_color = np.asarray([0, 0, 0])
        self.pcd = o3d.geometry.PointCloud()

        # 提前创建 100 个 LineSet
        for i in range(0, 100):
            line_set = o3d.geometry.LineSet()
            self.box_list.append(line_set)
        '''-------Initializing the 3d visualizer-------'''

    def init_model(self):
        print(">>> Defining RangeImage Processor.....")
        self.ranger = RangeImageCreator()
        print(">>> Done.....")

    def load_raw_data(self, _idx):
        ''' Matching data path '''
        self.LidarName = self.LidarNameList[_idx]
        if not os.path.exists(self.LidarName):
            print(f"No such file: {self.LidarName}")
            return False

        item = self.LidarName.split('/')[-1]
        # item = item.split('_')[0]
        item = item.split('.')[0]
        self.MatchName = self.MatchDataPath + '/' + item + ".npy"

        ''' Loading image and lidar data '''
        self.ImageName = self.ImagePath + "/" + item + '.jpg'
        if not os.path.exists(self.ImageName):
            print(f"No such file: {self.ImageName}")
            return False

        self.image = cv2.imread(self.ImageName)
        self.input_image = copy(self.image)

        self.lidar = np.fromfile(self.LidarName, dtype=np.int32)
        self.input_lidar = self.lidar.reshape([-1, 4])

        self.image_result_file = self.ImageBoxPath + "/" + item + '.txt'
        self.image_seg_file = self.ImagePath + "/" + item + '.png'
        self.lidar_result_file = self.LidarBoxPath + "/" + item + '.txt'

        return True

    def run(self):
        lines_box = np.array(
            [[0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 6], [2, 3], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]])
        colors = np.array([[0, 255, 0] for j in range(len(lines_box))])

        while True:
            if self.idx >= len(self.LidarNameList):
                break
            show_count = "%d/%d" % (self.idx + 1, len(self.LidarNameList))
            self.current_sImgBox_idx = -1  # SelectImgBox
            self.current_sRangeBox_idx = -1  # SelectRangeBox

            if not self.load_raw_data(self.idx):
                continue

            '''Creating RangeImage'''
            proj_range, proj_xyz, proj_remission, proj_mask = self.ranger.project_range(self.input_lidar)
            range_feature = self.ranger.get_range_feature()
            """ """
            # self.range_image = self.ranger.get_range_image()
            """ """
            proj_range[proj_range > 170] = 170
            zero_mask = proj_range == -1
            tmp_range_image = (
                    255 * (proj_range - np.min(proj_range)) / (np.max(proj_range) - np.min(proj_range))).astype(
                np.uint8)
            self.range_image = cv2.applyColorMap(tmp_range_image, cv2.COLORMAP_JET)
            self.range_image[zero_mask, :] = 0

            '''Loading detection result'''
            self.LidarBox = read_box3d_result_24d(self.lidar_result_file)  # type,{x,y,z}*8
            self.LidarBox_RangeImage, invalid = self.ranger.ProjLidarObj2RangeList8point_eval(self.LidarBox)
            self.ImageBox = read_box2d_result(self.image_result_file)
            draw_box2d_on_image(self.input_image, self.ImageBox, False)

            # 一对匹配帧中有多少个雷达框和图像框，有几个框已配对
            self.Unmatched3DBox = np.ones(len(self.LidarBox))
            self.UnmatchedBox = np.ones(len(self.ImageBox))
            """ 这是一个 M X N 的矩阵，M表示有多少个3Dbox，N表示有多少个box """
            self.MatchObject = np.zeros([len(self.LidarBox), len(self.ImageBox)])

            """ """
            x = self.input_lidar[:, :1] / 100.
            y = self.input_lidar[:, 1:2] / 100.
            z = self.input_lidar[:, 2:3] / 100.
            scan = np.hstack((x, y, z))
            # scan = np.hstack((y, -x, z))
            self.pcd.points = o3d.utility.Vector3dVector(np.asarray(scan))

            for obj_idx in range(0, len(self.LidarBox)):
                corner_point, _ = box3d_24d_obtain_corners(self.LidarBox[obj_idx])
                self.box_list[obj_idx].points = o3d.utility.Vector3dVector(corner_point)
                self.box_list[obj_idx].lines = o3d.utility.Vector2iVector(lines_box)
                self.box_list[obj_idx].colors = o3d.utility.Vector3dVector(colors)

            """ 基础调用 """
            # custom_draw_geometry(self.pcd, self.box_list)
            """ 目前作用，当第一张查看之后，关闭 vis 窗口
            后续 vis 显示自动进行
            """
            if self.idx == 0:
                for i in range(0, len(self.LidarBox)):
                    self.vis.add_geometry(self.box_list[i])
                self.vis.add_geometry(self.pcd)
                self.vis.run()  # block show
            else:
                self.vis.update_geometry(self.pcd)
                for i in range(0, len(self.LidarBox)):
                    self.vis.update_geometry(self.box_list[i])
            '''-------------Open3d:pcd---------------'''
            self.vis.update_geometry(self.pcd)
            self.vis.poll_events()
            self.vis.update_renderer()
            '''-------------Open3d:pcd---------------'''

            """ 没有匹配时，注释该段落 """
            # Update .npy
            # if os.path.exists(self.MatchName):
            #     self.MatchObject = np.load(self.MatchName)
            #     for ii in range(0, self.MatchObject.shape[0]):
            #         for jj in range(0, self.MatchObject.shape[1]):
            #             # 已配对 已选中
            #             if self.MatchObject[ii, jj] == 1:
            #                 self.Unmatched3DBox[ii] = 0
            #                 self.UnmatchedBox[jj] = 0

            '''Show object Detection'''
            self.show_init_box(show_count)

            merged_image = self.ShowMerge(self.input_image, self.range_image, self.MatchObject)
            cv.putText(self.input_image, show_count, (10, 20), 1, 2, color=(0, 0, 255), thickness=2)
            cv.putText(self.range_image, show_count, (10, 10), 1, 1, color=(0, 0, 255), thickness=2)
            cv.putText(merged_image, show_count, (10, 20), 1, 2, color=(0, 0, 255), thickness=2)
            self.show_cv(self.input_image, self.range_image, merged_image)
            cv.waitKey(1)

            self.idx += 1
        cv.destroyAllWindows()
        self.vis.clear_geometries()

    def show_init_box(self, _show_count):
        '''Show object Detection'''
        cv.putText(self.range_image, _show_count, (10, 10), 1, 1, color=(0, 0, 255), thickness=2)
        cv.putText(self.input_image, _show_count, (10, 20), 1, 2, color=(0, 0, 255), thickness=2)

        for ii in range(0, len(self.ImageBox)):
            tmpBox = self.ImageBox[ii]
            cv2.rectangle(self.input_image, (int(tmpBox[0]), int(tmpBox[1])), (int(tmpBox[2]), int(tmpBox[3])),
                          color=(0, 0, 255), thickness=5)
        for ii in range(0, len(self.LidarBox_RangeImage)):
            tmpBox = self.LidarBox_RangeImage[ii]
            cv2.rectangle(self.range_image, (tmpBox[0], tmpBox[1]), (tmpBox[2], tmpBox[3]),
                          color=(0, 0, 255), thickness=2)
        # cv2.imshow("Image", self.input_image)
        # cv2.imshow("RangeImage", self.range_image)
        # cv2.waitKey(0)

    def ShowMerge(self, _image, _range, _MatchObject):
        '''show merge image'''
        """将输入图像 _image 缩放到目标大小 Cfg.TargetImageSize"""
        show_image_ = cv2.resize(_image, (Cfg.TargetImageSize[1], Cfg.TargetImageSize[0]),
                                 cv2.INTER_LINEAR)
        rh = show_image_.shape[0] / _image.shape[0]
        rw = show_image_.shape[1] / _image.shape[1]
        """"创建一个新的图像 range_image，其高度与缩放后的输入图像相同，宽度与 _range 图像相同，初始值为全黑"""
        range_image = np.zeros((show_image_.shape[0], _range.shape[1], 3), dtype=np.uint8)
        offset = (range_image.shape[0] - Cfg.TargetRangeSize[0])
        """"将 _range 图像放置到 range_image 的底部位置，顶部用黑色填充"""
        range_image[(range_image.shape[0] - Cfg.TargetRangeSize[0]):, :, :] = _range
        """将缩放后的输入图像与处理后的 range_image 水平拼接成一个新的图像 merged_image"""
        merged_image = np.uint8(np.concatenate([show_image_, range_image], axis=1))
        merged_image = np.ascontiguousarray(merged_image)

        '''Create Gt'''
        """匹配对的可视化：遍历 MatchObject，计算匹配对的中心位置，并在合并后的图像上绘制线条和圆圈，以标记匹配对的位置"""
        pairs = []
        for i in range(0, _MatchObject.shape[0]):
            for j in range(0, _MatchObject.shape[1]):
                if _MatchObject[i, j] == 1:
                    sImgBox = self.ImageBox[j]
                    sRangeBox = self.LidarBox_RangeImage[i]

                    center_image = [int(0.5 * (sImgBox[0] + sImgBox[2])),
                                    int(0.5 * (sImgBox[1] + sImgBox[3]))]
                    center_range = [int(0.5 * (sRangeBox[0] + sRangeBox[2])),
                                    int(0.5 * (sRangeBox[1] + sRangeBox[3]))]
                    pairs.append([center_image[0], center_image[1], center_range[0], center_range[1]])

        for i in range(0, len(pairs)):
            if i > 18:
                tmp_color = color[0]
            else:
                tmp_color = color[i]
            tmp_pairs = pairs[i]
            tmp_pairs[0] = int(tmp_pairs[0] * rw)
            tmp_pairs[1] = int(tmp_pairs[1] * rh)

            if tmp_pairs[0] != -1 and tmp_pairs[1] != -1 and tmp_pairs[2] != -1 and tmp_pairs[3] != -1:
                cur_color = np.array([tmp_color[0], tmp_color[1], tmp_color[2]]).astype(np.uint8)
                cur_color = tuple([int(x) for x in cur_color])
                cv2.line(merged_image,
                         (int(tmp_pairs[0]), int(tmp_pairs[1])),
                         (tmp_pairs[2] + show_image_.shape[1], tmp_pairs[3] + offset),
                         cur_color, thickness=2)
                # cv2.line(merged_image,
                #          (int(tmp_pairs[0]), int(tmp_pairs[1])),
                #          (tmp_pairs[2] + show_image_.shape[1], tmp_pairs[3] + offset),
                #          (np.int(tmpcolor[0]), np.int(tmpcolor[1]), np.int(tmpcolor[2])), thickness=2)
                cv2.circle(merged_image, (int(tmp_pairs[0]), int(tmp_pairs[1])),
                           2, (0, 255, 0),
                           thickness=2)
                cv2.circle(merged_image, (tmp_pairs[2] + show_image_.shape[1], tmp_pairs[3] + offset),
                           2, (0, 255, 0),
                           thickness=2)
            elif tmp_pairs[0] != -1 and tmp_pairs[1] != -1:
                cv2.circle(merged_image, (int(tmp_pairs[0]), int(tmp_pairs[1])),
                           2, (0, 255, 255),
                           thickness=2)
            elif tmp_pairs[2] != -1 and tmp_pairs[3] != -1:
                cv2.circle(merged_image, (tmp_pairs[2] + show_image_.shape[1], tmp_pairs[3] + offset),
                           2, (0, 255, 255),
                           thickness=2)

        return merged_image


if __name__ == '__main__':
    root = ""
    configfile = GLOBAL_CONFIG["default_path"] + r'/install/bin/data/CameraCalibration/resolve.ini'
    with open(configfile, "r") as file:
        tmp_time = file.readlines()
    file.close()
    for i in range(len(tmp_time)):
        pre = tmp_time[i]
        if pre == '\n':
            continue
        if pre.split(' ')[0] == 'LoadPath':
            root = pre.split(' ')[-1].split('\n')[0]

    parser = argparse.ArgumentParser("Configuration setting.")
    # parser.add_argument("--root", default=f"./Z0_DATA/samples")
    parser.add_argument("--root", default=root, help='root used from resolve.ini')
    # parser.add_argument("--ReadFolderName", default=f"/result_unmatched")
    parser.add_argument("--ReadFolderName", default=f"/")
    args = parser.parse_args()

    threshold_pixcenter = 10

    labeler = ShowLabelByHand(root=args.root, args=args)
    labeler.init_model()
    labeler.init_cv()
    labeler.init_vis()
    labeler.run()

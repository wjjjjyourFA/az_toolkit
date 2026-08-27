''' Created by sunyi /2022/4/20
 all rights reserved '''

import argparse
import os
from copy import deepcopy as copy

import cv2
import numpy as np
import open3d as o3d
from open3d import *
from toolkit.data_loader.read_calib import *
from toolkit.data_loader.read_json import *
from toolkit.fusion.projector import *
from toolkit.trans.trans_box3d import *
from toolkit.trans.trans_tensor import *
from toolkit.utils.misc import load_timestamp_image


class Show3D:
    def __init__(self, root, args):
        self.root = root
        self.prefixRead = root + args.ReadFolderName
        self.idx = 0
        self.LidarPath = os.path.join(self.root, 'lidar')
        self.ImagePath = os.path.join(self.root, 'image')
        self.LidarBoxPath = os.path.join(self.prefixRead, 'box3d')
        self.ImageBoxPath = os.path.join(self.prefixRead, 'box')
        self.InfraPath = os.path.join(self.root, 'infra')
        self.RadarPath = os.path.join(self.root, 'radar')

        """ data """
        self.timestamp_list = []
        self.ImageName = None
        self.image = None
        self.input_image = None
        self.ImageBoxFile = None
        self.image_box = []

        self.LidarName = None
        self.lidar = None
        self.input_lidar = None
        self.LidarBoxFile = None
        # box3d: (N, 7) [x, y, z, dx, dy, dz, heading], (x, y, z) is the box center
        self.lidar_box3d = []
        self.lidar_label = []
        # box3d: (N, 8)[label, {x, y, z} * 8]
        self.LidarBox = None

        self.InfraName = None
        self.infra = None
        self.input_infra = None
        self.infra_params_file = None

        self.RadarName = None
        self.radar = None
        self.input_radar = None

        """ calib """
        self.camara_params_file = args.camara_params_file
        self.p_camera = []
        self.radar_calib_file = None
        self.rt_radar = []
        self.check_params()

        """ show """
        self.vis = None
        self.pcd = None
        self.box_list = []

    def check_params(self):
        print("Checking Camera Intrinsic Params.....")
        if not os.path.exists(self.camara_params_file):
            raise ("No such:{0} exists... ".format(self.camara_params_file))

    def init_cv(self):
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Infra", cv2.WINDOW_NORMAL)

    def init_vis(self):
        '''-------Initializing the 3d visualizer-------'''
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        render_option = self.vis.get_render_option()
        render_option.point_size = 4
        render_option.background_color = np.asarray([0, 0, 0])
        self.pcd = o3d.geometry.PointCloud()

        for i in range(0, 100):
            line_set = o3d.geometry.LineSet()
            self.box_list.append(line_set)

        lines_box = np.array(
            [[0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 6], [2, 3], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]])
        colors = np.array([[220 / 255.0, 220 / 255.0, 220 / 255.0] for j in range(len(lines_box))])

        for obj_idx in range(0, len(self.box_list)):
            self.box_list[obj_idx].points = o3d.utility.Vector3dVector(np.zeros([8, 3]))
            self.box_list[obj_idx].lines = o3d.utility.Vector2iVector(lines_box)
            self.box_list[obj_idx].colors = o3d.utility.Vector3dVector(colors)
        '''-------Initializing the 3d visualizer-------'''

    def choose_timestamp(self):
        self.timestamp_list = load_timestamp_image(self.ImagePath)

    def load_raw_data(self, _idx):
        item = self.timestamp_list[_idx]

        self.ImageName = self.ImagePath + "/" + item + '.jpg'
        self.image = cv2.imread(self.ImageName)
        self.input_image = copy(self.image)

        self.ImageBoxFile = self.ImageBoxPath + "/" + item + '.txt'
        if os.path.exists(self.ImageBoxFile):
            self.load_camera_box(self.ImageBoxFile)

        self.InfraName = self.InfraPath + "/" + item + '.jpg'
        self.infra = cv2.imread(self.InfraName)
        self.input_infra = copy(self.infra)

        self.LidarName = self.LidarPath + "/" + item + '.bin'
        self.lidar = np.fromfile(self.LidarName, dtype=np.int32)
        self.input_lidar = self.lidar.reshape([-1, 4])

        self.LidarBoxFile = self.LidarBoxPath + "/" + item + '.json'
        if os.path.exists(self.LidarBoxFile):
            self.load_lidar_box(self.LidarBoxFile)

        self.RadarName = self.RadarPath + "/" + item + '.txt'
        self.radar = np.loadtxt(self.RadarName)
        # 每个型号的 radar 数据是不一样的
        ''' X Y V '''
        self.input_radar = self.radar.reshape([-1, 3])
        ''' X Y Z V '''
        # self.input_radar = self.radar.reshape([-1, 4])

        return True

    def load_calib_p(self):
        camera_calib_data = read_camera_calib(self.camara_params_file)
        self.p_camera = camera_calib_data["P"]
        radar_calib_data = read_radar_calib(self.radar_calib_file)
        self.rt_radar = radar_calib_data["RT"]

    def load_lidar_box(self, _lidar_box_file):
        ############### Show 3D Annotations #################
        self.lidar_box3d, self.lidar_label = read_box3d_json(self.LidarBoxFile)

    def show_lidar_box(self, _lines_box, _colors):
        if len(self.lidar_box3d):
            self.LidarBox = boxes_to_corners_3d(self.lidar_box3d)

            for obj_idx in range(0, len(self.LidarBox)):
                corner_point = ObtainCorners(self.LidarBox[obj_idx])
                self.box_list[obj_idx].points = o3d.utility.Vector3dVector(corner_point)
                self.box_list[obj_idx].lines = o3d.utility.Vector2iVector(_lines_box)
                self.box_list[obj_idx].colors = o3d.utility.Vector3dVector(_colors)

    def load_camera_box(self, _image_box_file):
        # np.load(_image_box_file)
        print("nothing doing now ......")

    def run(self):
        lines_box = np.array(
            [[0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 6], [2, 3], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]])
        colors = np.array([[0, 255, 0] for j in range(len(lines_box))])

        self.choose_timestamp()
        self.load_calib_p()

        while True:
            if self.idx >= len(self.timestamp_list):
                break
            show_count = "%d/%d" % (self.idx + 1, len(self.timestamp_list))

            if not self.load_raw_data(self.idx):
                continue

            ''' Image loading '''
            self.input_image = self.input_image.astype(np.float32) / 255.0
            gaussian = cv2.getGaussianKernel(ksize=15, sigma=1)
            self.input_image = cv2.filter2D(self.input_image, cv2.CV_32FC3, gaussian)

            ''' LiDAR loading '''
            # n X 4
            self.input_lidar = np.hstack((self.input_lidar[:, :1],
                                          self.input_lidar[:, :2],
                                          self.input_lidar[:, :3],
                                          self.input_lidar[:, 3:4] * 255))
            self.input_lidar = self.input_lidar.astype(np.int32)

            x = self.input_lidar[:, :1] / 100.
            y = self.input_lidar[:, 1:2] / 100.
            z = self.input_lidar[:, 2:3] / 100.
            scan = np.hstack((x, y, z))
            # scan = np.hstack((y, -x, z))

            ''' Proj '''
            index, image_coord = proj_uv(self.input_image, self.input_lidar, self.p_camera)
            for i in range(image_coord.shape[0]):
                cv2.circle(self.input_image, (image_coord[i, 0], image_coord[i, 1]), 1, (0, 255, 255), 1)
            cv2.imshow("Image", self.input_image)

            """ radar 2 lidar """
            tmp_radar = self.trans_radar_to_lidar(self.input_radar, self.rt_radar)

            """ radar || lidar """
            scan = np.concatenate([scan, tmp_radar[:, :3] / 100], axis=0)

            """ """
            self.pcd.points = o3d.utility.Vector3dVector(np.asarray(scan))

            color_lidar = np.array([[0.5, 0.5, 0.5]]).repeat(self.input_lidar.shape[0], axis=0)
            s_color = self.input_image[image_coord[:, 1], image_coord[:, 0]]
            s_color[:, [0, 2]] = s_color[:, [2, 0]]
            color_lidar[index, :] = s_color

            color_radar = np.array([[1, 0, 0]]).repeat(self.input_radar.shape[0], axis=0)

            color = np.concatenate([color_lidar, color_radar], axis=0)
            self.pcd.colors = o3d.utility.Vector3dVector(np.asarray(color))

            """ """
            self.show_lidar_box(lines_box, colors)

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

            """ """
            self.show_radar_image(self.input_radar)

            """ """
            if self.input_infra is not None:
                cv2.imshow("Infra", self.input_infra)
            cv2.waitKey(1)

    def show_radar_image(self, points):
        radar_image = np.zeros((768, 1024, 3), np.uint8)
        for i in range(0, len(points)):
            x = int(points[i, 1] / 20 + 1024 / 2)
            y = int(768 / 2 - points[i, 0] / 20)
            cv2.circle(radar_image, (x, y), 1, (0, 255, 0), 2)
        cv2.namedWindow("radar", cv2.WINDOW_GUI_NORMAL)
        cv2.imshow("radar", radar_image)

    def trans_radar_to_lidar(self, _radar, _p):
        ''' X Y V ==> x y z=0 '''
        # [x,y,z]
        points = np.concatenate([_radar[:, 0:2], np.zeros(_radar.shape[0]).reshape(-1, 1)],
                                axis=1)
        # [x,y,z,1]
        points = np.pad(points.transpose(1, 0), ([0, 1], [0, 0]),
                        constant_values=1.0, mode="constant").transpose(1, 0)

        points = np.matmul(_p, points.transpose(1, 0)).transpose()

        return points


if __name__ == '__main__':
    # configfile = './../Z0_Data/resolve.ini'
    # with open(configfile, "r") as file:
    #     tmp_time = file.readlines()
    # file.close()
    # for i in range(len(tmp_time)):
    #     pre = tmp_time[i]
    #     if pre == '\n':
    #         continue
    #     if pre.split(' ')[0] == 'LoadPath':
    #         root = pre.split(' ')[-1].split('\n')[0]

    root = "./../data/samples_common"
    camara_params_file = "./../data/samples_common/calib/KK.ini"

    parser = argparse.ArgumentParser("Configuration setting.")
    parser.add_argument("--root", default=root, help='root used from resolve.ini')
    parser.add_argument("--camara_params_file", default=camara_params_file, help='calib.ini')
    parser.add_argument("--ReadFolderName", default=f"/result_unmatched")
    args = parser.parse_args()

    show_3d = Show3D(root=args.root, args=args)
    show_3d.init_cv()
    show_3d.init_vis()
    show_3d.run()

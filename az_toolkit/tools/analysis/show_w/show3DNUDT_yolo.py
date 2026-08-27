'''Created by sunyi /2022/4/20
all rights reserved'''
import argparse
import os
from copy import deepcopy as copy

import cv2
import numpy as np
import open3d as o3d
from Object_showme import Annotation_func
from Object_showme_yolo import Annotation_func_yolo
from open3d import *
from show3DinRangeImage import show_3DinRangeImage
from utils import readjson, read_cameraCalib, Proj3D2D

Show_annotation = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root',
                        default='/media/xie/WD_Main/Dataset_JCJQ/沙地/2023-07-10-1-DONE/',
                        help='The path of the image folder')
    config = parser.parse_args()
    dataroot = config.root

    lidar_path = dataroot + "LIDAR/"
    image_path = dataroot + "IMAGE/"
    imageBox_path = dataroot + "IMGBox/"
    infra_path = dataroot + "INFRA/"
    radar_path = dataroot + "Radar/"
    lidarbox_path = dataroot + "LIDARBox/"

    imageBox_yolo_path = dataroot + "YOLOlabel/"

    calib_path = dataroot + "/Calib/AR0231.ini"
    calib_radarpath = dataroot + "/Calib/Radar_new.ini"
    print(">>>>>>loading calibration files......")
    Projection_matrix = read_cameraCalib(calib_path)
    radarPOSE_EXIST = True
    if os.path.exists(calib_radarpath):
        radar_pose = np.loadtxt(calib_radarpath, delimiter=',')
    else:
        radarPOSE_EXIST = False

    filelist = os.listdir(image_path)
    Timestamplist = []
    for i in range(0, len(filelist)):
        tmpname = filelist[i]
        if tmpname.split('.')[-1] == 'jpg' or tmpname.split('.')[-1] == 'jpeg' or tmpname.split('.')[-1] == 'png':
            timestamp = tmpname.split('.')[0]
            Timestamplist.append(timestamp)
    print(">>>>>>>>>>>>>>>>>>>>>>>{0} file num:{1}".format(dataroot.split("/")[-2], len(Timestamplist)))
    Timestamplist.sort()

    Show3D = True
    if Show3D:
        '''-------Initializing the 3d visualizer-------'''
        vis = o3d.visualization.Visualizer()
        vis.create_window(width=800, height=600, left=800, top=150)
        pcd = o3d.geometry.PointCloud()

        boxlist = []
        for i in range(0, 100):
            line_set = o3d.geometry.LineSet()
            boxlist.append(line_set)
        '''-------------Open3d:pcd---------------'''

    for fileidx in range(0, len(Timestamplist)):
        infraname = infra_path + Timestamplist[fileidx] + ".jpg"
        radarname = radar_path + Timestamplist[fileidx] + ".txt"
        if os.path.exists(radarname):
            radar_data = np.loadtxt(radarname)
        infraImage = cv2.imread(infraname)
        LidarBoxname = lidarbox_path + Timestamplist[fileidx] + '.json'
        lidar_name = lidar_path + Timestamplist[fileidx] + ".bin"
        if Show_annotation and os.path.exists(LidarBoxname):
            ###############Show 3D annotations#################
            boxes3d, label = readjson(LidarBoxname)
            show_3DinRangeImage(lidar_name, LidarBoxname)

        p = Projection_matrix
        p = p.reshape((3, 4))
        image_name = image_path + Timestamplist[fileidx] + '.jpg'
        image = cv2.imread(image_name)
        imageboxname = imageBox_path + Timestamplist[fileidx] + '.txt'
        imageboxyoloname = imageBox_yolo_path + Timestamplist[fileidx] + '.txt'
        if Show_annotation and os.path.exists(imageboxname):
            Annotation_func(image_name, imageboxname)
        elif Show_annotation and os.path.exists(imageboxyoloname):
            Annotation_func_yolo(image_name, imageboxyoloname)

        '''Image loading'''
        image = image.astype(np.float32) / 255.0
        gaussian = cv2.getGaussianKernel(ksize=15, sigma=1)
        image = cv2.filter2D(image, cv2.CV_32FC3, gaussian)
        showim_RGB = copy(image)
        '''LiDAR loading'''
        lidarpoint = np.fromfile(lidar_name, dtype=np.int32)
        pointnum = lidarpoint.shape[0] // 4
        lidar = lidarpoint[:4 * pointnum]
        lidarpoint = lidarpoint.reshape((-1, 4))
        x = lidarpoint[:, :1] * 10.
        y = lidarpoint[:, 1:2] * 10.
        z = lidarpoint[:, 2:3] * 10.
        lidarpoint = np.hstack((x, y, z, lidarpoint[:, 3:4] * 255))
        lidarpoint = lidarpoint.astype(np.int32)
        # lidarpoint = np.array(lidarpoint).reshape(-1, 4)
        # lidarpoint = lidarpoint[lidarpoint[:,0]>0,:]
        # lidarpoint = lidarpoint[lidarpoint[:,2]>-15000,:]
        lidarpoint = lidarpoint[:, 0:3]

        '''Projectig'''
        index, imagecoord = Proj3D2D(lidarpoint, p, image)

        x = lidarpoint[:, :1] / 1000.
        y = lidarpoint[:, 1:2] / 1000.
        z = lidarpoint[:, 2:3] / 1000.
        scan = np.hstack((x, y, z))
        if os.path.exists(radarname):
            tmp = np.concatenate([radar_data[:, 0:2], np.zeros(radar_data.shape[0]).reshape(-1, 1)], axis=1)
            # radar2lidar = lidar_pose@radar_pose
            if radarPOSE_EXIST:
                radar2lidar = radar_pose
                tmp = np.pad(tmp.transpose(1, 0), ([0, 1], [0, 0]), constant_values=1.0, mode="constant").transpose(1,
                                                                                                                    0)
                tmp2 = tmp.transpose(1, 0)
                tmp3 = np.matmul(radar2lidar, tmp2).transpose()
                # tmp3=tmp3[:,:3]@np.array([[0,-1,0],[1,0,0],[0,0,1]])
                scan = np.concatenate([scan, tmp3[:, :3] / 100], axis=0)
        pcd.points = o3d.utility.Vector3dVector(np.asarray(scan))

        color = np.array([[0.5, 0.5, 0.5]]).repeat(lidarpoint.shape[0], axis=0)
        co = image[imagecoord[:, 1], imagecoord[:, 0]]
        co[:, [0, 2]] = co[:, [2, 0]]
        color[index, :] = co

        if os.path.exists(radarname):
            center = tmp[:, :2]
            radar_img = np.zeros((768, 1024, 3), np.uint8)
            for i in range(0, len(center)):
                x = int(center[i:i + 1, 1] / 20 + 1024 / 2)
                y = int(768 / 2 - center[i:i + 1, 0] / 20 + 200)
                cv2.circle(radar_img, (x, y), 1, (0, 255, 0), 2)
            cv2.namedWindow("radar", cv2.WINDOW_GUI_NORMAL)
            # cv2.moveWindow("radar1", 60, 700)
            cv2.imshow("radar", radar_img)
            color_radar = np.array([[1, 0, 0]]).repeat(radar_data.shape[0], axis=0)
            color = np.concatenate([color, color_radar], axis=0)
        pcd.colors = o3d.utility.Vector3dVector(np.asarray(color))

        # pcd = pcd.voxel_down_sample(voxel_size=0.02)
        # vis.clear_geometries()
        if fileidx == 0:
            if Show_annotation and os.path.exists(LidarBoxname):
                for i in range(0, len(boxlist)):
                    vis.add_geometry(boxlist[i])
            vis.add_geometry(pcd)
            # vis.run()  # block show
        else:
            vis.update_geometry(pcd)
            if Show_annotation and os.path.exists(LidarBoxname) and len(boxes3d) > 0:
                # print(" {0}".format(len(boxes3d)))
                for i in range(0, len(boxlist)):
                    vis.update_geometry(boxlist[i])

            else:
                for i in range(0, len(boxlist)):
                    vis.update_geometry(boxlist[i])

            # vis.destroy_window()
        '''-------------Open3d:pcd---------------'''
        vis.update_geometry(pcd)
        vis.poll_events()
        vis.update_renderer()
        '''--------------------Open3d:pcd------------------'''

        for i in range(imagecoord.shape[0]):
            cv2.circle(showim_RGB, (imagecoord[i, 0], imagecoord[i, 1]), 1, (0, 255, 255), 1)
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.imshow("image", image)
        cv2.namedWindow("image projection", cv2.WINDOW_NORMAL)
        cv2.imshow("image projection", showim_RGB)
        if infraImage is not None:
            cv2.namedWindow("infra image", cv2.WINDOW_NORMAL)
            cv2.imshow("infra image", infraImage)
        cv2.waitKey(10)

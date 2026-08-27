'''Created by sunyi /2022/4/20
all rights reserved'''
import os
from copy import deepcopy as copy

import cv2
import numpy as np
import open3d as o3d
from Object_showme import Annotation_func
from open3d import *
from show3DinRangeImage import show_3DinRangeImage
from utils import readjson, read_cameraCalib, boxes_to_corners_3d, ObtainCorner, Proj3D2D

Show_annotation = True
if __name__ == '__main__':
    dataroot = "/home/sunyi/DATASETs/DevelopKit/toolkit_nudt/2022-04-18-3-DONE/"
    lidar_path = dataroot + "LIDAR/"
    image_path = dataroot + "IMAGE/"
    infra_path = dataroot + "INFRA/"
    radar_path = dataroot + "/Radar/"
    lidarbox_path = dataroot + "LIDARBox/"

    calib_path = dataroot + "/Calib/Infra.ini"
    calib_radarpath = dataroot + "/Calib/radar.ini"

    print(">>>>>>loading calibration files......")
    with open(calib_path, "r") as f:
        while (True):
            head = f.readline().strip('\n')
            # print(head)
            if head == 'P':
                tmplist = []
                for i in range(0, 3):
                    linestr = (f.readline().strip('\n')).split(' ')
                    tmplist.append([float(linestr[0]), float(linestr[1]), float(linestr[2]), float(linestr[3])])
                break

        Projection_matrix = np.stack(tmplist)

    radar_pose = np.loadtxt(calib_radarpath, delimiter=',')

    filelist = os.listdir(image_path)
    Timestamplist = []
    for i in range(0, len(filelist)):
        tmpname = filelist[i]
        if tmpname.split('.')[-1] == 'jpg' or tmpname.split('.')[-1] == 'jpeg' or tmpname.split('.')[-1] == 'png':
            timestamp = tmpname.split('.')[0]
            Timestamplist.append(timestamp)
    print(">>>>>>>>>>>>>>>>>>>>>>>Total file:{0}".format(len(Timestamplist)))
    Timestamplist.sort()

    Show3D = True
    if Show3D:
        '''-------Initializing the 3d visualizer-------'''
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        render_option = vis.get_render_option()
        render_option.point_size = 4
        render_option.background_color = np.asarray([0 / 255.0, 0 / 255.0, 0 / 255.0])
        pcd = o3d.geometry.PointCloud()
        '''-------------Open3d:pcd---------------'''
        boxlist = []
        for i in range(0, 100):
            line_set = o3d.geometry.LineSet()
            boxlist.append(line_set)
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.moveWindow("image", 50, 50)
    cv2.namedWindow("infraimage", cv2.WINDOW_NORMAL)
    cv2.moveWindow("infraimage", 50, 500)
    for fileidx in range(0, len(Timestamplist)):
        infraname = infra_path + Timestamplist[fileidx] + ".jpg"
        radarname = radar_path + Timestamplist[fileidx] + ".txt"
        LidarBoxname = lidarbox_path + Timestamplist[fileidx] + '.json'
        radar_data = np.loadtxt(radarname)
        infraImage = cv2.imread(infraname)
        infraImage = infraImage.astype(np.float32) / 255.0
        lidar_name = lidar_path + Timestamplist[fileidx] + ".bin"

        if Show_annotation and os.path.exists(LidarBoxname):
            ###############Show 3D annotations#################
            boxes3d, label = readjson(LidarBoxname)
            show_3DinRangeImage(lidar_name, LidarBoxname)
            if len(boxes3d):
                corners = boxes_to_corners_3d(boxes3d)
                lines_box = np.array(
                    [[0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 6], [2, 3], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]])

                colors = np.array([[220 / 255.0, 220 / 255.0, 220 / 255.0] for j in range(len(lines_box))])
                for obidx in range(0, len(boxlist)):
                    boxlist[obidx].points = o3d.utility.Vector3dVector(np.zeros([8, 3]))
                    boxlist[obidx].lines = o3d.utility.Vector2iVector(lines_box)
                    boxlist[obidx].colors = o3d.utility.Vector3dVector(colors)

                colors = np.array([[0, 255, 0] for j in range(len(lines_box))])
                for obidx in range(0, len(boxes3d)):
                    # print(obidx+1)
                    cornerPoint = ObtainCorner(corners[obidx])
                    tmp = copy(cornerPoint[:, 0])
                    cornerPoint[:, 0] = -cornerPoint[:, 1]
                    cornerPoint[:, 1] = tmp
                    boxlist[obidx].points = o3d.utility.Vector3dVector(cornerPoint)
                    boxlist[obidx].lines = o3d.utility.Vector2iVector(lines_box)
                    boxlist[obidx].colors = o3d.utility.Vector3dVector(colors)
            else:
                lines_box = np.array(
                    [[0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 6], [2, 3], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]])
                colors = np.array([[220 / 255.0, 220 / 255.0, 220 / 255.0] for j in range(len(lines_box))])
                for obidx in range(0, len(boxlist)):
                    boxlist[obidx].points = o3d.utility.Vector3dVector(np.zeros([8, 3]))
                    boxlist[obidx].lines = o3d.utility.Vector2iVector(lines_box)
                    boxlist[obidx].colors = o3d.utility.Vector3dVector(colors)
        else:
            lines_box = np.array(
                [[0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 6], [2, 3], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]])
            colors = np.array([[220 / 255.0, 220 / 255.0, 220 / 255.0] for j in range(len(lines_box))])
            for obidx in range(0, len(boxlist)):
                boxlist[obidx].points = o3d.utility.Vector3dVector(np.zeros([8, 3]))
                boxlist[obidx].lines = o3d.utility.Vector2iVector(lines_box)
                boxlist[obidx].colors = o3d.utility.Vector3dVector(colors)

        p = Projection_matrix
        p = p.reshape((3, 4))
        image_name = image_path + Timestamplist[fileidx] + '.jpg'
        image = cv2.imread(image_name)
        image = image.astype(np.float32) / 255.0
        gaussian = cv2.getGaussianKernel(ksize=15, sigma=1)
        image = cv2.filter2D(image, cv2.CV_32FC3, gaussian)
        showim_RGB = copy(image)

        lidarpoint = np.fromfile(lidar_name, dtype=np.int32)
        pointnum = lidarpoint.shape[0] // 4
        lidar = lidarpoint[:4 * pointnum]
        lidarpoint = lidarpoint.reshape((-1, 4))
        x = lidarpoint[:, :1] * 10.
        y = lidarpoint[:, 1:2] * 10.
        z = lidarpoint[:, 2:3] * 10.
        lidarpoint = np.hstack((x, y, z, lidarpoint[:, 3:4] * 255))
        lidarpoint = lidarpoint.astype(np.int32)

        lidarpoint = np.array(lidarpoint).reshape(-1, 4)
        lidarpoint = lidarpoint[lidarpoint[:, 0] > 0, :]
        lidarpoint = lidarpoint[lidarpoint[:, 2] > -15000, :]
        lidarpoint = lidarpoint[:, 0:3]

        ones_metrics = np.ones((lidarpoint.shape[0], 1))
        lidarpoint = np.concatenate((lidarpoint, ones_metrics), axis=1)
        pts_2d = np.dot(p, np.transpose(lidarpoint))
        pts_2d = np.transpose(pts_2d)
        pts_2d[:, 0] /= pts_2d[:, 2]
        pts_2d[:, 1] /= pts_2d[:, 2]
        x = pts_2d[:, 0].astype(np.int).reshape((-1, 1))

        y = pts_2d[:, 1].astype(np.int).reshape((-1, 1))
        imagecoord = np.concatenate((x, y), axis=1)

        index = (imagecoord[:, 0] > 0) & (imagecoord[:, 0] < infraImage.shape[1]) & (imagecoord[:, 1] > 0) & (
                imagecoord[:, 1] < infraImage.shape[0])
        imagecoord = imagecoord[index, :]

        x = lidarpoint[:, :1] / 1000.
        y = lidarpoint[:, 1:2] / 1000.
        z = lidarpoint[:, 2:3] / 1000.
        scan = np.hstack((x, y, z))
        if os.path.exists(radarname):
            tmp = np.concatenate([radar_data[:, 0:2], np.zeros(radar_data.shape[0]).reshape(-1, 1)], axis=1)
            # radar2lidar = lidar_pose@radar_pose
            radar2lidar = radar_pose
            tmp = np.pad(tmp.transpose(1, 0), ([0, 1], [0, 0]), constant_values=1.0, mode="constant").transpose(1, 0)
            tmp2 = tmp.transpose(1, 0)
            tmp3 = np.matmul(radar2lidar, tmp2).transpose()
            # tmp3=tmp3[:,:3]@np.array([[0,-1,0],[1,0,0],[0,0,1]])
            scan = np.concatenate([scan, tmp3[:, :3] / 100], axis=0)
        pcd.points = o3d.utility.Vector3dVector(np.asarray(scan))

        color = np.array([[0.1, 0.1, 0.1]]).repeat(lidarpoint.shape[0], axis=0)
        co = infraImage[imagecoord[:, 1], imagecoord[:, 0]]
        co[:, [0, 2]] = co[:, [2, 0]]
        color[index, :] = co

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
            vis.run()  # block show
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
        cv2.imshow("image", showim_RGB)
        if infraImage is not None:
            cv2.imshow("infraimage", infraImage)
        cv2.waitKey(1)

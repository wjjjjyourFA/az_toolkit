import numpy as np

from A3_Config.config import Config as Cfg
from T0_Tools.trans.trans_box3d import *


def read_3dbox_result_24d(filename : str):
    """
        7 -------- 4
       /|         /|
      6 -------- 5 .
      | |        | |
      . 3 -------- 0
      |/         |/
      2 -------- 1
    Args:
        box3d:  (N, 8) [label, {x, y, z}*8], {x, y, z} is the box points
    """
    ''' load detection result '''
    result = []
    with open(filename) as f:
        while True:
            tmp = f.readline().strip('\n')
            if len(tmp.split(',')) < 25:  # 8 points
                break
            a = np.stack(tmp.split(',')).astype(np.float32)
            if abs(a[1]) > Cfg.ObjDis:  # Front Left Up
                continue
            result.append(a)
    return result


def read_3dbox_result_7d(filename : str):
    ''' load detection result '''
    result = []
    with open(filename) as f:
        while True:
            tmp = f.readline().strip('\n')
            if len(tmp.split(',')) < 8:
                break
            # 7d 格式
            a = np.stack(tmp.split(',')).astype(np.float32)
            # 转为 8points-24d 格式，是为了与真值标定时距离筛选保持一致，append的依然是 7d 格式
            a = convert_box_7d_2_24d(a)
            if abs(a[1]) > Cfg.ObjDis or abs(a[2]) > Cfg.ObjDis:
                continue
            result.append(a)
    return result


def read_box_result(filename : str):
    ''' load detection result '''
    result = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    # way 1
    # for i in range(len(lines)):
    #     # bbox = np.stack(lines[i].strip('\n').split(" ")).astype(np.int32)
    #     # ERROR: invalid literal for int() with base 10: '0.0'
    #     bbox = np.stack(lines[i].strip('\n').split(" ")).astype(np.float32).astype(np.int32)
    #
    #     result.append([bbox[0], bbox[1], bbox[2], bbox[3], bbox[4]])

    # way 2
    for line in lines:
        bbox = np.array(line.strip().split(" "), dtype=np.float32)
        # Ensure the coordinates are integers
        bbox = bbox.astype(np.int32)
        result.append(bbox)

    return result
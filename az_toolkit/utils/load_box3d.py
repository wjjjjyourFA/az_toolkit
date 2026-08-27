from az_toolkit.utils.trans_box3d import *

try:
    # 先尝试导入运行目录下的 custom_config.py
    from custom_config import CustomConfig as Cfg
except ImportError:
    # 如果没有，就导入工具包里的 custom_config.py
    from az_toolkit.custom_config.default_config import CustomConfig as Cfg


def read_box3d_result_24d(filename: str):
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


def read_box3d_result_7d(filename: str):
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
            a = box3d_convert_7d_to_24d(a)
            if abs(a[1]) > Cfg.ObjDis or abs(a[2]) > Cfg.ObjDis:
                continue
            result.append(a)
    return result

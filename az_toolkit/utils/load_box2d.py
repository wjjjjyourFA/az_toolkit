from az_toolkit.utils.trans_box3d import *

try:
    # 先尝试导入运行目录下的 custom_config.py
    from custom_config import CustomConfig as Cfg
except ImportError:
    # 如果没有，就导入工具包里的 custom_config.py
    from az_toolkit.custom_config.default_config import CustomConfig as Cfg


def read_box2d_result(filename: str):
    """Load 2D detection results, first column as cls_id."""
    result = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    # way 1
    # for i in range(len(lines)):
    #     # bbox = np.stack(lines[i].strip('\n').split(" ")).astype(np.int32)
    #     # ERROR: invalid literal for int() with base 10: '0.0'
    #     # 先把字符串转 float，再转 int
    #     bbox = np.stack(lines[i].strip('\n').split(" ")).astype(np.float32).astype(np.int32)
    #
    #     result.append([bbox[0], bbox[1], bbox[2], bbox[3], bbox[4]])

    # way 2
    """ # 原始: [ID, X1, Y1, X2, Y2]
        # 目标: [X1, Y1, X2, Y2, ID] """
    # id 转 int，bbox 坐标 保留 float  ==> 兼容 yolo
    for line in lines:
        bbox = np.array(line.strip().split(" "), dtype=np.float32)
        # Ensure the coordinates are integers
        # bbox = bbox.astype(np.int32)

        # 只将 cls_id 转 int
        bbox[0] = int(bbox[0])

        # 重排顺序: [x1, y1, x2, y2, id]
        reordered = np.array([bbox[1], bbox[2], bbox[3], bbox[4], bbox[0]], dtype=np.float32)

        result.append(reordered)

    return result

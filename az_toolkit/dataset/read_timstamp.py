# Copyright (c) FSZN. All rights reserved.
"""
手动配置需要读取哪些传感器数据的时间戳
将结果，按规则命名后，保存到指定文件夹
"""

try:
    # 作为包导入时
    from .common.misc import *
    from .extract.extract_timestamp import *
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.common.misc import *
    from az_toolkit.extract.extract_timestamp import *
    from az_toolkit.config import GLOBAL_CONFIG


def main(root="", fixedTsFile=False):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return

    timestamp_path = mkdir_folder(root, "timestamp")

    if fixedTsFile:
        """ 固定输出文件 """
        lidar_ts_file = os.path.join(timestamp_path, "lidar_timestamp.txt")
        image_ts_file = os.path.join(timestamp_path, "image_timestamp.txt")
        # infra_ts_file = os.path.join(timestamp_path, "infra_timestamp.txt")
        # radar_ts_file = os.path.join(timestamp_path, "radar_timestamp.txt")
        # star_ts_file = os.path.join(timestamp_path, "star_timestamp.txt")

        extract_timestamp(root, "lidar", ".bin", lidar_ts_file)
        # extract_timestamp(root, "lidar", ".pcd", lidar_ts_file)
        extract_timestamp(root, "image", ".jpg", image_ts_file)
        # extract_timestamp(root, "infra", ".jpg", infra_ts_file)
        # extract_timestamp(root, "radar", ".txt", radar_ts_file)
        # extract_timestamp(root, "star", ".jpg", star_ts_file)
    else:
        """ 使用固定命名文件 """
        extract_timestamp_fixed(root, "lidar", ".bin", timestamp_path)
        # extract_timestamp_fixed(root, "lidar", ".pcd", timestamp_path)
        extract_timestamp_fixed(root, "image", ".jpg", timestamp_path)
        # extract_timestamp_fixed(root, "radar_4d", ".txt", timestamp_path)
        # extract_timestamp_fixed(root, "radar_4d_1", ".txt", timestamp_path)
        # extract_timestamp_fixed(root, "radar_4d_2", ".txt", timestamp_path)
        # extract_timestamp_fixed(root, "radar_4d_3", ".txt", timestamp_path)


if __name__ == '__main__':
    # debug
    main(GLOBAL_CONFIG["simple_path"] + "/samples_common")
    # main("/media/jojo/WorkStation/test/yunjian/2026-02-05/2026-02-05-15-00-01")

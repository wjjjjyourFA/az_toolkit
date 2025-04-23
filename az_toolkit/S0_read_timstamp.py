import os
import sys
import argparse


if __package__ is None:
    # 作为独立脚本运行
    from utils.misc import *
    from extract.extract_timestamps import *
else:
    # 作为包导入
    from .utils.misc import *
    from .extract.extract_timestamps import *


def main(root="./../../test_data/samples_common"):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return
    timestamp_path = mkdir_folder(root, "/timestamp/")

    _flag = False
    if _flag:
        """ 自己设置输出文件 """
        lidar_ts_file = timestamp_path + "lidar_timestamp.txt"
        image_ts_file = timestamp_path + "image_timestamp.txt"
        # infra_ts_file = timestamp_path + "infra_timestamp.txt"
        # radar_ts_file = timestamp_path + "radar_timestamp.txt"
        # star_ts_file = timestamp_path + "star_timestamp.txt"

        extract_timestamps(root, "lidar", ".bin", lidar_ts_file)
        extract_timestamps(root, "image", ".jpg", image_ts_file)
        # extract_timestamps(root, "infra", ".jpg", infra_ts_file)
        # extract_timestamps(root, "radar", ".txt", radar_ts_file)
        # extract_timestamps(root, "star", ".jpg", star_ts_file)
    else:
        """ 使用固定命名文件 """
        extract_timestamps_fixed(root, "lidar", ".bin", timestamp_path)
        extract_timestamps_fixed(root, "image", ".jpg", timestamp_path)


if __name__ == '__main__':
    # main()
    main("/media/jojo/WorkStation/test/right")
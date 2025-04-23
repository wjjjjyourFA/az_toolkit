'''Extracting the files by a given interval'''
# import cv2

'''Created by Sy/2022/04/18'''
import os
import argparse
import shutil


try:
    # 作为包导入时
    from .utils.misc import *
    from .utils.auto_process import *
except ImportError:
    # 作为独立脚本运行
    from utils.misc import *
    from utils.auto_process import *


#Source
#RGB:undistor_Image
#Infra:Infra
#Lidar:LidarRS128
#StarLight:Star
#Radar:Radar

#Target Folder:
#RGB:IMAGE
#Infra:INFRA
#Lidar:LIDAR
#StarLight:STAR
#Radar:Radar


class Extractor:
    def __init__(self, args):
        self.prefix = args.data_root
        self.PrefixSave = args.target_folder
        self.args = args
        self.time_interval = args.TimeInterval
        self.LidarPath = os.path.join(self.prefix, 'lidar')
        self.ImagePath = os.path.join(self.prefix, 'image')
        self.InfraPath = os.path.join(self.prefix, 'infra')
        self.StarPath = os.path.join(self.prefix, 'star')
        self.RadarPath = os.path.join(self.prefix, 'radar')
        self.timestamp_path = mkdir_folder(self.prefix, "/timestamp/")
        self.mkdir_folder()
        self.tar_lidar_path = self.set_path(self.PrefixSave, "lidar")
        self.tar_image_path = self.set_path(self.PrefixSave, "image")
        self.tar_infra_path = self.set_path(self.PrefixSave, "infra")
        self.tar_star_path = self.set_path(self.PrefixSave, "star")
        self.tar_radar_path = self.set_path(self.PrefixSave, "radar")

    def mkdir_folder(self):
        ensure_dir(self.LidarPath)
        ensure_dir(self.ImagePath)
        # ensure_dir(self.InfraPath)
        # ensure_dir(self.StarPath)
        # ensure_dir(self.RadarPath)

    def set_path(self, source_path, sensor_name):
        target_path = os.path.join(source_path, f'{sensor_name}')
        ensure_dir(target_path)
        return target_path

    def run(self):
        """ way 1
         通过图像的时间戳文本获取时间戳 """
        # image_timestamp_list = load_timestamp(self.timestamp_path + "image_timestamp.txt", "image")
        """ way 2 
         在图像数据路径自动获取时间戳 """
        image_timestamp_list = load_timestamp_image(self.ImagePath)

        self.extract_files_interval(image_timestamp_list, self.prefix, "lidar", ".bin", self.PrefixSave, self.time_interval)
        self.extract_files_interval(image_timestamp_list, self.prefix, "image", ".jpg", self.PrefixSave, self.time_interval)
        self.extract_files_interval(image_timestamp_list, self.prefix, "infra", ".jpg", self.PrefixSave, self.time_interval)
        self.extract_files_interval(image_timestamp_list, self.prefix, "star", ".jpg", self.PrefixSave, self.time_interval)
        self.extract_files_interval(image_timestamp_list, self.prefix, "radar", ".txt", self.PrefixSave, self.time_interval)

    def extract_files_interval(self, timestamp_list, source_dirs, sensor_name, file_extension, target_dirs, time_interval):
        if not timestamp_list:
            raise ValueError("Error timestamp list")

        initial_timestamp = int(timestamp_list[0]) // 100 * 100

        for i, timestamp in enumerate(timestamp_list):
            current_timestamp = int(timestamp) // 100 * 100
            # 检查是否需要复制文件
            if (current_timestamp - initial_timestamp) >= time_interval:
                original_filename = os.path.join(
                    source_dirs, sensor_name, str(timestamp) + file_extension
                )
                target_filename = os.path.join(target_dirs, sensor_name, str(timestamp) + file_extension)

                if 0:
                    original_filename = source_dirs + "/" + sensor_name + "/" + '%015ld' % (timestamp) + file_extension
                    target_filename = target_dirs + "/" + sensor_name + "/" + '%015ld' % (timestamp) + file_extension

                try:
                    shutil.copyfile(original_filename, target_filename)
                except FileNotFoundError as e:
                    print(f"File not found: {original_filename}. Skipping.")
                except Exception as e:
                    print(f"Error moving or renaming file: {e}")

                # 更新初始时间戳
                initial_timestamp = int(timestamp)


if __name__ == '__main__':
    """ 将数据集中的数据按一定的格式和时间间隔，组成 another COM dataset
     各数据已经统一时间戳命名 """
    parser = argparse.ArgumentParser("Configuration setting.")
    parser.add_argument('--TimeInterval', default=200, help="ms")
    parser.add_argument('--data_root', default='', help='the root of data')
    parser.add_argument('--target_folder', default="")
    args = parser.parse_args()
    print(">>> Extracting the Multi-modal files.....")

    # debug
    # args.data_root = "./../../data_label/data/samples_common1"
    # args.target_folder = "./../../data_label/data/samples_common2"
    #
    # extractor = Extractor(args=args)
    # extractor.run()

    """ auto for data root folder """
    root_paths = ["./../../data_label/data"]
    process_folders(root_paths, target_suffix="_extracted", args=args, process_class=Extractor)

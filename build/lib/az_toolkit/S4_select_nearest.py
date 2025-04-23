import os
import shutil


try:
    # 作为包导入时
    from .utils.misc import *
    from .extract.extract_timestamps import *
except ImportError:
    # 作为独立脚本运行
    from utils.misc import *
    from extract.extract_timestamps import *


""" BUG，没有按时间戳大小顺序保存时间戳 
 20240614 修复 """
""" 以 f_select 中读取数据列表获取时间戳
 从 f_caught 中获取最接近的数据的时间戳 """


def match_and_copy_files_by_timestamp(source_timestamps, source_folder, target_folder, target_timestamps, file_extension, time_threshold=55):
    _read_ts = load_timestamp(source_timestamps)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 获取带挑选文件的列表
    _files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    write_ts_tmp = [os.path.splitext(f)[0] for f in _files]
    # 将字符串列表转换为整数列表
    write_ts_tmp = [int(ts) for ts in write_ts_tmp]
    write_ts_tmp.sort()

    # 寻找每个图像时间戳的最近点云时间戳
    matched_nearest_timestamp_list, _ = match_timestamp_nearest(_read_ts, write_ts_tmp, time_threshold)

    # 如果找到匹配的点云文件
    for i, timestamp in enumerate(matched_nearest_timestamp_list):
        original_filename = os.path.join(source_folder, str(timestamp) + file_extension)
        save_data_path = os.path.join(target_folder, f'{timestamp}{file_extension}')

        shutil.copyfile(original_filename, save_data_path)

    # 将匹配的点云时间戳保存到C.txt
    with open(target_timestamps, 'w') as file:
        for ts in matched_nearest_timestamp_list:
            file.write(f"{ts}\n")


if __name__ == '__main__':
    """ 定义基准文件夹路径 """
    prefix_path = "./../../data_label/data/samples_common"
    data_file_path = prefix_path + '/image'
    source_timestamps = prefix_path + "/timestamp/" + 'image_timestamp.txt'

    """ 定义被挑选的文件夹路径 """
    source_folder = "./../../data_label/data/samples_common/lidar"
    target_folder = prefix_path + "/lidar" + "_extracted"
    target_timestamps = prefix_path + "/timestamp/" + 'lidar_timestamp.txt'

    """ 如果还没有生成 image_timestamp.txt
     手动读取列表生成对应的 _timestamp.txt """
    match_and_copy_files_by_timestamp(
        source_timestamps=source_timestamps,
        source_folder=source_folder,
        target_folder=target_folder,
        target_timestamps=target_timestamps,
        file_extension=".bin",  # .bin .pcd .jpg .png
        time_threshold=55
    )
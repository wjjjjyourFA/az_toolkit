import os
from os.path import join
import numpy as np
import glob
import shutil


def ensure_dir(directory):
    """ 确保文件路径存在 """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")
    else:
        print(f"Directory {directory} already exists.")


def mkdir_folder(directory, folder_name="/"):
    # if not os.path.isdir(directory):
    #     print(f"❌ Root path does not exist: {directory}")
    #     return
    tar_path = directory + folder_name
    # tar_path = os.path.join(directory, folder_name)
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
        print(f"Directory {tar_path} created.")
    else:
        print(f"Directory {tar_path} already exists.")
    return tar_path


def my_move_file(src_file, dst_path):
    if not os.path.isfile(src_file):
        print(f"FIle %s not exist!" % src_file)
    else:
        mkdir_folder(dst_path)
        f_path, f_name = os.path.split(src_file)
        shutil.move(src_file, dst_path + f_name)
        print(f"Move %s -> %s" % (src_file, dst_path + f_name))


def load_timestamp(ts_file, sensor_name=""):
    """ this is read a timestamp.txt """
    # print("Loading timestamp ..... %s " % _sensor_name)
    print(f"Loading timestamp..... {sensor_name}")
    timestamp = []
    with open(ts_file, "r") as _file:
        while True:
            tmp_time = (_file.readline().strip('\n'))
            if not tmp_time:
                break
            tmp_time = int(tmp_time)  # int 32
            timestamp.append(tmp_time)
    # timestamp = np.stack(timestamp)
    # timestamp = np.array(timestamp, dtype=np.int)  # 将列表转换为 NumPy 数组
    timestamp = np.array(timestamp, dtype=np.int64)  # int32 is error
    timestamp.sort()
    return timestamp


def load_timestamp_fixed(timestamp_path, sensor_name=""):
    ts_file = timestamp_path + f"{sensor_name}_timestamp.txt"
    timestamp = load_timestamp(ts_file, sensor_name)
    return timestamp


def load_timestamp_image(path):
    """ from data file load timestamp """
    timestamp_list = []
    _file_list = os.listdir(path)
    for i in range(0, len(_file_list)):
        tmp_name = _file_list[i]
        if tmp_name.split('.')[-1] == 'jpg' or tmp_name.split('.')[-1] == 'jpeg' or tmp_name.split('.')[-1] == 'png':
            timestamp = tmp_name.split('.')[0]
            timestamp_list.append(timestamp)
    timestamp_list.sort()
    return timestamp_list


def load_data_file_sort(path: str, extensions: list = None):
    """ Load and sort data file paths with specific extensions. """
    if extensions is None:
        extensions = ['.bin', '.txt', '.pcd', '.jpg', '.png', '.jpeg']

    data_list = []
    for ext in extensions:
        data_list.extend(glob.glob(os.path.join(path, f"*{ext}")))

    return sorted(data_list)


def load_data_file_sort_image(path: str):
    """ Load and sort image file paths (jpg, jpeg, png) from a directory. """
    data_list = [
        os.path.join(path, file) for file in os.listdir(path)
        if file.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    return sorted(data_list)


def load_image_file_timestamp(path, timestamp):
    """ Load image files by timestamp, trying multiple extensions if necessary. """
    valid_extensions = ['.jpg', '.png', '.jpeg']
    data_list = []

    for idx in range(min(len(timestamp), len(os.listdir(path)))):
        image_path = None
        for ext in valid_extensions:
            temp_path = os.path.join(path, timestamp[idx] + ext)
            if os.path.exists(temp_path):
                image_path = temp_path
                break  # 找到文件就跳出循环

        if image_path:
            data_list.append(image_path)
        else:
            print(f">>> Image not found for timestamp: {timestamp[idx]}")

    return data_list
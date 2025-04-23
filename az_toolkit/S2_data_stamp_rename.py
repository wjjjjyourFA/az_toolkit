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


def move_and_rename_files(source_path, sensor_name, file_extension, target_timestamps, target_path_root, mode=True):
    """ 将已经对齐的各数据，按雷达时间戳的命名对齐
     便于COM数据集，迅速区分对齐帧"""
    target_path = mkdir_folder(target_path_root, f"/{sensor_name}/")

    # Read the reference timestamps
    reference_timestamp_path = mkdir_folder(source_path, "/timestamp_match/")
    # reference_timestamps = load_timestamp(reference_timestamp_path + f"{sensor_name}_timestamp.txt", f"{sensor_name}")
    reference_timestamps = load_timestamp_fixed(reference_timestamp_path, f"{sensor_name}")

    count = 0
    """ 两个要一样长 """
    for idx, target_timestamp in enumerate(target_timestamps):
        if idx >= len(reference_timestamps):
            break

        if mode:
            original_filename = os.path.join(
                source_path, sensor_name, str(reference_timestamps[idx]) + file_extension
            )
        else:
            original_filename = os.path.join(
                source_path, f"undistort_{sensor_name}", str(reference_timestamps[idx]) + file_extension
            )
        target_filename = os.path.join(target_path, str(target_timestamp) + file_extension)

        try:
            """ two steps """
            # # Move file to target path
            # # shutil.move(original_filename, target_path)
            # shutil.copy(original_filename, target_path)
            #
            # # Rename file in target path
            # moved_file_path = os.path.join(target_path, str(reference_timestamps[idx]) + file_extension)
            # os.rename(moved_file_path, target_filename)

            """ one step """
            shutil.copyfile(original_filename, target_filename)
            count += 1
        except FileNotFoundError as e:
            print(f"File not found: {original_filename}. Skipping.")
        except Exception as e:
            print(f"Error moving or renaming file: {e}")
    print(count)


def copy_timestamp_file(source_path, sensor_name, target_path_root):
    target_path = mkdir_folder(target_path_root, f"/timestamp/")

    reference_timestamp_path = mkdir_folder(source_path, "/timestamp_match/")
    file_path = reference_timestamp_path + f"lidar_timestamp.txt"

    # original_filename = os.path.join(source_path, file_path)
    original_filename = file_path
    target_filename = os.path.join(target_path, f"{sensor_name}_timestamp.txt")

    shutil.copyfile(original_filename, target_filename)


def main(root="./../../test_data/samples_common"):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return
    timestamp_match_path = mkdir_folder(root, "/timestamp_match/")
    data_matched_path = os.path.join(root, f"matched")

    # lidar_timestamp_list = load_timestamp(timestamp_match_path + "lidar_timestamp.txt", "lidar")
    lidar_timestamp_list = load_timestamp_fixed(timestamp_match_path, "lidar")

    """ move and rename """
    move_and_rename_files(root, "image", ".jpg", lidar_timestamp_list, data_matched_path)
    # move_and_rename_files(root, "infra", ".jpg", lidar_timestamp_list, data_matched_path)
    # move_and_rename_files(root, "radar", ".txt", lidar_timestamp_list, data_matched_path)
    move_and_rename_files(root, "lidar", ".bin", lidar_timestamp_list, data_matched_path)

    copy_timestamp_file(root, "image", data_matched_path)
    copy_timestamp_file(root, "lidar", data_matched_path)


if __name__ == '__main__':
    # main()
    main("/media/jojo/WorkStation/test/right")

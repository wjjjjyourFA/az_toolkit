# Copyright (c) FSZN. All rights reserved.
"""
读取指定文件夹下的时间戳文件，在 10Hz 内，按规则自动匹配最近邻
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


def match_timestamp_image(base_timestamp, catch_timestamp, time_threshold=55):
    matched_timestamp_list = []

    # Convert timestamps to integers for comparison
    base_timestamp_list = [int(ts) for ts in base_timestamp]
    catch_timestamp_list = [int(ts) for ts in catch_timestamp]

    base_delete_list = []
    j = 0

    """ 使用单顺序索引搜索，每个值只会被匹配一次 """
    for base_ts in base_timestamp_list:
        """ 移除比当前雷达时间戳小得多（时间差小于 time_threshold）的图像时间戳 """
        while j < len(catch_timestamp_list) and catch_timestamp_list[j] < base_ts - time_threshold:
            # Remove images that are too far in the past
            j += 1

        """ 删除尾和超长检查 ： ts2 已经匹配完，ts1 还存在的 ts1 """
        if j >= len(catch_timestamp_list):
            # If no catch timestamps are left, stop processing
            base_delete_list.append(base_ts)
            continue

        """ 删除头和中间漏帧： 剩余 ts2 恒大于 ts1 的 ts1 """
        """ 强制筛选，图像时间在雷达时间之前，
        如果有之前的，但阈值不满足，也会丢弃
        同时认为这帧雷达被丢弃
        """
        # if catch_timestamp_list[j] > base_ts + time_threshold:
        if catch_timestamp_list[j] > base_ts:
            # print(">>>>> ts1 has no match because ts2 is greater.")
            # print(base_ts)
            base_delete_list.append(base_ts)
            continue

        nearest_catch = catch_timestamp_list[j]

        """ COM数据集原因，默认图像消息需要在雷达前
         从小至大遍历时，该匹配结果会自动趋向最近 """
        for k in range(j + 1, len(catch_timestamp_list)):
            current_catch = catch_timestamp_list[k]

            if current_catch > base_ts:
                break

            nearest_catch = current_catch

        matched_timestamp_list.append(nearest_catch)

    return matched_timestamp_list, base_delete_list


def align_other_to_image(base_timestamp, catch_timestamp):
    """ 对齐数据源的基准时间戳，即开始时间戳
    初始 base_timestamp: ["1234567890", "1234567990", "1234568090"]
    初始 catch_timestamp: ["1234567800", "1234567880", "1234567900", "1234568000"]
    结果为 catch_timestamp: ['1234567900', '1234568000']
    """
    if not base_timestamp or not catch_timestamp:
        return []  # Return empty list if either list is empty

    """ 123456789 对齐后为 123456700 """
    # Calculate the reference timestamp from the first image
    first_time = int(base_timestamp[0]) // 100 * 100

    # Remove catch timestamps that are earlier than the reference
    while catch_timestamp and (int(catch_timestamp[0]) // 100 * 100 - first_time) < 0:
        catch_timestamp.pop(0)

    # Return the remaining catch timestamps
    return catch_timestamp


def main_com(root=""):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return

    timestamp_path = mkdir_folder(root, "timestamp")
    output_path = mkdir_folder(root, "timestamp_match")

    _flag = False
    if _flag:
        """ 自己设置输出文件 """
        lidar_timestamp_list = load_timestamp(timestamp_path + "lidar" + "_timestamp.txt", "lidar")
        image_timestamp_list = load_timestamp(timestamp_path + "image" + "_timestamp.txt", "image")
        infra_timestamp_list = load_timestamp(timestamp_path + "infra" + "_timestamp.txt", "infra")
        radar_timestamp_list = load_timestamp(timestamp_path + "radar" + "_timestamp.txt", "radar")
    else:
        """ 使用固定命名文件 """
        lidar_timestamp_list = load_timestamp_fixed(timestamp_path, "lidar")
        image_timestamp_list = load_timestamp_fixed(timestamp_path, "image")
        infra_timestamp_list = load_timestamp_fixed(timestamp_path, "infra")
        radar_timestamp_list = load_timestamp_fixed(timestamp_path, "radar")

    """" for image. image has to be before lidar """
    time_threshold = 55
    new_image_timestamp_list, unmatched_timestamp_list = match_timestamp_image(lidar_timestamp_list,
                                                                               image_timestamp_list, time_threshold)
    write_timestamp_fixed(output_path, new_image_timestamp_list, "image")

    """" for infra. infra has to be with image """
    time_threshold = 35
    """ 在COM数据集中，红外相机和可见光相机的视角方向一致
     为匹配最近的红外与雷达，选择的将红外与图像匹配"""
    # new_infra_timestamp_list, _ = match_timestamp_nearest(image_timestamp_list, infra_timestamp_list, time_threshold)
    # 与有匹配对的匹配
    new_infra_timestamp_list, _ = match_timestamp_nearest(new_image_timestamp_list, infra_timestamp_list,
                                                          time_threshold)
    """ manual choose infra timestamp base """
    # new_infra_timestamp_list = align_other_to_image(new_image_timestamp_list, new_infra_timestamp_list)
    write_timestamp_fixed(output_path, new_infra_timestamp_list, "infra")

    """ 删除未配匹配的 ts """
    new_lidar_timestamp_list = remove_unmatched_timestamp(lidar_timestamp_list, unmatched_timestamp_list)

    """" for radar. radar has to be caught nearest """
    time_threshold = 45
    # new_radar_timestamp_list, _ = match_timestamp_nearest(lidar_timestamp_list, radar_timestamp_list, time_threshold)
    # 与有匹配对的匹配
    new_radar_timestamp_list, _ = match_timestamp_nearest(new_lidar_timestamp_list, radar_timestamp_list,
                                                          time_threshold)
    write_timestamp_fixed(output_path, new_radar_timestamp_list, "radar")

    # write_timestamp_fixed(output_path, lidar_timestamp_list, "lidar")
    write_timestamp_fixed(output_path, new_lidar_timestamp_list, "lidar")


def main(root="", limit_num=200):
    # timestamp_path = root + "/timestamp"
    timestamp_path = os.path.join(root, "timestamp")

    # 检查路径是否存在
    if not os.path.exists(timestamp_path):
        raise FileNotFoundError(f"❌ Data path does not exist: {timestamp_path}")

    output_path = mkdir_folder(root, "timestamp_match")

    """ 使用固定命名文件 """
    lidar_timestamp_list = load_timestamp_fixed(timestamp_path, "lidar")
    image_timestamp_list = load_timestamp_fixed(timestamp_path, "image")

    """" for image. image has to be before lidar """
    time_threshold = 100  # 55
    # new_image_timestamp_list, unmatched_timestamp_list = match_timestamp_image(lidar_timestamp_list, image_timestamp_list, time_threshold)
    new_image_timestamp_list, unmatched_timestamp_list = match_timestamp_nearest(lidar_timestamp_list,
                                                                                 image_timestamp_list, time_threshold)

    """ 删除未配匹配的 ts """
    new_lidar_timestamp_list = remove_unmatched_timestamp(lidar_timestamp_list, unmatched_timestamp_list)

    """ 削减匹配对数量
    前提，ts 序列数量 一样长 """
    # 计算步长，确保均匀采样 200 个点
    if len(new_image_timestamp_list) > limit_num:
        indices = np.linspace(0, len(new_image_timestamp_list) - 1, limit_num, dtype=int)
        new_image_timestamp_list = [new_image_timestamp_list[i] for i in indices]
    write_timestamp_fixed(output_path, new_image_timestamp_list, "image")

    if len(new_lidar_timestamp_list) > limit_num:
        indices = np.linspace(0, len(new_lidar_timestamp_list) - 1, limit_num, dtype=int)
        new_lidar_timestamp_list = [new_lidar_timestamp_list[i] for i in indices]
    write_timestamp_fixed(output_path, new_lidar_timestamp_list, "lidar")


if __name__ == '__main__':
    # main_com(GLOBAL_CONFIG["simple_path"] + "/samples_common")
    # main(GLOBAL_CONFIG["simple_path"] + "/samples_common")
    main(GLOBAL_CONFIG["simple_path"] + "/samples_common", limit_num=80)
    # main("/media/jojo/WorkStation/test/yunjian/2026-02-05/2026-02-05-15-00-01")

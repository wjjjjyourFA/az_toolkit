import os


def extract_timestamps(root_path, data_subfolder, file_extension, output_file, strip_prefix=False):
    """
    Extracts timestamps from filenames with a specific extension in a given folder,
    and writes them to an output file.

    Args:
        root_path (str): Root directory path.
        data_subfolder (str): Subfolder containing the data files.
        file_extension (str): File extension to filter (e.g., '.bin', '.jpg').
        output_file (str): Output file to write the extracted timestamps.
    """
    data_path = os.path.join(root_path, data_subfolder)
    # output_file = os.path.join(root_path, output_file)

    # Get the list of files and sort them
    file_list = os.listdir(data_path)
    file_list.sort()

    with open(output_file, 'w') as file:
        for file_name in file_list:
            if os.path.splitext(file_name)[-1] == file_extension:
                timestamp = os.path.splitext(file_name)[0]  # 无修饰
                if strip_prefix:  # Strip the prefix before the first '-'
                    timestamp = timestamp.split("-", 1)[-1]  # 有前缀
                file.write(timestamp + '\n')


def extract_timestamps_fixed(root_path, data_subfolder, file_extension, output_file_path, strip_prefix=False):
    ts_file = output_file_path + f"{data_subfolder}" + f"_timestamp.txt"
    extract_timestamps(root_path, data_subfolder, file_extension, ts_file, strip_prefix)


def write_timestamp(ts_file, timestamp_list):
    # fp_ = open(ts_file, 'w')
    # for line in range(0, len(timestamp_list)):
    #     fp_.write(str(timestamp_list[line]))
    #     fp_.write("\n")
    # fp_.close()

    with open(ts_file, 'w') as file:
        for timestamp in timestamp_list:
            file.write(str(timestamp) + '\n')


def write_timestamp_fixed(timestamp_path, timestamp_list, sensor_name=""):
    ts_file = os.path.join(timestamp_path, f"{sensor_name}_timestamp.txt")
    write_timestamp(ts_file, timestamp_list, )


def match_timestamp_nearest(base_timestamp, catch_timestamp, time_threshold=55):
    matched_timestamp_list = []

    # Convert timestamps to integers for comparison
    """ ts are sorted """
    base_timestamp_list = [int(ts) for ts in base_timestamp]
    catch_timestamp_list = [int(ts) for ts in catch_timestamp]

    base_delete_list = []
    j = 0  # 用索引代替 pop(0) 以提高效率

    for base_ts in base_timestamp_list:
        """ 移除比当前时间戳小得多（时间差小于 time_threshold）的时间戳 """
        while j < len(catch_timestamp_list) and catch_timestamp_list[j] < base_ts - time_threshold:
            j += 1  # 只是前进索引，而不是 pop(0)，避免 O(n) 的移动操作

        if j >= len(catch_timestamp_list):
            base_delete_list.append(base_ts)
            continue  # 如果没有更多的 catch 时间戳，就退出

        """ 删除头和中间漏帧不符合要求的： 剩余 ts2 恒不满足于 ts1 的 ts1 """
        if catch_timestamp_list[j] > base_ts + time_threshold:
            # print(">>>>> ts1 has no match because ts2 is greater.")
            # print(base_ts)
            base_delete_list.append(base_ts)
            continue

        # Find the nearest catch timestamp
        nearest_catch = catch_timestamp_list[j]
        min_diff = abs(nearest_catch - base_ts)

        """ 从后续的时间戳中开始最近匹配 """
        # Check subsequent catch timestamps
        for k in range(j + 1, len(catch_timestamp_list)):
            current_catch = catch_timestamp_list[k]
            diff = abs(current_catch - base_ts)

            # If the difference starts increasing, stop checking further
            if diff > min_diff:
                break

            # Update nearest timestamp if current one is closer
            nearest_catch = current_catch
            min_diff = diff

        # Append the nearest catch timestamp to the result
        matched_timestamp_list.append(nearest_catch)

    return matched_timestamp_list, base_delete_list


def remove_unmatched_ts(base_timestamp, base_delete_list):
    # 使用列表推导式移除所有在 base_delete_list 中的时间戳
    cleaned_base_timestamp = [ts for ts in base_timestamp if ts not in base_delete_list]

    return cleaned_base_timestamp
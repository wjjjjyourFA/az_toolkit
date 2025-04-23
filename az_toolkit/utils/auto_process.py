import os


def process_folders(root_paths, target_suffix="_new", args=None, process_class=None):
    """
    遍历指定根路径中的所有文件夹，并为每个文件夹运行指定的提取操作。

    Args:
        root_paths (list): 根路径列表，每个路径下包含多个文件夹。
        target_suffix (str): 目标文件夹的后缀，默认为 "_extracted"。
        process_class (class): 用于处理文件夹的提取器类，应有 `run()` 方法。
    """
    for root_path in root_paths:
        if not os.path.exists(root_path):
            print(f"路径不存在: {root_path}")
            continue

        # 获取文件夹并排序
        folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
        folders.sort()

        # 遍历每个文件夹并执行操作
        for folder_name in folders:
            source_folder = os.path.join(root_path, folder_name)
            target_folder = os.path.join(root_path, folder_name + target_suffix)

            print(f"正在处理文件夹: {source_folder}")
            print(f"目标文件夹: {target_folder}")

            if process_class:
                args.data_root = source_folder
                args.target_folder = target_folder
                processor = process_class(args=args)
                processor.run()


# 示例调用
if __name__ == "__main__":
    root_paths = ["./../../../modules/tools/camera_calibration/Z0_Data/"]

    # 示例提取器类
    class Extracting:
        def __init__(self, args):
            self.args = args

        def run(self):
            print(f"提取中: {self.args.data_root} 到 {self.args.target_folder}")

    # 调用函数
    process_folders(root_paths, process_class=Extracting)

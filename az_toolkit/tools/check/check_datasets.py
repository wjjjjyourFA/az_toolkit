import os

try:
    # 作为包导入时
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.config import GLOBAL_CONFIG


def check_required_folders(root, required_folders=""):
    """
    检查指定路径下是否包含所有指定的文件夹。

    Args:
        root (str): 根路径。
        required_folders (list): 需要检查的文件夹列表。

    Returns:
        missing_folders (list): 缺失的文件夹列表。
    """
    missing_folders = []
    for folder in required_folders:
        folder_path = os.path.join(root, folder)
        if not os.path.exists(folder_path):
            missing_folders.append(folder)
    return missing_folders


def main(root=""):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return

    # 需要的文件夹列表
    required_folders = ["image", "calib", "lidar", "radar", "timestamp"]

    missing = check_required_folders(root, required_folders)

    if missing:
        print(f"The following required folders are missing in {root}:")
        for folder in missing:
            print(f" - {folder}")
        raise FileNotFoundError("Some required folders are missing.")
    else:
        print("All required folders are present.")


if __name__ == '__main__':
    main(GLOBAL_CONFIG["simple_path"] + "/samples_common")

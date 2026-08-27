import os
from pathlib import Path
from typing import Tuple

from PIL import Image

try:
    # 作为包导入时
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.config import GLOBAL_CONFIG


def check_image_pair_sizes(
    folder_a: str,
    folder_b: str,
    ext_map: Tuple[str, str] = ('.png', '.jpg')
):
    """
    检查两个文件夹中的图片文件是否一一对应，并比较大小
    Args:
        folder_a (str): 文件夹 A（比如标注图像）
        folder_b (str): 文件夹 B（比如训练图像）
        ext_map (tuple): A 文件的扩展名和 B 文件的扩展名
    """
    folder_a = Path(folder_a)
    folder_b = Path(folder_b)
    a_ext, b_ext = ext_map

    # 获取 folder_a 下的所有文件
    files_a = [f for f in folder_a.iterdir() if f.is_file() and f.suffix.lower() == a_ext]

    missing_files = []
    size_mismatch_files = []

    for file_a in files_a:
        # 构造 folder_b 中对应文件路径
        file_b_name = file_a.stem + b_ext
        file_b = folder_b / file_b_name

        if not file_b.exists():
            missing_files.append(file_b_name)
            continue

        # 打开图片比较大小
        try:
            with Image.open(file_a) as img_a, Image.open(file_b) as img_b:
                if img_a.size != img_b.size:
                    size_mismatch_files.append(file_b_name)
        except Exception as e:
            print(f"无法打开文件 {file_a} 或 {file_b}: {e}")

    # 打印结果
    if missing_files:
        print("缺失文件：")
        for f in missing_files:
            print(f"  {f}")
    # else:
    #     print("没有缺失文件。")

    if size_mismatch_files:
        print("大小不一致的文件：")
        for f in size_mismatch_files:
            print(f"  {f}")
    # else:
    #     print("没有大小不一致的文件。")

    print("数据检查完成。")


def main(root="", annFolder="", trainFolder=""):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return

    # 定义标注图片和训练图片的文件夹路径
    annotation_folder = Path(root) / annFolder
    train_image_folder = Path(root) / trainFolder

    if not annotation_folder.exists():
        print(f"❌ Annotation folder does not exist: {annotation_folder}")
        return

    if not train_image_folder.exists():
        print(f"❌ Training image folder does not exist: {train_image_folder}")
        return

    check_image_pair_sizes(annotation_folder, train_image_folder, ext_map=('.png', '.jpg'))


if __name__ == '__main__':
    main(GLOBAL_CONFIG["simple_path"] + "/samples_label", annFolder="image_seg", trainFolder="image_train")

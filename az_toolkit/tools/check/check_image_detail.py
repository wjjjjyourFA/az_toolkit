import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Union

from PIL import Image

try:
    # 作为包导入时
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.config import GLOBAL_CONFIG


def print_image_stats(stats: dict):
    """格式化打印图像统计信息"""
    print("=== 全局统计 ===")
    global_sizes = stats.get("global", {}).get("sizes", {})
    global_formats = stats.get("global", {}).get("formats", {})

    print("尺寸分布：")
    for size, count in sorted(global_sizes.items(), key=lambda x: x[0]):
        print(f"  {size[0]}x{size[1]} : {count} 张")

    print("格式分布：")
    for fmt, count in sorted(global_formats.items()):
        print(f"  {fmt} : {count} 张")

    print("\n=== 子文件夹统计 ===")
    folders = stats.get("folders", {})
    for folder, data in sorted(folders.items()):
        print(f"\n子文件夹: {folder or '.'}")
        sizes = data.get("sizes", {})
        formats = data.get("formats", {})

        print("  尺寸分布：")
        for size, count in sorted(sizes.items(), key=lambda x: x[0]):
            print(f"    {size[0]}x{size[1]} : {count} 张")

        print("  格式分布：")
        for fmt, count in sorted(formats.items()):
            print(f"    {fmt} : {count} 张")


def extract_image_info(filepath: Union[str, Path]) -> Dict[str, Union[str, tuple]]:
    """
    获取图像文件的详细信息
    Args:
        filepath (str | Path): 图像文件路径

    Returns:
        dict: 包含 format, mode, size 的信息
    """
    filepath = Path(filepath)
    details = {"format": None, "mode": None, "size": None}

    try:
        with Image.open(filepath) as img:
            details["format"] = img.format
            details["mode"] = img.mode
            details["size"] = img.size
    except Exception as e:
        details["error"] = str(e)

    return details


def analyze_image_folder(root: str):
    """
    批量获取文件夹及其子文件夹中所有图片的统计信息
    - 全局统计尺寸和格式
    - 按子文件夹分别统计尺寸和格式
    Args:
        root (str): 根目录路径
    Returns:
        dict: {
            "global": {
                "sizes": { (w, h): count },
                "formats": { "JPEG": count, ... }
            },
            "folders": {
                "subfolder_path": {
                    "sizes": {...},
                    "formats": {...}
                },
                ...
            }
        }
    """

    root = Path(root)
    global_size_counts = defaultdict(int)
    global_format_counts = defaultdict(int)
    folder_stats = defaultdict(lambda: {"sizes": defaultdict(int), "formats": defaultdict(int)})

    for file in root.rglob("*"):
        if not file.is_file():
            continue

        details = extract_image_info(file)
        if "error" in details:
            continue  # 跳过坏图像或非图像文件

        size = details["size"]
        fmt = details["format"] or "UNKNOWN"

        # 更新全局统计
        global_size_counts[size] += 1
        global_format_counts[fmt] += 1

        # 更新子文件夹统计（相对路径，便于区分）
        folder = str(file.parent.relative_to(root))
        folder_stats[folder]["sizes"][size] += 1
        folder_stats[folder]["formats"][fmt] += 1

    # 转换 defaultdict 为普通 dict
    return {
        "global": {
            "sizes": dict(global_size_counts),
            "formats": dict(global_format_counts)
        },
        "folders": {
            folder: {
                "sizes": dict(stats["sizes"]),
                "formats": dict(stats["formats"])
            }
            for folder, stats in folder_stats.items()
        }
    }


def main(root=""):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return

    stats = analyze_image_folder(root)
    print_image_stats(stats)


if __name__ == '__main__':
    # {'format': 'JPEG', 'mode': 'RGB', 'size': (1920, 1080)}
    info = extract_image_info("az_toolkit/test_data/tools/check/test_data/example.jpg")
    print(info)

    main(GLOBAL_CONFIG["simple_path"] + "/samples_label/image")

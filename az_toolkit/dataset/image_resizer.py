import os

from PIL import Image

try:
    # 作为包导入时
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.config import GLOBAL_CONFIG


class ImageResizer:
    def __init__(self, folder, target_size=(512, 512), background_color=(0, 0, 0), mode=1):
        """
        初始化图像处理器
        :param folder: 图像文件所在的文件夹
        :param target_size: 目标尺寸 (width, height)
        :param background_color: 背景颜色，默认为黑色
        """
        self.folder = folder
        self.target_size = target_size
        self.background_color = background_color
        self.mode = mode

    def get_image_files(self):
        """获取文件夹下所有图片文件"""
        exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif")
        return [
            f for f in os.listdir(self.folder)
            if os.path.isfile(os.path.join(self.folder, f)) and f.lower().endswith(exts)
        ]

    def process_image(self, file_name):
        """处理单张图片，调整到目标大小并居中"""
        file_path = os.path.join(self.folder, file_name)

        with Image.open(file_path) as img:
            if self.mode == 1:
                """ 贴到背景：保持原比例，但周围会有黑边。"""
                # 新建目标大小的背景图
                new_img = Image.new('RGB', self.target_size, color=self.background_color)

                # 计算居中的起始坐标
                start_x = (self.target_size[0] - img.size[0]) // 2
                start_y = (self.target_size[1] - img.size[1]) // 2

                # 粘贴到背景图
                new_img.paste(img, (start_x, start_y))
            elif self.mode == 2:
                """ 直接缩放 """
                # LANCZOS 高质量缩放
                # 缩小图像：LANCZOS   效果最佳，边缘平滑，细节保存较好
                new_img = img.resize(self.target_size, Image.Resampling.LANCZOS)

            """ --- 原文件夹下覆盖保存 --- """
            # new_img.save(file_path)
            """ --- 保存到指定文件夹 --- """
            output_folder = self.folder + "_resized"
            os.makedirs(output_folder, exist_ok=True)  # 如果不存在就创建
            output_path = os.path.join(output_folder, file_name)
            new_img.save(output_path)

    def process_all(self):
        """批量处理所有图片"""
        image_files = self.get_image_files()
        for file_name in image_files:
            self.process_image(file_name)
        print(f"所有图片已调整为 {self.target_size[0]}x{self.target_size[1]} 大小，并置于中央。")


def main(root="", mode=1):
    if not os.path.isdir(root):
        print(f"❌ Root path does not exist: {root}")
        return

    resizer = ImageResizer(root, target_size=(512, 512), background_color=(0, 0, 0), mode=mode)
    resizer.process_all()


if __name__ == "__main__":
    main(GLOBAL_CONFIG["simple_path"] + "/samples_label/image_train", mode=1)
    main(GLOBAL_CONFIG["simple_path"] + "/samples_label/image_seg", mode=1)

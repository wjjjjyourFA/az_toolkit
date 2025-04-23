import os
import glob
import cv2

# for jfif 2 png
from PIL import Image


def esp2png(source, target):
    image = Image.open(source + ".eps")
    image.load()
    image.save(target + ".png")


def webp2png(source, target):
    image = Image.open(source + ".webp")
    image.load()
    image.save(target + ".png")


def jfif2png(source, target):
    image = Image.open(source + ".jfif")
    image.load()
    image.save(target + ".png")


# for svg 2 png
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


def svg2png(source, target):
    image = svg2rlg(source + ".svg")
    renderPM.drawToFile(image, target + ".png", fmt="PNG")


class ImageConvert:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def conver_raw_to_png(self, raw_file, png_file):
        try:
            image = cv2.imread(raw_file)
            cv2.imwrite(png_file, image)
        except ValueError as e:
            print(f"文件格式错误或维度不匹配: {raw_file}. 错误信息: {e}")

    def run(self):
        files = os.listdir(self.input_path)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        for file_name in files:
            tmp_name = file_name.split('.')[0]
            # 生成输入和输出文件路径
            raw_file = os.path.join(self.input_path, file_name)
            png_file = os.path.join(self.output_path, tmp_name + ".png")

            # 执行转换
            self.conver_raw_to_png(raw_file, png_file)


if __name__ == "__main__":
    input_folder = r"./../../../modules/tools/camera_calibration/Z0_Data/samples/image"
    output_folder = input_folder + "_extracted"

    # debug
    # for frame in glob.glob(input_folder + "/*.jfif", recursive=True):
    #     image = Image.open(frame)
    #     source_path = os.path.split(frame)[0]
    #     target_file = os.path.split(frame)[1].replace("jfif", "png")
    #     target_path = os.path.join(source_path, "convert", target_file)
    #
    #     jfif2png(source_path, target_path)

    image_convertor = ImageConvert(input_folder, output_folder)
    image_convertor.run()

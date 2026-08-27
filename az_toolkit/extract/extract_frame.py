import os

import cv2

try:
    # 作为包导入时
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.config import GLOBAL_CONFIG


def extract_frame(data_path, file_extension, output_dir, strip_prefix=False, interval=10, show=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_count = 0
    # 遍历文件夹中的所有文件
    for image_file in sorted(os.listdir(data_path), key=lambda x: int(os.path.splitext(x)[0])):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            original_filename = os.path.join(data_path, image_file)

            if frame_count % interval == 0:
                # os.remove(original_filename)
                # save_image_path = os.path.join(output_dir, image_file)
                # shutil.copyfile(original_filename, save_image_path)

                frame = cv2.imread(original_filename)
                image_name = image_file.split('.')[0]
                save_image_path = os.path.join(output_dir, f'{image_name}{file_extension}')
                if strip_prefix:
                    save_image_path = os.path.join(output_dir, f'image-{image_name}{file_extension}')

                if show:
                    cv2.imshow('frame', frame)
                cv2.imwrite(save_image_path, frame)

            frame_count += 1

            keyboard = cv2.waitKeyEx(10)
            if keyboard == 27:
                exit()

    if show:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    data_path = GLOBAL_CONFIG["simple_path"] + r"/samples_common/image"
    save_path = data_path + "_extracted"

    extract_frame(
        data_path=data_path,
        file_extension=".jpg",
        output_dir=save_path,
        interval=1,
        show=False
    )

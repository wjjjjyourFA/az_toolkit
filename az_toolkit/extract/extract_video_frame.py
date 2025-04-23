import os
import datetime

import cv2


def extract_video_frame(video_path, file_extension, output_dir, strip_prefix=False, interval=1, show=False):
    """
    抽取视频中的帧并保存为图片。
    :param video_path: 输入视频的路径
    :param output_dir: 输出帧的保存路径
    :param interval: 抽帧的间隔，默认值为1（抽取每一帧）
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 读取视频
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print("Error: Unable to open video file.")
        return

    frame_count = 0
    saved_frame_count = 0
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            print("Error: Unable to read frame. Ending capture.")
            break

        if show:
            cv2.imshow('frame', frame)

        # 如果当前帧数 % frame_interval == 0，则保存该帧
        if frame_count % interval == 0:
            # tmp_timestamp = int(datetime.datetime.now().timestamp() * 1000)
            tmp_timestamp = saved_frame_count
            save_image_path = os.path.join(output_dir, f'{tmp_timestamp}{file_extension}')
            if strip_prefix:
                save_image_path = os.path.join(output_dir, f'image-{tmp_timestamp}{file_extension}')
            cv2.imwrite(save_image_path, frame)
            saved_frame_count += 1

        frame_count += 1

        keyboard = cv2.waitKeyEx(10)
        if keyboard == 27:
            exit()

    if show:
        cv2.destroyAllWindows()
    capture.release()

    print(f"从视频中提取了 {saved_frame_count} 帧。")


if __name__ == "__main__":
    video_path = r"./../../../modules/tools/camera_calibration/Z0_Data/samples/video/sample.mp4"
    save_path =  r"./../../../modules/tools/camera_calibration/Z0_Data/samples/image"

    extract_video_frame(
        video_path=video_path,
        file_extension=".jpg",
        output_dir=save_path,
        interval=30,
        show=False
    )

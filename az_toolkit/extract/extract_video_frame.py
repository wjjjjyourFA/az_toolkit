import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
from tqdm import tqdm

try:
    # 作为包导入时
    from .config import GLOBAL_CONFIG
except ImportError:
    # 作为独立脚本运行
    from az_toolkit.config import GLOBAL_CONFIG


def extract_video_frame(video_path, file_extension, output_dir, strip_prefix=False, interval=1, position=0, show=False):
    """
    抽取视频中的帧并保存为图片。
    :param video_path: 输入视频的路径
    :param output_dir: 输出帧的保存路径
    :param interval: 抽帧的间隔，默认值为1（抽取每一帧）
    """
    # 读取视频
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        # print(f"[X] Failed to open video: {video_path}")
        tqdm.write(f"[X] Failed to open video: {video_path}")
        print("Failed to open video file. Check path and codec.")
        return

    ''' 确保输出文件夹存在 '''
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    video_frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {video_frame_count}")

    frame_count = 0
    saved_frame_count = 0
    has_count = 0

    ''' 每个视频单独一个 tqdm 进度条（只显示处理帧）'''
    # base_name = os.path.basename(video_path)
    # total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    # pbar = tqdm(total=total_frames, desc=f"{base_name}", position=position, leave=True)

    window_name = os.path.basename(video_path) if show else None

    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            if frame_count >= video_frame_count:
                tqdm.write("✅ Finished reading all frames.")
            else:
                tqdm.write(f"⚠️ Error: Unable to read frame {frame_count}.")
            break

        frame_count += 1

        # 如果当前帧数 % frame_interval == 0，则保存该帧
        if frame_count % interval == 0:
            # tmp_timestamp = int(datetime.datetime.now().timestamp() * 1000)
            tmp_timestamp = frame_count - 1
            save_image_path = os.path.join(output_dir, f'{tmp_timestamp:06d}{file_extension}')
            # print(save_image_path)

            # 如果文件存在，跳过
            if os.path.exists(save_image_path):
                has_count += 1
                continue  # 或者 pass，根据你的循环逻辑

            if strip_prefix:
                save_image_path = os.path.join(output_dir, f'image-{tmp_timestamp:06d}{file_extension}')

            cv2.imwrite(save_image_path, frame)
            saved_frame_count += 1

            if show:
                cv2.imshow(window_name, frame)

        # pbar.update(1)

        if show:
            keyboard = cv2.waitKeyEx(1)
            if keyboard == 27:
                exit()

    # pbar.close()
    capture.release()

    if show:
        cv2.destroyAllWindows()

    # print(f"[✓] {os.path.basename(video_path)} --> {saved_frame_count} frames saved to: {output_dir}")
    tqdm.write(f"[✓] {os.path.basename(video_path)} --> {saved_frame_count} frames saved to: {output_dir}")
    print("has same image frames : ", has_count)


def process_all_videos(input_dir, output_root, interval=30, file_extension=".jpg", max_workers=4):
    supported_exts = [".mp4", ".MP4", ".mts", ".MTS", ".avi", ".mov", ".mkv"]  # 可根据需要扩展

    video_files = [
        f for f in os.listdir(input_dir)
        if os.path.splitext(f)[1].lower() in supported_exts
    ]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for idx, filename in enumerate(video_files):
            video_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            output_dir = os.path.join(output_root, base_name, "images")
            os.makedirs(output_dir, exist_ok=True)  # 确保文件夹存在

            ''' 提交任务给线程池 '''
            # 只有第一个视频启用 show = True
            future = executor.submit(
                extract_video_frame,
                video_path,
                file_extension,
                output_dir,
                strip_prefix=False,
                interval=interval,
                position=idx,  # 传入编号
                # show = (i == 0)
                show=False
            )
            futures[future] = filename

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing videos"):
            result = future.result()
            if result:  # 只输出有内容的结果
                # print(result)
                tqdm.write(str(result))  # 安全打印，不破坏进度条


def main(video_file, save_image_dir):
    extract_video_frame(
        video_path=video_file,
        file_extension=".jpg",
        output_dir=save_image_dir,
        interval=1,
        show=False
    )


def main_auto():
    '''
    批处理，将各video 解析到各自的文件夹下
    '''
    video_root_dir = GLOBAL_CONFIG["simple_path"] + r"/video"
    save_root_dir = GLOBAL_CONFIG["simple_path"] + r"/samples_common/image"

    process_all_videos(video_root_dir, save_root_dir, interval=10, max_workers=8)


if __name__ == "__main__":
    ''' 单视频处理 '''
    # video_path = GLOBAL_CONFIG["simple_path"] + r"/video/sample.mp4"
    # data_path = GLOBAL_CONFIG["simple_path"] + r"/samples_common/image"
    # save_path = data_path + "_extracted"
    #
    # extract_video_frame(
    #     video_path=video_path,
    #     file_extension=".jpg",
    #     output_dir=save_path,
    #     interval=30,
    #     show=False
    # )

    """ fsznpose """
    sub_dir = f"monkey_obj1"
    video_name = f"1"
    extension = f".mp4"
    # sub_dir = f"monkey_split2"
    # video_name = f"MAH01245-Intrusion"
    # extension = f".MP4"
    video_dir = f"/media/jojo/AQiDePan/FSZN/VideoSet"
    save_dir = f"/media/jojo/AQiDePan/FSZN/DataSet"

    video_file = os.path.join(video_dir, sub_dir, f"{video_name}{extension}")
    save_image_dir = os.path.join(save_dir, sub_dir, f"{video_name}", "images")

    main(video_file, save_image_dir)

    """ fsznpose """
    # sub_dir = f"monkey_obj3"
    # video_dir = f"/media/jojo/WorkStation/09/VideoSet"
    # save_dir = f"/media/jojo/WorkStation/09/DataSet"
    #
    # video_root_dir = os.path.join(video_dir, f'{sub_dir}')
    # save_root_dir = os.path.join(save_dir, f'{sub_dir}')
    # process_all_videos(video_root_dir, save_root_dir, interval=1, max_workers=8)

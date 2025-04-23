# -*- coding: utf-8 -*-
import os
import datetime

import cv2


def extract_rtsp_frame(rtsp_url, file_extension, output_dir, strip_prefix=False, interval=10, show=False):
    capture = cv2.VideoCapture(rtsp_url)
    if not capture.isOpened():
        print("Error: Unable to open RTSP stream.")
        return

    frame_count = 0
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            print("Error: Unable to read frame. Ending capture.")
            break

        # Display the resulting frame
        if show:
            cv2.imshow('frame', frame)

        if frame_count % interval == 0:
            tmp_timestamp = int(datetime.datetime.now().timestamp() * 1000)
            save_image_path = os.path.join(output_dir, f'{tmp_timestamp}{file_extension}')
            if strip_prefix:
                save_image_path = os.path.join(output_dir, f'image-{tmp_timestamp}{file_extension}')
            cv2.imwrite(save_image_path, frame)

        frame_count += 1

        keyboard = cv2.waitKeyEx(10)
        if keyboard == 27:
            exit()

    if show:
        cv2.destroyAllWindows()
    capture.release()


if __name__ == "__main__":
    rtsp_url = 'rtsp://username:password@192.168.1.64:554/stream'
    save_path =  r"./../../../modules/tools/camera_calibration/Z0_Data/samples/image"

    extract_rtsp_frame(
        rtsp_url=rtsp_url,
        file_extension=".jpg",
        output_dir=save_path,
        interval=30,
        show=False
    )

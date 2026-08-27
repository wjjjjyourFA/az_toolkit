import cv2
import numpy as np


def draw_box2d_on_image(image, image_box, show=False):
    """ 将标注框画在图像上
    Draw bounding boxes and key points on the image
    """
    # show_gt = copy(image)
    show_gt = image

    for bbox in image_box:
        # Calculate center and top of the bounding box
        cent_x = int((bbox[0] + bbox[2]) // 2)
        cent_y = int((bbox[1] + bbox[3]) // 2)
        top_y = int(bbox[1])

        cv2.rectangle(show_gt, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), thickness=2)  # box
        cv2.circle(show_gt, (cent_x, cent_y), radius=5, color=(0, 255, 255), thickness=-1)  # body center
        cv2.circle(show_gt, (cent_x, top_y), radius=5, color=(0, 255, 255), thickness=-1)  # head top

    if show:
        cv2.imshow("image_box", show_gt)
        cv2.waitKey(1)


def draw_box2d_matched_on_image(show_image, ImageBox, match_preds, match_gt, rh, rw):
    for idx, box in enumerate(ImageBox):
        x_min, y_min, x_max, y_max, class_id = box
        # 根据缩放因子调整坐标
        x_min_scaled = int(x_min * rw)
        y_min_scaled = int(y_min * rh)
        x_max_scaled = int(x_max * rw)
        y_max_scaled = int(y_max * rh)

        # 判断匹配状态
        pre_ = match_preds[:, idx]  # 预测的匹配结果
        gt_ = match_gt[:, idx]  # 实际的匹配结果
        if np.any(pre_):  # 如果存在匹配
            if np.array_equal(pre_, gt_):  # 匹配成功
                tmp_color = (0, 255, 0)  # 绿色
            else:  # 匹配失败
                tmp_color = (0, 0, 255)  # 红色
        else:  # 未匹配
            tmp_color = (255, 0, 0)  # 蓝色

        # 在图像上绘制缩放后的矩形
        cv2.rectangle(show_image,
                      (x_min_scaled, y_min_scaled),
                      (x_max_scaled, y_max_scaled),
                      color=tmp_color,
                      thickness=2)

    return show_image

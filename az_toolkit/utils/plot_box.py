import numpy as np
from copy import copy

import cv2


def PlotImageObj4Points(image, image_box, show=False):
    """ 将标注框画在图像上
    Draw bounding boxes and key points on the image
    """
    # show_gt = copy(image)
    show_gt = image

    for bbox in image_box:
        # Calculate center and top of the bounding box
        cent_x = (bbox[0] + bbox[2]) // 2
        cent_y = (bbox[1] + bbox[3]) // 2
        top_y = bbox[1]

        cv2.rectangle(show_gt, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), thickness=2)  # box
        cv2.circle(show_gt, (cent_x, cent_y), radius=5, color=(0, 255, 255), thickness=-1)  # body center
        cv2.circle(show_gt, (cent_x, top_y), radius=5, color=(0, 255, 255), thickness=-1)  # head top

    if show:
        cv2.imshow("image_box", show_gt)
        cv2.waitKey(1)


def draw_box_matched(show_image, ImageBox, match_preds, match_gt, rh, rw):
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
        # cv2.rectangle(show_image,
        #               (x_min_scaled, y_min_scaled),
        #               (x_max_scaled, y_max_scaled),
        #               color=tmp_color,
        #               thickness=2)

    return show_image


def draw_3dbox_matched(show_range, LidarBox_RangeImage, match_preds, match_gt):
    # 保证索引在s_pred, match_gt和gt_box3d_bev的有效范围内
    num_boxes = len(LidarBox_RangeImage)  # 激光雷达目标数量

    for idx in range(num_boxes):
        # 判断匹配状态
        # 鉴于行代表激光雷达目标，我们根据行来判断
        pre_ = match_preds[idx, :]  # 预测的匹配结果
        gt_ = match_gt[idx, :]  # 实际的匹配结果
        if np.any(pre_):  # 如果存在匹配
            if np.array_equal(pre_, gt_):  # 匹配成功
                tmp_color = (0, 255, 0)  # 绿色
            else:  # 匹配失败
                tmp_color = (0, 0, 255)  # 红色
        else:  # 未匹配
            tmp_color = (255, 0, 0)  # 蓝色

        # 绘制框的四条边
        tmpBox = LidarBox_RangeImage[idx]
        # cv2.rectangle(show_range, (tmpBox[0], tmpBox[1]), (tmpBox[2], tmpBox[3]),
        #               color=tmp_color, thickness=2)

    return show_range

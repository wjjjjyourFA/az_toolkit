import cv2
import numpy as np


def draw_box3d_matched_on_range_image(show_range, LidarBox_RangeImage, match_preds, match_gt):
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
        cv2.rectangle(show_range, (tmpBox[0], tmpBox[1]), (tmpBox[2], tmpBox[3]),
                      color=tmp_color, thickness=2)

    return show_range

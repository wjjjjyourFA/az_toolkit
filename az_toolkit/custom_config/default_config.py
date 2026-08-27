# Copyright (c) FSZN. All rights reserved.

class CustomConfig:
    """ default
    横坐标1024为azi方位角 360/2 ，纵坐标128为点云线数
    在卷积神经网络中，一般会对输入特征图做多次2倍下采样，所以图像的宽度需要设置为2的次幂，这里可设置为1024
    """
    # For RangeImage Start
    TargetRangeSize = (128, 1024)
    MaxDis = 100  # 数据点保留到 100m 以内
    fov_up = 35
    fov_down = -25

    """ rs128 """
    # fov_up = 16
    # fov_down = -25

    # For 3D BOX Start
    ObjDis = 25  # box3d 保留到 25m 以内

    # Combined Show
    ImageSize = (1080, 1920)
    # ImageSize = (540, 960)
    ShowImageSize = (int(ImageSize[0] / 2), int(ImageSize[1] / 2))
    ShowRangeSize = (int(ImageSize[0] / 4), int(ImageSize[1]))

    # Merge Show
    TargetImageSize = (256, 512)


def cityscapes_classes():
    """Cityscapes class names for external use."""
    return [
        'road', 'sidewalk', 'building', 'wall', 'fence', 'pole',
        'traffic light', 'traffic sign', 'vegetation', 'terrain', 'sky',
        'person', 'rider', 'car', 'truck', 'bus', 'train', 'motorcycle',
        'bicycle'
    ]

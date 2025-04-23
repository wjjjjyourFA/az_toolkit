import json
import numpy as np


def read_box3d_json(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    # json.load() 这种方法是解析一个文件中的数据
    # json.loads() 需要先将文件，读到一个变量作为字符串, 解析一个字符串中的数
    label_info = json.load(f)
    # print(len(label_info))

    boxes3d = []  # 初始化一个空列表用于存放三维边界框
    label = []  # 初始化一个空列表用于存放每个物体的类别

    for i in range(len(label_info)):
        position = label_info[i]['psr']['position']  # 获取物体的位置
        scale = label_info[i]['psr']['scale']  # 获取物体的尺度（长宽高）
        rotation = label_info[i]['psr']['rotation']  # 获取物体的旋转信息
        obj_type = label_info[i]['obj_type']  # 获取物体的类别
        obj_id = label_info[i]['obj_id']  # 获取物体的ID

        # 组装一个三维边界框 [y, -x, z, scale_y, scale_x, scale_z, rotation_z]
        # boxes3d_one = [position['y'], -position['x'], position['z'], scale['y'], scale['x'], scale['z'], rotation['z']]

        # 组装一个三维边界框 [x, y, z, scale_x, scale_y, scale_z, rotation_z]
        boxes3d_one = [position['x'], position['y'], position['z'], scale['x'], scale['y'], scale['z'], rotation['z']]

        # 将当前物体的边界框和类别信息添加到对应的列表中
        boxes3d.append(boxes3d_one)
        label.append(obj_type)

    # 将列表转换为 NumPy 数组
    boxes3d = np.array(boxes3d)

    return boxes3d, label  # 返回三维边界框和标签
import os
import random
import shutil

if __name__ == '__main__':
    # 定义文件夹路径
    img_folder = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/1/img'
    label_folder = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/1/instance_label'

    train_img_folder = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/train_image'
    train_label_folder = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/train_annotation'

    val_img_folder = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/val_image'
    val_label_folder = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/val_annotation'

    # 确保目标文件夹存在
    for folder in [train_img_folder, train_label_folder, val_img_folder, val_label_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # 获取所有图片文件名
    img_files = [f for f in os.listdir(img_folder) if os.path.isfile(os.path.join(img_folder, f))]
    random.shuffle(img_files)

    # 分配测试数据
    val_files = img_files[:200]
    train_files = img_files[200:]

    # 复制文件到相应文件夹
    for file in train_files:
        shutil.copy(os.path.join(img_folder, file), os.path.join(train_img_folder, file))
        shutil.copy(os.path.join(label_folder, file.replace('.jpg', '.png')),
                    os.path.join(train_label_folder, file.replace('.jpg', '.png')))

    for file in val_files:
        shutil.copy(os.path.join(img_folder, file), os.path.join(val_img_folder, file))
        shutil.copy(os.path.join(label_folder, file.replace('.jpg', '.png')),
                    os.path.join(val_label_folder, file.replace('.jpg', '.png')))

    print("数据分割完成。")

    # 创建 train_list.txt 和 val_list.txt
    train_list_file = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/train_list.txt'
    val_list_file = '/home/qsz/projects/my_projects/paddle/PaddleSeg/data/coastline/val_list.txt'

    # 写入训练数据列表
    with open(train_list_file, 'w') as file:
        for file_name in train_files:
            img_path = os.path.join('train_image', file_name)
            label_path = os.path.join('train_annotation', file_name.replace('.jpg', '.png'))
            file.write(f'{img_path} {label_path}\n')

    # 写入验证数据列表
    with open(val_list_file, 'w') as file:
        for file_name in val_files:
            img_path = os.path.join('val_image', file_name)
            label_path = os.path.join('val_annotation', file_name.replace('.jpg', '.png'))
            file.write(f'{img_path} {label_path}\n')

    print("train_list.txt 和 val_list.txt 已生成。")

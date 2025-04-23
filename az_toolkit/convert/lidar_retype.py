import os
import numpy as np
# import pcl
import open3d as o3d


def bin2txt(bin_file, target):
    # points = np.fromfile(bin_file + ".bin", dtype=np.int32).reshape(-1, 4)
    points = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)
    np.savetxt(target + ".txt", points, fmt='%s', delimiter=' ')


""" Python-pcl is not easy to install !
def bin2pcd_pcl(bin_file, target):
    # lidar_points = np.fromfile(bin_file + ".bin", dtype=np.int32).reshape(-1, 4)
    lidar_points = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)

    # 将坐标和强度分离
    points = lidar_points[:, :3] / 100  # 假设单位转换为米
    intensities = lidar_points[:, 3].reshape(-1, 1)

    # 合并点云和强度
    lidar_pcd = np.hstack((points, intensities)).astype(np.float32)

    # 创建 PCL 点云对象
    point_cloud = pcl.PointCloud_PointXYZI()
    point_cloud.from_array(lidar_pcd)

    # 保存为 PCD 文件
    base_name = os.path.splitext(os.path.basename(bin_file))[0]
    out_file = os.path.join(target, base_name + ".pcd")
    pcl.save(point_cloud, out_file)
"""


def bin2pcd_open3d(bin_file, target):
    # 读取二进制文件
    lidar_points = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)

    # 将坐标和强度分离
    points = lidar_points[:, :3] / 100  # 假设单位转换为米
    intensities = lidar_points[:, 3].reshape(-1, 1)

    # 创建 Open3D 点云对象
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    point_cloud.colors = o3d.utility.Vector3dVector(intensities / intensities.max())

    # 保存为 PCD 文件
    base_name = os.path.splitext(os.path.basename(bin_file))[0]
    out_file = os.path.join(target, base_name + ".pcd")
    o3d.io.write_point_cloud(str(out_file), point_cloud, write_ascii=True)


def bin2pcd_raw(bin_file, target):
    lidar_points = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)

    points = lidar_points[:, :3] / 100  # 假设单位转换为米
    intensities = lidar_points[:, 3].reshape(-1, 1)

    # Manually
    lidar_raw = np.c_[points, intensities]
    num = len(points)

    head = ["# .PCD v.7 - Point Cloud Data file format",
             "VERSION .7",
             "FIELDS x y z intensity",
             "SIZE 4 4 4 4",
             "TYPE F F F F",
             "COUNT 1 1 1 1",
             "WIDTH " + str(num),
             "HEIGHT 1",   # 有num个点的无序点云数据集
             "VIEWPOINT 0 0 0 1 0 0 0",
             "POINTS " + str(num),
             "DATA ascii"]

    base_name = os.path.splitext(os.path.basename(bin_file))[0]
    tmp_file = os.path.join(target, base_name + ".txt")
    out_file = os.path.join(target, base_name + ".pcd")

    file = open(tmp_file, 'w')
    for i in range(len(head)):
        s = head[i] + '\n'
        file.write(s)
    for j in range(len(lidar_raw)):
        s = str(lidar_raw[j][0]) + " " + str(lidar_raw[j][1]) + " "+str(lidar_raw[j][2]) + " " + str(int(lidar_raw[j][3])) + '\n'
        file.write(s)
    file.close()

    os.rename(tmp_file, out_file)



class LidarConvert:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def convert_bin_to_txt(self, bin_file, txt_file):
        try:
            # 从 .bin 文件读取点云数据
            points = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)
            # 保存到 .txt 文件
            np.savetxt(txt_file, points, fmt='%s', delimiter=' ')
        except ValueError as e:
            print(f"文件格式错误或维度不匹配: {bin_file}. 错误信息: {e}")

    def run(self):
        files = os.listdir(self.input_path)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        for file_name in files:
            if file_name.endswith(".bin"):
                # 生成输入和输出文件路径
                bin_file = os.path.join(self.input_path, file_name)
                txt_file = os.path.join(self.output_path, file_name.replace(".bin", ".txt"))

                # 执行转换
                self.convert_bin_to_txt(bin_file, txt_file)


if __name__ == "__main__":
    input_folder = r"./../../../modules/tools/camera_calibration/Z0_Data/samples/lidar"
    output_folder = input_folder + "_extracted"

    lidar_convertor = LidarConvert(input_folder, output_folder)
    lidar_convertor.run()
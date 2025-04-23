import numpy as np


def combine_r_t(rotate, translate):
    """
    将旋转矩阵和平移向量组合成齐次变换矩阵 (4x4)
    """
    # 确保 translate 是列向量
    translate = np.reshape(translate, (3, 1))

    # 构造 4x4 RT 矩阵
    rt_ = np.eye(4)  # 初始化 4x4 单位矩阵
    rt_[:3, :3] = rotate  # 填入旋转矩阵
    rt_[:3, 3] = translate[:, 0]  # 填入平移向量

    return rt_


def read_camera_calib(calib_path):
    """
    读取相机标定文件并提取内参、畸变系数、旋转矩阵、平移向量和投影矩阵。

    Args:
        calib_path (str): 标定文件路径。
    Returns:
        dict: 包含标定参数的字典。
    """

    calib_data = {
        "K": None,
        "k1k2k3": None,
        "p1p2": None,
        "Rotate": None,
        "Translate": None,
        "P": None,
        "RT": None
    }

    with open(calib_path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break  # 文件读取结束

            line = line.strip()
            if line == "K":
                # 读取内参矩阵
                calib_data["K"] = np.array([
                    list(map(float, f.readline().strip().split())),
                    list(map(float, f.readline().strip().split())),
                    list(map(float, f.readline().strip().split()))
                ])
            elif line == "k1k2k3":
                # 读取径向畸变系数
                calib_data["k1k2k3"] = np.array(list(map(float, f.readline().strip().split())))
            elif line == "p1p2":
                # 读取切向畸变系数
                calib_data["p1p2"] = np.array(list(map(float, f.readline().strip().split())))
            elif line == "Rotate":
                # 读取旋转矩阵
                calib_data["Rotate"] = np.array([
                    list(map(float, f.readline().strip().split())),
                    list(map(float, f.readline().strip().split())),
                    list(map(float, f.readline().strip().split()))
                ])
            elif line == "Translate":
                # 读取平移向量
                calib_data["Translate"] = np.array(list(map(float, f.readline().strip().split())))
            elif line == "P":
                # 读取投影矩阵
                projection_matrix = []
                for _ in range(3):
                    projection_matrix.append(list(map(float, f.readline().strip().split())))
                calib_data["P"] = np.array(projection_matrix)

    # 组合 RT 矩阵
    if calib_data["Rotate"] is not None and calib_data["Translate"] is not None:
        calib_data["RT"] = combine_r_t(calib_data["Rotate"], calib_data["Translate"])

    return calib_data


def read_radar_calib(calib_path):
    calib_data = {
        "Rotate": None,
        "Translate": None,
        "RT": None
    }

    with open(calib_path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break  # 文件读取结束

            line = line.strip()
            if line == "Rotate":
                # 读取旋转矩阵
                calib_data["Rotate"] = np.array([
                    list(map(float, f.readline().strip().split())),
                    list(map(float, f.readline().strip().split())),
                    list(map(float, f.readline().strip().split()))
                ])
            elif line == "Translate":
                # 读取平移向量
                calib_data["Translate"] = np.array(list(map(float, f.readline().strip().split())))

    # 组合 RT 矩阵
    if calib_data["Rotate"] is not None and calib_data["Translate"] is not None:
        calib_data["RT"] = combine_r_t(calib_data["Rotate"], calib_data["Translate"])

    return calib_data


def read_pso_calib_all(calib_path):
    calibration_data = []  # 用于存储所有的校准数据

    try:
        with open(calib_path, 'r') as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 如果是数字，则表示当前是一个新的校准数据块的开始
            if line.isdigit():
                calib_data = {
                    "K": None,
                    "k1k2k3": None,
                    "p1p2": None,
                    "Rotate": None,
                    "Translate": None,
                    "P": None,
                    "RT": None
                }
                # 初始化投影矩阵（3x4）
                P = np.zeros((3, 4))
                # 获取接下来的 3 行数据
                for j in range(3):
                    if i + j + 1 < len(lines):
                        # 读取当前行并替换逗号为数字分隔符（空格）
                        row_values = lines[i + j + 1].strip().replace(",", " ").split()

                        # 转换为浮动数值并填充到矩阵中
                        try:
                            row_values = [float(val) for val in row_values]
                        except ValueError:
                            continue  # 如果遇到无法转换为浮动数值的项，跳过该行

                        # 将读取的行放入矩阵
                        P[j, :] = row_values[:4]  # 保证每行只取4个元素（因为是3x4矩阵）

                # 将矩阵 P 添加到校准数据中
                calib_data["P"] = P
                calibration_data.append(calib_data)
                i += 4  # 跳过当前读取的4行（当前块 + 三个矩阵行）
            else:
                i += 1  # 如果该行不是数字，则继续处理下一行
    except Exception as e:
        print(f"Error parsing calibration file: {e}")

    return calibration_data


if __name__ == "__main__":
    calib_file = "./../../../modules/tools/camera_calibration/Z0_Data/samples/calib/KK.ini"
    calib_params = read_camera_calib(calib_file)

    print("Camera Calibration Parameters:")
    for key, value in calib_params.items():
        print(f"{key}:\n{value}\n")
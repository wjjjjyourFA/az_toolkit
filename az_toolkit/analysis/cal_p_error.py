import os
import sys
import numpy as np
import math

from scipy.spatial.transform import Rotation as R
from az_toolkit.read_file.read_calib import *
from az_toolkit.trans.quat2rotation import *

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 切换当前工作目录
os.chdir(script_dir)
sys.path.append(script_dir)
print("脚本所在路径：", script_dir)
print("当前工作目录：", os.getcwd())


def decompose_projection_matrix(P, K):
    # Decompose P = K[R|T] to get R and T
    K_inv = np.linalg.inv(K)

    # Extract the left 3x3 part of P
    M = P[:, :3]

    # Calculate R = K^-1 * M
    R = K_inv @ M

    # Normalize R to ensure it's a proper rotation matrix
    U, _, Vt = np.linalg.svd(R)
    R = U @ Vt

    # Make sure the determinant is 1 (proper rotation matrix)
    if np.linalg.det(R) < 0:
        R = -R

    # Extract T = K^-1 * p4
    T = K_inv @ P[:, 3]

    return R, T


def cal_rotation_diff_trace(R1, R2):
    """
    计算两个旋转矩阵之间的差异，并返回旋转角度。

    参数:
    - R1: 第一个旋转矩阵
    - R2: 第二个旋转矩阵

    返回:
    - angle_diff: 旋转差异角度（单位：度）
    """
    # Calculate the relative rotation matrix
    R_rel = R1.T @ R2

    # Calculate the rotation angle using the formula:
    # trace(R) = 1 + 2*cos(θ)
    cos_theta = (np.trace(R_rel) - 1) / 2

    # 确保数值稳定性
    cos_theta = min(1.0, max(-1.0, cos_theta))

    # 计算角度（以度为单位）
    theta = np.arccos(cos_theta) * 180 / np.pi

    return theta


def cal_rotation_diff(R1, R2):
    """
    计算两个旋转矩阵之间的差异，并返回旋转角度。
    是两个姿态角之间的相对旋转矩阵
    参数:
    - R1: 第一个旋转矩阵
    - R2: 第二个旋转矩阵

    返回:
    - angle_diff: 旋转差异角度（单位：度）
    - ypr_diff: 绕Z（Yaw）、Y（Pitch）、X（Roll）的旋转角度差（单位：度）
    """
    # 计算相对旋转矩阵
    R_relative = np.dot(R1.T, R2)

    # 使用 scipy 计算从旋转矩阵到角度的转换（旋转角度）
    r = R.from_matrix(R_relative)

    # 返回旋转角度（以度为单位）
    theta = r.magnitude() * 180 / np.pi  # 转换为度

    # 按 ZYX 输出姿态角差（Yaw-Pitch-Roll）
    ypr_diff = r.as_euler('ZYX', degrees=True)

    return theta, ypr_diff


def cal_translation_diff(T1, T2):
    """
    Calculate the translation error between two translation vectors.
    Returns the Euclidean distance.
    """
    diff = T2 - T1
    dist = np.linalg.norm(diff)
    return dist, diff


def main(calib_file_test, calib_file_gt):
    auto_calib_data = read_camera_calib(calib_file_test)
    gt_calib_data = read_camera_calib(calib_file_gt)

    P_matrix_gt = gt_calib_data['P']
    intrinsic_matrix = gt_calib_data['K']
    print("Camera Intrinsic Matrix:")
    print(intrinsic_matrix)

    R_gt, T_gt = decompose_projection_matrix(P_matrix_gt, intrinsic_matrix)
    print("\nR_gt ():")
    print(R_gt)
    print("T_gt (mm):")
    print(T_gt)

    # 拼接 k1,k2,p1,p2,k3
    # distortion_temp = np.concatenate((gt_calib_data["k1k2k3"], gt_calib_data["p1p2"]))
    # distortion_coeffs = np.array(
    #     [distortion_temp[0], distortion_temp[1], distortion_temp[3], distortion_temp[4], distortion_temp[2]])
    # print("\nDistortion Coefficients (k1, k2, p1, p2, k3):")
    # print(distortion_coeffs)

    """ test data """
    P = auto_calib_data["P"]

    R, T = decompose_projection_matrix(P, intrinsic_matrix)
    print("\nR_ ():")
    print(R)
    print("T_ (mm):")
    print(T)

    # Calculate rotation and translation errors
    rotation_error, ypr_error = cal_rotation_diff(R, R_gt)
    translation_error, xyz_error = cal_translation_diff(T, T_gt)
    print("\nRotation error (euler degree):", rotation_error)
    print("[yaw, pitch, roll] :", ypr_error)
    print("Translation error (euclidean distance mm):", translation_error)
    print("[dx, dy, dz] :", xyz_error)


def average_rotation_matrices(R_matrices):
    """
    Calculate the average rotation matrix using the method described in:
    https://link.springer.com/article/10.1007/s10851-018-0865-2
    """
    n = len(R_matrices)

    # Convert to 4x4 quaternions
    Q = []
    for R in R_matrices:
        q = rotation_matrix_to_quaternion(R)
        Q.append(q)

    Q = np.array(Q)

    # Form the 4x4 matrix M
    M = np.zeros((4, 4))
    for q in Q:
        M += np.outer(q, q)
    M = M / n

    # Find the eigenvector with the largest eigenvalue
    eigenvalues, eigenvectors = np.linalg.eig(M)
    idx = np.argmax(eigenvalues)
    q_avg = eigenvectors[:, idx]

    # Convert back to rotation matrix
    R_avg = quaternion_to_rotation_matrix(q_avg)

    return R_avg


def compute_lidar_transform(T_lidar2cam1, T_lidar2cam2):
    # 两个 4x4 numpy array
    # [R T
    #  0 1]
    # 计算从 lidar1 到 lidar2 的变换矩阵
    T_lidar1_inv = np.linalg.inv(T_lidar2cam1)
    T_lidar1_to_lidar2 = np.dot(T_lidar1_inv, T_lidar2cam2)

    # 提取平移
    translation = T_lidar1_to_lidar2[:3, 3]

    # 提取旋转
    rotation_matrix = T_lidar1_to_lidar2[:3, :3]
    euler_angles = R.from_matrix(rotation_matrix).as_euler('xyz', degrees=True)  # 欧拉角 (x, y, z)

    return translation, euler_angles, T_lidar1_to_lidar2


def main_all():
    # Parse the AutoCalib_PSO.txt file
    auto_calib_data = read_pso_calib_all("./testdata/auto_all.txt")
    gt_calib_data = read_camera_calib("./testdata/manual.ini")

    P_matrix_gt = gt_calib_data['P']
    intrinsic_matrix = gt_calib_data['K']
    print("Camera Intrinsic Matrix:")
    print(intrinsic_matrix)

    R_gt, T_gt = decompose_projection_matrix(P_matrix_gt, intrinsic_matrix)
    # print("R_gt ():")
    # print(R_gt)
    # print("T_gt (mm):")
    # print(T_gt)

    # 拼接 k1,k2,p1,p2,k3
    # distortion_temp = np.concatenate((gt_calib_data["k1k2k3"], gt_calib_data["p1p2"]))
    # distortion_coeffs = np.array(
    #     [distortion_temp[0], distortion_temp[1], distortion_temp[3], distortion_temp[4], distortion_temp[2]])
    # print("Camera Intrinsic Matrix:")
    # print(intrinsic_matrix)
    # print("\nDistortion Coefficients (k1, k2, p1, p2, k3):")
    # print(distortion_coeffs)

    """ test data """
    # Extract P matrices from the calibration data
    P_matrices = [calib_data["P"] for calib_data in auto_calib_data]

    # Calculate R and T matrices for the first three calibrations
    R_matrices = []
    T_vectors = []
    for i in range(len(P_matrices)):  # First 3 calibrations
        P = P_matrices[i]
        # print(f"\nProcessing calibration #{i + 1}")
        R, T = decompose_projection_matrix(P, intrinsic_matrix)
        R_matrices.append(R)
        T_vectors.append(T)
        # print(f"R matrix #{i + 1}:")
        # print(R)
        # print(f"T vector #{i + 1}:")
        # print(T)

    # Calculate average R and T as ground truth
    R_avg = average_rotation_matrices(R_matrices)
    T_avg = np.mean(T_vectors, axis=0)
    print("\nAverage R matrix (ground truth):")
    print(R_avg)
    print("Average T vector (ground truth mm):")
    print(T_avg)

    # Calculate R and T for the fourth calibration
    P_check = P_matrices[-1]
    R_check, T_check = decompose_projection_matrix(P_check, intrinsic_matrix)
    # print("\nR check -1:")
    # print(R_check)
    # print("T check -1:")
    # print(T_check)

    # Calculate rotation and translation errors
    rotation_error = cal_rotation_diff(R_avg, R_check)
    translation_error = cal_translation_diff(T_avg, T_check)

    print("\nRotation error (euler degree):", rotation_error)
    print("Translation error (euclidean distance mm):", translation_error)


def check_2transform():
    T_lidar2cam1 = np.array([
        [0.00535521, - 0.99945784, 0.03248613, 354.69303791],
        [0.04789471, - 0.03219296, - 0.99833347, 287.11502598],
        [0.99883803, 0.0069022, 0.04769634, -498.213],
        [0, 0, 0, 1]
    ])
    T_lidar2cam2 = np.array([
        [-0.01121493, - 0.99860596, 0.05157872, -450.55320112],
        [0.03172808, - 0.05191136, - 0.99814755, 262.66493271],
        [0.99943362, - 0.00955766, 0.03226604, 520.054],
        [0, 0, 0, 1]
    ])

    translation, euler_angles, _ = compute_lidar_transform(T_lidar2cam1, T_lidar2cam2)

    print("\nR_ ():")
    print(euler_angles)
    print("T_ (mm):")
    print(translation)


def check_transform_offset():
    # === 原始雷达到相机旋转和平移 ===
    R_gt = np.array([
        [0.01282395, -0.99974093, 0.01880475],
        [0.06007962, -0.01800194, -0.99803125],
        [0.99811121, 0.01392848, 0.0598332]
    ])
    T_gt = np.array([-41.6067333, -71.73449723, 30.5194])  # mm

    # === 相机内参 ===
    K_gt = np.array([
        [1957.43694246195, 0, 983.756456853235],
        [0, 1956.52145070368, 460.726049215283],
        [0, 0, 1]
    ])

    # === 雷达初始姿态 ===
    roll0  = 0.00436332     # ≈ 0.25°
    pitch0 = -0.0209438     # ≈ -1.2°
    yaw0   = -0.00436315    # ≈ -0.25°

    # === 初始雷达姿态旋转矩阵 ===
    R_lidar0 = R.from_euler('xyz', [roll0, pitch0, yaw0]).as_matrix()

    # === 增量变化 ===
    # delta_rpy_deg = np.array([-0.5, +0.5, -0.5])  # deg
    # delta_rpy_rad = np.deg2rad(delta_rpy_deg)
    # delta_T = np.array([0.5, 0.4, 0.3]) * 1000  # m → mm

    # === 增量变化 ===
    delta_rpy_deg = np.array([-0.5, +0.5, -0.5])  # deg
    delta_rpy_rad = np.deg2rad(delta_rpy_deg)
    delta_T = np.array([0.5, 0.4, 0.3]) * 1000  # m → mm

    # === 增量旋转矩阵 ===
    R_delta = R.from_euler('xyz', delta_rpy_rad).as_matrix()

    # === 雷达最终姿态 = 初始姿态 × 增量 ===
    R_lidar_new = R_delta @ R_lidar0  # 注意乘法顺序：先变化再初始

    # 逆变换：从新雷达坐标系变回旧雷达，再变换到相机坐标系
    R_new = R_gt @ np.linalg.inv(R_lidar_new) @ R_lidar0
    T_new = R_gt @ (-np.linalg.inv(R_lidar_new) @ delta_T) + T_gt

    # === 投影矩阵 ===
    Rt = np.hstack((R_new, T_new.reshape(3, 1)))  # 3x4
    P_new = K_gt @ Rt

    # === 打印结果 ===
    print("【新的 R_new】：")
    print(R_new)
    print("\n【新的 T_new (mm)】：")
    print(T_new)
    print("\n【新的 投影矩阵 P】：")
    print(P_new)

    # 可选：计算误差（如与 R_gt 对比）
    return R_new, T_new, P_new


if __name__ == "__main__":
    test_path = "/media/jojo/AQiDePan/CodexOpen/modules/tools/camera_calibration/T0_Tools/analysis"
    calib_file_test = test_path + "/testdata/AutoCalib_PSO.txt"
    calib_file_gt = test_path + "/testdata/AutoCalib_PSO_gt2.txt"
    main(calib_file_test, calib_file_gt)
    # main_all()
    # check_2transform()
    # check_transform_offset()

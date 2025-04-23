import numpy as np
import math

from scipy.spatial.transform import Rotation as R
from az_toolkit.read_file.read_calib import *
from az_toolkit.trans.quat2rotation import *


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

    参数:
    - R1: 第一个旋转矩阵
    - R2: 第二个旋转矩阵

    返回:
    - angle_diff: 旋转差异角度（单位：度）
    """
    # 计算相对旋转矩阵
    R_relative = np.dot(R1.T, R2)

    # 使用 scipy 计算从旋转矩阵到角度的转换（旋转角度）
    r = R.from_matrix(R_relative)

    # 返回旋转角度（以度为单位）
    theta = r.magnitude() * 180 / np.pi  # 转换为度

    return theta


def cal_translation_diff(T1, T2):
    """
    Calculate the translation error between two translation vectors.
    Returns the Euclidean distance.
    """
    return np.linalg.norm(T1 - T2)


def main():
    auto_calib_data = read_camera_calib("./testdata/auto.txt")
    gt_calib_data = read_camera_calib("./testdata/manual.ini")

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

    # Calculate rotation and translation errors
    rotation_error = cal_rotation_diff(R, R_gt)
    translation_error = cal_translation_diff(T, T_gt)
    print("\nRotation error (euler degree):", rotation_error)
    print("Translation error (euclidean distance mm):", translation_error)


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


if __name__ == "__main__":
    main()
    # main_all()

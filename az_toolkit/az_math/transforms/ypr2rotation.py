import numpy as np
import math


def ypr2rotation(yaw, pitch, roll):
    """ Rtotal = Rz(ψ)×Ry(θ)×Rx(ϕ) """

    # Define rotation matrices around X, Y, and Z axes
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(roll), -np.sin(roll)],
                   [0, np.sin(roll), np.cos(roll)]])

    Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                   [0, 1, 0],
                   [-np.sin(pitch), 0, np.cos(pitch)]])

    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                   [np.sin(yaw), np.cos(yaw), 0],
                   [0, 0, 1]])

    # Compute the total rotation matrix
    R_total = np.dot(Rz, np.dot(Ry, Rx))

    return R_total


def YPR2RotationMatrix(ypr):
    # R = Rot_z(yaw) * Rot_y(pitch) * Rot_x(roll)

    eulerZ = ypr[0]
    eulerY = ypr[1]
    eulerX = ypr[2]

    ci = math.cos(eulerX);
    cj = math.cos(eulerY);
    ch = math.cos(eulerZ);
    si = math.sin(eulerX);
    sj = math.sin(eulerY);
    sh = math.sin(eulerZ);

    cc = ci * ch;
    cs = ci * sh;
    sc = si * ch;
    ss = si * sh;
    
    R = np.array([[cj * ch, sj * sc - cs, sj * cc + ss],
                  [cj * sh, sj * ss + cc, sj * cs - sc],
                  [-sj, cj * si, cj * ci]])

    return R


def RotationMatrix2YPR(R, legacy = False):
    if legacy:
        pitch = -math.asin(R[2,0])
        cos_pitch_abs = abs(math.cos(pitch))
        azimuth = math.atan2(R[1,0] / (cos_pitch_abs + 0.000001), R[0,0] / (cos_pitch_abs + 0.000001))
        roll = math.atan2(R[2,1] / (cos_pitch_abs + 0.000001), R[2,2] / (cos_pitch_abs + 0.000001))
        return np.array([azimuth, pitch, roll])
    else:
        EPS = 1e-6

        # 限制范围避免asin报错
        r20 = max(-1.0, min(1.0, R[2, 0]))
        pitch = -math.asin(r20)
        cos_pitch = math.cos(pitch)

        if abs(cos_pitch) < EPS:  # pitch接近±90度
            yaw = math.atan2(-R[0, 1], R[1, 1])
            roll = 0.0
        else:
            yaw = math.atan2(R[1, 0], R[0, 0])
            roll = math.atan2(R[2, 1], R[2, 2])

        return np.array([yaw, pitch, roll])


if __name__ == '__main__':
    # Define the roll, pitch, and yaw angles in radians
    roll = 1.563
    pitch = -0.0235
    yaw = 1.512

    rotation = ypr2rotation(yaw, pitch, roll)
    print("3x3 Rotation Matrix: ")
    print(rotation)

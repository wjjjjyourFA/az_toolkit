import numpy as np


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

    return  R_total


if __name__ == '__main__':
    # Define the roll, pitch, and yaw angles in radians
    roll = 1.563
    pitch = -0.0235
    yaw = 1.512

    rotation = ypr2rotation(yaw, pitch, roll)
    print("3x3 Rotation Matrix: ")
    print(rotation)


import numpy as np
import math


def rotation_matrix_to_quaternion(R):
    """Convert a rotation matrix to a quaternion."""
    trace = np.trace(R)

    if trace > 0:
        S = np.sqrt(trace + 1.0) * 2
        w = 0.25 * S
        x = (R[2, 1] - R[1, 2]) / S
        y = (R[0, 2] - R[2, 0]) / S
        z = (R[1, 0] - R[0, 1]) / S
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        S = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        w = (R[2, 1] - R[1, 2]) / S
        x = 0.25 * S
        y = (R[0, 1] + R[1, 0]) / S
        z = (R[0, 2] + R[2, 0]) / S
    elif R[1, 1] > R[2, 2]:
        S = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        w = (R[0, 2] - R[2, 0]) / S
        x = (R[0, 1] + R[1, 0]) / S
        y = 0.25 * S
        z = (R[1, 2] + R[2, 1]) / S
    else:
        S = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
        w = (R[1, 0] - R[0, 1]) / S
        x = (R[0, 2] + R[2, 0]) / S
        y = (R[1, 2] + R[2, 1]) / S
        z = 0.25 * S

    return np.array([w, x, y, z])


def quaternion_to_rotation_matrix(q):
    """Convert a quaternion to a rotation matrix."""
    q = q / np.linalg.norm(q)  # Normalize
    w, x, y, z = q

    R = np.zeros((3, 3))

    R[0, 0] = 1 - 2 * y * y - 2 * z * z
    R[0, 1] = 2 * x * y - 2 * z * w
    R[0, 2] = 2 * x * z + 2 * y * w
    R[1, 0] = 2 * x * y + 2 * z * w
    R[1, 1] = 1 - 2 * x * x - 2 * z * z
    R[1, 2] = 2 * y * z - 2 * x * w
    R[2, 0] = 2 * x * z - 2 * y * w
    R[2, 1] = 2 * y * z + 2 * x * w
    R[2, 2] = 1 - 2 * x * x - 2 * y * y

    return R

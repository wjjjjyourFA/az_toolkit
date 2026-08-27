import numpy as np
import os


def list_dir(path):
    res = []
    for i in os.listdir(path):
        tmp_dir = os.path.join(path, i)
        if os.path.isdir(tmp_dir):
            res.append(tmp_dir)
    return res


def get_axis_aligned_bbox(region):
    """ convert region to (cx, cy, w, h) that represent by axis aligned box
    """
    nv = region.size
    if nv == 8:
        cx = np.mean(region[0::2])
        cy = np.mean(region[1::2])
        x1 = min(region[0::2])
        x2 = max(region[0::2])
        y1 = min(region[1::2])
        y2 = max(region[1::2])
        A1 = np.linalg.norm(region[0:2] - region[2:4]) * \
            np.linalg.norm(region[2:4] - region[4:6])
        A2 = (x2 - x1) * (y2 - y1)
        s = np.sqrt(A1 / A2)
        w = s * (x2 - x1) + 1
        h = s * (y2 - y1) + 1
    else:
        x = region[0]
        y = region[1]
        w = region[2]
        h = region[3]
        cx = x + w / 2
        cy = y + h / 2
    x = int(cx - w / 2)
    y = int(cy - h / 2)
    w = int(w)
    h = int(h)
    return [x, y, w, h]


def write_new_gt(original_path, new_path):
    f = open(original_path,'r')
    data = f.readlines()
    f.close()

    f = open(new_path,'w')
    for each_gt in data:
        each_gt = each_gt[:-1]
        list_gt = each_gt.split(',')
        region = []
        for str in list_gt:
            region.append(float(str))
        gt = get_axis_aligned_bbox(np.array(region))

        f.writelines('%d,%d,%d,%d\n' %(gt[0], gt[1], gt[2], gt[3]))

    f.close()


if __name__ == '__main__':
    path = './VOT2019'
    res = list_dir(path)
    for gt_file in res:
        splits = gt_file.split('/')
        original_path = os.path.join(gt_file, splits[-1], 'groundtruth.txt')
        new_path = os.path.join(gt_file, splits[-1], 'new_groundtruth.txt')
        #print(original_path)
        write_new_gt(original_path, new_path)

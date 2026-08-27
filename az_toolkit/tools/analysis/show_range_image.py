from az_toolkit.pointcloud.range_image_creator import *
from az_toolkit.utils.read_box3d_json import *


class ShowRangeImage:
    def __init__(self, root):
        self.prefix = root

        """ object raw data path """
        self.lidar_list = self.prefix + '/timestamp/lidar_timestamp.txt'

        """ raw data """
        self.LidarFile = None
        self.lidar = None
        self.input_lidar = None
        # box3d:  (N, 7) [x, y, z, dx, dy, dz, heading], (x, y, z) is the box center
        self.LidarBoxFile = None
        self.box3d = []
        self.box3d_label = []

        self.range_image = None

        """ processor """
        self.ranger = None

    def load_raw_data(self, idx, _lidar_timestamp):
        lidar_time = _lidar_timestamp[idx]
        json_name = lidar_time

        self.LidarFile = self.prefix + '/lidar/' + '%d' % lidar_time + '.bin'
        self.LidarBoxFile = self.prefix + '/box3d/' + '%d' % json_name + '.json'

        self.lidar = np.fromfile(self.LidarFile, dtype=np.int32)
        self.input_lidar = self.lidar.reshape([-1, 4])

        """ JSON 标注框 """
        self.box3d, self.box3d_label = read_box3d_json(self.LidarBoxFile)
        """ 24d 标注框 """
        # self.box3d = read_box3d_result_24d(self.LidarBoxFile)  # type,{x,y,z}*8
        return True

    def init_model(self):
        print(">>> Defining RangeImage Processor.....")
        self.ranger = RangeImageCreator()
        print(">>> Done.....")

    def init_cv(self):
        cv2.namedWindow("RangeImage", cv2.WINDOW_NORMAL)

    def show_cv(self, _image):
        cv2.imshow("RangeImage", _image)
        cv2.waitKey(1)

    def run(self):
        for lidar_idx in tqdm(range(0, self.lidar_timestamp.shape[0], 1)):
            if not self.load_raw_data(lidar_idx, self.lidar_timestamp):
                continue

            '''Creating RangeImage'''
            proj_range, proj_xyz, proj_remission, proj_mask = self.ranger.project_range(self.input_lidar)
            # range_feature = self.ranger.get_range_feature()
            """ 用于显示，废弃 """
            # self.range_image = self.ranger.get_range_image()
            """ """
            show_range, show_range_at = self.ShowAttention(proj_range)
            self.range_image = show_range

            """ Project lidar objects into range_image """
            self.range_image = self.draw_box3d_in_rangeimage(self.box3d, self.box3d_label, self.range_image)

            self.show_cv(self.range_image)

    def draw_box3d_in_rangeimage(self, _box3d, _label, show_range_image):
        if len(_box3d):
            corners = box3d_convert_7d_to_24d(_box3d)
            lidar_range_result, _ = self.ranger.ProjLidarObj2RangeList8Point(corners)
            for ii in range(0, len(lidar_range_result)):
                tmp_box = lidar_range_result[ii]
                cv2.rectangle(show_range_image, (tmp_box[0], tmp_box[1]), (tmp_box[2], tmp_box[3]),
                              color=(0, 0, 255),
                              thickness=2)
                cv2.putText(show_range_image, _label[ii], (tmp_box[0], tmp_box[1]),
                            fontFace=1, fontScale=1,
                            color=(0, 0, 255), thickness=2)
        return show_range_image

    def ShowAttention(self, _proj_range):
        _proj_range[_proj_range > 40] = 40
        zero_mask = _proj_range == -1
        tmp = (255 * (_proj_range - np.min(_proj_range)) / (np.max(_proj_range) - np.min(_proj_range))).astype(np.uint8)

        show_range_ = cv2.applyColorMap(tmp, cv2.COLORMAP_JET)
        show_range_[zeroMask, :] = 0

        return show_range_


if __name__ == '__main__':
    runner = ShowRangeImage()
    runner.init_model()
    runner.init_cv()
    runner.run()

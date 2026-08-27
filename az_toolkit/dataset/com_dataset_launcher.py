# Copyright (c) FSZN. All rights reserved.
"""
This is a toolbox designed for auto-calibration algorithms and common dataset construction.
Before using this toolbox, you need to use the data_processor module to parse
and preprocess the raw data in advance, generating a dataset in the required format.
"""

import az_toolkit.dataset.data_stamp_rename
# 导入模块
import az_toolkit.dataset.read_timstamp
import az_toolkit.dataset.timestamp_match
from az_toolkit.config import GLOBAL_CONFIG


def main(z_data_path=""):
    """ 生成时间戳序列 """
    az_toolkit.dataset.read_timstamp.main(z_data_path, fixedTsFile=False)
    az_toolkit.dataset.timestamp_match.main(z_data_path, limit_num=100)
    az_toolkit.dataset.select_nearest.main(z_data_path, z_data_path)
    az_toolkit.dataset.data_stamp_rename.main(z_data_path)


if __name__ == '__main__':
    main(GLOBAL_CONFIG["simple_path"] + "/samples_dataset")
    # main("/media/jojo/WorkStation/test/yunjian/cam4")

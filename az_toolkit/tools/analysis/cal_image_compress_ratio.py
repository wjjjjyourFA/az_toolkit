#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image, CompressedImage


class InfoTest:
    def __init__(self):
        self.raw_size = 0
        self.compressed_size = 0

        self.raw_topic = "/Test/sensor/camera/type/pos"
        self.comp_topic = self.raw_topic + "/compressed"

        rospy.Subscriber(self.raw_topic, Image, self.raw_callback)
        rospy.Subscriber(self.comp_topic, CompressedImage, self.compressed_callback)

    def raw_callback(self, msg):
        # step 已经是每行的字节数
        self.raw_size = msg.step * msg.height

    def compressed_callback(self, msg):
        self.compressed_size = len(msg.data)
        if self.raw_size > 0:
            ratio = float(self.compressed_size) / float(self.raw_size)
            rospy.loginfo(
                "Raw: %d bytes, Compressed: %d bytes, Ratio: %.2f",
                self.raw_size, self.compressed_size, ratio
            )


if __name__ == "__main__":
    rospy.init_node("check_compression_ratio")
    info = InfoTest()
    rospy.spin()

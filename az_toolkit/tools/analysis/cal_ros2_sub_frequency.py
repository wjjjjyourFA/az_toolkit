#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node
from rslidar_msg.msg import RslidarPacket
from sensor_msgs.msg import PointCloud2


class TopicFrequencyTest(Node):
    def __init__(self):
        super().__init__('topic_frequency_monitor')

        self.lidar_points_topic = '/m1/rslidar_points'
        self.subscription = self.create_subscription(
            PointCloud2,
            self.lidar_points_topic,
            self.listener_callback,
            10)

        # self.lidar_packets_topic = '/m1/rslidar_packets'
        # self.subscription = self.create_subscription(
        #     RslidarPacket,
        #     self.lidar_packets_topic,
        #     self.listener_callback,
        #     10)

        self.count = 0
        self.start_time = time.time()

    def listener_callback(self, msg):
        self.count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 1.0:  # 每秒统计一次
            frequency = self.count / elapsed_time
            self.get_logger().info(f"Frequency: {frequency:.2f} Hz")
            self.start_time = time.time()
            self.count = 0


def main(args=None):
    rclpy.init(args=args)
    node = TopicFrequencyTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

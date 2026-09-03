#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np


class MockLidarPublisher(Node):
    def __init__(self):
        super().__init__('mock_lidar_publisher')
        
        # Publisher on /scan topic
        self.publisher_ = self.create_publisher(LaserScan, '/fake_scan', 10)
        
        # Publish at 10 Hz (every 0.1 seconds)
        self.timer = self.create_timer(0.1, self.publish_mock_scan)
        
        self.get_logger().info('Mock LiDAR Publisher has been started.')

    def publish_mock_scan(self):
        msg = LaserScan()
        
        # Header setup
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'lidar_link'
        
        # Scanner configuration
        msg.angle_min = -3.14159
        msg.angle_max = 3.14159
        msg.angle_increment = 6.28318 / 360.0
        msg.range_min = 0.1
        msg.range_max = 20.0
        
        # Initialize 360 ranges with max distance (20.0m - open space)
        ranges = np.full(360, 20.0, dtype=np.float32)
        
        # Simulate a wall/obstacle directly in front (around index 180) at 2.5 meters
        ranges[170:190] = 2.5
        
        # Add slight random noise to simulate real sensor variation
        noise = np.random.uniform(-0.05, 0.05, size=360)
        ranges = np.clip(ranges + noise, msg.range_min, msg.range_max)
        
        # Convert NumPy array to Python list for ROS message compatibility
        msg.ranges = ranges.tolist()
        
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MockLidarPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
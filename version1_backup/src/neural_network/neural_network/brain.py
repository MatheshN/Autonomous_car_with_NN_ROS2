#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped

import numpy as np


class NeuralNetwork:

    def __init__(self):

        self.input_size = 9
        self.hidden_size = 16
        self.output_size = 1

        # Input → Hidden
        self.W1 = np.random.randn(
            self.input_size,
            self.hidden_size
        )

        self.b1 = np.zeros(self.hidden_size)

        # Hidden → Output
        self.W2 = np.random.randn(
            self.hidden_size,
            self.output_size
        )

        self.b2 = np.zeros(self.output_size)

    def forward(self, x):

        # Input → Hidden
        z1 = np.dot(x, self.W1) + self.b1

        # ReLU
        a1 = np.maximum(0, z1)

        # Hidden → Output
        z2 = np.dot(a1, self.W2) + self.b2

        return z2[0]


class BrainNode(Node):

    def __init__(self):

        super().__init__('brain_node')

        # Create neural network
        self.network = NeuralNetwork()

        # LiDAR subscriber
        self.subscription = self.create_subscription(
            LaserScan,
            '/fake_scan',
            self.lidar_callback,
            10
        )

        # Steering publisher
        self.publisher = self.create_publisher(
            TwistStamped,
            '/ackermann_steering_controller/reference',
            10
        )

        self.get_logger().info(
            'Neural Network Brain Node Started!'
        )

    def lidar_callback(self, msg):

        # Convert LiDAR ranges to NumPy array
        ranges = np.array(msg.ranges, dtype=np.float32)

        # ------------------------------------------------
        # STEP 1: Divide 360 LiDAR readings into 9 sectors
        # ------------------------------------------------

        sector_size = len(ranges) // 9

        sector_distances = []

        for i in range(9):

            start = i * sector_size
            end = start + sector_size

            sector = ranges[start:end]

            # Closest obstacle in this sector
            minimum_distance = np.min(sector)

            sector_distances.append(minimum_distance)

        # Convert to NumPy array
        lidar_input = np.array(
            sector_distances,
            dtype=np.float32
        )

        # ------------------------------------------------
        # STEP 2: Neural Network prediction
        # ------------------------------------------------

        steering = self.network.forward(lidar_input)

        # ------------------------------------------------
        # STEP 3: Limit steering
        # ------------------------------------------------

        max_steering = 0.6

        steering = np.clip(
            steering,
            -max_steering,
            max_steering
        )

        # ------------------------------------------------
        # STEP 4: Create ROS message
        # ------------------------------------------------

        cmd = TwistStamped()

        cmd.header.stamp = self.get_clock().now().to_msg()

        # Vehicle speed
        cmd.twist.linear.x = 1.0

        # Neural network steering output
        cmd.twist.angular.z = float(steering)

        # ------------------------------------------------
        # STEP 5: Send command to Gazebo controller
        # ------------------------------------------------

        self.publisher.publish(cmd)

        # Debug information
        self.get_logger().info(
            f'LiDAR: {lidar_input} | '
            f'Steering: {steering:.3f}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = BrainNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        # Stop the vehicle
        stop_cmd = TwistStamped()

        stop_cmd.header.stamp = node.get_clock().now().to_msg()
        stop_cmd.twist.linear.x = 0.0
        stop_cmd.twist.angular.z = 0.0

        node.publisher.publish(stop_cmd)

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()
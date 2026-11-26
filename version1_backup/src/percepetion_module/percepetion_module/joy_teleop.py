#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import TwistStamped

class JoyTeleop(Node):
    def __init__(self):
        super().__init__('joy_teleop')
        
        self.publisher_ = self.create_publisher(
            TwistStamped, 
            '/ackermann_steering_controller/reference', 
            10
        )
        
        self.subscription = self.create_subscription(
            Joy, 
            '/joy', 
            self.joy_callback, 
            10
        )
        
        # --- CONFIGURATION ---
        # Standard layout for most gamepads (Xbox/PlayStation):
        self.throttle_axis = 1  # Left stick Up/Down
        self.steering_axis = 3  # Right stick Left/Right 
        # Note: If the right stick doesn't steer, change steering_axis to 2 or 4.
        
        self.max_steering_angle = 0.5  # Maximum physical steering radians
        self.max_speed = 2.0           # Maximum forward/reverse speed in m/s

        self.get_logger().info("Teleop Active: Left Stick = Speed | Right Stick = Steer")

    def joy_callback(self, msg: Joy):
        twist_msg = TwistStamped()
        
        # Timestamps required by strict Ackermann controllers
        twist_msg.header.stamp = self.get_clock().now().to_msg()
        twist_msg.header.frame_id = 'base_link'
        
        # 1. Steering (Angular Z) - Right Stick
        twist_msg.twist.angular.z = msg.axes[self.steering_axis] * self.max_steering_angle
        
        # 2. Throttle (Linear X) - Left Stick
        # If your car drives backward when pushing forward, change to: msg.axes[self.throttle_axis] * -self.max_speed
        twist_msg.twist.linear.x = msg.axes[self.throttle_axis] * self.max_speed
        
        self.publisher_.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = JoyTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
import os
import cv2
import numpy as np
import torch
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge

from neural_network.steering_angle_predictor import CarNN


class AutopilotNode(Node):
    def __init__(self):
        super().__init__('autopilot_node')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = CarNN().to(self.device)

        model_path = os.path.expanduser('~/autonomous_car_nn/autopilot_brain.pth')
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        self.get_logger().info(f'Loaded trained model from {model_path}')

        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.publisher = self.create_publisher(
            TwistStamped,
            '/ackermann_steering_controller/reference',
            10
        )

        self.forward_speed = 0.5

    def preprocess(self, cv_img):
        cropped = cv_img[180:440, :]
        resized = cv2.resize(cropped, (200, 66), interpolation=cv2.INTER_AREA)
        img_normalized = (resized / 127.5) - 1.0
        img_chw = np.transpose(img_normalized, (2, 0, 1))
        tensor = torch.tensor(img_chw, dtype=torch.float32).unsqueeze(0)
        return tensor.to(self.device)

    def image_callback(self, msg):
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        input_tensor = self.preprocess(cv_img)

        with torch.no_grad():
            steering_angle = self.model(input_tensor).item()

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.linear.x = self.forward_speed
        cmd.twist.angular.z = float(steering_angle)
        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = AutopilotNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
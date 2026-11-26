# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import Image
# from geometry_msgs.msg import TwistStamped
# from cv_bridge import CvBridge
# import os
# import csv
# import cv2

# class DataLogger(Node):
#     def __init__ (self):
#         super().__init__("data_logger")
#         self.image_subscriber = self.create_subscription(Image, "/camera/image_raw", self.image_callback, 10)
#         self.steer_subscriber = self.create_subscription(TwistStamped, "/ackermann_steering_controller/reference", self.steering_callback, 10)

#         self.current_steering = 0.0
#         self.bridge = CvBridge()

#         self.dataset_dir = os.path.expanduser('~/autonomous_car_nn/dataset')
#         self.images_dir = os.path.join(self.dataset_dir, 'images')
#         self.csv_path = os.path.join(self.dataset_dir, 'data.csv')

#         os.makedirs(self.images_dir, exist_ok=True)

#         if not os.path.exists(self.csv_path):
#             with open(self.csv_path, mode='w', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(['image_path', 'steering_angle'])
#             self.get_logger().info(f"Created new dataset log at {self.csv_path}")
#         else:
#             self.get_logger().info(f"Appending to existing dataset at {self.csv_path}")


#     def steering_callback(self, msg):

#         self.current_steering = msg.twist.angular.z


#     def image_callback(self, msg):

#         #convert
#         try:
#             cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

#             active_steering = self.current_steering


#             image_filename = f"frame_{self.frame_count:06d}.jpg"
#             image_full_path = os.path.join(self.images_dir, image_filename)
#             image_relative_path = os.path.join('images', image_filename)

#             cv2.imwrite(image_full_path, cv_image)

#             with open(self.csv_path, mode='a', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow([image_relative_path, active_steering])

#             if self.frame_count % 50 == 0:
#                 self.get_logger().info(
#                   f"Image shape: {cv_image.shape} | paired Steering: {active_steering:+.3f} rad"
#                 )
#             self.frame_count +=1

#         except Exception as e:
#             self.get_logger().error(f"Failed to process image: {e}")

# def main(args=None):
#     rclpy.init(args=args)
#     node = DataLogger()

#     try:
#         rclpy.spin(node)

#     except KeyboardInterrupt:
#         node.get_logger().info("shutting down the datalogger")
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()


#!/usr/bin/env python3

import os
import csv
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge

class DataLogger(Node):
    def __init__(self):
        super().__init__("data_logger")
        
        # 1. State Variables
        self.current_steering = 0.0
        self.frame_count = 0
        self.bridge = CvBridge()

        # 2. Storage Paths
        self.dataset_dir = os.path.expanduser('~/autonomous_car_nn/dataset')
        self.images_dir = os.path.join(self.dataset_dir, 'images')
        self.csv_path = os.path.join(self.dataset_dir, 'data.csv')

        # 3. Create folders on disk
        os.makedirs(self.images_dir, exist_ok=True)

        # 4. Initialize CSV file with header if it doesn't exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['image_path', 'steering_angle'])
            self.get_logger().info(f"Created new dataset log at {self.csv_path}")
        else:
            self.get_logger().info(f"Appending to existing dataset at {self.csv_path}")

        # 5. Subscribers
        self.steer_subscriber = self.create_subscription(
            TwistStamped, 
            "/ackermann_steering_controller/reference", 
            self.steering_callback, 
            10
        )
        self.image_subscriber = self.create_subscription(
            Image, 
            "/camera/image_raw", 
            self.image_callback, 
            10
        )

        self.get_logger().info("Data Logger running. Ready to record driving data.")

    def steering_callback(self, msg: TwistStamped):
        # Update the latest steering value on the whiteboard
        self.current_steering = msg.twist.angular.z

    def image_callback(self, msg: Image):
        try:
            # Convert ROS Image to OpenCV matrix
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            active_steering = self.current_steering

            # Generate formatted image filename (frame_000000.jpg, frame_000001.jpg, etc.)
            image_filename = f"frame_{self.frame_count:06d}.jpg"
            image_full_path = os.path.join(self.images_dir, image_filename)
            image_relative_path = os.path.join('images', image_filename)

            # 1. Save image to disk
            cv2.imwrite(image_full_path, cv_image)

            # 2. Append pair to CSV
            with open(self.csv_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([image_relative_path, active_steering])

            # 3. Log progress every 50 frames to avoid spamming the console
            if self.frame_count % 50 == 0:
                self.get_logger().info(
                    f"Logged frame {self.frame_count} | Steering: {active_steering:+.3f} rad"
                )

            self.frame_count += 1

        except Exception as e:
            self.get_logger().error(f"Failed to log frame: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = DataLogger()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down the data logger...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
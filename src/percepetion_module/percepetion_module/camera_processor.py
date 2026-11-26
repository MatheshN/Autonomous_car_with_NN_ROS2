import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraProcessor(Node):
    def __init__(self):
        super().__init__("camera_processor")
        self.get_logger().info("Hello, ROS2 Python Node has been started!")

        self.subscriber = self.create_subscription(Image , "/camera/image_raw", self.callback, 10)

        self.publisher = self.create_publisher(Processed_Image, "/liveimage", 10)

        self.bridge = CvBridge()

    def callback(self, msg):
        try:

            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # TODO: Neural Network inference and lane detection will go here

            cv2.imshow("Autonomous Vehicle - vision pipeline", cv_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Failed to process image frame: {e}")
            
def main(args=None):
    rclpy.init(args=args)
    node= CameraProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("shutting down Vision Pipeline.")
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
# #!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
# import cv2

# class CameraProcessor(Node):
#     def __init__(self):
#         super().__init__('camera_processor_node')
        
#         # Initialize the ROS 2 to OpenCV translation bridge
#         self.bridge = CvBridge()
        
#         # Subscribe to the raw camera topic
#         self.subscription = self.create_subscription(
#             Image,
#             '/camera/image_raw',
#             self.image_callback,
#             10  # QoS profile depth
#         )
        
#         self.get_logger().info("Vision Pipeline initialized. Waiting for camera frames...")

#     def image_callback(self, msg):
#         try:
#             # Convert ROS 2 Image message to an OpenCV BGR NumPy array
#             cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
#             # TODO: Neural Network inference and lane detection will go here
            
#             # Live visualization for verification
#             cv2.imshow("Autonomous Vehicle - Vision Pipeline", cv_image)
#             cv2.waitKey(1)  # 1ms delay required for OpenCV GUI to render
              
#         except Exception as e:
#             self.get_logger().error(f"Failed to process image frame: {e}")

# def main(args=None):
#     rclpy.init(args=args)
#     node = CameraProcessor()
    
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         node.get_logger().info("Shutting down Vision Pipeline.")
#     finally:
#         cv2.destroyAllWindows()
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()
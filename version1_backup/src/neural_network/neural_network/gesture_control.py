#!/usr/bin/env python3

import math

import cv2
import mediapipe as mp
import rclpy

from geometry_msgs.msg import TwistStamped
from rclpy.node import Node


class GestureControlNode(Node):

    def __init__(self):
        super().__init__('gesture_control_node')

        # ==================================================
        # ROS2 publisher
        # ==================================================

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            '/ackermann_steering_controller/reference',
            10
        )

        # ==================================================
        # MediaPipe Hands
        # ==================================================

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        # ==================================================
        # Camera
        # ==================================================

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            self.get_logger().error(
                "Could not open webcam."
            )
            raise RuntimeError(
                "Webcam could not be opened."
            )

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )

        # ==================================================
        # Control loop
        # ==================================================

        self.timer = self.create_timer(
            0.033,
            self.process_frame
        )

        self.get_logger().info(
            "Gesture Control Node Started!"
        )

        self.get_logger().info(
            "Hold two hands up to steer the car."
        )

    # ======================================================
    # PROCESS CAMERA FRAME
    # ======================================================

    def process_frame(self):

        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warning(
                "Failed to read frame from webcam."
            )
            return

        # Mirror camera
        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        # ==================================================
        # Convert BGR -> RGB
        # ==================================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # ==================================================
        # MediaPipe
        # ==================================================

        results = self.hands.process(rgb_frame)

        # ==================================================
        # Default command = STOP
        # ==================================================

        twist = TwistStamped()

        twist.header.stamp = (
            self.get_clock().now().to_msg()
        )

        twist.twist.linear.x = 0.0
        twist.twist.angular.z = 0.0

        # ==================================================
        # TWO HANDS DETECTED
        # ==================================================

        if (
            results.multi_hand_landmarks
            and len(results.multi_hand_landmarks) == 2
        ):

            # ----------------------------------------------
            # Get wrist landmarks
            # ----------------------------------------------

            hand1 = (
                results.multi_hand_landmarks[0]
                .landmark[0]
            )

            hand2 = (
                results.multi_hand_landmarks[1]
                .landmark[0]
            )

            # ----------------------------------------------
            # Convert normalized coordinates to pixels
            # ----------------------------------------------

            x1 = int(hand1.x * w)
            y1 = int(hand1.y * h)

            x2 = int(hand2.x * w)
            y2 = int(hand2.y * h)

            # ----------------------------------------------
            # Determine left/right hand on screen
            # ----------------------------------------------

            if x1 < x2:

                left_hand = (x1, y1)
                right_hand = (x2, y2)

            else:

                left_hand = (x2, y2)
                right_hand = (x1, y1)

            # ----------------------------------------------
            # Draw line between hands
            # ----------------------------------------------

            cv2.line(
                frame,
                left_hand,
                right_hand,
                (0, 255, 0),
                4
            )

            cv2.circle(
                frame,
                left_hand,
                10,
                (0, 0, 255),
                -1
            )

            cv2.circle(
                frame,
                right_hand,
                10,
                (255, 0, 0),
                -1
            )

            # ==================================================
            # Calculate hand orientation
            # ==================================================

            dx = right_hand[0] - left_hand[0]
            dy = right_hand[1] - left_hand[1]

            angle = math.atan2(
                dy,
                dx
            )

            # ==================================================
            # Convert gesture -> vehicle command
            # ==================================================

            # Forward velocity
            twist.twist.linear.x = 1.5

            # Steering velocity
            twist.twist.angular.z = (
                -float(angle) * 1.5
            )

            # Limit angular velocity
            max_angular_velocity = 1.0

            twist.twist.angular.z = max(
                -max_angular_velocity,
                min(
                    max_angular_velocity,
                    twist.twist.angular.z
                )
            )

            # ==================================================
            # Display information
            # ==================================================

            cv2.putText(
                frame,
                f"Steer: {twist.twist.angular.z:.2f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "TWO HANDS DETECTED",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # ==================================================
        # SAFETY STOP
        # ==================================================

        else:

            twist.twist.linear.x = 0.0
            twist.twist.angular.z = 0.0

            cv2.putText(
                frame,
                "Place BOTH hands in frame",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # ==================================================
        # PUBLISH TO ACKERMANN CONTROLLER
        # ==================================================

        self.cmd_pub.publish(twist)

        # ==================================================
        # Draw hand landmarks
        # ==================================================

        if results.multi_hand_landmarks:

            for hand_landmarks in (
                results.multi_hand_landmarks
            ):

                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

        # ==================================================
        # Display camera
        # ==================================================

        cv2.imshow(
            "Gesture Controller",
            frame
        )

        # ==================================================
        # Press Q to stop
        # ==================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):

            self.get_logger().info(
                "Q pressed. Stopping gesture controller."
            )

            self.timer.cancel()

            self.cleanup()

            rclpy.shutdown()

    # ======================================================
    # CLEANUP
    # ======================================================

    def cleanup(self):

        if self.cap is not None:
            self.cap.release()

        if self.hands is not None:
            self.hands.close()

        cv2.destroyAllWindows()

    # ======================================================
    # DESTROY NODE
    # ======================================================

    def destroy_node(self):

        self.cleanup()

        super().destroy_node()


# ==========================================================
# MAIN
# ==========================================================

def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = GestureControlNode()

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    except Exception as e:

        print(
            f"Gesture controller error: {e}"
        )

    finally:

        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == '__main__':
    main()
"""Detector node: runs YOLO on a frame and publishes detections as JSON."""
import json
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import cv2
from ultralytics import YOLO


class Detector(Node):
    def __init__(self) -> None:
        super().__init__("detector")
        model_path = os.environ.get("YOLO_MODEL", "yolov8n.pt")
        self.model = YOLO(model_path)
        self.image_path = os.environ.get("SAMPLE_IMAGE", "/assets/sample.jpg")
        self.publisher = self.create_publisher(String, "detections", 10)
        self.timer = self.create_timer(1.0, self.tick)
        self.get_logger().info("Detector started, publishing to /detections")

    def tick(self) -> None:
        frame = cv2.imread(self.image_path)
        if frame is None:
            self.get_logger().warn(f"Cannot read image: {self.image_path}")
            return

        results = self.model(frame, verbose=False)[0]
        count = 0
        for box in results.boxes:
            label = self.model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detection = {
                "label": label,
                "confidence": round(confidence, 4),
                "x": round(x1, 2),
                "y": round(y1, 2),
                "width": round(x2 - x1, 2),
                "height": round(y2 - y1, 2),
            }
            msg = String()
            msg.data = json.dumps(detection)
            self.publisher.publish(msg)
            count += 1

        self.get_logger().info(f"Published {count} detections")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Detector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

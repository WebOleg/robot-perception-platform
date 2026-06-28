"""Detector node: runs YOLO on camera frames (or a fallback image).

Subscribes to /camera (sensor_msgs/Image). If frames arrive (e.g. from Gazebo),
detection runs on the latest frame. If no camera frame is available, it falls
back to a baked sample image so the demo always works. Publishes detections to
/detections only when the scene changes.
"""
import json
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image

import cv2
from ultralytics import YOLO


class Detector(Node):
    def __init__(self) -> None:
        super().__init__("detector")
        model_path = os.environ.get("YOLO_MODEL", "yolov8n.pt")
        self.model = YOLO(model_path)
        self.fallback_path = os.environ.get("SAMPLE_IMAGE", "/assets/sample.jpg")
        self.latest_frame = None

        self.subscription = self.create_subscription(
            Image, "camera", self.on_frame, 10
        )
        self.publisher = self.create_publisher(String, "detections", 10)
        self.timer = self.create_timer(1.0, self.tick)
        self.last_fingerprint: str | None = None
        self.get_logger().info("Detector started (camera with image fallback)")

    def on_frame(self, msg: Image) -> None:
        import numpy as np
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, -1
        )
        if frame.shape[2] >= 3:
            frame = cv2.cvtColor(frame[:, :, :3], cv2.COLOR_RGB2BGR)
        self.latest_frame = frame

    def tick(self) -> None:
        frame = self.latest_frame
        source = "camera"
        if frame is None:
            frame = cv2.imread(self.fallback_path)
            source = "fallback"
        if frame is None:
            self.get_logger().warn("No frame available (camera or fallback)")
            return

        results = self.model(frame, verbose=False)[0]
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append({
                "label": self.model.names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 4),
                "x": round(x1, 2),
                "y": round(y1, 2),
                "width": round(x2 - x1, 2),
                "height": round(y2 - y1, 2),
            })

        fingerprint = json.dumps(
            sorted((d["label"], d["x"], d["y"]) for d in detections)
        )
        if fingerprint == self.last_fingerprint:
            return
        self.last_fingerprint = fingerprint

        for detection in detections:
            msg = String()
            msg.data = json.dumps(detection)
            self.publisher.publish(msg)

        self.get_logger().info(
            f"Scene changed ({source}): published {len(detections)} detections"
        )


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

"""Detector node: runs YOLO on camera frames (or a fallback image).

Two outputs with different lifecycles (see ADR 0001):
- /detections (std_msgs/String, JSON): light facts, published only on scene
  change, stored in the database via the bridge.
- /annotated (sensor_msgs/CompressedImage, JPEG): the heavy annotated frame,
  published every tick as the current view, never persisted.

Set USE_SEG=1 to use a segmentation model (draws masks) instead of boxes.
"""
import json
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image, CompressedImage

import cv2
import numpy as np
from ultralytics import YOLO


class Detector(Node):
    def __init__(self) -> None:
        super().__init__("detector")
        self.use_seg = os.environ.get("USE_SEG", "0") == "1"
        if self.use_seg:
            model_path = os.environ.get("YOLO_SEG_MODEL", "/assets/yolov8n-seg.pt")
        else:
            model_path = os.environ.get("YOLO_MODEL", "yolov8n.pt")
        self.model = YOLO(model_path)
        self.fallback_path = os.environ.get("SAMPLE_IMAGE", "/assets/sample.jpg")
        self.latest_frame = None

        self.create_subscription(Image, "camera", self.on_frame, 10)
        self.detections_pub = self.create_publisher(String, "detections", 10)
        self.annotated_pub = self.create_publisher(CompressedImage, "annotated", 10)
        self.timer = self.create_timer(1.0, self.tick)
        self.last_fingerprint: str | None = None
        mode = "segmentation" if self.use_seg else "boxes"
        self.get_logger().info(f"Detector started ({mode}, camera with fallback)")

    def on_frame(self, msg: Image) -> None:
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, -1
        )
        if frame.shape[2] >= 3:
            frame = cv2.cvtColor(frame[:, :, :3], cv2.COLOR_RGB2BGR)
        self.latest_frame = frame

    def tick(self) -> None:
        if not rclpy.ok():
            return
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
        annotated = frame.copy()

        masks = results.masks
        for i, box in enumerate(results.boxes):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            label = self.model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            detections.append({
                "label": label,
                "confidence": round(confidence, 4),
                "x": round(x1, 2),
                "y": round(y1, 2),
                "width": round(x2 - x1, 2),
                "height": round(y2 - y1, 2),
            })
            drew_mask = False
            if self.use_seg and masks is not None and i < len(masks.data):
                self._draw_mask(annotated, masks.data[i], f"{label} {confidence:.0%}",
                                int(x1), int(y1))
                drew_mask = True
            if not drew_mask:
                self._draw_box(annotated, int(x1), int(y1), int(x2), int(y2),
                               f"{label} {confidence:.0%}")

        self._publish_annotated(annotated)
        self._publish_detections(detections, source)

    def _draw_box(self, img, x1, y1, x2, y2, text) -> None:
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 200, 255), 2)
        cv2.putText(img, text, (x1, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1, cv2.LINE_AA)

    def _draw_mask(self, img, mask_tensor, text, x1, y1) -> None:
        m = mask_tensor.cpu().numpy()
        m = cv2.resize(m, (img.shape[1], img.shape[0]))
        colored = np.zeros_like(img)
        colored[m > 0.5] = (0, 200, 255)
        cv2.addWeighted(colored, 0.45, img, 1.0, 0, img)
        cv2.putText(img, text, (x1, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def _publish_annotated(self, img) -> None:
        ok, buf = cv2.imencode(".jpg", img)
        if not ok:
            return
        msg = CompressedImage()
        msg.format = "jpeg"
        msg.data = buf.tobytes()
        self.annotated_pub.publish(msg)

    def _publish_detections(self, detections, source) -> None:
        fingerprint = json.dumps(
            sorted((d["label"], d["x"], d["y"]) for d in detections)
        )
        if fingerprint == self.last_fingerprint:
            return
        self.last_fingerprint = fingerprint
        for detection in detections:
            msg = String()
            msg.data = json.dumps(detection)
            self.detections_pub.publish(msg)
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
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

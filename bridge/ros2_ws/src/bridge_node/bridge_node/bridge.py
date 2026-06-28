"""Bridge node — the seam between World A (robot) and World B (web).

Subscribes to a ROS2 topic and forwards each event to the backend over HTTP.
This is the ONLY component that speaks both languages: ROS2 in, REST out.

Reliability: the network between worlds can blink. We retry with backoff and
never crash the node on a failed delivery (principle: robustness at the seam).
"""
import os
import time

import rclpy
import requests
from rclpy.node import Node
from std_msgs.msg import String


class Bridge(Node):
    def __init__(self) -> None:
        super().__init__("bridge")

        # Where to send detections. From env (principle #5: nothing hardcoded).
        base_url = os.environ.get("BRIDGE_TARGET_URL", "http://api:8080")
        self.target = f"{base_url}/detections"

        # HTTP session reused across requests (connection pooling).
        self.session = requests.Session()

        self.subscription = self.create_subscription(
            String, "heartbeat", self.on_message, 10
        )
        self.counter = 0
        self.get_logger().info(f"Bridge started. Forwarding to {self.target}")

    def on_message(self, msg: String) -> None:
        """Each topic message becomes one detection sent to World B.

        For now we synthesize a valid detection per tick. When the camera +
        YOLO arrive, they will publish real detections and this forwarding
        logic stays unchanged.
        """
        detection = {
            "label": "heartbeat",
            "confidence": 0.99,
            "x": 0.0,
            "y": 0.0,
            "width": 1.0,
            "height": 1.0,
        }
        self._post_with_retry(detection)

    def _post_with_retry(self, detection: dict, max_attempts: int = 3) -> None:
        """POST the detection, retrying with exponential backoff on failure."""
        for attempt in range(1, max_attempts + 1):
            try:
                resp = self.session.post(self.target, json=detection, timeout=5)
                if resp.status_code == 201:
                    self.get_logger().info(
                        f"Forwarded detection (id={resp.json().get('id')})"
                    )
                    return
                self.get_logger().warn(
                    f"Backend returned {resp.status_code}, attempt {attempt}"
                )
            except requests.RequestException as exc:
                self.get_logger().warn(f"Delivery failed (attempt {attempt}): {exc}")

            if attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))  # 1s, 2s backoff

        self.get_logger().error("Giving up on this detection after retries.")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Bridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

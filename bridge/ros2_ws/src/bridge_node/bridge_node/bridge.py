"""Bridge node: subscribes to /detections and forwards each to the backend."""
import json
import os
import time

import rclpy
import requests
from rclpy.node import Node
from std_msgs.msg import String


class Bridge(Node):
    def __init__(self) -> None:
        super().__init__("bridge")
        base_url = os.environ.get("BRIDGE_TARGET_URL", "http://api:8080")
        self.target = f"{base_url}/detections"
        self.session = requests.Session()
        self.subscription = self.create_subscription(
            String, "detections", self.on_message, 10
        )
        self.get_logger().info(f"Bridge started. Forwarding to {self.target}")

    def on_message(self, msg: String) -> None:
        try:
            detection = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().warn(f"Bad JSON, skipping: {msg.data[:80]}")
            return
        self._post_with_retry(detection)

    def _post_with_retry(self, detection: dict, max_attempts: int = 3) -> None:
        for attempt in range(1, max_attempts + 1):
            try:
                resp = self.session.post(self.target, json=detection, timeout=5)
                if resp.status_code == 201:
                    self.get_logger().info(
                        f"Forwarded {detection['label']} (id={resp.json().get('id')})"
                    )
                    return
                self.get_logger().warn(
                    f"Backend returned {resp.status_code}, attempt {attempt}"
                )
            except requests.RequestException as exc:
                self.get_logger().warn(f"Delivery failed (attempt {attempt}): {exc}")
            if attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))
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

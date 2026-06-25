"""Heartbeat node — the simplest meaningful World A node.

Publishes a counter message to a topic once per second. Proves that ROS2
publishing works inside the container. One node, one responsibility (principle #2).
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Heartbeat(Node):
    def __init__(self) -> None:
        super().__init__("heartbeat")
        # Create a publisher: message type String, topic name "heartbeat", queue size 10.
        self.publisher = self.create_publisher(String, "heartbeat", 10)
        self.counter = 0
        # Call self.tick() every 1.0 seconds.
        self.timer = self.create_timer(1.0, self.tick)
        self.get_logger().info("Heartbeat node started, publishing to /heartbeat")

    def tick(self) -> None:
        msg = String()
        msg.data = f"alive #{self.counter}"
        self.publisher.publish(msg)
        self.get_logger().info(f"Published: {msg.data}")
        self.counter += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Heartbeat()
    try:
        rclpy.spin(node)  # keep running, processing timers/callbacks
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

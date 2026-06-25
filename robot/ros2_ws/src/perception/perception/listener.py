"""Listener node — subscribes to the heartbeat topic.

Demonstrates the other half of pub/sub: it reacts to messages without knowing
who sent them. Decoupled by design (principle #1).
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    def __init__(self) -> None:
        super().__init__("listener")
        # Subscribe to the same topic the heartbeat node publishes to.
        self.subscription = self.create_subscription(
            String, "heartbeat", self.on_message, 10
        )
        self.get_logger().info("Listener node started, subscribed to /heartbeat")

    def on_message(self, msg: String) -> None:
        # Called automatically every time a message arrives on the topic.
        self.get_logger().info(f"Received: {msg.data}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

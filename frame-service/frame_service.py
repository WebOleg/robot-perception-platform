"""Frame service: subscribes to /annotated and serves the latest frame over HTTP.

Heavy media path (see ADR 0001). The latest annotated frame is held in memory
only and never persisted. GET /frame returns image/jpeg, or 404 if no frame
has arrived yet.
"""
import os
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage

from aiohttp import web


class FrameHolder(Node):
    def __init__(self) -> None:
        super().__init__("frame_service")
        self.latest_jpeg: bytes | None = None
        self.create_subscription(CompressedImage, "annotated", self.on_frame, 10)
        self.get_logger().info("Frame service subscribed to /annotated")

    def on_frame(self, msg: CompressedImage) -> None:
        self.latest_jpeg = bytes(msg.data)


def make_app(holder: FrameHolder) -> web.Application:
    async def get_frame(request: web.Request) -> web.Response:
        if holder.latest_jpeg is None:
            return web.Response(status=404, text="no frame yet")
        return web.Response(body=holder.latest_jpeg, content_type="image/jpeg")

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    app = web.Application()
    app.router.add_get("/frame", get_frame)
    app.router.add_get("/health", health)
    return app


def main() -> None:
    rclpy.init()
    holder = FrameHolder()

    spin_thread = threading.Thread(target=rclpy.spin, args=(holder,), daemon=True)
    spin_thread.start()

    port = int(os.environ.get("FRAME_PORT", "8090"))
    web.run_app(make_app(holder), host="0.0.0.0", port=port)

    holder.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

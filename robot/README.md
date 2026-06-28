# robot/ — World A (robot domain)

Real-time, stateless ROS2 nodes. Camera capture, perception (OpenCV + YOLO),
and a C++ throughput monitor. Heavy data (frames) never leaves this domain;
only light structured detections cross the seam.

## Nodes

- `detector` (Python): runs YOLOv8 on incoming frames, publishes detections
  as JSON to `/detections`. Subscribes to `/camera`; falls back to a baked
  sample image when no camera frame is available. Publishes only on scene
  change (deduplication).
- `monitor` (C++, rclcpp): subscribes to `/detections` and reports throughput.
- `heartbeat` / `listener`: minimal pub/sub demo nodes.

## Simulation (Gazebo)

`robot/sim/` contains a Gazebo (Ignition) simulation that publishes camera
frames to the `/camera` ROS2 topic via `ros_gz_bridge`. It runs headless with
software rendering (xvfb + Mesa).

It is a separate, opt-in Compose profile so it never loads during normal use:

    docker compose --profile sim up sim     # start the simulation
    docker compose up                        # normal run, no simulation

Note: on this arm64 macOS dev machine the official Gazebo image runs under
amd64 emulation, so the camera renders in software at a low frame rate. The
detector's image fallback keeps the live demo working regardless. The
architecture is source-agnostic: the detector consumes `/camera` whether the
publisher is Gazebo, a video file, or a real camera.

# robot/ — World A (robot domain)

Real-time, stateless ROS2 nodes. Camera capture and perception
(OpenCV + YOLO). Heavy data (frames) never leaves this domain.

One node = one responsibility. Nodes communicate only via ROS2 topics.

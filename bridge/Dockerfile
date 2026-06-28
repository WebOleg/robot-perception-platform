# The seam — bridge container.
# ROS2 Humble base (to subscribe to topics) + requests (to POST over HTTP).
FROM ros:humble-ros-base

ENV PYTHONUNBUFFERED=1

# HTTP client for forwarding detections to World B.
# Use python3 -m pip (the ROS2 base image has no bare 'pip' on PATH).
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache-dir requests==2.32.3

WORKDIR /ros2_ws
COPY ros2_ws/src ./src

RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

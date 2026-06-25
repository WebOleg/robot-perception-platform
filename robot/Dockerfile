# World A — robot domain container.
# Official ROS2 Humble (LTS) base: ROS2 + Python tooling preinstalled.
FROM ros:humble-ros-base

# Don't buffer Python output (logs appear immediately).
ENV PYTHONUNBUFFERED=1

# Workspace where ROS2 packages live and get built.
WORKDIR /ros2_ws

# Copy our packages into the workspace source tree.
COPY ros2_ws/src ./src

# Build the workspace with colcon (ROS2's build tool).
# 'source' the ROS2 environment first so colcon and deps are on PATH.
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Entry: source both ROS2 and our built workspace, then run whatever command is given.
# Using a shell entrypoint so the ROS2 environment is always loaded.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

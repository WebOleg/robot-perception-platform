# World A simulation: Gazebo (Ignition) + ROS2 bridge.
# Headless software rendering so the camera renders without a GPU/display.
FROM osrf/ros:humble-desktop-full

ENV PYTHONUNBUFFERED=1 \
    LIBGL_ALWAYS_SOFTWARE=1

# Virtual display so the rendering backend has somewhere to draw.
RUN apt-get update && apt-get install -y --no-install-recommends xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

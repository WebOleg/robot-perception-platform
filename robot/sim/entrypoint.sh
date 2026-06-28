#!/bin/bash
set -e
source /opt/ros/humble/setup.bash

WORLD=${GZ_WORLD:-/usr/share/ignition/ignition-gazebo6/worlds/camera_video_record_dbl_pendulum.sdf}

# Start Gazebo server (headless, software rendering via virtual display).
xvfb-run -a -s "-screen 0 1280x720x24" \
  ign gazebo -s -r -v 1 "$WORLD" &

# Wait for the camera topic to appear, then bridge it into ROS2.
sleep 30
exec ros2 run ros_gz_bridge parameter_bridge \
  /camera@sensor_msgs/msg/Image@ignition.msgs.Image

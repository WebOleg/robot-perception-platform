#!/bin/bash
set -e

# Load the base ROS2 environment.
source /opt/ros/humble/setup.bash

# Load our built workspace, if it exists (it will after colcon build).
if [ -f /ros2_ws/install/setup.bash ]; then
  source /ros2_ws/install/setup.bash
fi

# Run whatever command was passed (default: bash).
exec "$@"

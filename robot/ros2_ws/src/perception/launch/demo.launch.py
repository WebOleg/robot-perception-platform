"""Launch file: starts heartbeat + listener together.

The ROS2 way to run multiple nodes with one command, instead of manual
background processes. Analogous to docker-compose, but for ROS2 nodes.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package="perception",
            executable="heartbeat",
            name="heartbeat",
            output="screen",
        ),
        Node(
            package="perception",
            executable="listener",
            name="listener",
            output="screen",
        ),
    ])

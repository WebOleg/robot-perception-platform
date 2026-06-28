from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package="perception",
            executable="detector",
            name="detector",
            output="screen",
        ),
    ])

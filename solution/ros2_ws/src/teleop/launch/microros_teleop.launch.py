"""
Lesson 5 -- drive the micro-ROS robot.

    ros2 launch teleop microros_teleop.launch.py

No bridge this time. The ESP32 subscribes to /cmd_vel itself, so the
keyboard node talks to it directly. Start the agent in another
terminal first:

    ./scripts/start_agent.sh
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='teleop',
            executable='key_teleop',
            name='key_teleop',
            output='screen',
        ),
    ])

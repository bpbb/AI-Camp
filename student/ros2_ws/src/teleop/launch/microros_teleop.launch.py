"""
บทที่ 5 -- ขับหุ่นยนต์ micro-ROS

    ros2 launch teleop microros_teleop.launch.py

ไม่มี bridge: ESP32 subscribe /cmd_vel เอง node คีย์บอร์ดจึงคุยกับมันโดยตรง
ให้เปิด agent ในอีก terminal ก่อน:

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

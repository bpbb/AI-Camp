"""
บทที่ 6 และ 7 -- MQTT gateway

    ros2 launch teleop mqtt_gateway.launch.py

subscribe MQTT แล้ว publish /cmd_vel ให้ขับหุ่นยนต์ผ่าน MQTT ได้
(terminal ในบทที่ 6, มือถือในบทที่ 7) หุ่นยนต์ยังใช้ firmware micro-ROS
จากบทที่ 5 จึงต้องเปิด agent แยกก่อน:

    ./scripts/start_agent.sh

เปิด key_teleop ในอีก terminal ได้ถ้าต้องการขับทั้งคีย์บอร์ดและ MQTT พร้อมกัน
(ทั้งคู่ publish ไปที่ /cmd_vel)
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from teleop.robot_config import robot_id as configured_robot_id


def generate_launch_description():
    host = LaunchConfiguration('host')
    robot_id = LaunchConfiguration('robot_id')

    return LaunchDescription([
        DeclareLaunchArgument('host', default_value='localhost',
                              description='MQTT broker address'),
        DeclareLaunchArgument('robot_id', default_value=configured_robot_id(),
                              description='which robot the phone drives'),

        Node(
            package='teleop',
            executable='mqtt_teleop',
            name='mqtt_teleop',
            output='screen',
            parameters=[{'host': host, 'robot_id': robot_id}],
        ),
    ])

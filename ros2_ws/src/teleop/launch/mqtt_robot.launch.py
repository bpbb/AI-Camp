"""
Appendix -- drive the MQTT-firmware robot from ROS 2.

Not part of the lessons; see docs/appendix-mqtt-robot.md. Starts the
keyboard node and the /cmd_vel -> MQTT bridge together:

    ros2 launch teleop mqtt_robot.launch.py host:=192.168.1.100

The keyboard node needs a real terminal to read keys from, which is
why it is launched with output on screen and its own prefix.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    host = LaunchConfiguration('host')
    robot_id = LaunchConfiguration('robot_id')

    return LaunchDescription([
        DeclareLaunchArgument('host', default_value='192.168.1.100',
                              description='MQTT broker address'),
        DeclareLaunchArgument('robot_id', default_value='robot1',
                              description='which robot to drive'),

        Node(
            package='teleop',
            executable='mqtt_bridge',
            name='mqtt_bridge',
            output='screen',
            parameters=[{'host': host, 'robot_id': robot_id}],
        ),
        Node(
            package='teleop',
            executable='key_teleop',
            name='key_teleop',
            output='screen',
            prefix='xterm -e',   # keyboard node needs its own window
        ),
    ])

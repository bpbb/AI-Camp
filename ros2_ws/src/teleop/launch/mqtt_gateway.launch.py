"""
Lessons 6 and 7 -- the MQTT gateway.

    ros2 launch teleop mqtt_gateway.launch.py

Subscribes to MQTT and publishes /cmd_vel, so anything that can speak
MQTT -- a terminal in lesson 6, a phone in lesson 7 -- can drive the
robot. The robot keeps its micro-ROS firmware from lesson 5, so start
the agent separately first:

    ./scripts/start_agent.sh

Add key_teleop in another terminal if you want to drive from both the
keyboard and MQTT at the same time -- they both publish to /cmd_vel,
and the robot does not care which one it hears.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    host = LaunchConfiguration('host')
    robot_id = LaunchConfiguration('robot_id')

    return LaunchDescription([
        DeclareLaunchArgument('host', default_value='localhost',
                              description='MQTT broker address'),
        DeclareLaunchArgument('robot_id', default_value='robot1',
                              description='which robot the phone drives'),

        Node(
            package='teleop',
            executable='mqtt_teleop',
            name='mqtt_teleop',
            output='screen',
            parameters=[{'host': host, 'robot_id': robot_id}],
        ),
    ])

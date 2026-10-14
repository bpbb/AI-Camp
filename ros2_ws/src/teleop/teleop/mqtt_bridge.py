#!/usr/bin/env python3
"""
APPENDIX -- drive the MQTT-firmware robot from ROS 2.

Subscribes to /cmd_vel and republishes each message to MQTT, so a robot
running the MQTT firmware (env:mqtt) can be driven by key_teleop
without changing a single line of that firmware.

Not used in the lessons -- see docs/appendix-mqtt-robot.md. Note it
points the OPPOSITE way to mqtt_teleop.py, which converts MQTT into
/cmd_vel so a phone can drive the micro-ROS robot.

    ros2 run teleop mqtt_bridge --ros-args -p host:=192.168.1.100
"""
import json

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import paho.mqtt.client as mqtt


def make_client():
    """Build an MQTT client that works on both versions of the library.

    paho-mqtt 2.x wants to be told which callback style you want;
    1.x (what `apt` installs) has never heard of the argument. You will
    meet this kind of thing a lot -- the library moved on, but the one
    in the distribution did not.
    """
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        return mqtt.Client()


class MqttBridge(Node):
    def __init__(self):
        super().__init__('mqtt_bridge')

        # Parameters, so nobody has to edit this file to change the broker.
        self.declare_parameter('host', '192.168.1.100')
        self.declare_parameter('port', 1883)
        self.declare_parameter('robot_id', 'robot1')

        host = self.get_parameter('host').value
        port = self.get_parameter('port').value
        robot_id = self.get_parameter('robot_id').value

        self.topic = f'robot/{robot_id}/cmd'

        self.client = make_client()
        try:
            self.client.connect(host, port, keepalive=60)
        except OSError as exc:
            # A full Python traceback here tells a beginner nothing useful,
            # so say what to actually check instead.
            self.get_logger().error(
                f'cannot reach the MQTT broker at {host}:{port} ({exc.strerror}).\n'
                f'  is the broker running?      systemctl status mosquitto\n'
                f'  is this the right address?  hostname -I\n'
                f'  see docs/troubleshooting.md')
            raise SystemExit(1)
        self.client.loop_start()
        self.get_logger().info(f'publishing /cmd_vel to mqtt {host}:{port} {self.topic}')

        self.create_subscription(Twist, 'cmd_vel', self.on_cmd_vel, 10)

    def on_cmd_vel(self, msg: Twist):
        # A Twist has six numbers. A two-wheeled robot on a flat floor
        # can only obey two of them, so we send only those.
        payload = json.dumps({
            'lin': round(msg.linear.x, 3),
            'ang': round(msg.angular.z, 3),
        })
        self.client.publish(self.topic, payload)

    def destroy_node(self):
        # Leave the robot stopped, not coasting.
        self.client.publish(self.topic, json.dumps({'lin': 0.0, 'ang': 0.0}))
        self.client.loop_stop()
        self.client.disconnect()
        super().destroy_node()


def main():
    rclpy.init()
    node = MqttBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

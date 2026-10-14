#!/usr/bin/env python3
"""
LESSON 6 -- the MQTT gateway.

Points the opposite way to mqtt_bridge:

    anything --MQTT--> mqtt_teleop --/cmd_vel--> esp32_robot

Lots of things speak MQTT and cannot speak ROS 2 -- a terminal running
mosquitto_pub (lesson 6), a phone app (lesson 7), a sensor somewhere
else entirely. This node translates whatever arrives on an MQTT topic
into the Twist messages the robot already understands.

The robot's firmware does not change at all; as far as it can tell,
someone is just publishing to /cmd_vel.

    ros2 run teleop mqtt_teleop --ros-args -p host:=192.168.1.100
"""
import json

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import paho.mqtt.client as mqtt

# What each button on the phone means, in m/s and rad/s.
LETTERS = {
    'F': (0.20, 0.0),
    'B': (-0.20, 0.0),
    'L': (0.0, 1.5),
    'R': (0.0, -1.5),
    'S': (0.0, 0.0),
}

PUBLISH_HZ = 10.0
SILENCE_TIMEOUT = 1.0   # seconds before we assume the phone went away


def make_client():
    """paho-mqtt 2.x needs an argument that 1.x does not accept."""
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        return mqtt.Client()


class MqttTeleop(Node):
    def __init__(self):
        super().__init__('mqtt_teleop')

        self.declare_parameter('host', '192.168.1.100')
        self.declare_parameter('port', 1883)
        self.declare_parameter('robot_id', 'robot1')

        host = self.get_parameter('host').value
        port = self.get_parameter('port').value
        robot_id = self.get_parameter('robot_id').value
        self.topic = f'robot/{robot_id}/cmd'

        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.lin = 0.0
        self.ang = 0.0
        self.last_seen = self.get_clock().now()

        self.client = make_client()
        self.client.on_message = self.on_mqtt
        try:
            self.client.connect(host, port, keepalive=60)
        except OSError as exc:
            self.get_logger().error(
                f'cannot reach the MQTT broker at {host}:{port} ({exc.strerror}).\n'
                f'  is the broker running?      systemctl status mosquitto\n'
                f'  is this the right address?  hostname -I\n'
                f'  see docs/troubleshooting.md')
            raise SystemExit(1)
        self.client.subscribe(self.topic)
        self.client.loop_start()

        # Republish steadily rather than only when the phone sends
        # something. The robot stops if it stops hearing commands, and
        # a phone button only fires on press and release.
        self.create_timer(1.0 / PUBLISH_HZ, self.tick)

        self.get_logger().info(f'{self.topic} (mqtt)  ->  /cmd_vel (ros 2)')

    # Runs on the MQTT library's thread, not the ROS one.
    def on_mqtt(self, client, userdata, message):
        text = message.payload.decode(errors='replace').strip()

        if text.upper() in LETTERS:
            self.lin, self.ang = LETTERS[text.upper()]
        else:
            try:
                data = json.loads(text)
                self.lin = float(data.get('lin', 0.0))
                self.ang = float(data.get('ang', 0.0))
            except (ValueError, TypeError):
                self.get_logger().warn(f'did not understand: {text!r}')
                return

        self.last_seen = self.get_clock().now()
        self.get_logger().info(f'{text!r} -> lin={self.lin:+.2f} ang={self.ang:+.2f}')

    def tick(self):
        # If the phone goes quiet -- app closed, screen locked, WiFi
        # dropped -- stop asking the robot to move.
        silent = (self.get_clock().now() - self.last_seen).nanoseconds / 1e9
        if silent > SILENCE_TIMEOUT:
            self.lin = 0.0
            self.ang = 0.0

        msg = Twist()
        msg.linear.x = self.lin
        msg.angular.z = self.ang
        self.pub.publish(msg)

    def destroy_node(self):
        self.pub.publish(Twist())
        self.client.loop_stop()
        self.client.disconnect()
        super().destroy_node()


def main():
    rclpy.init()
    node = MqttTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

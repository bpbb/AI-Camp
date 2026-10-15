#!/usr/bin/env python3
"""
บทที่ 6 -- MQTT gateway

    anything --MQTT--> mqtt_teleop --/cmd_vel--> esp32_robot

แปลงข้อความจาก MQTT topic เป็น Twist บน /cmd_vel
เพื่อให้อุปกรณ์ที่พูด MQTT ได้แต่พูด ROS 2 ไม่ได้ (mosquitto_pub ในบทที่ 6,
แอปมือถือในบทที่ 7) ขับหุ่นยนต์ได้ โดยไม่ต้องแก้ firmware

    ros2 run teleop mqtt_teleop
"""
import json

import rclpy
from rclpy.signals import SignalHandlerOptions
from rclpy.node import Node
from geometry_msgs.msg import Twist

from teleop.robot_config import robot_id as configured_robot_id

import paho.mqtt.client as mqtt

# ความหมายของแต่ละปุ่มบนมือถือ (m/s, rad/s)
LETTERS = {
    'F': (0.20, 0.0),
    'B': (-0.20, 0.0),
    'L': (0.0, 2.5),
    'R': (0.0, -2.5),
    'S': (0.0, 0.0),
}

PUBLISH_HZ = 10.0
SILENCE_TIMEOUT = 1.0   # วินาทีที่เงียบก่อนถือว่ามือถือหลุดไป


def make_client():
    """paho-mqtt 2.x ต้องมี argument ที่ 1.x ไม่รองรับ"""
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        return mqtt.Client()


class MqttTeleop(Node):
    def __init__(self):
        super().__init__('mqtt_teleop')

        self.declare_parameter('host', 'localhost')
        self.declare_parameter('port', 1883)
        self.declare_parameter('robot_id', configured_robot_id())

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

        # publish ซ้ำต่อเนื่อง ไม่ใช่เฉพาะตอนมือถือส่งมา
        # เพราะหุ่นยนต์จะหยุดถ้าไม่ได้รับคำสั่ง และปุ่มมือถือส่งแค่ตอนกด/ปล่อย
        self.create_timer(1.0 / PUBLISH_HZ, self.tick)

        self.get_logger().info(f'{self.topic} (mqtt)  ->  /cmd_vel (ros 2)')

    # ทำงานบน thread ของไลบรารี MQTT ไม่ใช่ของ ROS
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
        # ถ้ามือถือเงียบไป (ปิดแอป, ล็อกจอ, WiFi หลุด)
        # ให้หุ่นยนต์หยุด
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
    # ให้ Ctrl+C มาถึงโค้ดของเราก่อน ROS ปิดตัว
    # เพื่อให้ยังส่งคำสั่ง "หยุด" สุดท้ายได้
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
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

#!/usr/bin/env python3
"""
บทที่ 2 -- subscriber

รอรับ message จาก topic แล้วตอบสนองเมื่อมี message เข้ามา

    ros2 run workshop listener

รันตัวนี้ก่อน talker จะยังไม่มีอะไรเกิดขึ้น (แค่รอ) จากนั้นรัน talker
ในอีก terminal แล้วดูว่าทั้งสองเจอกันเองโดยไม่ต้องตั้งค่าใดๆ
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# ต้องตรงกับ TOPIC ของ talker ถ้าแก้ฝั่งเดียว ทั้งสองจะไม่ได้ยินกัน
# (ลองทำผิดแบบนี้ดูโดยตั้งใจ)
TOPIC = 'chatter'


class Listener(Node):
    def __init__(self):
        super().__init__('listener')

        # argument สุดท้ายคือ callback ที่จะถูกเรียกทุกครั้งที่มี message
        # เราไม่ได้เรียก on_message เอง ROS 2 เป็นผู้เรียกให้
        self.create_subscription(String, TOPIC, self.on_message, 10)

        self.get_logger().info(f'listening on /{TOPIC} ... (nothing yet)')

    def on_message(self, msg: String):
        self.get_logger().info(f'heard: "{msg.data}"')


def main():
    rclpy.init()
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
บทที่ 2 -- publisher

ส่ง message ออกไปที่ topic โดยไม่สนว่ามีใครรับอยู่หรือไม่

    ros2 run workshop talker

ลองรันโดยไม่มี listener ดู มันยังทำงานต่อได้ปกติ เพราะ publisher
ไม่รู้ว่ามีใครรับอยู่ นี่คือแนวคิดที่สำคัญที่สุดของ ROS 2
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# ---- ลองแก้ค่าเหล่านี้แล้วดูผลลัพธ์ ----
TOPIC = 'chatter'
MESSAGE = 'hello'
RATE_HZ = 1.0


class Talker(Node):
    def __init__(self):
        # 'talker' คือชื่อ node ที่จะแสดงใน `ros2 node list`
        super().__init__('talker')

        # สร้าง publisher: ระบุชนิด message, topic และจำนวน message
        # ที่เก็บไว้ (queue) เผื่อฝั่งรับทำงานช้า
        self.pub = self.create_publisher(String, TOPIC, 10)

        self.count = 0
        self.create_timer(1.0 / RATE_HZ, self.tick)

        self.get_logger().info(f'publishing on /{TOPIC} at {RATE_HZ} Hz')

    def tick(self):
        msg = String()
        msg.data = f'{MESSAGE} {self.count}'

        self.pub.publish(msg)
        self.get_logger().info(f'sent: "{msg.data}"')
        self.count += 1


def main():
    rclpy.init()
    node = Talker()
    try:
        rclpy.spin(node)          # วนลูปไม่รู้จบ ให้ timer ทำงาน
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

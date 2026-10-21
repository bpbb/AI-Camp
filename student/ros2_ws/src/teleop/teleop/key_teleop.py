#!/usr/bin/env python3
"""
บทที่ 5 -- ขับหุ่นยนต์ด้วยคีย์บอร์ด

อ่านปุ่มคีย์บอร์ดแล้ว publish Twist ไปที่ /cmd_vel
(โครงสร้างเหมือน talker ในบทที่ 2: node + publisher + topic)
Twist บอกแค่ความเร็วเดินหน้าและความเร็วเลี้ยว ไม่ผูกกับหุ่นยนต์ตัวใด
หุ่นยนต์ใดที่เข้าใจ /cmd_vel ก็ขับด้วย node นี้ได้

    w/s : เดินหน้า / ถอยหลัง
    a/d : เลี้ยวซ้าย / ขวา
    space : หยุด
    q : ออก
"""
import sys
import termios
import tty
import select

import rclpy
from rclpy.signals import SignalHandlerOptions
from rclpy.node import Node
from geometry_msgs.msg import Twist

HELP = __doc__

LINEAR_STEP = 0.05   # m/s ที่เพิ่มต่อการกดหนึ่งครั้ง
ANGULAR_STEP = 0.5   # rad/s ที่เพิ่มต่อการกดหนึ่งครั้ง
LINEAR_MAX = 0.30
ANGULAR_MAX = 4.0    # ที่ WHEEL_BASE 0.15 คือหมุนตัวเต็มความเร็ว

LINEAR_MIN = 0.15
ANGULAR_MIN = 2.0


def clamp(value, limit):
    return max(-limit, min(limit, value))


def step(value, delta, low, high):
    """บวก delta โดยข้าม deadzone: จาก 0 กระโดดไป +-low
    และค่าที่ตกอยู่ในช่วง (-low, low) จะกลับเป็น 0"""
    if value == 0.0:
        return clamp(low if delta > 0 else -low, high)
    new = value + delta
    if abs(new) < low - 1e-6:
        return 0.0
    return clamp(new, high)


class KeyTeleop(Node):
    def __init__(self):
        super().__init__('key_teleop')
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.lin = 0.0
        self.ang = 0.0

        # publish 10 ครั้งต่อวินาทีเสมอ แม้ไม่มีการกดปุ่ม
        # เพราะหุ่นยนต์จะหยุดเองถ้าไม่ได้รับคำสั่ง
        self.create_timer(0.1, self.tick)

    def tick(self):
        msg = Twist()
        # TODO(student) 2/2 -- บทที่ 4: ใส่ความเร็วลงใน message
        #   self.lin ใส่ใน msg.linear.x และ self.ang ใส่ใน msg.angular.z
        #   ถ้าไม่ใส่ หุ่นยนต์จะได้รับค่าศูนย์ทั้งหมดและไม่ขยับ
        self.pub.publish(msg)

    def handle_key(self, key):
        if key == 'q':
            return False
        if key == ' ':
            self.lin = 0.0
            self.ang = 0.0

        # w/s เปลี่ยนความเร็วเดินหน้า, a/d เปลี่ยนความเร็วเลี้ยว
        if key == 'w':
            self.lin = step(self.lin, LINEAR_STEP, LINEAR_MIN, LINEAR_MAX)
        elif key == 's':
            self.lin = step(self.lin, -LINEAR_STEP, LINEAR_MIN, LINEAR_MAX)
        elif key == 'a':
            self.ang = step(self.ang, ANGULAR_STEP, ANGULAR_MIN, ANGULAR_MAX)
        elif key == 'd':
            self.ang = step(self.ang, -ANGULAR_STEP, ANGULAR_MIN, ANGULAR_MAX)

        self.get_logger().info(f'lin={self.lin:+.2f}  ang={self.ang:+.2f}')
        return True


def read_key(timeout=0.1):
    """อ่านปุ่มที่กดหนึ่งตัวโดยไม่ต้องรอ Enter"""
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read(1)
    return None


def main():
    # ให้ Ctrl+C มาถึงโค้ดของเราก่อน ROS ปิดตัว
    # เพื่อให้ยังส่งคำสั่ง "หยุด" สุดท้ายได้
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = KeyTeleop()
    print(HELP)

    # ตั้ง terminal เป็น raw mode เพื่อรับปุ่มทันที
    # ต้องคืนค่าเดิมเสมอ ไม่เช่นนั้น shell จะใช้งานไม่ได้
    settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01)
            key = read_key(0.01)
            if key is not None and not node.handle_key(key):
                break
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        # ให้หุ่นยนต์หยุดเสมอก่อนออก
        stop = Twist()
        node.pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

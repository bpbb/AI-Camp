#!/usr/bin/env python3
"""
LESSON 5 -- Driving the robot from the keyboard.

Reads the keyboard and publishes a Twist message on /cmd_vel. It is the
same shape as the talker you ran in lesson 2: a node, a publisher, and
a topic. Only the message type and the topic name have changed.

A Twist says "how fast forward" and "how fast turning". It does not
know anything about your robot: no wheels, no motors, no ESP32. That
is the point. Any robot that understands /cmd_vel can be driven by
this node, and this node never has to change.

    w/s : forward / back
    a/d : turn left / right
    space : stop
    q : quit
"""
import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

HELP = __doc__

LINEAR_STEP = 0.05   # m/s added per key press
ANGULAR_STEP = 0.5   # rad/s added per key press
LINEAR_MAX = 0.30
ANGULAR_MAX = 4.0    # at WHEEL_BASE 0.15 this is a full-speed spin


def clamp(value, limit):
    return max(-limit, min(limit, value))


class KeyTeleop(Node):
    def __init__(self):
        super().__init__('key_teleop')
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.lin = 0.0
        self.ang = 0.0

        # Publish 10 times a second whether or not a key was pressed.
        # The robot stops if it stops hearing from us, so we have to
        # keep talking.
        self.create_timer(0.1, self.tick)

    def tick(self):
        msg = Twist()
        msg.linear.x = self.lin
        msg.angular.z = self.ang
        self.pub.publish(msg)

    def handle_key(self, key):
        if key == 'w':
            self.lin = clamp(self.lin + LINEAR_STEP, LINEAR_MAX)
        elif key == 's':
            self.lin = clamp(self.lin - LINEAR_STEP, LINEAR_MAX)
        elif key == 'a':
            self.ang = clamp(self.ang + ANGULAR_STEP, ANGULAR_MAX)
        elif key == 'd':
            self.ang = clamp(self.ang - ANGULAR_STEP, ANGULAR_MAX)
        elif key == ' ':
            self.lin = 0.0
            self.ang = 0.0
        elif key == 'q':
            return False
        self.get_logger().info(f'lin={self.lin:+.2f}  ang={self.ang:+.2f}')
        return True


def read_key(timeout=0.1):
    """Grab one keypress without waiting for Enter."""
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read(1)
    return None


def main():
    rclpy.init()
    node = KeyTeleop()
    print(HELP)

    # Put the terminal in raw mode so we see keys immediately.
    # We must always put it back, or the shell is left unusable.
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
        # Always leave the robot stopped.
        stop = Twist()
        node.pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

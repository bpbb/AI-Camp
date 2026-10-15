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
from rclpy.signals import SignalHandlerOptions
from rclpy.node import Node
from geometry_msgs.msg import Twist

HELP = __doc__

LINEAR_STEP = 0.05   # m/s added per key press
ANGULAR_STEP = 0.5   # rad/s added per key press
LINEAR_MAX = 0.30
ANGULAR_MAX = 4.0    # at WHEEL_BASE 0.15 this is a full-speed spin

# Below these the motors buzz but the robot doesn't move (deadzone).
# The first press jumps straight here instead of creeping up from zero.
LINEAR_MIN = 0.15
ANGULAR_MIN = 2.0


def clamp(value, limit):
    return max(-limit, min(limit, value))


def step(value, delta, low, high):
    """Add delta, but skip the deadzone: 0 jumps to +-low, and
    anything that would land inside (-low, low) goes back to 0."""
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

        # Publish 10 times a second whether or not a key was pressed.
        # The robot stops if it stops hearing from us, so we have to
        # keep talking.
        self.create_timer(0.1, self.tick)

    def tick(self):
        msg = Twist()
        # TODO(student) 3/4 -- lesson 5: put our speeds into the message.
        #   self.lin goes in msg.linear.x, self.ang in msg.angular.z.
        #   Leave them out and the robot receives all zeros: it never moves.
        self.pub.publish(msg)

    def handle_key(self, key):
        if key == 'q':
            return False
        if key == ' ':
            self.lin = 0.0
            self.ang = 0.0

        # TODO(student) 4/4 -- lesson 5: make w/s/a/d change the speeds.
        #   w faster forward, s slower/backwards  -> change self.lin
        #   a turn left,      d turn right        -> change self.ang
        #   Use step() from the top of this file, for example:
        #       self.lin = step(self.lin, LINEAR_STEP, LINEAR_MIN, LINEAR_MAX)
        #   s and d go the other way: use -LINEAR_STEP and -ANGULAR_STEP.

        self.get_logger().info(f'lin={self.lin:+.2f}  ang={self.ang:+.2f}')
        return True


def read_key(timeout=0.1):
    """Grab one keypress without waiting for Enter."""
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read(1)
    return None


def main():
    # Let Ctrl+C reach our own code instead of shutting ROS down
    # first, so the final "stop" message can still be sent.
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
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

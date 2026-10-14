#!/usr/bin/env python3
"""
LESSON 2 -- a publisher.

It shouts into a topic and does not care who listens.

    ros2 run workshop talker

Try running it with no listener at all. It keeps going quite happily --
a publisher never knows whether anyone is there. That is the single
most important idea in ROS 2.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# ---- CHANGE THESE AND SEE WHAT HAPPENS ----
TOPIC = 'chatter'
MESSAGE = 'hello'
RATE_HZ = 1.0


class Talker(Node):
    def __init__(self):
        # 'talker' is the node name -- what shows up in `ros2 node list`
        super().__init__('talker')

        # Make a publisher: what type of message, which topic, and how
        # many messages to keep if the listener is slow.
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
        rclpy.spin(node)          # loop forever, letting timers fire
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

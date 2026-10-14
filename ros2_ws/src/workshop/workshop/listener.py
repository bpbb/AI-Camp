#!/usr/bin/env python3
"""
LESSON 2 -- a subscriber.

It waits on a topic and reacts to whatever turns up.

    ros2 run workshop listener

Start this one FIRST, before the talker. Nothing happens -- it just
waits. Now start the talker in another terminal and watch them find
each other with no configuration at all.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Must match the talker's TOPIC. Change one and not the other,
# and they stop hearing each other -- a good mistake to make on purpose.
TOPIC = 'chatter'


class Listener(Node):
    def __init__(self):
        super().__init__('listener')

        # The last argument is the function to run for every message.
        # We never call on_message ourselves -- ROS 2 calls it for us.
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

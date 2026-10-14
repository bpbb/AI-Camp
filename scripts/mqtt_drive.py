#!/usr/bin/env python3
"""
APPENDIX -- drive the robot with no ROS 2 at all.

Only works with the MQTT firmware (env:mqtt), not the micro-ROS one.
See docs/appendix-mqtt-robot.md.

Plain Python. It connects to the broker and sends one letter per
keypress.

    python3 scripts/mqtt_drive.py 192.168.1.100 robot1

    w/s : forward / back      a/d : left / right
    space : stop              q : quit
"""
import sys
import termios
import tty

import paho.mqtt.client as mqtt

def make_client():
    """paho-mqtt 2.x needs an argument that 1.x does not accept."""
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        return mqtt.Client()


KEYS = {
    'w': 'F',
    's': 'B',
    'a': 'L',
    'd': 'R',
    ' ': 'S',
}


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else '192.168.1.100'
    robot_id = sys.argv[2] if len(sys.argv) > 2 else 'robot1'
    topic = f'robot/{robot_id}/cmd'

    client = make_client()
    try:
        client.connect(host, 1883, 60)
    except OSError as exc:
        print(f'cannot reach the broker at {host}:1883 ({exc.strerror})')
        print('  is mosquitto running, and is that the right IP?')
        print('  see docs/troubleshooting.md')
        raise SystemExit(1)
    client.loop_start()
    print(f'connected to {host}, sending to {topic}')
    print(__doc__)

    settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while True:
            key = sys.stdin.read(1)
            if key == 'q':
                break
            if key in KEYS:
                client.publish(topic, KEYS[key])
                print(f'sent {KEYS[key]}')
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        client.publish(topic, 'S')   # always leave it stopped
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()

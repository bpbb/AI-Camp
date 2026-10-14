# Appendix: the robot speaking MQTT instead of ROS 2

Not part of the lessons. Two reasons it's here:

1. **Plan B.** If micro-ROS won't cooperate on the day -- a build
   problem, a network that blocks the agent -- this path still gets the
   robot moving in about five minutes.
2. It's a clean example of the same robot with a completely different
   communication stack, for anyone who wants to compare.

```
   lesson 5:   key_teleop --/cmd_vel--> esp32_robot        (micro-ROS)
   this page:  key_teleop --/cmd_vel--> mqtt_bridge --MQTT--> robot
```

Note the bridge points the **opposite way** to `mqtt_teleop` in lesson 6.
There it converts MQTT *into* `/cmd_vel` for a robot that speaks ROS 2;
here it converts `/cmd_vel` *into* MQTT for a robot that doesn't.

## Flash it

Switch the env to **`env:mqtt`** and upload. This replaces the
micro-ROS firmware -- you'll need to re-flash `env:microros` to go back.

Serial Monitor should show:

```
wifi: ok, my address is 192.168.1.42
mqtt: ok, listening on robot/robot1/cmd
```

## Drive it with no ROS 2 at all

```bash
mosquitto_pub -h localhost -t robot/robot1/cmd -m F
mosquitto_pub -h localhost -t robot/robot1/cmd -m S
```

`F` forward, `B` back, `L` left, `R` right, `S` stop. Or with the
keyboard:

```bash
python3 scripts/mqtt_drive.py <broker-ip> robot1
```

It also understands JSON, if you want exact speeds:

```bash
mosquitto_pub -h localhost -t robot/robot1/cmd -m '{"lin":0.1,"ang":0.5}'
```

## Watch the traffic

```bash
mosquitto_sub -h localhost -t 'robot/#' -v
```

`#` means "everything below here". You'll see commands going out and
the robot's status coming back once a second.

## Drive it from ROS 2 anyway

```bash
ros2 run teleop mqtt_bridge --ros-args -p host:=<broker-ip>
ros2 run teleop key_teleop          # in another terminal
```

The same `key_teleop` from lesson 5 now drives an MQTT robot, because
it never knew what was on the other end of `/cmd_vel`.

## What you give up

`ros2 node list` will not show the robot. `rqt_graph` can't draw it.
`ros2 bag` records the bridge's output, not the robot's. Nothing else
in ROS 2 can talk to it without going through code you wrote yourself.

That's the trade, and it's the whole reason lesson 5 exists.

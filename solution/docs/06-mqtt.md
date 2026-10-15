# 6. MQTT: a different way to send messages

You now know one way for programs to talk: ROS 2 topics. This lesson
teaches a second one, and the comparison is the point.

MQTT is everywhere in the real world — thermostats, sensors, factory
machines, phone apps. Almost none of those speak ROS 2. If you want
your robot to talk to anything outside the ROS world, this is usually
how.

## Pub/sub again, but with a postbox

```
     ROS 2                              MQTT
  ┌──────────┐                     ┌──────────┐
  │  talker  │                     │ publisher│
  └────┬─────┘                     └────┬─────┘
       │ /chatter                       │ robot/<ROBOT_ID>/cmd
       │                                v
       │                          ┌──────────┐
       │  (they find each         │  BROKER  │   <-- the difference
       │   other by themselves)   └────┬─────┘
       v                                v
  ┌──────────┐                     ┌──────────┐
  │ listener │                     │subscriber│
  └──────────┘                     └──────────┘
```

Same idea: publishers, subscribers, named topics, and nobody knows who
else is there.

**The difference is the broker.** In ROS 2 the nodes find each other by
themselves. In MQTT everything goes through one server in the middle.
If the broker stops, everything stops.

| | ROS 2 | MQTT |
|---|---|---|
| Needs a server in the middle? | no | yes, the broker |
| Topic name | `/cmd_vel` | `robot/<ROBOT_ID>/cmd` |
| Message | a typed message, e.g. `Twist` | any bytes you like |
| Works over the internet | not really | yes, easily |
| Runs on a phone | no | yes |

That last row is why this lesson exists.

## Try it with no robot at all

Exactly like the talker and listener in lesson 2, but with MQTT tools.
Your computer is already running a broker (`setup_pc.sh` installed it).
If `mosquitto_sub` says "command not found", it didn't -- run
`sudo apt install mosquitto mosquitto-clients`, then see
[troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away)
to let other devices reach it.

Terminal 1 — subscribe and wait:

```bash
mosquitto_sub -t test/hello -v
```

Terminal 2 — publish:

```bash
mosquitto_pub -t test/hello -m "hi there"
```

The message appears in terminal 1. No code, no compiling, no `source`.

The two letters to know:

| | means |
|---|---|
| `-t` | **t**opic -- which postbox |
| `-m` | **m**essage -- what to put in it |

(`-v` on `mosquitto_sub` just prints the topic name next to each
message. No `-h` needed: the broker is on this computer.)

Now try the wildcard. Stop terminal 1 and run:

```bash
mosquitto_sub -t 'test/#' -v
```

`#` means "this topic and everything below it". Publish to
`test/hello`, `test/other`, `test/a/b/c` — you see all of them. There
is no equivalent in ROS 2.

### Compare it to lesson 2

1. Kill the broker: `sudo systemctl stop mosquitto`. Try publishing.
   What happens? Now do the same thought experiment with `talker` and
   `listener` — is there anything you could kill to break them?
2. Start `mosquitto_sub` on a topic nobody publishes to. Does it
   complain? Does `ros2 topic echo` on an unused topic behave the same?
3. Which system would you choose to send a temperature reading from a
   sensor on the other side of the world? Which for two programs on
   one robot?

```bash
sudo systemctl start mosquitto      # put it back when you're done
```

## Now connect it to the robot

Your robot speaks ROS 2, not MQTT. So we put a **gateway** in between:
a node that subscribes to MQTT and publishes `/cmd_vel`.

```
  ┌──────────┐        ┌──────────────┐   /cmd_vel   ┌─────────────┐
  │ anything │ ─MQTT─>│ mqtt_teleop  │ ───────────> │ esp32_robot │
  │ that can │        │  (gateway)   │              │ (unchanged) │
  │ publish  │        └──────────────┘              └─────────────┘
  └──────────┘
```

**No upload needed.** The robot keeps the micro-ROS firmware from
lesson 5 and never sees MQTT. As far as the ESP32 can tell, somebody
is publishing to `/cmd_vel` — and it never asks who.

Start the agent and the robot as in lesson 5, and check that
`ros2 node list` shows `/esp32_robot`.

Then start the gateway:

```bash
ros2 launch teleop mqtt_gateway.launch.py
```

No IP needed: the gateway runs on the same computer as the broker, so
it connects to `localhost`. (Only if the broker is on a *different*
computer, add `host:=<that-computer's-ip>`.) The robot and the phone
still need your real IP -- that goes in `config.h` and the app.

You should see `robot/<ROBOT_ID>/cmd (mqtt)  ->  /cmd_vel (ros 2)`. If it
says `process has died` instead, see
[troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away).

## Drive the robot by typing

```bash
mosquitto_pub -t robot/<ROBOT_ID>/cmd -m F
mosquitto_pub -t robot/<ROBOT_ID>/cmd -m S
```

Replace `<ROBOT_ID>` with the name in `firmware/include/config.h`. If it
is `"test"`, the topic is `robot/test/cmd`. The gateway reads the same
name from `config.h` by itself, so you never type it there. After
changing `ROBOT_ID`, run `colcon build` in `ros2_ws` so the gateway
picks it up.
`F` forward, `B` back, `L` left, `R` right, `S` stop. The gateway
prints what it received and the robot moves -- for about a second,
then it stops by itself. That's on purpose; see "Try this" below.

The gateway printing `'F' -> lin=+0.20` but the robot not moving means
the problem is after the gateway: is the robot running the **micro-ROS**
firmware (not the motor test), is the agent running, and does
`ros2 node list` show `/esp32_robot`?

It also understands JSON, for exact speeds:

```bash
mosquitto_pub -t robot/<ROBOT_ID>/cmd -m '{"lin":0.1,"ang":0.5}'
```

## Watch all three layers at once

Four terminals, and the whole chain is visible:

```bash
mosquitto_sub -t 'robot/#' -v    # the MQTT side
ros2 topic echo /cmd_vel                      # the ROS 2 side
ros2 node list                                # who is involved
rqt_graph                                     # the picture
```

Publish one command and watch it become a Twist, then PWM on two motor
pins.

Notice what `rqt_graph` shows: `mqtt_teleop` publishing to `/cmd_vel`,
and the robot subscribing. The MQTT half is **invisible** to ROS 2 —
the graph stops at the gateway, exactly as it stopped at the broker in
the diagram above.

## Try this

1. Run `key_teleop` **and** publish over MQTT at the same time. Both
   end up on `/cmd_vel`. What does the robot do? Is that a bug?
2. Send `F` once and don't send anything else. The robot twitches and
   stops. Why? There are now **two** timeouts in the chain — one in the
   gateway, one in the firmware. Find both.
3. Send nonsense: `mosquitto_pub ... -m banana`. What does the gateway
   do? Should a gateway crash on bad input?
4. Why can't you just run `ros2 topic echo` and see the MQTT messages?

## Why not put MQTT on the robot itself?

You could. But then the robot stops being a ROS 2 node: `ros2 bag` can't record it,
`rqt_graph` can't draw it, and nothing else in ROS 2 can drive it.

Putting the gateway on the computer instead keeps the robot in the ROS
2 world and still lets the outside world in. That trade — a translator
at the boundary, rather than changing what your system speaks — is one
of the most common decisions in real engineering.

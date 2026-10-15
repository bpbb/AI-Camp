# 5. The robot becomes a ROS 2 node

In lesson 2 you had a talker and a listener on your computer. Today the
listener is the robot.

```
  ┌────────────┐      /cmd_vel      ┌─────────────┐
  │ key_teleop │ ─────────────────> │ esp32_robot │
  └────────────┘   Twist message    └─────────────┘
   your keyboard                      the ESP32
```

Same idea as `/chatter`. Different topic name, different message type,
and one of the nodes happens to be a microcontroller on wheels.

## Why micro-ROS and not just ROS 2

ROS 2 cannot run on an ESP32 -- not "it's slow", it genuinely does not
fit. A minimal ROS 2 node wants tens of megabytes and a full operating
system. The ESP32 has about **320 KB of RAM**.

**micro-ROS** is a small version built for microcontrollers. You write
almost the same code, but it talks to an **agent** on your computer, and
the agent is what puts it on the real ROS 2 graph.

```
   ESP32                    computer
  ┌────────┐   WiFi       ┌────────┐     ┌──────────────────┐
  │ micro- │ ───────────> │ agent  │ ──> │  the ROS 2 graph │
  │  ROS   │              │        │     │  (your other     │
  └────────┘              └────────┘     │   nodes)         │
                                         └──────────────────┘
```

The agent must be running **before** the robot connects. If the ESP32
boots first it waits and keeps retrying -- that's the `WAITING_AGENT`
state in the firmware.

## The message: Twist

Driving a robot needs two numbers: how fast forward, and how fast
turning. ROS 2 has a standard message for exactly this,
`geometry_msgs/msg/Twist`:

```
linear.x   metres per second forward   (negative = backwards)
angular.z  radians per second turning  (positive = left)
```

A Twist actually carries six numbers, for robots that can move in 3D. A
robot on a floor with two wheels can only use those two.

This is the payoff of using ROS 2: **every wheeled robot in the world
understands a Twist on `/cmd_vel`.** Your robot is about to join that
club.

## Set your team's domain

Remember the number from lesson 2. It goes in two places.

In `firmware/include/config.h`:

```c
#define ROS_DOMAIN_ID  7
```

And in every terminal on your computer:

```bash
export ROS_DOMAIN_ID=7
```

**They must match**, and they must be different from every other team's.
Get this wrong and you will drive someone else's robot -- which is funny
for about two minutes.

## Upload

**Build this one from a terminal, with the script:**

```bash
./scripts/build_firmware.sh microros upload
```

Not the VS Code build button -- at least not the first time. Here is why.

This build compiles micro-ROS from source, including its own private
copy of the ROS build tools. In lesson 1 you added ROS 2 to your
`~/.bashrc` so it loads in every terminal, and that is exactly what
confuses it: the build finds *your* ROS instead of its own, and fails
with a wall of CMake errors about `rosidl_runtime_cpp` naming a
workspace that has nothing to do with this project.

`build_firmware.sh` clears those settings before building, so it just
works. (The VS Code button is fine too, as long as you launched VS Code
from the applications menu rather than by typing `code .` in a terminal
that already had ROS loaded.)

The micro-ROS compile takes **2-3 minutes**. If this is the very first
firmware you have ever built on this machine, add about 8 minutes for
downloading the ESP32 compiler. After that everything is cached and
rebuilds take seconds.

Before uploading, check `firmware/include/config.h` has your WiFi,
your computer's IP (`hostname -I`, first address) in `AGENT_IP`, and
your domain number. If the upload fails, see
[troubleshooting.md](troubleshooting.md#the-board-wont-upload).

## Every terminal from here on

Each new terminal you open in lessons 5-7 needs these two lines first
(skip the `source` line if you added it to `~/.bashrc` in lesson 1):

```bash
source ~/AI-Camp/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=7
```

## Start the agent

Terminal 1:

```bash
./scripts/start_agent.sh
```

Leave it running. When the ESP32 connects you'll see a burst of
`session established` messages. If you see nothing, the robot can't
reach your computer -- check [troubleshooting.md](troubleshooting.md).

## Drive

Terminal 2 (with the two lines above):

```bash
ros2 run teleop key_teleop
```

`w` `a` `s` `d` to drive, space to stop, `q` to quit.

## Prove the ESP32 is really a node

This is the moment the lesson is about. With everything running, in
terminal 3:

```bash
ros2 node list
```
```
/key_teleop
/esp32_robot      <-- that is the microcontroller
```

```bash
ros2 topic echo /heartbeat
```

A counter, published by the ESP32 itself, arriving on your computer.

```bash
rqt_graph
```

The robot is drawn in the picture next to your keyboard node. To the
rest of ROS 2 it is indistinguishable from a program on the computer.

## Drive it without the keyboard

Nothing cares where a Twist comes from:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.1}, angular: {z: 0.0}}' -r 10
```

`-r 10` means repeat ten times a second. Try leaving it off: the robot
twitches once and stops. That's the safety timeout in the firmware --
no command for 500 ms and the motors stop. Find it in
[main.cpp](../firmware/src/microros/main.cpp).

## Record and replay

```bash
ros2 bag record /cmd_vel      # drive around, then Ctrl+C
ros2 bag play <folder>        # the robot repeats what you did
```

You didn't write that tool. It works because your robot speaks the same
language as everything else in ROS 2.

## Try this

1. Kill the agent while driving. What does the robot do? Restart it --
   does it recover without pressing reset?
2. Run **two** `key_teleop` nodes at once. What happens? What does
   `ros2 topic hz /cmd_vel` say?
3. Change your `ROS_DOMAIN_ID` on the computer but not the robot. What
   does `ros2 node list` show? Why is this a useful thing to know?
4. `ros2 topic hz /heartbeat` -- is it exactly 1 Hz? Why not?

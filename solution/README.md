# Two-wheeled robot with ROS 2

A teaching project. Students learn ROS 2 from the terminal up, build a
small two-wheeled robot driven by an ESP32, and make it a real ROS 2
node with micro-ROS. If there's time, they drive it from a phone.

Everything is done in VS Code. No Arduino IDE.

## The lessons

| | | needs a robot? |
|---|---|---|
| 0 | [Setting up](docs/00-setup.md) | no |
| 1 | [Surviving the terminal](docs/01-terminal.md) | no |
| 2 | [Nodes, topics, publishers, subscribers](docs/02-ros2-basics.md) | no |
| 3 | [Building the robot](docs/03-hardware.md) | — |
| 4 | [Does the hardware work?](docs/04-motor-test.md) | yes, no network |
| 5 | [The robot becomes a ROS 2 node](docs/05-micro-ros.md) | yes |
| 6 | [MQTT: a different way to send messages](docs/06-mqtt.md) | yes |
| 7 | [Driving from a phone](docs/07-phone-teleop.md) | yes, optional |
| | [When it doesn't work](docs/troubleshooting.md) | read before asking |

The order is deliberate. Lessons 1–2 need no hardware at all, so a late
delivery doesn't block the start. Lesson 4 proves the wiring with no
network involved, so that when something breaks in lesson 5 you already
know it isn't the motors. Lesson 6 teaches MQTT against the robot they
already have working, and lesson 7 is then only an app to configure —
so it's safe to drop if the clock runs out.

## What's here

```
firmware/                one PlatformIO project, two programs
  include/config.h         <- edit this first
  include/motor.h          turning "forward + turn" into two wheel speeds
  src/motortest/           lesson 4: no network, just motors
  src/microros/            lesson 5: a real ROS 2 node

ros2_ws/src/
  workshop/                lesson 2: talker and listener to play with
    workshop/talker.py       a publisher
    workshop/listener.py     a subscriber
  teleop/
    teleop/key_teleop.py     keyboard -> /cmd_vel
    teleop/mqtt_teleop.py    lessons 6-7: MQTT -> /cmd_vel gateway

scripts/
  setup_pc.sh              installs everything on the computer
  check_setup.sh           confirms a machine matches the reference setup
  build_firmware.sh        builds/uploads ESP32 firmware (ROS-free env)
  start_agent.sh           runs the micro-ROS agent

docs/                    the lessons
```

<!-- TEACHER-ONLY -->
## Teacher and student versions

This `solution/` folder is the **full** version, with every part
working. Students get a copy with four short gaps to fill in, marked
`TODO(student)`:

```bash
python3 scripts/make_student.py      # writes ../student/
```

```
AI-Camp/
  solution/    the full version -- edit this one
  student/     generated from it -- hand this out
```

Hand out the contents of `student/` as the students' `~/AI-Camp`. It
also resets `config.h` to placeholder WiFi, IP and domain.

The gaps are marked in the full code between `STUDENT-BEGIN` and
`STUDENT-END` comments. Inside them, comments stay as hints,
`STUDENT-STUB:` lines become placeholder code, and the solution is
removed. Always edit the full version and run the script again. Never
edit `student/` by hand; it's rebuilt from scratch every time.

Students get the **Thai** docs: `docs-th/` becomes their `docs/`, and
the English `docs/` here is the teacher's copy. When you change a lesson,
change it in both, or the student version falls behind.
<!-- /TEACHER-ONLY -->

## Quick start

```bash
./scripts/setup_pc.sh                  # note the IP it prints
$EDITOR firmware/include/config.h      # put that IP in, and your WiFi
cd ros2_ws && colcon build && source install/setup.bash
cd .. && ./scripts/check_setup.sh      # should be all green
```

Set one machine up this way, check it, then clone the image to the
rest. `check_setup.sh` re-run on lesson day catches the things that
drift: the computer's IP, group membership, and a stopped broker.

## Running a class of several robots

Every team needs their own two numbers, or they will drive each other's
robots:

- **`ROBOT_ID`** in `config.h` — separates MQTT topics
- **`ROS_DOMAIN_ID`** in `config.h` *and* `export`ed in every terminal —
  separates ROS 2 graphs entirely

Students meet `ROS_DOMAIN_ID` in lesson 2, before it can cause any
damage.

## Requirements

- Ubuntu 24.04 — `setup_pc.sh` installs ROS 2 Jazzy if needed
  (22.04 + Humble also works; the scripts detect which you have)
- VS Code with the PlatformIO, ROS and Python extensions
- No docker. `setup_pc.sh` builds the micro-ROS agent from source,
  since there is no apt package for it.
- ESP32 dev board, L298N or TB6612 motor driver, two DC motors, a
  battery, a caster wheel
- For lesson 7: an Android or iOS phone with **IoT MQTT Panel**

Versions in `firmware/platformio.ini` are pinned deliberately. Leave
them alone unless you know why you're changing them.

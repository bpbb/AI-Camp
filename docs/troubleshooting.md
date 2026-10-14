# When it doesn't work

Work down the list. Most problems are in the first three.

## VS Code says "Can not find working Python 3.6+ Interpreter"

Your Python is almost certainly fine. Check it:

```bash
python3 --version        # 3.12 on Ubuntu 24.04 -- PlatformIO needs 3.6+
```

The real problem is usually a missing package, not a missing Python.
The PlatformIO extension builds itself a virtual environment on first
run, and that needs `python3-venv`:

```bash
sudo apt install python3-venv
```

Then reload VS Code (**Ctrl+Shift+P** -> "Developer: Reload Window").

Test whether that was it:

```bash
python3 -m venv /tmp/test && echo works && rm -rf /tmp/test
```

If that prints an error about `ensurepip`, the package is missing.

> **Do not reinstall or replace Python to fix this.** On Ubuntu,
> `/usr/bin/python3` is what `apt` and ROS 2 are built on.
> Replacing it can leave you unable to install anything -- including
> whatever you would need to undo it. Each ROS 2 release is built
> against one specific Python, so changing it breaks the course.

## micro-ROS firmware: CMake errors about `rosidl_runtime_cpp`

If the error names a workspace that isn't this project -- something like
`/home/you/some_other_ws/install/...` -- your shell has ROS 2 loaded and
the firmware build is finding it instead of its own copy.

Build with the script, which clears those settings first:

```bash
./scripts/build_firmware.sh microros upload
```

Then delete the half-finished build and start clean:

```bash
rm -rf firmware/.pio
```

Same thing causes the VS Code build button to fail, if you started VS
Code by typing `code .` in a terminal that had ROS loaded. Launch it
from the applications menu instead, or just use the script.

## micro-ROS firmware: "No module named 'catkin_pkg'"

The lesson-5 build compiles micro-ROS from source, and it does that with
**PlatformIO's own Python**, not the system one. That virtualenv cannot
see ROS packages installed system-wide, so it needs its own copy of the
build tools:

```bash
~/.platformio/penv/bin/python -m pip install catkin_pkg "empy==3.3.4" lark
```

`scripts/setup_pc.sh` does this for you; you only hit it if PlatformIO
was installed by hand.

The `empy` pin matters. The ROS 2 message generators use the empy 3.x
API, and empy 4.x changed it — an unpinned install fails later and much
less clearly.

Check what the venv has:

```bash
~/.platformio/penv/bin/python -m pip list | grep -Ei 'catkin|empy|lark'
```

If you changed anything here, delete `firmware/.pio/` and build again —
the failed build is cached otherwise.

## The board won't upload

- Charge-only USB cable. Try another one.
- Hold the **BOOT** button while the upload starts.
- Serial Monitor still open from last time -- close it, it holds the port.
- `Permission denied /dev/ttyUSB0`:
  ```bash
  sudo usermod -aG dialout $USER
  ```
  then **log out and back in**.

## WiFi never connects

- SSID and password are case sensitive.
- The ESP32 cannot see 5 GHz networks. It must be a 2.4 GHz one.
- Phone hotspots often work when school WiFi doesn't.

## MQTT: `rc=-2`

The broker address is wrong or unreachable.

- Is `MQTT_HOST` the computer's current IP? It changes when you reconnect.
  Check with `hostname -I`.
- Is the broker listening to the network, not just itself?
  ```bash
  sudo ss -tlnp | grep 1883     # want 0.0.0.0:1883, not 127.0.0.1:1883
  ```
  `scripts/setup_pc.sh` fixes this.
- From the robot's network, can you reach the computer at all? `ping` it.

## The robot doesn't move, but the Serial Monitor looks fine

- The motor battery is flat or not switched on. The ESP32 runs happily
  off USB while the motors have no power at all.
- The GND wire between the ESP32 and the motor driver is missing. See
  [03-hardware.md](03-hardware.md).
- `MIN_DUTY` in `motor.h` is too low for your motors. Every command is
  scaled to sit above it, but if your motors need more push than the
  default 60, even a full-speed request will only buzz. Raise it until
  the robot moves, then stop -- too high and slow speeds vanish.

## It moves for a moment, then stops

Working as designed. The safety timeout stops the motors when no
command has arrived for 500 ms. Send commands repeatedly (`-r 10` with
`ros2 topic pub`) rather than once.

## `ros2 run` says package not found

You forgot:

```bash
source install/setup.bash
```

In every new terminal. Every time.

## I'm driving someone else's robot

Two teams sharing a `ROS_DOMAIN_ID`, or sharing a `ROBOT_ID`. Both must
be unique per team, and the domain must match between
`firmware/include/config.h` and every terminal on your computer.

```bash
echo $ROS_DOMAIN_ID                          # your computer
grep ROS_DOMAIN_ID firmware/include/config.h # your robot
```

Changing it in `config.h` means re-uploading -- it's compiled in.

## micro-ROS builds but the node never appears

- Is the agent running? Start it before the robot.
- If `start_agent.sh` says the agent is not built, run
  `./scripts/setup_pc.sh` -- it builds it from source, which takes a
  few minutes.
- Does `ROS_DOMAIN_ID` match in all three places -- your shell, the
  agent's shell, and `config.h`? A mismatch connects the session and
  then shows nothing in `ros2 node list`.
- Does `board_microros_distro` in `platformio.ini` match the ROS 2 on
  your computer? `jazzy` on Ubuntu 24.04, `humble` on 22.04. A mismatch
  connects and then goes quiet -- the most confusing failure of the
  whole project. `./scripts/check_setup.sh` checks this for you.
- Same subnet? The robot and the computer must be able to reach each
  other; check with `ping` from one to the other.
- Delete `.pio/` and rebuild if you changed the distro or transport.
  That setting is baked in at build time.

## The phone can't reach the broker

- Phone on the same WiFi as the computer?
- Broker address in the app is the computer's IP, not `localhost`.
- Check the broker sees it:
  ```bash
  mosquitto_sub -h localhost -t 'robot/#' -v
  ```
  Press a button. Nothing appearing means the problem is phone-to-broker,
  not broker-to-robot.

## The robot twitches and stops when I hold a phone button

"Repeat payload until released" is off. One message on press isn't
enough -- the firmware stops after 500 ms of silence. See
[07-phone-teleop.md](07-phone-teleop.md).

## Everything looked fine yesterday

Your computer's IP changed. Re-check `hostname -I` and update
`config.h`. `./scripts/check_setup.sh` catches this.

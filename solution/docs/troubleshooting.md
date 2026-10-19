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

## micro-ROS firmware: "cannot open .../.platformio/penv/bin/activate"

The micro-ROS library always builds inside `~/.platformio/penv`, and
this PC doesn't have it (PlatformIO was installed another way, such as
pipx). Run setup again; it creates the venv and moves PlatformIO there:

```bash
bash scripts/setup_pc.sh
```

Then delete `firmware/.pio` so the failed build isn't reused, and build again.

## micro-ROS firmware: "No module named 'catkin_pkg'"

The lesson-5 build compiles micro-ROS from source, and it does that with
**PlatformIO's own Python**, not the system one. That virtualenv cannot
see ROS packages installed system-wide, so it needs its own copy of the
build tools:

```bash
bash scripts/setup_pc.sh      # installs them into the right Python
```

Which Python that is depends on how PlatformIO was installed (pipx on
Ubuntu 24.04, the system Python on 22.04, or the VS Code extension's own
venv), so let the setup script work it out; running it again is safe.

The `empy` pin matters. The ROS 2 message generators use the empy 3.x
API, and empy 4.x changed it — an unpinned install fails later and much
less clearly.

Check:

```bash
./scripts/check_setup.sh      # checks the Python that runs pio
```

If you changed anything here, delete `firmware/.pio/` and build again —
the failed build is cached otherwise.

## Starting a build fresh: `clean` or delete `.pio`?

Two ways to throw away an old build. They are not the same.

```bash
./scripts/build_firmware.sh microros clean   # light
rm -rf firmware/.pio                         # everything
```

| | Deletes | Rebuild takes | Use it when |
|---|---|---|---|
| `clean` | that program's compiled files only | seconds | a build acts strangely and you want a fresh compile |
| `rm -rf firmware/.pio` | everything, including the downloaded micro-ROS library | several minutes | you changed `board_microros_distro` or the transport in `platformio.ini`, or a micro-ROS build error won't go away |

`clean` keeps the micro-ROS library, and the ROS 2 version is built
into that library. So after changing the distro, `clean` changes
nothing; only deleting `.pio` does.

## `Permission denied` when running `./scripts/...`

The scripts lost their execute permission, which happens when the
project is copied by USB drive, ZIP or a cloud drive. From the project
folder:

```bash
chmod +x scripts/*.sh
```

Or run one through `bash` directly: `bash scripts/setup_pc.sh`.
Copying with `git clone` keeps the permission.

## `PlatformIO (pio) not found` or `env: 'pio': No such file or directory`

PlatformIO isn't installed, usually because `setup_pc.sh` stopped early
(for example on an apt error). Fix that error, then run it again; it
skips what is already done:

```bash
./scripts/setup_pc.sh
```

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
- `config.h` still says `MyNetwork` / `changeme`? Put your real WiFi in
  and upload again.
- The ESP32 cannot see 5 GHz networks. It must be a 2.4 GHz one.
- Open guest WiFi with a login page won't work, and neither will
  networks that ask for a username *and* password (WPA2-Enterprise).
- Phone hotspots often work when school WiFi doesn't.

## Only one wheel moves, with no error

The pins in `firmware/include/motor.h` don't match your wiring. Compare
them with the table in [03-hardware.md](03-hardware.md) and fix
whichever is wrong, then upload the motor test again.

## Both wheels run backwards

Swap `L_IN1`/`L_IN2` and `R_IN1`/`R_IN2` in `motor.h` and upload, or
swap each motor's two wires at the driver.

## `mosquitto_sub: command not found`

The broker isn't installed. Use apt, not snap:

```bash
sudo apt install mosquitto mosquitto-clients
```

Then do the next section too.

## MQTT: the gateway dies straight away

`[ERROR] [mqtt_teleop-1]: process has died ... exit code 1` means it
couldn't reach the broker. Usually the broker is only listening to the
computer itself:

```bash
ss -ltn | grep 1883      # 127.0.0.1:1883 only = the problem
```

Let other devices in:

```bash
echo -e "listener 1883\nallow_anonymous true" | sudo tee /etc/mosquitto/conf.d/workshop.conf
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

Now `ss` should show `0.0.0.0:1883`. If you passed `host:=...`, drop
it -- the default (`localhost`) is right when the broker is on this PC.

## The robot doesn't move, but the Serial Monitor looks fine

- The motor battery is flat or not switched on. The ESP32 runs happily
  off USB while the motors have no power at all.
- The GND wire between the ESP32 and the motor driver is missing. See
  [03-hardware.md](03-hardware.md).
- `MIN_DUTY` in `motor.h` is too low for your motors. Every command is
  scaled to sit above it, but if your motors need more push than the
  default 60, even a full-speed request will only buzz. Raise it until
  the robot moves, then stop -- too high and slow speeds vanish.

## The gateway prints the command but the robot does nothing

The MQTT side works; the problem is between the computer and the robot.

- Is the robot running the **micro-ROS** firmware? The motor test
  ignores every command. Upload `microros`.
- Is the agent running (`./scripts/start_agent.sh`)?
- Does `ros2 node list` show `/esp32_robot`? If not, see "micro-ROS
  builds but the node never appears" below.

## It moves for a moment, then stops

Working as designed. The safety timeout stops the motors when no
command has arrived for 500 ms. Send commands repeatedly (`-r 10` with
`ros2 topic pub`) rather than once.

## `ros2 run` / `ros2 launch` says package not found

Either the workspace was never built, or this terminal hasn't loaded it:

```bash
cd ~/Documents/AI-Camp/solution/ros2_ws
colcon build                 # once, and after changing Python code
source install/setup.bash    # or put it in ~/.bashrc (lesson 1)
```

If it's in `~/.bashrc` but still not found, you built the workspace
*after* opening this terminal. Open a new one.

## I'm driving someone else's robot

Two teams sharing a `ROS_DOMAIN_ID`, or sharing a `ROBOT_ID`. Both must
be unique per team, and the domain must match between
`firmware/include/config.h` and every terminal on your computer.

```bash
echo $ROS_DOMAIN_ID                          # your computer
grep ROS_DOMAIN_ID ~/.bashrc                 # where it comes from
grep ROS_DOMAIN_ID firmware/include/config.h # your robot
```

Two `ROS_DOMAIN_ID` lines in `~/.bashrc` (one from another project)?
The last one wins. Keep one.

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
  mosquitto_sub -t 'robot/#' -v
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

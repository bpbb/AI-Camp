# 0. Setting up

Do this the day before, not on the morning of the first lesson. The
first firmware build downloads a lot and takes about 10 minutes.

The lessons go in this order, and each one assumes the last:

| | | |
|---|---|---|
| 1 | Terminal | no ROS, no robot |
| 2 | Nodes and topics | computer only |
| 3 | Build the robot | no software |
| 4 | Motor test | no network |
| 5 | micro-ROS | the robot joins the graph |
| 6 | MQTT | a second way to send messages |
| 7 | Phone teleop | optional |

Nothing needs the robot until lesson 3, so a late hardware delivery
does not block the start.

## What you need

- A computer with **Ubuntu 24.04**
  (`setup_pc.sh` installs ROS 2 Jazzy if it isn't there yet)
- **VS Code**
- An ESP32 dev board and a USB cable (a *data* cable -- charge-only
  cables will not work and give no useful error)

## 1. VS Code extensions

Open the project folder in VS Code. It will offer to install the
recommended extensions -- say yes. If it doesn't, install these by hand:

| Extension | What it's for |
|---|---|
| PlatformIO IDE | building and uploading ESP32 firmware |
| ROS | ROS 2 support |
| Python | the teleop nodes |

## 2. Computer packages

```bash
./scripts/setup_pc.sh
```

This installs the MQTT broker, the Python MQTT library, and builds the
micro-ROS agent from source -- there is no ready-made package for it.
That takes a few minutes and only happens once per machine.

At the end it prints your computer's IP address. **Write that number
down**, you need it in the next step.

No docker anywhere. Everything runs directly on the machine.

> On Ubuntu 24.04, `pip3 install --user` is refused with
> **`error: externally-managed-environment`**. That is normal and has
> nothing to do with your Python version -- 24.04 simply protects the
> system Python. `setup_pc.sh` uses `pipx` and `apt` instead, so you
> should not hit it. If you do, do not reinstall Python.

## 3. Tell the robot where your computer is

Open `firmware/include/config.h` and fill in:

```c
#define WIFI_SSID      "..."      // your network
#define WIFI_PASSWORD  "..."
#define ROBOT_ID       "robot1"   // your team name
#define AGENT_IP       "..."      // the IP from step 2
#define MQTT_HOST      "..."      // the same IP
#define ROS_DOMAIN_ID  0          // your team's number -- see lesson 2
```

Every team needs a **different** `ROBOT_ID` and a **different**
`ROS_DOMAIN_ID`, or you will drive each other's robots.

## 4. Build the ROS 2 workspace

```bash
cd ros2_ws
colcon build
source install/setup.bash
```

You need that `source` line in **every new terminal**. Forgetting it is
the single most common reason `ros2 run` says "package not found".

## 5. Warm up the firmware build

```bash
cd firmware
pio run -e motortest
pio run -e microros     # this is the slow one, ~10 minutes
```

Both should end in `SUCCESS`.

Do the `microros` one **before** the lesson, not during it. It compiles
micro-ROS from source and downloads a lot. Twenty computers doing that at
once on the same WiFi is a bad afternoon. Once it's built it's cached,
and later builds take seconds.

## 6. Check it

```bash
./scripts/check_setup.sh
```

Everything should be green. Re-run it on the morning of a lesson too --
it catches the things that drift overnight, like the computer's IP
address changing.

## A note about WiFi

The robot and your computer must be on the **same network**, and that
network must allow devices to talk to each other. Many school and
guest networks block this on purpose ("client isolation"). If nothing
works later and everything looks right, this is usually why -- use a
dedicated router.

# 7. Driving from a phone

Optional, if there's time.

Nothing new to build. In lesson 6 you drove the robot by typing
`mosquitto_pub`. A phone app does exactly the same thing — it just has
buttons instead of a keyboard.

```
  ┌────────┐        ┌──────────────┐   /cmd_vel   ┌─────────────┐
  │ phone  │ ─MQTT─>│ mqtt_teleop  │ ───────────> │ esp32_robot │
  │  app   │        │  (gateway)   │              │ (unchanged) │
  └────────┘        └──────────────┘              └─────────────┘
       ^
       └── the only new part. Everything else is lesson 6.
```

## Install the app

**IoT MQTT Panel**, on Android or iOS.

Add a connection:

| | |
|---|---|
| Broker address | your computer's IP (`hostname -I`) |
| Port | 1883 |
| Client ID | anything unique, e.g. `phone1` |
| Username / password | leave empty |

The phone must be on the **same WiFi** as your computer.

### Check it before going further

On your computer:

```bash
mosquitto_sub -h localhost -t 'test/#' -v
```

Add a temporary Button panel in the app publishing `hello` to
`test/phone`, and press it. If the message appears on your computer,
the phone is talking to the broker and the rest is easy. If it
doesn't, fix that first — nothing else can work until it does.

## Add the driving buttons

Five **Button** panels, all publishing to the same topic:

```
robot/robot1/cmd          (use your own ROBOT_ID)
```

| Button | Payload on press | Payload on release | Repeat while held |
|---|---|---|---|
| Forward | `F` | `S` | on |
| Back | `B` | `S` | on |
| Left | `L` | `S` | on |
| Right | `R` | `S` | on |
| STOP | `S` | | off |

These are the same letters you typed in lesson 6. The gateway cannot
tell the difference between your thumb and your keyboard.

**Turn on "repeat payload until released."** This matters: the robot
stops if it hears nothing for 500 ms, so a single message on press
would make it twitch and stop. Repeating keeps it fed while your thumb
is down, and the release payload stops it the instant you let go.

You found both of those timeouts in lesson 6. Here's what they were for.

### A speed slider (optional)

Add a **Slider** panel on the same topic, min `-0.3`, max `0.3`,
publishing JSON:

```json
{"lin": <value>, "ang": 0}
```

Set **live = true** so it publishes as you drag rather than only when
you let go.

> Setting up five widgets by hand is slow for a whole class. Build it
> once on one phone, then use the app's **export configuration**
> feature and share that file — everyone else imports it.

## Run it

Agent, robot and gateway all running as in lesson 6:

```bash
export ROS_DOMAIN_ID=7
ros2 launch teleop mqtt_gateway.launch.py host:=<your-computer-ip>
```

Press a button. You should see it arrive:

```
[INFO] [mqtt_teleop]: 'F' -> lin=+0.20 ang=+0.00
```

And the robot moves.

## Try this

1. Drive with the phone and `key_teleop` at the same time. Who wins?
2. Close the app mid-drive. How long until the robot stops? Which
   timeout stopped it — the gateway's or the firmware's?
3. Two phones, same broker, same topic. What happens? How would you
   give each team their own robot?
4. Walk out of WiFi range while holding Forward. What should happen,
   and what actually does?
5. Your robot is a ROS 2 node, and your phone cannot speak ROS 2 — yet
   the phone drives it. Draw the chain from thumb to motor and label
   which parts speak which language.

## Where to go next

The robot understands `/cmd_vel`, which means anything that publishes
`/cmd_vel` can drive it. That includes programs you haven't written
yet: a node that follows a line, avoids obstacles, or takes a path from
Nav2. None of them need to know the robot has an ESP32 in it.

That is what you bought by making it a ROS 2 node in lesson 5.

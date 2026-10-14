# 3. Building the robot

A two-wheeled robot. Two motors, a caster wheel at the back to stop it
falling over, a battery, a motor driver and an ESP32.

## Why a motor driver?

The ESP32 runs on 3.3 V and its pins can supply a few milliamps --
enough to light an LED, nowhere near enough to turn a motor. The motor
driver is a switch: small signals from the ESP32 on one side, battery
power to the motors on the other.

## Wiring

| Motor driver | ESP32 | What it does |
|---|---|---|
| ENA | GPIO 25 | left motor speed (PWM) |
| IN1 | GPIO 26 | left motor direction |
| IN2 | GPIO 27 | left motor direction |
| ENB | GPIO 33 | right motor speed (PWM) |
| IN3 | GPIO 14 | right motor direction |
| IN4 | GPIO 13 | right motor direction |
| GND | GND | **required** -- see below |

Battery `+` to the driver's `12V`/`VIN`, battery `-` to the driver's `GND`.

### The ground wire

The ESP32's GND and the motor driver's GND **must** be connected, even
though they have separate power. "3.3 volts" means 3.3 volts *compared
to ground* -- if the two boards don't agree on where ground is, the
driver cannot tell a HIGH from a LOW. Robots that twitch randomly are
almost always missing this wire.

### Don't use these pins

GPIO 0, 2, 12 and 15 are read by the ESP32 at power-on to decide how to
boot. If a motor driver is pulling on them the board may not start at
all. The pins in the table above avoid them.

## Next

Don't write any code yet. Lesson 4 uploads a test program that drives
each wheel in turn, so you can check every wire before anything else
is added. That's also where you measure the robot and set
`WHEEL_BASE`.

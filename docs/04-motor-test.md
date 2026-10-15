# 4. Does the hardware work?

No WiFi. No broker. No ROS 2. Just the motors.

This lesson exists to catch wiring mistakes **now**, while there is
only one thing that can be wrong. Every lesson after this adds a
network, and a robot that won't move is much harder to diagnose when
there are five things in the chain instead of one.

> **Put the robot on a book** so the wheels spin in the air. It will
> drive off the table otherwise.

## Upload it

In the VS Code status bar at the bottom, click the env switcher and
choose **`env:motortest`**. Press the **→** arrow to upload.

Or from a terminal:

```bash
./scripts/build_firmware.sh motortest upload
./scripts/build_firmware.sh motortest monitor    # watch the output
```

Open the Serial Monitor (the plug icon). You should see the robot
announce each step as it does it:

```
motor test -- put the robot on a book, wheels in the air
[1/9] LEFT wheel forward   (right should be still)
[2/9] LEFT wheel backward
[3/9] RIGHT wheel forward  (left should be still)
...
```

## Check each step

Watch the wheels and tick these off:

| Step | What must happen |
|---|---|
| 1 | left wheel forward, right wheel still |
| 2 | left wheel backward |
| 3 | right wheel forward, left wheel still |
| 4 | right wheel backward |
| 5 | both forward, same speed |
| 6 | both backward |
| 7 | spins left (left back, right forward) |
| 8 | spins right |
| 9 | everything stops |

## When something's wrong

**A wheel turns the wrong way.** Either swap that motor's two wires at
the driver, or swap its two direction pins in
[motor.h](../firmware/include/motor.h) (`L_IN1`/`L_IN2` for the left
wheel, `R_IN1`/`R_IN2` for the right) and upload again. Both work. If
*both* wheels are backwards, swap both pairs.

**The wrong wheel moves.** Your left and right motors are swapped at
the driver. Swap the two pairs.

**Nothing moves, but the Serial Monitor is fine.** The ESP32 is running
happily on USB power while the motors have none. Check the battery is
connected and switched on.

**Motors buzz but don't turn.** Not enough push to overcome friction.
Open [motor.h](../firmware/include/motor.h) and raise `MIN_DUTY` a
little at a time until they move.

**The board keeps restarting.** The motors are pulling more current
than the supply can give, and the voltage is sagging. Use a separate
battery for the motors, and check the grounds are joined
([03-hardware.md](03-hardware.md)).

**Only one wheel ever moves.** Most often the pins in
[motor.h](../firmware/include/motor.h) don't match how you wired it --
compare them one by one with the table in
[03-hardware.md](03-hardware.md). Then check that wheel's three wires
at the driver, and the ENA/ENB jumper on an L298N.

## Measure your robot

While you're here, open [motor.h](../firmware/include/motor.h) and set:

```c
#define WHEEL_BASE 0.15f   // metres between the two wheels
```

Measure from the middle of one tyre to the middle of the other. If this
is wrong the robot still drives, but "turn 90 degrees" won't turn 90
degrees.

## Don't move on until

All nine steps do the right thing. From here on, if the robot doesn't
move, you know it isn't the hardware -- and that is worth an hour of
anyone's time.

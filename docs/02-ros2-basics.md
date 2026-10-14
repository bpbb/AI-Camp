# 2. Nodes, topics, publishers, subscribers

No robot in this lesson. Nothing to break, nothing to plug in. We're
learning the vocabulary first, because once you have it, the robot is
just one more node.

## The whole idea in one picture

```
   ┌────────────┐                        ┌────────────┐
   │   talker   │ ─────/chatter─────────>│  listener  │
   └────────────┘                        └────────────┘
      a NODE            a TOPIC              a NODE
   (one program)    (a named channel)     (one program)
```

- A **node** is one program doing one job.
- A **topic** is a named channel that messages travel on.
- A node that sends on a topic is a **publisher**.
- A node that receives from a topic is a **subscriber**.

The rule that matters: **the talker and the listener have never heard
of each other.** They only agree on the name `/chatter`. Either one can
be restarted, replaced or rewritten in another language, and the other
will not notice.

## Run it

Terminal 1:

```bash
ros2 run workshop listener
```

It says it's listening, then nothing happens. It's waiting.

Terminal 2:

```bash
ros2 run workshop talker
```

Now watch both windows. They found each other with no addresses, no
configuration, nothing. You only told them a topic name.

## Look at what you built

Leave both running. In a third terminal:

```bash
ros2 node list
```
```
/listener
/talker
```

```bash
ros2 topic list
```
```
/chatter
/parameter_events
/rosout
```

```bash
ros2 topic echo /chatter
```

This is the most useful command in ROS 2. It subscribes to a topic and
prints whatever goes past. You have just added a third subscriber
without touching any code.

```bash
ros2 topic info /chatter
```
```
Type: std_msgs/msg/String
Publisher count: 1
Subscription count: 2      <-- listener, and your echo
```

```bash
ros2 topic hz /chatter      # how many messages per second
rqt_graph                   # draw the picture
```

## Publish without writing a program

Stop the talker (Ctrl+C) and leave the listener running. Then:

```bash
ros2 topic pub /chatter std_msgs/msg/String '{data: "hi from the terminal"}'
```

The listener hears you. It cannot tell the difference between your
terminal and the real talker -- and that is exactly the point.

## Now change the code

Open [talker.py](../ros2_ws/src/workshop/workshop/talker.py). Near the
top:

```python
TOPIC = 'chatter'
MESSAGE = 'hello'
RATE_HZ = 1.0
```

Try each of these, rebuilding each time:

```bash
cd ~/AI-Camp/ros2_ws && colcon build && source install/setup.bash
```

1. Change `MESSAGE` to your name.
2. Change `RATE_HZ` to `10.0`. Check with `ros2 topic hz /chatter`.
3. Change `TOPIC` to `'robot'` in the talker **but not** the listener.
   They stop hearing each other. Fix it by changing the listener too.
   **This is the mistake you will make with the real robot**, so make
   it here first.

## Workshop: talk to the next table

Two computers on the same WiFi. One runs the talker, the other runs the
listener -- and it works, across machines, with no setup at all.

Then everyone does it at once and it stops being fun: twenty talkers
all publishing to `/chatter`, and every listener hears all of them.

The fix is a **domain**, a number that separates groups from each other:

```bash
export ROS_DOMAIN_ID=7      # in every terminal, on both computers
```

Pick a number per team, 0 to 101. Nodes on different domains cannot see
each other at all -- `ros2 node list` won't even show them.

Write your team's number down. **You will need the same number on the
robot in lesson 5.**

## What you should be able to answer

1. What is the difference between a node and a topic?
2. If the listener isn't running, what does the talker do?
3. Two nodes both publish to `/chatter`. Who receives what?
4. You change `TOPIC` in only one file. What happens, and how would
   you diagnose it with `ros2 topic list`?
5. Why does each team need a different `ROS_DOMAIN_ID`?

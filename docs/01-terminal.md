# 1. Surviving the terminal

Everything in ROS 2 happens in a terminal. If you have never used one,
this is the half hour that makes the rest of the week possible.

Open one with **Ctrl+Alt+T**. In VS Code, **Ctrl+`** (the key above Tab).

## Six commands

| | |
|---|---|
| `pwd` | where am I? |
| `ls` | what's here? |
| `cd folder` | go into a folder |
| `cd ..` | go back up one |
| `cat file` | show me what's in this file |
| `clear` | tidy up the screen |

Try it:

```bash
cd ~/AI-Camp
pwd
ls
cd docs
ls
cat 01-terminal.md
cd ..
```

## Two keys that save you

**Tab** completes what you're typing. Type `cd doc` then press Tab --
it finishes it for you. Use this constantly. It also means you never
misspell a folder name.

**Up arrow** brings back the last command. You will run the same
commands over and over this week; do not retype them.

## Ctrl+C

Stops whatever is running. ROS 2 programs run forever until you stop
them, so you will use this a lot.

If Ctrl+C doesn't work, the program is stuck -- close the terminal tab
and open a new one.

## You will need many terminals at once

This is normal in ROS 2. One program per terminal, all running at the
same time. In VS Code, click the **+** in the terminal panel for a new
one, and click between them.

By lesson 5 you will have three or four open. That is not a mistake.

## The one command you must never forget

```bash
source /opt/ros/jazzy/setup.bash
```

(`jazzy` on Ubuntu 24.04. On 22.04 it is `humble` -- check with
`ls /opt/ros` if you are unsure.)

This tells the terminal where ROS 2 lives. **Every new terminal needs
it.** Without it, every `ros2` command says "command not found".

Once you have built the workspace you need a second one too:

```bash
source ~/AI-Camp/ros2_ws/install/setup.bash
```

That's two lines in every terminal, every time. Typing them gets old
fast, so put them in the file your shell reads at startup:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/AI-Camp/ros2_ws/install/setup.bash" >> ~/.bashrc
```

Use `humble` instead of `jazzy` on 22.04. The lessons assume the
project is at `~/AI-Camp`; if yours is somewhere else (for example
`~/Documents/AI-Camp`), use that path instead, here and in every later
lesson.

New terminals now do it for you. (`>>` adds a line to the end of a
file. `>` would *replace* the whole file -- be careful with that one.)

### One place this gets in the way

Sourcing ROS 2 in every terminal is right for everything you do on the
computer. It is wrong for one job: **building the robot's firmware** in
lesson 5.

That build compiles its own private copy of the ROS build tools, and a
sourced workspace confuses it. You don't have to remember this --
`scripts/build_firmware.sh` clears the ROS settings for you, and the
lessons tell you to use it. Just don't be surprised that it exists.

## Check it worked

Open a **new** terminal and run:

```bash
ros2 --help
```

If you get a help page, you're ready. If you get "command not found",
the `source` line didn't happen.

#!/usr/bin/env bash
# Sets up a computer for the robot lessons.
#
#   ./scripts/setup_pc.sh
#
# Works on Ubuntu 24.04 (ROS 2 Jazzy) and 22.04 (ROS 2 Humble). It works
# out which one you are on. Student machines are 24.04.
#
# Every machine should end up identical: build one image with this,
# check it with scripts/check_setup.sh, then clone it.
#
# No `set -u`: sourcing ROS setup scripts fails under it.
set -eo pipefail

PLATFORMIO_VERSION="6.1.16"
AGENT_WS="${HOME}/microros_agent_ws"

# ---------------------------------------------------------------
#  Which ROS 2 belongs on this machine?
# ---------------------------------------------------------------
. /etc/os-release
case "${VERSION_ID}" in
    24.04) WANT_DISTRO="jazzy" ;;
    22.04) WANT_DISTRO="humble" ;;
    *)
        echo "Unsupported Ubuntu (${VERSION_ID}). Expected 24.04 or 22.04." >&2
        exit 1
        ;;
esac

# An already-installed ROS wins, so we never fight an existing setup.
for d in jazzy humble; do
    [ -d "/opt/ros/${d}" ] && { WANT_DISTRO="${d}"; break; }
done

echo "==> Ubuntu ${VERSION_ID}, using ROS 2 ${WANT_DISTRO}"

# ---------------------------------------------------------------
#  ROS 2 itself
# ---------------------------------------------------------------
if [ -d "/opt/ros/${WANT_DISTRO}" ]; then
    echo "==> ROS 2 ${WANT_DISTRO} already installed, skipping"
else
    echo "==> installing ROS 2 ${WANT_DISTRO} (this is the big one, ~2 GB)"
    sudo apt-get update
    sudo apt-get install -y software-properties-common curl locales
    sudo add-apt-repository -y universe

    sudo locale-gen en_US en_US.UTF-8
    sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

    # The keyring method on purpose, not the newer ros2-apt-source .deb.
    # That one asks the GitHub API for the latest release, and a room
    # full of machines behind one router gets rate-limited (HTTP 403).
    # This talks only to packages.ros.org.
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu ${UBUNTU_CODENAME} main" \
        | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null

    sudo apt-get update
    sudo apt-get install -y "ros-${WANT_DISTRO}-desktop" ros-dev-tools
fi

# ---------------------------------------------------------------
#  Everything else from apt
# ---------------------------------------------------------------
echo "==> apt packages"
sudo apt-get update
sudo apt-get install -y \
    git cmake python3-pip python3-venv python3-rosdep \
    mosquitto mosquitto-clients \
    python3-paho-mqtt \
    xterm

# python3-venv is easy to miss and the failure is misleading. The
# PlatformIO VS Code extension builds itself a virtualenv on first run;
# without this package that fails, and the extension reports
# "Can not find working Python 3.6+ Interpreter" -- which sends people
# off reinstalling Python, which on Ubuntu breaks apt and ROS 2.
#
# paho-mqtt comes from apt rather than pip so it lands where the ROS
# nodes can import it. The version differs between releases (1.6 on
# 22.04, 2.x on 24.04); the nodes handle both, see make_client().

echo "==> letting other machines reach the broker"
sudo tee /etc/mosquitto/conf.d/lan.conf >/dev/null <<'CONF'
listener 1883 0.0.0.0
allow_anonymous true
CONF
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

# ---------------------------------------------------------------
#  PlatformIO
# ---------------------------------------------------------------
echo "==> PlatformIO ${PLATFORMIO_VERSION}"
if ls /usr/lib/python3.*/EXTERNALLY-MANAGED >/dev/null 2>&1; then
    # Ubuntu 24.04 enforces PEP 668: `pip3 install --user` is refused
    # with "error: externally-managed-environment". pipx gives the tool
    # its own venv, which is the supported way to install an app.
    echo "    (PEP 668 in force -- installing with pipx)"
    sudo apt-get install -y pipx
    pipx install "platformio==${PLATFORMIO_VERSION}" 2>/dev/null \
        || pipx upgrade platformio
    pipx ensurepath >/dev/null
else
    pip3 install --user "platformio==${PLATFORMIO_VERSION}"
fi

export PATH="${HOME}/.local/bin:${PATH}"

echo "==> ROS build tools inside PlatformIO's own virtualenv"
# Not obvious, and not optional.
#
# micro_ros_platformio builds libmicroros from source using PlatformIO's
# bundled Python at ~/.platformio/penv -- NOT the system python3. That
# venv cannot see system-wide ROS packages, so the build dies with:
#
#     ModuleNotFoundError: No module named 'catkin_pkg'
#
# empy must be 3.3.x: the message generators use the old empy API and
# empy 4.x changed it, which fails later and far less clearly.
pio system info >/dev/null 2>&1 || true   # first run creates the penv

PENV_PY="${HOME}/.platformio/penv/bin/python"
if [ -x "${PENV_PY}" ]; then
    "${PENV_PY}" -m pip install -q "catkin_pkg" "empy==3.3.4" "lark"
else
    echo "    WARNING: ${PENV_PY} not found."
    echo "    Run 'pio system info' once, then re-run this script."
fi

# ---------------------------------------------------------------
#  micro-ROS agent
# ---------------------------------------------------------------
echo "==> micro-ROS agent (${WANT_DISTRO})"
# No apt package exists for the agent, so it is built from source.
# A few minutes, once per machine. No docker involved.
if [ -x "${AGENT_WS}/install/micro_ros_agent/lib/micro_ros_agent/micro_ros_agent" ]; then
    echo "    already built at ${AGENT_WS}, skipping"
else
    sudo rosdep init 2>/dev/null || true
    rosdep update

    mkdir -p "${AGENT_WS}/src"
    if [ ! -d "${AGENT_WS}/src/micro_ros_setup" ]; then
        git clone -b "${WANT_DISTRO}" \
            https://github.com/micro-ROS/micro_ros_setup.git \
            "${AGENT_WS}/src/micro_ros_setup"
    fi

    # Its own workspace, deliberately. Inside ros2_ws, every `colcon
    # build` a student runs would rebuild the agent too.
    (
        set -e
        set +u
        cd "${AGENT_WS}"
        source "/opt/ros/${WANT_DISTRO}/setup.bash"
        rosdep install --from-paths src --ignore-src -y
        colcon build
        source install/local_setup.bash
        ros2 run micro_ros_setup create_agent_ws.sh
        ros2 run micro_ros_setup build_agent.sh
    )
fi

# ---------------------------------------------------------------
echo
echo "Done. ROS 2 ${WANT_DISTRO} on Ubuntu ${VERSION_ID}."
echo
echo "This machine's address on the network:"
hostname -I | awk '{print "    " $1}'
echo
echo "Next:"
echo "  1. put that address in firmware/include/config.h (AGENT_IP)"
echo "  2. set board_microros_distro = ${WANT_DISTRO} in firmware/platformio.ini"
echo "  3. run ./scripts/check_setup.sh"

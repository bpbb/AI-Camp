#!/usr/bin/env bash
# Starts the micro-ROS agent for lesson 5.
#
#   ./scripts/start_agent.sh          # udp on port 8888
#   ./scripts/start_agent.sh 9999     # some other port
#
# The agent joins whatever ROS_DOMAIN_ID your shell is set to, so it
# must match the ROS_DOMAIN_ID in firmware/include/config.h.
# No `set -u`: sourcing the ROS setup scripts below fails under it,
# because they read variables they never set.
set -eo pipefail

PORT="${1:-8888}"
DOMAIN="${ROS_DOMAIN_ID:-0}"
AGENT_WS="${HOME}/microros_agent_ws"

# Works on Jazzy (24.04) and Humble (22.04) -- whichever is installed.
ROS_SETUP=""
for d in jazzy humble; do
    [ -f "/opt/ros/${d}/setup.bash" ] && ROS_SETUP="/opt/ros/${d}/setup.bash" && break
done
if [ -z "${ROS_SETUP}" ]; then
    echo "no ROS 2 found in /opt/ros -- run ./scripts/setup_pc.sh first" >&2
    exit 1
fi

echo "ROS_DOMAIN_ID=${DOMAIN} -- must match config.h on the robot"


if [ -f "${AGENT_WS}/install/local_setup.bash" ]; then
    source "${ROS_SETUP}"
    source "${AGENT_WS}/install/local_setup.bash"
elif ! ros2 pkg list 2>/dev/null | grep -q micro_ros_agent; then
    echo "the agent is not built yet -- run ./scripts/setup_pc.sh first" >&2
    exit 1
fi

echo "starting agent on udp port ${PORT}"
exec ros2 run micro_ros_agent micro_ros_agent udp4 --port "${PORT}" -v4

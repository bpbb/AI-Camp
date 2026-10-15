#!/usr/bin/env bash
# เริ่ม micro-ROS agent สำหรับบทที่ 5
#
#   ./scripts/start_agent.sh          # udp port 8888
#   ./scripts/start_agent.sh 9999     # ใช้ port อื่น
#
# agent ใช้ ROS_DOMAIN_ID ตามที่ตั้งไว้ใน shell ซึ่งต้องตรงกับ
# ROS_DOMAIN_ID ใน firmware/include/config.h
# ไม่ใช้ `set -u` เพราะ ROS setup script อ่านตัวแปรที่ไม่ได้ตั้งค่าไว้
set -eo pipefail

PORT="${1:-8888}"
DOMAIN="${ROS_DOMAIN_ID:-0}"
AGENT_WS="${HOME}/microros_agent_ws"

# ใช้ได้ทั้ง Jazzy (24.04) และ Humble (22.04) ตามที่ติดตั้งไว้
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

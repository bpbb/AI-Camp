#!/usr/bin/env bash
# Build or upload the ESP32 firmware in a clean environment.
#
#   ./scripts/build_firmware.sh motortest
#   ./scripts/build_firmware.sh microros upload
#   ./scripts/build_firmware.sh microros monitor
#
# Why this exists
# ---------------
# Lesson 1 tells you to put `source /opt/ros/<distro>/setup.bash` in your
# ~/.bashrc, because you need ROS 2 in every terminal. That is correct
# for everything except this one job.
#
# The micro-ROS firmware build compiles its own private copy of the ROS
# build tools. If a real ROS workspace is sourced, its AMENT_PREFIX_PATH
# and CMAKE_PREFIX_PATH leak in, CMake finds the wrong packages, and the
# build fails with errors about rosidl_runtime_cpp that point at a
# workspace which has nothing to do with this project.
#
# So this script strips the ROS variables back out before calling pio.
set -eo pipefail

ENV_NAME="${1:-motortest}"
TARGET="${2:-}"

case "${ENV_NAME}" in
    motortest|microros) ;;
    *)
        echo "usage: $0 {motortest|microros} [upload|monitor|clean]" >&2
        exit 1
        ;;
esac

cd "$(dirname "$0")/../firmware"

ARGS=(run -e "${ENV_NAME}")
[ -n "${TARGET}" ] && ARGS+=(-t "${TARGET}")

# pio lives in ~/.platformio/penv (setup_pc.sh or the VS Code extension).
CLEAN_PATH="${HOME}/.platformio/penv/bin:${HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin"
if ! PATH="${CLEAN_PATH}" command -v pio >/dev/null; then
    echo "PlatformIO (pio) not found. Run ./scripts/setup_pc.sh first." >&2
    exit 1
fi

echo "building '${ENV_NAME}' with a clean (ROS-free) environment"

exec env \
    -u AMENT_PREFIX_PATH \
    -u CMAKE_PREFIX_PATH \
    -u COLCON_PREFIX_PATH \
    -u AMENT_CURRENT_PREFIX \
    -u ROS_DISTRO \
    -u ROS_VERSION \
    -u ROS_PYTHON_VERSION \
    -u ROS_LOCALHOST_ONLY \
    -u ROS_DOMAIN_ID \
    -u PYTHONPATH \
    -u LD_LIBRARY_PATH \
    PATH="${CLEAN_PATH}" \
    HOME="${HOME}" \
    pio "${ARGS[@]}"

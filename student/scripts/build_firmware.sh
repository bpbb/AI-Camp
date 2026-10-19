#!/usr/bin/env bash
# Build หรือ upload firmware ของ ESP32 ใน environment ที่สะอาด
#
#   ./scripts/build_firmware.sh motortest
#   ./scripts/build_firmware.sh microros upload
#   ./scripts/build_firmware.sh microros monitor
#
# การ build firmware ของ micro-ROS จะคอมไพล์ ROS build tools ชุดของตัวเอง
# ถ้า source ROS 2 ไว้ (เช่นใน ~/.bashrc) ตัวแปร AMENT_PREFIX_PATH/CMAKE_PREFIX_PATH
# จะปนเข้ามา ทำให้ CMake หา package ผิดและ build ล้มเหลว
# จึงต้องล้างตัวแปร ROS ออกก่อนเรียก pio
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

# pio อยู่ใน ~/.platformio/penv (ติดตั้งโดย setup_pc.sh หรือ VS Code extension)
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

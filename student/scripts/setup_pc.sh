#!/usr/bin/env bash
# ตั้งค่าคอมพิวเตอร์สำหรับบทเรียนหุ่นยนต์
#
#   ./scripts/setup_pc.sh
#
# ใช้ได้กับ Ubuntu 24.04 (ROS 2 Jazzy) และ 22.04 (ROS 2 Humble) โดยตรวจเวอร์ชันให้อัตโนมัติ
# ทุกเครื่องควรเหมือนกัน: สร้าง image ด้วยสคริปต์นี้ ตรวจด้วย
# scripts/check_setup.sh แล้วจึง clone
#
# ไม่ใช้ `set -u` เพราะการ source ROS setup script จะล้มเหลว
set -eo pipefail

PLATFORMIO_VERSION="6.1.16"
AGENT_WS="${HOME}/microros_agent_ws"

# ---------------------------------------------------------------
#  เครื่องนี้ควรใช้ ROS 2 ตัวไหน
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

# ถ้ามี ROS ติดตั้งอยู่แล้วให้ใช้ตัวนั้น เพื่อไม่ชนกับ setup เดิม
for d in jazzy humble; do
    [ -d "/opt/ros/${d}" ] && { WANT_DISTRO="${d}"; break; }
done

echo "==> Ubuntu ${VERSION_ID}, using ROS 2 ${WANT_DISTRO}"

# ---------------------------------------------------------------
#  ติดตั้ง ROS 2
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

# ใช้วิธี keyring แทน .deb ros2-apt-source เพราะตัวนั้นเรียก GitHub API
# ซึ่งจะโดน rate-limit (HTTP 403) เมื่อหลายเครื่องใช้ router เดียวกัน
# วิธีนี้ติดต่อแค่ packages.ros.org
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu ${UBUNTU_CODENAME} main" \
        | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null

    sudo apt-get update
    sudo apt-get install -y "ros-${WANT_DISTRO}-desktop" ros-dev-tools
fi

# ---------------------------------------------------------------
#  package อื่น ๆ จาก apt
# ---------------------------------------------------------------
echo "==> apt packages"
sudo apt-get update
sudo apt-get install -y \
    git cmake python3-pip python3-venv python3-rosdep \
    mosquitto mosquitto-clients \
    python3-paho-mqtt \
    xterm

# ต้องมี python3-venv: PlatformIO extension ของ VS Code สร้าง venv ตอนรันครั้งแรก
# ถ้าไม่มีจะแจ้ง "Can not find working Python 3.6+ Interpreter" ซึ่งชวนเข้าใจผิด
# ห้ามติดตั้ง Python ใหม่เอง เพราะจะทำให้ apt และ ROS 2 บน Ubuntu พัง
#
# ติดตั้ง paho-mqtt จาก apt (ไม่ใช่ pip) เพื่อให้ ROS node import ได้
# เวอร์ชันต่างกันตาม release (1.6 บน 22.04, 2.x บน 24.04) แต่ node รองรับทั้งคู่ ดู make_client()

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
    # Ubuntu 24.04 บังคับ PEP 668: `pip3 install --user` จะถูกปฏิเสธ
    # จึงใช้ pipx ซึ่งสร้าง venv แยกให้แต่ละแอป (วิธีที่รองรับอย่างเป็นทางการ)
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
# จำเป็นต้องทำ: micro_ros_platformio build libmicroros ด้วย Python ของ PlatformIO
# ที่ ~/.platformio/penv (ไม่ใช่ python3 ของระบบ) ซึ่งมองไม่เห็น ROS package ของระบบ
# ถ้าขาดจะเจอ: ModuleNotFoundError: No module named 'catkin_pkg'
#
# empy ต้องเป็น 3.3.x เพราะ message generator ใช้ API เก่า ซึ่ง empy 4.x เปลี่ยนไปแล้ว
pio system info >/dev/null 2>&1 || true   # รันครั้งแรกจะสร้าง penv

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
# agent ไม่มี package ใน apt จึงต้อง build จาก source
# ใช้เวลาไม่กี่นาที ทำครั้งเดียวต่อเครื่อง ไม่ต้องใช้ docker
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

    # แยก workspace ของ agent โดยเจตนา ถ้าอยู่ใน ros2_ws
    # ทุกครั้งที่นักเรียนรัน `colcon build` จะ build agent ใหม่ด้วย
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

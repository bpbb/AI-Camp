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

# คัดลอกผ่าน USB/ZIP แล้วสิทธิ์ execute หาย: กำหนดให้ทุกสคริปต์รันได้
chmod +x "$(dirname "$0")"/*.sh

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
    xterm terminator

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
#  VS Code
# ---------------------------------------------------------------
echo "==> VS Code and its extensions"
# snap เป็นแพ็กเกจทางการของ Microsoft และอัปเดตตัวเองได้
if ! command -v code >/dev/null; then
    sudo snap install code --classic
fi
export PATH="/snap/bin:${PATH}"
# extension สามตัวเดียวกับใน .vscode/extensions.json (ถ้าไม่มีเน็ตก็ข้ามได้)
for ext in platformio.platformio-ide ms-iot.vscode-ros ms-python.python; do
    code --install-extension "${ext}" >/dev/null 2>&1 \
        || echo "    WARNING: could not install ${ext}; VS Code will offer it later"
done

# ---------------------------------------------------------------
#  PlatformIO
# ---------------------------------------------------------------
echo "==> PlatformIO ${PLATFORMIO_VERSION} in ~/.platformio/penv"
# micro-ROS build ด้วย ~/.platformio/penv เสมอ (ฝังไว้ใน micro_ros_platformio)
# จึงต้องติดตั้ง PlatformIO ไว้ที่นี่ ถ้าใช้ pipx จะ error: cannot open .../penv/bin/activate
# VS Code PlatformIO extension ใช้ venv เดียวกันนี้
# เครื่องมือ build ต้องอยู่ใน venv นี้ด้วย (ไม่งั้น No module named 'catkin_pkg')
# empy ต้องเป็น 3.3.x เพราะ message generator ใช้ API เวอร์ชันเก่า
PENV="${HOME}/.platformio/penv"
[ -x "${PENV}/bin/python" ] || python3 -m venv "${PENV}"
"${PENV}/bin/python" -m pip install -q --upgrade pip
[ -x "${PENV}/bin/pio" ] || "${PENV}/bin/python" -m pip install -q "platformio==${PLATFORMIO_VERSION}"
"${PENV}/bin/python" -m pip install -q catkin_pkg "empy==3.3.4" lark

# setup รุ่นก่อนติดตั้ง pio ด้วย pipx: ลบออกเพื่อให้เหลือ pio ตัวเดียว
if command -v pipx >/dev/null && pipx list 2>/dev/null | grep -q 'package platformio'; then
    pipx uninstall platformio >/dev/null
fi

# ให้พิมพ์ `pio` ได้ (~/.local/bin จะอยู่ใน PATH หลัง login ครั้งถัดไป)
mkdir -p "${HOME}/.local/bin"
ln -sf "${PENV}/bin/pio" "${HOME}/.local/bin/pio"
export PATH="${HOME}/.local/bin:${PATH}"

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

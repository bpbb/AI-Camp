#!/usr/bin/env bash
# Confirms this machine matches the reference setup.
#
#   ./scripts/check_setup.sh
#
# Works on Ubuntu 24.04 (Jazzy) and 22.04 (Humble). Every machine of the
# same kind should give an identical report. Run it after imaging, and
# again on the morning of a lesson -- it catches the three things that
# drift: the IP address, group membership, and a stopped broker.

PLATFORMIO_VERSION="6.1.16"
AGENT_WS="${HOME}/microros_agent_ws"

pass=0
fail=0
ok()   { printf '  \033[32mok  \033[0m %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
note() { printf '       %s\n' "$1"; }

echo "checking this machine"
echo

# ---- operating system, and which ROS belongs on it ----
. /etc/os-release
case "${VERSION_ID}" in
    24.04) WANT_DISTRO="jazzy" ;;
    22.04) WANT_DISTRO="humble" ;;
    *)     WANT_DISTRO="" ;;
esac

if [ -n "${WANT_DISTRO}" ]; then
    ok "Ubuntu ${VERSION_ID} (expects ROS 2 ${WANT_DISTRO})"
else
    bad "Ubuntu ${VERSION_ID} -- expected 24.04 or 22.04"
fi

if [ -n "${WANT_DISTRO}" ] && [ -f "/opt/ros/${WANT_DISTRO}/setup.bash" ]; then
    ok "ROS 2 ${WANT_DISTRO}"
    FOUND_DISTRO="${WANT_DISTRO}"
else
    FOUND_DISTRO=""
    for d in jazzy humble; do
        [ -f "/opt/ros/${d}/setup.bash" ] && FOUND_DISTRO="${d}" && break
    done
    if [ -n "${FOUND_DISTRO}" ]; then
        bad "found ROS 2 ${FOUND_DISTRO}, but this Ubuntu wants ${WANT_DISTRO}"
    else
        bad "no ROS 2 found in /opt/ros"
        note "./scripts/setup_pc.sh   installs it"
    fi
fi

command -v colcon >/dev/null && ok "colcon" || bad "colcon missing"

# ---- python ----
# Any paho works: the nodes handle both the 1.x and 2.x constructors.
got=$(python3 -c 'import paho.mqtt as p; print(p.__version__)' 2>/dev/null)
if [ -n "$got" ]; then
    ok "paho-mqtt ${got}"
else
    bad "paho-mqtt not installed"
    note "sudo apt install python3-paho-mqtt"
fi

# The PlatformIO VS Code extension needs this to build its virtualenv.
# Without it the extension claims Python is missing, which it is not.
if python3 -m venv --help >/dev/null 2>&1 && \
   python3 -c 'import ensurepip' >/dev/null 2>&1; then
    ok "python3-venv"
else
    bad "python3-venv missing -- the PlatformIO extension will claim it cannot find Python"
    note "sudo apt install python3-venv"
fi

# Same places build_firmware.sh looks: ~/.local/bin is only on PATH
# after a new login, but the scripts find it anyway.
PIO_BIN="$(PATH="${HOME}/.platformio/penv/bin:${HOME}/.local/bin:${PATH}" command -v pio)"
got=$("${PIO_BIN:-pio}" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
# Any 6.x is fine: the VS Code extension updates it, and the toolchain
# itself is pinned in platformio.ini (platform = espressif32@...).
if [ "${got%%.*}" = "6" ]; then
    ok "platformio ${got}"
elif [ -n "$got" ]; then
    bad "platformio ${got}, expected 6.x"
else
    bad "platformio not installed"
    note "run ./scripts/setup_pc.sh"
fi
if [ -n "$got" ] && ! command -v pio >/dev/null; then
    note "pio works from the scripts; to type 'pio' yourself, open a new terminal (or log out and in)"
fi

# ---- ROS build tools inside PlatformIO's Python ----
# micro_ros_platformio compiles libmicroros with the Python that runs
# PlatformIO, which cannot see system-wide ROS packages. Missing these
# fails the firmware build with "No module named 'catkin_pkg'".
PIO_PY="${HOME}/.platformio/penv/bin/python"   # micro-ROS always builds with this one
if [ -x "${PIO_PY}" ]; then
    missing=""
    for mod in catkin_pkg em lark; do
        "${PIO_PY}" -c "import ${mod}" >/dev/null 2>&1 || missing="${missing} ${mod}"
    done
    if [ -z "${missing}" ]; then
        ok "PlatformIO's Python has the ROS build tools"
    else
        bad "PlatformIO's Python missing:${missing} -- micro-ROS firmware will not build"
        note "re-run ./scripts/setup_pc.sh"
    fi
    emv=$("${PIO_PY}" -c "import em; print(em.__version__)" 2>/dev/null)
    case "${emv}" in
        3.3.*) ok "PlatformIO's Python empy ${emv}" ;;
        "")    : ;;
        *)     bad "PlatformIO's Python empy ${emv} -- needs 3.3.x"
               note "re-run ./scripts/setup_pc.sh" ;;
    esac
else
    bad "~/.platformio/penv missing -- micro-ROS firmware will not build"
    note "run ./scripts/setup_pc.sh"
fi

# ---- mqtt broker ----
if systemctl is-active --quiet mosquitto; then
    ok "mosquitto running"
    if ss -tln 2>/dev/null | grep -q '0.0.0.0:1883'; then
        ok "mosquitto listening on the network"
    else
        bad "mosquitto only listening on localhost -- robots cannot reach it"
        note "re-run scripts/setup_pc.sh"
    fi
else
    if command -v mosquitto_sub >/dev/null; then
        bad "mosquitto not running"
        note "sudo systemctl start mosquitto"
    else
        bad "mosquitto not installed"
        note "sudo apt install mosquitto mosquitto-clients  (or re-run ./scripts/setup_pc.sh)"
    fi
fi

# ---- micro-ROS agent ----
if [ -x "${AGENT_WS}/install/micro_ros_agent/lib/micro_ros_agent/micro_ros_agent" ]; then
    ok "micro-ROS agent built"
else
    bad "micro-ROS agent not built"
    note "./scripts/setup_pc.sh   (a few minutes, once per machine)"
fi

# ---- serial port access ----
if id -nG | grep -qw dialout; then
    ok "user is in the dialout group"
else
    bad "user not in dialout -- uploading to the ESP32 will fail"
    note "sudo usermod -aG dialout \$USER   then log out and back in"
fi

# ---- the firmware must target the same distro as the computer ----
PIO_INI="$(dirname "$0")/../firmware/platformio.ini"
if [ -f "${PIO_INI}" ] && [ -n "${FOUND_DISTRO}" ]; then
    pio_distro=$(grep -oP 'board_microros_distro\s*=\s*\K\w+' "${PIO_INI}" 2>/dev/null | head -1)
    if [ "${pio_distro}" = "${FOUND_DISTRO}" ]; then
        ok "firmware targets ${pio_distro}, matching this computer"
    else
        bad "firmware targets ${pio_distro:-?}, but this computer runs ${FOUND_DISTRO}"
        note "set board_microros_distro = ${FOUND_DISTRO} in firmware/platformio.ini"
        note "then delete firmware/.pio -- the distro is baked in at build time"
    fi
fi

# ---- the bit that changes on its own ----
echo
ip=$(hostname -I | awk '{print $1}')
echo "this machine's address: ${ip:-none}"
CFG="$(dirname "$0")/../firmware/include/config.h"
if [ -f "${CFG}" ]; then
    cfg=$(grep -oP 'define\s+AGENT_IP\s+"\K[^"]+' "${CFG}" 2>/dev/null)
    if [ "$cfg" = "$ip" ]; then
        ok "config.h AGENT_IP matches (${cfg})"
    else
        bad "config.h says ${cfg}, this machine is ${ip}"
        note "edit firmware/include/config.h"
    fi
fi

echo
if [ "$fail" -eq 0 ]; then
    printf '\033[32mall %d checks passed\033[0m\n' "$pass"
else
    printf '\033[31m%d of %d checks failed\033[0m\n' "$fail" "$((pass+fail))"
    exit 1
fi

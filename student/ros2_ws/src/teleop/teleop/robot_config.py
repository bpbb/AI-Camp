"""Read ROBOT_ID from firmware/include/config.h.

The robot and the computer must agree on the name, so it lives in one
place. `colcon build` copies config.h into this package (see setup.py);
change it, then build again.
"""
import os
import re

DEFAULT_ROBOT_ID = 'robot1'


def _config_path():
    try:
        from ament_index_python.packages import get_package_share_directory
        return os.path.join(get_package_share_directory('teleop'), 'config.h')
    except Exception:
        return None


def robot_id(path=None):
    path = path or _config_path()
    try:
        with open(path) as f:
            m = re.search(r'^\s*#define\s+ROBOT_ID\s+"([^"]+)"', f.read(), re.M)
        if m:
            return m.group(1)
    except (OSError, TypeError):
        pass
    return DEFAULT_ROBOT_ID

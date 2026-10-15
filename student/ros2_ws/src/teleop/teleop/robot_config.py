"""อ่าน ROBOT_ID จาก firmware/include/config.h

หุ่นยนต์และคอมพิวเตอร์ต้องใช้ชื่อเดียวกัน จึงเก็บไว้ที่เดียว
`colcon build` จะคัดลอก config.h เข้ามาใน package นี้ (ดู setup.py)
แก้ไขแล้วต้อง build ใหม่
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

from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'teleop'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Phuriwat',
    maintainer_email='phuriwat47665@gmail.com',
    description='Keyboard teleoperation for a two-wheeled robot, with an MQTT bridge.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'key_teleop = teleop.key_teleop:main',
            'mqtt_bridge = teleop.mqtt_bridge:main',
            'mqtt_teleop = teleop.mqtt_teleop:main',
        ],
    },
)

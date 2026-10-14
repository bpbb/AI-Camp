from setuptools import find_packages, setup

package_name = 'workshop'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Phuriwat',
    maintainer_email='phuriwat47665@gmail.com',
    description='Tiny publisher and subscriber for learning ROS 2 topics.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = workshop.talker:main',
            'listener = workshop.listener:main',
        ],
    },
)

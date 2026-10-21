# ROS 2 Command Cheatsheet

**Ubuntu 24.04 · ROS 2 Jazzy**

## Terminal Shortcuts

| Shortcut | หน้าที่ |
|---|---|
| Ctrl+Alt+T | เปิด Terminal |
| Ctrl+Shift+T | เปิด Tab ใหม่ |
| Ctrl+C | หยุดโปรแกรมที่กำลังทำงาน |
| Tab | เติมชื่อคำสั่งหรือ Path |
| ↑ / ↓ | เลือกคำสั่งที่เคยใช้ |

## Basic Commands

| Command | หน้าที่ |
|---|---|
| `pwd` | ดูตำแหน่งปัจจุบัน |
| `ls` | ดูไฟล์และโฟลเดอร์ |
| `cd ~/AI-Camp` | เข้าโฟลเดอร์โปรเจกต์ |
| `cd ..` | กลับไปโฟลเดอร์แม่ |
| `cat filename.py` | อ่านไฟล์ โดยเปลี่ยน `filename.py` เป็นชื่อไฟล์จริง |
| `clear` | ล้างข้อความบนหน้าจอ |

## Environment Setup

รันในแต่ละ Terminal โดยเปลี่ยน `7` เป็น Domain ของทีม ให้ตรงกับหุ่นยนต์

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=7
CAMP_DIR=~/AI-Camp/student
```

`CAMP_DIR` ระบุโฟลเดอร์ที่มี `ros2_ws` และ `scripts` หากชุดนักเรียนอยู่ที่ `~/AI-Camp` โดยตรง ให้ใช้ `CAMP_DIR=~/AI-Camp` แทน

หลัง Build แล้ว โหลด Workspace ในแต่ละ Terminal:

```bash
source "$CAMP_DIR/ros2_ws/install/setup.bash"
```

ตรวจสอบ Environment:

```bash
echo "$ROS_DISTRO"
echo "$ROS_DOMAIN_ID"
```

ควรแสดง `jazzy` และหมายเลขทีม

## Team Identification

| ค่า | หน้าที่ | ต้องตรงกันที่ |
|---|---|---|
| `ROS_DOMAIN_ID` | แยก ROS 2 Graph ของทีม | Terminal, Agent และ ESP32 |
| `ROBOT_ID` | แยก MQTT Topic เช่น `robot/robot1/cmd` | Firmware config, Gateway และแอปโทรศัพท์ |

## Workspace Build

ใช้ครั้งแรกและหลังแก้โค้ด Python จากนั้นหยุดและเปิด Node ที่แก้ไขใหม่

```bash
cd "$CAMP_DIR/ros2_ws"
colcon build
source install/setup.bash
```

## Publisher and Subscriber

เปิดแยก Terminal โดยแต่ละหน้าต่างโหลด Environment และ Workspace แล้ว

| Command | หน้าที่ |
|---|---|
| `ros2 run workshop talker` | เปิด Publisher |
| `ros2 run workshop listener` | เปิด Subscriber |
| `ros2 topic echo /chatter` | ดูข้อความที่ส่ง |
| `ros2 topic hz /chatter` | ดูอัตราการส่ง |

โค้ดชุดนี้ส่งข้อความพร้อมตัวนับผ่าน `/chatter` ชนิด `std_msgs/msg/String`

ส่งข้อความจาก Terminal หนึ่งครั้ง:

```bash
ros2 topic pub --once /chatter std_msgs/msg/String '{data: "hello"}'
```

## Node and Topic Inspection

| Command | หน้าที่ |
|---|---|
| `ros2 node list` | ดู Node ทั้งหมดที่ค้นพบ |
| `ros2 node info /talker` | ดูข้อมูล Publisher/Subscriber ของ Node |
| `ros2 topic list -t` | ดูชื่อ Topic และชนิด Message |
| `ros2 topic info /chatter` | ดูจำนวน Publisher และ Subscriber |
| `ros2 interface show std_msgs/msg/String` | ดูโครงสร้างข้อความ |
| `ros2 interface show geometry_msgs/msg/Twist` | ดูโครงสร้างคำสั่งความเร็ว |
| `rqt_graph` | ดูภาพการเชื่อมต่อ |

## Assignment Build and Upload

| ไฟล์ที่แก้ | การนำโค้ดไปใช้ |
|---|---|
| TODO 1/2: `motor.h` | Upload `motortest` เพื่อตรวจล้อ |
| `config.h` | Upload `microros` |
| TODO 2/2: `key_teleop.py` | `colcon build` แล้วเปิด Node ใหม่ |

```bash
cd "$CAMP_DIR"
./scripts/build_firmware.sh motortest upload
```

ทดสอบล้อบนแท่นมั่นคง แล้วเปลี่ยนเป็น micro-ROS Firmware ก่อนรับ `/cmd_vel`:

```bash
./scripts/build_firmware.sh microros upload
```

## Robot Connection

เมื่อ Firmware และเครือข่ายพร้อม เปิด Agent ใน Terminal แยกแล้วปล่อยให้ทำงาน:

```bash
cd "$CAMP_DIR"
./scripts/start_agent.sh
```

ตรวจสอบหุ่นยนต์ในอีก Terminal:

| Command | หน้าที่ |
|---|---|
| `ros2 node list` | ตรวจว่าพบ `/esp32_robot` |
| `ros2 node info /esp32_robot` | ดู Topic ของหุ่นยนต์ |
| `ros2 topic echo /heartbeat` | รับตัวนับจากหุ่นยนต์ |
| `ros2 topic echo /cmd_vel` | ดูคำสั่งความเร็ว |

## Robot Velocity Commands

ทดสอบโดยยกล้อพ้นพื้นบนแท่นมั่นคง และใช้ผู้ส่งคำสั่งควบคุมเพียงตัวเดียว

**เดินหน้าตรง:**

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.1}, angular: {z: 0.0}}'
```

กด **Ctrl+C** หยุดคำสั่งเดิมก่อนเปลี่ยนค่า:

| การเคลื่อนที่ | `linear.x` | `angular.z` |
|---|---|---|
| เดินหน้า | `0.1` | `0.0` |
| ถอยหลัง | `-0.1` | `0.0` |
| หมุนซ้าย | `0.0` | `1.0` |
| หมุนขวา | `0.0` | `-1.0` |
| เลี้ยวโค้งซ้าย | `0.1` | `0.5` |
| หยุด | `0.0` | `0.0` |

`linear.x` ใช้หน่วย m/s และ `angular.z` ใช้ rad/s ส่วน `-r 10` ส่งซ้ำสิบครั้งต่อวินาที เพื่อให้คำสั่งต่อเนื่องตามค่า Timeout `500 ms` ของ Firmware เวลาหยุดจริงอาจมากกว่านี้ขณะรอการสื่อสาร

**ส่งคำสั่งหยุดหลังปิดผู้ส่งคำสั่งอื่นแล้ว:**

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.0}, angular: {z: 0.0}}'
```

## Keyboard Teleoperation

```bash
ros2 run teleop key_teleop
```

| ปุ่ม | หน้าที่ |
|---|---|
| `w` / `s` | เพิ่ม / ลดความเร็วเดินหน้า |
| `a` / `d` | เพิ่ม / ลดความเร็วหมุนซ้าย |
| Space | หยุด |
| `q` | หยุดและออก |

การปล่อยปุ่มไม่ได้หยุดหุ่นยนต์ ต้องกด Space เพื่อหยุด

## MQTT Teleoperation

ใช้เมื่อ Broker และ Agent ทำงานแล้ว โดยเปลี่ยน `robot1` ให้ตรงกับ `ROBOT_ID` ของทีม

**Terminal สำหรับ Gateway:**

```bash
ros2 launch teleop mqtt_gateway.launch.py robot_id:=robot1
```

**อีก Terminal สำหรับรับส่ง MQTT:**

```bash
ROBOT_ID=robot1
mosquitto_sub -t "robot/$ROBOT_ID/cmd" -v
```

กด **Ctrl+C** หยุดรับข้อมูลก่อนส่งคำสั่ง:

```bash
mosquitto_pub -t "robot/$ROBOT_ID/cmd" -m F
mosquitto_pub -t "robot/$ROBOT_ID/cmd" -m S
```

| Payload | ความหมาย |
|---|---|
| `F` / `B` | เดินหน้า / ถอยหลัง |
| `L` / `R` | หมุนซ้าย / หมุนขวา |
| `S` | หยุด |

ส่งความเร็วแบบ JSON:

```bash
mosquitto_pub -t "robot/$ROBOT_ID/cmd" -m '{"lin":0.1,"ang":0.5}'
```

คำสั่ง MQTT ข้างต้นส่งครั้งเดียว Gateway จะเปลี่ยนเป็นคำสั่งหยุดหลังไม่มีข้อมูลใหม่ประมาณหนึ่งวินาที ตัวอย่างใช้ Broker บนคอมพิวเตอร์เดียวกัน

## Phone Control Settings

| ค่า | การตั้งค่า |
|---|---|
| Broker IP | ใช้ `hostname -I` ดู IP เครือข่ายที่โทรศัพท์เข้าถึงได้ |
| Port | `1883` |
| Topic | `robot/robot1/cmd` เปลี่ยนเป็นชื่อทีม |
| ปุ่มทิศทาง | ส่ง `F`, `B`, `L`, `R` ซ้ำขณะกด เช่นทุก `100 ms` |
| ปล่อยปุ่ม / Stop | ส่ง `S` |

## Common Errors

| อาการ | จุดตรวจสอบ |
|---|---|
| `ros2: command not found` | โหลด `/opt/ros/jazzy/setup.bash` |
| `Package not found` | Build แล้วโหลด Workspace |
| ไม่พบ `/esp32_robot` | Agent การเชื่อมต่อ และ Domain ต้องตรงกัน |
| แก้โค้ดแล้วผลไม่เปลี่ยน | Build ใหม่ แล้วเปิด Node ใหม่ |
| หุ่นยนต์ขยับแล้วหยุด | คำสั่ง `/cmd_vel` ต้องส่งต่อเนื่อง |

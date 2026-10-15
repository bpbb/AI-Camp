# 5. หุ่นยนต์กลายเป็น ROS 2 node

ในบทที่ 2 คุณมี talker กับ listener อยู่บนคอมพิวเตอร์ วันนี้
listener คือตัวหุ่นยนต์

```
  ┌────────────┐      /cmd_vel      ┌─────────────┐
  │ key_teleop │ ─────────────────> │ esp32_robot │
  └────────────┘   Twist message    └─────────────┘
   your keyboard                      the ESP32
```

แนวคิดเดียวกับ `/chatter` แค่ชื่อ topic ต่างกัน ชนิด message ต่างกัน
และ node ตัวหนึ่งบังเอิญเป็น microcontroller ที่ติดล้อ

## ทำไมต้อง micro-ROS ไม่ใช่ ROS 2 ธรรมดา

ROS 2 รันบน ESP32 ไม่ได้ -- ไม่ใช่ว่า "มันช้า" แต่มันใส่ไม่ลงจริง ๆ
ROS 2 node ที่เล็กที่สุดยังต้องการหน่วยความจำหลายสิบเมกะไบต์และระบบปฏิบัติการ
เต็มรูปแบบ ส่วน ESP32 มี **RAM แค่ประมาณ 320 KB**

**micro-ROS** คือเวอร์ชันเล็กที่สร้างมาสำหรับ microcontroller คุณเขียน
โค้ดแทบเหมือนเดิม แต่มันจะคุยกับ **agent** บนคอมพิวเตอร์ของคุณ และ
agent นี่แหละที่พามันเข้าไปอยู่ใน ROS 2 graph จริง

```
   ESP32                    computer
  ┌────────┐   WiFi       ┌────────┐     ┌──────────────────┐
  │ micro- │ ───────────> │ agent  │ ──> │  the ROS 2 graph │
  │  ROS   │              │        │     │  (your other     │
  └────────┘              └────────┘     │   nodes)         │
                                         └──────────────────┘
```

agent ต้องรันอยู่**ก่อน**ที่หุ่นจะเชื่อมต่อ ถ้า ESP32
บูตขึ้นมาก่อน มันจะรอและพยายามเชื่อมต่อซ้ำไปเรื่อย ๆ -- นั่นคือ
สถานะ `WAITING_AGENT` ใน firmware

## Message: Twist

การขับหุ่นยนต์ต้องใช้ตัวเลขสองตัว: เดินหน้าเร็วแค่ไหน และเลี้ยว
เร็วแค่ไหน ROS 2 มี message มาตรฐานสำหรับเรื่องนี้โดยเฉพาะ
คือ `geometry_msgs/msg/Twist`:

```
linear.x   metres per second forward   (negative = backwards)
angular.z  radians per second turning  (positive = left)
```

จริง ๆ แล้ว Twist มีตัวเลขหกตัว สำหรับหุ่นที่เคลื่อนที่ได้แบบ 3 มิติ
แต่หุ่นสองล้อที่วิ่งบนพื้นใช้ได้แค่สองตัวนี้

นี่คือข้อดีของการใช้ ROS 2: **หุ่นยนต์มีล้อทุกตัวในโลก
เข้าใจ Twist บน `/cmd_vel`** และหุ่นของคุณกำลังจะเข้าร่วม
แก๊งนี้

## ตั้งค่า domain ของทีมคุณ

จำเลขจากบทที่ 2 ได้ไหม มันต้องใส่ไว้สองที่

ใน `firmware/include/config.h`:

```c
#define ROS_DOMAIN_ID  7
```

และบนคอมพิวเตอร์ของคุณ ซึ่งคุณทำไปแล้วในบทที่ 2 ตอนที่ใส่
ไว้ใน `~/.bashrc` เช็กดู:

```bash
echo $ROS_DOMAIN_ID      # ต้องพิมพ์เลขเดียวกับใน config.h
```

**สองค่านี้ต้องตรงกัน** และต้องไม่ซ้ำกับทีมอื่นเลย
ถ้าตั้งผิด คุณจะไปขับหุ่นของคนอื่น -- ซึ่งก็ตลกดี
อยู่ประมาณสองนาที

## โค้ดของคุณ: TODOs 2-4

มีช่องว่างสั้น ๆ สามที่ แต่ละที่มี comment `TODO(student)` บอก
ว่าต้องใส่อะไร:

| TODO | ไฟล์ | หน้าที่ |
|---|---|---|
| 2/4 | [firmware/src/microros/main.cpp](../firmware/src/microros/main.cpp), `onCmdVel()` | หุ่นทำตาม Twist ทุกอันที่ได้รับ |
| 3/4 | [ros2_ws/src/teleop/teleop/key_teleop.py](../ros2_ws/src/teleop/teleop/key_teleop.py), `tick()` | ใส่ความเร็วของคุณลงใน Twist |
| 4/4 | ไฟล์เดียวกัน, `handle_key()` | w/s/a/d เปลี่ยนความเร็ว |

TODO 2 อยู่ใน firmware ดังนั้นแก้แล้วต้อง upload ส่วน TODOs 3 และ 4
อยู่บนคอมพิวเตอร์ ดังนั้นแก้แล้วให้รัน `colcon build` ใน `ros2_ws` ถ้าหุ่น
เชื่อมต่อได้แต่ไม่ขยับเลย แปลว่ายังมีอันใดอันหนึ่งว่างอยู่
`ros2 topic echo /cmd_vel` จะบอกได้ว่าเป็นฝั่งไหน: ถ้าเป็นศูนย์หมด แปลว่า
ฝั่งคอมพิวเตอร์ (3 หรือ 4)

## Upload

**อันนี้ให้ build จาก terminal ด้วย script:**

```bash
./scripts/build_firmware.sh microros upload
```

อย่าใช้ปุ่ม build ของ VS Code -- อย่างน้อยก็ในครั้งแรก เหตุผลคือ

build นี้ compile micro-ROS จาก source รวมถึง
ชุดเครื่องมือ build ของ ROS ที่มันมีเป็นของตัวเองด้วย ในบทที่ 1 คุณเพิ่ม ROS 2 ไว้ใน
`~/.bashrc` เพื่อให้โหลดในทุก terminal และนั่นแหละที่ทำให้มันสับสน:
build ไปเจอ ROS *ของคุณ* แทนที่จะเป็นของมันเอง แล้วก็ fail
พร้อม error ของ CMake ยาวเป็นพรืดเกี่ยวกับ `rosidl_runtime_cpp` ที่อ้างถึง
workspace ซึ่งไม่เกี่ยวอะไรกับโปรเจกต์นี้เลย

`build_firmware.sh` จะล้างค่าพวกนั้นก่อน build มันเลยใช้ได้
เลย (ปุ่มของ VS Code ก็ใช้ได้เหมือนกัน ตราบใดที่คุณเปิด VS Code
จากเมนูแอปพลิเคชัน ไม่ใช่พิมพ์ `code .` ใน terminal
ที่โหลด ROS ไว้แล้ว)

การ compile micro-ROS ใช้เวลา **2-3 นาที** ถ้านี่เป็น
firmware ตัวแรกที่คุณ build บนเครื่องนี้ ให้บวกเพิ่มอีกประมาณ 8 นาทีสำหรับ
ดาวน์โหลด compiler ของ ESP32 หลังจากนั้นทุกอย่างจะถูก cache ไว้และ
การ build ซ้ำใช้เวลาแค่ไม่กี่วินาที

ก่อน upload เช็กว่าใน `firmware/include/config.h` มี WiFi ของคุณ,
IP ของคอมพิวเตอร์คุณ (`hostname -I` เอาเลขแรก) ใน `AGENT_IP` และ
เลข domain ของคุณ ถ้า upload ไม่ผ่าน ดู
[troubleshooting.md](troubleshooting.md#the-board-wont-upload)

## ทุก terminal นับจากนี้

คุณจะเปิด terminal ไว้สามอัน `~/.bashrc` ของคุณตั้งค่าให้แล้ว (ROS 2,
workspace นี้, domain ของคุณ) เลยไม่ต้องพิมพ์อะไรก่อน ถ้า
คำสั่งไหนบอกว่า "package not found" หรือคุณมองไม่เห็นหุ่น ให้กลับไปดู
บทที่ 1 และ 2:

```bash
echo $ROS_DOMAIN_ID      # เลขของทีมคุณ
```

## เริ่ม agent

Terminal 1:

```bash
./scripts/start_agent.sh
```

เปิดทิ้งไว้ พอ ESP32 เชื่อมต่อได้ คุณจะเห็นข้อความ
`session established` ขึ้นมาเป็นชุด ถ้าไม่เห็นอะไรเลย แปลว่าหุ่นติดต่อ
คอมพิวเตอร์คุณไม่ได้ -- เช็ก [troubleshooting.md](troubleshooting.md)

## ขับ

Terminal 2:

```bash
ros2 run teleop key_teleop
```

`w` `a` `s` `d` เพื่อขับ, spacebar เพื่อหยุด, `q` เพื่อออก

## พิสูจน์ว่า ESP32 เป็น node จริง ๆ

นี่คือหัวใจของบทนี้ ตอนที่ทุกอย่างรันอยู่ ใน
terminal 3:

```bash
ros2 node list
```
```
/key_teleop
/esp32_robot      <-- that is the microcontroller
```

```bash
ros2 topic echo /heartbeat
```

ตัวนับที่ ESP32 publish เอง ส่งมาถึงคอมพิวเตอร์ของคุณ

```bash
rqt_graph
```

หุ่นยนต์จะถูกวาดอยู่ในภาพข้าง ๆ node คีย์บอร์ดของคุณ สำหรับ
ส่วนอื่นของ ROS 2 แล้ว มันไม่ต่างอะไรจากโปรแกรมที่รันบนคอมพิวเตอร์เลย

## ขับโดยไม่ใช้คีย์บอร์ด

ไม่มีใครสนว่า Twist มาจากไหน:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.1}, angular: {z: 0.0}}' -r 10
```

`-r 10` แปลว่าส่งซ้ำสิบครั้งต่อวินาที ลองไม่ใส่ดู: หุ่นจะ
กระตุกทีเดียวแล้วหยุด นั่นคือ safety timeout ใน firmware --
ถ้าไม่มีคำสั่งเข้ามา 500 ms มอเตอร์จะหยุด ลองหาดูใน
[main.cpp](../firmware/src/microros/main.cpp)

## บันทึกแล้วเล่นซ้ำ

```bash
ros2 bag record /cmd_vel      # ขับไปรอบ ๆ แล้วกด Ctrl+C
ros2 bag play <folder>        # หุ่นจะทำซ้ำสิ่งที่คุณทำ
```

คุณไม่ได้เขียนเครื่องมือนี้เอง มันใช้ได้เพราะหุ่นของคุณพูด
ภาษาเดียวกับทุกอย่างใน ROS 2

## ลองทำดู

1. ปิด agent ระหว่างที่กำลังขับ หุ่นทำอะไร? เปิดใหม่ --
   มันกลับมาทำงานได้เองโดยไม่ต้องกด reset ไหม?
2. รัน `key_teleop` **สอง**ตัวพร้อมกัน เกิดอะไรขึ้น? แล้ว
   `ros2 topic hz /cmd_vel` บอกว่าอะไร?
3. เปลี่ยน `ROS_DOMAIN_ID` บนคอมพิวเตอร์ แต่ไม่เปลี่ยนบนหุ่น
   `ros2 node list` แสดงอะไร? ทำไมเรื่องนี้ถึงมีประโยชน์ที่ควรรู้?
4. `ros2 topic hz /heartbeat` -- ได้ 1 Hz พอดีเป๊ะไหม? ทำไมไม่?

# เมื่อมันไม่ทำงาน

ไล่ดูทีละข้อจากบนลงล่าง ปัญหาส่วนใหญ่อยู่ในสามข้อแรก

## VS Code ขึ้นว่า "Can not find working Python 3.6+ Interpreter"

Python ของเราน่าจะปกติดีเกือบแน่นอน ลองเช็กดู:

```bash
python3 --version        # Ubuntu 24.04 ได้ 3.12 -- PlatformIO ต้องการ 3.6 ขึ้นไป
```

ปัญหาจริง ๆ มักเป็นเพราะขาด package ไม่ใช่ขาด Python
extension ของ PlatformIO จะสร้าง virtual environment ให้ตัวเองตอนรัน
ครั้งแรก และต้องใช้ `python3-venv`:

```bash
sudo apt install python3-venv
```

จากนั้น reload VS Code (**Ctrl+Shift+P** -> "Developer: Reload Window")

ลองทดสอบว่าใช่สาเหตุนี้ไหม:

```bash
python3 -m venv /tmp/test && echo works && rm -rf /tmp/test
```

ถ้ามี error เกี่ยวกับ `ensurepip` แปลว่าขาด package นี้จริง

> **อย่าติดตั้ง Python ใหม่หรือเปลี่ยนตัว Python เพื่อแก้ปัญหานี้** บน Ubuntu
> `/usr/bin/python3` คือสิ่งที่ `apt` และ ROS 2 ใช้เป็นฐาน
> ถ้าไปเปลี่ยนมัน อาจทำให้ติดตั้งอะไรไม่ได้อีกเลย -- รวมถึงสิ่งที่
> ต้องใช้เพื่อย้อนกลับด้วย ROS 2 แต่ละ release ถูก build มาให้ใช้กับ
> Python เวอร์ชันเดียวโดยเฉพาะ ถ้าเปลี่ยนก็จะทำให้คอร์สนี้พังทั้งหมด

## micro-ROS firmware: CMake error เกี่ยวกับ `rosidl_runtime_cpp`

ถ้า error พูดถึง workspace ที่ไม่ใช่ของโปรเจกต์นี้ -- เช่น
`/home/you/some_other_ws/install/...` -- แปลว่า shell ของเราโหลด ROS 2 ไว้อยู่
แล้วตอน build firmware ดันไปเจออันนั้นแทนที่จะใช้ของตัวเอง

ให้ build ด้วย script ซึ่งจะล้างค่าพวกนั้นออกก่อน:

```bash
./scripts/build_firmware.sh microros upload
```

แล้วลบ build ที่ค้างไว้ครึ่งทางทิ้ง เริ่มใหม่แบบสะอาด:

```bash
rm -rf firmware/.pio
```

สาเหตุเดียวกันนี้ทำให้ปุ่ม build ใน VS Code fail ด้วย ถ้าเราเปิด VS
Code โดยพิมพ์ `code .` ใน terminal ที่โหลด ROS ไว้ ให้เปิดจาก
เมนู applications แทน หรือใช้ script ไปเลย

## micro-ROS firmware: "No module named 'catkin_pkg'"

การ build ในบทที่ 5 จะคอมไพล์ micro-ROS จาก source และทำผ่าน
**Python ของ PlatformIO เอง** ไม่ใช่ Python ของระบบ virtualenv ตัวนั้น
มองไม่เห็น ROS package ที่ติดตั้งไว้ทั้งระบบ เลยต้องมีเครื่องมือ build
ชุดของตัวเอง:

```bash
~/.platformio/penv/bin/python -m pip install catkin_pkg "empy==3.3.4" lark
```

`scripts/setup_pc.sh` ทำขั้นตอนนี้ให้อยู่แล้ว จะเจอปัญหานี้ก็ต่อเมื่อ
ติดตั้ง PlatformIO เองด้วยมือ

การล็อกเวอร์ชัน `empy` สำคัญนะ ตัว generate message ของ ROS 2 ใช้ API ของ
empy 3.x แต่ empy 4.x เปลี่ยน API ไปแล้ว — ถ้าติดตั้งโดยไม่ล็อกเวอร์ชัน
จะไป fail ทีหลัง และดูสาเหตุยากกว่ามาก

เช็กว่าใน venv มีอะไรบ้าง:

```bash
~/.platformio/penv/bin/python -m pip list | grep -Ei 'catkin|empy|lark'
```

ถ้าแก้อะไรตรงนี้ไป ให้ลบ `firmware/.pio/` แล้ว build ใหม่ —
ไม่อย่างนั้นมันจะใช้ build ที่ fail ซึ่ง cache ไว้

## เริ่ม build ใหม่ตั้งแต่ต้น: ใช้ `clean` หรือลบ `.pio`?

มีสองวิธีในการล้าง build เก่าทิ้ง และสองวิธีนี้ไม่เหมือนกัน

```bash
./scripts/build_firmware.sh microros clean   # ล้างเบา ๆ
rm -rf firmware/.pio                         # ลบทุกอย่าง
```

| | ลบอะไร | build ใหม่ใช้เวลา | ใช้ตอนไหน |
|---|---|---|---|
| `clean` | เฉพาะไฟล์ที่ compile แล้วของโปรแกรมนั้น | ไม่กี่วินาที | build มีอาการแปลก ๆ และอยาก compile ใหม่ให้สะอาด |
| `rm -rf firmware/.pio` | ทุกอย่าง รวมถึง library ของ micro-ROS ที่ดาวน์โหลดมา | หลายนาที | เปลี่ยน `board_microros_distro` หรือ transport ใน `platformio.ini` หรือเจอ error ตอน build micro-ROS ที่แก้ยังไงก็ไม่หาย |

`clean` จะเก็บ library ของ micro-ROS ไว้ และเวอร์ชันของ ROS 2 ถูก
build ฝังอยู่ใน library นั้น ดังนั้นหลังเปลี่ยน distro การใช้ `clean`
จะไม่ช่วยอะไรเลย ต้องลบ `.pio` เท่านั้น

<a id="the-board-wont-upload"></a>
## บอร์ด upload ไม่ได้

- สาย USB เป็นแบบชาร์จไฟอย่างเดียว ลองเปลี่ยนเส้นอื่น
- กดปุ่ม **BOOT** ค้างไว้ตอนที่ upload เริ่ม
- Serial Monitor ยังเปิดค้างจากรอบก่อน -- ปิดซะ เพราะมันยึด port ไว้
- `Permission denied /dev/ttyUSB0`:
  ```bash
  sudo usermod -aG dialout $USER
  ```
  แล้ว **log out แล้ว log in ใหม่**

## WiFi เชื่อมต่อไม่ได้เลย

- SSID และรหัสผ่านต้องพิมพ์ตัวเล็กตัวใหญ่ให้ตรง
- `config.h` ยังเป็น `MyNetwork` / `changeme` อยู่หรือเปล่า? ใส่ WiFi จริงของเรา
  แล้ว upload ใหม่
- ESP32 มองไม่เห็นเครือข่าย 5 GHz ต้องเป็น 2.4 GHz เท่านั้น
- WiFi สาธารณะแบบเปิดที่มีหน้า login ใช้ไม่ได้ และเครือข่ายที่
  ถามทั้ง username *และ* รหัสผ่าน (WPA2-Enterprise) ก็ใช้ไม่ได้เหมือนกัน
- hotspot จากมือถือมักใช้ได้ ในกรณีที่ WiFi ของโรงเรียนใช้ไม่ได้

## ล้อหมุนแค่ข้างเดียว และไม่มี error

pin ใน `firmware/include/motor.h` ไม่ตรงกับการต่อสายของเรา เทียบ
กับตารางใน [03-hardware.md](03-hardware.md) แล้วแก้ฝั่งที่ผิด
จากนั้น upload motor test ใหม่อีกรอบ

## ล้อทั้งสองข้างหมุนถอยหลัง

สลับ `L_IN1`/`L_IN2` และ `R_IN1`/`R_IN2` ใน `motor.h` แล้ว upload หรือ
สลับสายสองเส้นของมอเตอร์แต่ละตัวที่ driver

## `mosquitto_sub: command not found`

ยังไม่ได้ติดตั้ง broker ให้ใช้ apt ไม่ใช่ snap:

```bash
sudo apt install mosquitto mosquitto-clients
```

แล้วทำหัวข้อถัดไปด้วย

<a id="mqtt-the-gateway-dies-straight-away"></a>
## MQTT: gateway ดับทันทีที่เปิด

`[ERROR] [mqtt_teleop-1]: process has died ... exit code 1` แปลว่ามัน
ติดต่อ broker ไม่ได้ ส่วนใหญ่เป็นเพราะ broker รับฟังแค่จาก
คอมพิวเตอร์เครื่องตัวเองเท่านั้น:

```bash
ss -ltn | grep 1883      # ถ้ามีแค่ 127.0.0.1:1883 = นี่แหละปัญหา
```

เปิดให้อุปกรณ์อื่นเข้ามาได้:

```bash
echo -e "listener 1883\nallow_anonymous true" | sudo tee /etc/mosquitto/conf.d/workshop.conf
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

ตอนนี้ `ss` ควรจะแสดง `0.0.0.0:1883` ถ้าเราใส่ `host:=...` ไว้ ให้เอา
ออก -- ค่า default (`localhost`) ถูกต้องอยู่แล้วเมื่อ broker อยู่บน PC เครื่องนี้

## หุ่นยนต์ไม่ขยับ แต่ Serial Monitor ดูปกติ

- แบตมอเตอร์หมด หรือยังไม่ได้เปิดสวิตช์ ESP32 รันได้สบาย ๆ
  ด้วยไฟจาก USB ในขณะที่มอเตอร์ไม่มีไฟเลยสักนิด
- ไม่ได้ต่อสาย GND ระหว่าง ESP32 กับ motor driver ดู
  [03-hardware.md](03-hardware.md)
- `MIN_DUTY` ใน `motor.h` ต่ำเกินไปสำหรับมอเตอร์ของเรา ทุกคำสั่งจะถูก
  scale ให้อยู่เหนือค่านี้ แต่ถ้ามอเตอร์ต้องการแรงมากกว่าค่า
  default 60 ต่อให้สั่งเต็มสปีดก็จะแค่มีเสียงหึ่ง ๆ ให้เพิ่มค่าขึ้นจน
  หุ่นยนต์ขยับได้ แล้วหยุดแค่นั้น -- ถ้าสูงเกินไป ความเร็วต่ำ ๆ จะหายไป

## gateway พิมพ์คำสั่งออกมา แต่หุ่นยนต์ไม่ทำอะไรเลย

ฝั่ง MQTT ทำงานปกติ ปัญหาอยู่ระหว่างคอมพิวเตอร์กับหุ่นยนต์

- หุ่นยนต์รัน firmware **micro-ROS** อยู่หรือเปล่า? motor test จะ
  ไม่สนคำสั่งใด ๆ เลย ให้ upload `microros`
- agent รันอยู่หรือเปล่า (`./scripts/start_agent.sh`)?
- `ros2 node list` แสดง `/esp32_robot` ไหม? ถ้าไม่ ดูหัวข้อ "micro-ROS
  build ผ่าน แต่ node ไม่โผล่มาเลย" ด้านล่าง

## ขยับแป๊บเดียวแล้วหยุด

ทำงานตามที่ออกแบบไว้ safety timeout จะหยุดมอเตอร์เมื่อไม่มี
คำสั่งเข้ามาเป็นเวลา 500 ms ให้ส่งคำสั่งซ้ำ ๆ (`-r 10` กับ
`ros2 topic pub`) แทนการส่งครั้งเดียว

## `ros2 run` / `ros2 launch` บอกว่าหา package ไม่เจอ

ไม่ workspace ยังไม่เคยถูก build ก็ terminal นี้ยังไม่ได้โหลดมัน:

```bash
cd ~/AI-Camp/ros2_ws
colcon build                 # ทำครั้งเดียว และทำใหม่หลังแก้โค้ด Python
source install/setup.bash    # หรือใส่ไว้ใน ~/.bashrc (บทที่ 1)
```

ถ้าใส่ไว้ใน `~/.bashrc` แล้วแต่ยังหาไม่เจอ แปลว่าเรา build workspace
*หลังจาก* เปิด terminal นี้ไปแล้ว ให้เปิด terminal ใหม่

## ฉันดันไปขับหุ่นยนต์ของคนอื่น

มีสองทีมใช้ `ROS_DOMAIN_ID` ซ้ำกัน หรือใช้ `ROBOT_ID` ซ้ำกัน ทั้งสองค่า
ต้องไม่ซ้ำกันในแต่ละทีม และค่า domain ต้องตรงกันระหว่าง
`firmware/include/config.h` กับทุก terminal บนคอมพิวเตอร์ของเรา

```bash
echo $ROS_DOMAIN_ID                          # คอมพิวเตอร์ของเรา
grep ROS_DOMAIN_ID ~/.bashrc                 # ค่ามาจากไหน
grep ROS_DOMAIN_ID firmware/include/config.h # หุ่นยนต์ของเรา
```

มีบรรทัด `ROS_DOMAIN_ID` สองบรรทัดใน `~/.bashrc` (อันหนึ่งมาจากโปรเจกต์อื่น) หรือเปล่า?
บรรทัดสุดท้ายจะเป็นตัวที่ใช้ ให้เก็บไว้แค่บรรทัดเดียว

ถ้าเปลี่ยนค่าใน `config.h` ต้อง upload ใหม่ -- เพราะค่านี้ถูกคอมไพล์ฝังไว้

## micro-ROS build ผ่าน แต่ node ไม่โผล่มาเลย

- agent รันอยู่หรือเปล่า? ให้เปิด agent ก่อนหุ่นยนต์
- ถ้า `start_agent.sh` บอกว่า agent ยังไม่ได้ build ให้รัน
  `./scripts/setup_pc.sh` -- มันจะ build จาก source ซึ่งใช้เวลา
  หลายนาที
- `ROS_DOMAIN_ID` ตรงกันทั้งสามที่ไหม -- shell ของเรา, shell ของ
  agent และ `config.h`? ถ้าไม่ตรงกัน session จะเชื่อมต่อได้ แต่
  `ros2 node list` จะไม่แสดงอะไรเลย
- `board_microros_distro` ใน `platformio.ini` ตรงกับ ROS 2 บน
  คอมพิวเตอร์ของเราไหม? Ubuntu 24.04 ใช้ `jazzy` ส่วน 22.04 ใช้ `humble` ถ้าไม่ตรงกัน
  จะเชื่อมต่อได้แล้วก็เงียบไปเลย -- เป็นอาการที่งงที่สุดของ
  ทั้งโปรเจกต์ `./scripts/check_setup.sh` เช็กเรื่องนี้ให้ได้
- อยู่ subnet เดียวกันไหม? หุ่นยนต์กับคอมพิวเตอร์ต้องติดต่อกันได้
  ลองเช็กด้วย `ping` จากฝั่งหนึ่งไปอีกฝั่ง
- ถ้าเปลี่ยน distro หรือ transport ให้ลบ `.pio/` แล้ว build ใหม่
  เพราะค่านี้ถูกฝังไว้ตอน build

## มือถือติดต่อ broker ไม่ได้

- มือถือต่อ WiFi เดียวกับคอมพิวเตอร์หรือเปล่า?
- address ของ broker ในแอปต้องเป็น IP ของคอมพิวเตอร์ ไม่ใช่ `localhost`
- เช็กว่า broker เห็นข้อความไหม:
  ```bash
  mosquitto_sub -t 'robot/#' -v
  ```
  กดปุ่มดู ถ้าไม่มีอะไรขึ้นมา แปลว่าปัญหาอยู่ระหว่างมือถือกับ broker
  ไม่ใช่ระหว่าง broker กับหุ่นยนต์

## หุ่นยนต์กระตุกแล้วหยุด ตอนที่กดปุ่มในมือถือค้างไว้

"Repeat payload until released" ปิดอยู่ ข้อความเดียวตอนกดไม่
พอ -- firmware จะหยุดหลังจากเงียบไป 500 ms ดู
[07-phone-teleop.md](07-phone-teleop.md)

## เมื่อวานยังดี ๆ อยู่เลย

IP ของคอมพิวเตอร์เราเปลี่ยน เช็ก `hostname -I` ใหม่แล้วอัปเดต
`config.h` `./scripts/check_setup.sh` จับปัญหานี้ได้

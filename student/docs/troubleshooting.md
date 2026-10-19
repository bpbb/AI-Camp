# การแก้ไขปัญหา

เอกสารนี้รวบรวมปัญหาที่พบบ่อยและวิธีแก้ไข ให้ตรวจสอบตามลำดับหัวข้อจากบนลงล่าง

## VS Code แสดงข้อความ "Can not find working Python 3.6+ Interpreter"

โดยทั่วไป Python ของระบบทำงานได้ตามปกติ ให้ตรวจสอบเวอร์ชันดังนี้

```bash
python3 --version        # Ubuntu 24.04 ใช้เวอร์ชัน 3.12 ส่วน PlatformIO ต้องการเวอร์ชัน 3.6 ขึ้นไป
```

สาเหตุของปัญหานี้มักเกิดจากการขาด package มิใช่การขาด Python
extension ของ PlatformIO จะสร้าง virtual environment ของตนเองเมื่อรัน
ครั้งแรก ซึ่งต้องใช้ `python3-venv` ให้ติดตั้งดังนี้

```bash
sudo apt install python3-venv
```

จากนั้นให้ reload VS Code (**Ctrl+Shift+P** -> "Developer: Reload Window")

ตรวจสอบว่าปัญหาเกิดจากสาเหตุนี้หรือไม่ด้วยคำสั่งต่อไปนี้

```bash
python3 -m venv /tmp/test && echo works && rm -rf /tmp/test
```

หากปรากฏ error เกี่ยวกับ `ensurepip` แสดงว่าระบบขาด package ดังกล่าว

> **ห้ามติดตั้ง Python ใหม่หรือเปลี่ยน Python ของระบบเพื่อแก้ไขปัญหานี้** บน Ubuntu
> `/usr/bin/python3` เป็นพื้นฐานที่ `apt` และ ROS 2 ใช้งาน
> การเปลี่ยนแปลงอาจทำให้ไม่สามารถติดตั้งซอฟต์แวร์ใด ๆ ได้อีก รวมถึงซอฟต์แวร์ที่
> จำเป็นสำหรับการย้อนกลับ นอกจากนี้ ROS 2 แต่ละ release ถูก build ให้ใช้กับ
> Python เวอร์ชันใดเวอร์ชันหนึ่งโดยเฉพาะ การเปลี่ยนเวอร์ชันจะทำให้ระบบทั้งหมดของหลักสูตรนี้ใช้งานไม่ได้

## micro-ROS firmware: CMake error เกี่ยวกับ `rosidl_runtime_cpp`

หาก error อ้างถึง workspace ที่ไม่ใช่ของโปรเจกต์นี้ เช่น
`/home/you/some_other_ws/install/...` แสดงว่า shell ได้โหลด ROS 2 ไว้ก่อนแล้ว
และขั้นตอน build firmware ใช้ค่าดังกล่าวแทนค่าของตนเอง

ให้ build ผ่าน script ซึ่งจะล้างค่าเหล่านั้นออกก่อน

```bash
./scripts/build_firmware.sh microros upload
```

จากนั้นให้ลบ build ที่ค้างอยู่ไม่สมบูรณ์ แล้วเริ่ม build ใหม่ทั้งหมด

```bash
rm -rf firmware/.pio
```

สาเหตุเดียวกันนี้ทำให้ปุ่ม build ใน VS Code ล้มเหลวด้วย หากเปิด VS
Code ด้วยคำสั่ง `code .` จาก terminal ที่โหลด ROS ไว้ ให้เปิดจาก
เมนู applications แทน หรือใช้ script ในการ build

## micro-ROS firmware: "cannot open .../.platformio/penv/bin/activate"

library ของ micro-ROS จะ build ภายใน `~/.platformio/penv` เสมอ และเครื่องนี้
ยังไม่มี venv ดังกล่าว (เนื่องจากติดตั้ง PlatformIO ด้วยวิธีอื่น เช่น pipx)
ให้รันสคริปต์ setup อีกครั้ง สคริปต์จะสร้าง venv และย้าย PlatformIO ไปไว้ที่นั่น:

```bash
bash scripts/setup_pc.sh
```

จากนั้นลบ `firmware/.pio` เพื่อไม่ให้ใช้ผล build ที่ล้มเหลวซ้ำ แล้ว build ใหม่

## micro-ROS firmware: "No module named 'catkin_pkg'"

การ build ในบทที่ 5 เป็นการคอมไพล์ micro-ROS จาก source ผ่าน
**Python ของ PlatformIO** มิใช่ Python ของระบบ virtualenv ดังกล่าว
ไม่สามารถเข้าถึง ROS package ที่ติดตั้งไว้ในระบบ จึงต้องติดตั้งเครื่องมือ build
แยกต่างหาก ดังนี้

```bash
bash scripts/setup_pc.sh      # ติดตั้งลงใน Python ที่ถูกต้องให้อัตโนมัติ
```

Python ที่ใช้ขึ้นอยู่กับวิธีติดตั้ง PlatformIO (pipx บน Ubuntu 24.04,
Python ของระบบบน 22.04 หรือ venv ของ VS Code extension) จึงให้สคริปต์
setup เป็นผู้ตรวจสอบและติดตั้ง ซึ่งสามารถรันซ้ำได้อย่างปลอดภัย

จำเป็นต้องระบุเวอร์ชันของ `empy` ให้ตรงตามที่กำหนด เนื่องจากตัว generate message ของ ROS 2 ใช้ API ของ
empy 3.x ขณะที่ empy 4.x มีการเปลี่ยนแปลง API หากติดตั้งโดยไม่ระบุเวอร์ชัน
การ build จะล้มเหลวในขั้นตอนถัดไป และวิเคราะห์สาเหตุได้ยากกว่า

ตรวจสอบด้วยคำสั่งต่อไปนี้

```bash
./scripts/check_setup.sh      # ตรวจสอบ Python ที่รัน pio
```

หลังแก้ไขส่วนนี้ ให้ลบ `firmware/.pio/` แล้ว build ใหม่
มิฉะนั้นระบบจะใช้ผลการ build ที่ล้มเหลวซึ่งถูก cache ไว้

## การเริ่ม build ใหม่ทั้งหมด: การใช้ `clean` เทียบกับการลบ `.pio`

การล้าง build เดิมทำได้สองวิธี ซึ่งให้ผลแตกต่างกัน

```bash
./scripts/build_firmware.sh microros clean   # ล้างเฉพาะไฟล์ที่คอมไพล์แล้ว
rm -rf firmware/.pio                         # ลบทั้งหมด
```

| | สิ่งที่ถูกลบ | เวลาที่ใช้ build ใหม่ | กรณีที่ใช้ |
|---|---|---|---|
| `clean` | เฉพาะไฟล์ที่คอมไพล์แล้วของโปรแกรมนั้น | ไม่กี่วินาที | build มีพฤติกรรมผิดปกติ และต้องการคอมไพล์ใหม่ทั้งหมด |
| `rm -rf firmware/.pio` | ทั้งหมด รวมถึง library ของ micro-ROS ที่ดาวน์โหลดไว้ | หลายนาที | เปลี่ยน `board_microros_distro` หรือ transport ใน `platformio.ini` หรือพบ error ขณะ build micro-ROS ที่ไม่สามารถแก้ไขด้วยวิธีอื่น |

`clean` จะคงไว้ซึ่ง library ของ micro-ROS และเวอร์ชันของ ROS 2 ถูก
build ฝังอยู่ใน library ดังกล่าว ดังนั้นหลังการเปลี่ยน distro การใช้ `clean`
จะไม่มีผล ต้องลบ `.pio` เท่านั้น

## `Permission denied` เมื่อรัน `./scripts/...`

สคริปต์ไม่มีสิทธิ์ในการรัน (execute permission) ซึ่งเกิดขึ้นเมื่อคัดลอกโปรเจกต์
ผ่าน USB drive, ไฟล์ ZIP หรือ cloud drive ให้กำหนดสิทธิ์ใหม่จากโฟลเดอร์โปรเจกต์:

```bash
chmod +x scripts/*.sh
```

หรือรันผ่าน `bash` โดยตรง เช่น `bash scripts/setup_pc.sh`

## `PlatformIO (pio) not found` หรือ `env: 'pio': No such file or directory`

ยังไม่ได้ติดตั้ง PlatformIO ซึ่งมักเกิดจาก `setup_pc.sh` หยุดทำงานกลางคัน
(เช่น จาก error ของ apt) ให้แก้ไข error นั้นก่อน แล้วรันสคริปต์อีกครั้ง
สคริปต์จะข้ามขั้นตอนที่ทำเสร็จแล้ว:

```bash
./scripts/setup_pc.sh
```

<a id="the-board-wont-upload"></a>
## ไม่สามารถ upload ไปยังบอร์ดได้

- สาย USB อาจเป็นชนิดสำหรับชาร์จไฟเท่านั้น ให้เปลี่ยนสายเส้นอื่น
- กดปุ่ม **BOOT** ค้างไว้ขณะที่การ upload เริ่มต้น
- Serial Monitor อาจเปิดค้างอยู่จากครั้งก่อนและยึด port ไว้ ให้ปิด Serial Monitor
- กรณีพบ `Permission denied /dev/ttyUSB0`:
  ```bash
  sudo usermod -aG dialout $USER
  ```
  จากนั้น **log out แล้ว log in ใหม่**

## ไม่สามารถเชื่อมต่อ WiFi ได้

- SSID และรหัสผ่านต้องตรงกันทั้งตัวพิมพ์เล็กและตัวพิมพ์ใหญ่
- ตรวจสอบว่า `config.h` ยังเป็นค่า `MyNetwork` / `changeme` หรือไม่ หากใช่ ให้ระบุข้อมูล WiFi ที่ใช้งานจริง
  แล้ว upload ใหม่
- ESP32 ไม่รองรับเครือข่าย 5 GHz ต้องใช้เครือข่าย 2.4 GHz เท่านั้น
- ไม่รองรับ WiFi สาธารณะแบบเปิดที่มีหน้า login และเครือข่ายที่
  ต้องระบุทั้ง username *และ* รหัสผ่าน (WPA2-Enterprise)
- hotspot จากโทรศัพท์มือถือสามารถใช้แทนได้ในกรณีที่ WiFi ของโรงเรียนใช้งานไม่ได้

## ล้อหมุนเพียงข้างเดียว และไม่มี error

pin ใน `firmware/include/motor.h` ไม่ตรงกับการต่อสาย ให้เปรียบเทียบ
กับตารางใน [03-hardware.md](03-hardware.md) แล้วแก้ไขส่วนที่ไม่ถูกต้อง
จากนั้น upload motor test ใหม่

## ล้อทั้งสองข้างหมุนถอยหลัง

สลับ `L_IN1`/`L_IN2` และ `R_IN1`/`R_IN2` ใน `motor.h` แล้ว upload ใหม่ หรือ
สลับสายสองเส้นของมอเตอร์แต่ละตัวที่ driver

## `mosquitto_sub: command not found`

ยังไม่ได้ติดตั้ง broker ให้ติดตั้งผ่าน apt (ไม่ใช้ snap) ดังนี้

```bash
sudo apt install mosquitto mosquitto-clients
```

จากนั้นให้ดำเนินการตามหัวข้อถัดไปด้วย

<a id="mqtt-the-gateway-dies-straight-away"></a>
## MQTT: gateway หยุดทำงานทันทีหลังเริ่มต้น

`[ERROR] [mqtt_teleop-1]: process has died ... exit code 1` แสดงว่า gateway
ไม่สามารถติดต่อ broker ได้ โดยส่วนใหญ่เกิดจาก broker รับการเชื่อมต่อเฉพาะจาก
เครื่องคอมพิวเตอร์ของตนเองเท่านั้น ตรวจสอบได้ดังนี้

```bash
ss -ltn | grep 1883      # หากแสดงเพียง 127.0.0.1:1883 แสดงว่าเป็นสาเหตุของปัญหา
```

ตั้งค่าให้อุปกรณ์อื่นเชื่อมต่อได้ ดังนี้

```bash
echo -e "listener 1883\nallow_anonymous true" | sudo tee /etc/mosquitto/conf.d/workshop.conf
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

หลังจากนั้น `ss` ควรแสดง `0.0.0.0:1883` หากมีการระบุ `host:=...` ไว้ ให้นำ
ออก เนื่องจากค่า default (`localhost`) ถูกต้องแล้วเมื่อ broker ทำงานอยู่บน PC เครื่องนี้

## หุ่นยนต์ไม่เคลื่อนที่ แต่ Serial Monitor แสดงผลปกติ

- แบตเตอรี่ของมอเตอร์หมด หรือยังไม่ได้เปิดสวิตช์ ESP32 สามารถทำงานได้
  ด้วยไฟจาก USB แม้มอเตอร์จะไม่ได้รับไฟเลย
- ไม่ได้ต่อสาย GND ระหว่าง ESP32 กับ motor driver ดู
  [03-hardware.md](03-hardware.md)
- `MIN_DUTY` ใน `motor.h` ต่ำเกินไปสำหรับมอเตอร์ที่ใช้ ทุกคำสั่งจะถูก
  scale ให้อยู่เหนือค่านี้ แต่หากมอเตอร์ต้องการกำลังมากกว่าค่า
  default 60 แม้สั่งที่ความเร็วสูงสุด มอเตอร์จะมีเพียงเสียงหึ่ง ให้เพิ่มค่าทีละน้อยจน
  หุ่นยนต์เริ่มเคลื่อนที่แล้วหยุดที่ค่านั้น หากตั้งค่าสูงเกินไป จะไม่สามารถควบคุมความเร็วต่ำได้

## gateway แสดงคำสั่ง แต่หุ่นยนต์ไม่ตอบสนอง

ส่วนของ MQTT ทำงานปกติ ปัญหาอยู่ระหว่างคอมพิวเตอร์กับหุ่นยนต์

- ตรวจสอบว่าหุ่นยนต์รัน firmware **micro-ROS** อยู่ motor test จะ
  ไม่รับคำสั่งใด ๆ ให้ upload `microros`
- ตรวจสอบว่า agent กำลังทำงานอยู่ (`./scripts/start_agent.sh`)
- ตรวจสอบว่า `ros2 node list` แสดง `/esp32_robot` หากไม่แสดง ให้ดูหัวข้อ "micro-ROS
  build สำเร็จ แต่ไม่พบ node" ด้านล่าง

## หุ่นยนต์เคลื่อนที่ระยะสั้นแล้วหยุด

เป็นพฤติกรรมตามที่ออกแบบไว้ safety timeout จะหยุดมอเตอร์เมื่อไม่มี
คำสั่งเข้ามาเป็นเวลา 500 ms ให้ส่งคำสั่งต่อเนื่อง (`-r 10` กับ
`ros2 topic pub`) แทนการส่งเพียงครั้งเดียว

## `ros2 run` / `ros2 launch` แจ้งว่าไม่พบ package

workspace ยังไม่ได้ถูก build หรือ terminal ปัจจุบันยังไม่ได้โหลด workspace ให้ดำเนินการดังนี้

```bash
cd ~/AI-Camp/ros2_ws
colcon build                 # ดำเนินการครั้งแรก และดำเนินการใหม่ทุกครั้งหลังแก้ไขโค้ด Python
source install/setup.bash    # หรือเพิ่มไว้ใน ~/.bashrc (บทที่ 1)
```

หากเพิ่มไว้ใน `~/.bashrc` แล้วแต่ยังไม่พบ package แสดงว่า workspace ถูก build
*หลังจาก* เปิด terminal นี้ ให้เปิด terminal ใหม่

## หุ่นยนต์ของทีมอื่นรับคำสั่งจากเครื่องของเรา

มีสองทีมใช้ `ROS_DOMAIN_ID` หรือ `ROBOT_ID` ซ้ำกัน ทั้งสองค่า
ต้องไม่ซ้ำกันระหว่างทีม และค่า domain ต้องตรงกันระหว่าง
`firmware/include/config.h` กับทุก terminal บนคอมพิวเตอร์ของทีม

```bash
echo $ROS_DOMAIN_ID                          # ค่าบนคอมพิวเตอร์
grep ROS_DOMAIN_ID ~/.bashrc                 # แหล่งที่มาของค่า
grep ROS_DOMAIN_ID firmware/include/config.h # ค่าบนหุ่นยนต์
```

ตรวจสอบว่าใน `~/.bashrc` มีบรรทัด `ROS_DOMAIN_ID` สองบรรทัด (เช่น บรรทัดหนึ่งมาจากโปรเจกต์อื่น) หรือไม่
ระบบจะใช้บรรทัดสุดท้าย ให้คงไว้เพียงบรรทัดเดียว

หากเปลี่ยนค่าใน `config.h` ต้อง upload ใหม่ เนื่องจากค่านี้ถูกคอมไพล์ฝังไว้ใน firmware

## micro-ROS build สำเร็จ แต่ไม่พบ node

- ตรวจสอบว่า agent กำลังทำงานอยู่ ให้เริ่ม agent ก่อนเปิดหุ่นยนต์
- หาก `start_agent.sh` แจ้งว่า agent ยังไม่ได้ build ให้รัน
  `./scripts/setup_pc.sh` ซึ่งจะ build จาก source และใช้เวลา
  หลายนาที
- ตรวจสอบว่า `ROS_DOMAIN_ID` ตรงกันทั้งสามตำแหน่ง ได้แก่ shell ที่ใช้งาน, shell ของ
  agent และ `config.h` หากไม่ตรงกัน session จะเชื่อมต่อได้ แต่
  `ros2 node list` จะไม่แสดงผลใด ๆ
- ตรวจสอบว่า `board_microros_distro` ใน `platformio.ini` ตรงกับ ROS 2 บน
  คอมพิวเตอร์ Ubuntu 24.04 ใช้ `jazzy` ส่วน 22.04 ใช้ `humble` หากไม่ตรงกัน
  การเชื่อมต่อจะสำเร็จแต่ไม่มีข้อมูลรับส่ง ซึ่งเป็นอาการที่วิเคราะห์ได้ยากที่สุดของ
  โปรเจกต์นี้ `./scripts/check_setup.sh` สามารถตรวจสอบรายการนี้ได้
- ตรวจสอบว่าหุ่นยนต์และคอมพิวเตอร์อยู่ใน subnet เดียวกันและติดต่อกันได้
  โดยใช้ `ping` จากฝั่งหนึ่งไปยังอีกฝั่งหนึ่ง
- หากเปลี่ยน distro หรือ transport ให้ลบ `.pio/` แล้ว build ใหม่
  เนื่องจากค่าเหล่านี้ถูกฝังไว้ขณะ build

## โทรศัพท์มือถือไม่สามารถติดต่อ broker ได้

- ตรวจสอบว่าโทรศัพท์มือถือเชื่อมต่อ WiFi เดียวกับคอมพิวเตอร์
- address ของ broker ในแอปต้องเป็น IP ของคอมพิวเตอร์ มิใช่ `localhost`
- ตรวจสอบว่า broker ได้รับข้อความหรือไม่:
  ```bash
  mosquitto_sub -t 'robot/#' -v
  ```
  จากนั้นกดปุ่มในแอป หากไม่มีข้อความปรากฏ แสดงว่าปัญหาอยู่ระหว่างโทรศัพท์มือถือกับ broker
  มิใช่ระหว่าง broker กับหุ่นยนต์

## หุ่นยนต์กระตุกแล้วหยุด ขณะกดปุ่มในโทรศัพท์มือถือค้างไว้

ตัวเลือก "Repeat payload until released" ถูกปิดอยู่ การส่งข้อความเพียงครั้งเดียวขณะกดปุ่ม
ไม่เพียงพอ เนื่องจาก firmware จะหยุดมอเตอร์เมื่อไม่ได้รับข้อความเป็นเวลา 500 ms ดู
[07-phone-teleop.md](07-phone-teleop.md)

## ระบบที่เคยทำงานได้ ไม่ทำงานในครั้งถัดมา

IP ของคอมพิวเตอร์อาจเปลี่ยนไป ให้ตรวจสอบ `hostname -I` แล้วอัปเดตค่าใน
`config.h` ทั้งนี้ `./scripts/check_setup.sh` สามารถตรวจพบปัญหานี้ได้

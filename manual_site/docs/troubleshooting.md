# การแก้ไขปัญหา

หาหัวข้อที่ตรงกับอาการที่เจอ แล้วทำตามทีละข้อ
หัวข้อเรียงตามกลุ่ม: ติดตั้งและ build → upload และ WiFi → มอเตอร์ → ROS 2 และหุ่น → MQTT และมือถือ

---

**กลุ่ม 1: ติดตั้งและ build**

## `ros2: command not found`

terminal นี้ยังไม่ได้ `source` ดูหัวข้อ "`source` คืออะไร" ใน [01-terminal.md](01-terminal.md)
ถ้าเพิ่มไว้ใน `~/.bashrc` แล้ว ให้ปิด terminal แล้วเปิดใหม่

## `ros2 run` หรือ `ros2 launch` บอกว่าหา package ไม่เจอ

ยังไม่ได้ build หรือ terminal นี้ยังไม่ได้โหลดผล build ให้รัน:

```bash
cd ~/AI-Camp/ros2_ws
colcon build                 # ทำครั้งแรก และทุกครั้งที่แก้โค้ด Python
source install/setup.bash    # โหลดผล build เข้า terminal นี้
```

ถ้าใส่ `source` ไว้ใน `~/.bashrc` แล้วแต่ยังหาไม่เจอ แปลว่าเพิ่ง build หลังจากเปิด terminal นี้
ให้เปิด terminal ใหม่

## VS Code ขึ้น "Can not find working Python 3.6+ Interpreter"

ส่วนใหญ่ Python ไม่ได้หาย เช็กเวอร์ชันก่อน (ต้องเป็น 3.6 ขึ้นไป Ubuntu 24.04 จะเป็น 3.12):

```bash
python3 --version
```

ถ้าเวอร์ชันถูกแล้ว แปลว่าขาด package ตัวหนึ่ง ให้ติดตั้ง:

```bash
sudo apt install python3-venv
```

แล้ว reload VS Code: กด **Ctrl+Shift+P** พิมพ์ "Developer: Reload Window"

เช็กว่าแก้หายแล้ว:

```bash
python3 -m venv /tmp/test && echo works && rm -rf /tmp/test
```

ถ้าขึ้น `works` แปลว่าใช้ได้ ถ้ายังมี error คำว่า `ensurepip` ให้ติดตั้งคำสั่งข้างบนอีกครั้ง

> **ห้ามติดตั้ง Python ใหม่ หรือเปลี่ยน Python ของเครื่องเด็ดขาด**
> ROS 2 และโปรแกรมติดตั้งของ Ubuntu ใช้ Python ตัวนี้ ถ้าเปลี่ยน ทั้งเครื่องอาจใช้งานไม่ได้

## build firmware ไม่ผ่าน: CMake error เกี่ยวกับ `rosidl_runtime_cpp`

สาเหตุ: build ผ่านปุ่มใน VS Code หรือ build ใน terminal ที่โหลด ROS ไว้ ทำให้เครื่องมือตีกัน

วิธีแก้:

1. ลบผล build ที่พังทิ้ง:

```bash
rm -rf firmware/.pio
```

2. build ใหม่ด้วยสคริปต์ (สคริปต์ล้างค่าที่ตีกันให้เอง):

```bash
./scripts/build_firmware.sh microros upload
```

ถ้าชอบเปิด VS Code ด้วยคำสั่ง `code .` จาก terminal ปุ่ม build ใน VS Code จะพังแบบเดียวกัน
ให้เปิด VS Code จากเมนูแทน หรือใช้สคริปต์ build เสมอ

## build firmware ไม่ผ่าน: "No module named 'catkin_pkg'"

ปกติ `scripts/setup_pc.sh` ติดตั้งให้แล้ว ถ้ายังเจอ ให้รัน:

```bash
~/.platformio/penv/bin/python -m pip install catkin_pkg "empy==3.3.4" lark
```

ต้องพิมพ์เวอร์ชัน `empy==3.3.4` ให้ตรง ถ้าใช้เวอร์ชันอื่นจะ build ไม่ผ่านในขั้นถัดไป

เช็กว่าติดตั้งครบ:

```bash
~/.platformio/penv/bin/python -m pip list | grep -Ei 'catkin|empy|lark'
```

แล้วลบ `firmware/.pio/` ก่อน build ใหม่ ไม่อย่างนั้นจะได้ผล build ที่พังจากครั้งก่อน

## อยาก build ใหม่ทั้งหมด: ใช้ `clean` หรือลบ `.pio`

```bash
./scripts/build_firmware.sh microros clean   # ล้างเฉพาะโค้ดที่ compile แล้ว (เร็ว)
rm -rf firmware/.pio                         # ลบทั้งหมด (ช้า หลายนาที)
```

| | ลบอะไร | build ใหม่ใช้เวลา | ใช้เมื่อไร |
|---|---|---|---|
| `clean` | เฉพาะโค้ดที่ compile แล้ว | ไม่กี่วินาที | build แปลก ๆ อยาก compile ใหม่ |
| `rm -rf firmware/.pio` | ทั้งหมด รวม micro-ROS ที่ดาวน์โหลดไว้ | หลายนาที | แก้ `board_microros_distro` ใน `platformio.ini` หรือลองทุกอย่างแล้วไม่หาย |

ถ้าแก้ `board_microros_distro` ต้องลบ `.pio` เท่านั้น ใช้ `clean` ไม่พอ

---

**กลุ่ม 2: upload และ WiFi**

<a id="the-board-wont-upload"></a>
## upload ลงบอร์ดไม่ได้

ลองทีละข้อ:

1. **เปลี่ยนสาย USB** สายบางเส้นชาร์จไฟได้อย่างเดียว ส่งข้อมูลไม่ได้
2. **กดปุ่ม BOOT บนบอร์ดค้างไว้** ตอนที่ upload เริ่ม
3. **ถอดสาย IN1 (GPIO 2) ออกชั่วคราว** แล้ว upload ใหม่ เสร็จแล้วค่อยเสียบกลับ
   (ใช้เมื่อเห็นข้อความ `Wrong boot mode` หรือ `Failed to connect`)
4. **ปิดหน้าจอ monitor** ที่อาจเปิดค้างจากครั้งก่อน เพราะมันจองช่อง USB ไว้
5. ถ้าเห็น `Permission denied /dev/ttyUSB0` ให้รัน:

```bash
sudo usermod -aG dialout $USER
```

   แล้ว **log out แล้ว log in ใหม่**

## หุ่นต่อ WiFi ไม่ได้

- ชื่อ WiFi และรหัสผ่านใน `config.h` ต้องถูกทุกตัว รวมถึงตัวพิมพ์เล็ก-ใหญ่
- เช็กว่า `config.h` ยังเป็นค่าตัวอย่าง `MyNetwork` / `changeme` อยู่ไหม ถ้าใช่ แก้เป็นของจริงแล้ว upload ใหม่
- ESP32 ใช้ได้เฉพาะ WiFi **2.4 GHz** (ใช้ 5 GHz ไม่ได้)
- ใช้ไม่ได้กับ WiFi ที่ต้องเข้าหน้า login หรือต้องใส่ทั้ง username และรหัสผ่าน
- ถ้า WiFi ของโรงเรียนใช้ไม่ได้ ใช้ hotspot จากมือถือแทนได้

## เคยใช้ได้ แต่วันนี้ใช้ไม่ได้

IP ของคอมพิวเตอร์อาจเปลี่ยน (เช่น ต่อ WiFi คนละตัวกับเมื่อวาน)

1. ดู IP ปัจจุบันด้วย `hostname -I`
2. แก้ `AGENT_IP` ใน `config.h` ให้ตรง
3. upload firmware ใหม่

`./scripts/check_setup.sh` ช่วยเช็กเรื่องนี้ให้ได้

---

**กลุ่ม 3: มอเตอร์และล้อ**

## หมุนแค่ล้อเดียว และไม่มี error

เลขขาใน `firmware/include/motor.h` ไม่ตรงกับสายที่ต่อจริง
เทียบทีละขากับตารางใน [03-hardware.md](03-hardware.md) แก้ให้ตรง แล้ว upload motor test ใหม่

## ล้อไม่หมุนเลยทั้งสองข้าง และไม่มี error

- เช็กว่า **jumper ที่ ENA และ ENB ยังเสียบอยู่** ถ้าถอด driver จะไม่จ่ายไฟให้มอเตอร์
- เช็กแบตเตอรี่ และสวิตช์เปิดแล้ว
- เช็กสาย GND ระหว่าง ESP32 กับ driver

## ล้อทั้งสองข้างหมุนกลับทิศ

เลือกทำอย่างใดอย่างหนึ่ง แล้ว upload ใหม่:

- สลับ `L_IN1` กับ `L_IN2` และ `R_IN1` กับ `R_IN2` ใน `motor.h`
- หรือสลับสายสองเส้นของมอเตอร์แต่ละตัวที่ driver

## หุ่นไม่ขยับ แต่ข้อความบนหน้าจอ monitor ปกติ

- **แบตเตอรี่หมด หรือยังไม่เปิดสวิตช์** ESP32 ทำงานด้วยไฟจาก USB ได้ แม้มอเตอร์ไม่มีไฟเลย
- **ลืมต่อสาย GND** ระหว่าง ESP32 กับ driver ดู [03-hardware.md](03-hardware.md)
- **มอเตอร์มีเสียงหึ่ง ๆ แต่ไม่หมุน** แรงไม่พอ ให้เพิ่มค่า `MIN_DUTY` ใน `motor.h` (เริ่มต้นคือ 60)
  ทีละนิดจนหุ่นเริ่มขยับ แล้วหยุดที่ค่านั้น ถ้าตั้งสูงเกินไป หุ่นจะวิ่งช้า ๆ ไม่ได้

## หุ่นวิ่งแล้วหยุด สลับกันไปเรื่อย ๆ

ไม่ใช่ปัญหา เป็นระบบความปลอดภัย: ถ้าหุ่นไม่ได้รับคำสั่งใหม่ภายใน 0.5 วินาที จะหยุดเอง

ถ้าใช้ `ros2 topic pub` แล้วไม่ใส่ `-r` คำสั่งจะถูกส่งแค่วินาทีละครั้ง หุ่นจึงวิ่ง-หยุดสลับกัน
ให้เติม `-r 10` (ส่งวินาทีละ 10 ครั้ง)

---

**กลุ่ม 4: ROS 2 และหุ่นยนต์**

## build และ upload ผ่าน แต่ `ros2 node list` ไม่เห็นหุ่น

เช็กทีละข้อ:

1. **agent เปิดอยู่ไหม** ต้องเปิด agent ก่อนเปิดหุ่น (`./scripts/start_agent.sh`)
   ถ้าสคริปต์บอกว่า agent ยังไม่ได้ build ให้รัน `./scripts/setup_pc.sh` (ใช้เวลาหลายนาที)
2. **เลข domain ตรงกันทั้ง 3 ที่ไหม**: terminal ที่ใช้, terminal ของ agent และ `config.h`
   ถ้าไม่ตรง agent จะต่อได้ แต่ `ros2 node list` จะว่างเปล่า
3. **`board_microros_distro` ตรงกับเครื่องไหม** (Ubuntu 24.04 = `jazzy`, 22.04 = `humble`)
   ถ้าไม่ตรง จะต่อได้แต่ไม่มีข้อมูลส่งถึงกัน เป็นอาการที่หาสาเหตุยากที่สุด
   `./scripts/check_setup.sh` เช็กข้อนี้ให้ได้ ถ้าแก้ ต้องลบ `.pio/` แล้ว build ใหม่
4. **หุ่นกับคอมพิวเตอร์อยู่ WiFi เดียวกันไหม** ลอง `ping` หากัน

## gateway แสดงคำสั่ง แต่หุ่นไม่ขยับ

ฝั่ง MQTT ทำงานปกติแล้ว ปัญหาอยู่ระหว่างคอมพิวเตอร์กับหุ่น ให้เช็ก:

1. หุ่นใช้ firmware **micro-ROS** อยู่ (ถ้ายังเป็น motor test จะไม่รับคำสั่ง ให้ upload `microros`)
2. agent เปิดอยู่ (`./scripts/start_agent.sh`)
3. `ros2 node list` มี `/esp32_robot` (ถ้าไม่มี ดูหัวข้อด้านบน)

## หุ่นของทีมอื่นขยับตามคำสั่งของเรา

มีสองทีมใช้เลข `ROS_DOMAIN_ID` หรือชื่อ `ROBOT_ID` ซ้ำกัน แต่ละทีมต้องใช้ไม่ซ้ำกัน

เช็กว่าเลขของเราตรงกันทั้งบนคอมพิวเตอร์และในหุ่น:

```bash
cd ~/AI-Camp
echo $ROS_DOMAIN_ID
grep "define ROS_DOMAIN_ID" firmware/include/config.h
```

ผลลัพธ์ที่ควรเห็น (ตัวเลขต้องตรงกัน และไม่ซ้ำกับทีมอื่น):

```text
7
#define ROS_DOMAIN_ID  7
```

เช็กว่าใน `~/.bashrc` มีบรรทัด `ROS_DOMAIN_ID` แค่บรรทัดเดียว (ถ้ามีหลายบรรทัด จะใช้บรรทัดสุดท้าย):

```bash
grep ROS_DOMAIN_ID ~/.bashrc
```

ถ้ามีหลายบรรทัด แก้ให้เหลือบรรทัดเดียว (เปลี่ยน `7` เป็นเลขทีม):

```bash
sed -i '/^export ROS_DOMAIN_ID=/d' ~/.bashrc
echo "export ROS_DOMAIN_ID=7" >> ~/.bashrc
```

ถ้าแก้เลขใน `config.h` ต้อง **upload firmware ใหม่** ด้วย

---

**กลุ่ม 5: MQTT และมือถือ**

## `mosquitto_sub: command not found`

ยังไม่ได้ติดตั้ง broker ให้ติดตั้งด้วย apt:

```bash
sudo apt install mosquitto mosquitto-clients
```

แล้วทำตามหัวข้อถัดไปด้วย

<a id="mqtt-the-gateway-dies-straight-away"></a>
## gateway ปิดตัวเองทันทีที่เปิด

ถ้าเห็น `[ERROR] [mqtt_teleop-1]: process has died ... exit code 1` แปลว่า gateway ต่อ broker ไม่ได้
ส่วนใหญ่เพราะ broker ยอมรับการเชื่อมต่อจากเครื่องตัวเองเท่านั้น

เช็กด้วย:

```bash
ss -ltn | grep 1883      # ถ้าขึ้นแค่ 127.0.0.1:1883 แปลว่าเป็นปัญหานี้
```

แก้ให้อุปกรณ์อื่นต่อได้:

```bash
echo -e "listener 1883\nallow_anonymous true" | sudo tee /etc/mosquitto/conf.d/workshop.conf
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

รัน `ss` อีกครั้ง ต้องเห็น `0.0.0.0:1883`
ถ้าเคยใส่ `host:=...` ตอนเปิด gateway ให้เอาออก ค่าเดิม (`localhost`) ถูกแล้ว

## มือถือต่อ broker ไม่ได้

- มือถือต้องต่อ **WiFi เดียวกับคอมพิวเตอร์**
- Broker address ในแอปต้องเป็น **IP ของคอมพิวเตอร์** ห้ามใช้ `localhost`
- เช็กว่าข้อความจากมือถือมาถึง broker ไหม รันคำสั่งนี้บนคอมพิวเตอร์ แล้วกดปุ่มในแอป:

```bash
mosquitto_sub -t 'robot/#' -v
```

  ถ้าไม่มีอะไรขึ้นเลย ปัญหาอยู่ระหว่างมือถือกับคอมพิวเตอร์ (ยังไม่เกี่ยวกับหุ่น)

## กดปุ่มในมือถือค้างไว้ แต่หุ่นกระตุกแล้วหยุด

เปิดหน้า Edit Panel ของปุ่มนั้น แล้วเช็ก:

- **Repeat publish until released** ต้อง **ติ๊ก** ถ้าไม่ติ๊ก แอปส่งแค่ครั้งเดียว แล้ว gateway สั่งหยุดหลัง 1 วินาที
- **Repeat interval in milliseconds** ต้องเป็น `200` ถ้าเป็น `1000` หุ่นจะกระตุกเป็นพัก ๆ

ดูวิธีตั้งปุ่มทั้งหมดใน [07-phone-teleop.md](07-phone-teleop.md)

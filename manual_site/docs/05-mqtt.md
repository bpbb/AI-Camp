# 5. MQTT: ส่งคำสั่งอีกแบบหนึ่ง

บทที่ผ่านมาเราส่ง message ด้วย ROS 2 บทนี้จะลองอีกวิธีหนึ่งที่ชื่อ **MQTT**

ทำไมต้องรู้จัก MQTT? อุปกรณ์รอบตัวจำนวนมาก เช่น เซนเซอร์ในบ้าน เครื่องจักรในโรงงาน และแอปบนมือถือ
ใช้ MQTT คุยกัน แต่ไม่รู้จัก ROS 2 ถ้าอยากให้หุ่นคุยกับอุปกรณ์พวกนี้ได้ ต้องใช้ MQTT

## MQTT ต่างจาก ROS 2 อย่างไร

```text
     ROS 2                              MQTT
  ┌──────────┐                     ┌──────────┐
  │  talker  │                     │ publisher│
  └────┬─────┘                     └────┬─────┘
       │ /chatter                       │ robot/<ROBOT_ID>/cmd
       │                                v
       │                          ┌──────────┐
       │  (they find each         │  BROKER  │   <-- the difference
       │   other by themselves)   └────┬─────┘
       v                                v
  ┌──────────┐                     ┌──────────┐
  │ listener │                     │subscriber│
  └──────────┘                     └──────────┘
```

**เหมือนกัน:** มี publisher, subscriber และ topic ที่ตั้งชื่อไว้ ฝั่งส่งกับฝั่งรับไม่ต้องรู้จักกัน

**ต่างกัน:** MQTT ต้องมี **broker** เป็นตัวกลาง ทุกข้อความต้องผ่าน broker
ถ้า broker หยุดทำงาน ทุกอย่างหยุดตาม ส่วน ROS 2 ไม่มีตัวกลาง แต่ละ node หากันเจอเอง

| | ROS 2 | MQTT |
|---|---|---|
| ต้องมีตัวกลางไหม | ไม่ต้อง | ต้องมี (broker) |
| ชื่อ topic | `/cmd_vel` | `robot/<ROBOT_ID>/cmd` |
| message | มีรูปแบบตายตัว เช่น `Twist` | ส่งอะไรก็ได้ |
| ใช้ผ่านอินเทอร์เน็ต | ยาก | ง่าย |
| ใช้บนมือถือ | ไม่ได้ | ได้ |

## ลองใช้ MQTT (ยังไม่ใช้หุ่น)

คอมพิวเตอร์มี broker รันอยู่แล้ว (ติดตั้งไว้ตั้งแต่บทที่ 0) ให้เปิด terminal 2 อัน

**Terminal 1** รอรับข้อความ:

```bash
mosquitto_sub -t test/hello -v
```

**Terminal 2** ส่งข้อความ:

```bash
mosquitto_pub -t test/hello -m "hi there"
```

ผลลัพธ์ที่ควรเห็นใน Terminal 1:

```text
test/hello hi there
```

ไม่ต้องเขียนโค้ด ไม่ต้อง build ไม่ต้อง `source`

| ตัวเลือก | ความหมาย |
|---|---|
| `-t` | ชื่อ **t**opic |
| `-m` | ข้อความ (**m**essage) ที่จะส่ง |
| `-v` | ให้ `mosquitto_sub` แสดงชื่อ topic หน้าข้อความด้วย |

> ถ้าขึ้น `mosquitto_sub: command not found` ให้ติดตั้งด้วย
> `sudo apt install mosquitto mosquitto-clients` แล้วดู
> [troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away)

### รับหลาย topic พร้อมกัน (wildcard)

ใน Terminal 1 กด Ctrl+C แล้วรันใหม่:

```bash
mosquitto_sub -t 'test/#' -v
```

`#` แปลว่า "ทุก topic ที่ขึ้นต้นด้วย `test/`"
ลองส่งจาก Terminal 2 ไปที่ `test/hello`, `test/other` และ `test/a/b/c` แล้วดูว่า Terminal 1 ได้รับครบไหม

## ต่อ MQTT เข้ากับหุ่นยนต์

หุ่นของเราพูด ROS 2 ได้แต่พูด MQTT ไม่ได้ จึงต้องมี **gateway** (ตัวแปลภาษา) คั่นอยู่ตรงกลาง
gateway รับข้อความ MQTT แล้วส่งต่อเป็น Twist ไปที่ `/cmd_vel`

```text
 MQTT
┌───────────────────────┐     ┌────────────────────┐     ┌────────────────┐
│ MQTT client           │     │ MQTT topic         │     │ node (gateway) │
│ phone / mosquitto_pub │────>│ robot/robot<N>/cmd │────>│ /mqtt_teleop   │
└───────────────────────┘     └────────────────────┘     └────────┬───────┘
       ┌──────────────────────────────────────────────────────────┘
 ROS 2 ▼                                    ┌──> motors
┌────────────┐     ┌────────────────────┐   │ ┌────────────┐
│ topic      │     │ node               │───┘ │ topic      │
│ /cmd_vel   │────>│ /esp32_robot       │────>│ /heartbeat │
└────────────┘     └────────────────────┘     └────────────┘

──>  = direction of data
```

- แถวบน (**MQTT**): มือถือหรือ `mosquitto_pub` ส่งข้อความไปที่ MQTT topic `robot/robot<N>/cmd`
  (`<N>` คือเลขเครื่อง) ผ่าน broker บนคอมพิวเตอร์ แล้ว **/mqtt_teleop** (gateway) รับข้อความนั้น
- แถวล่าง (**ROS 2**): gateway publish เป็น Twist ไปที่ `/cmd_vel` ส่วนที่เหลือเหมือนบทที่ 4 ทุกอย่าง

**ไม่ต้อง upload firmware ใหม่** หุ่นยังใช้ firmware จากบทที่ 4
หุ่นรู้แค่ว่ามีคำสั่งเข้ามาที่ `/cmd_vel` ไม่สนว่าใครส่งมา

### เปิด gateway

1. เปิด agent และหุ่นเหมือนบทที่ 4 (`./scripts/start_agent.sh`)
2. เช็กว่า `ros2 node list` มี `/esp32_robot`
3. เปิด terminal ใหม่ แล้วรัน gateway:

```bash
ros2 launch teleop mqtt_gateway.launch.py
```

ผลลัพธ์ที่ควรเห็น (ตัวอย่างของเครื่องที่ 7 ตัวเลขจะต่างกันตามเครื่อง):

```text
[INFO] [...] [mqtt_teleop]: robot/robot7/cmd (mqtt)  ->  /cmd_vel (ros 2)
```

เช็กว่าชื่อในบรรทัดนี้ตรงกับ `ROBOT_ID` ใน `config.h` ของเครื่องเรา
ถ้าไม่ตรง ให้ build ใหม่ แล้วเปิด gateway อีกครั้ง:

```bash
cd ~/AI-Camp/ros2_ws && colcon build && source install/setup.bash
```

ถ้าเห็น `process has died` ดู [troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away)

ไม่ต้องใส่ IP ให้ gateway เพราะ gateway กับ broker รันอยู่บนเครื่องเดียวกัน

## ขับหุ่นด้วยคำสั่ง MQTT

แทน `<เลขเครื่อง>` ในคำสั่งด้านล่างด้วยเลขเครื่องของเรา ให้ตรงกับ `ROBOT_ID` ใน `config.h` (เช่น เครื่องที่ 7 ใช้ `robot/robot7/cmd`)

เดินหน้า:

```bash
mosquitto_pub -t "robot/robot<เลขเครื่อง>/cmd" -m F
```

หยุด:

```bash
mosquitto_pub -t "robot/robot<เลขเครื่อง>/cmd" -m S
```

| ตัวอักษร | ความหมาย |
|---|---|
| `F` | เดินหน้า |
| `B` | ถอยหลัง |
| `L` | หมุนซ้าย |
| `R` | หมุนขวา |
| `S` | หยุด |

ผลลัพธ์ที่ควรเห็นใน terminal ของ gateway:

```text
[INFO] [...] [mqtt_teleop]: 'F' -> lin=+0.20 ang=+0.00
```

ถ้า gateway ขึ้น `'F' -> lin=+0.20` แต่หุ่นไม่ขยับ ปัญหาอยู่ที่ฝั่งหุ่น ให้เช็ก:

1. หุ่นใช้ firmware **micro-ROS** (ไม่ใช่ motor test จากบทที่ 3)
2. agent ยังเปิดอยู่
3. `ros2 node list` มี `/esp32_robot`

### กำหนดความเร็วเอง

gateway รับข้อความแบบ JSON ได้ด้วย (`lin` = เดินหน้า, `ang` = เลี้ยว):

```bash
mosquitto_pub -t "robot/robot<เลขเครื่อง>/cmd" -m '{"lin":0.1,"ang":0.5}'
```

## ดูข้อมูลที่วิ่งผ่านแต่ละชั้น

เปิด terminal 3 อัน แล้วรันคำสั่งด้านล่างอันละหนึ่งคำสั่ง:

```bash
mosquitto_sub -t 'robot/#' -v
```

```bash
ros2 topic echo /cmd_vel
```

```bash
rqt_graph
```

จากนั้นส่งคำสั่ง MQTT หนึ่งครั้ง แล้วดูว่าข้อความเดินทางอย่างไร:
ข้อความ MQTT → gateway แปลงเป็น Twist → หุ่นแปลงเป็นแรงมอเตอร์

ใน `rqt_graph` จะเห็น `mqtt_teleop` ส่งไปที่ `/cmd_vel` โดยมีหุ่นเป็นฝั่งรับ
แต่จะ **ไม่เห็น** ฝั่ง MQTT เพราะภาพนี้แสดงแค่ส่วนที่เป็น ROS 2

## ทำไมไม่ให้หุ่นใช้ MQTT ตรง ๆ

ทำได้ แต่หุ่นจะไม่ใช่ ROS 2 node อีกต่อไป
`rqt_graph` จะมองไม่เห็นหุ่น และโปรแกรม ROS 2 อื่น ๆ ก็สั่งหุ่นไม่ได้

การวาง gateway ไว้บนคอมพิวเตอร์ทำให้ได้ทั้งสองอย่าง:
หุ่นยังอยู่ในระบบ ROS 2 และยังรับคำสั่งจากโลกภายนอกผ่าน MQTT ได้
วิศวกรใช้วิธีนี้บ่อยมาก: วางตัวแปลงไว้ที่ขอบของระบบ แทนที่จะแก้ทั้งระบบ

## แบบฝึกหัดเพิ่มเติม (ไม่บังคับ)

ส่วนนี้ไม่บังคับ ทำเพิ่มได้เมื่อทำบทหลักเสร็จแล้ว

1. รัน `key_teleop` และส่งคำสั่ง MQTT พร้อมกัน (ทั้งสองส่งไป `/cmd_vel`) หุ่นมีพฤติกรรมอย่างไร ถือว่าเป็น bug ไหม
2. ส่ง `F` ครั้งเดียวแล้วไม่ส่งอะไรอีก หุ่นขยับสั้น ๆ แล้วหยุด เพราะอะไร
   ในระบบมีตัวจับเวลา **สองตัว** ที่ทำให้หุ่นหยุด ลองหาให้เจอ:
   ตัวหนึ่งชื่อ `SILENCE_TIMEOUT` ใน `mqtt_teleop.py` อีกตัวชื่อ `COMMAND_TIMEOUT_MS` ใน firmware
3. ส่งข้อความมั่ว ๆ เช่น `-m banana` gateway รับมืออย่างไร และ gateway ควรหยุดทำงานไหม
4. ทำไมใช้ `ros2 topic echo` ดูข้อความ MQTT ไม่ได้

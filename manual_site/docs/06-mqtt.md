# 6. MQTT: ส่งคำสั่งอีกแบบหนึ่ง

บทที่ผ่านมาเราส่ง message ด้วย ROS 2 บทนี้ลองอีกวิธีหนึ่งชื่อ **MQTT**

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

**เหมือนกัน:** มี publisher, subscriber และ topic ที่มีชื่อ ทั้งสองฝั่งไม่ต้องรู้จักกัน

**ต่างกัน:** MQTT ต้องมี **broker** เป็นตัวกลาง ทุกข้อความต้องผ่าน broker
ถ้า broker หยุดทำงาน ทุกอย่างหยุดตาม ส่วน ROS 2 ไม่มีตัวกลาง node หากันเจอเอง

| | ROS 2 | MQTT |
|---|---|---|
| ต้องมีตัวกลางไหม | ไม่ต้อง | ต้องมี (broker) |
| ชื่อ topic | `/cmd_vel` | `robot/<ROBOT_ID>/cmd` |
| message | มีรูปแบบกำหนด เช่น `Twist` | ส่งอะไรก็ได้ |
| ใช้ผ่านอินเทอร์เน็ต | ยาก | ง่าย |
| ใช้บนมือถือ | ไม่ได้ | ได้ |

## ลองใช้ MQTT (ยังไม่ใช้หุ่น)

คอมพิวเตอร์มี broker รันอยู่แล้ว (ติดตั้งตอนบทที่ 0) เปิด terminal 2 อัน

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

หุ่นของเราพูด ROS 2 ไม่ได้พูด MQTT จึงต้องมี **gateway** (ตัวแปลภาษา) อยู่ตรงกลาง
gateway รับข้อความ MQTT แล้วส่งต่อเป็น Twist ไปที่ `/cmd_vel`

```text
  ┌──────────┐        ┌──────────────┐   /cmd_vel   ┌─────────────┐
  │ anything │ ─MQTT─>│ mqtt_teleop  │ ───────────> │ esp32_robot │
  │ that can │        │  (gateway)   │              │ (unchanged) │
  │ publish  │        └──────────────┘              └─────────────┘
  └──────────┘
```

**ไม่ต้อง upload firmware ใหม่** หุ่นยังใช้ firmware จากบทที่ 5
หุ่นรู้แค่ว่ามีคำสั่งเข้ามาที่ `/cmd_vel` ไม่สนว่าใครส่งมา

### เปิด gateway

1. เปิด agent และหุ่นเหมือนบทที่ 5 (`./scripts/start_agent.sh`)
2. เช็กว่า `ros2 node list` มี `/esp32_robot`
3. เปิด terminal ใหม่ แล้วรัน gateway:

```bash
ros2 launch teleop mqtt_gateway.launch.py
```

ผลลัพธ์ที่ควรเห็น:

```text
[INFO] [...] [mqtt_teleop]: robot/robot7/cmd (mqtt)  ->  /cmd_vel (ros 2)
```

เช็กชื่อ `robot7` ในบรรทัดนี้ ต้องเป็นชื่อหุ่นของทีมเรา
ถ้าไม่ตรง ให้ build ใหม่ แล้วเปิด gateway อีกครั้ง:

```bash
cd ~/AI-Camp/ros2_ws && colcon build && source install/setup.bash
```

ถ้าเห็น `process has died` ดู [troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away)

ไม่ต้องใส่ IP ให้ gateway เพราะ gateway กับ broker อยู่เครื่องเดียวกัน

## ขับหุ่นด้วยคำสั่ง MQTT

`$ROBOT_ID` คือชื่อหุ่นที่ตั้งไว้ในบทที่ 2 จึงคัดลอกคำสั่งไปใช้ได้เลย

เดินหน้า:

```bash
mosquitto_pub -t "robot/$ROBOT_ID/cmd" -m F
```

หยุด:

```bash
mosquitto_pub -t "robot/$ROBOT_ID/cmd" -m S
```

| ตัวอักษร | ความหมาย |
|---|---|
| `F` | เดินหน้า |
| `B` | ถอยหลัง |
| `L` | หมุนซ้าย |
| `R` | หมุนขวา |
| `S` | หยุด |

หุ่นจะขยับประมาณ 1 วินาทีแล้วหยุดเอง **ตั้งใจออกแบบไว้แบบนี้** เพื่อความปลอดภัย

ผลลัพธ์ที่ควรเห็นที่ terminal ของ gateway:

```text
[INFO] [...] [mqtt_teleop]: 'F' -> lin=+0.20 ang=+0.00
```

ถ้า gateway ขึ้น `'F' -> lin=+0.20` แต่หุ่นไม่ขยับ ปัญหาอยู่ที่ฝั่งหุ่น ให้เช็ก:

1. หุ่นใช้ firmware **micro-ROS** (ไม่ใช่ motor test จากบทที่ 4)
2. agent ยังเปิดอยู่
3. `ros2 node list` มี `/esp32_robot`

### กำหนดความเร็วเอง

gateway รับข้อความแบบ JSON ได้ด้วย (`lin` = เดินหน้า, `ang` = เลี้ยว):

```bash
mosquitto_pub -t "robot/$ROBOT_ID/cmd" -m '{"lin":0.1,"ang":0.5}'
```

## ดูข้อมูลวิ่งผ่านทุกชั้น

เปิด terminal 3 อัน รันคนละคำสั่ง:

```bash
mosquitto_sub -t 'robot/#' -v
```

```bash
ros2 topic echo /cmd_vel
```

```bash
rqt_graph
```

แล้วส่งคำสั่ง MQTT หนึ่งครั้ง ดูว่าข้อความเดินทางอย่างไร:
ข้อความ MQTT → gateway แปลงเป็น Twist → หุ่นแปลงเป็นแรงมอเตอร์

ใน `rqt_graph` จะเห็น `mqtt_teleop` ส่งไปที่ `/cmd_vel` และหุ่นรับอยู่
แต่จะ **ไม่เห็น** ฝั่ง MQTT เพราะภาพนี้แสดงแค่ส่วนที่เป็น ROS 2

## ทำไมไม่ให้หุ่นใช้ MQTT ตรง ๆ

ทำได้ แต่หุ่นจะไม่ใช่ ROS 2 node อีกต่อไป
`rqt_graph` จะมองไม่เห็นหุ่น และโปรแกรม ROS 2 อื่น ๆ ก็สั่งหุ่นไม่ได้

การวาง gateway ไว้บนคอมพิวเตอร์ทำให้ได้ทั้งสองอย่าง:
หุ่นยังอยู่ในระบบ ROS 2 และยังรับคำสั่งจากโลกภายนอกผ่าน MQTT ได้
วิศวกรใช้วิธีนี้บ่อยมาก: วางตัวแปลงไว้ที่ขอบ แทนที่จะเปลี่ยนทั้งระบบ

## ลองคิดเองภายหลัง

ส่วนนี้ไม่บังคับ สามารถลองทำเองได้ในภายหลัง

1. รัน `key_teleop` และส่งคำสั่ง MQTT พร้อมกัน (ทั้งสองส่งไป `/cmd_vel`) หุ่นทำอย่างไร ถือว่าเป็น bug ไหม
2. ส่ง `F` ครั้งเดียวแล้วไม่ส่งอะไรอีก หุ่นขยับสั้น ๆ แล้วหยุด เพราะอะไร
   ในระบบมีตัวจับเวลา **สองตัว** ที่ทำให้หุ่นหยุด ลองหาให้เจอ:
   ตัวหนึ่งชื่อ `SILENCE_TIMEOUT` ใน `mqtt_teleop.py` อีกตัวชื่อ `COMMAND_TIMEOUT_MS` ใน firmware
3. ส่งข้อความมั่ว ๆ เช่น `-m banana` gateway ทำอย่างไร ควรหยุดทำงานไหม
4. ทำไมใช้ `ros2 topic echo` ดูข้อความ MQTT ไม่ได้

# 6. MQTT: อีกวิธีในการส่ง message

ตอนนี้เรารู้จักวิธีหนึ่งที่โปรแกรมคุยกันได้แล้ว นั่นคือ ROS 2 topic บทนี้จะสอน
อีกวิธีหนึ่ง และหัวใจของบทนี้คือการเปรียบเทียบสองวิธีนี้

MQTT มีอยู่ทุกที่ในโลกจริง ทั้งเทอร์โมสตัท เซนเซอร์ เครื่องจักรในโรงงาน
และแอปบนมือถือ แทบไม่มีอะไรในนั้นที่พูด ROS 2 ได้เลย ถ้าอยากให้หุ่นยนต์
คุยกับอะไรก็ได้ที่อยู่นอกโลก ROS ส่วนใหญ่ก็ต้องใช้วิธีนี้

## Pub/sub อีกครั้ง แต่มีตู้ไปรษณีย์

```
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

แนวคิดเดียวกัน: มี publisher, subscriber, topic ที่มีชื่อ และไม่มีใครรู้ว่า
มีใครอยู่อีกบ้าง

**ความต่างอยู่ที่ broker** ใน ROS 2 แต่ละ node หากันเจอเอง แต่ใน MQTT
ทุกอย่างต้องวิ่งผ่าน server ตัวเดียวตรงกลาง ถ้า broker หยุด ทุกอย่างก็หยุดตาม

| | ROS 2 | MQTT |
|---|---|---|
| ต้องมี server ตรงกลางไหม? | ไม่ต้อง | ต้อง คือ broker |
| ชื่อ topic | `/cmd_vel` | `robot/<ROBOT_ID>/cmd` |
| Message | message ที่มี type เช่น `Twist` | byte อะไรก็ได้ตามใจ |
| ใช้ผ่านอินเทอร์เน็ตได้ | ไม่ค่อยได้ | ได้ แถมง่ายด้วย |
| รันบนมือถือได้ | ไม่ได้ | ได้ |

แถวสุดท้ายนี่แหละคือเหตุผลที่มีบทนี้

## ลองเล่นโดยไม่ต้องมีหุ่นยนต์เลย

เหมือน talker กับ listener ในบทที่ 2 เป๊ะ แต่ใช้เครื่องมือของ MQTT แทน
คอมพิวเตอร์ของเรามี broker รันอยู่แล้ว (`setup_pc.sh` ติดตั้งไว้ให้)
ถ้า `mosquitto_sub` ขึ้นว่า "command not found" แปลว่ายังไม่ได้ติดตั้ง -- ให้รัน
`sudo apt install mosquitto mosquitto-clients` แล้วดู
[troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away)
เพื่อให้อุปกรณ์อื่นเชื่อมต่อเข้ามาได้

Terminal 1 — subscribe แล้วรอ:

```bash
mosquitto_sub -t test/hello -v
```

Terminal 2 — publish:

```bash
mosquitto_pub -t test/hello -m "hi there"
```

Message จะโผล่ขึ้นมาใน terminal 1 ไม่ต้องเขียนโค้ด ไม่ต้อง compile ไม่ต้อง `source`

ตัวอักษรสองตัวที่ต้องรู้:

| | ความหมาย |
|---|---|
| `-t` | **t**opic -- ตู้ไปรษณีย์ใบไหน |
| `-m` | **m**essage -- จะใส่อะไรลงไป |

(`-v` ของ `mosquitto_sub` แค่พิมพ์ชื่อ topic ไว้ข้าง ๆ แต่ละ message
ไม่ต้องใส่ `-h` เพราะ broker อยู่บนคอมพิวเตอร์เครื่องนี้)

ต่อไปลอง wildcard หยุด terminal 1 แล้วรัน:

```bash
mosquitto_sub -t 'test/#' -v
```

`#` แปลว่า "topic นี้และทุกอย่างที่อยู่ใต้มัน" ลอง publish ไปที่
`test/hello`, `test/other`, `test/a/b/c` — จะเห็นทั้งหมดเลย ใน ROS 2
ไม่มีอะไรแบบนี้

### เทียบกับบทที่ 2

1. ปิด broker: `sudo systemctl stop mosquitto` แล้วลอง publish ดู
   เกิดอะไรขึ้น? ทีนี้ลองคิดแบบเดียวกันกับ `talker` และ
   `listener` — มีอะไรที่เราปิดแล้วทำให้มันพังได้ไหม?
2. รัน `mosquitto_sub` บน topic ที่ไม่มีใคร publish มันบ่นอะไรไหม?
   แล้ว `ros2 topic echo` บน topic ที่ไม่มีใครใช้ทำแบบเดียวกันหรือเปล่า?
3. ถ้าจะส่งค่าอุณหภูมิจากเซนเซอร์ที่อยู่อีกซีกโลก จะเลือกระบบไหน?
   แล้วถ้าเป็นสองโปรแกรมบนหุ่นยนต์ตัวเดียวกันล่ะ?

```bash
sudo systemctl start mosquitto      # เปิดกลับคืนเมื่อทำเสร็จ
```

## ทีนี้มาต่อกับหุ่นยนต์

หุ่นยนต์ของเราพูด ROS 2 ไม่ใช่ MQTT เราเลยวาง **gateway** ไว้ตรงกลาง:
เป็น node ที่ subscribe MQTT แล้ว publish `/cmd_vel`

```
  ┌──────────┐        ┌──────────────┐   /cmd_vel   ┌─────────────┐
  │ anything │ ─MQTT─>│ mqtt_teleop  │ ───────────> │ esp32_robot │
  │ that can │        │  (gateway)   │              │ (unchanged) │
  │ publish  │        └──────────────┘              └─────────────┘
  └──────────┘
```

**ไม่ต้อง upload อะไรใหม่** หุ่นยนต์ยังใช้ firmware micro-ROS จาก
บทที่ 5 เหมือนเดิม และไม่เคยเห็น MQTT เลย ในมุมของ ESP32 แค่มีใครสักคน
publish มาที่ `/cmd_vel` — และมันก็ไม่เคยถามด้วยว่าใคร

เปิด agent และหุ่นยนต์เหมือนในบทที่ 5 แล้วเช็กว่า
`ros2 node list` แสดง `/esp32_robot`

จากนั้นเปิด gateway:

```bash
ros2 launch teleop mqtt_gateway.launch.py
```

ไม่ต้องใส่ IP: gateway รันอยู่บนคอมพิวเตอร์เครื่องเดียวกับ broker เลย
เชื่อมต่อไปที่ `localhost` ได้เลย (เฉพาะกรณีที่ broker อยู่บนคอมพิวเตอร์*คนละเครื่อง*
ให้เพิ่ม `host:=<that-computer's-ip>`) ส่วนหุ่นยนต์กับมือถือ
ยังต้องใช้ IP จริงของเครื่องเรา -- ใส่ไว้ใน `config.h` และในแอป

ควรจะเห็น `robot/<ROBOT_ID>/cmd (mqtt)  ->  /cmd_vel (ros 2)` ถ้ามัน
ขึ้นว่า `process has died` แทน ให้ดู
[troubleshooting.md](troubleshooting.md#mqtt-the-gateway-dies-straight-away)

## ขับหุ่นยนต์ด้วยการพิมพ์

```bash
mosquitto_pub -t robot/<ROBOT_ID>/cmd -m F
mosquitto_pub -t robot/<ROBOT_ID>/cmd -m S
```

แทน `<ROBOT_ID>` ด้วยชื่อที่อยู่ใน `firmware/include/config.h` ถ้า
เป็น `"test"` topic ก็คือ `robot/test/cmd` ส่วน gateway จะอ่านชื่อเดียวกัน
จาก `config.h` เอง เราเลยไม่ต้องพิมพ์ใส่ตรงนั้น หลังจาก
เปลี่ยน `ROBOT_ID` ให้รัน `colcon build` ใน `ros2_ws` เพื่อให้ gateway
ได้ค่าใหม่
`F` เดินหน้า, `B` ถอยหลัง, `L` เลี้ยวซ้าย, `R` เลี้ยวขวา, `S` หยุด gateway จะ
พิมพ์สิ่งที่ได้รับออกมาและหุ่นยนต์จะขยับ -- ประมาณหนึ่งวินาที
แล้วหยุดเอง ตั้งใจให้เป็นแบบนี้ ดูหัวข้อ "ลองทำดู" ด้านล่าง

ถ้า gateway พิมพ์ `'F' -> lin=+0.20` แต่หุ่นยนต์ไม่ขยับ แปลว่า
ปัญหาอยู่หลัง gateway: หุ่นยนต์รัน firmware **micro-ROS** อยู่หรือเปล่า
(ไม่ใช่ motor test), agent รันอยู่ไหม, และ
`ros2 node list` แสดง `/esp32_robot` หรือเปล่า?

มันยังเข้าใจ JSON ด้วย เผื่ออยากกำหนดความเร็วแบบเป๊ะ ๆ:

```bash
mosquitto_pub -t robot/<ROBOT_ID>/cmd -m '{"lin":0.1,"ang":0.5}'
```

## ดูทั้งสามชั้นพร้อมกัน

เปิดสี่ terminal แล้วจะเห็นทั้งสายเลย:

```bash
mosquitto_sub -t 'robot/#' -v    # ฝั่ง MQTT
ros2 topic echo /cmd_vel                      # ฝั่ง ROS 2
ros2 node list                                # ใครเกี่ยวข้องบ้าง
rqt_graph                                     # ภาพรวม
```

ลอง publish คำสั่งหนึ่งครั้ง แล้วดูมันกลายเป็น Twist จากนั้นกลายเป็น PWM
บนขามอเตอร์สองขา

สังเกตสิ่งที่ `rqt_graph` แสดง: `mqtt_teleop` publish ไปที่ `/cmd_vel`
และหุ่นยนต์ subscribe อยู่ ฝั่ง MQTT นั้น **มองไม่เห็น** จาก ROS 2 —
กราฟหยุดอยู่ที่ gateway เหมือนกับที่มันหยุดอยู่ที่ broker ใน
แผนภาพด้านบนเป๊ะ

## ลองทำดู

1. รัน `key_teleop` **และ** publish ผ่าน MQTT ไปพร้อมกัน ทั้งคู่
   ไปจบที่ `/cmd_vel` หุ่นยนต์จะทำอะไร? นี่คือ bug หรือเปล่า?
2. ส่ง `F` ครั้งเดียวแล้วไม่ส่งอะไรอีก หุ่นยนต์กระตุกแล้วหยุด
   ทำไม? ตอนนี้ในสายมี timeout อยู่ **สองตัว** — ตัวหนึ่งอยู่ใน
   gateway อีกตัวอยู่ใน firmware ลองหาให้เจอทั้งคู่
3. ส่งอะไรมั่ว ๆ: `mosquitto_pub ... -m banana` gateway ทำอะไร?
   gateway ควรพังเพราะ input ผิด ๆ ไหม?
4. ทำไมเราถึงแค่รัน `ros2 topic echo` แล้วเห็น message ของ MQTT ไม่ได้?

## ทำไมไม่ใส่ MQTT ลงในหุ่นยนต์ไปเลย?

ทำได้ แต่แบบนั้นหุ่นยนต์จะไม่ใช่ ROS 2 node อีกต่อไป: `ros2 bag` บันทึกมันไม่ได้
`rqt_graph` วาดมันไม่ได้ และไม่มีอะไรอื่นใน ROS 2 สั่งขับมันได้

การเอา gateway ไปไว้บนคอมพิวเตอร์แทน ทำให้หุ่นยนต์ยังอยู่ในโลก ROS
2 และยังเปิดให้โลกภายนอกเข้ามาได้ การแลกแบบนี้ — มีตัวแปลภาษา
อยู่ตรงขอบ แทนที่จะเปลี่ยนภาษาที่ระบบเราพูด — เป็นหนึ่งในการตัดสินใจ
ที่เจอบ่อยที่สุดในงานวิศวกรรมจริง

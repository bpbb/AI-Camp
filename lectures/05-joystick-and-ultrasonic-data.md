# Lecture 5: MQTT and Phone Teleoperation

**Camp:** NextGen AI Camp 2026

## Learning Objectives

- อธิบายเส้นทางคำสั่งจากโทรศัพท์ผ่าน MQTT ไปยังหุ่นยนต์
- เชื่อม Payload กับค่า `linear.x` และ `angular.z`
- ตรวจสอบข้อมูลทั้งฝั่ง MQTT และ ROS 2

## 1. Teleoperation Data Flow

Teleoperation คือการควบคุมหุ่นยนต์จากผู้ใช้ระยะไกล ในชุดนี้แอปโทรศัพท์ส่งคำสั่งผ่าน MQTT แล้ว Node `mqtt_teleop` แปลงเป็น Twist ให้หุ่นยนต์

```text
Phone buttons / Control panel
           │ MQTT payload
           ▼
      MQTT broker
           │ robot/<ROBOT_ID>/cmd
           ▼
      mqtt_teleop
           │ /cmd_vel: Twist
           ▼
 micro-ROS agent ↔ ESP32 → Motors
```

MQTT broker กระจายข้อความตาม Topic ส่วน `mqtt_teleop` แปลงข้อความเป็น ROS 2 Message หุ่นยนต์รับ Twist ผ่าน micro-ROS โดยไม่ต้องรับ MQTT โดยตรง

## 2. MQTT Robot Identification

`ROBOT_ID` เป็นชื่อที่ใช้แยก MQTT Topic ของหุ่นยนต์แต่ละทีม ผู้ส่งกับ Gateway ต้องใช้ชื่อช่องทางตรงกัน

```text
ROBOT_ID = robot1 → robot/robot1/cmd
ROBOT_ID = robot2 → robot/robot2/cmd
```

แต่ละทีมใช้ชื่อไม่ซ้ำกัน ส่วน `ROS_DOMAIN_ID` แยก ROS 2 Graph ที่ Gateway กับหุ่นยนต์ใช้สื่อสารกัน

## 3. MQTT Commands

Topic คำสั่งใช้รูปแบบ `robot/<ROBOT_ID>/cmd` เช่น `robot/robot1/cmd`

| Payload | การเคลื่อนที่ | `linear.x` | `angular.z` |
|---|---|---|---|
| `F` | เดินหน้า | `0.20` | `0.0` |
| `B` | ถอยหลัง | `-0.20` | `0.0` |
| `L` | หมุนซ้าย | `0.0` | `2.5` |
| `R` | หมุนขวา | `0.0` | `-2.5` |
| `S` | หยุด | `0.0` | `0.0` |

ค่าข้างต้นมาจากตาราง `LETTERS` ใน `mqtt_teleop.py` หากต้องการระบุความเร็วเอง ใช้ JSON:

```json
{"lin": 0.1, "ang": 0.5}
```

`lin` แปลงเป็น `linear.x` หน่วย m/s และ `ang` แปลงเป็น `angular.z` หน่วย rad/s

## 4. Gateway Operation

Gateway ใช้ `ROBOT_ID` เลือก MQTT Topic แล้วแปลงข้อความที่ได้รับให้เป็น Twist บน `/cmd_vel` ใน ROS Domain ของทีม

```text
robot/robot1/cmd ──→ mqtt_teleop ──→ /cmd_vel
     MQTT                             ROS 2
```

Gateway ใช้ `localhost` เมื่อ Broker อยู่บนเครื่องเดียวกัน ส่วนโทรศัพท์ต้องใช้ IP ของคอมพิวเตอร์ที่เปิด Broker

## 5. Phone Commands and Network Addresses

โทรศัพท์เป็นผู้ส่งคำสั่ง ส่วน Broker เป็นจุดรับและกระจายข้อมูล การส่งคำสั่งจึงต้องระบุทั้งที่อยู่ Broker และชื่อ Topic

```text
Phone
  │
  ├── Broker address ──→ Which computer receives the connection
  └── Topic name ──────→ Which command channel receives the data
```

IP address ระบุเครื่องบนเครือข่าย ส่วน Port ระบุช่องบริการบนเครื่องนั้น โทรศัพท์กับคอมพิวเตอร์ต้องเชื่อมต่อถึงกันได้ก่อน ข้อความจึงจะเดินทางไปถึง Broker

`localhost` หมายถึงเครื่องที่โปรแกรมนั้นกำลังทำงาน สำหรับ Gateway จึงอาจหมายถึงคอมพิวเตอร์ที่เปิด Broker แต่สำหรับแอปบนโทรศัพท์จะหมายถึงตัวโทรศัพท์เอง

### Button Events and Motion

การกดปุ่ม กดค้าง และปล่อยปุ่ม เป็นเหตุการณ์คนละอย่าง:

```text
Press and hold Forward:  F → F → F → F
Release:                                S
                        ────────────────→ Time
```

ข้อความ `F` ซ้ำแสดงว่าผู้ใช้ยังต้องการเดินหน้า ส่วน `S` ระบุให้หยุดทันทีที่ Gateway ประมวลผล การไม่มีข้อความใหม่อาจเกิดจากการปล่อยปุ่มหรือการเชื่อมต่อขาด ระบบจึงใช้ Timeout เป็นเงื่อนไขหยุดเพิ่มเติม

## 6. MQTT to ROS 2 Conversion

```text
┌────────────────────────────────────────┐
│ mqtt_teleop node                       │
│                                        │
│ Receive MQTT → Decode letter / JSON    │
│                         │              │
│                         ▼              │
│                  Set lin / ang         │
│                         │              │
│                         ▼              │
│ Timer → Publish Twist ─────────────────┼──→ /cmd_vel
└────────────────────────────────────────┘
```

Gateway ส่ง Twist ที่ 10 Hz หากไม่ได้รับ MQTT ใหม่เกินหนึ่งวินาที จะเปลี่ยนเป็นคำสั่งหยุด

ข้อความก่อนและหลัง Gateway แทนความต้องการเดียวกัน แต่มีรูปแบบต่างกัน:

```text
MQTT payload          ROS 2 Twist
     F        ──→     linear.x = 0.20
                      angular.z = 0.0
```

หาก Payload มาถึงแต่ยังไม่มี Twist ปัญหาอยู่ในช่วงแปลงหรือส่งต่อข้อมูล หาก Twist มาถึงหุ่นยนต์แล้วแต่ล้อไม่หมุน ต้องพิจารณาส่วนควบคุมมอเตอร์และกำลังไฟต่อไป

## 7. Sensor Data Overview

Ultrasonic sensor เป็นตัวอย่างแหล่งข้อมูลเพิ่มเติม หากมีส่วนอ่าน Sensor จะสามารถส่งค่าระยะทางให้โปรแกรมอื่นรับได้:

```text
Ultrasonic sensor → Sensor node → Distance topic → Display
```

ข้อมูลระยะเป็นค่าที่วัดได้ ไม่ใช่คำสั่งมอเตอร์ ตัวอย่างนี้แสดงการต่อยอดด้วย Sensor ส่วนการควบคุมในบทใช้ MQTT และไม่ต้องใช้ Ultrasonic

## Review Questions

1. MQTT broker กับ `mqtt_teleop` ทำหน้าที่ต่างกันอย่างไร?
2. Payload `F` เปลี่ยนเป็นข้อมูลใดบน `/cmd_vel`?
3. หาก MQTT มาถึงแต่หุ่นยนต์ไม่ขยับ ควรตรวจสอบข้อมูลจุดใดต่อ?

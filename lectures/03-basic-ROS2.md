# Lecture 3: ROS 2 System Overview, Publisher and Subscriber

**Camp:** NextGen AI Camp 2026

## Learning Objectives

| Topic | เป้าหมาย |
|---|---|
| Node, Topic, Pub/Sub | เข้าใจและตรวจสอบการสื่อสารด้วย ROS 2 CLI |
| Publisher | เข้าใจการสร้างข้อความพร้อมตัวนับใน `talker` |
| Subscriber | เข้าใจการรับข้อความใน `listener` |

## 1. ROS 2 Communication

| Term | ความหมาย |
|---|---|
| Node | ส่วนของโปรแกรมที่รับผิดชอบงานหนึ่งในระบบ |
| Topic | ช่องทางที่มีชื่อสำหรับส่งข้อมูล |
| Message | ข้อมูลที่มีชนิดและโครงสร้างกำหนดไว้ |
| Publisher | ส่วนของ Node ที่ส่ง Message |
| Subscriber | ส่วนของ Node ที่รับ Message |

```text
Publisher ───── Topic + Message ─────→ Subscriber
```

ผู้ส่งและผู้รับต้องใช้ Topic และชนิด Message ตรงกัน โดยไม่ต้องเรียกโค้ดของอีกฝ่ายโดยตรง

### Node Structure

Node หนึ่งรับและส่งข้อมูลได้หลายทาง เช่น Robot node รับคำสั่งความเร็วและส่ง Heartbeat กลับมา

```text
                     ┌───────────────────────────────────┐
                     │ Robot node                        │
/cmd_vel ───────────→│ Subscriber → Motor control         │
                     │                                   │
/heartbeat ←─────────│ Publisher ← Heartbeat counter      │
                     └───────────────────────────────────┘
```

Publisher และ Subscriber อยู่ภายใน Node ส่วน Topic เป็นช่องทางสื่อสารระหว่าง Node

### Multiple Subscribers

```text
                         ┌──→ Control node
Sensor node ─ /distance ─┼──→ Display node
                         └──→ Recording node
```

Topic เดียวมีผู้รับได้หลายตัว ภาพรวมของ Node และการเชื่อมต่อเรียกว่า **ROS 2 Graph**

## 2. Robot Communication

หุ่นยนต์ของค่ายใช้ Node ชื่อ `/esp32_robot` บน ESP32 เชื่อมกับคอมพิวเตอร์ผ่าน micro-ROS agent

```text
Control node ─── /cmd_vel ───→ esp32_robot ───→ Motors
                                  │
                             /heartbeat
                                  │
                                  ▼
                            Monitoring tool
```

| Topic | ข้อมูล | ทิศทาง |
|---|---|---|
| `/cmd_vel` | คำสั่งความเร็ว ชนิด `Twist` | ส่งไปยังหุ่นยนต์ |
| `/heartbeat` | ตัวนับ ชนิด `Int32` | ส่งจากหุ่นยนต์ |

Heartbeat ช่วยตรวจสอบการสื่อสารขณะหุ่นยนต์อยู่นิ่ง ไม่ใช่ค่าความเร็วล้อ

## 3. Talker and Listener

Package `workshop` มี `talker` ส่งข้อความพร้อมตัวนับ และ `listener` รับข้อความผ่าน `/chatter` ชนิด `std_msgs/msg/String` เช่น `hello 0`, `hello 1`

```text
┌──────────────────┐       /chatter       ┌──────────────────┐
│ talker           │ ──────────────────→ │ listener         │
│ Publisher        │ std_msgs/msg/String │ Subscriber       │
└──────────────────┘                     └──────────────────┘
             "hello 0", "hello 1", "hello 2", ...
```

ตัวอย่างใน Package `workshop` แยกหน้าที่ส่งและรับเป็นสอง Node โดยใช้ข้อความเป็นข้อมูล ยังไม่มีการสั่งมอเตอร์

### Message Sequence

```text
Time        talker          /chatter          listener
0 s         Publish ────── "hello 0" ──────→ Receive
1 s         Publish ────── "hello 1" ──────→ Receive
2 s         Publish ────── "hello 2" ──────→ Receive
```

ค่า Counter เพิ่มขึ้นทุกครั้งที่ส่ง ส่วนผู้รับแสดงข้อความที่มาถึง หากเปิดผู้รับหลังจากเริ่มส่งแล้ว ตัวเลขแรกที่เห็นอาจไม่ใช่ศูนย์

## 4. Talker Publisher

`talker` สร้าง String โดยนำข้อความ `MESSAGE` รวมกับตัวนับ แล้วส่งตาม Timer ที่กำหนดด้วย `RATE_HZ` ค่าเริ่มต้นคือหนึ่งครั้งต่อวินาที

```text
┌───────────────────────────┐
│ Talker Publisher          │
│                           │
│ Timer → Prepare message ──┼────→ /chatter
│              │            │
│              ▼            │
│        Increase count     │
└───────────────────────────┘
```

| ส่วนสำคัญ | หน้าที่ |
|---|---|
| Counter | เก็บค่าปัจจุบัน |
| Timer | กำหนดช่วงเวลาส่ง |
| Callback | ใส่ค่าลงใน Message ส่งออก และเพิ่มตัวนับ |

**Callback** คือฟังก์ชันที่ทำงานเมื่อเกิดเหตุการณ์ ใน Publisher นี้เหตุการณ์คือ Timer ครบเวลา

`MESSAGE` กำหนดข้อความ `RATE_HZ` กำหนดอัตราส่ง และ `TOPIC` กำหนดช่องทางที่ผู้รับต้องใช้ตรงกัน

**ตัวอย่าง:** เมื่อเพิ่ม `RATE_HZ` จาก `1` เป็น `2` ข้อความจะส่งประมาณทุกครึ่งวินาที

## 5. Listener Subscriber

`listener` รับ String จาก `/chatter` แล้วอ่าน Field `data` มาแสดงผ่าน Callback โดยใช้ Topic และชนิด Message ตรงกับ `talker`

```text
/chatter
    │
    ▼
┌───────────────────────────┐
│ Listener Subscriber       │
│                           │
│ Receive → Callback        │
│              │            │
│              ▼            │
│        Display text       │
└───────────────────────────┘
```

Callback ของ Subscriber ทำงานเมื่อมี Message เข้ามา และอ่านข้อความจาก `msg.data`

ในตัวอย่างนี้ Publisher ส่งตาม Timer ส่วน Subscriber รับผ่าน Callback ชื่อ Node ต่างกันได้ แต่ Topic และชนิด Message ต้องตรงกัน

## 6. Communication Behavior

| การเปลี่ยนแปลง | ผลที่คาดหวัง |
|---|---|
| หยุด Subscriber | Publisher ยังส่งต่อ |
| เปิด Subscriber ภายหลัง | รับค่าปัจจุบัน อาจไม่เริ่มจากศูนย์ |
| เปลี่ยน Topic ของผู้รับ | ไม่ได้รับข้อมูลจาก Topic เดิม |
| เพิ่ม Subscriber | ผู้รับหลายตัวรับข้อมูลเดียวกันได้ |
| ใช้ Domain ต่างกัน | ไม่สื่อสารกันในตัวอย่างนี้ |

## 7. Robot Motion Commands

Topic **`/cmd_vel`** ใช้รับคำสั่งความเร็ว โดย `cmd` หมายถึง Command และ `vel` หมายถึง Velocity ผู้ส่งใช้ Message ชนิด **`geometry_msgs/msg/Twist`**

```text
ros2 topic pub ── /cmd_vel: Twist ──→ esp32_robot ──→ Motors
   Publisher                           Subscriber
```

| Field | ความหมาย |
|---|---|
| `linear.x` | ความเร็วเดินหน้า หน่วย m/s |
| `angular.z` | ความเร็วในการหมุน หน่วย rad/s |

ตัวอย่าง Message ที่ใช้ `linear.x = 0.1` และ `angular.z = 0.0` หมายถึงเดินหน้าตรงด้วยความเร็วที่ต้องการ `0.1 m/s`

```text
/chatter: "hello 1" ──→ Display text
/cmd_vel: Twist     ──→ Control wheels
```

หลักการส่งข้อมูลเหมือนกัน แต่ชนิด Message และงานของผู้รับต่างกัน

## 8. Data Flow Analysis

การที่โปรแกรมผู้รับทำงานอยู่ไม่ได้ยืนยันว่ามีข้อมูลเข้ามา การสื่อสารต้องมีทั้งผู้ส่ง ช่องทางที่ตรงกัน และผู้รับที่ประมวลผลข้อมูลได้

```text
Publisher ─────── Topic ───────→ Subscriber
    │               │                │
Creates data    Carries data    Processes data
```

| สถานการณ์ | ผลที่เกิดขึ้น | หลักการที่เกี่ยวข้อง |
|---|---|---|
| ผู้ส่งหยุด แต่ผู้รับยังทำงาน | ไม่มีข้อความใหม่ | ผู้รับไม่สร้างข้อมูลแทนผู้ส่ง |
| ทั้งสอง Node ทำงาน แต่ใช้ Topic ต่างกัน | ไม่ได้รับข้อความจากกัน | ชื่อช่องทางต้องตรงกัน |
| เครื่องมือดู Topic รับข้อความได้ แต่โปรแกรมผู้รับไม่แสดงผล | ข้อมูลมาถึง Topic แล้ว | ปัญหาอาจอยู่ที่การเชื่อมต่อหรือประมวลผลของผู้รับ |

การแยกสามส่วนนี้ช่วยอธิบายปัญหาจากเส้นทางข้อมูล แทนการมองระบบทั้งหมดเป็นโปรแกรมเดียว

## Review Questions

1. Node, Topic และ Message ต่างกันอย่างไร?
2. Publisher กับ Subscriber ต้องใช้ข้อมูลใดตรงกัน?
3. การหยุด Subscriber ทำให้ Publisher หยุดด้วยหรือไม่?
4. ข้อความ `/chatter` และคำสั่งมอเตอร์ใช้หลักการสื่อสารเดียวกันอย่างไร?

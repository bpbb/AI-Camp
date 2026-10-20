# 2. Node, topic, publisher, subscriber

บทนี้จะเรียนคำศัพท์พื้นฐานของ ROS 2 ผ่านโปรแกรมตัวอย่างสองตัว
พอเข้าใจบทนี้แล้ว จะเห็นว่าหุ่นยนต์ในบทที่ 4 ก็คือโปรแกรมแบบเดียวกันนี่เอง

## คำศัพท์ 4 คำ

```text
   ┌────────────┐                        ┌────────────┐
   │   talker   │ ─────/chatter─────────>│  listener  │
   └────────────┘                        └────────────┘
      a NODE            a TOPIC              a NODE
   (one program)    (a named channel)     (one program)
```

| คำ | ความหมาย | ในรูปคือ |
|---|---|---|
| **node** | โปรแกรมหนึ่งตัว ทำงานหนึ่งอย่าง | `talker`, `listener` |
| **topic** | ช่องทางส่งข้อมูลที่มีชื่อ | `/chatter` |
| **publisher** | node ที่ **ส่ง** ข้อมูลเข้า topic | `talker` |
| **subscriber** | node ที่ **รับ** ข้อมูลจาก topic | `listener` |

ข้อมูลที่ส่งไปมาเรียกว่า **message**

จุดสำคัญ: **talker กับ listener ไม่รู้จักกันเลย** รู้แค่ว่าใช้ topic ชื่อ `/chatter` เหมือนกัน
เราจึงปิด เปิดใหม่ หรือเปลี่ยนโปรแกรมฝั่งใดฝั่งหนึ่งได้โดยไม่กระทบอีกฝั่ง

## ลองรันโปรแกรม

เปิด terminal 2 อัน

**Terminal 1** รัน listener:

```bash
ros2 run workshop listener
```

listener จะรอเงียบ ๆ จนกว่าจะมี message เข้ามา

**Terminal 2** รัน talker:

```bash
ros2 run workshop talker
```

ดูทั้งสองหน้าต่าง จะเห็นว่า talker ส่งข้อความ และ listener ได้รับข้อความนั้น
ทั้งสองโปรแกรมหากันเจอเอง โดยเราไม่ต้องบอกเลยว่าอีกฝั่งอยู่ที่ไหน

## ตรวจสอบระบบด้วยคำสั่ง ros2

ปล่อยทั้งสองโปรแกรมรันไว้ แล้วเปิด **Terminal 3** เพื่อลองรันคำสั่งต่อไปนี้ทีละคำสั่ง

**ดูว่ามี node อะไรบ้าง**

```bash
ros2 node list
```

ผลลัพธ์ที่ควรเห็น:

```text
/listener
/talker
```

**ดูว่ามี topic อะไรบ้าง**

```bash
ros2 topic list
```

ผลลัพธ์ที่ควรเห็น:

```text
/chatter
/parameter_events
/rosout
```

**ดูข้อมูลที่วิ่งอยู่ใน topic** (กด Ctrl+C เพื่อหยุด)

```bash
ros2 topic echo /chatter
```

คำสั่งนี้จะทำหน้าที่เป็น subscriber อีกตัวหนึ่ง แล้วแสดงทุก message ที่ผ่านเข้ามาให้ดู

**ดูรายละเอียดของ topic**

```bash
ros2 topic info /chatter
```

ผลลัพธ์ที่ควรเห็น:

```text
Type: std_msgs/msg/String
Publisher count: 1
Subscription count: 1
```

ถ้า `ros2 topic echo` ยังเปิดอยู่ `Subscription count` จะเป็น 2 (listener 1 + echo 1)

**ดูว่าส่งเร็วแค่ไหน** (วินาทีละกี่ครั้ง)

```bash
ros2 topic hz /chatter
```

**ดูเป็นภาพ**

```bash
rqt_graph
```

## ส่ง message เองโดยไม่ต้องเขียนโปรแกรม

1. ไปที่ terminal ของ talker แล้วกด Ctrl+C เพื่อหยุด (ปล่อย listener รันต่อไว้)
2. พิมพ์:

```bash
ros2 topic pub /chatter std_msgs/msg/String '{data: "hi from the terminal"}'
```

listener จะได้รับข้อความนี้ โดยไม่รู้เลยว่าข้อความมาจาก terminal ไม่ใช่จาก talker

คำสั่งนี้จะส่งซ้ำวินาทีละครั้ง กด Ctrl+C เพื่อหยุด

## แก้โค้ด talker

เปิดไฟล์ [talker.py](../ros2_ws/src/workshop/workshop/talker.py)
ตอนต้นไฟล์มีค่าที่แก้ได้ 3 ตัว:

```python
TOPIC = 'chatter'
MESSAGE = 'hello'
RATE_HZ = 1.0
```

ทุกครั้งที่แก้ไฟล์ ให้ทำ 3 ขั้นตอนนี้:

1. หยุด talker (Ctrl+C)
2. build ใหม่:

```bash
cd ~/AI-Camp/ros2_ws && colcon build && source install/setup.bash
```

3. รัน talker ใหม่

ลองแก้ทีละข้อ:

1. เปลี่ยน `MESSAGE` เป็นชื่อของคุณ
2. เปลี่ยน `RATE_HZ` เป็น `10.0` แล้วดูความเร็วด้วย `ros2 topic hz /chatter`
3. เปลี่ยน `TOPIC` เป็น `'robot'` **เฉพาะใน talker**
    - listener ยังได้รับข้อความอยู่ไหม?
    - ใช้ `ros2 topic list` หาสาเหตุ
    - แก้ listener ให้ใช้ topic ตรงกัน

    ชื่อ topic ไม่ตรงกันเป็นปัญหาที่เจอบ่อยมากในหุ่นยนต์จริง

## Domain: แยกแต่ละเครื่องไม่ให้ปนกัน

ทุกเครื่องในห้องใช้ WiFi วงเดียวกัน ถ้าไม่แยกกัน node ของทุกเครื่องจะมองเห็นกันหมด
และ listener ของเราจะได้รับข้อความจาก talker ของทุกเครื่อง

วิธีแยกคือ **domain** (ตัวเลขประจำกลุ่ม) node ที่อยู่คนละ domain จะมองไม่เห็นกัน
แต่ละเครื่องใช้เลขที่ไม่ซ้ำกันในช่วง 1 ถึง 101 **ใช้หมายเลขเครื่องคอมพิวเตอร์ที่ใช้อยู่**

### เลขเครื่องของคุณ

เลขเครื่องตั้งไว้ใน `~/.bashrc` แล้วตั้งแต่บทที่ 1 พร้อมกับ `source`
(ถ้ายังไม่ได้ตั้ง ให้กลับไปทำหัวข้อ "ตั้งค่าใน `~/.bashrc` ครั้งเดียว" ในบทที่ 1)

เช็กค่า:

```bash
echo $ROS_DOMAIN_ID
```

ผลลัพธ์ที่ควรเห็น (ตัวอย่างของเครื่องที่ 7 ตัวเลขจะต่างกันตามเครื่อง):

```text
7
```

### ทดลอง: คนละ domain มองไม่เห็นกัน

ปล่อย talker และ listener รันไว้ แล้วเปิด terminal ใหม่และพิมพ์:

```bash
export ROS_DOMAIN_ID=99
ros2 node list
```

ผลลัพธ์ที่ควรเห็น: ไม่มีอะไรขึ้นเลย เพราะ terminal นี้อยู่ใน domain 99 ส่วน talker/listener อยู่ใน domain ของเครื่องเรา

ปิด terminal นี้ทิ้งได้เลย (`export` ที่พิมพ์เองมีผลเฉพาะใน terminal นั้น)

### ทดลอง: คุยกับเครื่องข้าง ๆ

node ที่อยู่ **domain เดียวกัน** คุยกันได้ แม้จะอยู่คนละเครื่อง
ลองจับคู่กับเครื่องข้าง ๆ แล้วตกลงกันว่าจะใช้ domain ของเครื่องใด เช่น ใช้เลขเครื่องของเพื่อน

ใส่ `ROS_DOMAIN_ID=...` ไว้หน้าคำสั่ง จะเปลี่ยน domain **เฉพาะคำสั่งนั้น** โดยไม่แก้ `~/.bashrc`

**เครื่องเรา** รัน talker ใน domain ของเพื่อน (แทน `<เลขเครื่องเพื่อน>` ด้วยตัวเลข เช่น `8`):

```bash
ROS_DOMAIN_ID=<เลขเครื่องเพื่อน> ros2 run workshop talker
```

**เครื่องเพื่อน** รัน listener ตามปกติ (อยู่ใน domain ของตัวเองอยู่แล้ว):

```bash
ros2 run workshop listener
```

ผลลัพธ์ที่ควรเห็น: listener บนเครื่องเพื่อนได้รับข้อความ `hello ...` จากเครื่องเรา

กด **Ctrl+C** เพื่อหยุด เมื่อรันคำสั่งถัดไปโดยไม่ใส่ `ROS_DOMAIN_ID=...` นำหน้า
จะกลับมาใช้ domain ของเครื่องเราตามเดิม

> ถ้าไม่ได้รับข้อความ: เช็กว่าทั้งสองเครื่องต่อ WiFi วงเดียวกัน และใส่เลข domain ตรงกัน

## แบบฝึกหัดเพิ่มเติม (ไม่บังคับ)

ส่วนนี้ไม่บังคับ ทำเพิ่มได้เมื่อทำบทหลักเสร็จแล้ว

1. node กับ topic ต่างกันอย่างไร
2. ถ้า listener ไม่ได้รันอยู่ talker จะเป็นอย่างไร
3. ทำไมแต่ละเครื่องต้องใช้ `ROS_DOMAIN_ID` ไม่ซ้ำกัน

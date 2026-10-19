# 2. Node, topic, publisher, subscriber

บทนี้เรียนคำศัพท์พื้นฐานของ ROS 2 ด้วยโปรแกรมตัวอย่างสองตัว
พอเข้าใจบทนี้ จะเห็นว่าหุ่นยนต์ในบทที่ 5 ก็คือโปรแกรมแบบเดียวกันนี่เอง

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
เราจึงปิด เปิดใหม่ หรือเปลี่ยนโปรแกรมฝั่งหนึ่งได้ โดยไม่กระทบอีกฝั่ง

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

ดูทั้งสองหน้าต่าง: talker ส่งข้อความ listener ได้รับ
ทั้งสองหากันเจอเอง เราไม่ต้องบอกเลยว่าอีกฝั่งอยู่ที่ไหน

## ส่องดูระบบ

ปล่อยทั้งสองโปรแกรมรันไว้ แล้วเปิด **Terminal 3** ลองคำสั่งต่อไปนี้ทีละคำสั่ง

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

**ดูข้อมูลที่วิ่งอยู่ใน topic** (คำสั่งที่ใช้บ่อยที่สุด กด Ctrl+C เพื่อหยุด)

```bash
ros2 topic echo /chatter
```

คำสั่งนี้ทำตัวเป็น subscriber อีกตัว แล้วพิมพ์ทุก message ที่ผ่านมาให้ดู

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

1. ไปที่ terminal ของ talker กด Ctrl+C เพื่อหยุด (ให้ listener รันต่อ)
2. พิมพ์:

```bash
ros2 topic pub /chatter std_msgs/msg/String '{data: "hi from the terminal"}'
```

listener จะได้รับข้อความนี้ และไม่รู้เลยว่ามาจาก terminal ไม่ใช่จาก talker

คำสั่งนี้ส่งซ้ำวินาทีละครั้ง กด Ctrl+C เพื่อหยุด

## แก้โค้ด talker

เปิดไฟล์ [talker.py](../ros2_ws/src/workshop/workshop/talker.py)
ตอนต้นไฟล์มีค่า 3 ตัวที่แก้ได้:

```python
TOPIC = 'chatter'
MESSAGE = 'hello'
RATE_HZ = 1.0
```

ทุกครั้งที่แก้ ให้ทำ 3 อย่างนี้:

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
    - listener ยังได้ข้อความไหม?
    - ใช้ `ros2 topic list` หาสาเหตุ
    - แก้ listener ให้ใช้ topic ตรงกัน

    ชื่อ topic ไม่ตรงกัน เป็นปัญหาที่เจอบ่อยมากกับหุ่นยนต์จริง

## Domain: แยกทีมไม่ให้ปนกัน

ทุกเครื่องในห้องใช้ WiFi เดียวกัน ถ้าไม่แยก node ของทุกทีมจะเห็นกันหมด
listener ของเราจะได้ข้อความจาก talker ของทุกทีม

วิธีแยกคือ **domain** (ตัวเลขประจำกลุ่ม) node ที่อยู่คนละ domain จะมองไม่เห็นกัน
แต่ละทีมใช้เลขไม่ซ้ำกัน ระหว่าง 1 ถึง 101 **ใช้เลขทีมที่ได้รับจากผู้สอน**

### ตั้งเลขทีม

1. เปลี่ยน `7` ในบรรทัดแรกเป็นเลขทีมของคุณ
2. รันทั้งก้อน:

```bash
TEAM=7
sed -i -e '/^export ROS_DOMAIN_ID=/d' -e '/^export ROBOT_ID=/d' ~/.bashrc
echo "export ROS_DOMAIN_ID=$TEAM" >> ~/.bashrc
echo "export ROBOT_ID=robot$TEAM" >> ~/.bashrc
```

คำสั่งนี้ตั้งค่า 2 ตัวไว้ใน `~/.bashrc` (ลบค่าเก่าก่อน รันซ้ำได้ไม่ซ้ำซ้อน):

- `ROS_DOMAIN_ID` เลข domain ของทีม (ใช้บทนี้และบทที่ 5)
- `ROBOT_ID` ชื่อหุ่นของทีม เช่น `robot7` (ใช้บทที่ 5-7)

3. **ปิด terminal แล้วเปิดใหม่** แล้วตรวจ:

```bash
echo $ROS_DOMAIN_ID
echo $ROBOT_ID
```

ผลลัพธ์ที่ควรเห็น (ถ้าเลขทีมคือ 7):

```text
7
robot7
```

**จดเลขทีมไว้** บทที่ 5 ต้องใช้เลขเดียวกันนี้กับหุ่นยนต์

### ทดลอง: คนละ domain มองไม่เห็นกัน

ให้ talker และ listener รันอยู่ แล้วเปิด terminal ใหม่ พิมพ์:

```bash
export ROS_DOMAIN_ID=99
ros2 node list
```

ผลลัพธ์ที่ควรเห็น: ไม่มีอะไรขึ้นเลย เพราะ terminal นี้อยู่ domain 99 ส่วน talker/listener อยู่ domain ของทีม

ปิด terminal นี้ทิ้งได้เลย (`export` ที่พิมพ์เองมีผลแค่ใน terminal นั้น)

## ลองคิดเองภายหลัง

ส่วนนี้ไม่บังคับ สามารถลองทำเองได้ในภายหลัง

1. node กับ topic ต่างกันอย่างไร
2. ถ้า listener ไม่ได้รันอยู่ talker จะเป็นอย่างไร
3. ทำไมแต่ละทีมต้องใช้ `ROS_DOMAIN_ID` ไม่ซ้ำกัน

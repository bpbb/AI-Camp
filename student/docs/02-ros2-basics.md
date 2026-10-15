# 2. Node, topic, publisher, subscriber

บทนี้ยังไม่ใช้หุ่นยนต์ ไม่มีอะไรให้พัง ไม่มีอะไรต้องเสียบสาย เราจะมาเรียน
คำศัพท์กันก่อน เพราะพอเข้าใจคำพวกนี้แล้ว หุ่นยนต์ก็เป็นแค่ node
อีกตัวหนึ่งเท่านั้นเอง

## ไอเดียทั้งหมดในภาพเดียว

```
   ┌────────────┐                        ┌────────────┐
   │   talker   │ ─────/chatter─────────>│  listener  │
   └────────────┘                        └────────────┘
      a NODE            a TOPIC              a NODE
   (one program)    (a named channel)     (one program)
```

- **node** คือโปรแกรมหนึ่งตัวที่ทำงานหนึ่งอย่าง
- **topic** คือช่องทางที่มีชื่อ ใช้ส่ง message ไปมา
- node ที่ส่งข้อมูลออกไปบน topic เรียกว่า **publisher**
- node ที่รับข้อมูลจาก topic เรียกว่า **subscriber**

กฎที่สำคัญที่สุด: **talker กับ listener ไม่เคยรู้จักกันเลย** ทั้งคู่แค่ตกลง
ใช้ชื่อ `/chatter` ร่วมกันเท่านั้น ตัวไหนจะถูก restart, ถูกเปลี่ยนตัว
หรือถูกเขียนใหม่ด้วยภาษาอื่น อีกตัวก็จะไม่รู้สึกอะไรเลย

## ลองรัน

Terminal 1:

```bash
ros2 run workshop listener
```

มันจะบอกว่ากำลังฟังอยู่ แล้วก็เงียบไป มันกำลังรออยู่

Terminal 2:

```bash
ros2 run workshop talker
```

ทีนี้ดูทั้งสองหน้าต่าง พวกมันหากันเจอเองโดยไม่ต้องใส่ address ไม่ต้อง
ตั้งค่าอะไรเลย คุณแค่บอกชื่อ topic ให้มันเท่านั้น

## ดูสิ่งที่คุณสร้างขึ้นมา

ปล่อยให้ทั้งสองตัวรันค้างไว้ แล้วเปิด terminal ที่สาม:

```bash
ros2 node list
```
```
/listener
/talker
```

```bash
ros2 topic list
```
```
/chatter
/parameter_events
/rosout
```

```bash
ros2 topic echo /chatter
```

นี่คือคำสั่งที่มีประโยชน์ที่สุดใน ROS 2 มันจะ subscribe topic แล้วพิมพ์
ทุกอย่างที่วิ่งผ่านออกมา คุณเพิ่งเพิ่ม subscriber ตัวที่สามเข้าไป
โดยไม่ต้องแตะโค้ดเลยสักบรรทัด

```bash
ros2 topic info /chatter
```
```
Type: std_msgs/msg/String
Publisher count: 1
Subscription count: 2      <-- listener, and your echo
```

```bash
ros2 topic hz /chatter      # วินาทีละกี่ message
rqt_graph                   # วาดภาพให้ดู
```

## Publish โดยไม่ต้องเขียนโปรแกรม

หยุด talker (Ctrl+C) แล้วปล่อย listener รันไว้ จากนั้น:

```bash
ros2 topic pub /chatter std_msgs/msg/String '{data: "hi from the terminal"}'
```

listener ได้ยินคุณ มันแยกไม่ออกเลยว่าข้อความมาจาก terminal ของคุณ
หรือมาจาก talker ตัวจริง -- และนั่นแหละคือประเด็นทั้งหมด

## ทีนี้ลองแก้โค้ด

เปิด [talker.py](../ros2_ws/src/workshop/workshop/talker.py) ใกล้ ๆ
ด้านบนจะมี:

```python
TOPIC = 'chatter'
MESSAGE = 'hello'
RATE_HZ = 1.0
```

ลองทำทีละข้อ และ build ใหม่ทุกครั้ง:

```bash
cd ~/AI-Camp/ros2_ws && colcon build && source install/setup.bash
```

1. เปลี่ยน `MESSAGE` เป็นชื่อของคุณ
2. เปลี่ยน `RATE_HZ` เป็น `10.0` แล้วเช็คด้วย `ros2 topic hz /chatter`
3. เปลี่ยน `TOPIC` เป็น `'robot'` ใน talker **แต่ไม่เปลี่ยน**ใน listener
   ทั้งคู่จะไม่ได้ยินกันอีกต่อไป แก้โดยเปลี่ยนใน listener ด้วย
   **นี่คือความผิดพลาดที่คุณจะเจอแน่ ๆ กับหุ่นยนต์จริง** เพราะฉะนั้น
   ลองพลาดที่นี่ก่อน

## Workshop: คุยกับโต๊ะข้าง ๆ

คอมสองเครื่องต่อ WiFi เดียวกัน เครื่องหนึ่งรัน talker อีกเครื่องรัน
listener -- แล้วมันก็ใช้ได้เลย ข้ามเครื่องกันได้โดยไม่ต้องตั้งค่าอะไรเลย

แต่พอทุกคนทำพร้อมกัน มันก็เริ่มไม่สนุกแล้ว: talker ยี่สิบตัว
publish ไปที่ `/chatter` หมด และ listener ทุกตัวก็ได้ยินทุกตัว

ทางแก้คือ **domain** ซึ่งเป็นตัวเลขที่ใช้แยกกลุ่มออกจากกัน:

```bash
export ROS_DOMAIN_ID=7
```

เลือกเลขหนึ่งตัวต่อทีม ตั้งแต่ 1 ถึง 101 node ที่อยู่คนละ domain จะมองไม่เห็น
กันเลย -- `ros2 node list` ก็จะไม่แสดงด้วยซ้ำ

เหมือนกับบรรทัด `source` ในบทที่ 1 ค่านี้อยู่ได้แค่ใน terminal เดียว
ให้ใส่ไว้ใน `~/.bashrc` เพื่อให้ทุก terminal ที่เปิดใหม่ได้ค่านี้ด้วย (ใช้เลขของทีมคุณเอง):

```bash
grep ROS_DOMAIN_ID ~/.bashrc        # มีอยู่แล้วหนึ่งบรรทัด? ให้แก้บรรทัดนั้นแทน
echo "export ROS_DOMAIN_ID=7" >> ~/.bashrc
```

เปิด terminal **ใหม่** แล้วเช็ค:

```bash
echo $ROS_DOMAIN_ID                 # ควรพิมพ์เลขของคุณออกมา
```

ถ้า `grep` เจอบรรทัดเก่า เช่นจากโปรเจกต์อื่น ให้เปิด `~/.bashrc`
ใน VS Code แล้วแก้เลขในบรรทัดนั้นแทนที่จะเพิ่มบรรทัดที่สอง
มีสองบรรทัดก็ใช้ได้ แต่บรรทัดสุดท้ายจะชนะ และคุณจะลืมว่าบรรทัดไหน

จดเลขของทีมไว้ **คุณจะต้องใช้เลขเดียวกันนี้บนหุ่นยนต์ในบทที่ 5**

## สิ่งที่คุณควรตอบได้

1. node กับ topic ต่างกันอย่างไร?
2. ถ้า listener ไม่ได้รันอยู่ talker จะทำอะไร?
3. node สองตัว publish ไปที่ `/chatter` ทั้งคู่ ใครได้รับอะไรบ้าง?
4. คุณเปลี่ยน `TOPIC` แค่ในไฟล์เดียว จะเกิดอะไรขึ้น และคุณจะใช้
   `ros2 topic list` หาสาเหตุได้อย่างไร?
5. ทำไมแต่ละทีมต้องใช้ `ROS_DOMAIN_ID` คนละเลข?

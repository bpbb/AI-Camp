# Lecture 2: Terminal and ROS 2 CLI

**Camp:** NextGen AI Camp 2026

## Learning Objectives

- อ่านคำสั่งและระบุตำแหน่งทำงานของ Shell
- อธิบายหน้าที่ของ Environment, Workspace และ Domain
- เลือกเครื่องมือ CLI ให้ตรงกับข้อมูลที่ต้องการตรวจสอบ

## 1. Terminal and Shell

### Graphical and Command Line Interfaces

การสั่งงานคอมพิวเตอร์ทำได้ทั้งผ่านหน้าต่างและการพิมพ์คำสั่ง ทั้งสองวิธีใช้เปิดโปรแกรมและจัดการไฟล์ได้ แต่มีวิธีระบุงานต่างกัน

| Interface | วิธีสั่งงาน | ตัวอย่าง |
|---|---|---|
| Graphical User Interface (GUI) | เลือกเมนู ปุ่ม หรือไอคอน | เปิดโฟลเดอร์เพื่อดูไฟล์ |
| Command Line Interface (CLI) | พิมพ์ชื่อคำสั่งและค่าที่ต้องการ | ใช้ `ls docs` เพื่อดูรายการไฟล์ใน `docs` |

CLI ระบุงานเป็นข้อความ จึงนำคำสั่งเดิมกลับมาใช้ เปลี่ยนค่าบางส่วน หรือรวมหลายคำสั่งเป็น Script ได้

### CLI in Robotics

ระบบหุ่นยนต์มีหลายโปรแกรมทำงานพร้อมกัน บางโปรแกรมไม่มีหน้าต่างของตัวเอง เช่น โปรแกรมรับ Sensor หรือส่ง Message การใช้ CLI ช่วยเปิดโปรแกรมและดูข้อมูลของแต่ละส่วนได้โดยตรง

```text
                         ROS 2 CLI
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
      Run a node        Inspect topics     Read messages
```

| ประโยชน์ | ตัวอย่างใน ROS 2 |
|---|---|
| สั่งงานได้ชัดเจน | ระบุชื่อ Package และ Node ที่ต้องการรัน |
| ทำซ้ำได้ง่าย | ใช้คำสั่งเดิมกับ Topic หรือค่าความเร็วที่เปลี่ยนไป |
| ตรวจข้อมูลได้โดยตรง | ดู Message ที่หุ่นยนต์ส่งโดยไม่ต้องเขียนหน้าจอเพิ่ม |
| อ่านสาเหตุของปัญหาได้ | ดู Output และ Error จากโปรแกรม |

ตัวอย่าง `ros2 topic echo /heartbeat` แสดงข้อมูลที่หุ่นยนต์ส่งมา ส่วน `ros2 topic echo /cmd_vel` แสดงคำสั่งความเร็ว โครงสร้างคำสั่งเหมือนกัน แต่เลือกข้อมูลคนละช่องทาง

### Terminal and Shell Roles

**Terminal** เป็นหน้าต่างสำหรับพิมพ์คำสั่งและอ่านข้อความตอบกลับ ส่วน **Shell** เป็นโปรแกรมที่ตีความคำสั่งแล้วดำเนินงาน ในบทนี้ใช้ Bash เป็น Shell

```text
┌───────────────────────────────────────────────────┐
│ Terminal                                          │
│                                                   │
│ Command input → Shell → Execute → Output           │
│                   │                               │
│                   └── Current directory           │
│                       Environment settings        │
└───────────────────────────────────────────────────┘
```

เมื่อพิมพ์ `ls docs` Shell จะเรียกโปรแกรม `ls` ให้แสดงรายการใน `docs` แล้ว Terminal จะแสดงผล ส่วน `cd docs` เป็นคำสั่งที่ Shell ใช้เปลี่ยนตำแหน่งทำงานของตัวเอง

Terminal จึงเป็นช่องทางติดต่อกับ Shell ขณะที่ Shell จัดการคำสั่ง ตำแหน่งทำงาน และค่าตั้งที่โปรแกรมต้องใช้

### Command Structure

```text
ls       -l       docs
│        │        │
Command  Option   Argument
```

`ls` ระบุงานแสดงรายการ `-l` เพิ่มรายละเอียด และ `docs` ระบุโฟลเดอร์เป้าหมาย การอ่านคำสั่งจึงเริ่มจากงานที่ต้องการ ตามด้วยตัวเลือกและข้อมูลที่ใช้กับงานนั้น

## 2. Directories and Paths

Shell ทำงานอยู่ในโฟลเดอร์หนึ่ง เรียกว่า Current working directory ส่วน Path ระบุตำแหน่งไฟล์หรือโฟลเดอร์

```text
AI-Camp/
└── student/             ← Project directory
    ├── docs/
    ├── firmware/
    └── ros2_ws/
```

เมื่ออยู่ที่ `student` คำสั่ง `cd docs` จะเข้าโฟลเดอร์ `docs` ด้านใน เมื่ออยู่ที่อื่น ชื่อ `docs` อาจอ้างถึงคนละตำแหน่ง

| Command / Symbol | ความหมาย |
|---|---|
| `pwd` | แสดงตำแหน่งปัจจุบัน |
| `ls` | แสดงรายการไฟล์และโฟลเดอร์ |
| `cd docs` | เข้าโฟลเดอร์ `docs` |
| `cd ..` | กลับขึ้นหนึ่งระดับ |
| `cat filename` | แสดงเนื้อหาไฟล์ |
| `~` | Home directory ของผู้ใช้ |

```text
student ── cd docs ──→ docs
student ←── cd .. ─── docs
```

ชื่อไฟล์แยกตัวพิมพ์ใหญ่และเล็ก เช่น `docs` กับ `Docs` เป็นคนละชื่อ

## 3. Program Execution

Prompt แสดงว่า Shell พร้อมรับคำสั่ง เช่น `student@camp-pc:~$` โปรแกรมบางชนิดคืน Prompt ทันที ขณะที่ Node มักทำงานต่อเพื่อรอข้อมูล

```text
ls:          Start → Show files → Finish
ROS 2 node:  Start → Wait → Receive / Process → Wait → ...
```

การไม่เห็น Prompt ไม่ได้แปลว่าโปรแกรมค้างเสมอไป **Ctrl+C** ใช้ขอหยุดโปรแกรมที่กำลังทำงาน

### Terminal Shortcuts

| Shortcut | หน้าที่ |
|---|---|
| Ctrl+Alt+T | เปิด Ubuntu Terminal |
| Ctrl+Shift+T | เปิด Tab ใหม่ |
| Tab | เติมชื่อคำสั่งหรือ Path |
| ↑ / ↓ | เลือกคำสั่งที่เคยใช้ |

## 4. Multiple Terminal Sessions

โปรแกรมหลายส่วนทำงานพร้อมกันได้ แต่ละ Terminal มี Shell ตำแหน่งทำงาน และ Environment แยกกัน

```text
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Terminal 1     │  │ Terminal 2     │  │ Terminal 3     │
│ Publisher      │  │ Subscriber     │  │ Inspect data   │
└────────────────┘  └────────────────┘  └────────────────┘
```

การเปลี่ยนโฟลเดอร์หรือค่าตั้งใน Terminal หนึ่งไม่เปลี่ยนอีก Terminal ที่เปิดอยู่แล้ว

## 5. Environment and Workspace

Environment ช่วยให้ Shell ค้นหาเครื่องมือและ Library ได้ ส่วน Workspace เก็บ Package ของโปรเจกต์ เช่น `workshop` และ `teleop`

```text
Source ROS 2 setup ──→ Find ROS 2 tools
Source workspace  ──→ Find workshop / teleop packages
```

`source` โหลดค่าตั้ง ส่วน `colcon build` เตรียมโค้ดของ Workspace ให้ใช้งานได้ ทั้งสองคำสั่งทำหน้าที่ต่างกัน

```text
Edit source code → Build → Load workspace → Run node
```

ตัวอย่าง `source /opt/ros/jazzy/setup.bash` ทำให้ Shell ค้นหาเครื่องมือ ROS 2 ได้ การติดตั้งโปรแกรมกับการโหลด Environment จึงเป็นคนละขั้นตอน

## 6. ROS Domain Identification

`ROS_DOMAIN_ID` แยก ROS 2 Graph ของแต่ละทีม โปรแกรมที่ต้องสื่อสารกันต้องใช้ Domain เดียวกัน

```text
Domain 7                         Domain 8
Computer ↔ Agent ↔ Robot         Computer ↔ Agent ↔ Robot
```

ตัวอย่าง `export ROS_DOMAIN_ID=7` เลือก Domain ให้ Shell ปัจจุบัน ค่าใน Terminal ของ Agent และ Firmware ต้องตรงกัน

## 7. ROS 2 Inspection

คำสั่งตรวจสอบช่วยตอบคำถามคนละระดับ:

| ข้อมูลที่ต้องการ | Command |
|---|---|
| โปรแกรมใดทำงานอยู่ | `ros2 node list` |
| Node ส่งและรับอะไร | `ros2 node info /esp32_robot` |
| มีช่องทางข้อมูลใด | `ros2 topic list -t` |
| Topic มีผู้ส่งและผู้รับกี่ตัว | `ros2 topic info /heartbeat` |
| ข้อมูลมีค่าอะไร | `ros2 topic echo /heartbeat` |
| ส่งบ่อยเท่าไร | `ros2 topic hz /heartbeat` |
| เชื่อมกันอย่างไร | `rqt_graph` |

```text
Node exists? → Topic exists? → Message arrives?
  node list     topic list       topic echo
```

## Review Questions

1. `pwd`, `ls` และ `cd` ให้ข้อมูลหรือเปลี่ยนสถานะต่างกันอย่างไร?
2. Build กับ `source` ทำหน้าที่ต่างกันอย่างไร?
3. หากต้องการรู้ว่าหุ่นยนต์ส่งข้อมูลหรือไม่ ควรเลือกคำสั่งใด?

// ============================================================
//  Differential drive: แปลงคำสั่ง "เดินหน้า / เลี้ยว"
//  เป็นความเร็วของมอเตอร์สองตัว
//
//  เดินตรง: สองล้อหมุนทิศเดียวกันด้วยความเร็วเท่ากัน
//  เลี้ยว: ล้อหนึ่งหมุนเร็วกว่าอีกล้อ
// ============================================================
#pragma once
#include <Arduino.h>

// ---- การต่อสาย motor driver (L298N / TB6612) ----
// ห้ามใช้ GPIO 0, 2, 12, 15: ESP32 อ่านขาเหล่านี้ตอน boot
// ถ้า motor driver ดึงขาไว้ บอร์ดอาจ boot ไม่ขึ้น
// สลับ IN1/IN2 และ IN3/IN4 ไว้ให้ "เดินหน้า" ตรงกับการติดตั้งมอเตอร์
// ถ้าล้อใดหมุนกลับทิศ ให้สลับเฉพาะคู่ของล้อนั้น
#define L_IN1 26   // IN2
#define L_IN2 27   // IN1
#define L_PWM 14   // ENA
#define R_IN1 33   // IN4
#define R_IN2 25   // IN3
#define R_PWM 32   // ENB

#define PWM_FREQ 20000   // 20 kHz: สูงเกินหูได้ยิน มอเตอร์จึงไม่มีเสียงหวีด
#define PWM_RES  8       // ความละเอียด 8-bit -> duty 0..255
#define L_CH 0
#define R_CH 1

// ---- ขนาดหุ่นและขีดจำกัด ----
#define WHEEL_BASE 0.15f  // ระยะห่างระหว่างสองล้อ (เมตร) วัดของหุ่นตัวเอง
#define MAX_LIN    0.30f  // m/s ที่ความเร็วสูงสุด ค่าประมาณก็พอ
#define MIN_DUTY   60     // ต่ำกว่านี้มอเตอร์มีเสียงแต่ไม่หมุน
                          // ปรับค่านี้: ลดลงจนคำสั่งเบา ๆ ยังขยับหุ่นได้
                          // เพิ่มขึ้นถ้ามอเตอร์มีเสียงแต่ไม่หมุน

// ฟังก์ชัน PWM ของ ESP32 เปลี่ยนชื่อใน Arduino core 3.x
// ส่วนนี้ทำให้ build ได้ทั้งสองเวอร์ชัน
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  #define PWM_SETUP(pin, ch) ledcAttach(pin, PWM_FREQ, PWM_RES)
  #define PWM_WRITE(pin, ch, duty) ledcWrite(pin, duty)
#else
  #define PWM_SETUP(pin, ch) do { ledcSetup(ch, PWM_FREQ, PWM_RES); \
                                  ledcAttachPin(pin, ch); } while (0)
  #define PWM_WRITE(pin, ch, duty) ledcWrite(ch, duty)
#endif

inline void motorSetup() {
  pinMode(L_IN1, OUTPUT); pinMode(L_IN2, OUTPUT);
  pinMode(R_IN1, OUTPUT); pinMode(R_IN2, OUTPUT);
  PWM_SETUP(L_PWM, L_CH);
  PWM_SETUP(R_PWM, R_CH);
}

// ขับมอเตอร์หนึ่งตัว speed อยู่ในช่วง -1.0 (ถอยสุด) .. +1.0 (เดินหน้าสุด)
inline void setMotor(int in1, int in2, int pwmPin, int ch, float speed) {
  bool forward = speed >= 0;
  digitalWrite(in1, forward ? HIGH : LOW);
  digitalWrite(in2, forward ? LOW : HIGH);

  float mag = fabsf(speed);
  int duty;

  if (mag < 0.01f) {
    duty = 0;                 // สั่งให้หยุดจริง
  } else {
    // มอเตอร์ต้องได้แรงขั้นต่ำจึงจะเริ่มหมุน จึงย่อช่วง 0..1
    // ให้อยู่ในช่วง MIN_DUTY..255 เพื่อให้คำสั่งเบา ๆ ยังขยับหุ่นได้
    duty = (int)(MIN_DUTY + mag * (255.0f - MIN_DUTY));
  }

  if (duty > 255) duty = 255;
  PWM_WRITE(pwmPin, ch, duty);
}

// ============================================================
//  ฟังก์ชันสำคัญ
//
//  lin = ความเร็วเดินหน้า หน่วย m/s   (ค่าลบ = ถอยหลัง)
//  ang = ความเร็วเลี้ยว หน่วย rad/s  (ค่าบวก = เลี้ยวซ้าย)
//
//  ตรงกับข้อมูลใน ROS 2 Twist message ทุกโปรแกรมในโปรเจกต์
//  (motor test, micro-ROS, MQTT) จึงเรียกใช้ฟังก์ชันนี้
// ============================================================
inline void drive(float lin, float ang) {
  // TODO(student) 1/4 -- บทที่ 4: แปลง (lin, ang) เป็นความเร็วสองล้อ
  //   เดินตรง: ทั้งสองล้อใช้ความเร็ว lin
  //   เลี้ยวซ้าย (ang > 0): ล้อขวาเร็วขึ้นและล้อซ้ายช้าลง
  //   ล้อละ ang * WHEEL_BASE / 2
  //   ตรวจคำตอบด้วย WHEEL_BASE 0.15:
  //     lin=0.1, ang=0  ->  left= 0.10, right=0.10   (เดินตรง)
  //     lin=0,   ang=2  ->  left=-0.15, right=0.15   (หมุนซ้ายอยู่กับที่)
  float left  = 0.0f;   // <- ใส่สูตรตรงนี้
  float right = 0.0f;   // <- ใส่สูตรตรงนี้

  // ถ้าสั่งเกินที่มอเตอร์ทำได้ ให้ลดทั้งสองล้อด้วยอัตราส่วนเดียวกัน
  // ถ้าตัดแยกกัน หุ่นจะวิ่งผิดเส้นทาง
  float biggest = fmaxf(fabsf(left), fabsf(right));
  if (biggest > MAX_LIN) {
    left  = left  / biggest * MAX_LIN;
    right = right / biggest * MAX_LIN;
  }

  setMotor(L_IN1, L_IN2, L_PWM, L_CH, left  / MAX_LIN);
  setMotor(R_IN1, R_IN2, R_PWM, R_CH, right / MAX_LIN);
}

inline void stopMotors() { drive(0.0f, 0.0f); }

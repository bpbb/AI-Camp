// ============================================================
//  บทที่ 4 -- ทดสอบ hardware
//
//  ไม่มี WiFi, broker หรือ ROS 2 ทดสอบเฉพาะมอเตอร์
//  หาข้อผิดพลาดการต่อสายตอนนี้ ก่อนบทถัดไปเพิ่มระบบเครือข่าย
//  ซึ่งทำให้หาสาเหตุได้ยากขึ้นมาก
//
//  วางหุ่นบนหนังสือให้ล้อลอยจากพื้น ไม่เช่นนั้นหุ่นจะวิ่งตกโต๊ะ
// ============================================================
#include <Arduino.h>

#include "config.h"
#include "motor.h"

// แต่ละขั้น: ชื่อ, การเคลื่อนที่ และระยะเวลา
struct Step {
  const char *label;
  float lin;     // m/s เดินหน้า
  float ang;     // rad/s เลี้ยว
  int ms;
};

const Step STEPS[] = {
  // เลี้ยวพอดีให้ล้อหนึ่งความเร็วเป็นศูนย์ เพื่อตรวจทีละล้อ
  // ang ค่าบวก = เลี้ยวซ้าย ล้อที่หมุนคือล้อขวา
  {"LEFT wheel forward   (right should be still)",  0.10f, -1.333f, 2000},
  {"LEFT wheel backward",                          -0.10f,  1.333f, 2000},
  {"RIGHT wheel forward  (left should be still)",   0.10f,  1.333f, 2000},
  {"RIGHT wheel backward",                         -0.10f, -1.333f, 2000},
  {"both forward",                                  0.20f,  0.0f,   2000},
  {"both backward",                                -0.20f,  0.0f,   2000},
  {"spin left",                                     0.0f,   2.0f,   2000},
  {"spin right",                                    0.0f,  -2.0f,   2000},
  {"stop",                                          0.0f,   0.0f,   2000},
};

const int STEP_COUNT = sizeof(STEPS) / sizeof(STEPS[0]);

void setup() {
  Serial.begin(115200);
  delay(1000);

  motorSetup();
  stopMotors();

  Serial.println();
  Serial.println("motor test -- put the robot on a book, wheels in the air");
  Serial.println("watch each step and check it does what it says");
  Serial.println();
}

void loop() {
  for (int i = 0; i < STEP_COUNT; i++) {
    Serial.printf("[%d/%d] %s\n", i + 1, STEP_COUNT, STEPS[i].label);
    drive(STEPS[i].lin, STEPS[i].ang);
    delay(STEPS[i].ms);
  }

  stopMotors();
  Serial.println("--- done, starting again in 3s ---\n");
  delay(3000);
}

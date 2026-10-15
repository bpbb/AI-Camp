// ============================================================
//  Differential drive: turning "go forward / turn left" into
//  two motor speeds.
//
//  You have two wheels. To go straight, both spin the same way
//  at the same speed. To turn, one spins faster than the other.
//  That is the whole idea.
// ============================================================
#pragma once
#include <Arduino.h>

// ---- Motor driver wiring (L298N / TB6612) ----
// Avoid GPIO 0, 2, 12 and 15: the ESP32 reads those at boot to
// decide how to start up, and a motor driver pulling on them can
// stop the board from booting at all.
// IN1/IN2 and IN3/IN4 are swapped here so "forward" matches how the
// motors are mounted. If one wheel runs backwards, swap just its pair.
#define L_IN1 26   // IN2
#define L_IN2 27   // IN1
#define L_PWM 14   // ENA
#define R_IN1 33   // IN4
#define R_IN2 25   // IN3
#define R_PWM 32   // ENB

#define PWM_FREQ 20000   // 20 kHz: above hearing, so the motors don't whine
#define PWM_RES  8       // 8-bit resolution -> duty is 0..255
#define L_CH 0
#define R_CH 1

// ---- Robot shape and limits ----
#define WHEEL_BASE 0.15f  // metres between the two wheels. MEASURE YOURS.
#define MAX_LIN    0.30f  // m/s at full throttle. A rough guess is fine.
#define MIN_DUTY   60     // below this the motors buzz but don't turn
                          // TUNE THIS: lower it until a gentle command
                          // still moves the robot, raise it if the
                          // motors whine without turning.

// The ESP32 PWM functions were renamed in Arduino core 3.x. This keeps
// the sketch building on either version.
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

// Drive one motor. speed is -1.0 (full reverse) .. +1.0 (full forward).
inline void setMotor(int in1, int in2, int pwmPin, int ch, float speed) {
  bool forward = speed >= 0;
  digitalWrite(in1, forward ? HIGH : LOW);
  digitalWrite(in2, forward ? LOW : HIGH);

  float mag = fabsf(speed);
  int duty;

  if (mag < 0.01f) {
    duty = 0;                 // actually asked to stop
  } else {
    // A motor needs a minimum push before it turns at all. If we just
    // cut off everything below MIN_DUTY, small requests would do
    // nothing and the robot would feel broken. Instead, squeeze the
    // whole 0..1 range into the part of the scale that actually works.
    duty = (int)(MIN_DUTY + mag * (255.0f - MIN_DUTY));
  }

  if (duty > 255) duty = 255;
  PWM_WRITE(pwmPin, ch, duty);
}

// ============================================================
//  THE IMPORTANT FUNCTION
//
//  lin = how fast forward, in m/s   (negative = backwards)
//  ang = how fast turning, in rad/s (positive = turn left)
//
//  This is exactly what a ROS 2 Twist message carries, which is
//  why every program in this project ends up calling this one
//  function -- the motor test, micro-ROS and MQTT all alike.
// ============================================================
inline void drive(float lin, float ang) {
  // TODO(student) 1/4 -- lesson 4: turn (lin, ang) into two wheel speeds.
  //   Going straight, both wheels run at lin.
  //   Turning left (ang > 0), the right wheel goes faster and the left
  //   slower, each by ang * WHEEL_BASE / 2.
  //   Check with WHEEL_BASE 0.15:
  //     lin=0.1, ang=0  ->  left= 0.10, right=0.10   (straight)
  //     lin=0,   ang=2  ->  left=-0.15, right=0.15   (spin left)
  float left  = 0.0f;   // <- your formula here
  float right = 0.0f;   // <- your formula here

  // If we asked for more than the motors can do, scale BOTH down by
  // the same amount. Clipping them separately would bend the path.
  float biggest = fmaxf(fabsf(left), fabsf(right));
  if (biggest > MAX_LIN) {
    left  = left  / biggest * MAX_LIN;
    right = right / biggest * MAX_LIN;
  }

  setMotor(L_IN1, L_IN2, L_PWM, L_CH, left  / MAX_LIN);
  setMotor(R_IN1, R_IN2, R_PWM, R_CH, right / MAX_LIN);
}

inline void stopMotors() { drive(0.0f, 0.0f); }

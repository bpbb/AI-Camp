// ============================================================
//  LESSON 4 -- Does the hardware work?
//
//  No WiFi. No broker. No ROS 2. Nothing but the motors.
//
//  The point is to find wiring mistakes now, while there is only
//  one thing that can be wrong. Every later lesson adds a network,
//  and a robot that doesn't move is much harder to diagnose once
//  there are five things in the chain instead of one.
//
//  Put the robot ON A BOOK so the wheels spin in the air. It will
//  drive off the table otherwise.
// ============================================================
#include <Arduino.h>

#include "config.h"
#include "motor.h"

// Each step: a label, how to move, and for how long.
struct Step {
  const char *label;
  float lin;     // m/s forward
  float ang;     // rad/s turning
  int ms;
};

const Step STEPS[] = {
  // Turning hard enough that one wheel lands on exactly zero, so each
  // wheel can be checked on its own. Positive ang turns LEFT, which
  // means the RIGHT wheel is the one that moves.
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

// ============================================================
//  EDIT THIS FILE FIRST.
//  Everything you need to change for your own robot is here.
// ============================================================
#pragma once

// ---- Your WiFi ----
#define WIFI_SSID      "MyNetwork"
#define WIFI_PASSWORD  "changeme"

// ---- Give your robot a name ----
// Use your team name. If two robots share a name they will both
// respond to the same commands, which is funny once and then annoying.
#define ROBOT_ID       "robot1"

// ---- Lesson 6: MQTT broker (the teacher's computer) ----
#define MQTT_HOST      "192.168.1.100"
#define MQTT_PORT      1883

// ---- Lesson 5: micro-ROS agent (also the teacher's computer) ----
#define AGENT_IP       "192.168.1.100"
#define AGENT_PORT     8888

// ---- Which ROS 2 "channel" your team is on ----
// Every team in the room must use a DIFFERENT number, or you will all
// publish to the same /cmd_vel and drive each other's robots. Use the
// number your teacher gives you, and set the same one on your computer:
//     export ROS_DOMAIN_ID=<number>
#define ROS_DOMAIN_ID  0

// ---- Safety ----
// If no command arrives for this long, stop the motors.
// Without this, a dropped WiFi packet means the robot keeps driving.
#define COMMAND_TIMEOUT_MS  500

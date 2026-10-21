// ============================================================
//  EDIT THIS FILE FIRST.
//  Everything you need to change for your own robot is here.
// ============================================================
#pragma once

// ---- Your WiFi ----
#define WIFI_SSID      "VISTEC-GUEST"
#define WIFI_PASSWORD  ""

// ---- Give your robot a name (lessons 6-7) ----
// The phone drives it on MQTT topic robot/<ROBOT_ID>/cmd. Use your team
// name. The robot itself doesn't use this; the gateway on the computer
// reads it from here, so run `colcon build` in ros2_ws after changing it.
#define ROBOT_ID       "test"

// ---- micro-ROS agent: your computer's IP (`hostname -I`) ----
#define AGENT_IP       "10.204.79.39"
#define AGENT_PORT     8888 

// ---- Fixed IP for the ESP32 (always set) ----
// Must be on the same network as AGENT_IP and not used by any other device.
#define ESP_STATIC_IP  "192.168.1.111"
#define ESP_GATEWAY    "192.168.1.1"     // the router
#define ESP_SUBNET     "255.255.255.0"

// ---- Which ROS 2 "channel" your team is on ----
// Every team in the room must use a DIFFERENT number, or you will all
// publish to the same /cmd_vel and drive each other's robots. Use the
// number your teacher gives you, and set the same one on your computer:
//     export ROS_DOMAIN_ID=<number>
#define ROS_DOMAIN_ID  7

// ---- Safety ----
// If no command arrives for this long, stop the motors.
// Without this, a dropped WiFi packet means the robot keeps driving.
#define COMMAND_TIMEOUT_MS  500

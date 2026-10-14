// ============================================================
//  APPENDIX -- Driving the robot over MQTT instead of ROS 2.
//
//  Not part of the lessons. Keep it as a fallback: if micro-ROS will
//  not cooperate, this still gets the robot moving.
//
//  MQTT is a postbox. The robot subscribes to a topic (its own
//  address) and waits. Anyone who publishes to that topic can
//  drive it. There is no ROS 2 here at all.
//
//  Try it from a terminal:
//    mosquitto_pub -h <broker> -t robot/robot1/cmd -m F
// ============================================================
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "motor.h"

WiFiClient wifi;
PubSubClient mqtt(wifi);

char cmdTopic[64];
char statusTopic[64];

unsigned long lastCommand = 0;   // when we last heard anything
unsigned long lastStatus  = 0;

float curLin = 0.0f;
float curAng = 0.0f;

// ------------------------------------------------------------
//  This runs every time a message arrives for us.
// ------------------------------------------------------------
void onMessage(char *topic, byte *payload, unsigned int len) {
  // payload is not a normal string, so copy it and add the \0 ourselves
  char msg[128];
  if (len >= sizeof(msg)) len = sizeof(msg) - 1;
  memcpy(msg, payload, len);
  msg[len] = '\0';

  Serial.printf("got: %s\n", msg);

  // --- Style 1: a single letter. Easy to type, easy to remember. ---
  if (len == 1) {
    switch (toupper(msg[0])) {
      case 'F': curLin =  0.20f; curAng =  0.0f; break;  // forward
      case 'B': curLin = -0.20f; curAng =  0.0f; break;  // back
      case 'L': curLin =  0.0f;  curAng =  1.5f; break;  // spin left
      case 'R': curLin =  0.0f;  curAng = -1.5f; break;  // spin right
      case 'S': curLin =  0.0f;  curAng =  0.0f; break;  // stop
      default: return;                                   // nonsense, ignore
    }
    lastCommand = millis();
    return;
  }

  // --- Style 2: JSON, so you can ask for any speed you like. ---
  //     {"lin": 0.15, "ang": -0.4}
  JsonDocument doc;
  if (deserializeJson(doc, msg) != DeserializationError::Ok) {
    Serial.println("could not read that as JSON");
    return;
  }
  curLin = doc["lin"] | 0.0f;
  curAng = doc["ang"] | 0.0f;
  lastCommand = millis();
}

void connectWifi() {
  Serial.printf("wifi: joining %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.printf("\nwifi: ok, my address is %s\n", WiFi.localIP().toString().c_str());
}

void connectMqtt() {
  while (!mqtt.connected()) {
    Serial.printf("mqtt: connecting to %s ...\n", MQTT_HOST);
    if (mqtt.connect(ROBOT_ID)) {
      mqtt.subscribe(cmdTopic);
      Serial.printf("mqtt: ok, listening on %s\n", cmdTopic);
    } else {
      // rc=-2 almost always means wrong broker address
      Serial.printf("mqtt: failed (rc=%d), retrying\n", mqtt.state());
      stopMotors();
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  motorSetup();
  stopMotors();

  snprintf(cmdTopic,    sizeof(cmdTopic),    "robot/%s/cmd",    ROBOT_ID);
  snprintf(statusTopic, sizeof(statusTopic), "robot/%s/status", ROBOT_ID);

  connectWifi();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMessage);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { stopMotors(); connectWifi(); }
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();                   // let the MQTT library do its work

  // --- Safety: heard nothing recently? stop. ---
  // Take this out and the robot will happily drive into a wall the
  // moment WiFi hiccups.
  if (millis() - lastCommand > COMMAND_TIMEOUT_MS) {
    curLin = 0.0f;
    curAng = 0.0f;
  }

  drive(curLin, curAng);

  // --- Tell everyone we're alive, once a second ---
  if (millis() - lastStatus > 1000) {
    lastStatus = millis();
    char buf[96];
    snprintf(buf, sizeof(buf),
             "{\"id\":\"%s\",\"lin\":%.2f,\"ang\":%.2f,\"rssi\":%d}",
             ROBOT_ID, curLin, curAng, WiFi.RSSI());
    mqtt.publish(statusTopic, buf);
  }
}

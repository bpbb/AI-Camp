// ============================================================
//  บทที่ 5 -- ESP32 กลายเป็น ROS 2 node จริง
//
//  ใช้หุ่น มอเตอร์ และ drive() เหมือน motor test ต่างกันแค่ที่มาของคำสั่ง
//  เหมือน listener ในบทที่ 2: node ที่ subscribe topic (/cmd_vel)
//  จะเห็นได้ใน `ros2 node list` และ rqt_graph
//
//  รัน agent บนคอมพิวเตอร์ก่อน:
//    ./scripts/start_agent.sh        (รอรับที่ AGENT_PORT, 8888)
// ============================================================
#include <Arduino.h>
#include <micro_ros_platformio.h>
#include <WiFi.h>

#include <rcl/rcl.h>
#include <rcl/init_options.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <geometry_msgs/msg/twist.h>
#include <std_msgs/msg/int32.h>

#include "config.h"
#include "motor.h"

rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
rclc_executor_t executor;

rcl_subscription_t cmdSub;
geometry_msgs__msg__Twist cmdMsg;

rcl_publisher_t beatPub;
std_msgs__msg__Int32 beatMsg;
rcl_timer_t beatTimer;

unsigned long lastCommand = 0;
unsigned long lastPing = 0;

// ============================================================
//  ส่วนที่ต้องเขียน
//  โค้ดหลังจากนี้เป็นส่วนเชื่อมต่อระบบ
// ============================================================

// ถูกเรียกทุกครั้งที่มีการ publish มาที่ /cmd_vel
void onCmdVel(const void *msgin) {
  const geometry_msgs__msg__Twist *m = (const geometry_msgs__msg__Twist *)msgin;

  // Twist บอกการเคลื่อนที่ 3 มิติ แต่หุ่นล้อใช้แค่ 2 ค่า: วิ่งตามแกน x และหมุนรอบแกน z
  drive(m->linear.x, m->angular.z);
  // บันทึกเวลาที่ได้รับคำสั่งล่าสุด ให้ safety timeout ใน loop() ใช้ตรวจ
  lastCommand = millis();
}

// ROS 2 timer เรียกทุก 1 วินาที เพื่อ publish ตัวนับ
// ตรวจการเชื่อมต่อได้ด้วย `ros2 topic echo /heartbeat`
void onBeatTimer(rcl_timer_t *timer, int64_t) {
  if (timer == NULL) return;
  beatMsg.data++;
  rcl_publish(&beatPub, &beatMsg, NULL);
}

// ============================================================
//  ส่วนเชื่อมต่อระบบ -- ไม่ต้องแก้ไขโค้ดด้านล่าง
//
//  state machine ด้านล่างสร้าง node ใหม่เองเมื่อ agent restart
//  หรือ WiFi หลุด โดยไม่ต้องกด reset
// ============================================================

#define RCCHECK(fn) { if ((fn) != RCL_RET_OK) return false; }

enum State { WAITING_AGENT, AGENT_CONNECTED, AGENT_DISCONNECTED };
State state = WAITING_AGENT;

bool createEntities() {
  allocator = rcl_get_default_allocator();

  // เข้า ROS 2 domain เดียวกับคอมพิวเตอร์ ถ้าไม่ตั้ง หุ่นทุกตัวจะอยู่ domain 0
  // และรับคำสั่ง /cmd_vel เดียวกันหมด
  rcl_init_options_t initOptions = rcl_get_zero_initialized_init_options();
  RCCHECK(rcl_init_options_init(&initOptions, allocator));
  RCCHECK(rcl_init_options_set_domain_id(&initOptions, ROS_DOMAIN_ID));
  RCCHECK(rclc_support_init_with_options(&support, 0, NULL, &initOptions, &allocator));

  RCCHECK(rclc_node_init_default(&node, "esp32_robot", "", &support));

  RCCHECK(rclc_subscription_init_default(
      &cmdSub, &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist),
      "cmd_vel"));

  RCCHECK(rclc_publisher_init_default(
      &beatPub, &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
      "heartbeat"));

  RCCHECK(rclc_timer_init_default(&beatTimer, &support,
                                  RCL_MS_TO_NS(1000), onBeatTimer));

  // "2" = จำนวนสิ่งที่ executor ต้องดูแล: subscription และ timer
  // ถ้าใส่เลขผิด จะมีตัวใดตัวหนึ่งไม่ทำงาน
  RCCHECK(rclc_executor_init(&executor, &support.context, 2, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor, &cmdSub, &cmdMsg,
                                         &onCmdVel, ON_NEW_DATA));
  RCCHECK(rclc_executor_add_timer(&executor, &beatTimer));

  beatMsg.data = 0;
  return true;
}

void destroyEntities() {
  rmw_context_t *rmw = rcl_context_get_rmw_context(&support.context);
  rmw_uros_set_context_entity_destroy_session_timeout(rmw, 0);

  rcl_subscription_fini(&cmdSub, &node);
  rcl_publisher_fini(&beatPub, &node);
  rcl_timer_fini(&beatTimer);
  rclc_executor_fini(&executor);
  rcl_node_fini(&node);
  rclc_support_fini(&support);
}

void setup() {
  Serial.begin(115200);
  motorSetup();
  stopMotors();

  // set_microros_wifi_transports() เชื่อม WiFi และชี้ micro-ROS ไปที่ agent
  // แต่จะรอ WiFi เงียบ ๆ ไม่มีกำหนด จึงแสดงเครือข่ายที่เห็นก่อน
  // เพื่อให้รู้ทันทีถ้าชื่อผิดหรือเป็นเครือข่าย 5 GHz อย่างเดียว
  WiFi.mode(WIFI_STA);
  int found = WiFi.scanNetworks();
  bool seen = false;
  Serial.printf("\nwifi: %d networks in range (2.4 GHz only):\n", found);
  for (int i = 0; i < found; i++) {
    Serial.printf("  %s  (%d dBm)\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i));
    if (WiFi.SSID(i) == WIFI_SSID) seen = true;
  }
  if (!seen) Serial.printf("wifi: \"%s\" NOT in range -- wrong name, or 5 GHz?\n", WIFI_SSID);
  Serial.printf("wifi: joining \"%s\" ...\n", WIFI_SSID);

  IPAddress agent;
  agent.fromString(AGENT_IP);

  // ใช้ IP คงที่จาก config.h เสมอ ไม่รับ IP จากเครือข่ายที่ตอบก่อน
  IPAddress ip, gw, mask;
  ip.fromString(ESP_STATIC_IP);
  gw.fromString(ESP_GATEWAY);
  mask.fromString(ESP_SUBNET);
  WiFi.config(ip, gw, mask);
  Serial.printf("wifi: fixed IP %s\n", ESP_STATIC_IP);
  // ESP32 กับ agent ต้องอยู่วงเดียวกัน ไม่เช่นนั้นจะติดต่อ agent ไม่ได้
  if ((uint32_t(ip) & uint32_t(mask)) != (uint32_t(agent) & uint32_t(mask))) {
    Serial.printf("wifi: WARNING ESP_STATIC_IP %s and AGENT_IP %s are on different networks\n",
                  ESP_STATIC_IP, AGENT_IP);
  }
  set_microros_wifi_transports(WIFI_SSID, WIFI_PASSWORD, agent, AGENT_PORT);

  Serial.printf("wifi: ok, my IP is %s\n", WiFi.localIP().toString().c_str());
  delay(2000);   // รอให้ WiFi เชื่อมต่อเสร็จก่อนคุยกับ agent
}

void loop() {
  switch (state) {
    case WAITING_AGENT:
      // ping agent ซ้ำจนกว่าจะตอบ
      // WiFi โรงเรียน/guest อาจใช้เวลา 250 ms+ ต่อรอบ
      if (rmw_uros_ping_agent(500, 1) == RMW_RET_OK) {
        state = createEntities() ? AGENT_CONNECTED : WAITING_AGENT;
        if (state == AGENT_CONNECTED) Serial.println("agent: connected");
      } else {
        stopMotors();
        // แสดงสถานะว่ากำลังรออะไร
        if (WiFi.status() != WL_CONNECTED) {
          Serial.printf("wifi: not connected to \"%s\" yet\n", WIFI_SSID);
        } else {
          Serial.printf("agent: waiting for %s:%d (my IP %s)\n", AGENT_IP,
                        AGENT_PORT, WiFi.localIP().toString().c_str());
        }
        delay(500);
      }
      break;

    case AGENT_CONNECTED:
      // ตรวจเป็นระยะว่า agent ยังอยู่ (ไม่ทำทุก loop เพราะแต่ละ ping
      // ใช้เวลาไป-กลับผ่าน WiFi และทำให้ /cmd_vel ช้า)
      if (millis() - lastPing > 500) {
        lastPing = millis();
        // ถือว่าหลุดเมื่อ ping ไม่ตอบ 5 ครั้งติดกัน (~2.5 s)
        if (rmw_uros_ping_agent(500, 5) != RMW_RET_OK) {
          Serial.println("agent: lost");
          state = AGENT_DISCONNECTED;
          break;
        }
      }
      rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10));

      // ไม่มีคำสั่งใหม่ = หยุด ดู COMMAND_TIMEOUT_MS ใน config.h
      if (millis() - lastCommand > COMMAND_TIMEOUT_MS) stopMotors();
      break;

    case AGENT_DISCONNECTED:
      stopMotors();
      destroyEntities();
      state = WAITING_AGENT;
      break;
  }
}

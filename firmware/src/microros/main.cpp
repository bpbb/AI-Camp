// ============================================================
//  LESSON 5 -- The ESP32 becomes a real ROS 2 node
//
//  Same robot, same motors, same drive() function as the motor test.
//  The only thing that changes is where the numbers come from.
//
//  In lesson 2 you wrote a listener that waited on /chatter. This is
//  the same thing: a node that subscribes to a topic. It shows up in
//  `ros2 node list`, it subscribes to /cmd_vel like any other robot,
//  and rqt_graph draws it next to your computer's nodes.
//
//  Run the agent on the computer first:
//    ./scripts/start_agent.sh        (listens on AGENT_PORT, 8888)
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
//  THE PART THAT MATTERS
//  Everything below this block is plumbing.
// ============================================================

// Called every time someone publishes to /cmd_vel.
void onCmdVel(const void *msgin) {
  const geometry_msgs__msg__Twist *m = (const geometry_msgs__msg__Twist *)msgin;

  // A Twist describes motion in 3D, but a wheeled robot on a floor
  // can only do two of those: drive along x, and turn about z.
  drive(m->linear.x, m->angular.z);
  lastCommand = millis();
}

// Called once a second by a ROS 2 timer. Publishes a counter so you
// can prove the link works with `ros2 topic echo /heartbeat`.
void onBeatTimer(rcl_timer_t *timer, int64_t) {
  if (timer == NULL) return;
  beatMsg.data++;
  rcl_publish(&beatPub, &beatMsg, NULL);
}

// ============================================================
//  PLUMBING -- you don't need to change anything below here.
//
//  The extra complexity is reconnection. If the agent restarts, or
//  WiFi drops, a naive sketch stays dead until you press reset. The
//  state machine below notices and rebuilds the node by itself.
// ============================================================

#define RCCHECK(fn) { if ((fn) != RCL_RET_OK) return false; }

enum State { WAITING_AGENT, AGENT_CONNECTED, AGENT_DISCONNECTED };
State state = WAITING_AGENT;

bool createEntities() {
  allocator = rcl_get_default_allocator();

  // Join the same ROS 2 domain as your computer. Without this every robot
  // in the room lands on domain 0 together and they all answer to the
  // same /cmd_vel.
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

  // "2" = how many things the executor has to watch: the subscription
  // and the timer. Get this number wrong and one of them never fires.
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

  // This one line replaces all the transport code you would write by
  // hand on an STM32: it joins the WiFi and points micro-ROS at the agent.
  // The line after this waits for WiFi forever, silently. Say what we
  // can see first, so a wrong name or a 5 GHz-only network is obvious.
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
  set_microros_wifi_transports(WIFI_SSID, WIFI_PASSWORD, agent, AGENT_PORT);

  Serial.printf("wifi: ok, my IP is %s\n", WiFi.localIP().toString().c_str());
  delay(2000);   // let WiFi actually associate before we talk to the agent
}

void loop() {
  switch (state) {
    case WAITING_AGENT:
      // Knock on the agent's door once a second until it answers.
      if (rmw_uros_ping_agent(100, 1) == RMW_RET_OK) {
        state = createEntities() ? AGENT_CONNECTED : WAITING_AGENT;
        if (state == AGENT_CONNECTED) Serial.println("agent: connected");
      } else {
        stopMotors();
        // Say what we're waiting for, so a silent monitor isn't a mystery.
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
      // Check every so often that the agent is still there. Not every
      // loop: each ping is a WiFi round trip that delays /cmd_vel.
      if (millis() - lastPing > 500) {
        lastPing = millis();
        if (rmw_uros_ping_agent(100, 3) != RMW_RET_OK) {
          Serial.println("agent: lost");
          state = AGENT_DISCONNECTED;
          break;
        }
      }
      rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10));

      // No recent command, no motion. See COMMAND_TIMEOUT_MS in config.h.
      if (millis() - lastCommand > COMMAND_TIMEOUT_MS) stopMotors();
      break;

    case AGENT_DISCONNECTED:
      stopMotors();
      destroyEntities();
      state = WAITING_AGENT;
      break;
  }
}

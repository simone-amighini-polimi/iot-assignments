#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

// configurable flags
#define PRINT_TIMINGS true
#define SEND_ISR_ACTIVE true
#define RECEIVE_ISR_ACTIVE false
#define MAX_TRANSMISSION_POWER false

// non configurable options and initializations
#define LDR_VCC_PIN 32
#define PIR_VCC_PIN 33
#define LDR_INPUT_PIN 35
#define PIR_INPUT_PIN 9

const float GAMMA = 0.7;
const float RL10 = 50;

String message;
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
esp_now_peer_info_t peerInfo;

const unsigned long TIME_TO_SLEEP_US = 5.2 * 1e6;
unsigned long timeLogs[7];

void sendISR(const wifi_tx_info_t *info, esp_now_send_status_t status) {
  Serial.print(">>> Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "OK" : "ERROR");
}

void receiveISR(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  Serial.print(">>> Message received: ");
  char receivedString[len];
  memcpy(receivedString, data, len);
  Serial.println(String(receivedString));
}

void printMicros() {
  Serial.print(">>> Timings summary: ");
  for (int i = 0; i < 7; i++) {
    Serial.print(timeLogs[i]);
    if (i < 6) {
      Serial.print(", ");
    }
  }
  Serial.println();
}

void sensorsOn() {
  digitalWrite(LDR_VCC_PIN, HIGH);
  digitalWrite(PIR_VCC_PIN, HIGH);
}

void sensorsOff() {
  digitalWrite(LDR_VCC_PIN, LOW);
  digitalWrite(PIR_VCC_PIN, LOW);
}

void setup() {
  // serial initialization
  Serial.begin(115200);
  timeLogs[0] = micros();
  
  // pins initialization
  pinMode(LDR_VCC_PIN, OUTPUT);
  digitalWrite(LDR_VCC_PIN, LOW);
  pinMode(PIR_VCC_PIN, OUTPUT);
  digitalWrite(PIR_VCC_PIN, LOW);
  pinMode(LDR_INPUT_PIN, INPUT);
  pinMode(PIR_INPUT_PIN, INPUT);

  // sensing
  timeLogs[1] = micros();
  sensorsOn();
  int motionValue = digitalRead(PIR_INPUT_PIN);
  int sensorVoltageValue = analogRead(LDR_INPUT_PIN);
  sensorsOff();
  
  // elaborate sensing data and prepare message
  timeLogs[2] = micros();
  float voltage = sensorVoltageValue / 4095.0 * 3.3;
  float resistance = 10000.0 * voltage / (3.3 - voltage);
  float lux = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance, (1 / GAMMA));
  switch (motionValue) {
    case 1:
      message = "MOTION_DETECTED-LUMINOSITY:" + String(lux);
      break;
    case 0:
      message = "MOTION_NOT_DETECTED-LUMINOSITY:" + String(lux);
      break;
  }
  Serial.println(">>> Message to send: " + message);
  
  // WiFi initialization
  timeLogs[3] = micros();
  WiFi.mode(WIFI_STA);
  WiFi.setTxPower(MAX_TRANSMISSION_POWER ? WIFI_POWER_19_5dBm : WIFI_POWER_2dBm);
  esp_now_init();
  if(SEND_ISR_ACTIVE) {
    esp_now_register_send_cb(sendISR);
  }
  if(RECEIVE_ISR_ACTIVE) {
    esp_now_register_recv_cb(receiveISR);
  }
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  esp_now_add_peer(&peerInfo);
  
  // transmission
  timeLogs[4] = micros();
  esp_now_send(broadcastAddress, (uint8_t *)message.c_str(), message.length() + 1);
  
  // WiFi deactivation
  WiFi.mode(WIFI_OFF);
  timeLogs[5] = micros();
  
  // wait for reception if needed
  if(RECEIVE_ISR_ACTIVE) {
    delay(1000);
  }

  // deactivation and deep sleep
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_US);
  timeLogs[6] = micros();
  if (PRINT_TIMINGS) {
    printMicros();
  }
  Serial.flush();
  esp_deep_sleep_start();
}

void loop() {}

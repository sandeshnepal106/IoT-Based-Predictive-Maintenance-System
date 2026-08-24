#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <math.h>

#define DHTPIN 15
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define POT_PIN 34
#define LED_RUN 21
#define LED_FAULT 19

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);
bool machine_running = true;

void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (int i = 0; i < length; i++) msg += (char)payload[i];
  
  if (msg == "SHUTDOWN") {
    machine_running = false;
    digitalWrite(LED_RUN, LOW);
    digitalWrite(LED_FAULT, HIGH);
    Serial.println("[CRITICAL] Streamlit Trip Command Received! Machine Halted.");
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  pinMode(LED_RUN, OUTPUT);
  pinMode(LED_FAULT, OUTPUT);
  digitalWrite(LED_RUN, HIGH); // System starts in a healthy state
  digitalWrite(LED_FAULT, LOW);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    if (client.connect("ESP32_IIoT_Visual_Node")) {
      client.subscribe("iiot/factory/motor1/control");
    }
  }
  client.loop();

  if (machine_running) {
    // 1. Read Interactive Temperature
    float actual_temp = dht.readTemperature();
    if (isnan(actual_temp)) actual_temp = 40.0; 

    // 2. Read Interactive Vibration/Wear Knob
    int pot_value = analogRead(POT_PIN);
    float base_wear = map(pot_value, 0, 4095, 0, 150) / 10.0; 

    // 3. Add simulated high-frequency noise to the base slider value
    float vib_raw = sin(millis()) * 2.0 + base_wear + (random(-10, 10) / 10.0);
    float vib_rms = sqrt(pow(vib_raw, 2)); 

    String payload = "{\"temp\":" + String(actual_temp) + ",\"vib_rms\":" + String(vib_rms) + "}";
    client.publish("iiot/factory/motor1/telemetry", payload.c_str());
    Serial.println("Telemetry: " + payload);
  }
  
  delay(1000);
}
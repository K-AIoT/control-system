// Hei, dette er Audun, jeg har fortsatt brukt Eirik sin kode som basis så full disclosure er hos han for pakker brukt
// [1] https://microcontrollerslab.com/l298n-dc-motor-driver-module-esp8266-nodemcu/ Used to understand motor controller

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

#define DHTTYPE DHT22
// WIFI network
const char* ssid = "NTGR_E495";
const char* password = "L9j29iAU";
// MQTT broker credentials and IP
const char* MQTT_username = "kaiot";
const char* MQTT_password = "kebabsjappe";
const char* mqtt_server = "192.168.1.22";
WiFiClient espClient;
PubSubClient client(espClient);
// Motor driver pins
const int ENA = D7;  // controls speed
const int IN1 = D1;  // Directional control if needed
const int IN2 = D2;  // Directional control if needed

// Some declared as 0 to prevent memory conflict on startup
const int DHTPin = D4;
DHT dht(DHTPin, DHTTYPE);
float humidityPub = 0;
float tempPub = 0;
int speed = 0;
// Timer variable
long now = millis();
long lastMeasure = 0;

void setup() {
  Serial.begin(115200);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  digitalWrite(IN1, LOW);  // Ensures motor wont jumpstart with both low
  digitalWrite(IN2, LOW);
  delay(500);
  digitalWrite(IN1, HIGH); // Set direction
  digitalWrite(IN2, LOW);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883); // Sets mqtt server with the right port
  client.setCallback(callback); // Sets callcback function
}

void loop() {
  delay(500);
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("ESP8266ClientDCMotor", MQTT_username, MQTT_password);
  now = millis(); //sets up measurement interval
  if (now - lastMeasure > 2000) {  // checks measurement interval
    lastMeasure = now;
    float humidityPub = dht.readHumidity(); // reads humidity
    float tempPub = dht.readTemperature(); // reads temperature
    if (isnan(humidityPub)) { // could add an or statement to check temperature aswell
      Serial.println("Failed to read from DHT sensor!");
      return;
    }
    client.publish("dry/humidity", String(humidityPub).c_str()); // publishes humidity
    client.publish("dry/temperature", String(tempPub).c_str()); // publishes temperature
    Serial.print("Measured humidity: ");
    Serial.println(humidityPub);
    Serial.print("Measured temp: ");
    Serial.println(tempPub);
  }
}

//Function to change speed based on humidity
void changeSpeed(int speed) {
  Serial.println("Jeg snurrer"); // just to verify the funciton is called
  digitalWrite(IN1, HIGH); //ensure direction, incase it is switched later
  digitalWrite(IN2, LOW);
  analogWrite(ENA, speed); // sets speed recieved from contorl system
}


void callback(char* topic, byte* message, unsigned int length) { // runs when message is recieved
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String msg;
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    msg += (char)message[i];
  }                                         // the input string
  // int msgInt = msg.substring(msg.indexOf(':') + 2, msg.lastIndexOf('.')).toInt();  // extracting the integer value, not used at the moment
  Serial.println();
  if (strcmp(topic, "dry/speed") == 0) { // if the message is from the right topic
    Serial.print("The current motor output is ");
    Serial.println(msg);
    speed = msg.toInt();  // converts speed message from string to int
    changeSpeed(speed); // changes speed if the message was from the right topic
  }
  Serial.println();
}

// This functions connects your ESP8266 to your router
void setup_wifi() { // Connects to the network
  delay(10);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { // prints . for every 500ms of connection to create feeling progress
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP()); // Prints IP
}

void reconnect() {
  while (!client.connected()) { // Loops until connected 
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266ClientDC", MQTT_username, MQTT_password)) {
      Serial.println("connected");
      client.subscribe("dry/speed"); // subscribe to relevant topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
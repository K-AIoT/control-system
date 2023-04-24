/*****
 
 All the resources for this project:
 https://randomnerdtutorials.com/
 
*****/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// Defining which DHT sensor type is used
#define DHTTYPE DHT22  // DHT 22 

// Wifi credentials so the ESP8266 connects to the network
const char* ssid = "LAPTOP-JTPD9MA7 0005";
const char* password = "000%Y0e9";

// MQTT broker credentials
const char* MQTT_username = "kaiot";
const char* MQTT_password = "kebabsjappe";

// The Raspberry Pi IP address, so the sensor can connect to the MQTT broker
const char* mqtt_server = "192.168.137.38";


// Initializes the espClient
WiFiClient espClient;
PubSubClient client(espClient);

// DHT Sensor - GPIO 5 = D1 on ESP-12E NodeMCU board
const int DHTPin = 5;

// Lamp - LED - GPIO 4 = D2 on ESP-12E NodeMCU board
const int templamp = 14;
const int humlamp = 4;

// Initialize DHT sensor.
DHT dht(DHTPin, DHTTYPE);

// Timers auxiliar variables
long now = millis();
long lastMeasure = 0;

// This functions connects your ESP8266 to your router
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());
}

// This function is executed when some device publishes a message to a topic that your ESP8266 is subscribed to
// Change the function below to add logic to your program, so when a device publishes a message to a topic that
// your ESP8266 is subscribed you can actually do something
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String msg;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    msg += (char)message[i];
  }
  Serial.println();

  // Feel free to add more if statements to control more GPIOs with MQTT

  // If a message is received on the topic room/lamp, you check if the message is either on or off. Turns the lamp GPIO according to the message
  if (strcmp(topic, "bed/temp") == 0) {
    Serial.print("Changing Bed temp lamp to ");
    if (msg == "True") {
      digitalWrite(templamp, HIGH);
      Serial.print("On");
    } else if (msg == "False") {
      digitalWrite(templamp, LOW);
      Serial.print("Off");
    }
    Serial.println();
  }

  if (strcmp(topic, "bed/hum") == 0) {
    Serial.print("Changing Bed hum lamp to ");
    if (msg == "True") {
      digitalWrite(humlamp, HIGH);
      Serial.print("On");
    } else if (msg == "False") {
      digitalWrite(humlamp, LOW);
      Serial.print("Off");
    }
  }
  Serial.println();
}


// This functions reconnects your ESP8266 to your MQTT broker
// Change the function below if you want to subscribe to more topics with your ESP8266
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    /*
     YOU MIGHT NEED TO CHANGE THIS LINE, IF YOU'RE HAVING PROBLEMS WITH MQTT MULTIPLE CONNECTIONS
     To change the ESP device ID, you will have to give a new name to the ESP8266.
     Here's how it looks:
       if (client.connect("ESP8266Client")) {
     You can do it like this:
       if (client.connect("ESP1_Office")) {
     Then, for the other ESP:
       if (client.connect("ESP2_Garage")) {
      That should solve your MQTT multiple connections problem
    */
    if (client.connect("DHT22Sensor", MQTT_username, MQTT_password)) {
      Serial.println("connected");
      // Subscribe or resubscribe to a topic
      // You can subscribe to more topics (to control more LEDs in this example)
      client.subscribe("bed/temp");
      client.subscribe("bed/hum");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// The setup function sets your ESP GPIOs to Outputs, starts the serial communication at a baud rate of 115200
// Sets your mqtt broker and sets the callback function
// The callback function is what receives messages and actually controls the LEDs
void setup() {
  pinMode(templamp, OUTPUT);
  pinMode(humlamp, OUTPUT);

  dht.begin();

  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

// For this project, you don't need to change anything in the loop function. Basically it ensures that you ESP is connected to your broker
void loop() {
  delay(500);
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("ESP8266Client", MQTT_username, MQTT_password);

  now = millis();
  // Publishes new temperature and humidity every 2 seconds
  if (now - lastMeasure > 2000) {
    lastMeasure = now;
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    float humidity = dht.readHumidity();
    // Read temperature as Celsius (the default)
    float temperatureC = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    float temperatureF = dht.readTemperature(true);

    // Check if any reads failed and exit early (to try again).
    if (isnan(humidity) || isnan(temperatureC) || isnan(temperatureF)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }

    // Publishes Temperature and Humidity values
    client.publish("bed/temperature", String(temperatureC).c_str());
    client.publish("bed/humidity", String(humidity).c_str());
    //Uncomment to publish temperature in F degrees
    //client.publish("room/temperature", String(temperatureF).c_str());

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print(" %    ");
    Serial.print("Temperature: ");
    Serial.print(temperatureC);
    Serial.println(" ºC");
  }
}
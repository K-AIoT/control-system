// Hei, dette er Audun, mye av mqtt koden er kopiert av eirik, så se på hans kilder
// Open source links used:
// [1] https://lastminuteengineers.com/esp8266-i2c-lcd-tutorial/ Used to get LCD to work
// [2] https://github.com/johnrickman/LiquidCrystal_I2C/blob/master/examples/CustomChars/CustomChars.pde Used to create custom characters
// [3] https://randomnerdtutorials.com/esp8266-nodemcu-hc-sr04-ultrasonic-arduino/ Used to get ultrasonic sensor working
// #include <Wire.h> // not needed after the LCD memory slots are found at 0x27
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>


LiquidCrystal_I2C lcd(0x27, 20, 4);  // set the LCD address to 0x27 for a 16 chars and 2 line display

// WIFI network
const char* ssid = "NTGR_E495";
const char* password = "L9j29iAU";
// MQTT broker credentials and IP
const char* MQTT_username = "kaiot";
const char* MQTT_password = "kebabsjappe";
const char* mqtt_server = "192.168.1.22";
WiFiClient espClient;
PubSubClient client(espClient);


const int trigPin = D6;  // trigger pin
const int echoPin = D5;  // echo pin

// Some declared as 0 to ensure we dont get initial values that create unlikely scenarios due to use of old memory
float soundVelocity = 0.034;  // cm / us
int distance = 0;
float distanceCm = 0;
long duration = 0;
long now = millis();
long lastMeasure = 0;
int intMsg = 0;

void setup() {

  pinMode(trigPin, OUTPUT);             // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);              // Sets the echoPin as an Input
  Serial.begin(115200);                 // Starts the serial communication
  setup_wifi();                         // Connects to wifi with ssid and password
  client.setServer(mqtt_server, 1883);  //
  client.setCallback(callback);
  lcd.init();                // initialize the lcd
  lcd.backlight();           //enables LCD backlight
  lcd.home();                // puts cursor in the upper left of the LCD
  createCustomCharacters();  // calls function that defines the custom characters inside the ESP8266
}

void loop() {

  delay(500);
  if (!client.connected()) {  // reconnects if disconnected
    reconnect();
  }
  if (!client.loop())  // Connects to MQTT
    client.connect("ESP8266ClientLCD", MQTT_username, MQTT_password);
  now = millis();                  //sets up measurement interval
  if (now - lastMeasure > 2000) {  // checks measurement interval
    lastMeasure = now;
    distance = readRange();
    if (isnan(distance)) {
      Serial.println("Failed to read from ultrasonic sensor!");
      return;
    } else {
      client.publish("LCD/distance", String(distance).c_str());  // if valid measurement, the measurement is published
    }
  }
}

int readRange() {  // function that measures and returns range
  // Used to send the proper pulseout of the sensors
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in us
  duration = pulseIn(echoPin, HIGH);
  // Calculate the distance
  distanceCm = duration * soundVelocity / 2;
  // Prints the distance on the Serial Monitor
  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);
  distance = round(distanceCm);  // rounds the float to and integer
  return distance;
}

void printLCD(int msg) {
  // calculate the length of the integer recieved
  lcd.clear();        //clears lcd for new number
  int length = 0;     // tempoary variable for length
  int tempInt = msg;  // tempoary variable for recieved int
  while (tempInt != 0) {
    length++;
    tempInt /= 10;  //divides itself (int) by 10 until it is 0 to get length of message recieved
  }
  for (int i = length - 1; i >= 0; i--) {                 // to display each digit of the recieved integer
    int num = (msg / static_cast<int>(pow(10, i))) % 10;  // finds the relevant digit by divid the message by a power of 10, then doing the modulus operation on that number to find the remainder, this gives the digit in focus
    int u = 3 * (length - i);                             // a variable to find the correct position for the cursor on the LCD display
    // do something with digit
    if (num >= 0 && num <= 9) {  // if the digit is 0-9 print the digit to the relevant position on the LCD
      switch (num) {
        case 0:
          display0(u);
          break;
        case 1:
          display1(u);
          break;
        case 2:
          display2(u);
          break;
        case 3:
          display3(u);
          break;
        case 4:
          display4(u);
          break;
        case 5:
          display5(u);
          break;
        case 6:
          display6(u);
          break;
        case 7:
          display7(u);
          break;
        case 8:
          display8(u);
          break;
        case 9:
          display9(u);
          break;
        default:
          Serial.println("Invalid input!");
          break;
      }
    }
  }
}

void callback(char* topic, byte* message, unsigned int length) {  // callback function runs everytime a messge is recieved
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String msg;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    msg += (char)message[i];
  }

  Serial.println();
  // if we recieve from the right topic
  if (strcmp(topic, "LCD/print") == 0) {  // compares if the topic of the recieved message is the topic we want
    Serial.print("The current percieved range is ");
    Serial.println(msg);
    intMsg = msg.toInt();  // converts speed message from string to int
  }
  Serial.println();
  printLCD(intMsg);  // calls function to print recieved message, should be put into the if check so that it does not run unless there is a new value
}

// This functions connects your ESP8266 to your router
void setup_wifi() {
  delay(100);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {  // prints a . for every 500ms that it is unconnected to give an authentic experience of progress
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());  //prints ip so that we can use it on the KM laptop
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client", MQTT_username, MQTT_password)) {
      Serial.println("connected");
      client.subscribe("LCD/print");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// write numbers from printLCD function
// displayN where N is the number
// check report for what the custom characters 0 through 7 means
void display0(int pos) {  //Recives curcors position
  lcd.setCursor(pos, 0);  // upper half of display
  lcd.write(0);
  lcd.write(1);
  lcd.setCursor(pos, 1);  // lower half of display
  lcd.write(2);
  lcd.write(3);
}
void display1(int pos) {
  lcd.setCursor(pos, 0);
  lcd.print(" ");
  lcd.write(6);
  lcd.setCursor(pos, 1);
  lcd.print(" ");
  lcd.write(6);
}
void display2(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(7);
  lcd.write(5);
  lcd.setCursor(pos, 1);
  lcd.write(4);
  lcd.write(7);
}
void display3(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(7);
  lcd.write(5);
  lcd.setCursor(pos, 1);
  lcd.write(7);
  lcd.write(5);
}
void display4(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(2);
  lcd.write(3);
  lcd.setCursor(pos, 1);
  lcd.print(" ");
  lcd.write(6);
}
void display5(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(4);
  lcd.write(7);
  lcd.setCursor(pos, 1);
  lcd.write(7);
  lcd.write(5);
}
void display6(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(4);
  lcd.write(7);
  lcd.setCursor(pos, 1);
  lcd.write(4);
  lcd.write(5);
}
void display7(int pos) {
  lcd.setCursor(pos, 0);
  lcd.print(" ");
  lcd.write(1);
  lcd.setCursor(pos, 1);
  lcd.print(" ");
  lcd.write(6);
}
void display8(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(4);
  lcd.write(5);
  lcd.setCursor(pos, 1);
  lcd.write(4);
  lcd.write(5);
}
void display9(int pos) {
  lcd.setCursor(pos, 0);
  lcd.write(4);
  lcd.write(5);
  lcd.setCursor(pos, 1);
  lcd.print(" ");
  lcd.write(6);
}

// custom characters used to display numbers
void createCustomCharacters() {
  //Blank
  byte customChar0[] = {
    B00011111,
    B00011111,
    B00011000,
    B00011000,
    B00011000,
    B00011000,
    B00011000,
    B00011000,
  };
  byte customChar1[] = {
    B00011111,
    B00011111,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
  };
  byte customChar2[] = {
    B00011000,
    B00011000,
    B00011000,
    B00011000,
    B00011000,
    B00011000,
    B00011111,
    B00011111,
  };
  byte customChar3[] = {
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00011111,
    B00011111,
  };
  byte customChar6[] = {
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
  };
  byte customChar5[] = {
    B00011111,
    B00011111,
    B00000011,
    B00000011,
    B00000011,
    B00000011,
    B00011111,
    B00011111,
  };
  byte customChar7[] = {
    B00011111,
    B00011111,
    B00000000,
    B00000000,
    B00000000,
    B00000000,
    B00011111,
    B00011111,
  };
  byte customChar4[] = {
    B00011111,
    B00011111,
    B00011000,
    B00011000,
    B00011000,
    B00011000,
    B00011111,
    B00011111,
  };
  lcd.createChar(0, customChar0);
  lcd.createChar(1, customChar1);
  lcd.createChar(2, customChar2);
  lcd.createChar(3, customChar3);
  lcd.createChar(4, customChar4);
  lcd.createChar(5, customChar5);
  lcd.createChar(6, customChar6);
  lcd.createChar(7, customChar7);
}

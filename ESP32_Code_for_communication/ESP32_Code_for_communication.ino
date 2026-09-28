#include <WiFi.h>
#include <ESP32Servo.h>
#include <LiquidCrystal.h>

#define LED_PIN 4
#define SERVO_PIN 2

const char* ssid = "SUNDAR ONE 2F";
const char* password = "1122334455";

WiFiServer server(80);

LiquidCrystal lcd(23, 22, 21, 19, 18, 5);
Servo myservo;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Booting...");

  pinMode(LED_PIN, OUTPUT);
  lcd.begin(16, 2);
  myservo.attach(SERVO_PIN);
  myservo.write(0);
  lcd.clear();
  lcd.print("System Ready");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    lcd.clear();
    lcd.print("Connecting WiFi");
  }
  Serial.println();
  Serial.print("WiFi connected. IP address: ");
  Serial.println(WiFi.localIP());
  lcd.clear();
  lcd.print("WiFi Connected");
  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String request = client.readStringUntil('\r');
    client.flush();

    if (request.indexOf("/infected") != -1) {
      digitalWrite(LED_PIN, HIGH);
      lcd.clear();
      lcd.print("infected");
      myservo.write(90);
      client.println("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nInfected action done");
    } else if (request.indexOf("/notinfected") != -1) {
      digitalWrite(LED_PIN, LOW);
      lcd.clear();
      lcd.print("not infected");
      myservo.write(0);
      client.println("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nNot infected action done");
    } else {
      client.println("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot found");
    }
    delay(1);
    client.stop();
  }
}
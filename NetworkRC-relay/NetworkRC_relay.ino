#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Servo.h>

const char* ssid = "Quantum Link";
const char* password = "HPGNLWZ2DNTXB5K7";

ESP8266WebServer server(80);
Servo turn;

void handleControls() {
  String message;

  if (server.arg("steerAngle") != "") {
    turn.write(server.arg("steerAngle").toInt());
    message += "servo angle: " + server.arg("steerAngle") + "\n";
  }

  if (server.arg("Relay") != "") {
    int relay = server.arg("Relay").toInt();
    if (relay == 2) {
      digitalWrite(D8, LOW);
      digitalWrite(D7, LOW);
      message += "Stop\n";
    }
    if (relay == 1) {
      digitalWrite(D8, LOW);
      digitalWrite(D7, HIGH);
      message += "Forward\n";
    }
    if (relay == 0) {
      digitalWrite(D7, LOW);
      digitalWrite(D8, HIGH);
      message += "Backward\n";
    }
  }
  server.send(200, "text / plain", message);
}


void setup() {

  //Communication setup.
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Waiting to connect…");
  }
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC address: ");
  Serial.println(WiFi.macAddress());
  server.on("/controls", handleControls);
  server.begin();
  Serial.println("Server listening:");

  //Motor Interface setup.
  pinMode(D7, OUTPUT); // relay A
  pinMode(D8, OUTPUT); // relay B
  pinMode(D5, OUTPUT); // led light strip

  turn.attach(D0); // steering Control (pwm 60 - 80 - 100)
}

void loop() {
  int lightlev = 256 - analogRead(A0) / 4;
  if (lightlev > 100) {
    digitalWrite(D5, HIGH);
  }
  else {
    digitalWrite(D5, LOW);
  }
  delay(5);
  server.handleClient();
}


#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Servo.h>

const char* ssid = "";
const char* password = "";

ESP8266WebServer server(80);

Servo turn;

int timeout = 0;
bool motor = false;

void keep_alive() {
  if (server.client() == 0) {
    timeout++;
    delay(5);
    if (timeout > 50) {
      timeout = 0;
      if (motor) {
        Serial.println("off");
        motor = false;
        digitalWrite(D4, LOW);
        digitalWrite(D5, LOW);
      }
    }
  }
}

void com() {
  String message;
  timeout = 0;
  if (server.arg("steerAngle") != "") {
    turn.write(server.arg("steerAngle").toInt());
    message += "servo angle: " + server.arg("steerAngle") + "\n";
  }

  if (server.arg("Relay") != "") {
    int relay = server.arg("Relay").toInt();
    if (relay == 0) {
      digitalWrite(D4, LOW);
      digitalWrite(D5, LOW);
      message += "Stop\n";
    }
    if (relay == 1) {
      motor = true;
      digitalWrite(D4, LOW);
      digitalWrite(D5, HIGH);
      message += "Forward\n";
    }
    if (relay == 2) {
      motor = true;
      digitalWrite(D4, HIGH);
      digitalWrite(D5, LOW);
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
  server.on("/", com);
  server.begin();
  Serial.println("Server listening:");

  //Motor Interface setup.
  pinMode(D5, OUTPUT); // relay A
  pinMode(D4, OUTPUT); // relay B
  //pinMode(D5, OUTPUT); // led light strip

  turn.attach(D0); // steering Control (pwm 60 - 80 - 100)
  turn.write(90);
}

void loop() {
  server.handleClient();
  keep_alive();
}

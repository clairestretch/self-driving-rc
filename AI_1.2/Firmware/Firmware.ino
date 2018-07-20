#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "WiFiClient.h"

const char* ssid = "";
const char* password = "";

ESP8266WebServer server(80);
int timeout = 0;
int pins[6] = {D1, D2, D3, D4, D5, D7};
bool motor = false;

//keep connection alive if client is connected, kill connection and turn off pins if timeout.
void keep_alive() {
  if (!server.client()) {
    timeout++;
    delay(5);
    if (timeout > 50) {
      timeout = 0;
      if (motor) {
        motor = false;
        for (int i = 0; i < 6; i++) {
          digitalWrite(pins[i], LOW);
        }
      }
    }
  }
}

void root() {
  String message;
  timeout = 0;

  if (server.arg("turn") != "") {
    int TURN = server.arg("turn").toInt();
    if (TURN == 0) {
      digitalWrite(D1, LOW);
      digitalWrite(D2, LOW);
      message += "STRAIGHT";
    }
    if (TURN == 1) {
      motor = true;
      digitalWrite(D1, HIGH);
      digitalWrite(D2, LOW);
      message += "TURN LEFT";
    }
    if (TURN == 2) {
      motor = true;
      digitalWrite(D1, LOW);
      digitalWrite(D2, HIGH);
      message += "TURN RIGHT";
    }
  }

  if (server.arg("drive") != "") {
    int DIR = server.arg("drive").toInt();
    if (DIR == 0) {
      digitalWrite(D3, LOW);
      digitalWrite(D4, LOW);
      digitalWrite(D7, LOW);
      message += "STOP";
    }
    if (DIR == 1) {
      motor = true;
      digitalWrite(D3, LOW);
      digitalWrite(D4, HIGH);
      digitalWrite(D7, LOW);
      message += "FORWARD";
    }
    if (DIR == 2) {
      motor = true;
      digitalWrite(D3, HIGH);
      digitalWrite(D4, LOW);
      digitalWrite(D7, HIGH);
      message += "BACKWARD";
    }
  }

  if (server.arg("drivepwm") != "") {
    int pulse = server.arg("drivepwm").toInt();
    analogWrite(D5, pulse);
    message += " PWM: " + String(pulse);
  }
  server.send(200, "text / plain", message);
}


void setup() {
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

  // Start the server
  server.on("/", root);
  server.begin();
  Serial.println("Server started");

  //Turn Motor
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);

  //Drive Motor
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);

  //Drive Motor Speed 0 - 1023
  pinMode(D5, OUTPUT);

  //Lights
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);

  //headlights
  digitalWrite(D6, HIGH);
}

void loop() {
  server.handleClient();
  keep_alive();
}

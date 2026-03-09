#include <Servo.h>
#include <Wire.h>
#include <Adafruit_INA219.h>

Servo myServo;
Adafruit_INA219 ina219;

// Pins
const int servoPin = 8;
const int feedbackPin = A1;

// Servo limits
int lowLimit = 20;
int highLimit = 165;

// Calibration values
int fbMin = 640;
int fbMax = 60;

// Commanded angle
int commandAngle = 90;

// Logging interval (milliseconds)
const unsigned long logInterval = 50;

// Timing variables
unsigned long lastLogTime = 0;
unsigned long startTime = 0;

void setup() {

  Serial.begin(115200);

  myServo.attach(servoPin);
  myServo.write(commandAngle);

  // Initialize INA219
  if (!ina219.begin()) {
    Serial.println("INA219 not detected");
    while (1);
  }

  startTime = millis();

  // CSV header
  Serial.println("time_ms,command_angle,feedback_angle,current_mA");
}

void loop() {

  // Read commanded angle from Serial
  if (Serial.available() > 0) {

    int targetAngle = Serial.parseInt();

    if (targetAngle >= 0 && targetAngle <= 180) {
      commandAngle = targetAngle;
      myServo.write(commandAngle);
    }

    while (Serial.available()) Serial.read();
  }

  // Read servo feedback
  int fbRaw = analogRead(feedbackPin);

  int fbAngle = map(fbRaw, fbMin, fbMax, lowLimit, highLimit);
  fbAngle = constrain(fbAngle, lowLimit, highLimit);

  // Log data at specified interval
  if (millis() - lastLogTime >= logInterval) {

    unsigned long timeNow = millis() - startTime;

    float current_mA = ina219.getCurrent_mA();

    Serial.print(timeNow);
    Serial.print(",");
    Serial.print(commandAngle);
    Serial.print(",");
    Serial.print(fbAngle);
    Serial.print(",");
    Serial.println(current_mA);

    lastLogTime = millis();
  }
}

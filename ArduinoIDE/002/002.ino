/***
 * LED Blinking
 * Code Written by TechMartian
 */
#include <esp_adc_cal.h>

const int ledPin = 22;
const int BUTTON_1 = 32;

void setup() {
  Serial.begin(115200);
  // setup pin 5 as a digital output pin
  pinMode(ledPin, OUTPUT);
  pinMode(BUTTON_1, INPUT);
}

void loop() {
  if(digitalRead(BUTTON_1) == HIGH) {
    digitalWrite (ledPin, HIGH);  // turn on the LED
  } else {
    digitalWrite (ledPin, LOW);  // turn on the LED
  }
}

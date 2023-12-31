/***
 * LED Blinking
 * Code Written by TechMartian
 */
#include <esp_adc_cal.h>

const int ledPin = 22;

void setup() {
  Serial.begin(115200);
  // setup pin 5 as a digital output pin
  pinMode (ledPin, OUTPUT);
}

void loop() {
  digitalWrite (ledPin, HIGH);  // turn on the LED

  delay(500); // wait for half a second or 500 milliseconds

  digitalWrite (ledPin, LOW); // turn off the LED

  delay(3000); // wait for half a second or 500 milliseconds
  Serial.println("OK");

}

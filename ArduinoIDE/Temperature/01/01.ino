#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 22
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

unsigned long lastTime = millis();

void setup(void) {
  Serial.begin(115200);
  Serial.println("Dallas Temperature IC Control Library");
  sensors.begin();
}

void loop(void) {
  if (millis() - lastTime > 3000) {
    lastTime = millis();

    Serial.println("Requesting temperatures...");
    sensors.requestTemperatures();
    Serial.print("Temperature is: ");
    Serial.print(sensors.getTempCByIndex(0));
    Serial.println(" *C");
  }
}

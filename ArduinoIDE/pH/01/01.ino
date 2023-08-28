#define PH_PIN 4
float voltage;
unsigned long lastTime = millis();

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (millis() - lastTime > 3000) {
    lastTime = millis();

    voltage = analogRead(PH_PIN)/4095.0 * 3000;
    Serial.println(voltage);
  }
}

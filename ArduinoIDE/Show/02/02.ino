#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <U8g2_for_Adafruit_GFX.h>
#include <OneWire.h>
#include <DallasTemperature.h>

enum MenuState { SPLASH, INSTRUCTION };

#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

unsigned long lastTime = millis();

//ESP32-WROOM
#define TFT_CS    15 //CS
#define TFT_RST   -1 
#define TFT_DC    27 //A0
#define TFT_MOSI  13 //SDA
#define TFT_CLK   14 //SCK
#define TFT_MISO  0

#define offset_X  32
#define offset_Y 120

#define X_center 160
#define Y_center 160

const int reducedSize = 256;

SPIClass * hspi = new SPIClass(HSPI);
Adafruit_ILI9341 tft = Adafruit_ILI9341(hspi, TFT_DC, TFT_CS, TFT_RST);

U8G2_FOR_ADAFRUIT_GFX u8g2Fonts;

const int splashPin = 25;

const int BUTTON_1 = 35;
const int BUTTON_2 = 36;
const int ledGreenPin = 21;

const int POT_1 = 34;
const int ledPin = 22;

const int freq = 5000;
const int ledChannel = 0;
const int resolution = 8;

bool showInstruction = false;
bool buttonState = false;
bool lastButtonState = false;

bool deviceState = false;
bool button1State = false;
bool lastButton1State = false;
bool button2State = false;
bool lastButton2State = false;

MenuState page = SPLASH;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  sensors.begin();
  
  pinMode(splashPin, INPUT);
  
  pinMode(ledGreenPin, OUTPUT);
  pinMode(BUTTON_1, INPUT);
  pinMode(BUTTON_2, INPUT);
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(ledPin, ledChannel);

  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(ILI9341_BLACK);
  delay(500);
  u8g2Fonts.begin(tft); // connect u8g2 procedures to Adafruit GFX
  delay(1000);

  uint16_t bg = ILI9341_BLACK;
  uint16_t fg = ILI9341_WHITE;
  u8g2Fonts.setForegroundColor(fg);         // apply Adafruit GFX color
  u8g2Fonts.setBackgroundColor(bg);

  u8g2Fonts.setFont(u8g2_font_fub20_tf);

  drawSplash();

}

void loop() {
  // put your main code here, to run repeatedly:
  int analogValue = analogRead(POT_1);
  int percentage = map(analogValue, 0, 4095, 255, 0);
  ledcWrite(ledChannel, percentage);

  int reading = digitalRead(splashPin);
  int reading1 = digitalRead(BUTTON_1);
  int reading2 = digitalRead(BUTTON_2);

  if (reading != buttonState) {
    buttonState = reading;

    if (buttonState == LOW) {
      showInstruction = !showInstruction;
      if (showInstruction) {
        page = INSTRUCTION;
        tft.fillScreen(ILI9341_BLACK);
        u8g2Fonts.setCursor(20, 30);
        u8g2Fonts.print("INPUT");
        u8g2Fonts.setCursor(180, 30);
        u8g2Fonts.print("OUTPUT");

        u8g2Fonts.setCursor(40, 60);
        u8g2Fonts.print("35");
        u8g2Fonts.setCursor(200, 60);
        u8g2Fonts.print("21");
        u8g2Fonts.setCursor(40, 90);
        u8g2Fonts.print("36");
        u8g2Fonts.setCursor(200, 90);
        u8g2Fonts.print("21");
        u8g2Fonts.setCursor(40, 120);
        u8g2Fonts.print("34: POT");
        u8g2Fonts.setCursor(200, 120);
        u8g2Fonts.print("22");

        u8g2Fonts.setCursor(20, 150);
        u8g2Fonts.print("Temp (DS18B20): 4");
        tft.drawLine(0, 160, 320, 160, ILI9341_WHITE);
        u8g2Fonts.setCursor(20, 200);
        u8g2Fonts.print("Temp:");
        u8g2Fonts.setCursor(200, 200);
        u8g2Fonts.print("\xB0\C");
      } else {
        page = SPLASH;
        tft.fillScreen(ILI9341_BLACK);
        drawSplash();
      }
    }
  }

  if (reading1 != lastButton1State) {
    lastButton1State = reading1;

    if (reading1 == LOW) {
      deviceState = false;
    } else {
      deviceState = true;
    }
    digitalWrite(ledGreenPin, deviceState);
  }

  if (reading2 != lastButton2State) {
    lastButton2State = reading2;

    if (reading2 == LOW) {
      deviceState = !deviceState;
      digitalWrite(ledGreenPin, deviceState);
    }
  }

  
  if (millis() - lastTime > 4000) {
    lastTime = millis();

    if (page == INSTRUCTION) {
      tft.fillRect(115, 175, 80, 30, ILI9341_BLACK);
      sensors.requestTemperatures();
      u8g2Fonts.setCursor(120, 200);
      u8g2Fonts.print(sensors.getTempCByIndex(0));
    }
  }
  //lastButtonState = reading;
}

void drawSplash() {
  u8g2Fonts.setCursor(100, 30);
  u8g2Fonts.print("TitraLab");

  for (int i = X_center-100, j = Y_center-130; i <= X_center; i+=5, j+=9) {
    tft.drawLine(i, j, i+100, 240-j, ILI9341_RED);
  }
}

#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <U8g2_for_Adafruit_GFX.h>

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

const int BUTTON_1 = 35;
const int ledGreenPin = 21;

const int POT_1 = 34;
const int ledPin = 22;

const int freq = 5000;
const int ledChannel = 0;
const int resolution = 8;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(ledGreenPin, OUTPUT);
  pinMode(BUTTON_1, INPUT);
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(ledPin, ledChannel);

  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(ILI9341_BLACK);
  delay(500);
  u8g2Fonts.begin(tft); // connect u8g2 procedures to Adafruit GFX
  delay(1000);

  //tft.drawRect(offset_X-2, offset_Y-100, reducedSize+4, 200, ILI9341_WHITE);
  //tft.drawRect(offset_X-3, offset_Y-101, reducedSize+6, 202, ILI9341_WHITE);

  uint16_t bg = ILI9341_BLACK;
  uint16_t fg = ILI9341_WHITE;
  u8g2Fonts.setForegroundColor(fg);         // apply Adafruit GFX color
  u8g2Fonts.setBackgroundColor(bg);

  u8g2Fonts.setFont(u8g2_font_fub20_tr);

  /*
  tft.setCursor(0, 0);
  tft.setTextColor(ILI9341_WHITE);  tft.setTextSize(1);
  tft.println("Hello World!");
  */

  u8g2Fonts.setCursor(100, 30);
  u8g2Fonts.print("TitraLab");

  for (int i = X_center-100, j = Y_center-130; i <= X_center; i+=5, j+=9) {
    tft.drawLine(i, j, i+100, 240-j, ILI9341_RED);
  }
  //tft.drawLine(X_center-100, Y_center-50, X_center, Y_center+50, ILI9341_RED);
  //tft.drawLine(X_center, Y_center+50, X_center+100, Y_center-50, ILI9341_RED);
}

void loop() {
  // put your main code here, to run repeatedly:
  int analogValue = analogRead(POT_1);
  int percentage = map(analogValue, 0, 4095, 255, 0);
  ledcWrite(ledChannel, percentage);

  if (digitalRead(BUTTON_1) == HIGH) {
    digitalWrite(ledGreenPin, HIGH);
  } else {
    digitalWrite(ledGreenPin, LOW);
  }
}

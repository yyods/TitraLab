# ==============================================================================
# TitraLab Pin Configuration / การกำหนดขา TitraLab
# ==============================================================================
# ไฟล์นี้กำหนดขา GPIO มาตรฐานสำหรับบอร์ด TitraLab
# This file defines standard GPIO pins for the TitraLab board
# ==============================================================================

# LEDs - ไฟ LED แสดงสถานะ (Status LEDs)
LED_RED   = 2    # GPIO2  - LED สีแดง (Red LED)
LED_GREEN = 4    # GPIO4  - LED สีเขียว (Green LED)

# Buttons - ปุ่มกด (Push buttons) - Input only, no internal pull-up
BUTTON1 = 34     # GPIO34 - ปุ่มกด 1 (Button 1)
BUTTON2 = 35     # GPIO35 - ปุ่มกด 2 (Button 2)
BUTTON3 = 39     # GPIO39 - ปุ่มกด 3 (Button 3)

# Temperature Sensor - เซ็นเซอร์อุณหภูมิ (DS18B20 OneWire)
DS18B20_PIN = 16  # GPIO16 - เซ็นเซอร์อุณหภูมิ DS18B20 (Temperature sensor)

# pH Sensor - เซ็นเซอร์วัดค่า pH (ADC input)
PH_PIN = 25      # GPIO25 - เซ็นเซอร์ pH (pH sensor ADC)

# Potentiometers - ตัวต้านทานปรับค่าได้ (Variable resistors)
POT1_PIN = 32    # GPIO32 - Potentiometer 1
POT2_PIN = 33    # GPIO33 - Potentiometer 2

# Buzzer - ลำโพง Buzzer (PWM output)
BUZZER_PIN = 26  # GPIO26 - Buzzer (PWM)

# Pump - ปั๊มสำหรับไทเทรชัน (PWM output)
PUMP_PIN = 21    # GPIO21 - ปั๊ม (Pump PWM)

# SD Card (SoftSPI) - การ์ด SD สำหรับบันทึกข้อมูล (Data storage)
SD_MISO = 19     # GPIO19 - SD Card MISO
SD_MOSI = 23     # GPIO23 - SD Card MOSI
SD_SCK  = 18     # GPIO18 - SD Card SCK (Clock)
SD_CS   = 5      # GPIO5  - SD Card CS (Chip Select)

# TFT Display (SPI Bus 1) - จอแสดงผล TFT ILI9341
TFT_SCK  = 14    # GPIO14 - TFT SPI Clock
TFT_MOSI = 13    # GPIO13 - TFT SPI Data (MOSI)
TFT_DC   = 27    # GPIO27 - TFT Data/Command
TFT_CS   = 15    # GPIO15 - TFT Chip Select
TFT_RST  = 0     # GPIO0  - TFT Reset
TFT_SPI_BUS = 1  # SPI Bus 1

# ==============================================================================
# 02_temperature.py - การแสดงอุณหภูมิบนจอ TFT (Temperature Display on TFT)
# ==============================================================================
# โปรแกรมนี้อ่านค่าอุณหภูมิจาก DS18B20 และแสดงผลบนจอ TFT
# This program reads temperature from DS18B20 and displays on TFT
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

from time import sleep, ticks_ms, sleep_ms
from ili9341 import Display, color565
from machine import Pin, SPI
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20

# ==============================================================================
# การตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
# DS18B20 Temperature sensor setup
# ==============================================================================
ONE_WIRE_BUS = 16  # GPIO16 สำหรับ DS18B20 (GPIO16 for DS18B20)
ow = OneWire(Pin(ONE_WIRE_BUS))
ds = DS18X20(ow)

# ==============================================================================
# การตั้งค่าจอ TFT ILI9341 (SPI Bus 1)
# TFT ILI9341 setup (SPI Bus 1)
# ==============================================================================
SPI_BUS = 1
SCK_PIN = 14    # GPIO14 - SPI Clock
MOSI_PIN = 13   # GPIO13 - SPI Data
DC_PIN = 27     # GPIO27 - Data/Command
CS_PIN = 15     # GPIO15 - Chip Select
RST_PIN = 0     # GPIO0  - Reset

# สร้าง SPI และ Display object
# Create SPI and Display objects
spi = SPI(SPI_BUS, baudrate=40000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
display = Display(spi, dc=Pin(DC_PIN), cs=Pin(CS_PIN), rst=Pin(RST_PIN),
                  width=320, height=240, rotation=90)

# สแกนหาเซ็นเซอร์ DS18B20 (Scan for DS18B20 sensors)
roms = ds.scan()

# โหลดฟอนต์ (Load font)
print("กำลังโหลดฟอนต์... (Loading font...)")
arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)

# กำหนดสี (Define colors)
WHITE = color565(255, 255, 255)
GREEN = color565(0, 255, 0)
BLACK = color565(0, 0, 0)
YELLOW = color565(255, 255, 0)

# ตัวแปรสำหรับจับเวลา (Variable for timing)
last_temp_update = 0
UPDATE_INTERVAL = 3000  # อัปเดตทุก 3 วินาที (Update every 3 seconds)

# ==============================================================================
# ตรวจสอบเซ็นเซอร์ (Check sensors)
# ==============================================================================
print("=" * 50)
print("แสดงอุณหภูมิบนจอ TFT (Temperature Display on TFT)")
print("=" * 50)

if not roms:
    print("ไม่พบเซ็นเซอร์ DS18B20 (DS18B20 sensor not found)")
    display.draw_text(60, 100, 'Sensor not found!', arcadepix, color565(255, 0, 0))
else:
    print(f"พบเซ็นเซอร์ {len(roms)} ตัว (Found {len(roms)} sensor(s))")

    # แสดงหัวข้อบนจอ (Display header on screen)
    display.draw_text(90, 20, 'Temperature:', arcadepix, WHITE)

    print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")

    try:
        while True:
            current_time = ticks_ms()

            # ตรวจสอบว่าถึงเวลาอัปเดตหรือยัง
            # Check if it's time to update
            if current_time - last_temp_update >= UPDATE_INTERVAL:
                last_temp_update = current_time

                for rom in roms:
                    # สั่งให้เซ็นเซอร์แปลงค่าอุณหภูมิ
                    # Command sensor to convert temperature
                    ds.convert_temp()
                    sleep_ms(750)  # รอการแปลงค่า (Wait for conversion)

                    # อ่านค่าอุณหภูมิ (Read temperature)
                    temp = ds.read_temp(rom)
                    temp_str = "{:.2f} C".format(temp)

                    # แสดงใน console (Display in console)
                    print(f"อุณหภูมิ (Temperature): {temp_str}")

                    # ลบค่าเดิมบนจอโดยวาดพื้นหลังสีดำ
                    # Clear old value by drawing black background
                    display.fill_rectangle(90, 70, 140, 30, BLACK)

                    # แสดงค่าใหม่บนจอ (Display new value on screen)
                    display.draw_text(100, 70, temp_str, arcadepix, GREEN)

    except KeyboardInterrupt:
        print("\nหยุดโปรแกรม (Program stopped)")

    finally:
        # ล้างจอ (Clear display)
        display.clear()
        print("ปิดจอแล้ว (Display cleared)")

# ==============================================================================
# 01_readTemp.py - การอ่านค่าอุณหภูมิจาก DS18B20 (Reading Temperature from DS18B20)
# ==============================================================================
# โปรแกรมนี้สาธิตการอ่านค่าอุณหภูมิจากเซ็นเซอร์ DS18B20 ผ่านโปรโตคอล OneWire
# This program demonstrates reading temperature from DS18B20 sensor via OneWire protocol
# ==============================================================================

import time
import machine
import onewire
import ds18x20

# กำหนดขา GPIO16 สำหรับเซ็นเซอร์ DS18B20 (OneWire protocol)
# Set GPIO16 for DS18B20 sensor (OneWire protocol)
dat = machine.Pin(16)

# สร้าง OneWire bus และ DS18X20 object
# Create OneWire bus and DS18X20 object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# สแกนหาเซ็นเซอร์ DS18B20 ที่เชื่อมต่ออยู่
# Scan for connected DS18B20 sensors
sensors = ds.scan()

# ตรวจสอบว่าพบเซ็นเซอร์หรือไม่
# Check if sensors are found
if not sensors:
    print("ไม่พบเซ็นเซอร์ DS18B20 (DS18B20 sensor not found)")
    print("กรุณาตรวจสอบการเชื่อมต่อ (Please check the connection)")
else:
    print(f"พบเซ็นเซอร์ DS18B20 จำนวน {len(sensors)} ตัว")
    print(f"Found {len(sensors)} DS18B20 sensor(s)")
    print("=" * 40)

    # สั่งให้เซ็นเซอร์แปลงค่าอุณหภูมิ
    # Command sensor to convert temperature
    ds.convert_temp()

    # รอ 750ms สำหรับการแปลงค่า (ความละเอียด 12-bit)
    # Wait 750ms for conversion (12-bit resolution)
    time.sleep_ms(750)

    # อ่านและแสดงค่าอุณหภูมิจากแต่ละเซ็นเซอร์
    # Read and display temperature from each sensor
    for i, sensor in enumerate(sensors):
        temp = ds.read_temp(sensor)
        print(f"เซ็นเซอร์ {i+1} (Sensor {i+1}): {temp:.2f} °C")

    print("=" * 40)
    print("เสร็จสิ้น (Done)")

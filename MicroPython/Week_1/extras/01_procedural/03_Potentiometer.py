# ==============================================================================
# 03_Potentiometer.py - การอ่านค่า ADC จาก Potentiometer
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ ADC เพื่ออ่านค่าแรงดันไฟฟ้าจาก Potentiometer
# This program demonstrates using ADC to read voltage from Potentiometer
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

import machine
import time

# กำหนดขา ADC สำหรับ Potentiometer ที่ GPIO32
# Set ADC pin for Potentiometer at GPIO32
# หมายเหตุ: GPIO32 และ GPIO33 เป็นขา Potentiometer มาตรฐานของ TitraLab
# Note: GPIO32 and GPIO33 are standard Potentiometer pins on TitraLab
adc = machine.ADC(machine.Pin(32))

# ตั้งค่าความละเอียด ADC เป็น 12-bit (0-4095)
# Set ADC resolution to 12-bit (0-4095)
adc.width(machine.ADC.WIDTH_12BIT)

# ตั้งค่า attenuation เป็น 11dB เพื่ออ่านแรงดัน 0-3.3V
# Set attenuation to 11dB to read voltage 0-3.3V
adc.atten(machine.ADC.ATTN_11DB)

print("เริ่มอ่านค่า Potentiometer - กด Ctrl+C เพื่อหยุด")
print("Start reading Potentiometer - Press Ctrl+C to stop")
print("=" * 50)

try:
    while True:
        # อ่านค่า ADC (Read ADC value)
        pot_value = adc.read()

        # แปลงค่า ADC เป็นแรงดันไฟฟ้า (Convert ADC to voltage)
        voltage = (pot_value / 4095) * 3.3

        # แสดงค่า (Display values)
        print(f"ค่า ADC (ADC Value): {pot_value:4d} | แรงดัน (Voltage): {voltage:.2f} V")

        # หน่วงเวลา 1 วินาที (Delay 1 second)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

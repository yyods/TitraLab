from machine import ADC, Pin
from time import ticks_ms

PH_PIN = 25  # กำหนดขาที่เชื่อมต่อกับแอนะล็อก

# สร้างอ็อบเจกต์ ADC สำหรับอ่านค่าแอนะล็อก
ph_sensor = ADC(Pin(PH_PIN))

lastTime = 0

while True:
    current_time = ticks_ms()
    
    if current_time - lastTime > 1000:
        lastTime = current_time

        # อ่านค่าแอนะล็อกและแปลงเป็นโวลต์
        analog_value = ph_sensor.read()
        voltage = (analog_value / 4095.0) * 3000.0
        
        acidVoltage = 0  # กำหนดค่า voltage สำหรับกรด
        neutralVoltage = 1500.0  # กำหนดค่า voltage สำหรับกลาง
        
        slope = (7.0 - 4.0) / ((neutralVoltage - 1500.0) / 3.0 - (acidVoltage - 1500.0) / 3.0)
        intercept = 7.0 - slope * (neutralVoltage - 1500.0) / 3.0
        phValue = slope * (voltage - 1500.0) / 3.0 + intercept
        phValue = round(phValue, 2)

        print(phValue)

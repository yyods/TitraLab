from machine import ADC, Pin
from time import ticks_ms

# กำหนดขาที่เชื่อมต่อกับ ADC
analog_pin = 25

# สร้างอ็อบเจกต์ ADC
adc = ADC(Pin(analog_pin))

# กำหนดค่าแอตเทนชันสำหรับแอนะล็อก
adc.atten(ADC.ATTN_11DB)
lastTime = 0

while True:
    current_time = ticks_ms()
    
    if current_time - lastTime > 3000:
        lastTime = current_time
        
        # อ่านค่าแอนะล็อก
        analog_value = adc.read()

        # แปลงค่าแอนะล็อกเป็นโวลต์ (ตั้งค่าเสียเป็น 12 บิต)
        voltage = (analog_value / 4095.0) * 3300  # หากใช้แรงดัน 3.3 โวลต์

        print("Voltage: {:.2f} V".format(voltage))

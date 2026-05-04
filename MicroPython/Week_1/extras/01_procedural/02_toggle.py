# ==============================================================================
# 02_toggle.py - การตรวจจับการกดปุ่มแบบ Toggle (Button Toggle Detection)
# ==============================================================================
# โปรแกรมนี้สาธิตการตรวจจับการเปลี่ยนแปลงสถานะปุ่มกด
# This program demonstrates detecting button state changes
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

import machine
import time

# กำหนดขา GPIO35 เป็น INPUT สำหรับปุ่มกด 2
# Set GPIO35 as INPUT for button 2
#
# หมายเหตุสำคัญเรื่องขา GPIO34, 35, 39 (Important note about GPIO34, 35, 39):
# - เป็นขา input-only ไม่มี internal pull-up/pull-down
#   (input-only pins, no internal pull-up/pull-down available)
# - TitraLab ใช้ external pull-down resistor ดังนั้น:
#   (TitraLab uses external pull-down resistor, therefore:)
#   - ไม่กดปุ่ม (not pressed) = 0 (ต่อลงกราวด์ผ่าน pull-down)
#   - กดปุ่ม (pressed) = 1 (ต่อกับ VCC 3.3V)
#
button = machine.Pin(35, machine.Pin.IN)

# ตัวแปรเก็บสถานะปุ่มกดก่อนหน้า (Variable to store previous button state)
button_pressed = False

print("เริ่มตรวจจับปุ่มกด - กด Ctrl+C เพื่อหยุด")
print("Start button detection - Press Ctrl+C to stop")

try:
    while True:
        # ตรวจจับการกดปุ่ม (Detect button press)
        if button.value() == 1 and not button_pressed:
            print("เปิด (ON)")
            button_pressed = True

        # ตรวจจับการปล่อยปุ่ม (Detect button release)
        elif button.value() == 0 and button_pressed:
            print("ปิด (OFF)")
            button_pressed = False

        # หน่วงเวลาเล็กน้อยเพื่อลด CPU usage และ debounce
        # Small delay to reduce CPU usage and debounce
        time.sleep_ms(10)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

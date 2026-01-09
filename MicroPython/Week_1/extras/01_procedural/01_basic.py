# ==============================================================================
# 01_basic.py - การอ่านค่าปุ่มกดพื้นฐาน (Basic Button Read)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ GPIO เป็น INPUT เพื่ออ่านสถานะปุ่มกด
# This program demonstrates using GPIO as INPUT to read button state
# ==============================================================================

import machine

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

# อ่านและแสดงค่าปุ่มกด (Read and display button value)
# ค่า 1 = กด (pressed), ค่า 0 = ไม่กด (not pressed) - ใช้ external pull-down
value = button.value()
print(f"ค่าปุ่มกด (Button value): {value}")

if value == 1:
    print("สถานะ: กดปุ่มอยู่ (Status: Button pressed)")
else:
    print("สถานะ: ไม่ได้กดปุ่ม (Status: Button not pressed)")

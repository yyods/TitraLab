# ==============================================================================
# 01_basic.py - การอ่านค่าปุ่มกดพื้นฐาน (Basic Button Read)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ GPIO เป็น INPUT เพื่ออ่านสถานะปุ่มกด
# This program demonstrates using GPIO as INPUT to read button state
# ==============================================================================

import machine

# กำหนดขา GPIO35 เป็น INPUT สำหรับปุ่มกด 2
# Set GPIO35 as INPUT for button 2
# หมายเหตุ: GPIO34, 35, 39 เป็นขา input-only ไม่มี internal pull-up
# Note: GPIO34, 35, 39 are input-only pins without internal pull-up
button = machine.Pin(35, machine.Pin.IN)

# อ่านและแสดงค่าปุ่มกด (Read and display button value)
# ค่า 0 = กด (pressed), ค่า 1 = ไม่กด (not pressed)
value = button.value()
print(f"ค่าปุ่มกด (Button value): {value}")

if value == 0:
    print("สถานะ: กดปุ่มอยู่ (Status: Button pressed)")
else:
    print("สถานะ: ไม่ได้กดปุ่ม (Status: Button not pressed)")

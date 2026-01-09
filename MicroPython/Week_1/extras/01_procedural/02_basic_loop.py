# ==============================================================================
# 02_basic_loop.py - การกะพริบ LED แบบวนซ้ำ (LED Blink with Loop)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ for loop เพื่อกะพริบ LED หลายครั้ง
# This program demonstrates using for loop to blink LED multiple times
# ==============================================================================

import machine
import time

# กำหนดขา GPIO2 เป็น OUTPUT สำหรับ LED สีแดง
# Set GPIO2 as OUTPUT for red LED
led_red = machine.Pin(2, machine.Pin.OUT)

# วนซ้ำ 10 รอบ (Loop 10 times)
for i in range(10):
    # เปิด LED (Turn LED on)
    led_red.on()
    time.sleep(0.5)

    # ปิด LED (Turn LED off)
    led_red.off()
    time.sleep(0.5)

    # แสดงรอบที่กำลังทำงาน (Show current iteration)
    print(f"รอบที่ (Round) {i + 1}")

print("เสร็จสิ้น (Done)")

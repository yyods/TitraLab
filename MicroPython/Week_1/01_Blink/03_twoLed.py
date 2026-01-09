# ==============================================================================
# 03_twoLed.py - การควบคุม LED สองดวง (Two LED Control)
# ==============================================================================
# โปรแกรมนี้สาธิตการควบคุม LED สองดวงสลับกัน
# This program demonstrates controlling two LEDs alternately
# ==============================================================================

import machine
import time

# กำหนดขา GPIO สำหรับ LED ทั้งสองดวง
# Set GPIO pins for both LEDs
led_red = machine.Pin(2, machine.Pin.OUT)    # LED สีแดง (Red LED) - GPIO2
led_green = machine.Pin(4, machine.Pin.OUT)  # LED สีเขียว (Green LED) - GPIO4

# วนซ้ำ 10 รอบ (Loop 10 times)
for i in range(10):
    # เปิด LED แดง, ปิด LED เขียว (Red ON, Green OFF)
    led_red.on()
    led_green.off()
    time.sleep(0.5)

    # ปิด LED แดง, เปิด LED เขียว (Red OFF, Green ON)
    led_red.off()
    led_green.on()
    time.sleep(0.5)

    print(f"รอบที่ (Round) {i + 1}")

# ปิด LED ทั้งสองดวงเมื่อจบโปรแกรม (Turn off both LEDs when done)
led_red.off()
led_green.off()
print("เสร็จสิ้น (Done)")

# ==============================================================================
# 01_basic.py - การกะพริบ LED พื้นฐาน (Basic LED Blink)
# ==============================================================================
# โปรแกรมนี้สาธิตการควบคุม GPIO เป็น OUTPUT เพื่อเปิด-ปิด LED
# This program demonstrates GPIO OUTPUT control to turn LED on and off
# ==============================================================================

import machine
import time

# กำหนดขา GPIO2 เป็น OUTPUT สำหรับ LED สีแดง
# Set GPIO2 as OUTPUT for red LED
led_red = machine.Pin(2, machine.Pin.OUT)

# เปิด LED (Turn LED on)
led_red.on()

# หน่วงเวลา 0.5 วินาที (Delay 0.5 seconds)
time.sleep(0.5)

# ปิด LED (Turn LED off)
led_red.off()

print("เสร็จสิ้น (Done)")

# ==============================================================================
# 04_twoLed_infiniteLoop.py - การควบคุม LED แบบไม่สิ้นสุด (Infinite LED Control)
# ==============================================================================
# โปรแกรมนี้สาธิตการควบคุม LED สองดวงสลับกันแบบไม่มีที่สิ้นสุด
# This program demonstrates controlling two LEDs alternately in an infinite loop
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

import machine
import time

# กำหนดขา GPIO สำหรับ LED ทั้งสองดวง
# Set GPIO pins for both LEDs
led_red = machine.Pin(2, machine.Pin.OUT)    # LED สีแดง (Red LED) - GPIO2
led_green = machine.Pin(4, machine.Pin.OUT)  # LED สีเขียว (Green LED) - GPIO4

print("เริ่มโปรแกรม - กด Ctrl+C เพื่อหยุด (Starting - Press Ctrl+C to stop)")

try:
    while True:
        # เปิด LED แดง, ปิด LED เขียว (Red ON, Green OFF)
        led_red.on()
        led_green.off()
        time.sleep(0.5)

        # ปิด LED แดง, เปิด LED เขียว (Red OFF, Green ON)
        led_red.off()
        led_green.on()
        time.sleep(0.5)

except KeyboardInterrupt:
    # หยุดโปรแกรมเมื่อกด Ctrl+C (Stop program when Ctrl+C is pressed)
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ปิด LED ทั้งสองดวงเมื่อจบโปรแกรม (Turn off both LEDs when done)
    led_red.off()
    led_green.off()
    print("ปิด LED ทั้งหมดแล้ว (All LEDs turned off)")

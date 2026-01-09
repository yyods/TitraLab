# ==============================================================================
# 04_PWM_OUT.py - การควบคุม LED ด้วย PWM (LED Control with PWM)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ PWM เพื่อควบคุมความสว่างของ LED
# This program demonstrates using PWM to control LED brightness
# PWM = Pulse Width Modulation (การมอดูเลตความกว้างพัลส์)
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

import machine
import time

# กำหนดขา PWM สำหรับ LED สีแดงที่ GPIO2
# Set PWM pin for red LED at GPIO2
led_pin = 2

# สร้าง PWM object ที่ความถี่ 500 Hz
# Create PWM object at 500 Hz frequency
led = machine.PWM(machine.Pin(led_pin), freq=500)

def fade_in(led, max_duty=1023, step=10, delay=0.01):
    """
    ค่อยๆ เพิ่มความสว่าง LED (Gradually increase LED brightness)
    max_duty: ค่า duty cycle สูงสุด (maximum duty cycle value)
    step: ขนาดการเพิ่มแต่ละครั้ง (increment size)
    delay: เวลาหน่วงระหว่างแต่ละ step (delay between steps)
    """
    for duty in range(0, max_duty + 1, step):
        led.duty(duty)
        time.sleep(delay)

def fade_out(led, max_duty=1023, step=10, delay=0.01):
    """
    ค่อยๆ ลดความสว่าง LED (Gradually decrease LED brightness)
    """
    for duty in range(max_duty, -1, -step):
        led.duty(duty)
        time.sleep(delay)

print("เริ่ม PWM Fade - กด Ctrl+C เพื่อหยุด")
print("Start PWM Fade - Press Ctrl+C to stop")

try:
    while True:
        # เพิ่มความสว่าง (Fade in)
        fade_in(led)
        # ลดความสว่าง (Fade out)
        fade_out(led)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ปิด LED และคืนทรัพยากร PWM (Turn off LED and release PWM resources)
    led.duty(0)
    led.deinit()
    print("ปิด PWM แล้ว (PWM released)")

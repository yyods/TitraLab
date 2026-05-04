# ==============================================================================
# 01_pwm_led_brightness.py - PWM Basics: LED Brightness Control
# ==============================================================================
# พื้นฐาน PWM: การควบคุมความสว่างของ LED ด้วย Duty Cycle
# PWM Basics: Controlling LED brightness using Duty Cycle
#
# PWM คืออะไร? (What is PWM?)
#   PWM (Pulse Width Modulation) คือการจำลองสัญญาณแอนะล็อกจากดิจิทัล
#   PWM simulates analog output from digital signals
#
#   ใช้การเปิด-ปิดอย่างรวดเร็ว เพื่อควบคุม "ค่าเฉลี่ย" ของแรงดัน
#   Uses rapid on-off switching to control "average" voltage
#
# Duty Cycle คืออะไร? (What is Duty Cycle?)
#   Duty Cycle = สัดส่วนเวลาที่สัญญาณเป็น HIGH (เปิด)
#   Duty Cycle = proportion of time the signal is HIGH (on)
#
#   ESP32 ใช้ค่า 0-1023 (10-bit resolution):
#   - 0    = 0%   = ปิดตลอด (always off)
#   - 512  = 50%  = เปิดครึ่งเวลา (half on, half off)
#   - 1023 = 100% = เปิดตลอด (always on)
#
# แผนภาพ Duty Cycle (Duty Cycle Diagram):
#
#   0% Duty (duty=0)       50% Duty (duty=512)    100% Duty (duty=1023)
#   ____________________   _____     _____        ____________________
#                         |     |___|     |___
#   LED: ปิด (Off)        LED: หรี่ (Dim)         LED: สว่างสุด (Bright)
#
# Chemistry Preview (เชื่อมโยงเคมี):
#   นี่คือหลักการเดียวกับที่ใช้ควบคุมความเร็วปั๊มในสัปดาห์ที่ 2!
#   This is the same principle used to control pump speed in Week 2!
#   - duty ต่ำ = ปั๊มช้า (slow pump)
#   - duty สูง = ปั๊มเร็ว (fast pump)
#
# ==============================================================================

from machine import Pin, PWM
import time

# นำเข้าค่าคงที่จาก pins.py (Import constants from pins.py)
# LED_RED = 2
LED_RED = 2

# ==============================================================================
# ส่วนที่ 1: สร้าง PWM Object (Create PWM Object)
# ==============================================================================

print("=" * 50)
print("PWM LED Brightness Control Demo")
print("สาธิตการควบคุมความสว่าง LED ด้วย PWM")
print("=" * 50)

# สร้าง PWM บนขา LED แดง (Create PWM on red LED pin)
# หมายเหตุ: PWM แปลง Pin จาก digital เป็น analog-like output
# Note: PWM converts Pin from digital to analog-like output
led_pwm = PWM(Pin(LED_RED))

# กำหนดความถี่ PWM (Set PWM frequency)
# 1000 Hz = เปิด-ปิด 1000 ครั้งต่อวินาที (1000 cycles per second)
# ความถี่สูงพอที่ตาจะไม่เห็นการกระพริบ
# High enough frequency so eyes don't see flickering
led_pwm.freq(1000)

print(f"PWM Frequency: {led_pwm.freq()} Hz")
print()

# ==============================================================================
# ส่วนที่ 2: ทดลองค่า Duty Cycle ต่างๆ (Test Different Duty Cycles)
# ==============================================================================

try:
    # ทดสอบ 5 ระดับความสว่าง (Test 5 brightness levels)
    brightness_levels = [
        (0,    "0%    - ปิด (Off)"),
        (256,  "25%   - หรี่มาก (Very dim)"),
        (512,  "50%   - ปานกลาง (Medium)"),
        (768,  "75%   - สว่าง (Bright)"),
        (1023, "100%  - สว่างสุด (Maximum)")
    ]

    print("ทดสอบระดับความสว่าง (Testing brightness levels):")
    print("-" * 50)

    for duty_value, description in brightness_levels:
        # ตั้งค่า duty cycle (Set duty cycle)
        led_pwm.duty(duty_value)

        # แสดงข้อมูล (Display info)
        percentage = (duty_value / 1023) * 100
        print(f"Duty = {duty_value:4d} ({percentage:5.1f}%) - {description}")

        # รอให้สังเกตความสว่าง (Wait to observe brightness)
        time.sleep(2)

    print("-" * 50)
    print()

    # ==============================================================================
    # ส่วนที่ 3: ปรับความสว่างแบบต่อเนื่อง (Continuous Brightness Adjustment)
    # ==============================================================================

    print("ปรับความสว่างต่อเนื่อง 0 -> 100% (Ramping up 0 -> 100%)")

    # เพิ่มความสว่างทีละน้อย (Gradually increase brightness)
    for duty in range(0, 1024, 64):  # เพิ่มทีละ 64 (step by 64)
        led_pwm.duty(duty)
        percentage = (duty / 1023) * 100
        # แสดง progress bar แบบง่าย (Simple progress bar)
        bar = "#" * int(percentage / 5)
        print(f"[{bar:<20}] {percentage:5.1f}%", end="\r")
        time.sleep(0.2)

    led_pwm.duty(1023)  # สว่างสุด (Maximum)
    print(f"[{'#' * 20}] 100.0% - สว่างสุด!")
    time.sleep(1)

    print("\nปรับความสว่างต่อเนื่อง 100% -> 0 (Ramping down 100% -> 0)")

    # ลดความสว่างทีละน้อย (Gradually decrease brightness)
    for duty in range(1023, -1, -64):  # ลดทีละ 64 (step by -64)
        led_pwm.duty(duty)
        percentage = (duty / 1023) * 100
        bar = "#" * int(percentage / 5)
        print(f"[{bar:<20}] {percentage:5.1f}%", end="\r")
        time.sleep(0.2)

    led_pwm.duty(0)  # ปิด (Off)
    print(f"[{' ' * 20}]   0.0% - ปิดแล้ว!")

    print()
    print("=" * 50)
    print("สรุป (Summary):")
    print("  - PWM ใช้ duty cycle ควบคุมค่าเฉลี่ยของสัญญาณ")
    print("  - duty=0: ปิด, duty=512: 50%, duty=1023: 100%")
    print("  - Week 2: ใช้หลักการนี้ควบคุมความเร็วปั๊ม!")
    print("=" * 50)

except KeyboardInterrupt:
    # ผู้ใช้กด Ctrl+C (User pressed Ctrl+C)
    print("\n\nหยุดโปรแกรม (Program stopped by user)")

finally:
    # สำคัญมาก! ต้องปิด PWM เสมอเมื่อจบโปรแกรม
    # IMPORTANT! Always cleanup PWM when program ends
    led_pwm.duty(0)     # ปิด LED ก่อน (Turn off LED first)
    led_pwm.deinit()    # คืนทรัพยากร PWM (Release PWM resources)
    print("PWM cleanup completed / ทำความสะอาด PWM เรียบร้อย")

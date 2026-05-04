# ==============================================================================
# 02_pwm_led_fade.py - Smooth LED Fading Effect
# ==============================================================================
# เอฟเฟกต์ LED ค่อยๆ สว่าง-ดับ อย่างนุ่มนวล
# Smooth LED fade in and fade out effect
#
# หลักการ (Principle):
#   เปลี่ยนค่า duty cycle ทีละน้อยอย่างต่อเนื่อง
#   Change duty cycle gradually and continuously
#
# ความสัมพันธ์ระหว่าง Duty Cycle กับความสว่างที่ตาเห็น:
# Relationship between Duty Cycle and Perceived Brightness:
#
#   ตามันุษย์ไม่รับรู้แสงแบบเชิงเส้น (linear)
#   Human eyes don't perceive light linearly
#
#   ถ้าเพิ่ม duty แบบเส้นตรง:
#   If we increase duty linearly:
#   - 0->50%: ดูเหมือนสว่างขึ้นเร็วมาก (seems to brighten quickly)
#   - 50->100%: ดูเหมือนสว่างเพิ่มขึ้นน้อย (seems to barely change)
#
#   แผนภาพ (Diagram):
#
#   Perceived    |          .----- Linear (เชิงเส้น)
#   Brightness   |        .'
#   ความสว่าง    |      .'
#   ที่รับรู้    |    .'
#                | .'
#                |______________ Duty Cycle
#                0%            100%
#
#   เพื่อให้ดูนุ่มนวล อาจใช้ exponential curve แต่ในตัวอย่างนี้ใช้ linear ก่อน
#   For smoother effect, we could use exponential, but this example uses linear
#
# Chemistry Context (บริบทเคมี):
#   - การเปลี่ยนความเร็วปั๊มอย่างนุ่มนวลช่วยควบคุม titration ได้ดีขึ้น
#   - Smooth pump speed changes help control titration better
#   - เมื่อใกล้จุดสมมูล ลดความเร็วปั๊มให้ช้าลงทีละน้อย
#   - When approaching equivalence point, gradually slow down the pump
#
# ==============================================================================

from machine import Pin, PWM
import time

# GPIO Pin สำหรับ LED แดง (GPIO Pin for Red LED)
LED_RED = 2

# ==============================================================================
# ส่วนที่ 1: ตั้งค่า PWM (PWM Setup)
# ==============================================================================

print("=" * 50)
print("PWM LED Fade Effect Demo")
print("สาธิตเอฟเฟกต์ LED Fade (ค่อยๆ สว่าง-ดับ)")
print("=" * 50)

# สร้าง PWM object (Create PWM object)
led_pwm = PWM(Pin(LED_RED))
led_pwm.freq(1000)  # ความถี่ 1000 Hz (1000 Hz frequency)

print(f"LED Pin: GPIO{LED_RED}")
print(f"PWM Frequency: {led_pwm.freq()} Hz")
print()

# ==============================================================================
# ส่วนที่ 2: ฟังก์ชัน Fade (Fade Functions)
# ==============================================================================

def fade_in(pwm, duration_ms=1000, steps=50):
    """
    ค่อยๆ สว่างขึ้น (Gradually brighten)

    Args:
        pwm: PWM object
        duration_ms (int): ระยะเวลาทั้งหมด (total duration in ms)
        steps (int): จำนวนขั้นตอน (number of steps)
    """
    step_delay = duration_ms / steps
    duty_step = 1023 / steps

    for i in range(steps + 1):
        duty = int(i * duty_step)
        pwm.duty(duty)
        time.sleep_ms(int(step_delay))


def fade_out(pwm, duration_ms=1000, steps=50):
    """
    ค่อยๆ ดับลง (Gradually dim)

    Args:
        pwm: PWM object
        duration_ms (int): ระยะเวลาทั้งหมด (total duration in ms)
        steps (int): จำนวนขั้นตอน (number of steps)
    """
    step_delay = duration_ms / steps
    duty_step = 1023 / steps

    for i in range(steps, -1, -1):
        duty = int(i * duty_step)
        pwm.duty(duty)
        time.sleep_ms(int(step_delay))


def breathe(pwm, cycles=3, period_ms=2000):
    """
    เอฟเฟกต์หายใจ - สว่างขึ้นแล้วดับลงสลับกัน
    Breathing effect - fade in then fade out repeatedly

    Args:
        pwm: PWM object
        cycles (int): จำนวนรอบ (number of cycles)
        period_ms (int): ระยะเวลาต่อรอบ (period per cycle in ms)
    """
    half_period = period_ms // 2

    for cycle in range(cycles):
        print(f"  Breath {cycle + 1}/{cycles}")
        fade_in(pwm, half_period)
        fade_out(pwm, half_period)


# ==============================================================================
# ส่วนที่ 3: การทดสอบ (Testing)
# ==============================================================================

try:
    # ทดสอบ Fade In (Test Fade In)
    print("--- ทดสอบ Fade In (Testing Fade In) ---")
    print("LED จะค่อยๆ สว่างขึ้น (LED will gradually brighten)")
    fade_in(led_pwm, duration_ms=2000, steps=100)
    print("Fade In เสร็จสิ้น (Fade In complete)")
    time.sleep(1)

    # ทดสอบ Fade Out (Test Fade Out)
    print("\n--- ทดสอบ Fade Out (Testing Fade Out) ---")
    print("LED จะค่อยๆ ดับลง (LED will gradually dim)")
    fade_out(led_pwm, duration_ms=2000, steps=100)
    print("Fade Out เสร็จสิ้น (Fade Out complete)")
    time.sleep(1)

    # ทดสอบ Breathing Effect (Test Breathing Effect)
    print("\n--- ทดสอบ Breathing Effect (Testing Breathing Effect) ---")
    print("เอฟเฟกต์หายใจ 5 รอบ (5 breathing cycles)")
    breathe(led_pwm, cycles=5, period_ms=2000)
    print("Breathing effect เสร็จสิ้น (complete)")
    time.sleep(0.5)

    # สาธิต: ความเร็ว Fade ต่างกัน (Demo: Different Fade Speeds)
    print("\n--- เปรียบเทียบความเร็ว Fade (Comparing Fade Speeds) ---")

    speeds = [
        (500,  "เร็ว (Fast)"),
        (1500, "ปานกลาง (Medium)"),
        (3000, "ช้า (Slow)")
    ]

    for duration, description in speeds:
        print(f"\n  Fade speed: {description} ({duration} ms)")
        fade_in(led_pwm, duration_ms=duration, steps=50)
        fade_out(led_pwm, duration_ms=duration, steps=50)

    print("\n" + "=" * 50)
    print("สรุป (Summary):")
    print("  - Fade effect = เปลี่ยน duty cycle ทีละน้อย")
    print("  - steps มาก = นุ่มนวลกว่า แต่ใช้เวลานานกว่า")
    print("  - Chemistry: ใช้หลักการนี้ควบคุมปั๊มแบบ smooth")
    print("=" * 50)

except KeyboardInterrupt:
    print("\n\nหยุดโปรแกรม (Program stopped by user)")

finally:
    # ทำความสะอาด PWM (Cleanup PWM)
    # สำคัญ: ต้องทำเสมอเมื่อจบการใช้งาน PWM
    # Important: Always do this when done with PWM
    led_pwm.duty(0)     # ปิด LED (Turn off LED)
    led_pwm.deinit()    # คืนทรัพยากร (Release resources)
    print("PWM cleanup completed / ทำความสะอาด PWM เรียบร้อย")

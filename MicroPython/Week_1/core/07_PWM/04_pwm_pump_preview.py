# ==============================================================================
# 04_pwm_pump_preview.py - Pump Control Preview for Week 2
# ==============================================================================
# ตัวอย่างการควบคุมปั๊มอย่างง่าย เตรียมความพร้อมสำหรับสัปดาห์ที่ 2
# Simple pump control preview, preparing for Week 2
#
# ข้อควรระวังด้านความปลอดภัย (Safety Warning):
#   - ก่อนรันโค้ดนี้ ตรวจสอบว่าท่อปั๊มต่ออยู่กับภาชนะที่เหมาะสม
#   - Before running this code, ensure pump tubes are connected to appropriate containers
#   - ระวังการหกของสารเคมี (Be careful of chemical spills)
#
# PWM กับปั๊ม (PWM with Pump):
#
#   Duty Cycle ควบคุมความเร็วปั๊ม (Duty cycle controls pump speed):
#
#   duty = 0     -> ปั๊มหยุด (Pump stopped)
#   duty = 256   -> ปั๊มช้า ~25% (Slow ~25%)
#   duty = 512   -> ปั๊มกลาง ~50% (Medium ~50%)
#   duty = 768   -> ปั๊มเร็ว ~75% (Fast ~75%)
#   duty = 1023  -> ปั๊มเร็วสุด (Maximum speed)
#
#   แผนภาพความสัมพันธ์ (Relationship Diagram):
#
#   Pump Speed    |                    /
#   ความเร็วปั๊ม  |                  /
#                 |                /
#                 |              /
#                 |            /
#                 |          /
#                 |        /
#                 |      /
#                 |    /
#                 |  /
#                 |/__________________ Duty Cycle
#                 0                  1023
#
# Chemistry Application (การประยุกต์ใช้ทางเคมี):
#
#   ในการไทเทรชัน (In titration):
#   - เริ่มต้น: ใช้ duty สูง (เร็ว) เพราะ pH เปลี่ยนช้า
#   - Start: Use high duty (fast) because pH changes slowly
#
#   - ใกล้จุดสมมูล: ลด duty ลง (ช้า) เพื่อควบคุมปริมาณที่แม่นยำ
#   - Near equivalence: Lower duty (slow) for precise volume control
#
#   Week 2 จะเรียนรู้ (You will learn in Week 2):
#   - การสอบเทียบปั๊ม (Pump calibration)
#   - การคำนวณ mL/min จาก duty cycle
#   - การควบคุมปั๊มอัตโนมัติตามค่า pH
#
# ==============================================================================

from machine import Pin, PWM
import time

# GPIO Pins จาก pins.py (GPIO Pins from pins.py)
PUMP_PIN = 21     # ปั๊ม (Pump)
LED_GREEN = 4     # LED สีเขียว แสดงสถานะปั๊มทำงาน (Green LED shows pump running)
LED_RED = 2       # LED สีแดง แสดงสถานะปั๊มหยุด (Red LED shows pump stopped)

# ==============================================================================
# ส่วนที่ 1: ตั้งค่า (Setup)
# ==============================================================================

print("=" * 50)
print("PWM Pump Control Preview")
print("ตัวอย่างการควบคุมปั๊มด้วย PWM")
print("=" * 50)
print()
print("!!! ข้อควรระวัง / WARNING !!!")
print("ตรวจสอบว่าท่อปั๊มต่ออยู่กับภาชนะที่เหมาะสม")
print("Ensure pump tubes are connected to appropriate containers")
print()

# สร้าง PWM สำหรับปั๊ม (Create PWM for pump)
pump_pwm = PWM(Pin(PUMP_PIN))
pump_pwm.freq(1000)  # ความถี่มาตรฐานสำหรับปั๊ม (Standard frequency for pump)
pump_pwm.duty(0)     # เริ่มต้นปิดปั๊ม (Start with pump off)

# LED สำหรับแสดงสถานะ (Status LEDs)
led_green = Pin(LED_GREEN, Pin.OUT)
led_red = Pin(LED_RED, Pin.OUT)
led_red.on()     # เริ่มต้น: LED แดงติด = ปั๊มหยุด (Start: Red LED on = pump stopped)
led_green.off()

print(f"Pump Pin: GPIO{PUMP_PIN}")
print(f"PWM Frequency: {pump_pwm.freq()} Hz")
print()

# ==============================================================================
# ส่วนที่ 2: ฟังก์ชันควบคุมปั๊ม (Pump Control Functions)
# ==============================================================================

def pump_on(pwm, duty=512):
    """
    เปิดปั๊มที่ความเร็วที่กำหนด (Turn on pump at specified speed)

    Args:
        pwm: PWM object ของปั๊ม
        duty (int): ค่า duty cycle 0-1023 (default 512 = 50%)
    """
    pwm.duty(duty)
    led_green.on()
    led_red.off()
    percentage = (duty / 1023) * 100
    print(f"ปั๊มเปิด (Pump ON): duty={duty} ({percentage:.1f}%)")


def pump_off(pwm):
    """
    ปิดปั๊ม (Turn off pump)

    Args:
        pwm: PWM object ของปั๊ม
    """
    pwm.duty(0)
    led_green.off()
    led_red.on()
    print("ปั๊มปิด (Pump OFF)")


def pump_set_speed(pwm, percentage):
    """
    ตั้งความเร็วปั๊มเป็นเปอร์เซ็นต์ (Set pump speed as percentage)

    Args:
        pwm: PWM object ของปั๊ม
        percentage (float): ความเร็ว 0-100%
    """
    # แปลง % เป็น duty cycle (Convert % to duty cycle)
    # 0% = 0, 100% = 1023
    duty = int((percentage / 100) * 1023)
    duty = max(0, min(1023, duty))  # จำกัดค่า 0-1023 (clamp to 0-1023)

    pwm.duty(duty)
    if duty > 0:
        led_green.on()
        led_red.off()
    else:
        led_green.off()
        led_red.on()

    print(f"ความเร็วปั๊ม (Pump speed): {percentage:.1f}% (duty={duty})")


# ==============================================================================
# ส่วนที่ 3: การทดสอบ (Testing)
# ==============================================================================

try:
    input("กด Enter เพื่อเริ่มทดสอบปั๊ม (Press Enter to start pump test)...")
    print()

    # ทดสอบ 1: เปิด-ปิดปั๊ม (Test 1: On/Off)
    print("-" * 50)
    print("ทดสอบที่ 1: เปิด-ปิดปั๊ม (Test 1: Pump On/Off)")
    print("-" * 50)

    pump_on(pump_pwm, duty=512)  # เปิดที่ 50%
    time.sleep(2)
    pump_off(pump_pwm)
    time.sleep(1)

    # ทดสอบ 2: ความเร็วต่างๆ (Test 2: Different Speeds)
    print()
    print("-" * 50)
    print("ทดสอบที่ 2: ความเร็วต่างๆ (Test 2: Different Speeds)")
    print("-" * 50)

    speeds = [25, 50, 75, 100]

    for speed in speeds:
        print(f"\nทดสอบความเร็ว {speed}% (Testing {speed}% speed)")
        pump_set_speed(pump_pwm, speed)
        time.sleep(2)

    pump_off(pump_pwm)
    time.sleep(1)

    # ทดสอบ 3: ค่อยๆ เพิ่มความเร็ว (Test 3: Gradual Speed Increase)
    print()
    print("-" * 50)
    print("ทดสอบที่ 3: ค่อยๆ เพิ่มความเร็ว (Test 3: Gradual Ramp Up)")
    print("-" * 50)

    print("เพิ่มความเร็วจาก 0% -> 100% (Ramping 0% -> 100%)")
    for speed in range(0, 101, 10):
        pump_set_speed(pump_pwm, speed)
        time.sleep(0.5)

    print()
    print("ลดความเร็วจาก 100% -> 0% (Ramping 100% -> 0%)")
    for speed in range(100, -1, -10):
        pump_set_speed(pump_pwm, speed)
        time.sleep(0.5)

    pump_off(pump_pwm)
    print()

    # ==============================================================================
    # ส่วนที่ 4: จำลองการไทเทรชัน (Simulated Titration Pattern)
    # ==============================================================================

    print("-" * 50)
    print("ทดสอบที่ 4: จำลองรูปแบบการไทเทรชัน")
    print("Test 4: Simulated Titration Pattern")
    print("-" * 50)
    print()
    print("  เริ่มต้น: เร็ว (ห่างจากจุดสมมูล)")
    print("  Start: Fast (far from equivalence point)")
    print()
    print("  ใกล้จุดสมมูล: ช้าลง (ควบคุมแม่นยำ)")
    print("  Near equivalence: Slower (precise control)")
    print()

    # Phase 1: ไกลจากจุดสมมูล - เร็ว (Far from endpoint - fast)
    print("Phase 1: ห่างจากจุดสมมูล - ความเร็ว 80%")
    pump_set_speed(pump_pwm, 80)
    time.sleep(3)

    # Phase 2: เข้าใกล้ - ปานกลาง (Approaching - medium)
    print("Phase 2: เข้าใกล้จุดสมมูล - ความเร็ว 50%")
    pump_set_speed(pump_pwm, 50)
    time.sleep(3)

    # Phase 3: ใกล้มาก - ช้า (Very close - slow)
    print("Phase 3: ใกล้จุดสมมูลมาก - ความเร็ว 25%")
    pump_set_speed(pump_pwm, 25)
    time.sleep(3)

    # Phase 4: ถึงจุดสมมูล - หยุด (Reached endpoint - stop)
    print("Phase 4: ถึงจุดสมมูล! - หยุดปั๊ม")
    pump_off(pump_pwm)

    print()
    print("=" * 50)
    print("สรุป: การควบคุมปั๊มด้วย PWM")
    print("Summary: PWM Pump Control")
    print("-" * 50)
    print()
    print("  1. ใช้ duty cycle ควบคุมความเร็ว")
    print("     Use duty cycle to control speed")
    print()
    print("  2. ความถี่ 1000 Hz เหมาะกับปั๊ม TitraLab")
    print("     1000 Hz frequency is suitable for TitraLab pump")
    print()
    print("  3. สำคัญ: เรียก pump_pwm.deinit() เมื่อจบ!")
    print("     Important: Call pump_pwm.deinit() when done!")
    print()
    print("  4. Week 2: เรียนรู้การสอบเทียบและควบคุมอัตโนมัติ")
    print("     Week 2: Learn calibration and automatic control")
    print()
    print("=" * 50)

except KeyboardInterrupt:
    print("\n\nหยุดโปรแกรม (Program stopped by user)")

finally:
    # ทำความสะอาดทรัพยากร (Cleanup resources)
    # สำคัญมาก! ต้องหยุดปั๊มและคืน PWM เสมอ
    # CRITICAL! Always stop pump and release PWM

    pump_pwm.duty(0)     # หยุดปั๊มก่อน (Stop pump first)
    pump_pwm.deinit()    # คืนทรัพยากร PWM (Release PWM resources)

    # ปิด LED ทั้งหมด (Turn off all LEDs)
    led_green.off()
    led_red.off()

    print()
    print("ปิดปั๊มและทำความสะอาด PWM เรียบร้อย")
    print("Pump stopped and PWM cleanup completed")

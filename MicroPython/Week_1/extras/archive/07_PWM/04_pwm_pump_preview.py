# ==============================================================================
# 04_pwm_pump_preview.py - ควบคุมปั๊มไทเทรชัน (Titration Pump Control)
# ==============================================================================
# โปรแกรมนี้สอนการควบคุมปั๊มด้วย PWM เพื่อเตรียมความพร้อมสำหรับ Week 3
# This program teaches pump control with PWM in preparation for Week 3
#
# นี่คือพื้นฐานการควบคุมปั๊มที่ใช้ใน Week 3
# This is the basis for pump control used in Week 3
#
# ==============================================================================
# ข้อควรระวังด้านความปลอดภัย!!! (SAFETY WARNINGS!!!)
# ==============================================================================
#
#   !!! อ่านก่อนรันโค้ด (READ BEFORE RUNNING CODE) !!!
#
#   1. ตรวจสอบท่อปั๊ม (Check pump tubes):
#      - ต่อท่อทางเข้ากับภาชนะที่มีน้ำหรือสารละลาย
#      - Connect inlet tube to container with water or solution
#      - ต่อท่อทางออกกับภาชนะรองรับที่เหมาะสม
#      - Connect outlet tube to appropriate receiving container
#
#   2. ระวังการหกของสารเคมี (Beware of chemical spills):
#      - วางภาชนะบนถาดรองรับ (Place containers on a tray)
#      - เตรียมกระดาษซับ (Have paper towels ready)
#
#   3. สารเคมีไทเทรชัน (Titration chemicals):
#      - NaOH เป็นสารกัดกร่อน สวมถุงมือ!
#      - NaOH is corrosive, wear gloves!
#      - หากสัมผัสผิวหนัง ล้างด้วยน้ำทันที
#      - If skin contact, wash with water immediately
#
#   4. ปุ่มหยุดฉุกเฉิน (Emergency stop):
#      - กด Ctrl+C เพื่อหยุดปั๊มทันที
#      - Press Ctrl+C to stop pump immediately
#      - โค้ดมี finally block ที่จะหยุดปั๊มเสมอ
#      - Code has finally block that always stops pump
#
# ==============================================================================
# ฮาร์ดแวร์ปั๊มบนบอร์ด TitraLab (Pump Hardware on TitraLab)
# ==============================================================================
#
#   PUMP_PIN = GPIO21 (CONTROL_1)
#
#   วงจรขับปั๊ม (Pump driver circuit):
#   - ESP32 GPIO21 -> EL357N optocoupler (แยกสัญญาณ/isolation)
#   - Optocoupler -> MOSFET 5.8A/30V (ขับโหลด/load driver)
#   - แรงดันออก: 12V จาก MT3608 boost converter
#   - Output voltage: 12V from MT3608 boost converter
#
#   ความถี่ PWM ที่แนะนำ: 1000 Hz
#   Recommended PWM frequency: 1000 Hz
#
#   ช่วง Duty Cycle: 0-1023 (0-100% ความเร็ว)
#   Duty Cycle range: 0-1023 (0-100% speed)
#
# ==============================================================================
# ความสัมพันธ์ Duty Cycle กับความเร็วปั๊ม (Duty Cycle vs Pump Speed)
# ==============================================================================
#
#   Duty Cycle ควบคุมความเร็วปั๊ม (Duty cycle controls pump speed):
#
#   duty = 0     -> ปั๊มหยุด (Pump stopped)
#   duty = 256   -> ปั๊มช้า ~25% (Slow ~25%)
#   duty = 512   -> ปั๊มกลาง ~50% (Medium ~50%)
#   duty = 768   -> ปั๊มเร็ว ~75% (Fast ~75%)
#   duty = 1023  -> ปั๊มเร็วสุด 100% (Maximum speed 100%)
#
#   แผนภาพความสัมพันธ์ (Relationship Diagram):
#
#   Pump Speed    |                    *
#   ความเร็วปั๊ม  |                  *
#   (mL/min)      |                *
#                 |              *
#                 |            *
#                 |          *
#                 |        *
#                 |      *
#                 |    *
#                 |  *
#                 |*__________________ Duty Cycle
#                 0                  1023
#
#   หมายเหตุ: ความสัมพันธ์อาจไม่เป็นเชิงเส้นสมบูรณ์
#   Note: Relationship may not be perfectly linear
#   ต้องสอบเทียบใน Week 2 เพื่อหาค่าจริง (mL/min vs duty)
#   Must calibrate in Week 2 for real values (mL/min vs duty)
#
# ==============================================================================
# การประยุกต์ใช้ในไทเทรชัน (Application in Titration)
# ==============================================================================
#
#   ในการไทเทรชันอัตโนมัติ Week 3:
#   In automatic titration Week 3:
#
#   Phase 1: ห่างจากจุดสมมูล (Far from equivalence point)
#            - ใช้ duty สูง (80-100%) เพราะ pH เปลี่ยนช้า
#            - Use high duty (80-100%) as pH changes slowly
#
#   Phase 2: เข้าใกล้จุดสมมูล (Approaching equivalence point)
#            - ลด duty ลง (40-60%) เพื่อความระมัดระวัง
#            - Lower duty (40-60%) for caution
#
#   Phase 3: ใกล้จุดสมมูลมาก (Very close to equivalence point)
#            - ใช้ duty ต่ำ (15-30%) เพื่อความแม่นยำ
#            - Use low duty (15-30%) for precision
#
#   Phase 4: ถึงจุดสมมูล (Reached equivalence point)
#            - หยุดปั๊มทันที! (Stop pump immediately!)
#
# ==============================================================================

from machine import Pin, PWM
import time

# นำเข้าค่าขา GPIO (Import GPIO pins)
try:
    from pins import PUMP_PIN, LED_GREEN, LED_RED
except ImportError:
    PUMP_PIN = 21     # ปั๊ม (Pump)
    LED_GREEN = 4     # LED สีเขียว (Green LED)
    LED_RED = 2       # LED สีแดง (Red LED)

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================

PWM_FREQ = 1000      # ความถี่ PWM มาตรฐานสำหรับปั๊ม (Standard PWM freq for pump)
DUTY_MAX = 1023      # ค่า duty สูงสุด (Maximum duty value)
DUTY_MIN = 0         # ค่า duty ต่ำสุด (Minimum duty value)

# ความเร็วที่ใช้ในแต่ละ Phase ของไทเทรชัน
# Speeds used in each titration phase
SPEED_FAST = 80      # Phase 1: ห่างจากจุดสมมูล (Far from endpoint)
SPEED_MEDIUM = 50    # Phase 2: เข้าใกล้ (Approaching)
SPEED_SLOW = 25      # Phase 3: ใกล้มาก (Very close)

# ==============================================================================
# ส่วนที่ 1: ตั้งค่าฮาร์ดแวร์ (Hardware Setup)
# ==============================================================================

print("=" * 60)
print("การควบคุมปั๊มไทเทรชันด้วย PWM")
print("Titration Pump Control with PWM")
print("=" * 60)
print()
print("!!! ข้อควรระวังด้านความปลอดภัย / SAFETY WARNINGS !!!")
print("-" * 60)
print("  1. ตรวจสอบว่าท่อปั๊มต่อกับภาชนะที่เหมาะสม")
print("     Ensure pump tubes are connected properly")
print("  2. วางภาชนะบนถาดรองรับเพื่อป้องกันการหก")
print("     Place containers on tray to prevent spills")
print("  3. สวมถุงมือเมื่อใช้สารเคมี (NaOH, HCl)")
print("     Wear gloves when handling chemicals")
print("  4. กด Ctrl+C เพื่อหยุดปั๊มฉุกเฉิน")
print("     Press Ctrl+C for emergency stop")
print("-" * 60)
print()

# สร้าง PWM สำหรับปั๊ม (Create PWM for pump)
pump_pwm = PWM(Pin(PUMP_PIN))
pump_pwm.freq(PWM_FREQ)
pump_pwm.duty(DUTY_MIN)  # เริ่มต้นปิดปั๊ม (Start with pump off)

# LED สำหรับแสดงสถานะ (Status LEDs)
led_green = Pin(LED_GREEN, Pin.OUT)
led_red = Pin(LED_RED, Pin.OUT)
led_red.on()     # LED แดงติด = ปั๊มหยุด (Red LED on = pump stopped)
led_green.off()

print("ฮาร์ดแวร์ปั๊ม TitraLab (TitraLab Pump Hardware):")
print(f"  Pump Pin: GPIO{PUMP_PIN}")
print(f"  PWM Frequency: {PWM_FREQ} Hz")
print(f"  Driver: EL357N optocoupler -> MOSFET 5.8A/30V")
print(f"  Output Voltage: 12V (MT3608 boost converter)")
print()

# ==============================================================================
# ส่วนที่ 2: ฟังก์ชันควบคุมปั๊ม (Pump Control Functions)
# ==============================================================================

def pump_on(pwm, duty=512):
    """
    เปิดปั๊มที่ความเร็วที่กำหนด (Turn on pump at specified speed)

    Args:
        pwm: PWM object ของปั๊ม (Pump PWM object)
        duty (int): ค่า duty cycle 0-1023 (default 512 = 50%)

    หมายเหตุ: ใน Week 3 จะใช้ค่า duty ที่ได้จากการสอบเทียบ
    Note: In Week 3, will use duty values from calibration
    """
    # จำกัดค่า duty ให้อยู่ในช่วงที่ถูกต้อง (Clamp duty to valid range)
    duty = max(DUTY_MIN, min(DUTY_MAX, duty))

    pwm.duty(duty)
    led_green.on()
    led_red.off()

    percentage = (duty / DUTY_MAX) * 100
    print(f"ปั๊มเปิด (Pump ON): duty={duty} ({percentage:.1f}%)")


def pump_off(pwm):
    """
    ปิดปั๊ม (Turn off pump)

    สำคัญ: ต้องเรียกฟังก์ชันนี้เมื่อ:
    Important: Must call this function when:
    - ถึงจุดสมมูลในการไทเทรชัน (Reached equivalence point)
    - เกิดข้อผิดพลาด (Error occurs)
    - ผู้ใช้กด Ctrl+C (User presses Ctrl+C)

    Args:
        pwm: PWM object ของปั๊ม (Pump PWM object)
    """
    pwm.duty(DUTY_MIN)
    led_green.off()
    led_red.on()
    print("ปั๊มปิด (Pump OFF)")


def pump_set_speed(pwm, percentage):
    """
    ตั้งความเร็วปั๊มเป็นเปอร์เซ็นต์ (Set pump speed as percentage)

    ใน Week 3 จะสอบเทียบ % กับ mL/min
    In Week 3, will calibrate % vs mL/min

    ตัวอย่างค่าสอบเทียบ (Example calibration values):
      25% -> ~0.5 mL/min (ช้า/slow)
      50% -> ~1.0 mL/min (ปานกลาง/medium)
      75% -> ~1.5 mL/min (เร็ว/fast)
      100% -> ~2.0 mL/min (เร็วสุด/max)

    Args:
        pwm: PWM object ของปั๊ม (Pump PWM object)
        percentage (float): ความเร็ว 0-100%
    """
    # แปลง % เป็น duty cycle (Convert % to duty cycle)
    duty = int((percentage / 100) * DUTY_MAX)
    duty = max(DUTY_MIN, min(DUTY_MAX, duty))  # จำกัดค่า (clamp)

    pwm.duty(duty)

    if duty > 0:
        led_green.on()
        led_red.off()
    else:
        led_green.off()
        led_red.on()

    print(f"ความเร็วปั๊ม (Pump speed): {percentage:.1f}% (duty={duty})")


def pump_emergency_stop(pwm):
    """
    หยุดปั๊มฉุกเฉิน (Emergency pump stop)

    เรียกใช้เมื่อ (Call when):
    - ตรวจพบข้อผิดพลาด (Error detected)
    - ปั๊มทำงานผิดปกติ (Pump malfunction)
    - ต้องการหยุดทันที (Need immediate stop)
    """
    pwm.duty(DUTY_MIN)
    # กระพริบ LED แดง 3 ครั้ง (Blink red LED 3 times)
    led_green.off()
    for _ in range(3):
        led_red.on()
        time.sleep(0.1)
        led_red.off()
        time.sleep(0.1)
    led_red.on()
    print("!!! หยุดฉุกเฉิน (EMERGENCY STOP) !!!")


# ==============================================================================
# ส่วนที่ 3: การทดสอบปั๊ม (Pump Testing)
# ==============================================================================

try:
    input("กด Enter เพื่อเริ่มทดสอบปั๊ม (Press Enter to start pump test)...")
    print()

    # -------------------------------------------------------------------------
    # ทดสอบ 1: เปิด-ปิดปั๊ม (Test 1: On/Off)
    # -------------------------------------------------------------------------
    print("-" * 60)
    print("ทดสอบที่ 1: เปิด-ปิดปั๊ม (Test 1: Pump On/Off)")
    print("-" * 60)

    pump_on(pump_pwm, duty=512)  # เปิดที่ 50%
    time.sleep(2)
    pump_off(pump_pwm)
    time.sleep(1)

    # -------------------------------------------------------------------------
    # ทดสอบ 2: ความเร็วต่างๆ (Test 2: Different Speeds)
    # -------------------------------------------------------------------------
    print()
    print("-" * 60)
    print("ทดสอบที่ 2: ความเร็วต่างๆ (Test 2: Different Speeds)")
    print("-" * 60)

    speeds = [25, 50, 75, 100]

    for speed in speeds:
        print(f"\nทดสอบความเร็ว {speed}% (Testing {speed}% speed)")
        pump_set_speed(pump_pwm, speed)
        time.sleep(2)

    pump_off(pump_pwm)
    time.sleep(1)

    # -------------------------------------------------------------------------
    # ทดสอบ 3: ค่อยๆ เพิ่ม/ลดความเร็ว (Test 3: Gradual Speed Change)
    # -------------------------------------------------------------------------
    print()
    print("-" * 60)
    print("ทดสอบที่ 3: ค่อยๆ เพิ่ม/ลดความเร็ว (Test 3: Gradual Ramp)")
    print("-" * 60)

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

    # -------------------------------------------------------------------------
    # ทดสอบ 4: จำลองรูปแบบไทเทรชัน (Test 4: Titration Pattern Simulation)
    # -------------------------------------------------------------------------
    print("-" * 60)
    print("ทดสอบที่ 4: จำลองรูปแบบการไทเทรชันจริง")
    print("Test 4: Real Titration Pattern Simulation")
    print("-" * 60)
    print()
    print("  กลยุทธ์การไทเทรชัน (Titration Strategy):")
    print()
    print("  Phase 1: ห่างจากจุดสมมูล -> เร็ว (80%)")
    print("           Far from equivalence -> Fast")
    print()
    print("  Phase 2: เข้าใกล้จุดสมมูล -> ปานกลาง (50%)")
    print("           Approaching equivalence -> Medium")
    print()
    print("  Phase 3: ใกล้จุดสมมูลมาก -> ช้า (25%)")
    print("           Very close to equivalence -> Slow")
    print()
    print("  Phase 4: ถึงจุดสมมูล -> หยุด!")
    print("           Reached equivalence -> Stop!")
    print()

    # Phase 1: ห่างจากจุดสมมูล - เร็ว (Far from endpoint - fast)
    print(f"Phase 1: ห่างจากจุดสมมูล - ความเร็ว {SPEED_FAST}%")
    print("         (pH ยังเปลี่ยนช้า เติมได้เร็ว)")
    pump_set_speed(pump_pwm, SPEED_FAST)
    time.sleep(3)

    # Phase 2: เข้าใกล้ - ปานกลาง (Approaching - medium)
    print(f"\nPhase 2: เข้าใกล้จุดสมมูล - ความเร็ว {SPEED_MEDIUM}%")
    print("         (pH เริ่มเปลี่ยนเร็วขึ้น ต้องระวัง)")
    pump_set_speed(pump_pwm, SPEED_MEDIUM)
    time.sleep(3)

    # Phase 3: ใกล้มาก - ช้า (Very close - slow)
    print(f"\nPhase 3: ใกล้จุดสมมูลมาก - ความเร็ว {SPEED_SLOW}%")
    print("         (pH เปลี่ยนเร็วมาก ต้องแม่นยำ)")
    pump_set_speed(pump_pwm, SPEED_SLOW)
    time.sleep(3)

    # Phase 4: ถึงจุดสมมูล - หยุด (Reached endpoint - stop)
    print("\nPhase 4: ถึงจุดสมมูล! - หยุดปั๊มทันที")
    print("         (pH ถึงค่าที่ต้องการแล้ว)")
    pump_off(pump_pwm)

    # =========================================================================
    # สรุป (Summary)
    # =========================================================================
    print()
    print("=" * 60)
    print("สรุป: การควบคุมปั๊มด้วย PWM สำหรับไทเทรชัน")
    print("Summary: PWM Pump Control for Titration")
    print("=" * 60)
    print()
    print("นี่คือพื้นฐานการควบคุมปั๊มที่ใช้ใน Week 3")
    print("This is the basis for pump control used in Week 3")
    print()
    print("-" * 60)
    print("สิ่งที่เรียนรู้ (What you learned):")
    print("-" * 60)
    print()
    print("  1. Duty Cycle ควบคุมความเร็วปั๊ม")
    print("     Duty cycle controls pump speed")
    print("     - duty 0 = หยุด, duty 1023 = เร็วสุด")
    print()
    print("  2. ความถี่ PWM ที่เหมาะสมคือ 1000 Hz")
    print("     Suitable PWM frequency is 1000 Hz")
    print()
    print("  3. ฮาร์ดแวร์ปั๊ม TitraLab:")
    print("     TitraLab pump hardware:")
    print("     - GPIO21 -> optocoupler -> MOSFET")
    print("     - แรงดันออก 12V จาก boost converter")
    print()
    print("  4. กลยุทธ์ไทเทรชัน: เร็ว -> กลาง -> ช้า -> หยุด")
    print("     Titration strategy: Fast -> Medium -> Slow -> Stop")
    print()
    print("  5. สำคัญ: ต้องเรียก pump_pwm.deinit() เมื่อจบ!")
    print("     Important: Must call pump_pwm.deinit() when done!")
    print()
    print("-" * 60)
    print("ขั้นตอนต่อไป (Next Steps):")
    print("-" * 60)
    print("  Week 2: การสอบเทียบปั๊ม (Pump Calibration)")
    print("          - หาความสัมพันธ์ % กับ mL/min")
    print("          - Find relationship between % and mL/min")
    print()
    print("  Week 3: การไทเทรชันอัตโนมัติ (Automatic Titration)")
    print("          - ปรับความเร็วปั๊มตามค่า pH อัตโนมัติ")
    print("          - Automatically adjust pump speed based on pH")
    print()
    print("=" * 60)

except KeyboardInterrupt:
    print()
    print()
    print("!!! หยุดโปรแกรมโดยผู้ใช้ (Program stopped by user) !!!")
    print()

finally:
    # =========================================================================
    # ทำความสะอาดทรัพยากร (Cleanup Resources)
    # =========================================================================
    #
    # สำคัญมาก! ต้องหยุดปั๊มและคืน PWM เสมอ
    # CRITICAL! Always stop pump and release PWM
    #
    # บล็อก finally นี้จะทำงานเสมอ ไม่ว่าจะ:
    # This finally block ALWAYS runs whether:
    # - โปรแกรมจบปกติ (Program ends normally)
    # - เกิด exception (Exception occurs)
    # - ผู้ใช้กด Ctrl+C (User presses Ctrl+C)
    #

    # หยุดปั๊มก่อนอื่น! (Stop pump first!)
    pump_pwm.duty(DUTY_MIN)

    # คืนทรัพยากร PWM (Release PWM resources)
    pump_pwm.deinit()

    # ปิด LED ทั้งหมด (Turn off all LEDs)
    led_green.off()
    led_red.off()

    print()
    print("-" * 60)
    print("ทำความสะอาดทรัพยากรเรียบร้อย (Cleanup completed):")
    print("  - ปั๊มหยุดแล้ว (Pump stopped)")
    print("  - PWM deinit แล้ว (PWM deinitialized)")
    print("  - LED ปิดแล้ว (LEDs off)")
    print("-" * 60)

# ==============================================================================
# 03_pump_validate_stepwise.py - การตรวจสอบปริมาตรปั๊มแบบเป็นช่วง
# (Intermittent Pump Volume Validation with pH Stabilization)
# ==============================================================================
# โปรแกรมนี้จำลองการทำงานของปั๊มในช่วงใกล้จุดสมมูล (equivalence point)
# โดยปั๊มเป็นช่วงสั้นๆ แล้วหยุดรอให้ pH stabilize ก่อนปั๊มต่อ
#
# This program simulates pump operation near the equivalence point
# by pumping in short bursts, then pausing for pH stabilization
#
# เวลาที่ใช้ในการเรียนรู้ (Estimated Teaching Time): 25-35 นาที
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้านเคมี (Chemistry Learning Objectives):
# ==============================================================================
# 1. เข้าใจความจำเป็นของการปั๊มเป็นช่วงใกล้จุดสมมูล
#    (Understand why intermittent pumping is needed near equivalence point)
#
# 2. เรียนรู้เรื่อง pH stabilization time และผลต่อความแม่นยำ
#    (Learn about pH stabilization time and its effect on accuracy)
#
# 3. เปรียบเทียบความแม่นยำระหว่างการปั๊มต่อเนื่องกับปั๊มเป็นช่วง
#    (Compare accuracy between continuous and intermittent pumping)
#
# ==============================================================================
# ทำไมต้องปั๊มเป็นช่วงใกล้จุดสมมูล? (Why Intermittent Pumping Near Eq. Point?)
# ==============================================================================
# ในการไทเทรตกรด-เบส:
# - ช่วงเริ่มต้น (pH 2-4): pH เปลี่ยนช้า → ปั๊มต่อเนื่องได้
# - ช่วงใกล้จุดสมมูล (pH 4-10): pH เปลี่ยนเร็วมาก → ต้องปั๊มทีละน้อย
# - หลังจุดสมมูล (pH 10-12): pH เปลี่ยนช้าลง
#
# การหยุดรอ (pause) มีความสำคัญเพราะ:
# 1. สารไทแทรนต์ต้องผสมกับสารตัวอย่างให้ทั่ว
# 2. ปฏิกิริยาเคมีต้องใช้เวลาเข้าสู่สมดุล
# 3. เซ็นเซอร์ pH ต้องใช้เวลาในการอ่านค่าที่เสถียร
#
# ==============================================================================
# การใช้งานในการไทเทรตจริง (Real Titration Usage):
# ==============================================================================
# รูปแบบการปั๊มที่แนะนำ:
# 1. pH < 4:  ปั๊มต่อเนื่อง 1 mL/ครั้ง (pumpValidate_1.py)
# 2. pH 4-6:  ปั๊ม 0.5 mL → หยุด 2 วินาที
# 3. pH 6-8:  ปั๊ม 0.1 mL → หยุด 3 วินาที (ใกล้จุดสมมูลที่สุด)
# 4. pH > 8:  ปั๊มต่อเนื่องได้อีกครั้ง
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้าน OOP/Programming (OOP Learning Objectives):
# ==============================================================================
# 1. การควบคุม timing แบบซับซ้อน (Complex timing control)
# 2. การออกแบบ state machine สำหรับการปั๊มเป็นช่วง
# 3. การรวม sensor feedback กับ actuator control (แนวคิดสำหรับ Week 3)
#
# ==============================================================================
# Hardware Configuration:
# ==============================================================================
# - GPIO 21: Pump (PWM output)
# - GPIO 2:  Red LED (ปั๊มทำงาน / Pump running)
# - GPIO 4:  Green LED (หยุดรอ pH stabilize / Waiting for stabilization)
# - GPIO 34: Button 1 (Start/Stop) - input-only
# - GPIO 35: Button 2 (ปรับเวลา pause / Adjust pause time) - input-only
# ==============================================================================

from machine import Pin, PWM
from time import ticks_us, ticks_diff, sleep_ms

# ==============================================================================
# การตั้งค่าขา GPIO (GPIO Pin Configuration)
# ==============================================================================

# LED แสดงสถานะ (Status LEDs)
led_red = Pin(2, Pin.OUT)    # LED สีแดง - ปั๊มทำงาน (Red LED - pump running)
led_green = Pin(4, Pin.OUT)  # LED สีเขียว - รอ stabilize (Green LED - waiting)

# ปุ่มกด (Buttons)
# หมายเหตุ: GPIO34, 35 เป็น input-only pin ไม่รองรับ internal pull resistors
# Note: GPIO34, 35 are input-only, do NOT support internal pull resistors
btn_start = Pin(34, Pin.IN)    # ปุ่มเริ่ม/หยุด (Start/Stop button)
btn_adjust = Pin(35, Pin.IN)   # ปุ่มปรับเวลา pause (Adjust pause time)

# ปั๊ม (Pump) - PWM Control
pump_pin = Pin(21, Pin.OUT)
pump_pwm = PWM(pump_pin, freq=1000)
pump_pwm.duty(0)  # เริ่มต้นปิดปั๊ม (Start with pump off)

# ==============================================================================
# ค่าคงที่สำหรับการคำนวณปริมาตร (Volume Calculation Constants)
# ==============================================================================

def load_flow_rate():
    """
    โหลดค่า flow rate จากไฟล์ data_flowrate.txt
    Load flow rate from data_flowrate.txt file
    """
    # ทศนิยม 4 ตำแหน่ง - สำคัญมากต่อความแม่นยำของปริมาตรที่ปั๊ม
    # 4 decimal places - critical for precise transferred volume calculation
    # เช่น 0.2800 vs 0.28 ต่างกัน 0.0000 แต่ถ้า 0.2834 vs 0.28 ผิดพลาด ~1.2%
    default_flow_rate = 0.2800  # ค่าเริ่มต้น (Default value)

    try:
        with open('data_flowrate.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('flow_rate='):
                    value = float(line.split('=')[1])
                    print(f"โหลด flow_rate จากไฟล์: {value:.4f} mL/s")
                    return value
    except OSError:
        print(f"ไม่พบไฟล์ - ใช้ค่าเริ่มต้น {default_flow_rate:.4f} mL/s")
        print("*** รัน 01_flowRate.py เพื่อสอบเทียบปั๊มก่อน ***")
    except Exception as e:
        print(f"ข้อผิดพลาด (Error): {e}")

    return default_flow_rate


# โหลดค่า flow rate (Load flow rate)
FLOW_RATE = load_flow_rate()  # mL/s

# ค่าเป้าหมายสำหรับการตรวจสอบ (Target values for validation)
TARGET_VOLUME = 5.0           # ปริมาตรเป้าหมาย (mL)
DUTY_CYCLE_PERCENT = 100      # Duty cycle (%)

# ==============================================================================
# การตั้งค่าการปั๊มเป็นช่วง (Intermittent Pumping Settings)
# ==============================================================================
# นิสิตสามารถปรับค่าเหล่านี้ได้ตามการทดลอง
# Students can adjust these values based on experiments

PUMP_DURATION = 1.0      # เวลาปั๊มแต่ละรอบ (s) - Pump duration per cycle
PAUSE_DURATION = 2.0     # เวลาหยุดระหว่างรอบ (s) - Pause between cycles (for pH stabilization)

# ตัวเลือกเวลา pause สำหรับปุ่ม 2 (Pause time options for Button 2)
PAUSE_OPTIONS = [1.0, 2.0, 3.0, 5.0]  # วินาที (seconds)
pause_index = 1  # เริ่มต้นที่ 2.0 วินาที (Start at 2.0 seconds)

# ==============================================================================
# ตัวแปรควบคุม (Control Variables)
# ==============================================================================
running = False               # สถานะปั๊ม (Pump running state)
debounce_time_ms = 300        # เวลา debounce (ms)
last_press_time = {34: 0, 35: 0}  # เวลากดปุ่มล่าสุด

# ผลการทดสอบ (Test results)
test_results = []
cycle_count = 0

# ==============================================================================
# ฟังก์ชัน Precise Sleep (Precise Sleep Function)
# ==============================================================================
def precise_sleep(duration_s):
    """
    หยุดทำงานชั่วคราวด้วยความแม่นยำระดับไมโครวินาที
    Pause execution with microsecond precision
    """
    start_time = ticks_us()
    target_us = int(duration_s * 1_000_000)
    while ticks_diff(ticks_us(), start_time) < target_us:
        pass


# ==============================================================================
# ฟังก์ชันปั๊มเป็นช่วง (Intermittent Pump Function)
# ==============================================================================
def pump_intermittent(target_volume_ml, pump_time_s, pause_time_s):
    """
    ปั๊มน้ำแบบเป็นช่วงๆ จนถึงปริมาตรเป้าหมาย
    Pump water intermittently until target volume is reached

    รูปแบบการทำงาน (Operation Pattern):
    [ปั๊ม pump_time_s] → [หยุด pause_time_s] → [วัด pH] → ทำซ้ำ

    พารามิเตอร์ (Parameters):
    - target_volume_ml: ปริมาตรเป้าหมาย (mL)
    - pump_time_s: เวลาปั๊มแต่ละรอบ (s)
    - pause_time_s: เวลาหยุดระหว่างรอบ (s)

    Returns:
    - tuple: (เวลาปั๊มรวม, ปริมาตรรวม, จำนวนรอบ)
    """
    global running, cycle_count

    if running:
        print("ปั๊มกำลังทำงานอยู่แล้ว (Pump already running)")
        return None

    running = True
    cycle_count = 0
    total_pump_time = 0
    total_volume = 0
    duty_value = int((DUTY_CYCLE_PERCENT / 100) * 1023)

    # คำนวณปริมาตรต่อรอบ (Calculate volume per cycle)
    volume_per_cycle = FLOW_RATE * pump_time_s

    print("\n" + "=" * 60)
    print("  เริ่มปั๊มแบบเป็นช่วง (INTERMITTENT PUMPING STARTED)")
    print("=" * 60)
    print(f"  ปริมาตรเป้าหมาย (Target): {target_volume_ml:.2f} mL")
    print(f"  Flow rate: {FLOW_RATE:.4f} mL/s")
    print(f"  รูปแบบ: ปั๊ม {pump_time_s}s → หยุด {pause_time_s}s → ทำซ้ำ")
    print(f"  ปริมาตรต่อรอบ: {volume_per_cycle:.3f} mL")
    print("-" * 60)
    print("  LED สีแดง = ปั๊มทำงาน | LED สีเขียว = รอ pH stabilize")
    print("-" * 60)

    start_time_total = ticks_us()

    while total_volume < target_volume_ml:
        cycle_count += 1
        print(f"\n  --- รอบที่ (Cycle) {cycle_count} ---")

        # คำนวณปริมาตรที่เหลือ (Calculate remaining volume)
        remaining = target_volume_ml - total_volume

        # ตรวจสอบรอบสุดท้าย (Check if last cycle)
        if remaining < volume_per_cycle:
            # ปรับเวลาปั๊มสำหรับรอบสุดท้าย (Adjust pump time for last cycle)
            adjusted_pump_time = remaining / FLOW_RATE
            print(f"  [รอบสุดท้าย] ปั๊ม {adjusted_pump_time:.2f} วินาที")
        else:
            adjusted_pump_time = pump_time_s

        # === ช่วงปั๊ม (Pumping Phase) ===
        led_red.on()
        led_green.off()
        print(f"  [ปั๊ม] กำลังปั๊ม... ({adjusted_pump_time:.2f}s)")

        pump_pwm.duty(duty_value)
        precise_sleep(adjusted_pump_time)
        pump_pwm.duty(0)

        led_red.off()

        # อัพเดตค่า (Update values)
        volume_pumped = FLOW_RATE * adjusted_pump_time
        total_volume += volume_pumped
        total_pump_time += adjusted_pump_time

        print(f"  [ปั๊มเสร็จ] +{volume_pumped:.3f} mL | รวม: {total_volume:.3f} mL")

        # ตรวจสอบว่าถึงเป้าหมายหรือยัง (Check if target reached)
        if total_volume >= target_volume_ml:
            break

        # === ช่วงรอ pH stabilize (Pause Phase) ===
        led_green.on()
        print(f"  [รอ] pH stabilizing... ({pause_time_s}s)")
        print(f"        (ในการไทเทรตจริง จะอ่านค่า pH ช่วงนี้)")

        # แสดง countdown (Show countdown)
        for i in range(int(pause_time_s), 0, -1):
            print(f"        เหลืออีก {i} วินาที...")
            precise_sleep(1.0)

        led_green.off()

    # คำนวณเวลารวมทั้งหมด (Calculate total elapsed time)
    total_elapsed = ticks_diff(ticks_us(), start_time_total) / 1_000_000

    running = False
    led_red.off()
    led_green.off()

    # กระพริบ LED เขียวแสดงเสร็จสิ้น (Blink green LED to show completion)
    for _ in range(3):
        led_green.on()
        sleep_ms(200)
        led_green.off()
        sleep_ms(200)

    print("\n" + "=" * 60)
    print("  เสร็จสิ้น! (COMPLETE!)")
    print("=" * 60)
    print(f"  จำนวนรอบ (Cycles): {cycle_count}")
    print(f"  เวลาปั๊มรวม (Total pump time): {total_pump_time:.3f} s")
    print(f"  เวลาทั้งหมด (Total elapsed): {total_elapsed:.1f} s")
    print(f"  ปริมาตรที่คำนวณได้ (Calculated volume): {total_volume:.3f} mL")
    print("=" * 60)

    return (total_pump_time, total_volume, cycle_count)


def adjust_pause_time():
    """
    ปรับเวลา pause สำหรับ pH stabilization
    Adjust pause time for pH stabilization
    """
    global pause_index, PAUSE_DURATION

    pause_index = (pause_index + 1) % len(PAUSE_OPTIONS)
    PAUSE_DURATION = PAUSE_OPTIONS[pause_index]

    print(f"\n*** เวลา pause ใหม่: {PAUSE_DURATION} วินาที ***")
    print(f"*** New pause time: {PAUSE_DURATION} seconds ***")


def display_validation_instructions(calculated_volume, cycles):
    """
    แสดงคำแนะนำสำหรับการตรวจสอบความแม่นยำ
    Display instructions for accuracy validation
    """
    print("\n" + "=" * 60)
    print("  การตรวจสอบความแม่นยำ (ACCURACY VALIDATION)")
    print("=" * 60)
    print(f"  ปริมาตรที่คำนวณได้: {calculated_volume:.3f} mL")
    print(f"  จำนวนรอบการปั๊ม: {cycles}")
    print()
    print("  ขั้นตอน (Steps):")
    print("  1. วัดปริมาตรน้ำในกระบอกตวง")
    print("  2. คำนวณ % error:")
    print("     % error = |ค่าจริง - ค่าคำนวณ| / ค่าคำนวณ x 100")
    print()
    print("  เปรียบเทียบกับ pumpValidate_1.py (continuous):")
    print("  - ปั๊มเป็นช่วงใช้เวลานานกว่า แต่แม่นยำกว่าใกล้จุดสมมูล")
    print("  - ในการไทเทรตจริง เริ่มด้วย continuous แล้วเปลี่ยนเป็น intermittent")
    print("=" * 60)
    print()
    print("การควบคุม (Controls):")
    print(f"  [ปุ่ม 1] เริ่มทดสอบใหม่ | [ปุ่ม 2] ปรับเวลา pause (ปัจจุบัน: {PAUSE_DURATION}s)")
    print("  [Ctrl+C] หยุดโปรแกรม")


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
print("\n" + "=" * 65)
print("  การตรวจสอบปริมาตรปั๊มแบบเป็นช่วง")
print("  (Intermittent Pump Volume Validation)")
print("=" * 65)
print()
print("ความสำคัญในการไทเทรต (Importance in Titration):")
print("  ใกล้จุดสมมูล (equivalence point) pH เปลี่ยนเร็วมาก!")
print("  - ต้องเติมสารไทแทรนต์ทีละน้อย")
print("  - ต้องรอให้ pH stabilize ก่อนอ่านค่า")
print("  - รูปแบบ: ปั๊ม → หยุด → อ่าน pH → ปั๊ม → ...")
print()
print(f"ค่าที่ใช้ (Current Settings):")
print(f"  Flow Rate: {FLOW_RATE:.4f} mL/s")
print(f"  ปริมาตรเป้าหมาย (Target): {TARGET_VOLUME:.2f} mL")
print(f"  เวลาปั๊มต่อรอบ: {PUMP_DURATION} s")
print(f"  เวลารอ pH stabilize: {PAUSE_DURATION} s")
print()
print("การเตรียมตัว (Preparation):")
print("  1. วางกระบอกตวงเปล่าใต้หัวปั๊ม")
print("  2. เตรียมบีกเกอร์น้ำสำหรับปั๊ม")
print()
print("การควบคุม (Controls):")
print("  [ปุ่ม 1] เริ่มปั๊ม")
print(f"  [ปุ่ม 2] ปรับเวลา pause (ตัวเลือก: {PAUSE_OPTIONS}s)")
print("  [Ctrl+C] หยุดโปรแกรม")
print("=" * 65)

try:
    led_red.off()
    led_green.off()

    while True:
        current_time = ticks_us() // 1000  # แปลงเป็น ms

        # ตรวจสอบปุ่ม 1 - Start (Check Button 1 - Start)
        if btn_start.value() == 1 and not running:
            if (current_time - last_press_time[34]) > debounce_time_ms:
                last_press_time[34] = current_time

                # รอจนกว่าปุ่มจะถูกปล่อย (Wait for button release)
                while btn_start.value() == 1:
                    sleep_ms(10)

                # เริ่มปั๊ม (Start pumping)
                result = pump_intermittent(TARGET_VOLUME, PUMP_DURATION, PAUSE_DURATION)

                if result:
                    pump_time, volume, cycles = result
                    test_results.append(result)
                    display_validation_instructions(volume, cycles)

        # ตรวจสอบปุ่ม 2 - Adjust pause (Check Button 2 - Adjust pause)
        if btn_adjust.value() == 1 and not running:
            if (current_time - last_press_time[35]) > debounce_time_ms:
                last_press_time[35] = current_time

                # รอจนกว่าปุ่มจะถูกปล่อย (Wait for button release)
                while btn_adjust.value() == 1:
                    sleep_ms(10)

                adjust_pause_time()

        sleep_ms(10)  # ลด CPU usage

except KeyboardInterrupt:
    print("\n\nหยุดโปรแกรม (Program stopped by user)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    pump_pwm.duty(0)
    pump_pwm.deinit()
    led_red.off()
    led_green.off()
    print("ปิดปั๊มและ LED แล้ว (Pump and LEDs released)")

    # แสดงสรุปผลการทดสอบ (Show test summary)
    if len(test_results) > 0:
        print("\n" + "=" * 55)
        print("สรุปผลการทดสอบทั้งหมด (All Test Results)")
        print("=" * 55)
        for i, (time_s, vol_ml, cyc) in enumerate(test_results, 1):
            print(f"  ครั้งที่ {i}: {vol_ml:.3f} mL | {cyc} รอบ | {time_s:.2f}s ปั๊มจริง")
        print("=" * 55)

        # เปรียบเทียบกับการปั๊มต่อเนื่อง (Compare with continuous pumping)
        avg_volume = sum(r[1] for r in test_results) / len(test_results)
        print(f"\nปริมาตรเฉลี่ย: {avg_volume:.3f} mL")
        print(f"เป้าหมาย: {TARGET_VOLUME:.2f} mL")
        error = abs(avg_volume - TARGET_VOLUME) / TARGET_VOLUME * 100
        print(f"% error โดยเฉลี่ย: {error:.2f}%")

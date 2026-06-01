# ==============================================================================
# 02_pump_validate_continuous.py - การตรวจสอบปริมาตรปั๊มแบบต่อเนื่อง
# (Continuous Pump Volume Validation)
# ==============================================================================
# โปรแกรมนี้ช่วยนิสิตตรวจสอบความแม่นยำของการสอบเทียบปั๊มโดยปั๊มน้ำ
# ปริมาตรที่กำหนดแบบต่อเนื่อง แล้วเปรียบเทียบกับปริมาตรที่วัดได้จริง
#
# This program helps students validate pump calibration accuracy by pumping
# a target volume continuously, then comparing with actual measured volume
#
# เวลาที่ใช้ในการเรียนรู้ (Estimated Teaching Time): 20-30 นาที
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้านเคมี (Chemistry Learning Objectives):
# ==============================================================================
# 1. ตรวจสอบความแม่นยำของการสอบเทียบปั๊ม (Validate pump calibration accuracy)
# 2. เข้าใจความสัมพันธ์ระหว่าง flow rate, เวลา และปริมาตร
#    (Understand relationship between flow rate, time and volume)
# 3. คำนวณ % error ระหว่างค่าที่คาดหวังกับค่าจริง
#    (Calculate % error between expected and actual values)
#
# ความสำคัญ: ถ้า flow rate ไม่แม่นยำ จะส่งผลต่อ:
# - การคำนวณปริมาตรสารไทแทรนต์ที่จุดสมมูล
# - ความเข้มข้นของสารตัวอย่างที่คำนวณได้
# - ค่าความไม่แน่นอน (uncertainty) ของผลการทดลอง
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้าน OOP/Programming (OOP Learning Objectives):
# ==============================================================================
# 1. การอ่านค่าจากไฟล์สอบเทียบ (Reading calibration data from file)
# 2. การใช้ precise timing สำหรับการควบคุมที่แม่นยำ
# 3. การคำนวณปริมาตรจาก flow rate และเวลา
#
# ==============================================================================
# การใช้งานในการไทเทรต (Usage in Titration):
# ==============================================================================
# การปั๊มต่อเนื่องใช้ในช่วงเริ่มต้นการไทเทรต:
# - เมื่อ pH ยังห่างจากจุดสมมูลมาก (เช่น pH < 4 สำหรับกรดแก่-เบสแก่)
# - ต้องการเติมสารไทแทรนต์ปริมาณมากเพื่อประหยัดเวลา
# - ตัวอย่าง: ปั๊ม 5 mL ก่อน แล้วเปลี่ยนเป็นปั๊มเป็นช่วงเมื่อใกล้จุดสมมูล
#
# ==============================================================================
# Hardware Configuration:
# ==============================================================================
# - GPIO 21: Pump (PWM output)
# - GPIO 2:  Red LED (ปั๊มทำงาน / Pump running)
# - GPIO 4:  Green LED (เสร็จสิ้น / Complete)
# - GPIO 34: Button 1 (Start pump) - input-only
#
# ==============================================================================
# ⚠ ความปลอดภัยของแอคชูเอเตอร์ — โปรดอ่าน (ACTUATOR SAFETY — READ FIRST)
# ==============================================================================
# สคริปต์นี้ขับปั๊มด้วย machine.PWM โดยตรง (raw PWM) เพื่อสอน duty-cycle/flow-rate
# This script drives the pump with raw machine.PWM (for duty-cycle teaching).
#
# *** RAW PWM ไม่ผ่านตัวจับเวลานิรภัยของเฟิร์มแวร์ (F-40 actuator guard) ***
# Raw PWM BYPASSES the firmware F-40 actuator-guard GPTimer. There is NO
# hardware max-on-time force-cut on this path. On firmware 0.3.x the run-scoped
# watchdog is also DISABLED (decision 0026/F-156), so a wedged script has NO
# firmware backstop keeping the pump on indefinitely.
#
# ดังนั้นสคริปต์นี้สำหรับใช้งานแบบมีผู้ควบคุม / เข้าถึงเครื่องโดยตรงเท่านั้น
# THEREFORE: supervised / physical-access (Thonny over USB) use ONLY.
# Do NOT run unattended. Last-line stops if the script wedges:
#   • กดปุ่ม 3 ค้าง (hold physical BUTTON_3) • Ctrl+C • รีเซ็ต/ถอดไฟ (reset/power-cut)
# This script enforces R-safeguards: stop_requested() poll in the loop,
# try/finally that forces the pump OFF, and KeyboardInterrupt -> pump OFF.
# (safety-hw ruling R, decision 0027)
# ==============================================================================

from machine import Pin, PWM
from time import ticks_us, ticks_diff, sleep_ms

# ให้แอป Student/Instructor สั่งหยุดสคริปต์ได้แบบ cooperative (F-149 STOP ladder)
# Let the Student/Instructor app stop this script cooperatively (F-149 STOP).
try:
    from scilabpro import stop_requested
except ImportError:
    stop_requested = None

# ==============================================================================
# การตั้งค่าขา GPIO (GPIO Pin Configuration)
# ==============================================================================

# LED แสดงสถานะ (Status LEDs)
led_red = Pin(2, Pin.OUT)    # LED สีแดง - ปั๊มทำงาน (Red LED - pump running)
led_green = Pin(4, Pin.OUT)  # LED สีเขียว - เสร็จสิ้น (Green LED - complete)

# ปุ่มกด (Button)
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull resistors
# Note: GPIO34 is input-only, does NOT support internal pull resistors
btn_start = Pin(34, Pin.IN)  # ปุ่มเริ่มปั๊ม (Start pump button)

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

    ไฟล์นี้สร้างจากโปรแกรม 01_flowRate.py
    This file is created by 01_flowRate.py

    Returns:
        float: flow rate ใน mL/s หรือค่า default ถ้าไม่พบไฟล์
    """
    # ทศนิยม 4 ตำแหน่ง - สำคัญมากต่อความแม่นยำของปริมาตรที่ปั๊ม
    # 4 decimal places - critical for precise transferred volume calculation
    # เช่น 0.2800 vs 0.28 ต่างกัน 0.0000 แต่ถ้า 0.2834 vs 0.28 ผิดพลาด ~1.2%
    default_flow_rate = 0.2800  # ค่าเริ่มต้นถ้าไม่พบไฟล์ (Default if file not found)

    try:
        with open('data_flowrate.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('flow_rate='):
                    value = float(line.split('=')[1])
                    print(f"โหลด flow_rate จากไฟล์: {value:.4f} mL/s")
                    print("(Loaded flow_rate from file)")
                    return value
    except OSError:
        print(f"ไม่พบไฟล์ data_flowrate.txt - ใช้ค่าเริ่มต้น {default_flow_rate:.4f} mL/s")
        print("(File not found - using default value)")
        print("*** คำแนะนำ: รัน 01_flowRate.py เพื่อสอบเทียบปั๊มก่อน ***")
        print("*** Tip: Run 01_flowRate.py to calibrate pump first ***")
    except Exception as e:
        print(f"ข้อผิดพลาดในการอ่านไฟล์ (Error reading file): {e}")

    return default_flow_rate


# โหลดค่า flow rate (Load flow rate)
FLOW_RATE = load_flow_rate()  # mL/s - อัตราการไหลที่สอบเทียบได้

# ค่าเป้าหมายสำหรับการตรวจสอบ (Target values for validation)
TARGET_VOLUME = 5.0           # ปริมาตรเป้าหมาย (mL) - ลองปั๊ม 5 mL ก่อน
DUTY_CYCLE_PERCENT = 100      # Duty cycle (%) - ความเร็วเต็มที่

# ==============================================================================
# ตัวแปรควบคุม (Control Variables)
# ==============================================================================
running = False               # สถานะปั๊ม (Pump running state)
debounce_time_ms = 300        # เวลา debounce (ms)
last_press_time = 0           # เวลากดปุ่มล่าสุด (Last button press time)

# ผลการทดสอบ (Test results)
test_results = []             # รายการผลการทดสอบ

# ==============================================================================
# ฟังก์ชัน Precise Sleep (Precise Sleep Function)
# ==============================================================================
def precise_sleep(duration_s):
    """
    หยุดทำงานชั่วคราวด้วยความแม่นยำระดับไมโครวินาที
    Pause execution with microsecond precision

    พารามิเตอร์ (Parameters):
    - duration_s: เวลาที่ต้องการหยุด (วินาที) / Time to sleep (seconds)

    หมายเหตุ: ใช้ busy-wait loop เพื่อความแม่นยำสูงสุด
    Note: Uses busy-wait loop for maximum precision
    ข้อเสีย: ใช้ CPU 100% ระหว่างรอ แต่แม่นยำกว่า sleep_ms
    Downside: Uses 100% CPU while waiting, but more precise than sleep_ms
    """
    start_time = ticks_us()
    target_us = int(duration_s * 1_000_000)
    while ticks_diff(ticks_us(), start_time) < target_us:
        pass


# ==============================================================================
# ฟังก์ชันปั๊มต่อเนื่อง (Continuous Pump Function)
# ==============================================================================
def pump_continuous(target_volume_ml):
    """
    ปั๊มน้ำแบบต่อเนื่องจนถึงปริมาตรเป้าหมาย
    Pump water continuously until target volume is reached

    สูตรการคำนวณ (Calculation formula):
    - เวลาที่ต้องปั๊ม = ปริมาตรเป้าหมาย / flow_rate
    - pumping_time = target_volume / flow_rate

    พารามิเตอร์ (Parameters):
    - target_volume_ml: ปริมาตรเป้าหมาย (mL)

    Returns:
    - tuple: (เวลาที่ปั๊มจริง, ปริมาตรที่คำนวณได้)
    """
    global running

    if running:
        print("ปั๊มกำลังทำงานอยู่แล้ว (Pump already running)")
        return None

    running = True
    led_red.on()  # เปิด LED แดงแสดงปั๊มทำงาน (Turn on red LED)

    # คำนวณเวลาที่ต้องปั๊ม (Calculate pumping time)
    pumping_time = target_volume_ml / FLOW_RATE

    print("\n" + "=" * 55)
    print("  เริ่มปั๊มแบบต่อเนื่อง (CONTINUOUS PUMPING STARTED)")
    print("=" * 55)
    print(f"  ปริมาตรเป้าหมาย (Target volume): {target_volume_ml:.2f} mL")
    print(f"  Flow rate: {FLOW_RATE:.4f} mL/s")
    print(f"  เวลาที่ต้องปั๊ม (Pumping time): {pumping_time:.2f} s")
    print(f"  Duty Cycle: {DUTY_CYCLE_PERCENT}%")
    print("-" * 55)

    # เริ่มปั๊ม (Start pump)
    duty_value = int((DUTY_CYCLE_PERCENT / 100) * 1023)
    pump_pwm.duty(duty_value)
    start_time = ticks_us()

    # แสดง progress ทุก 1 วินาที (Show progress every 1 second)
    elapsed = 0
    while elapsed < pumping_time:
        # นิรภัย: ถ้าแอปสั่ง STOP ระหว่างปั๊มกำลังทำงาน ให้ตัดปั๊มทันที
        # Safety: if the app requests STOP while the pump is RUNNING, cut it now.
        if stop_requested is not None and stop_requested():
            pump_pwm.duty(0)
            print("\nได้รับคำสั่งหยุดจากแอป — ตัดปั๊มทันที (Stop requested -> pump cut)")
            break

        # รอ 1 วินาทีหรือเวลาที่เหลือ (Wait 1 second or remaining time)
        wait_time = min(1.0, pumping_time - elapsed)
        precise_sleep(wait_time)
        elapsed += wait_time

        # คำนวณปริมาตรปัจจุบัน (Calculate current volume)
        current_volume = elapsed * FLOW_RATE
        progress = (current_volume / target_volume_ml) * 100

        # แสดง progress bar (Show progress bar)
        bar_length = 20
        filled = int(bar_length * progress / 100)
        bar = "=" * filled + "-" * (bar_length - filled)
        print(f"  [{bar}] {progress:5.1f}% | {current_volume:.2f}/{target_volume_ml:.2f} mL")

    # หยุดปั๊ม (Stop pump)
    pump_pwm.duty(0)
    actual_time = ticks_diff(ticks_us(), start_time) / 1_000_000
    calculated_volume = actual_time * FLOW_RATE

    running = False
    led_red.off()
    led_green.on()  # เปิด LED เขียวแสดงเสร็จสิ้น (Turn on green LED)

    print("-" * 55)
    print("  เสร็จสิ้น! (COMPLETE!)")
    print("=" * 55)
    print(f"  เวลาที่ปั๊มจริง (Actual time): {actual_time:.3f} s")
    print(f"  ปริมาตรที่คำนวณได้ (Calculated volume): {calculated_volume:.3f} mL")
    print("=" * 55)

    # ปิด LED เขียวหลัง 2 วินาที (Turn off green LED after 2 seconds)
    sleep_ms(2000)
    led_green.off()

    return (actual_time, calculated_volume)


def display_validation_instructions(calculated_volume):
    """
    แสดงคำแนะนำสำหรับการตรวจสอบความแม่นยำ
    Display instructions for accuracy validation
    """
    print("\n" + "=" * 55)
    print("  การตรวจสอบความแม่นยำ (ACCURACY VALIDATION)")
    print("=" * 55)
    print("  ขั้นตอน (Steps):")
    print("  1. วัดปริมาตรน้ำในกระบอกตวง (Measure water in cylinder)")
    print("  2. เปรียบเทียบกับค่าที่คำนวณได้")
    print()
    print(f"  ปริมาตรที่คำนวณได้: {calculated_volume:.3f} mL")
    print(f"  ปริมาตรที่วัดได้จริง: _______ mL (กรอกเอง)")
    print()
    print("  สูตรคำนวณ % error:")
    print("  % error = |ค่าจริง - ค่าคำนวณ| / ค่าคำนวณ x 100")
    print()
    print("  เกณฑ์ยอมรับ (Acceptable criteria):")
    print("  - % error < 2% = ดีมาก (Excellent)")
    print("  - % error 2-5% = พอใช้ได้ (Acceptable)")
    print("  - % error > 5% = ควรสอบเทียบใหม่ (Recalibrate)")
    print("=" * 55)
    print()
    print("กดปุ่ม 1 เพื่อทดสอบอีกครั้ง หรือ Ctrl+C เพื่อหยุด")
    print("(Press Button 1 to test again, or Ctrl+C to stop)")


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
print("\n" + "=" * 60)
print("  การตรวจสอบปริมาตรปั๊มแบบต่อเนื่อง")
print("  (Continuous Pump Volume Validation)")
print("=" * 60)
print()
print("วัตถุประสงค์ (Purpose):")
print("  ตรวจสอบว่า flow rate ที่สอบเทียบถูกต้องหรือไม่")
print("  โดยปั๊มน้ำปริมาตรที่กำหนดแล้วเปรียบเทียบกับค่าจริง")
print()
print(f"ค่าที่ใช้ (Current Settings):")
print(f"  Flow Rate: {FLOW_RATE:.4f} mL/s")
print(f"  ปริมาตรเป้าหมาย (Target): {TARGET_VOLUME:.2f} mL")
print(f"  เวลาที่ต้องปั๊ม: {TARGET_VOLUME/FLOW_RATE:.2f} วินาที")
print()
print("การเตรียมตัว (Preparation):")
print("  1. วางกระบอกตวงเปล่าใต้หัวปั๊ม")
print("  2. เตรียมบีกเกอร์น้ำสำหรับปั๊ม")
print("  3. ต่อท่อปั๊มให้เรียบร้อย")
print()
print("การควบคุม (Controls):")
print("  [ปุ่ม 1] เริ่มปั๊ม")
print("  [Ctrl+C] หยุดโปรแกรม")
print("=" * 60)

try:
    led_red.off()
    led_green.off()

    while True:
        # หยุดแบบ cooperative เมื่อแอปสั่ง STOP (F-149) — ออกไปที่ finally เพื่อปิดปั๊ม
        # Cooperative stop on app STOP request -> falls through to finally (pump OFF)
        if stop_requested is not None and stop_requested():
            print("\nได้รับคำสั่งหยุดจากแอป (Stop requested by app)")
            break

        current_time = ticks_us() // 1000  # แปลงเป็น ms

        # ตรวจสอบปุ่มพร้อม debounce (Check button with debounce)
        if btn_start.value() == 1 and not running:
            if (current_time - last_press_time) > debounce_time_ms:
                last_press_time = current_time

                # รอจนกว่าปุ่มจะถูกปล่อย (Wait for button release)
                while btn_start.value() == 1:
                    sleep_ms(10)

                # เริ่มปั๊ม (Start pumping)
                result = pump_continuous(TARGET_VOLUME)

                if result:
                    actual_time, calculated_volume = result
                    test_results.append(result)
                    display_validation_instructions(calculated_volume)

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
        print("\n" + "=" * 50)
        print("สรุปผลการทดสอบ (Test Summary)")
        print("=" * 50)
        for i, (time_s, vol_ml) in enumerate(test_results, 1):
            print(f"  ครั้งที่ {i}: {time_s:.3f} s, {vol_ml:.3f} mL")
        print("=" * 50)

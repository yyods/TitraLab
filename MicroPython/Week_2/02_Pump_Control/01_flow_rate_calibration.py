# ==============================================================================
# 01_flow_rate_calibration.py - การสอบเทียบอัตราการไหลของปั๊ม (Pump Flow Rate Calibration)
# ==============================================================================
# โปรแกรมนี้ช่วยนิสิตสอบเทียบ (calibrate) ปั๊มเพื่อหาอัตราการไหลที่แท้จริง
# This program helps students calibrate the pump to find actual flow rate
#
# เวลาที่ใช้ในการเรียนรู้ (Estimated Teaching Time): 30-45 นาที
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้านเคมี (Chemistry Learning Objectives):
# ==============================================================================
# 1. เข้าใจความสำคัญของการสอบเทียบปั๊มต่อความแม่นยำในการไทเทรต
#    (Understand pump calibration importance for titration accuracy)
# 2. คำนวณอัตราการไหล (flow rate) จากปริมาตรและเวลา
#    (Calculate flow rate from volume and time)
# 3. เข้าใจผลกระทบของความคลาดเคลื่อนต่อผลการไทเทรต
#    (Understand how errors affect titration results)
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้าน OOP/Programming (OOP Learning Objectives):
# ==============================================================================
# 1. เรียนรู้ PWM (Pulse Width Modulation) สำหรับควบคุมความเร็วปั๊ม
# 2. เข้าใจ Duty Cycle และผลต่ออัตราการไหล
# 3. ฝึกการบันทึกข้อมูลสอบเทียบลงไฟล์
#
# ==============================================================================
# ความสำคัญในการไทเทรต (Why Pump Calibration Matters for Titration):
# ==============================================================================
# ในการไทเทรตอัตโนมัติ ปริมาตรสารไทแทรนต์ต้องแม่นยำมาก:
# - ความผิดพลาด 0.1 mL อาจทำให้คำนวณความเข้มข้นผิดพลาด 1-2%
# - Flow rate ที่ไม่แน่นอนทำให้หาจุดสมมูล (equivalence point) ได้ยาก
# - ปั๊มแต่ละตัวมี flow rate ไม่เท่ากัน ต้องสอบเทียบทุกครั้ง
#
# สูตรคำนวณ: flow_rate (mL/s) = ปริมาตรที่วัดได้ (mL) / เวลา (s)
#
# ==============================================================================
# ขั้นตอนการสอบเทียบ (Calibration Procedure):
# ==============================================================================
# 1. เตรียมกระบอกตวง (graduated cylinder) และบีกเกอร์น้ำ
# 2. กดปุ่ม 1 เพื่อเริ่มปั๊ม - จับเวลาอัตโนมัติ
# 3. ปั๊มน้ำลงกระบอกตวงประมาณ 10-20 วินาที
# 4. กดปุ่ม 1 อีกครั้งเพื่อหยุดปั๊ม
# 5. อ่านปริมาตรจากกระบอกตวง
# 6. กดปุ่ม 2 แล้วพิมพ์ปริมาตรที่วัดได้ใน Thonny terminal
# 7. ทำซ้ำ 3-5 ครั้งเพื่อหาค่าเฉลี่ย
# 8. กดปุ่ม 3 เพื่อบันทึกค่า flow rate ลงไฟล์
#
# ==============================================================================
# Hardware Configuration:
# ==============================================================================
# - GPIO 21: Pump (PWM output)
# - GPIO 2:  Red LED (สถานะปั๊มทำงาน / Pump running indicator)
# - GPIO 4:  Green LED (บันทึกสำเร็จ / Save success indicator)
# - GPIO 34: Button 1 (Start/Stop pump)
# - GPIO 35: Button 2 (บันทึกปริมาตรที่วัดได้ / Record measured volume)
# - GPIO 39: Button 3 (บันทึกลงไฟล์ / Save to file)
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
# import-guarded: ถ้าไม่มีเฟิร์มแวร์ scilabpro สคริปต์ยังรันบน MicroPython ปกติได้
try:
    from scilabpro import stop_requested
except ImportError:
    stop_requested = None

# ==============================================================================
# การตั้งค่าขา GPIO (GPIO Pin Configuration)
# ==============================================================================
# ใช้ค่าจาก pins.py เพื่อความสอดคล้องกับมาตรฐาน TitraLab
# Using values from pins.py for TitraLab standard compatibility

# LED แสดงสถานะ (Status LEDs)
led_red = Pin(2, Pin.OUT)    # LED สีแดง - ปั๊มทำงาน (Red LED - pump running)
led_green = Pin(4, Pin.OUT)  # LED สีเขียว - บันทึกสำเร็จ (Green LED - save success)

# ปุ่มกด (Buttons)
# หมายเหตุ: GPIO34, 35, 39 เป็น input-only pin ไม่รองรับ internal pull resistors
# Note: GPIO34, 35, 39 are input-only, do NOT support internal pull resistors
# บอร์ด TitraLab ใช้ external pull-down resistor (10K ohm)
btn_start_stop = Pin(34, Pin.IN)  # ปุ่ม 1: เริ่ม/หยุดปั๊ม (Start/Stop pump)
btn_record = Pin(35, Pin.IN)       # ปุ่ม 2: บันทึกปริมาตร (Record volume)
btn_save = Pin(39, Pin.IN)         # ปุ่ม 3: บันทึกลงไฟล์ (Save to file)

# ปั๊ม (Pump) - PWM Control
pump_pin = Pin(21, Pin.OUT)
pump_pwm = PWM(pump_pin, freq=1000)
pump_pwm.duty(0)  # เริ่มต้นปิดปั๊ม (Start with pump off)

# ==============================================================================
# ตัวแปรควบคุม (Control Variables)
# ==============================================================================
pump_running = False           # สถานะปั๊ม (Pump state)
start_time = 0                 # เวลาเริ่มปั๊ม (us) (Pump start time)
elapsed_time = 0               # เวลาที่ปั๊มทำงาน (s) (Pump run time)
duty_cycle_percent = 100       # Duty Cycle (%) - 100% = เต็มกำลัง (full power)

# ตัวแปรสำหรับการสอบเทียบ (Calibration variables)
calibration_data = []          # รายการข้อมูลสอบเทียบ [(เวลา, ปริมาตร, flow_rate), ...]
current_volume = 0.0           # ปริมาตรที่วัดได้ในรอบปัจจุบัน (mL)

# Debounce control
debounce_time_ms = 300         # เวลา debounce (ms)
last_press_time = {34: 0, 35: 0, 39: 0}  # เวลากดปุ่มล่าสุดแต่ละปุ่ม

# ค่าปริมาตรที่นิสิตป้อน (Volume input by student)
# นิสิตจะพิมพ์ค่าปริมาตรผ่าน Thonny terminal เมื่อกดปุ่ม 2
# Student will type measured volume via Thonny terminal when pressing Button 2

# ==============================================================================
# ฟังก์ชันการสอบเทียบ (Calibration Functions)
# ==============================================================================

def toggle_pump():
    """
    สลับสถานะปั๊ม - เริ่ม/หยุด พร้อมจับเวลาอัตโนมัติ
    Toggle pump state - start/stop with automatic timing

    การคำนวณ Duty Cycle:
    - ESP32 PWM ใช้ค่า 0-1023 (10-bit resolution)
    - duty_value = (percent / 100) * 1023
    - 100% = 1023, 50% = 511, 0% = 0
    """
    global pump_running, start_time, elapsed_time

    if not pump_running:
        # เริ่มปั๊ม (Start pump)
        duty_value = int((duty_cycle_percent / 100) * 1023)
        pump_pwm.duty(duty_value)
        start_time = ticks_us()
        pump_running = True
        led_red.on()  # เปิด LED แดงแสดงปั๊มทำงาน (Turn on red LED)
        print("\n" + "=" * 50)
        print("เริ่มปั๊ม (PUMP STARTED)")
        print(f"Duty Cycle: {duty_cycle_percent}%")
        print("กดปุ่ม 1 อีกครั้งเพื่อหยุด (Press Button 1 again to stop)")
        print("=" * 50)
    else:
        # หยุดปั๊ม (Stop pump)
        pump_pwm.duty(0)
        stop_time = ticks_us()
        pump_running = False
        led_red.off()  # ปิด LED แดง (Turn off red LED)

        # คำนวณเวลาที่ปั๊มทำงาน (Calculate pump run time)
        elapsed_time = ticks_diff(stop_time, start_time) / 1_000_000

        print("\n" + "=" * 50)
        print("หยุดปั๊ม (PUMP STOPPED)")
        print(f"เวลาที่ปั๊มทำงาน (Elapsed time): {elapsed_time:.3f} วินาที (seconds)")
        print("-" * 50)
        print("ขั้นตอนถัดไป (Next steps):")
        print("1. อ่านปริมาตรจากกระบอกตวง (Read volume from graduated cylinder)")
        print("2. กดปุ่ม 2 แล้วพิมพ์ปริมาตรที่วัดได้ (Press Button 2, then type volume)")
        print("=" * 50)


def record_measurement():
    """
    บันทึกผลการวัดและคำนวณ flow rate
    Record measurement and calculate flow rate

    สูตร: flow_rate = volume / time (mL/s)
    """
    global calibration_data, current_volume

    if elapsed_time <= 0:
        print("\nข้อผิดพลาด: กรุณาปั๊มน้ำก่อน (Error: Please pump water first)")
        return

    # รับค่าปริมาตรจากนิสิตผ่าน Thonny terminal
    # Get measured volume from student via Thonny terminal
    print(f"\nเวลาที่ปั๊มทำงาน (Elapsed time): {elapsed_time:.3f} s")
    try:
        vol_str = input("พิมพ์ปริมาตรที่วัดได้ (Enter measured volume in mL): ")
        current_volume = float(vol_str)
    except ValueError:
        print("ข้อผิดพลาด: กรุณาพิมพ์ตัวเลข เช่น 5.2 (Error: Please enter a number, e.g. 5.2)")
        return

    if current_volume <= 0:
        print("ข้อผิดพลาด: ปริมาตรต้องมากกว่า 0 (Error: Volume must be > 0)")
        return

    # คำนวณ flow rate (Calculate flow rate)
    flow_rate = current_volume / elapsed_time

    # บันทึกข้อมูล (Record data)
    calibration_data.append((elapsed_time, current_volume, flow_rate))

    # แสดงผล (Display results)
    print("\n" + "=" * 50)
    print(f"บันทึกครั้งที่ (Record #{len(calibration_data)})")
    print("=" * 50)
    print(f"เวลา (Time):     {elapsed_time:.3f} s")
    print(f"ปริมาตร (Volume): {current_volume:.2f} mL")
    print(f"Flow Rate:        {flow_rate:.4f} mL/s")
    print("-" * 50)

    # แสดงค่าเฉลี่ย (Show average)
    if len(calibration_data) >= 1:
        avg_flow_rate = sum(d[2] for d in calibration_data) / len(calibration_data)
        print(f"ค่าเฉลี่ย Flow Rate (Average): {avg_flow_rate:.4f} mL/s")

        # คำนวณค่าเบี่ยงเบนมาตรฐาน (Calculate standard deviation)
        if len(calibration_data) >= 2:
            variance = sum((d[2] - avg_flow_rate) ** 2 for d in calibration_data) / len(calibration_data)
            std_dev = variance ** 0.5
            rsd = (std_dev / avg_flow_rate) * 100  # Relative Standard Deviation (%)
            print(f"ค่าเบี่ยงเบนมาตรฐาน (Std Dev): {std_dev:.4f} mL/s")
            print(f"RSD: {rsd:.2f}%")

            # คำแนะนำสำหรับนิสิต (Advice for students)
            if rsd > 5:
                print("\n*** คำเตือน: RSD > 5% - ค่าไม่สม่ำเสมอ ลองสอบเทียบใหม่")
                print("*** Warning: RSD > 5% - values inconsistent, try recalibration")
            else:
                print("\n*** ค่า RSD ดี! สามารถบันทึกลงไฟล์ได้ (Good RSD! Ready to save)")

    print(f"\nจำนวนข้อมูล (Data points): {len(calibration_data)}")
    print("กดปุ่ม 3 เพื่อบันทึกลงไฟล์ (Press Button 3 to save)")
    print("=" * 50)


def save_calibration():
    """
    บันทึกค่า flow rate ลงไฟล์ data_flowrate.txt
    Save flow rate to data_flowrate.txt file

    ไฟล์นี้จะถูกใช้ในโปรแกรมไทเทรตอัตโนมัติ
    This file will be used in automatic titration programs
    """
    if len(calibration_data) == 0:
        print("\nข้อผิดพลาด: ไม่มีข้อมูลให้บันทึก")
        print("Error: No data to save")
        return

    # คำนวณค่าเฉลี่ย (Calculate average)
    avg_flow_rate = sum(d[2] for d in calibration_data) / len(calibration_data)

    try:
        # บันทึกลงไฟล์ (Save to file)
        with open('data_flowrate.txt', 'w') as f:
            f.write("# TitraLab Pump Flow Rate Calibration Data\n")
            f.write("# ข้อมูลการสอบเทียบอัตราการไหลของปั๊ม\n")
            f.write(f"# จำนวนข้อมูล (Data points): {len(calibration_data)}\n")
            f.write(f"# Duty Cycle: {duty_cycle_percent}%\n")
            f.write("#\n")
            f.write("# รายละเอียดการวัดแต่ละครั้ง (Individual measurements):\n")
            f.write("# Time(s), Volume(mL), FlowRate(mL/s)\n")
            for i, (t, v, fr) in enumerate(calibration_data, 1):
                f.write(f"# {i}: {t:.3f}, {v:.2f}, {fr:.4f}\n")
            f.write("#\n")
            # บันทึกทศนิยม 4 ตำแหน่ง เพราะส่งผลต่อความแม่นยำของปริมาตรที่ปั๊ม
            # Use 4 decimal places - critical for precise transferred volume calculation
            f.write(f"flow_rate={avg_flow_rate:.4f}\n")

        # แสดงผลสำเร็จ (Show success)
        led_green.on()
        print("\n" + "=" * 50)
        print("บันทึกสำเร็จ! (SAVE SUCCESSFUL!)")
        print("=" * 50)
        print(f"ไฟล์: data_flowrate.txt")
        print(f"Flow Rate เฉลี่ย: {avg_flow_rate:.4f} mL/s")
        print("-" * 50)
        print("ค่านี้จะถูกใช้ในโปรแกรมไทเทรตอัตโนมัติ")
        print("(This value will be used in auto titration programs)")
        print("=" * 50)

        sleep_ms(1000)
        led_green.off()

    except Exception as e:
        print(f"\nข้อผิดพลาดในการบันทึก (Save error): {e}")
        # กระพริบ LED แดง (Blink red LED for error)
        for _ in range(3):
            led_red.on()
            sleep_ms(200)
            led_red.off()
            sleep_ms(200)


def check_button(pin_num, btn_pin, action_func):
    """
    ตรวจสอบการกดปุ่มพร้อม debounce
    Check button press with debounce
    """
    global last_press_time

    current_time = ticks_us() // 1000  # แปลงเป็น ms

    if btn_pin.value() == 1 and (current_time - last_press_time[pin_num]) > debounce_time_ms:
        last_press_time[pin_num] = current_time
        action_func()

        # รอจนกว่าปุ่มจะถูกปล่อย (Wait for button release)
        while btn_pin.value() == 1:
            sleep_ms(10)


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
print("\n" + "=" * 60)
print("  การสอบเทียบอัตราการไหลของปั๊ม (Pump Flow Rate Calibration)")
print("  สำหรับระบบไทเทรชันอัตโนมัติ TitraLab")
print("=" * 60)
print("\nความสำคัญ (Why This Matters):")
print("  - ปั๊มแต่ละตัวมี flow rate ไม่เท่ากัน")
print("  - การไทเทรตต้องการปริมาตรที่แม่นยำ")
print("  - ความผิดพลาด 0.1 mL = ความผิดพลาด 1-2% ในผลลัพธ์")
print()
print("ขั้นตอนการสอบเทียบ (Calibration Steps):")
print("  1. เตรียมกระบอกตวงและบีกเกอร์น้ำ")
print("  2. กดปุ่ม 1 เริ่มปั๊ม → ปั๊ม 10-20 วินาที → กดปุ่ม 1 หยุด")
print("  3. อ่านปริมาตรจากกระบอกตวง")
print("  4. กดปุ่ม 2 แล้วพิมพ์ปริมาตรที่วัดได้ (ทำซ้ำ 3-5 ครั้ง)")
print("  5. กดปุ่ม 3 บันทึกลงไฟล์")
print()
print("การควบคุม (Controls):")
print(f"  [ปุ่ม 1] เริ่ม/หยุดปั๊ม | Duty Cycle: {duty_cycle_percent}%")
print("  [ปุ่ม 2] บันทึกผลการวัด")
print("  [ปุ่ม 3] บันทึกลงไฟล์ data_flowrate.txt")
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

        # ตรวจสอบปุ่มทั้งสาม (Check all three buttons)
        check_button(34, btn_start_stop, toggle_pump)
        check_button(35, btn_record, record_measurement)
        check_button(39, btn_save, save_calibration)

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

    # แสดงสรุปข้อมูลที่เก็บได้ (Show data summary)
    if len(calibration_data) > 0:
        avg_fr = sum(d[2] for d in calibration_data) / len(calibration_data)
        print(f"\nสรุป: เก็บข้อมูล {len(calibration_data)} ครั้ง")
        print(f"Flow Rate เฉลี่ย: {avg_fr:.4f} mL/s")

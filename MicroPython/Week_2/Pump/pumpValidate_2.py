# ==============================================================================
# pumpValidate_2.py - การตรวจสอบปริมาตรปั๊มแบบเป็นช่วง (Intermittent Pump Validation)
# ==============================================================================
# โปรแกรมนี้ตรวจสอบความแม่นยำของปั๊มโดยปั๊มเป็นช่วงๆ (ปั๊ม-หยุด-ปั๊ม)
# This program validates pump accuracy using intermittent pumping (pump-pause-pump)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การควบคุมปั๊มแบบเป็นช่วงๆ
# 2. เข้าใจความแตกต่างระหว่างการปั๊มต่อเนื่องและเป็นช่วง
# 3. ประยุกต์ใช้ในการไทเทรตใกล้จุดสมมูล
#
# ความสำคัญในการไทเทรต (Importance in Titration):
# - ใกล้จุดสมมูล (equivalence point) ต้องเติมสารไทแทรนต์ทีละน้อย
# - การปั๊มเป็นช่วงช่วยให้ pH stabilize ก่อนอ่านค่า
# - รูปแบบ: ปั๊ม 1 วินาที → หยุด 2 วินาที → วัด pH → ทำซ้ำ
#
# Hardware Configuration:
# - GPIO 21: Pump (PWM output)
# - GPIO 34: Button 1 (Start pump) - input-only, ต้องใช้ external pull-down
# ==============================================================================

from machine import Pin, PWM, Timer
from time import ticks_us, ticks_diff, sleep_ms

# ==============================================================================
# การตั้งค่าพินต่างๆ (Pin Configuration)
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull resistors
# Note: GPIO34 is input-only, does NOT support internal pull resistors
# ต้องใช้ตัวต้านทาน pull-down ภายนอก (10K ohm)
# Must use external pull-down resistor (10K ohm)
button_1_pin = Pin(34, Pin.IN)  # ปุ่มเริ่มปั๊ม (Start pump button)
pump_pin = Pin(21, Pin.OUT)     # พินปั๊ม GPIO21 (Pump pin GPIO21)

# ==============================================================================
# การตั้งค่า PWM และตัวจับเวลา (PWM and Timer Setup)
# ==============================================================================
# PWM ควบคุมความเร็วปั๊มโดยการเปิด-ปิดสัญญาณอย่างรวดเร็ว
# PWM controls pump speed by rapidly switching signal on/off
pump_pwm = PWM(pump_pin, freq=1000)  # สร้าง PWM ที่ 1000 Hz (Create PWM at 1000 Hz)
pump_pwm.duty(0)                      # เริ่มต้นปิดปั๊ม (Start with pump off)
timer = Timer(0)                      # สร้างตัวจับเวลา (Create timer)

# ==============================================================================
# ตัวแปรควบคุม (Control Variables)
# ==============================================================================
running = False           # สถานะปั๊ม (Pump running state)
debounce_time = 200       # เวลา debounce (ms)
last_press_time = 0       # เวลากดปุ่มล่าสุด (Last button press time)

# ==============================================================================
# ค่าคงที่สำหรับการคำนวณปริมาตร (Volume Calculation Constants)
# ==============================================================================
# ค่าเหล่านี้ได้จากการ calibrate ปั๊ม (These values come from pump calibration)
flow_rate_per_cycle = 0.2772  # ปริมาตรต่อรอบ 1 วินาที (mL/s) - Volume per 1-second cycle
target_volume = 10.0          # ปริมาตรเป้าหมาย (mL) - Target volume
total_volume = 0              # ปริมาตรสะสม (mL) - Accumulated volume
duty_cycle_percent = 100      # Duty cycle (%) - ความเร็วเต็มที่
total_elapsed_time = 0        # เวลารวมที่ปั๊มทำงาน (s) - Total pump run time

# การตั้งค่าการปั๊มเป็นช่วง (Intermittent Pumping Settings)
pump_duration = 1.0           # เวลาปั๊มแต่ละรอบ (s) - Pump duration per cycle
pause_duration = 2.0          # เวลาหยุดระหว่างรอบ (s) - Pause between cycles

# ==============================================================================
# ฟังก์ชัน Precise Sleep (Precise Sleep Function)
# ==============================================================================
def precise_sleep(duration):
    """
    หยุดทำงานชั่วคราวด้วยความแม่นยำระดับไมโครวินาที
    Pause execution with microsecond precision

    พารามิเตอร์ (Parameters):
    - duration: เวลาที่ต้องการหยุด (วินาที) / Time to sleep (seconds)

    หมายเหตุ: ใช้ busy-wait loop เพื่อความแม่นยำสูงสุด
    Note: Uses busy-wait loop for maximum precision
    """
    start_time = ticks_us()
    while ticks_diff(ticks_us(), start_time) < duration * 1_000_000:
        pass  # Busy-wait loop

# ==============================================================================
# ฟังก์ชันเริ่มปั๊ม (Start Pump Function)
# ==============================================================================
def start_pump():
    """
    เริ่มปั๊มแบบเป็นช่วงๆ จนถึงปริมาตรเป้าหมาย
    Start intermittent pumping until target volume is reached

    รูปแบบการทำงาน (Operation Pattern):
    1. ปั๊ม 1 วินาที (Pump for 1 second)
    2. หยุด 2 วินาที (Pause for 2 seconds) - ให้ pH stabilize
    3. ทำซ้ำจนถึงเป้าหมาย (Repeat until target reached)
    """
    global running, total_volume, total_elapsed_time

    if not running:  # ตรวจสอบว่าปั๊มยังไม่ทำงาน (Check pump not running)
        duty_cycle = int((duty_cycle_percent / 100) * 1023)
        running = True
        cycle_elapsed_time = 0
        cycle_count = 0

        print("=== เริ่มปั๊มแบบเป็นช่วง (Intermittent Pump Started) ===")
        print(f"เป้าหมาย (Target): {target_volume:.2f} mL")
        print(f"รูปแบบ (Pattern): ปั๊ม {pump_duration}s → หยุด {pause_duration}s")

        # ทำงานจนกว่าจะถึงปริมาตรเป้าหมาย
        # Run until target volume is reached
        while total_volume < target_volume:
            cycle_count += 1

            # ตรวจสอบรอบสุดท้าย (Check if last cycle)
            if total_volume + flow_rate_per_cycle > target_volume:
                # ปรับเวลาสำหรับรอบสุดท้าย (Adjust time for last cycle)
                remaining_volume = target_volume - total_volume
                run_time_adjusted = remaining_volume / flow_rate_per_cycle
                pump_pwm.duty(duty_cycle)
                precise_sleep(run_time_adjusted)
                total_volume += remaining_volume
                cycle_elapsed_time += run_time_adjusted
                break

            # ปั๊ม 1 วินาที (Pump for 1 second)
            pump_pwm.duty(duty_cycle)
            precise_sleep(pump_duration)
            total_volume += flow_rate_per_cycle
            cycle_elapsed_time += pump_duration
            print(f"รอบ (Cycle) {cycle_count}: {total_volume:.2f} mL")

            # หยุด 2 วินาที (Pause for 2 seconds)
            pump_pwm.duty(0)
            precise_sleep(pause_duration)

        total_elapsed_time += cycle_elapsed_time
        stop_pump()

# ==============================================================================
# ฟังก์ชันหยุดปั๊ม (Stop Pump Function)
# ==============================================================================
def stop_pump():
    """
    หยุดปั๊มและแสดงผลสรุป
    Stop pump and display summary
    """
    global running

    if running:
        pump_pwm.duty(0)  # หยุดปั๊ม (Stop pump)
        running = False

        print("=== หยุดปั๊ม (Pump Stopped) ===")
        print(f"ปริมาตรรวม (Total volume): {total_volume:.2f} mL")
        print(f"เวลาปั๊มรวม (Total pump time): {total_elapsed_time:.2f} วินาที (seconds)")

# ==============================================================================
# ฟังก์ชันตรวจสอบปุ่ม (Button Check Function)
# ==============================================================================
def check_buttons(t):
    """
    Callback สำหรับ Timer - ตรวจสอบการกดปุ่มพร้อม debounce
    Timer callback - check button press with debounce
    """
    global last_press_time

    current_time = ticks_us() // 1000  # แปลงเป็น ms (Convert to ms)

    # ตรวจสอบปุ่มพร้อม debounce (Check button with debounce)
    if button_1_pin.value() == 1 and not running:
        if (current_time - last_press_time) > debounce_time:
            last_press_time = current_time
            start_pump()

# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
print("=" * 50)
print("การตรวจสอบปริมาตรปั๊มแบบเป็นช่วง")
print("(Intermittent Pump Volume Validation)")
print(f"ปริมาตรเป้าหมาย (Target volume): {target_volume:.2f} mL")
print(f"Flow rate: {flow_rate_per_cycle:.4f} mL/s")
print(f"รูปแบบ: ปั๊ม {pump_duration}s → หยุด {pause_duration}s")
print("กดปุ่ม 1 เพื่อเริ่ม (Press Button 1 to start)")
print("=" * 50)

try:
    # ตรวจสอบปุ่มทุก 1 ms (Check button every 1 ms)
    timer.init(period=1, mode=Timer.PERIODIC, callback=check_buttons)

    # ลูปหลัก (Main loop)
    while True:
        precise_sleep(0.01)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    pump_pwm.duty(0)
    pump_pwm.deinit()
    timer.deinit()
    print("ปิดปั๊มและ Timer แล้ว (Pump and Timer released)")

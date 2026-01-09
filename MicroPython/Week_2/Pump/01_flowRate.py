# ==============================================================================
# 01_flowRate.py - การควบคุมอัตราการไหลของปั๊ม (Pump Flow Rate Control)
# ==============================================================================
# โปรแกรมนี้สาธิตการควบคุมปั๊มด้วย PWM และวัดเวลาการทำงาน
# This program demonstrates pump control with PWM and timing measurement
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้ PWM (Pulse Width Modulation) สำหรับควบคุมความเร็วปั๊ม
# 2. เข้าใจ Duty Cycle และผลต่ออัตราการไหล
# 3. วัดเวลาการทำงานของปั๊มเพื่อคำนวณปริมาตร
#
# ความสำคัญในการไทเทรต (Importance in Titration):
# ในการไทเทรตอัตโนมัติ ต้องควบคุมปริมาณสารไทแทรนต์ (titrant) อย่างแม่นยำ
# - Duty Cycle 100% = ไหลเร็ว (ใช้ตอนเริ่มไทเทรต)
# - Duty Cycle ต่ำ = ไหลช้า (ใช้ใกล้จุดสมมูล/equivalence point)
#
# Hardware Configuration:
# - GPIO 21: Pump (PWM output)
# - GPIO 34: Button 1 (Start/Stop)
# ==============================================================================

from machine import Pin, PWM
from time import ticks_us, ticks_diff, sleep_ms

# ==============================================================================
# การตั้งค่าปั๊ม (Pump Setup)
# ==============================================================================
# กำหนด GPIO21 สำหรับปั๊ม (PWM output)
# Set GPIO21 for pump (PWM output)
pump_pin = Pin(21, Pin.OUT)

# ==============================================================================
# การตั้งค่าปุ่มกด (Button Setup)
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull resistors
# Note: GPIO34 is input-only, does NOT support internal pull resistors
# ต้องใช้ตัวต้านทาน pull-down ภายนอก (10K ohm)
# Must use external pull-down resistor (10K ohm)
button_1_pin = Pin(34, Pin.IN)

# ==============================================================================
# การตั้งค่า PWM (PWM Setup)
# ==============================================================================
# PWM (Pulse Width Modulation) ควบคุมความเร็วปั๊มโดยการเปิด-ปิดสัญญาณอย่างรวดเร็ว
# PWM controls pump speed by rapidly switching signal on/off
# - ความถี่ (Frequency) 1000 Hz = 1000 รอบ/วินาที
# - Duty Cycle = เปอร์เซ็นต์เวลาที่สัญญาณเปิด (0-1023 หรือ 0-100%)
pump_pwm = PWM(pump_pin, freq=1000)
pump_pwm.duty(0)  # เริ่มต้นปิดปั๊ม (Start with pump off)

# ==============================================================================
# ตัวแปรควบคุม (Control Variables)
# ==============================================================================
pump_running = False      # สถานะปั๊ม (Pump state)
start_time = 0            # เวลาเริ่มต้น (Start time)
stop_time = 0             # เวลาหยุด (Stop time)
duty_cycle_percent = 100  # Duty Cycle (%) - 100% = เต็มกำลัง
last_press_time = 0       # เวลากดปุ่มล่าสุด (Last button press time)
debounce_time_ms = 200    # เวลา debounce (ms)

# ==============================================================================
# ฟังก์ชัน Toggle ปั๊ม (Pump Toggle Function)
# ==============================================================================
def toggle_pump():
    """
    สลับสถานะปั๊ม - เริ่ม/หยุด
    Toggle pump state - start/stop

    การคำนวณ Duty Cycle:
    - ESP32 PWM ใช้ค่า 0-1023 (10-bit)
    - duty_value = (percent / 100) × 1023
    - 100% → 1023, 50% → 511, 0% → 0
    """
    global pump_running, start_time, stop_time

    if not pump_running:
        # เริ่มปั๊ม (Start pump)
        duty_cycle_value = int((duty_cycle_percent / 100) * 1023)
        pump_pwm.duty(duty_cycle_value)
        start_time = ticks_us()
        pump_running = True
        print(f"เริ่มปั๊ม (Pump started) - Duty Cycle: {duty_cycle_percent}%")
    else:
        # หยุดปั๊ม (Stop pump)
        pump_pwm.duty(0)
        stop_time = ticks_us()
        pump_running = False

        # คำนวณเวลาที่ปั๊มทำงาน (Calculate pump run time)
        elapsed_time = ticks_diff(stop_time, start_time) / 1_000_000
        print(f"หยุดปั๊ม (Pump stopped)")
        print(f"เวลาที่ปั๊มทำงาน (Elapsed time): {elapsed_time:.2f} วินาที (seconds)")

        # คำนวณปริมาตรโดยประมาณ (ต้อง calibrate ก่อน)
        # Estimate volume (requires calibration)
        # flow_rate = X mL/s ที่ duty cycle นี้ (need to calibrate)
        # volume = flow_rate × elapsed_time

# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
print("=" * 50)
print("การควบคุมอัตราการไหลของปั๊ม (Pump Flow Rate Control)")
print("กดปุ่ม 1 เพื่อเริ่ม/หยุดปั๊ม (Press Button 1 to start/stop)")
print(f"Duty Cycle: {duty_cycle_percent}%")
print("=" * 50)

try:
    while True:
        current_time = ticks_us() // 1000  # เวลาปัจจุบัน (ms)

        # ตรวจสอบการกดปุ่มพร้อม debounce
        # Check button press with debounce
        if button_1_pin.value() == 1 and (current_time - last_press_time) > debounce_time_ms:
            last_press_time = current_time
            toggle_pump()

            # รอจนกว่าปุ่มจะถูกปล่อย (Wait for button release)
            while button_1_pin.value() == 1:
                sleep_ms(10)  # ใช้ sleep แทน busy wait

        sleep_ms(10)  # ลด CPU usage

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    pump_pwm.duty(0)
    pump_pwm.deinit()
    print("ปิดปั๊มและ PWM แล้ว (Pump and PWM released)")

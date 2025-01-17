from machine import Pin, PWM
from time import ticks_us, ticks_diff

# กำหนดพินสำหรับปั๊มและปุ่ม
pump_pin = Pin(21, Pin.OUT)  # GPIO26 เชื่อมต่อปั๊ม
button_1_pin = Pin(34, Pin.IN, Pin.PULL_DOWN)  # GPIO34 สำหรับ BUTTON_1

# ตั้งค่า PWM สำหรับควบคุมปั๊ม
pump_pwm = PWM(pump_pin, freq=1000)  # ตั้งค่าความถี่ 1000 Hz
pump_pwm.duty(0)  # เริ่มต้นที่ duty cycle = 0 (ปั๊มหยุดทำงาน)

# ตัวแปรควบคุมสถานะและเวลา
pump_running = False  # สถานะของปั๊ม (True = ทำงาน, False = หยุด)
start_time = 0  # เวลาเริ่มต้น
stop_time = 0  # เวลาหยุดทำงาน
duty_cycle_percent = 100  # ค่า Duty Cycle (หน่วย: %)
last_press_time = 0  # เวลากดปุ่มล่าสุด
debounce_time_ms = 200  # กำหนดเวลา debounce 200 มิลลิวินาที

# ฟังก์ชันสำหรับเริ่มและหยุดปั๊ม
def toggle_pump():
    global pump_running, start_time, stop_time

    if not pump_running:
        # เริ่มปั๊ม
        duty_cycle_value = int((duty_cycle_percent / 100) * 1023)  # แปลงเปอร์เซ็นต์เป็นค่า PWM
        pump_pwm.duty(duty_cycle_value)  # ตั้งค่า duty cycle
        start_time = ticks_us()  # บันทึกเวลาเริ่มต้น
        pump_running = True
        print(f"Pump started with duty cycle: {duty_cycle_percent}%")
    else:
        # หยุดปั๊ม
        pump_pwm.duty(0)  # หยุดปั๊ม
        stop_time = ticks_us()  # บันทึกเวลาหยุด
        pump_running = False

        # คำนวณเวลาที่ปั๊มทำงาน
        elapsed_time = ticks_diff(stop_time, start_time) / 1_000_000  # แปลงเป็นวินาที
        print(f"Pump stopped. Elapsed time: {elapsed_time:.2f} seconds")

# ตรวจสอบสถานะของปุ่ม
while True:
    current_time = ticks_us() // 1000  # เวลาปัจจุบันในหน่วยมิลลิวินาที
    if button_1_pin.value() == 1 and (current_time - last_press_time) > debounce_time_ms:
        last_press_time = current_time  # บันทึกเวลาที่กดปุ่มล่าสุด
        toggle_pump()  # เรียกใช้ฟังก์ชัน toggle_pump

        # รอจนกว่าปุ่มจะถูกปล่อย (ป้องกันการลั่น)
        while button_1_pin.value() == 1:
            pass

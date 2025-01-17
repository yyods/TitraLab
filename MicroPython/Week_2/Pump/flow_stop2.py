from machine import Pin, PWM, Timer
from time import ticks_us, ticks_diff, sleep_ms

# กำหนดพินต่างๆ
button_1_pin = Pin(34, Pin.IN, Pin.PULL_DOWN)  # ปุ่มกดสำหรับเริ่มการทำงานของปั๊ม
pump_pin = Pin(21, Pin.OUT)  # พินที่เชื่อมต่อกับปั๊ม

# ตั้งค่าเริ่มต้นสำหรับปั๊ม และตัวจับเวลา
pump_pwm = PWM(pump_pin, freq=1000)  # สร้างสัญญาณ PWM ที่ควบคุมปั๊ม
pump_pwm.duty(0)  # เริ่มต้นปั๊มในสถานะหยุด (duty cycle = 0)
timer = Timer(0)  # สร้างตัวจับเวลา
running = False  # ตัวแปรบอกสถานะว่าปั๊มกำลังทำงานหรือไม่
debounce_time = 200  # กำหนดเวลา debounce (หน่วย: มิลลิวินาที)
last_press_time = 0  # เวลาที่กดปุ่มครั้งล่าสุด

# กำหนดค่าคงที่
flow_rate_per_cycle = 0.2772  # ปริมาตรน้ำที่ไหลออกต่อรอบ
target_volume = 10.0  # ปริมาตรน้ำที่ต้องการ
total_volume = 0  # ปริมาตรน้ำที่ไหลออกมาทั้งหมด
duty_cycle_percent = 100  # ใช้ค่า duty cycle 100%
total_elapsed_time = 0  # เวลาเริ่มต้นที่ปั๊มทำงาน

# ฟังก์ชันหยุดทำงานชั่วคราว (sleep) ที่แม่นยำ
def precise_sleep(duration):
    start_time = ticks_us()
    while ticks_diff(ticks_us(), start_time) < duration * 1_000_000:
        pass  # Busy-wait loop

def start_pump():
    global running, total_volume, total_elapsed_time
    if not running:  # ตรวจสอบว่าปั๊มยังไม่ทำงาน
        duty_cycle = int((duty_cycle_percent / 100) * 1023)
        running = True  # เปลี่ยนสถานะเป็นปั๊มกำลังทำงาน
        cycle_elapsed_time = 0  # ตัวแปรเก็บเวลารวมของรอบปัจจุบัน

        while total_volume < target_volume:  # ทำงานจนกว่าจะถึงปริมาตรที่ต้องการ
            if total_volume + flow_rate_per_cycle > target_volume:  # หากรอบสุดท้ายปริมาตรเกินเป้าหมาย
                flow_rate_per_cycle_adjusted = target_volume - total_volume  # ปรับปริมาตรในรอบสุดท้าย
                run_time_adjusted = flow_rate_per_cycle_adjusted / flow_rate_per_cycle  # คำนวณเวลาปั๊มที่ต้องการ
                pump_pwm.duty(duty_cycle)
                precise_sleep(run_time_adjusted)  # ปั๊มด้วยเวลาที่ปรับ
                total_volume += flow_rate_per_cycle_adjusted  # เพิ่มปริมาตรน้ำที่ไหลออกมา
                cycle_elapsed_time += run_time_adjusted  # เก็บเวลาที่ใช้ในรอบสุดท้าย
                break  # จบรอบเมื่อถึงปริมาตรที่ต้องการ

            pump_pwm.duty(duty_cycle)  # เริ่มปั๊ม
            
            precise_sleep(1.0)  # ปั๊มด้วยเวลาปกติ 1 วินาที
            total_volume += flow_rate_per_cycle  # เพิ่มปริมาตรน้ำที่ไหลออกมาในแต่ละรอบ
            cycle_elapsed_time += 1.0  # เพิ่มเวลาที่ใช้ในรอบนี้
            print(f"Current volume: {total_volume:.2f} ml")  # แสดงผลปริมาตรในคอนโซล

            pump_pwm.duty(0)  # หยุดปั๊มชั่วคราว
            precise_sleep(2)  # หยุด x วินาที

        total_elapsed_time += cycle_elapsed_time  # เก็บเวลารวมที่ปั๊มทำงาน
        stop_pump(duty_cycle_percent, total_volume, total_elapsed_time)  # หยุดปั๊มหลังจากเวลาที่กำหนด

def stop_pump(duty_cycle_percent, total_volume, total_elapsed_time):
    global running
    if running:  # หากปั๊มกำลังทำงาน
        pump_pwm.duty(0)  # หยุดปั๊ม (duty cycle = 0)
        running = False  # เปลี่ยนสถานะเป็นปั๊มหยุดทำงาน
        
        # แสดงข้อมูลในคอนโซล
        print(f"Pump stopped. Total volume: {total_volume:.2f} ml")
        print(f"Total elapsed time: {total_elapsed_time:.2f} seconds")  # แสดงเวลารวมที่ปั๊มทำงาน

def check_buttons(timer):
    global last_press_time
    current_time = ticks_us() // 1000  # แปลงเวลาเป็นมิลลิวินาที
    if button_1_pin.value() == 1 and not running and (current_time - last_press_time) > debounce_time:  # ตรวจสอบ debounce
        last_press_time = current_time  # อัปเดตเวลาเมื่อปุ่มถูกกด
        start_pump()  # เริ่มปั๊ม

# ตรวจสอบการกดปุ่มทุก ๆ 1 มิลลิวินาที
timer.init(period=1, mode=Timer.PERIODIC, callback=check_buttons)

while True:
    precise_sleep(0.01) 
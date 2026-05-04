# ==============================================================================
# 02c_titration_alert_system.py - ระบบแจ้งเตือนการไทเทรชัน
# (Titration Alert System)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้ Composition และบริบทการไทเทรชัน
# Week 1: Learn Composition and Titration Context
#
# ต่อยอดจากไฟล์ 02b_adding_buzzer.py
# Building upon 02b_adding_buzzer.py
#
# สิ่งใหม่ในไฟล์นี้ (What's new in this file):
#   - ใช้ Composition รวม objects ใน class เดียว
#   - เพิ่มบริบทการไทเทรชัน (titration context)
#   - State management สำหรับกระบวนการไทเทรชัน
#   - ตัวอย่างการออกแบบระบบควบคุมห้องปฏิบัติการ
#
# การทำงาน (How it works):
#   - กดปุ่ม Start: เริ่มการไทเทรชัน (LED เขียวกระพริบ)
#   - กดปุ่ม Stop: หยุดการไทเทรชัน (LED แดงติด)
#   - กดค้างปุ่ม Exit: ออกจากโปรแกรม
#
# บริบทห้องปฏิบัติการ (Lab Context):
#   ในการไทเทรชันจริง LED และ Buzzer จะแสดงสถานะ:
#   - LED เขียวกระพริบ = กำลังหยดสารละลาย (dispensing)
#   - LED แดง = หยุด/รอ หรือถึงจุดสมมูล (endpoint)
#   - เสียง Buzzer = แจ้งเตือนเมื่อถึงจุดสมมูล
#
# ==============================================================================

from machine import Pin, PWM
import time


# ==============================================================================
# ส่วนที่ 1: นิยาม Classes พื้นฐาน (Basic Class Definitions)
# ==============================================================================
# Classes เหล่านี้เหมือนกับ 02b แต่มีการเพิ่ม blink() ใน LED
# These classes are same as 02b but added blink() to LED

class LED:
    """คลาสควบคุม LED (LED Control Class)"""

    def __init__(self, pin_number, name="LED"):
        self.pin_number = pin_number
        self.name = name
        self.is_on = False
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)
        print(f"LED '{name}' พร้อมที่ GPIO{pin_number}")

    def on(self):
        self._pin.value(1)
        self.is_on = True

    def off(self):
        self._pin.value(0)
        self.is_on = False

    def toggle(self):
        """สลับสถานะ - ใช้สำหรับกระพริบ (Toggle - used for blinking)"""
        if self.is_on:
            self.off()
        else:
            self.on()
        return self.is_on

    def blink(self, times=1, delay=0.3):
        """
        กระพริบ LED (Blink LED)

        ใช้แสดงว่ากำลังทำงาน เช่น กำลังหยดสารละลาย
        Used to show activity, e.g., dispensing solution

        Args:
            times (int): จำนวนครั้ง (number of times)
            delay (float): เวลาหน่วง วินาที (delay in seconds)
        """
        for _ in range(times):
            self.on()
            time.sleep(delay)
            self.off()
            time.sleep(delay)

    def deinit(self):
        self.off()
        print(f"ปิด LED '{self.name}'")


class Button:
    """คลาสอ่านปุ่มกด (Button Class)"""

    def __init__(self, pin_number, name="Button", debounce_ms=200):
        self.pin_number = pin_number
        self.name = name
        self.debounce_ms = debounce_ms
        self._pin = Pin(pin_number, Pin.IN)
        self._last_press_time = 0
        self._was_pressed = False
        self._press_start_time = 0
        print(f"Button '{name}' พร้อมที่ GPIO{pin_number}")

    def is_active(self):
        return self._pin.value() == 1

    def is_pressed(self):
        current_time = time.ticks_ms()
        is_active_now = self.is_active()

        if is_active_now and not self._was_pressed:
            if time.ticks_diff(current_time, self._last_press_time) > self.debounce_ms:
                self._last_press_time = current_time
                self._was_pressed = True
                return True

        if not is_active_now:
            self._was_pressed = False

        return False

    def is_held(self, seconds):
        """
        ตรวจสอบว่าปุ่มถูกกดค้าง (Check if button is held)

        ใช้สำหรับการยืนยันการออกจากโปรแกรม
        Used for confirming program exit

        Args:
            seconds (float): เวลาที่ต้องกดค้าง (time to hold)

        Returns:
            bool: True ถ้ากดค้างนานพอ (if held long enough)
        """
        if not self.is_active():
            self._press_start_time = 0
            return False

        if self._press_start_time == 0:
            self._press_start_time = time.ticks_ms()

        held_time = time.ticks_diff(time.ticks_ms(), self._press_start_time)
        return held_time >= (seconds * 1000)

    def get_hold_time(self):
        """อ่านเวลาที่กดค้าง (Get hold time in seconds)"""
        if not self.is_active() or self._press_start_time == 0:
            return 0
        return time.ticks_diff(time.ticks_ms(), self._press_start_time) / 1000


class Buzzer:
    """คลาสควบคุม Buzzer (Buzzer Class)"""

    def __init__(self, pin_number=26):
        self.pin_number = pin_number
        self._pin = Pin(pin_number, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(2000)
        self._pwm.duty(0)
        self._initialized = True
        print(f"Buzzer พร้อมที่ GPIO{pin_number}")

    def play_tone(self, freq, duration_ms, duty=512):
        self._pwm.freq(freq)
        self._pwm.duty(duty)
        time.sleep_ms(duration_ms)
        self._pwm.duty(0)

    def beep(self, duration_ms=100):
        self.play_tone(2000, duration_ms)

    def success_sound(self):
        """เสียงสำเร็จ - ใช้เมื่อไทเทรชันเสร็จสิ้น (Success - titration complete)"""
        for freq in [523, 659, 784, 1047]:
            self.play_tone(freq, 100)

    def error_sound(self):
        """เสียงผิดพลาด - ใช้เมื่อเกิดข้อผิดพลาด (Error - when error occurs)"""
        for freq in [800, 400, 200]:
            self.play_tone(freq, 150)

    def warning_sound(self):
        """เสียงเตือน - ใช้เมื่อหยุดกระบวนการ (Warning - process stopped)"""
        for _ in range(2):
            self.play_tone(1500, 100)
            time.sleep_ms(100)

    def endpoint_sound(self):
        """
        เสียงแจ้งจุดสมมูล (Endpoint detection sound)

        ใช้เมื่อตรวจพบจุดสมมูลในการไทเทรชัน
        Used when endpoint is detected in titration
        """
        for _ in range(3):
            self.play_tone(2500, 150)
            time.sleep_ms(100)

    def mute(self):
        self._pwm.duty(0)

    def deinit(self):
        if self._initialized:
            self.mute()
            self._pwm.deinit()
            self._initialized = False
            print("ปิด Buzzer")


# ==============================================================================
# [ใหม่] ส่วนที่ 2: TitrationAlertSystem Class - ใช้ Composition
# [NEW] Part 2: TitrationAlertSystem Class - Using Composition
# ==============================================================================

class TitrationAlertSystem:
    """
    ระบบแจ้งเตือนการไทเทรชัน (Titration Alert System)

    นี่คือตัวอย่างการใช้ "Composition" - การรวม objects หลายตัวใน class เดียว
    This is an example of "Composition" - combining multiple objects in one class

    *** Composition คืออะไร? (What is Composition?) ***

    Composition หมายถึง class หนึ่ง "มี" (has) objects ของ class อื่น
    เป็นสมาชิก แทนที่จะ "เป็น" (is) ประเภทของ class อื่น

    Composition means a class "has" objects of other classes
    as members, rather than "is" a type of another class

    ตัวอย่าง:
    - TitrationAlertSystem "มี" LED, Button, Buzzer
    - TitrationAlertSystem ไม่ "เป็น" LED

    ระบบนี้จำลองการควบคุมห้องปฏิบัติการสำหรับการไทเทรชัน:
    This system simulates lab control for titration:

    - LED สีเขียว: แสดงสถานะ "กำลังไทเทรต" (titrating)
    - LED สีแดง: แสดงสถานะ "หยุด" หรือ "ถึงจุดสมมูล" (stopped/endpoint)
    - Buzzer: เสียงแจ้งเตือนสถานะต่างๆ
    - ปุ่ม 3 ปุ่ม: ควบคุมกระบวนการไทเทรชัน
    """

    # === สถานะของการไทเทรชัน (Titration States) ===
    STATE_IDLE = "IDLE"           # รอเริ่ม (waiting to start)
    STATE_RUNNING = "RUNNING"     # กำลังไทเทรต (titrating)
    STATE_PAUSED = "PAUSED"       # หยุดชั่วคราว (paused)
    STATE_COMPLETE = "COMPLETE"   # เสร็จสิ้น (completed)

    def __init__(self):
        """
        สร้างระบบแจ้งเตือนการไทเทรชัน (Initialize titration alert system)

        *** Composition ในทางปฏิบัติ ***
        เราสร้าง objects ของ LED, Button, Buzzer และเก็บเป็น attributes
        We create objects of LED, Button, Buzzer and store as attributes
        """
        print("=" * 60)
        print("กำลังสร้างระบบแจ้งเตือนการไทเทรชัน")
        print("(Creating Titration Alert System)")
        print("=" * 60)

        # === สร้าง LED objects (Create LED objects) ===
        # ใน Composition เราเก็บ objects เป็น instance variables
        # In Composition we store objects as instance variables
        self.led_status = LED(4, "Status-Green")   # แสดงสถานะการทำงาน
        self.led_alert = LED(2, "Alert-Red")       # แสดงการเตือน/หยุด

        # === สร้าง Button objects (Create Button objects) ===
        self.btn_start = Button(34, "Start/Resume")
        self.btn_stop = Button(35, "Stop/Pause")
        self.btn_exit = Button(39, "Exit")

        # === สร้าง Buzzer object (Create Buzzer object) ===
        self.buzzer = Buzzer(26)

        # === สถานะของระบบ (System State) ===
        # State management เป็นสิ่งสำคัญในระบบ embedded
        # State management is crucial in embedded systems
        self.state = self.STATE_IDLE
        self.titration_count = 0  # จำนวนครั้งที่เริ่มไทเทรต

        # แสดงว่าระบบพร้อม (Show system is ready)
        print("\nระบบพร้อมใช้งาน (System ready)")
        print(f"สถานะเริ่มต้น: {self.state}")
        self.buzzer.beep()

    def start_titration(self):
        """
        เริ่มการไทเทรชัน (Start titration)

        ในการไทเทรชันจริง ขั้นตอนนี้จะ:
        - เปิดปั๊มหยดสารละลาย
        - เริ่มอ่านค่า pH/conductivity
        - บันทึกข้อมูล

        In real titration, this step would:
        - Turn on dispensing pump
        - Start reading pH/conductivity
        - Log data
        """
        if self.state != self.STATE_RUNNING:
            self.titration_count += 1
            print(f"\n>>> เริ่มการไทเทรชัน #{self.titration_count}")
            print(f"    (Starting titration #{self.titration_count})")

            self.state = self.STATE_RUNNING
            self.led_alert.off()
            self.led_status.on()
            self.buzzer.success_sound()

    def stop_titration(self):
        """
        หยุดการไทเทรชัน (Stop titration)

        ในการไทเทรชันจริง ขั้นตอนนี้จะ:
        - หยุดปั๊ม
        - บันทึกค่าปัจจุบัน
        - รอคำสั่งต่อไป

        In real titration, this step would:
        - Stop pump
        - Record current value
        - Wait for next command
        """
        if self.state == self.STATE_RUNNING:
            print("\n>>> หยุดการไทเทรชัน (Stopping titration)")

            self.state = self.STATE_PAUSED
            self.led_status.off()
            self.led_alert.on()
            self.buzzer.warning_sound()

    def show_status(self):
        """แสดงสถานะระบบ (Show system status)"""
        status_thai = {
            self.STATE_IDLE: "รอเริ่ม",
            self.STATE_RUNNING: "กำลังไทเทรต",
            self.STATE_PAUSED: "หยุดชั่วคราว",
            self.STATE_COMPLETE: "เสร็จสิ้น"
        }
        thai_text = status_thai.get(self.state, "ไม่ทราบ")
        print(f"สถานะ: {thai_text} ({self.state})")
        print(f"จำนวนการไทเทรชัน: {self.titration_count}")

    def run(self):
        """
        Main loop ของระบบ (Main loop of the system)

        Pattern นี้เรียกว่า "Event Loop" หรือ "Main Loop":
        1. วนลูปไม่สิ้นสุด
        2. ตรวจสอบ input (ปุ่มกด)
        3. อัพเดต state ตาม input
        4. อัพเดต output (LED, Buzzer) ตาม state
        5. หน่วงเวลาสั้นๆ
        """
        print("\n" + "=" * 60)
        print("คำสั่งควบคุมการไทเทรชัน (Titration Control Instructions):")
        print("=" * 60)
        print("  - กดปุ่ม 1 (GPIO34): เริ่ม/เริ่มต่อ การไทเทรชัน")
        print("    (Press Button 1: Start/Resume titration)")
        print("  - กดปุ่ม 2 (GPIO35): หยุดการไทเทรชัน")
        print("    (Press Button 2: Stop titration)")
        print("  - กดค้างปุ่ม 3 (GPIO39) 3 วินาที: ออกจากโปรแกรม")
        print("    (Hold Button 3 for 3 seconds: Exit)")
        print("=" * 60)

        try:
            while True:
                # === ตรวจสอบปุ่ม Start ===
                if self.btn_start.is_pressed():
                    self.start_titration()

                # === ตรวจสอบปุ่ม Stop ===
                if self.btn_stop.is_pressed():
                    self.stop_titration()

                # === ตรวจสอบปุ่ม Exit (กดค้าง 3 วินาที) ===
                if self.btn_exit.is_active():
                    hold_time = self.btn_exit.get_hold_time()
                    if hold_time > 0:
                        progress = min(hold_time / 3.0, 1.0)
                        bar = "#" * int(progress * 10)
                        print(f"\rกำลังออก: [{bar:10s}] {hold_time:.1f}s", end="")

                    if self.btn_exit.is_held(3):
                        print("\n\n>>> ออกจากโปรแกรม (Exiting)")
                        break

                # === อัพเดตการแสดงผลตามสถานะ ===
                # Update display based on state
                if self.state == self.STATE_RUNNING:
                    # กระพริบ LED เขียวเมื่อกำลังไทเทรต
                    # Blink green LED when titrating
                    self.led_status.toggle()

                # หน่วงเวลาสั้นๆ (Short delay)
                time.sleep_ms(200)

        except KeyboardInterrupt:
            print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

    def cleanup(self):
        """
        ทำความสะอาดระบบ (Clean up system)

        สำคัญ: ต้องเรียก cleanup เสมอเมื่อจบโปรแกรม
        Important: Must always call cleanup when program ends

        ใน Composition เราต้อง cleanup ทุก component
        In Composition we must cleanup all components
        """
        print("\n" + "=" * 60)
        print("กำลังปิดระบบ (Shutting down)")
        print("=" * 60)

        self.led_status.deinit()
        self.led_alert.deinit()
        self.buzzer.deinit()

        self.show_status()
        print("ปิดระบบเสร็จสิ้น (System shutdown complete)")


# ==============================================================================
# ส่วนที่ 3: โปรแกรมหลัก (Main Program)
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ระบบแจ้งเตือนการไทเทรชัน (Titration Alert System)")
    print("TitraLab - สัปดาห์ที่ 1: OOP Basics")
    print("=" * 60)

    # สร้างระบบ (Create system)
    # สังเกตว่าเราสร้างแค่ object เดียว แต่มันรวม LED, Button, Buzzer ไว้ภายใน
    # Notice we create just one object but it contains LED, Button, Buzzer inside
    system = TitrationAlertSystem()

    try:
        # รันระบบ (Run system)
        system.run()

    finally:
        # ทำความสะอาด (Cleanup)
        system.cleanup()

        print("\n" + "=" * 60)
        print("สรุปสิ่งที่เรียนรู้ (What we learned):")
        print("=" * 60)
        print("""
1. Composition - รวม objects หลายตัวใน class เดียว
   (Composition - combining multiple objects in one class)
   - TitrationAlertSystem "มี" LED, Button, Buzzer
   - ง่ายต่อการจัดการระบบที่ซับซ้อน
   - เรียก self.led_status.on() แทนการเรียกตรง

2. State Management - จัดการสถานะของระบบ
   (State Management - managing system state)
   - ใช้ self.state เก็บสถานะปัจจุบัน
   - มี 4 สถานะ: IDLE, RUNNING, PAUSED, COMPLETE
   - พฤติกรรมเปลี่ยนตาม state

3. บริบทห้องปฏิบัติการ (Lab Context)
   - LED เขียวกระพริบ = กำลังหยดสารละลาย
   - LED แดง = หยุด/จุดสมมูล
   - Buzzer = แจ้งเตือนเหตุการณ์สำคัญ

4. Main Loop Pattern
   - while True: วนลูปไม่สิ้นสุด
   - ตรวจ input -> อัพเดต state -> อัพเดต output

5. Cleanup ใน Composition
   - ต้อง cleanup ทุก component ใน system.cleanup()
   - ใช้ try-finally เพื่อให้แน่ใจ

*** การพัฒนาต่อ (Future Development) ***
ในสัปดาห์ถัดไปเราจะเพิ่ม:
- เซ็นเซอร์ pH และอุณหภูมิ
- ปั๊มควบคุมการหยด
- จอแสดงผล TFT
- บันทึกข้อมูลลง SD Card
""")
        print("เสร็จสิ้น (Done)")

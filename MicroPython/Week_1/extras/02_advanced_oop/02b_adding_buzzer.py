# ==============================================================================
# 02b_adding_buzzer.py - เพิ่ม Buzzer เข้าระบบ (Adding Buzzer to the System)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้การเพิ่ม component ใหม่เข้าระบบ
# Week 1: Learn to add new component to the system
#
# ต่อยอดจากไฟล์ 02a_two_objects.py
# Building upon 02a_two_objects.py
#
# สิ่งใหม่ในไฟล์นี้ (What's new in this file):
#   - เพิ่ม Buzzer class ที่ใช้ PWM
#   - เสียง feedback เมื่อกดปุ่ม
#   - เรียนรู้การ cleanup ทรัพยากร PWM
#
# การทำงาน (How it works):
#   - กดปุ่ม 1: เปิด LED เขียว + เสียง success
#   - กดปุ่ม 2: เปิด LED แดง + เสียง warning
#   - กดปุ่ม 3: ปิดทั้งหมด + เสียง beep
#
# ==============================================================================

from machine import Pin, PWM
import time


# ==============================================================================
# ส่วนที่ 1: นิยาม Classes (Class Definitions)
# ==============================================================================

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
        if self.is_on:
            self.off()
        else:
            self.on()
        return self.is_on

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


# ==============================================================================
# [ใหม่] Buzzer Class - ใช้ PWM สร้างเสียง
# [NEW] Buzzer Class - Uses PWM to generate sound
# ==============================================================================

class Buzzer:
    """
    คลาสควบคุม Buzzer ด้วย PWM (Buzzer Control Class using PWM)

    นี่คือ class ใหม่ที่เพิ่มเข้ามาจาก 02a_two_objects.py
    This is a new class added from 02a_two_objects.py

    ข้อแตกต่างจาก LED:
    - LED ใช้ digital output (on/off)
    - Buzzer ใช้ PWM (ความถี่กำหนดเสียง)

    Difference from LED:
    - LED uses digital output (on/off)
    - Buzzer uses PWM (frequency determines sound)
    """

    def __init__(self, pin_number=26):
        """
        สร้าง Buzzer object (Create Buzzer object)

        Args:
            pin_number (int): หมายเลขขา GPIO (GPIO pin number)
                             TitraLab ใช้ GPIO26
        """
        self.pin_number = pin_number
        self._pin = Pin(pin_number, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(2000)
        self._pwm.duty(0)  # เริ่มต้นปิดเสียง (start muted)
        self._initialized = True
        print(f"Buzzer พร้อมที่ GPIO{pin_number}")

    def play_tone(self, freq, duration_ms, duty=512):
        """
        เล่นเสียงที่ความถี่กำหนด (Play tone at specified frequency)

        Args:
            freq (int): ความถี่ Hz (frequency in Hz)
            duration_ms (int): ระยะเวลา มิลลิวินาที (duration in ms)
            duty (int): ความดัง 0-1023 (volume 0-1023)
        """
        self._pwm.freq(freq)
        self._pwm.duty(duty)
        time.sleep_ms(duration_ms)
        self._pwm.duty(0)

    def beep(self, duration_ms=100):
        """เสียง beep สั้น (Short beep sound)"""
        self.play_tone(2000, duration_ms)

    def success_sound(self):
        """
        เสียงสำเร็จ - ไล่จากต่ำไปสูง (Success sound - ascending)

        ใช้เมื่อการดำเนินการสำเร็จ
        Used when operation succeeds
        """
        for freq in [523, 659, 784, 1047]:  # C5, E5, G5, C6
            self.play_tone(freq, 100)

    def warning_sound(self):
        """
        เสียงเตือน - สลับสูง-ต่ำ (Warning sound - alternating)

        ใช้เมื่อต้องการเตือนผู้ใช้
        Used when need to warn user
        """
        for _ in range(2):
            self.play_tone(1500, 100)
            time.sleep_ms(100)

    def mute(self):
        """ปิดเสียง (Mute/silence)"""
        self._pwm.duty(0)

    def deinit(self):
        """
        ปิดการใช้งาน PWM (Deinitialize PWM)

        สำคัญ: ต้องเรียกเมื่อใช้งานเสร็จ!
        Important: Must call when done!

        PWM ใช้ hardware resource - ถ้าไม่ deinit จะมีปัญหา
        """
        if self._initialized:
            self.mute()
            self._pwm.deinit()
            self._initialized = False
            print("ปิด Buzzer")


# ==============================================================================
# ส่วนที่ 2: โปรแกรมหลัก - LED + Button + Buzzer
# (Main Program - LED + Button + Buzzer)
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ตัวอย่าง: LED + Button + Buzzer ทำงานร่วมกัน")
    print("(Example: LED + Button + Buzzer Working Together)")
    print("=" * 60)

    # === สร้าง Objects (Create Objects) ===
    # ตอนนี้เรามี 3 ประเภทของ objects แล้ว!
    # Now we have 3 types of objects!

    print("\n--- สร้าง LED objects ---")
    led_green = LED(4, "Green")
    led_red = LED(2, "Red")

    print("\n--- สร้าง Button objects ---")
    btn1 = Button(34, "Button-1")
    btn2 = Button(35, "Button-2")
    btn3 = Button(39, "Button-3")

    # [ใหม่] สร้าง Buzzer object (NEW - Create Buzzer object)
    print("\n--- สร้าง Buzzer object ---")
    buzzer = Buzzer(26)

    # Startup sound - แสดงว่าระบบพร้อม (show system is ready)
    buzzer.beep()

    # แสดงคำสั่ง (Show instructions)
    print("\n" + "=" * 60)
    print("คำสั่ง (Instructions):")
    print("  - กดปุ่ม 1 (GPIO34): LED เขียว + เสียงสำเร็จ")
    print("  - กดปุ่ม 2 (GPIO35): LED แดง + เสียงเตือน")
    print("  - กดปุ่ม 3 (GPIO39): ปิดทั้งหมด + beep")
    print("  - กด Ctrl+C: ออกจากโปรแกรม")
    print("=" * 60)

    try:
        while True:
            # ปุ่ม 1: LED เขียว + เสียงสำเร็จ
            # Button 1: Green LED + success sound
            if btn1.is_pressed():
                print(">>> ปุ่ม 1: LED เขียว ON + Success Sound")
                led_green.on()
                led_red.off()
                buzzer.success_sound()  # [ใหม่] เสียง feedback

            # ปุ่ม 2: LED แดง + เสียงเตือน
            # Button 2: Red LED + warning sound
            if btn2.is_pressed():
                print(">>> ปุ่ม 2: LED แดง ON + Warning Sound")
                led_green.off()
                led_red.on()
                buzzer.warning_sound()  # [ใหม่] เสียง feedback

            # ปุ่ม 3: ปิดทั้งหมด + beep
            # Button 3: All off + beep
            if btn3.is_pressed():
                print(">>> ปุ่ม 3: ปิดทั้งหมด + Beep")
                led_green.off()
                led_red.off()
                buzzer.beep()  # [ใหม่] เสียง feedback

            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

    finally:
        # === Cleanup ===
        # สำคัญ: ต้อง cleanup ทุก object โดยเฉพาะ PWM!
        # Important: Must cleanup all objects, especially PWM!

        print("\n--- ทำความสะอาด (Cleanup) ---")
        led_green.deinit()
        led_red.deinit()
        buzzer.deinit()  # [สำคัญ] PWM ต้อง deinit เสมอ!

        print("\n" + "=" * 60)
        print("สรุปสิ่งที่เรียนรู้ (What we learned):")
        print("=" * 60)
        print("""
1. เพิ่ม Buzzer class เข้าระบบ (Added Buzzer class)
   - Buzzer ใช้ PWM ไม่ใช่ digital output
   - ความถี่ (freq) กำหนดระดับเสียง
   - duty cycle กำหนดความดัง

2. เสียง Feedback ทำให้ UI ดีขึ้น (Sound feedback improves UI)
   - success_sound() เมื่อสำเร็จ
   - warning_sound() เมื่อต้องการเตือน
   - beep() สำหรับการตอบรับทั่วไป

3. PWM ต้อง cleanup เสมอ (PWM must always be cleaned up)
   - PWM ใช้ hardware timer
   - ถ้าไม่ deinit() จะมีปัญหาเมื่อรันใหม่
   - ใช้ try-finally เพื่อให้แน่ใจ

4. ระบบเริ่มซับซ้อนขึ้น (System getting more complex)
   - มี 3 ประเภท objects: LED, Button, Buzzer
   - ทุกอันทำงานร่วมกันใน main loop

ขั้นตอนถัดไป (Next Step):
   -> ดูไฟล์ 02c_titration_alert_system.py
   -> ใช้ Composition รวม objects ใน class เดียว
   -> เพิ่มบริบทการไทเทรชัน (titration context)
""")
        print("เสร็จสิ้น (Done)")

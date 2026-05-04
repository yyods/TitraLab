# ==============================================================================
# 02a_two_objects.py - สอง Objects ทำงานร่วมกัน (Two Objects Working Together)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้การใช้หลาย objects จากหลาย classes
# Week 1: Learn to use multiple objects from multiple classes
#
# ไฟล์นี้เป็นก้าวแรกจาก 01_combined_example.py
# This file is the first step from 01_combined_example.py
#
# สิ่งใหม่ในไฟล์นี้ (What's new in this file):
#   - ใช้ LED และ Button objects ร่วมกัน
#   - เข้าใจแนวคิด "หลาย objects ทำงานร่วมกัน"
#   - เรียนรู้ main loop แบบง่าย
#
# การทำงาน (How it works):
#   - กดปุ่ม 1: เปิด LED เขียว
#   - กดปุ่ม 2: เปิด LED แดง
#   - กดปุ่ม 3: ปิด LED ทั้งหมด
#
# ==============================================================================

from machine import Pin
import time


# ==============================================================================
# ส่วนที่ 1: นิยาม Classes (Class Definitions)
# ==============================================================================

class LED:
    """คลาสควบคุม LED (LED Control Class)"""

    def __init__(self, pin_number, name="LED"):
        """
        สร้าง LED object (Create LED object)

        Args:
            pin_number (int): หมายเลขขา GPIO (GPIO pin number)
            name (str): ชื่อ LED สำหรับแสดงข้อความ (LED name)
        """
        self.pin_number = pin_number
        self.name = name
        self.is_on = False
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)
        print(f"LED '{name}' พร้อมที่ GPIO{pin_number}")

    def on(self):
        """เปิด LED (Turn LED on)"""
        self._pin.value(1)
        self.is_on = True

    def off(self):
        """ปิด LED (Turn LED off)"""
        self._pin.value(0)
        self.is_on = False

    def toggle(self):
        """สลับสถานะ LED (Toggle LED state)"""
        if self.is_on:
            self.off()
        else:
            self.on()
        return self.is_on

    def deinit(self):
        """ทำความสะอาด (Cleanup)"""
        self.off()
        print(f"ปิด LED '{self.name}'")


class Button:
    """คลาสอ่านปุ่มกด (Button Class)"""

    def __init__(self, pin_number, name="Button", debounce_ms=200):
        """
        สร้าง Button object (Create Button object)

        Args:
            pin_number (int): หมายเลขขา GPIO (GPIO pin number)
            name (str): ชื่อปุ่ม (Button name)
            debounce_ms (int): เวลา debounce มิลลิวินาที (debounce time in ms)
        """
        self.pin_number = pin_number
        self.name = name
        self.debounce_ms = debounce_ms
        self._pin = Pin(pin_number, Pin.IN)
        self._last_press_time = 0
        self._was_pressed = False
        print(f"Button '{name}' พร้อมที่ GPIO{pin_number}")

    def is_active(self):
        """ตรวจสอบว่าปุ่มถูกกดอยู่ (Check if button is pressed)"""
        return self._pin.value() == 1

    def is_pressed(self):
        """
        ตรวจจับการกดปุ่มครั้งใหม่ พร้อม debounce
        (Detect new button press with debounce)

        Returns:
            bool: True ถ้าตรวจจับการกดใหม่ (if new press detected)
        """
        current_time = time.ticks_ms()
        is_active_now = self.is_active()

        # ตรวจสอบการกดใหม่ (Check for new press)
        if is_active_now and not self._was_pressed:
            if time.ticks_diff(current_time, self._last_press_time) > self.debounce_ms:
                self._last_press_time = current_time
                self._was_pressed = True
                return True

        # รีเซ็ตเมื่อปล่อยปุ่ม (Reset when released)
        if not is_active_now:
            self._was_pressed = False

        return False


# ==============================================================================
# ส่วนที่ 2: โปรแกรมหลัก - ใช้ 2 Objects ร่วมกัน
# (Main Program - Using 2 Objects Together)
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ตัวอย่าง: LED + Button ทำงานร่วมกัน")
    print("(Example: LED + Button Working Together)")
    print("=" * 60)

    # === สร้าง Objects (Create Objects) ===
    # แนวคิดสำคัญ: เราสร้าง "หลาย objects" จาก "หลาย classes"
    # Key concept: We create "multiple objects" from "multiple classes"

    print("\n--- สร้าง LED objects ---")
    led_green = LED(4, "Green")    # LED สีเขียว ที่ GPIO4
    led_red = LED(2, "Red")        # LED สีแดง ที่ GPIO2

    print("\n--- สร้าง Button objects ---")
    btn1 = Button(34, "Button-1")  # ปุ่ม 1 ที่ GPIO34
    btn2 = Button(35, "Button-2")  # ปุ่ม 2 ที่ GPIO35
    btn3 = Button(39, "Button-3")  # ปุ่ม 3 ที่ GPIO39

    # แสดงคำสั่ง (Show instructions)
    print("\n" + "=" * 60)
    print("คำสั่ง (Instructions):")
    print("  - กดปุ่ม 1 (GPIO34): เปิด LED เขียว (Turn on green LED)")
    print("  - กดปุ่ม 2 (GPIO35): เปิด LED แดง (Turn on red LED)")
    print("  - กดปุ่ม 3 (GPIO39): ปิด LED ทั้งหมด (Turn off all LEDs)")
    print("  - กด Ctrl+C: ออกจากโปรแกรม (Exit program)")
    print("=" * 60)

    try:
        # === Main Loop ===
        # นี่คือ pattern พื้นฐานของระบบ embedded:
        # วนลูปไม่สิ้นสุด ตรวจสอบ input แล้วตอบสนอง
        # This is the basic pattern of embedded systems:
        # Infinite loop, check input and respond

        while True:
            # ตรวจสอบปุ่ม 1 - เปิด LED เขียว (Check button 1 - turn on green)
            if btn1.is_pressed():
                print(">>> ปุ่ม 1 กด: เปิด LED เขียว (Button 1: Green ON)")
                led_green.on()

            # ตรวจสอบปุ่ม 2 - เปิด LED แดง (Check button 2 - turn on red)
            if btn2.is_pressed():
                print(">>> ปุ่ม 2 กด: เปิด LED แดง (Button 2: Red ON)")
                led_red.on()

            # ตรวจสอบปุ่ม 3 - ปิด LED ทั้งหมด (Check button 3 - turn off all)
            if btn3.is_pressed():
                print(">>> ปุ่ม 3 กด: ปิดทั้งหมด (Button 3: All OFF)")
                led_green.off()
                led_red.off()

            # หน่วงเวลาสั้นๆ เพื่อลด CPU usage (Short delay to reduce CPU)
            time.sleep_ms(50)

    except KeyboardInterrupt:
        print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

    finally:
        # === Cleanup ===
        # สำคัญ: ปิด hardware ทุกครั้งเมื่อจบโปรแกรม
        # Important: Always cleanup hardware when program ends

        print("\n--- ทำความสะอาด (Cleanup) ---")
        led_green.deinit()
        led_red.deinit()

        print("\n" + "=" * 60)
        print("สรุปสิ่งที่เรียนรู้ (What we learned):")
        print("=" * 60)
        print("""
1. ใช้หลาย objects ร่วมกัน (Multiple objects together)
   - led_green และ led_red เป็น LED objects
   - btn1, btn2, btn3 เป็น Button objects
   - ทั้งหมดทำงานร่วมกันใน main loop

2. Main Loop Pattern
   - while True: วนลูปไม่สิ้นสุด
   - ตรวจสอบ input (ปุ่ม) ทุกรอบ
   - ตอบสนองด้วย output (LED)

3. แต่ละ object เป็นอิสระ (Each object is independent)
   - led_green.on() ไม่กระทบ led_red
   - btn1.is_pressed() ไม่กระทบ btn2

4. Cleanup สำคัญ (Cleanup is important)
   - ใช้ try-finally เพื่อให้แน่ใจว่า cleanup

ขั้นตอนถัดไป (Next Step):
   -> ดูไฟล์ 02b_adding_buzzer.py เพิ่ม Buzzer เข้ามา
""")
        print("เสร็จสิ้น (Done)")

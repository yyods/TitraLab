# ==============================================================================
# 06_comparing_styles.py - เปรียบเทียบโค้ดแบบ Procedural vs OOP
# ==============================================================================
# สัปดาห์ที่ 1: เข้าใจความแตกต่างระหว่าง Procedural และ OOP
# Week 1: Understanding the difference between Procedural and OOP
#
# ไฟล์นี้แสดงโค้ดเดียวกันในสองรูปแบบ เพื่อให้เห็นข้อดีของ OOP
# This file shows the same code in two styles to demonstrate OOP benefits
# ==============================================================================

from machine import Pin
import time


# ==============================================================================
# ส่วนที่ 1: แบบ PROCEDURAL (ไม่ใช้ OOP)
# Part 1: PROCEDURAL style (without OOP)
# ==============================================================================
#
# นี่คือวิธีที่เราเรียนในไฟล์ 01_basic.py ถึง 04_twoLed_infiniteLoop.py
# This is the style we learned in files 01_basic.py to 04_twoLed_infiniteLoop.py
#
# ข้อจำกัด (Limitations):
#   - ต้องจำหมายเลข GPIO เอง
#   - ถ้ามี LED หลายดวง โค้ดจะยาวและซ้ำซ้อน
#   - ยากต่อการนำไปใช้ซ้ำ
#
# ==============================================================================

def procedural_example():
    """
    ตัวอย่างการควบคุม LED แบบ Procedural
    Example of LED control using Procedural style
    """
    print("=" * 50)
    print("แบบ PROCEDURAL (Procedural Style)")
    print("=" * 50)

    # ต้องสร้าง Pin เอง (Must create Pin manually)
    led1 = Pin(2, Pin.OUT)
    led2 = Pin(4, Pin.OUT)

    # ต้องจำว่า led1 คือสีแดง, led2 คือสีเขียว
    # Must remember led1 is red, led2 is green

    # เปิด-ปิด ต้องใช้ value(1) และ value(0)
    # On-off requires value(1) and value(0)
    led1.value(1)  # เปิด led1 - ต้องจำว่า 1 = เปิด
    time.sleep(0.5)
    led1.value(0)  # ปิด led1 - ต้องจำว่า 0 = ปิด

    led2.value(1)
    time.sleep(0.5)
    led2.value(0)

    # ถ้าต้องการ blink ต้องเขียน loop เอง
    # If want to blink, must write loop manually
    for _ in range(3):
        led1.value(1)
        time.sleep(0.3)
        led1.value(0)
        time.sleep(0.3)

    # ปิด LED ทั้งหมด (Turn off all LEDs)
    led1.value(0)
    led2.value(0)

    print("จบ Procedural example")


# ==============================================================================
# ส่วนที่ 2: แบบ OOP
# Part 2: OOP style
# ==============================================================================
#
# ข้อดี (Benefits):
#   - โค้ดอ่านง่าย: led_red.on() ชัดเจนกว่า led1.value(1)
#   - ใช้ซ้ำได้: สร้าง LED ใหม่แค่เรียก LED(pin, name)
#   - จัดการสถานะอัตโนมัติ: led.is_on บอกสถานะได้เลย
#   - มี method พร้อมใช้: blink(), toggle()
#
# ==============================================================================

class LED:
    """
    คลาส LED สำหรับควบคุม LED (LED class for LED control)
    """

    def __init__(self, pin_number, name="LED"):
        """สร้าง LED (Create LED)"""
        self.pin_number = pin_number
        self.name = name
        self.is_on = False
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)

    def on(self):
        """เปิด LED (Turn on)"""
        self._pin.value(1)
        self.is_on = True

    def off(self):
        """ปิด LED (Turn off)"""
        self._pin.value(0)
        self.is_on = False

    def blink(self, times=3, delay=0.3):
        """กระพริบ LED (Blink LED)"""
        for _ in range(times):
            self.on()
            time.sleep(delay)
            self.off()
            time.sleep(delay)


def oop_example():
    """
    ตัวอย่างการควบคุม LED แบบ OOP
    Example of LED control using OOP style
    """
    print("=" * 50)
    print("แบบ OOP (OOP Style)")
    print("=" * 50)

    # สร้าง LED พร้อมชื่อที่จำง่าย
    # Create LEDs with memorable names
    led_red = LED(2, "Red")
    led_green = LED(4, "Green")

    # เปิด-ปิด ด้วย method ที่ชัดเจน
    # On-off with clear methods
    led_red.on()    # ชัดเจนว่าเปิด LED สีแดง (clearly turning on red LED)
    time.sleep(0.5)
    led_red.off()   # ชัดเจนว่าปิด LED สีแดง (clearly turning off red LED)

    led_green.on()
    time.sleep(0.5)
    led_green.off()

    # กระพริบด้วย method blink() - ไม่ต้องเขียน loop เอง
    # Blink with blink() method - no need to write loop
    led_red.blink(3, 0.3)

    # ปิด LED ทั้งหมด (Turn off all LEDs)
    led_red.off()
    led_green.off()

    print("จบ OOP example")


# ==============================================================================
# ส่วนที่ 3: เปรียบเทียบโดยตรง (Direct Comparison)
# Part 3: Direct Comparison
# ==============================================================================

def show_comparison():
    """
    แสดงการเปรียบเทียบโค้ดโดยตรง
    Show direct code comparison
    """
    print("\n" + "=" * 60)
    print("เปรียบเทียบโค้ด (Code Comparison)")
    print("=" * 60)

    print("""
+--------------------------------------------------+
| การกระทำ (Action)     | Procedural    | OOP      |
+--------------------------------------------------+
| สร้าง LED            | Pin(2, OUT)   | LED(2)   |
+--------------------------------------------------+
| เปิด LED             | pin.value(1)  | led.on() |
+--------------------------------------------------+
| ปิด LED              | pin.value(0)  | led.off()|
+--------------------------------------------------+
| กระพริบ 3 ครั้ง       | เขียน for loop | led.blink(3)|
+--------------------------------------------------+
| ตรวจสถานะ           | ไม่มี (ต้องจำเอง)| led.is_on |
+--------------------------------------------------+
| ระบุชื่อ             | ใช้ comment    | led.name |
+--------------------------------------------------+
""")

    print("สรุป (Summary):")
    print("-" * 50)
    print("""
Procedural:
  - เหมาะกับโปรแกรมเล็กๆ ง่ายๆ
  - เรียนรู้ได้เร็ว
  - โค้ดสั้น (แต่อาจไม่ชัดเจน)

OOP:
  - เหมาะกับโปรแกรมใหญ่ที่ซับซ้อน
  - โค้ดอ่านง่าย เข้าใจง่าย
  - ใช้ซ้ำได้ นำไปประยุกต์ได้ง่าย
  - เป็นพื้นฐานสำหรับ Week 2 และ Week 3

ในสัปดาห์ที่ 1 เราจะเริ่มฝึกใช้ OOP กับ LED, Button, และ Buzzer
เพื่อเตรียมพร้อมสำหรับระบบที่ซับซ้อนขึ้นในสัปดาห์ถัดไป
""")


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("เปรียบเทียบ Procedural vs OOP")
    print("(Comparing Procedural vs OOP)")
    print("=" * 60)

    try:
        # รันทั้งสองตัวอย่าง (Run both examples)
        print("\n>>> รัน Procedural Example...")
        procedural_example()

        time.sleep(1)

        print("\n>>> รัน OOP Example...")
        oop_example()

        # แสดงตารางเปรียบเทียบ (Show comparison table)
        show_comparison()

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        # ปิด LED ทั้งหมด (Turn off all LEDs)
        Pin(2, Pin.OUT).value(0)
        Pin(4, Pin.OUT).value(0)
        print("\nปิด LED ทั้งหมดแล้ว (All LEDs turned off)")

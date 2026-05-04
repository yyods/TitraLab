# ==============================================================================
# 01_self_explained.py - ทำความเข้าใจ self ใน Python OOP
#                        (Understanding 'self' in Python OOP)
# ==============================================================================
# สัปดาห์ที่ 1: บทเรียนสำคัญเรื่อง self
# Week 1: Important lesson about self
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจว่า self คืออะไร (What is self?)
#   2. ทำไม self ต้องเป็นพารามิเตอร์แรกเสมอ (Why self must be first parameter)
#   3. Python แปลง led.on() เป็น LED.on(led) อย่างไร (How Python translates method calls)
#   4. ข้อผิดพลาดที่พบบ่อย (Common mistakes)
# ==============================================================================


# ==============================================================================
# ส่วนที่ 1: self คืออะไร? (What is self?)
# ==============================================================================
#
# self คือ "ตัวอ้างอิงถึง object ปัจจุบัน" (reference to the current object)
#
# ลองนึกภาพ:
#   - คุณมี LED 2 ดวง: led_red และ led_green
#   - ทั้งสองสร้างจาก class LED เดียวกัน
#   - เมื่อเรียก led_red.on() Python ต้องรู้ว่าจะเปิด LED ตัวไหน
#   - self คือตัวบอกว่า "ทำกับ object นี้"
#
# Imagine:
#   - You have 2 LEDs: led_red and led_green
#   - Both are created from the same LED class
#   - When calling led_red.on() Python needs to know which LED to turn on
#   - self tells Python "do it on THIS object"
#
# ==============================================================================


from machine import Pin


# ==============================================================================
# ส่วนที่ 2: ตัวอย่าง Class LED พร้อมคำอธิบาย self
# ==============================================================================

class LED:
    """
    คลาส LED สำหรับสาธิตการใช้ self
    (LED class to demonstrate self usage)
    """

    def __init__(self, pin_number, name="LED"):
        """
        Constructor - ทำงานเมื่อสร้าง object ใหม่
        (Constructor - runs when creating a new object)

        สังเกต: self เป็นพารามิเตอร์แรกเสมอ!
        (Notice: self is ALWAYS the first parameter!)

        Args:
            pin_number (int): หมายเลขขา GPIO (GPIO pin number)
            name (str): ชื่อ LED สำหรับแสดงผล (LED name for display)
        """
        # self.xxx = เก็บค่าไว้ใน object นี้
        # self.xxx = store value in THIS object
        self.pin_number = pin_number
        self.name = name
        self.is_on = False

        # สร้าง Pin object และเก็บไว้ใน self._pin
        # Create Pin object and store in self._pin
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.off()

        print(f"สร้าง {name} ที่ GPIO{pin_number} สำเร็จ")
        print(f"(Created {name} on GPIO{pin_number})")

    def on(self):
        """
        เปิด LED (Turn LED on)

        สังเกต: เมื่อเรียก led_red.on()
        Python แปลงเป็น LED.on(led_red) โดยอัตโนมัติ!

        (Notice: When you call led_red.on()
        Python automatically translates it to LED.on(led_red)!)
        """
        self._pin.on()           # ใช้ self เพื่อเข้าถึง _pin ของ object นี้
        self.is_on = True        # ใช้ self เพื่อเข้าถึง is_on ของ object นี้
        print(f"{self.name} เปิดแล้ว ({self.name} is ON)")

    def off(self):
        """
        ปิด LED (Turn LED off)
        """
        self._pin.off()
        self.is_on = False
        print(f"{self.name} ปิดแล้ว ({self.name} is OFF)")

    def toggle(self):
        """
        สลับสถานะ (Toggle state)
        """
        if self.is_on:
            self.off()    # เรียก method อื่นใน class เดียวกัน ผ่าน self
        else:
            self.on()


# ==============================================================================
# ส่วนที่ 3: Python แปลง method call อย่างไร?
#            (How Python translates method calls)
# ==============================================================================
#
# เมื่อคุณเขียน:
#     led_red.on()
#
# Python แปลงเป็น:
#     LED.on(led_red)
#
# นั่นคือเหตุผลว่าทำไม self ต้องเป็นพารามิเตอร์แรก!
# Python จะส่ง object (led_red) เข้ามาเป็น argument แรกโดยอัตโนมัติ
#
# When you write:
#     led_red.on()
#
# Python translates it to:
#     LED.on(led_red)
#
# That's why self must be the first parameter!
# Python automatically passes the object (led_red) as the first argument
#
# ==============================================================================


# ==============================================================================
# ส่วนที่ 4: ข้อผิดพลาดที่พบบ่อย (Common Mistakes)
# ==============================================================================

# --- ข้อผิดพลาดที่ 1: ลืม self ใน method definition ---
# --- Mistake 1: Forgetting self in method definition ---

class BadLED_NoSelf:
    """
    ตัวอย่างที่ผิด - ลืม self ใน method
    (Wrong example - forgot self in method)
    """

    def __init__(self, pin_number):
        self.pin_number = pin_number

    # ผิด! ลืมใส่ self เป็นพารามิเตอร์แรก
    # Wrong! Forgot to put self as first parameter
    # def on():                    # <-- ผิด! (Wrong!)
    #     print("LED on")          # จะเกิด TypeError เมื่อเรียกใช้
    #                              # (Will raise TypeError when called)

    # ถูกต้อง:
    # Correct:
    def on(self):                   # <-- ถูก! มี self (Correct! has self)
        print(f"LED at GPIO{self.pin_number} is ON")


# --- ข้อผิดพลาดที่ 2: ลืม self. เมื่อเข้าถึงตัวแปร instance ---
# --- Mistake 2: Forgetting self. when accessing instance variables ---

class BadLED_NoSelfDot:
    """
    ตัวอย่างที่ผิด - ลืม self. เมื่อเข้าถึงตัวแปร
    (Wrong example - forgot self. when accessing variables)
    """

    def __init__(self, pin_number):
        self.pin_number = pin_number
        self.is_on = False

    def on(self):
        # ผิด! ต้องใช้ self.is_on ไม่ใช่แค่ is_on
        # Wrong! Must use self.is_on not just is_on
        # is_on = True             # <-- ผิด! สร้างตัวแปร local แทน
        #                          # (Wrong! Creates local variable instead)

        # ถูกต้อง:
        # Correct:
        self.is_on = True          # <-- ถูก! เข้าถึงตัวแปร instance
                                   # (Correct! Accesses instance variable)
        print(f"GPIO{self.pin_number} is ON, is_on = {self.is_on}")


# ==============================================================================
# ส่วนที่ 5: สรุปกฎสำคัญของ self (Summary of self Rules)
# ==============================================================================
#
# กฎ 1: self ต้องเป็นพารามิเตอร์แรกของทุก method ใน class
#       (self must be the first parameter of every method in a class)
#
#       def my_method(self, arg1, arg2):   # ถูก (Correct)
#       def my_method(arg1, arg2):         # ผิด (Wrong)
#
# กฎ 2: ใช้ self.xxx เพื่อเข้าถึงหรือสร้างตัวแปร instance
#       (Use self.xxx to access or create instance variables)
#
#       self.pin_number = 2    # เก็บค่าใน object
#       print(self.pin_number) # อ่านค่าจาก object
#
# กฎ 3: ใช้ self.method_name() เพื่อเรียก method อื่นใน class เดียวกัน
#       (Use self.method_name() to call other methods in the same class)
#
#       def toggle(self):
#           if self.is_on:
#               self.off()     # เรียก off() ของ object นี้
#           else:
#               self.on()      # เรียก on() ของ object นี้
#
# ==============================================================================


# ==============================================================================
# ส่วนที่ 6: ทดสอบการทำงาน (Test Run)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ทำความเข้าใจ self (Understanding self)")
    print("=" * 60)

    # --- สาธิต: สร้าง 2 objects จาก class เดียวกัน ---
    # --- Demo: Create 2 objects from the same class ---
    print("\n--- สร้าง LED 2 ดวง (Creating 2 LEDs) ---")
    led_red = LED(2, "LED_RED")      # สร้าง LED สีแดงที่ GPIO2
    led_green = LED(4, "LED_GREEN")  # สร้าง LED สีเขียวที่ GPIO4

    # --- สาธิต: แต่ละ object มีค่าตัวแปรเป็นของตัวเอง ---
    # --- Demo: Each object has its own variable values ---
    print("\n--- แสดงค่าตัวแปรของแต่ละ object ---")
    print("(Showing variable values of each object)")
    print(f"led_red.pin_number = {led_red.pin_number}")
    print(f"led_green.pin_number = {led_green.pin_number}")
    print("สังเกต: pin_number ต่างกัน เพราะเป็นคนละ object!")
    print("(Notice: pin_number differs because they are different objects!)")

    # --- สาธิต: เรียก method แล้ว self ชี้ไปที่ object ถูกต้อง ---
    # --- Demo: When calling method, self points to correct object ---
    print("\n--- ทดสอบเรียก method ---")
    print("(Testing method calls)")

    print("\nเรียก led_red.on():")
    print("Python แปลงเป็น: LED.on(led_red)")
    print("(Python translates to: LED.on(led_red))")
    led_red.on()

    print("\nเรียก led_green.on():")
    print("Python แปลงเป็น: LED.on(led_green)")
    print("(Python translates to: LED.on(led_green))")
    led_green.on()

    # --- สาธิตข้อผิดพลาดที่แก้ไขแล้ว ---
    # --- Demo corrected mistakes ---
    print("\n--- ทดสอบ class ที่แก้ไขข้อผิดพลาดแล้ว ---")
    print("(Testing classes with corrected mistakes)")

    corrected_led = BadLED_NoSelf(2)
    corrected_led.on()

    corrected_led2 = BadLED_NoSelfDot(4)
    corrected_led2.on()

    # --- ปิด LED ---
    # --- Turn off LEDs ---
    print("\n--- ปิด LED ทั้งหมด ---")
    print("(Turning off all LEDs)")
    led_red.off()
    led_green.off()

    # --- สรุป ---
    # --- Summary ---
    print("\n" + "=" * 60)
    print("สรุปสิ่งที่เรียนรู้ (What we learned):")
    print("=" * 60)
    print("""
1. self คืออะไร? (What is self?)
   - เป็นตัวอ้างอิงถึง object ปัจจุบัน
   - (Reference to the current object)

2. ทำไม self ต้องเป็นพารามิเตอร์แรก? (Why self must be first?)
   - เพราะ Python แปลง obj.method() เป็น Class.method(obj)
   - (Because Python translates obj.method() to Class.method(obj))

3. การใช้ self.xxx (Using self.xxx)
   - self.xxx = value   # เก็บค่าใน object (store in object)
   - print(self.xxx)    # อ่านค่าจาก object (read from object)
   - self.method()      # เรียก method อื่น (call other method)

4. ข้อผิดพลาดที่พบบ่อย (Common mistakes)
   - ลืม self ใน def method(self, ...):
   - ลืม self. เมื่อเข้าถึงตัวแปร: self.xxx ไม่ใช่แค่ xxx
""")
    print("เสร็จสิ้น (Done)")

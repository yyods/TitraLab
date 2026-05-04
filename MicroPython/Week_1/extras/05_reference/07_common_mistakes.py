# ==============================================================================
# 07_common_mistakes.py - ข้อผิดพลาดที่พบบ่อยใน OOP
# (Common OOP Mistakes)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้จากข้อผิดพลาดที่มักเกิดขึ้นกับผู้เริ่มต้น
# Week 1: Learn from common mistakes made by beginners
#
# ไฟล์นี้รวบรวมข้อผิดพลาด 5 ข้อที่พบบ่อยในการเขียน OOP ด้วย MicroPython
# This file collects 5 common mistakes when writing OOP with MicroPython
#
# แต่ละข้อมีตัวอย่าง:
#   - [ผิด] WRONG - โค้ดที่ผิดพลาด
#   - [ถูก] CORRECT - โค้ดที่ถูกต้อง
#   - คำอธิบายว่าทำไมถึงผิดและวิธีแก้
#
# ==============================================================================

from machine import Pin
import time

print("=" * 60)
print("ข้อผิดพลาดที่พบบ่อยใน OOP (Common OOP Mistakes)")
print("=" * 60)


# ==============================================================================
# ข้อผิดพลาดที่ 1: ลืม self ใน method
# Mistake #1: Forgetting 'self' in methods
# ==============================================================================

print("\n" + "=" * 60)
print("ข้อผิดพลาดที่ 1: ลืม self ใน method")
print("(Mistake #1: Forgetting 'self' in methods)")
print("=" * 60)

# ----- [ผิด] WRONG -----
# ลืมใส่ self เป็น parameter แรกของ method
# Forgot to put self as first parameter of method

print("\n[ผิด] WRONG:")
print('''
class LED_Wrong1:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.OUT)

    def on():  # <-- ผิด! ลืม self (Wrong! Missing self)
        self.pin.value(1)  # จะ error เพราะไม่รู้จัก self
''')

print("Error ที่จะเกิด: TypeError: on() takes 0 positional arguments but 1 was given")
print("เหตุผล: Python ส่ง object เป็น argument แรกเสมอ แต่ method ไม่รับ")
print("(Reason: Python always passes object as first argument, but method doesn't accept it)")

# ----- [ถูก] CORRECT -----
print("\n[ถูก] CORRECT:")
print('''
class LED_Correct1:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.OUT)

    def on(self):  # <-- ถูก! มี self (Correct! Has self)
        self.pin.value(1)
''')

print("หลักการ: ทุก method ต้องมี self เป็น parameter แรก")
print("(Rule: Every method must have self as first parameter)")


# ==============================================================================
# ข้อผิดพลาดที่ 2: ลืมวงเล็บเมื่อสร้าง object
# Mistake #2: Missing parentheses when creating object
# ==============================================================================

print("\n" + "=" * 60)
print("ข้อผิดพลาดที่ 2: ลืมวงเล็บเมื่อสร้าง object")
print("(Mistake #2: Missing parentheses when creating object)")
print("=" * 60)

# ----- [ผิด] WRONG -----
print("\n[ผิด] WRONG:")
print('''
class LED:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.OUT)

    def on(self):
        self.pin.value(1)

# การใช้งาน (Usage):
led = LED  # <-- ผิด! ลืมวงเล็บ (Wrong! Missing parentheses)
led.on()   # จะ error
''')

print("Error ที่จะเกิด: TypeError: on() missing 1 required positional argument: 'self'")
print("เหตุผล: led ชี้ไปที่ class ไม่ใช่ object จึงไม่มี self")
print("(Reason: led points to class not object, so there's no self)")

# ----- [ถูก] CORRECT -----
print("\n[ถูก] CORRECT:")
print('''
led = LED(2)  # <-- ถูก! มีวงเล็บและ argument (Correct! Has parentheses and argument)
led.on()      # ทำงานได้ (Works!)
''')

print("หลักการ: สร้าง object ต้องมี () เสมอ แม้ไม่มี argument ก็ต้องใส่ ()")
print("(Rule: Creating object must have () always, even without arguments)")


# ==============================================================================
# ข้อผิดพลาดที่ 3: สับสน class กับ instance (object)
# Mistake #3: Confusing class with instance (object)
# ==============================================================================

print("\n" + "=" * 60)
print("ข้อผิดพลาดที่ 3: สับสน class กับ instance (object)")
print("(Mistake #3: Confusing class with instance)")
print("=" * 60)

# ----- [ผิด] WRONG -----
print("\n[ผิด] WRONG:")
print('''
class LED:
    def __init__(self, pin_number):
        self.pin_number = pin_number
        self.pin = Pin(pin_number, Pin.OUT)

# พยายามเรียก method โดยตรงจาก class
# Trying to call method directly from class
LED.on()  # <-- ผิด! เรียกจาก class ไม่ใช่ object
''')

print("Error ที่จะเกิด: TypeError หรือ AttributeError")
print("เหตุผล: LED เป็น 'พิมพ์เขียว' ต้องสร้าง object ก่อนใช้งาน")
print("(Reason: LED is a 'blueprint', must create object before use)")

# ----- [ถูก] CORRECT -----
print("\n[ถูก] CORRECT:")
print('''
class LED:
    def __init__(self, pin_number):
        self.pin_number = pin_number
        self.pin = Pin(pin_number, Pin.OUT)

    def on(self):
        self.pin.value(1)

# สร้าง object ก่อน แล้วค่อยเรียก method
# Create object first, then call method
led_red = LED(2)    # สร้าง object (Create object)
led_red.on()        # เรียก method จาก object (Call method from object)
''')

print("หลักการ: Class = พิมพ์เขียว, Object = ของจริงที่ใช้งานได้")
print("(Rule: Class = blueprint, Object = actual thing you can use)")


# ==============================================================================
# ข้อผิดพลาดที่ 4: ลืม self. เมื่ออ้างถึง instance variable
# Mistake #4: Forgetting self. when referring to instance variable
# ==============================================================================

print("\n" + "=" * 60)
print("ข้อผิดพลาดที่ 4: ลืม self. เมื่ออ้างถึง instance variable")
print("(Mistake #4: Forgetting self. when referring to instance variable)")
print("=" * 60)

# ----- [ผิด] WRONG -----
print("\n[ผิด] WRONG:")
print('''
class LED:
    def __init__(self, pin_number):
        self.pin_number = pin_number
        self.pin = Pin(pin_number, Pin.OUT)
        self.is_on = False

    def toggle(self):
        if is_on:  # <-- ผิด! ลืม self. (Wrong! Missing self.)
            pin.value(0)  # <-- ผิดอีก! (Wrong again!)
        else:
            pin.value(1)
''')

print("Error ที่จะเกิด: NameError: name 'is_on' is not defined")
print("เหตุผล: Python มองหา local variable ชื่อ is_on แต่ไม่เจอ")
print("(Reason: Python looks for local variable named is_on but doesn't find it)")

# ----- [ถูก] CORRECT -----
print("\n[ถูก] CORRECT:")
print('''
class LED:
    def __init__(self, pin_number):
        self.pin_number = pin_number
        self.pin = Pin(pin_number, Pin.OUT)
        self.is_on = False

    def toggle(self):
        if self.is_on:  # <-- ถูก! มี self. (Correct! Has self.)
            self.pin.value(0)  # <-- ถูก! (Correct!)
            self.is_on = False
        else:
            self.pin.value(1)
            self.is_on = True
''')

print("หลักการ: ทุกครั้งที่อ้างถึงตัวแปรของ object ต้องใส่ self.")
print("(Rule: Every time you refer to object's variable, use self.)")


# ==============================================================================
# ข้อผิดพลาดที่ 5: ไม่เรียก __init__ ของ parent class (สำหรับ Inheritance)
# Mistake #5: Not calling parent's __init__ (for Inheritance)
# ==============================================================================

print("\n" + "=" * 60)
print("ข้อผิดพลาดที่ 5: ไม่เรียก __init__ ของ parent class")
print("(Mistake #5: Not calling parent's __init__)")
print("=" * 60)

# ----- [ผิด] WRONG -----
print("\n[ผิด] WRONG:")
print('''
class OutputDevice:
    def __init__(self, pin_number, name):
        self.pin_number = pin_number
        self.name = name
        self.pin = Pin(pin_number, Pin.OUT)

class LED(OutputDevice):  # LED สืบทอดจาก OutputDevice
    def __init__(self, pin_number, name, color):
        # ลืมเรียก parent's __init__!
        # Forgot to call parent's __init__!
        self.color = color  # <-- ผิด! pin_number และ name ไม่ถูกตั้งค่า

led = LED(2, "Status", "red")
print(led.name)  # จะ error เพราะ name ไม่ถูกสร้าง
''')

print("Error ที่จะเกิด: AttributeError: 'LED' object has no attribute 'name'")
print("เหตุผล: __init__ ของ parent ไม่ถูกเรียก จึงไม่มี name, pin_number")
print("(Reason: Parent's __init__ not called, so no name, pin_number)")

# ----- [ถูก] CORRECT -----
print("\n[ถูก] CORRECT:")
print('''
class OutputDevice:
    def __init__(self, pin_number, name):
        self.pin_number = pin_number
        self.name = name
        self.pin = Pin(pin_number, Pin.OUT)

class LED(OutputDevice):
    def __init__(self, pin_number, name, color):
        # เรียก parent's __init__ ก่อน!
        # Call parent's __init__ first!
        super().__init__(pin_number, name)  # <-- ถูก! (Correct!)
        self.color = color  # แล้วค่อยเพิ่มของ LED

led = LED(2, "Status", "red")
print(led.name)   # "Status" - ทำงานได้!
print(led.color)  # "red" - ทำงานได้!
''')

print("หลักการ: เมื่อ override __init__ ต้องเรียก super().__init__() ก่อน")
print("(Rule: When overriding __init__, call super().__init__() first)")


# ==============================================================================
# สรุป: ตารางข้อผิดพลาด (Summary: Mistake Table)
# ==============================================================================

print("\n" + "=" * 60)
print("สรุป: ตารางข้อผิดพลาดที่พบบ่อย")
print("(Summary: Common Mistakes Table)")
print("=" * 60)

print("""
+-----+--------------------------------+--------------------------------+
| No. | ข้อผิดพลาด (Mistake)           | วิธีแก้ (Solution)              |
+-----+--------------------------------+--------------------------------+
|  1  | ลืม self ใน method            | ใส่ self เป็น parameter แรก    |
|     | (Missing self in method)       | (Add self as first parameter)  |
+-----+--------------------------------+--------------------------------+
|  2  | ลืม () เมื่อสร้าง object       | ใส่ () เสมอ: LED(2)            |
|     | (Missing () when creating)     | (Always add (): LED(2))        |
+-----+--------------------------------+--------------------------------+
|  3  | เรียก method จาก class        | สร้าง object ก่อน แล้วเรียก     |
|     | (Calling method from class)    | (Create object first)          |
+-----+--------------------------------+--------------------------------+
|  4  | ลืม self. กับ instance var    | ใส่ self. ทุกครั้ง: self.is_on |
|     | (Missing self. for inst var)   | (Always use self.is_on)        |
+-----+--------------------------------+--------------------------------+
|  5  | ลืมเรียก parent's __init__    | ใช้ super().__init__()         |
|     | (Missing parent's __init__)    | (Use super().__init__())       |
+-----+--------------------------------+--------------------------------+
""")


# ==============================================================================
# แบบฝึกหัด: หาข้อผิดพลาด (Exercise: Find the Mistakes)
# ==============================================================================

print("\n" + "=" * 60)
print("แบบฝึกหัด: หาข้อผิดพลาดในโค้ดนี้ (มี 3 ข้อ)")
print("(Exercise: Find mistakes in this code - there are 3)")
print("=" * 60)

print('''
class Button:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.IN)
        self.last_press = 0

    def is_pressed():  # <-- ข้อผิดพลาดที่ 1?
        current = time.ticks_ms()
        if pin.value() == 1:  # <-- ข้อผิดพลาดที่ 2?
            if time.ticks_diff(current, last_press) > 200:  # <-- ข้อผิดพลาดที่ 3?
                self.last_press = current
                return True
        return False

# การใช้งาน
btn = Button
btn.is_pressed()
''')

print("\nคำตอบ (Answers):")
print("1. is_pressed() ลืม self -> is_pressed(self)")
print("2. pin.value() ลืม self. -> self.pin.value()")
print("3. last_press ลืม self. -> self.last_press")
print("4. [โบนัส] btn = Button ลืม () และ argument -> btn = Button(34)")


# ==============================================================================
# โค้ดที่ถูกต้อง (Correct Code)
# ==============================================================================

print("\n" + "=" * 60)
print("โค้ดที่ถูกต้อง (Correct Code)")
print("=" * 60)

print('''
class Button:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.IN)
        self.last_press = 0

    def is_pressed(self):  # มี self
        current = time.ticks_ms()
        if self.pin.value() == 1:  # มี self.
            if time.ticks_diff(current, self.last_press) > 200:  # มี self.
                self.last_press = current
                return True
        return False

# การใช้งาน
btn = Button(34)  # มี () และ argument
if btn.is_pressed():
    print("กดปุ่มแล้ว!")
''')

print("\n" + "=" * 60)
print("เสร็จสิ้น (Done)")
print("=" * 60)

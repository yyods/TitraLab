# ==============================================================================
# 03_properties_demo.py - สาธิต @property Decorator และ Encapsulation
# (Properties and Encapsulation Demo)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ @property สำหรับ Encapsulation
# This program demonstrates @property for Encapsulation
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ @property decorator
#   2. เรียนรู้ @property.setter
#   3. เข้าใจ Encapsulation และ private attributes
#   4. ดูประโยชน์ของ validation ใน setter
#   5. เปรียบเทียบ property vs public attributes
#
# ===== @property คืออะไร? =====
#
# @property ทำให้ method ถูกเรียกเหมือน attribute:
#   - ไม่ต้องใช้ parentheses: sensor.name แทน sensor.name()
#   - สามารถเพิ่ม validation ได้
#   - Encapsulate implementation details
#
# Hardware Configuration:
#   - GPIO 25: pH Sensor (ADC)
#   - GPIO 21: Pump (PWM)
#
# ==============================================================================

from time import sleep_ms
import sys

# เพิ่ม lib path
sys.path.append('lib')

from lib.ph_sensor import PHSensor
from lib.pump import Pump


# ==============================================================================
# ส่วนที่ 1: อธิบาย @property
# Part 1: Explain @property
# ==============================================================================
def explain_property():
    """
    อธิบายหลักการ @property (Explain @property concept)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 1: @property คืออะไร?")
    print("Part 1: What is @property?")
    print("=" * 60)

    print("""
    ===== ปัญหาของ Public Attributes =====

    class BadSensor:
        def __init__(self):
            self.slope = -5.79    # Public attribute
            self.intercept = 16.7  # Public attribute

    ปัญหา:
    1. ไม่สามารถ validate ค่าได้:
       sensor.slope = "hello"  # ผิดแต่ไม่มี error!

    2. ไม่สามารถเพิ่ม logic ได้:
       sensor.slope = 10  # slope ควรเป็นค่าลบ!

    3. เปลี่ยน implementation ยาก:
       ถ้าอยากเปลี่ยนเป็นคำนวณ slope ต้องแก้ทุกที่

    ===== @property แก้ปัญหาอย่างไร =====

    class GoodSensor:
        def __init__(self):
            self._slope = -5.79  # Private attribute (_)

        @property
        def slope(self):
            return self._slope

        @slope.setter
        def slope(self, value):
            if value > 0:
                print("Warning: slope should be negative")
            self._slope = value

    ข้อดี:
    1. เข้าถึงเหมือน attribute: sensor.slope
    2. เพิ่ม validation ได้: ตรวจสอบค่าก่อนกำหนด
    3. เปลี่ยน implementation ได้โดยไม่กระทบ code ภายนอก

    ===== รูปแบบ @property =====

    @property           -> getter (อ่านค่า)
    @xxx.setter         -> setter (กำหนดค่า)
    @xxx.deleter        -> deleter (ลบค่า) - ไม่ค่อยใช้

    ตัวอย่าง:
        value = sensor.slope      # เรียก getter
        sensor.slope = -6.0       # เรียก setter
    """)


# ==============================================================================
# ส่วนที่ 2: สาธิต Read-only Property
# Part 2: Demonstrate Read-only Property
# ==============================================================================
def demonstrate_readonly_property():
    """
    สาธิต Read-only Property (Property ที่มีแค่ getter)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 2: Read-only Property")
    print("Part 2: Read-only Property")
    print("=" * 60)

    print("""
    ===== Read-only Property =====

    Property ที่มีแค่ @property (getter) โดยไม่มี setter
    ไม่สามารถกำหนดค่าได้ - จะเกิด AttributeError

    ตัวอย่าง:
        @property
        def name(self):
            return self._name
        # ไม่มี @name.setter

    ใช้สำหรับ:
    - ค่าที่ไม่ควรเปลี่ยนหลังสร้าง object
    - ค่าที่คำนวณจาก attributes อื่น
    """)

    print("\n--- สร้าง PHSensor ---")
    sensor = PHSensor()

    print("\n--- Read-only Properties ---")
    print(f"sensor.name: {sensor.name}")
    print(f"sensor.pin_number: {sensor.pin_number}")
    print(f"sensor.is_initialized: {sensor.is_initialized}")
    print(f"sensor.calibration_equation: {sensor.calibration_equation}")

    print("\n--- ทดลองกำหนดค่าให้ read-only property ---")
    print("sensor.name = 'New Name'")
    try:
        sensor.name = "New Name"
    except AttributeError as e:
        print(f"AttributeError: {e}")
        print("(คาดไว้แล้ว - name เป็น read-only)")


# ==============================================================================
# ส่วนที่ 3: สาธิต Read-Write Property กับ Validation
# Part 3: Demonstrate Read-Write Property with Validation
# ==============================================================================
def demonstrate_readwrite_property():
    """
    สาธิต Read-Write Property พร้อม Validation
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 3: Read-Write Property กับ Validation")
    print("Part 3: Read-Write Property with Validation")
    print("=" * 60)

    print("""
    ===== Read-Write Property =====

    Property ที่มีทั้ง getter และ setter
    สามารถอ่านและกำหนดค่าได้

    @property
    def slope(self):
        return self._slope

    @slope.setter
    def slope(self, value):
        # Validation ก่อนกำหนดค่า
        if value > 0:
            print("Warning: slope should be negative")
        self._slope = value
    """)

    print("\n--- สร้าง PHSensor ---")
    sensor = PHSensor()
    sensor.init()

    print("\n--- อ่านค่า slope และ intercept ---")
    print(f"sensor.slope: {sensor.slope}")
    print(f"sensor.intercept: {sensor.intercept}")

    print("\n--- กำหนดค่า slope ใหม่ ---")
    print("sensor.slope = -6.0")
    sensor.slope = -6.0
    print(f"sensor.slope หลังเปลี่ยน: {sensor.slope}")

    print("\n--- Validation ใน setter ---")
    print("sensor.slope = 5.0  # ค่าบวก (ควรเป็นลบ)")
    sensor.slope = 5.0  # จะแสดง warning

    print("\n--- กำหนดค่า intercept ใหม่ ---")
    print("sensor.intercept = 17.0")
    sensor.intercept = 17.0
    print(f"sensor.intercept หลังเปลี่ยน: {sensor.intercept}")

    # Pump example
    print("\n" + "-" * 50)
    print("ตัวอย่าง Pump")
    print("-" * 50)

    pump = Pump()

    print("\n--- อ่านค่า flow_rate ---")
    print(f"pump.flow_rate: {pump.flow_rate}")

    print("\n--- กำหนดค่า flow_rate ใหม่ ---")
    print("pump.flow_rate = 0.3")
    pump.flow_rate = 0.3
    print(f"pump.flow_rate หลังเปลี่ยน: {pump.flow_rate}")

    print("\n--- Validation: ค่าต้อง > 0 ---")
    print("pump.flow_rate = -0.1  # ค่าติดลบ")
    try:
        pump.flow_rate = -0.1
    except ValueError as e:
        print(f"ValueError: {e}")
        print("(คาดไว้แล้ว - flow_rate ต้อง > 0)")

    pump.deinit()


# ==============================================================================
# ส่วนที่ 4: สาธิต Computed Property
# Part 4: Demonstrate Computed Property
# ==============================================================================
def demonstrate_computed_property():
    """
    สาธิต Computed Property (Property ที่คำนวณจาก attributes อื่น)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 4: Computed Property")
    print("Part 4: Computed Property")
    print("=" * 60)

    print("""
    ===== Computed Property =====

    Property ที่ไม่ได้เก็บค่าจริงๆ แต่คำนวณทุกครั้งที่เรียก

    @property
    def calibration_equation(self):
        # คำนวณจาก slope และ intercept
        return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"

    ข้อดี:
    - ค่าอัปเดตอัตโนมัติเมื่อ attributes ที่เกี่ยวข้องเปลี่ยน
    - ไม่ต้องเก็บค่าซ้ำซ้อน
    """)

    print("\n--- สร้าง PHSensor ---")
    sensor = PHSensor()

    print("\n--- calibration_equation (Computed Property) ---")
    print(f"สมการปัจจุบัน: {sensor.calibration_equation}")

    print("\n--- เปลี่ยน slope และ intercept ---")
    sensor.slope = -5.5
    sensor.intercept = 15.0

    print(f"\n--- calibration_equation อัปเดตอัตโนมัติ ---")
    print(f"สมการใหม่: {sensor.calibration_equation}")


# ==============================================================================
# ส่วนที่ 5: Encapsulation - ซ่อน Private Attributes
# Part 5: Encapsulation - Hide Private Attributes
# ==============================================================================
def demonstrate_encapsulation():
    """
    สาธิต Encapsulation ด้วย private attributes
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 5: Encapsulation")
    print("Part 5: Encapsulation")
    print("=" * 60)

    print("""
    ===== Encapsulation คืออะไร? =====

    Encapsulation คือการซ่อนรายละเอียดภายในของ class
    - ใช้ _ นำหน้าสำหรับ private attributes
    - เข้าถึงผ่าน @property เท่านั้น

    Python Naming Conventions:
    - _variable : Private (convention, not enforced)
    - __variable : Name mangling (ป้องกันการเข้าถึงจาก subclass)
    - variable_ : หลีกเลี่ยง conflict กับ Python keywords

    ===== ทำไมต้อง Encapsulate? =====

    1. ป้องกันการเข้าถึงโดยตรง
    2. สามารถเพิ่ม validation ได้
    3. เปลี่ยน implementation ภายในได้โดยไม่กระทบภายนอก
    4. Interface คงที่แม้ implementation เปลี่ยน
    """)

    print("\n--- ตัวอย่างจาก PHSensor ---")
    sensor = PHSensor()

    print("\n--- Private Attributes (ขึ้นต้นด้วย _) ---")
    print("sensor._slope (private):", sensor._slope)
    print("sensor._intercept (private):", sensor._intercept)
    print("\nหมายเหตุ: ยังเข้าถึงได้ แต่ไม่ควรทำ (convention)")

    print("\n--- Public Interface (ผ่าน @property) ---")
    print("sensor.slope (property):", sensor.slope)
    print("sensor.intercept (property):", sensor.intercept)

    print("\n--- ความแตกต่าง ---")
    print("การเข้าถึง _slope โดยตรง: ไม่มี validation")
    print("การเข้าถึงผ่าน property: มี validation และ logging")


# ==============================================================================
# ส่วนที่ 6: สร้าง Class ที่ใช้ @property
# Part 6: Create Class with @property
# ==============================================================================
def demonstrate_create_class():
    """
    แสดงตัวอย่างการสร้าง class ที่ใช้ @property
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 6: สร้าง Class ที่ใช้ @property")
    print("Part 6: Create Class with @property")
    print("=" * 60)

    # สร้างตัวอย่าง class ง่ายๆ
    class CalibrationData:
        """
        ตัวอย่างคลาสสำหรับเก็บข้อมูล calibration
        (Example class for storing calibration data)
        """

        def __init__(self, slope=-5.79, intercept=16.77):
            # Private attributes
            self._slope = slope
            self._intercept = intercept
            self._is_valid = False

        # Read-only property
        @property
        def is_valid(self):
            """สถานะความถูกต้องของ calibration"""
            return self._is_valid

        # Read-write property กับ validation
        @property
        def slope(self):
            """ค่า slope"""
            return self._slope

        @slope.setter
        def slope(self, value):
            if not isinstance(value, (int, float)):
                raise TypeError("slope ต้องเป็นตัวเลข")
            if value > 0:
                print("คำเตือน: slope ควรเป็นค่าลบ")
            self._slope = value
            self._is_valid = False  # ต้อง validate ใหม่

        @property
        def intercept(self):
            """ค่า intercept"""
            return self._intercept

        @intercept.setter
        def intercept(self, value):
            if not isinstance(value, (int, float)):
                raise TypeError("intercept ต้องเป็นตัวเลข")
            self._intercept = value
            self._is_valid = False

        # Computed property
        @property
        def equation(self):
            """สมการ calibration"""
            return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"

        # Method
        def validate(self, r_squared):
            """ตรวจสอบความถูกต้องของ calibration"""
            self._is_valid = r_squared >= 0.99
            return self._is_valid

        def __repr__(self):
            return f"CalibrationData(slope={self._slope}, intercept={self._intercept})"

    print("\n--- Code ของ CalibrationData ---")
    print("""
    class CalibrationData:
        def __init__(self, slope=-5.79, intercept=16.77):
            self._slope = slope        # Private
            self._intercept = intercept # Private
            self._is_valid = False      # Private

        @property
        def slope(self):
            return self._slope

        @slope.setter
        def slope(self, value):
            if not isinstance(value, (int, float)):
                raise TypeError("slope ต้องเป็นตัวเลข")
            if value > 0:
                print("คำเตือน: slope ควรเป็นค่าลบ")
            self._slope = value

        @property
        def equation(self):  # Computed property
            return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"
    """)

    print("\n--- ทดสอบ CalibrationData ---")
    cal = CalibrationData()
    print(f"repr: {repr(cal)}")

    print(f"\nslope: {cal.slope}")
    print(f"intercept: {cal.intercept}")
    print(f"equation: {cal.equation}")
    print(f"is_valid: {cal.is_valid}")

    print("\n--- กำหนดค่าใหม่ ---")
    cal.slope = -6.0
    cal.intercept = 17.0
    print(f"equation หลังเปลี่ยน: {cal.equation}")

    print("\n--- Validate ---")
    cal.validate(0.995)
    print(f"is_valid หลัง validate: {cal.is_valid}")

    print("\n--- ทดสอบ validation ---")
    print("cal.slope = 'hello'")
    try:
        cal.slope = "hello"
    except TypeError as e:
        print(f"TypeError: {e}")


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
def main():
    """โปรแกรมหลัก (Main program)"""
    print("=" * 60)
    print("สาธิต @property และ Encapsulation")
    print("(Properties and Encapsulation Demo)")
    print("=" * 60)

    try:
        # ส่วนที่ 1: อธิบาย @property
        explain_property()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 2: Read-only Property
        demonstrate_readonly_property()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 3: Read-Write Property
        demonstrate_readwrite_property()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 4: Computed Property
        demonstrate_computed_property()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 5: Encapsulation
        demonstrate_encapsulation()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 6: สร้าง Class
        demonstrate_create_class()

    except KeyboardInterrupt:
        print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

    except Exception as e:
        print(f"\nข้อผิดพลาด (Error): {e}")

    finally:
        print("\n" + "=" * 60)
        print("สรุป (Summary):")
        print("- @property ทำให้ method ถูกเรียกเหมือน attribute")
        print("- @xxx.setter เพิ่ม validation เมื่อกำหนดค่า")
        print("- Private attributes ใช้ _ นำหน้า")
        print("- Encapsulation ซ่อนรายละเอียดและป้องกันการเข้าถึง")
        print("- Computed properties คำนวณค่าทุกครั้งที่เรียก")
        print("=" * 60)


# รันโปรแกรม
if __name__ == "__main__":
    main()

# ==============================================================================
# base_sensor.py - คลาสพื้นฐานสำหรับเซ็นเซอร์ทุกชนิด
# (Base Sensor Class - Abstract Base Class for All Sensors)
# ==============================================================================
# โมดูลนี้สาธิตแนวคิด OOP ระดับกลาง: Inheritance และ Abstract Base Class
# This module demonstrates intermediate OOP concepts: Inheritance and ABC
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Inheritance (การสืบทอด) - class Child(Parent)
#   2. เรียนรู้ Abstract Base Class และ interface design
#   3. ใช้ super().__init__() เพื่อเรียก constructor ของ parent class
#   4. เข้าใจ Method Overriding (การ override method ใน child class)
#   5. ใช้ @property decorator สำหรับ encapsulation
#
# แนวคิด OOP ที่สำคัญ (Key OOP Concepts):
#
#   Inheritance (การสืบทอด):
#   - Child class สืบทอดคุณสมบัติและ methods จาก Parent class
#   - ใช้ syntax: class ChildClass(ParentClass)
#   - Child สามารถ override methods ของ Parent ได้
#
#   Abstract Base Class (ABC):
#   - เป็น blueprint สำหรับ classes อื่นๆ
#   - กำหนด interface ที่ child classes ต้อง implement
#   - ไม่ควรสร้าง instance โดยตรง
#
#   Encapsulation:
#   - ซ่อนรายละเอียดภายในด้วย private attributes (_variable)
#   - เข้าถึงผ่าน @property และ @setter
#
# ==============================================================================

from machine import Pin, ADC
from time import sleep_ms


class BaseSensor:
    """
    คลาสพื้นฐานสำหรับเซ็นเซอร์ทุกชนิด (Abstract Base Class for all sensors)

    นี่คือ Abstract Base Class - ไม่ควรสร้าง instance โดยตรง
    This is an Abstract Base Class - should not be instantiated directly

    คลาสลูกต้อง implement methods ต่อไปนี้ (Child classes must implement):
        - read(): อ่านค่าจากเซ็นเซอร์ (Read value from sensor)
        - _init_hardware(): เริ่มต้นฮาร์ดแวร์ (Initialize hardware)

    ===== หลักการ Inheritance (Inheritance Principles) =====

    1. Child class สืบทอด attributes และ methods จาก Parent
       เช่น PHSensor จะได้รับ _name, _pin_number, is_available ฯลฯ

    2. Child class สามารถ:
       - ใช้ methods ของ Parent โดยตรง (เช่น log())
       - Override methods ของ Parent (เช่น read())
       - เพิ่ม methods ใหม่เฉพาะ Child (เช่น read_ph())

    3. super() ใช้เรียก methods ของ Parent class
       super().__init__() เรียก constructor ของ Parent

    ===== ตัวอย่างการใช้งาน (Usage Example) =====

    class MySensor(BaseSensor):
        def __init__(self, pin):
            # เรียก constructor ของ parent class ก่อน
            # Call parent constructor first
            super().__init__(name="My Sensor", pin=pin)

        def _init_hardware(self):
            # implement การเริ่มต้นฮาร์ดแวร์
            pass

        def read(self):
            # implement การอ่านค่า
            return some_value

    Attributes:
        _name (str): ชื่อเซ็นเซอร์ (Sensor name) - private
        _pin_number (int): หมายเลขขา GPIO (GPIO pin number) - private
        _is_initialized (bool): สถานะการเริ่มต้น (Initialization status) - private
        _last_value: ค่าล่าสุดที่อ่านได้ (Last read value) - private
        _read_count (int): จำนวนครั้งที่อ่าน (Read count) - private
    """

    # ===== Class Attributes (ค่าคงที่ระดับคลาส) =====
    # ค่าเหล่านี้ใช้ร่วมกันโดยทุก instances
    # These values are shared by all instances

    DEFAULT_SAMPLES = 10          # จำนวน samples เริ่มต้น (Default sample count)
    DEFAULT_DELAY_MS = 10         # เวลาหน่วงระหว่าง samples (Delay between samples)

    def __init__(self, name="Unknown Sensor", pin=None):
        """
        Constructor - สร้าง BaseSensor object

        ===== หลักการ __init__ ใน Inheritance =====

        เมื่อ child class มี __init__ ของตัวเอง ต้อง:
        1. เรียก super().__init__() เพื่อเริ่มต้น parent class
        2. จากนั้นจึงเริ่มต้น attributes เฉพาะของ child

        Args:
            name (str): ชื่อเซ็นเซอร์สำหรับแสดงผล (Sensor name for display)
            pin (int): หมายเลขขา GPIO (GPIO pin number)

        หมายเหตุ (Note):
            Private attributes ขึ้นต้นด้วย _ (underscore)
            เช่น _name, _pin_number - ไม่ควรเข้าถึงจากภายนอกคลาส
        """
        # Private attributes (ใช้ _ นำหน้า)
        # ควรเข้าถึงผ่าน @property เท่านั้น
        self._name = name
        self._pin_number = pin
        self._is_initialized = False
        self._last_value = None
        self._read_count = 0

        # แสดงข้อความเริ่มต้น (Show initialization message)
        self.log(f"กำลังสร้าง {name} (Creating {name})")

    # =========================================================================
    # Properties - การใช้ @property สำหรับ Encapsulation
    # =========================================================================
    # @property ช่วยให้เข้าถึง private attributes ได้อย่างปลอดภัย
    # @property provides safe access to private attributes

    @property
    def name(self):
        """
        ชื่อเซ็นเซอร์ (Sensor name) - Read-only property

        ===== หลักการ @property =====

        @property ทำให้ method ถูกเรียกเหมือน attribute:
            sensor.name  # ไม่ต้องใช้ sensor.name()

        ข้อดี:
        1. ซ่อนรายละเอียดภายใน (Encapsulation)
        2. สามารถเพิ่ม logic การตรวจสอบได้
        3. เปลี่ยน implementation โดยไม่กระทบ code ภายนอก

        Returns:
            str: ชื่อเซ็นเซอร์ (Sensor name)
        """
        return self._name

    @property
    def pin_number(self):
        """
        หมายเลขขา GPIO (GPIO pin number) - Read-only property

        Returns:
            int: หมายเลขขา GPIO หรือ None
        """
        return self._pin_number

    @property
    def is_initialized(self):
        """
        สถานะการเริ่มต้นฮาร์ดแวร์ (Hardware initialization status)

        Returns:
            bool: True ถ้าเริ่มต้นแล้ว (if initialized)
        """
        return self._is_initialized

    @property
    def last_value(self):
        """
        ค่าล่าสุดที่อ่านได้ (Last read value) - Read-only

        Returns:
            ค่าล่าสุด หรือ None ถ้ายังไม่ได้อ่าน
        """
        return self._last_value

    @property
    def read_count(self):
        """
        จำนวนครั้งที่อ่านค่า (Number of readings taken)

        Returns:
            int: จำนวนครั้ง
        """
        return self._read_count

    # =========================================================================
    # Abstract Methods - ต้อง override ใน child class
    # =========================================================================
    # Methods เหล่านี้กำหนด "interface" ที่ child classes ต้อง implement
    # These methods define the "interface" that child classes must implement

    def read(self):
        """
        อ่านค่าจากเซ็นเซอร์ (Read value from sensor)

        ===== Abstract Method =====

        นี่คือ abstract method - child class ต้อง override
        This is an abstract method - child class must override

        ถ้าเรียกจาก BaseSensor โดยตรง จะ raise NotImplementedError
        Calling from BaseSensor directly will raise NotImplementedError

        Returns:
            ค่าที่อ่านได้ (ขึ้นอยู่กับประเภทเซ็นเซอร์)

        Raises:
            NotImplementedError: ถ้าเรียกจาก BaseSensor โดยตรง
        """
        raise NotImplementedError(
            f"คลาสลูกต้อง implement read() "
            f"(Child class must implement read())"
        )

    def _init_hardware(self):
        """
        เริ่มต้นฮาร์ดแวร์ - Abstract Method (Initialize hardware)

        Method นี้มี _ นำหน้า แสดงว่าเป็น internal method
        ไม่ควรเรียกจากภายนอกคลาส

        Raises:
            NotImplementedError: ถ้าเรียกจาก BaseSensor โดยตรง
        """
        raise NotImplementedError(
            f"คลาสลูกต้อง implement _init_hardware() "
            f"(Child class must implement _init_hardware())"
        )

    # =========================================================================
    # Concrete Methods - ใช้ได้ทันทีใน child classes
    # =========================================================================
    # Methods เหล่านี้ implement แล้ว child class สามารถใช้ได้เลย
    # These methods are already implemented, child classes can use directly

    def init(self):
        """
        เริ่มต้นเซ็นเซอร์ (Initialize sensor)

        เรียก _init_hardware() ที่ child class implement
        Calls _init_hardware() implemented by child class

        Returns:
            bool: True ถ้าสำเร็จ (if successful)
        """
        try:
            self._init_hardware()
            self._is_initialized = True
            self.log("เริ่มต้นสำเร็จ (Initialized successfully)")
            return True
        except Exception as e:
            self._is_initialized = False
            self.log(f"เริ่มต้นล้มเหลว (Initialization failed): {e}")
            return False

    def read_averaged(self, num_samples=None, delay_ms=None):
        """
        อ่านค่าเฉลี่ยจากหลาย samples (Read averaged value from multiple samples)

        ใช้ได้กับทุก child class ที่ implement read()
        Works with any child class that implements read()

        Args:
            num_samples (int): จำนวน samples (ค่าเริ่มต้น: DEFAULT_SAMPLES)
            delay_ms (int): เวลาหน่วงระหว่าง samples (ms)

        Returns:
            float: ค่าเฉลี่ย หรือ None ถ้าอ่านไม่ได้
        """
        samples = num_samples if num_samples else self.DEFAULT_SAMPLES
        delay = delay_ms if delay_ms else self.DEFAULT_DELAY_MS

        values = []
        for _ in range(samples):
            try:
                value = self.read()
                if value is not None:
                    values.append(value)
            except Exception as e:
                self.log(f"ข้อผิดพลาดขณะอ่าน (Read error): {e}")
            sleep_ms(delay)

        if values:
            return sum(values) / len(values)
        return None

    def read_filtered(self, num_samples=None, delay_ms=None):
        """
        อ่านค่าพร้อมกรอง outliers (Read with outlier filtering)

        วิธีการ: ตัดค่าสูงสุดและต่ำสุดออก แล้วเฉลี่ยที่เหลือ
        Method: Remove highest and lowest values, then average the rest

        Args:
            num_samples (int): จำนวน samples (ขั้นต่ำ 5)
            delay_ms (int): เวลาหน่วงระหว่าง samples

        Returns:
            float: ค่าเฉลี่ยหลังกรอง หรือ None
        """
        samples = max(5, num_samples if num_samples else self.DEFAULT_SAMPLES)
        delay = delay_ms if delay_ms else self.DEFAULT_DELAY_MS

        values = []
        for _ in range(samples):
            try:
                value = self.read()
                if value is not None:
                    values.append(value)
            except Exception:
                pass
            sleep_ms(delay)

        if len(values) >= 5:
            # เรียงลำดับและตัดค่าสุดขีด (Sort and trim extremes)
            values.sort()
            trimmed = values[1:-1]  # ตัดค่าแรกและค่าสุดท้าย
            return sum(trimmed) / len(trimmed)
        elif values:
            return sum(values) / len(values)
        return None

    def log(self, message):
        """
        แสดงข้อความ log พร้อมชื่อเซ็นเซอร์ (Display log message with sensor name)

        Args:
            message (str): ข้อความที่ต้องการแสดง
        """
        print(f"[{self._name}] {message}")

    def reset_read_count(self):
        """รีเซ็ตตัวนับการอ่าน (Reset read counter)"""
        self._read_count = 0
        self.log("รีเซ็ตตัวนับแล้ว (Read count reset)")

    # =========================================================================
    # Class Methods และ Static Methods
    # =========================================================================

    @classmethod
    def get_default_samples(cls):
        """
        รับค่า default samples (Get default sample count)

        ===== @classmethod =====

        Class method รับ cls (class) แทน self (instance)
        สามารถเรียกได้โดยไม่ต้องสร้าง instance:
            BaseSensor.get_default_samples()

        ใช้สำหรับ:
        - เข้าถึง class attributes
        - Factory methods (สร้าง instances)

        Returns:
            int: จำนวน samples เริ่มต้น
        """
        return cls.DEFAULT_SAMPLES

    @staticmethod
    def validate_pin(pin_number):
        """
        ตรวจสอบความถูกต้องของหมายเลขขา GPIO
        (Validate GPIO pin number)

        ===== @staticmethod =====

        Static method ไม่รับ self หรือ cls
        เป็น utility function ที่เกี่ยวข้องกับคลาส

        สามารถเรียกได้โดยไม่ต้องสร้าง instance:
            BaseSensor.validate_pin(25)

        Args:
            pin_number (int): หมายเลขขา GPIO

        Returns:
            bool: True ถ้าถูกต้อง

        Raises:
            ValueError: ถ้าหมายเลขขาไม่ถูกต้อง
        """
        # ESP32 valid GPIO pins (ไม่รวม pins ที่ใช้ภายใน)
        valid_pins = [0, 2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19,
                      21, 22, 23, 25, 26, 27, 32, 33, 34, 35, 36, 39]

        if pin_number not in valid_pins:
            raise ValueError(
                f"GPIO{pin_number} ไม่ถูกต้อง "
                f"(GPIO{pin_number} is invalid)"
            )
        return True

    @staticmethod
    def celsius_to_fahrenheit(celsius):
        """
        แปลงอุณหภูมิจากเซลเซียสเป็นฟาเรนไฮต์
        (Convert temperature from Celsius to Fahrenheit)

        Static method เหมาะสำหรับ utility functions
        ไม่ต้องการ instance หรือ class data

        Args:
            celsius (float): อุณหภูมิในหน่วยเซลเซียส

        Returns:
            float: อุณหภูมิในหน่วยฟาเรนไฮต์
        """
        return celsius * 9 / 5 + 32

    @staticmethod
    def celsius_to_kelvin(celsius):
        """
        แปลงอุณหภูมิจากเซลเซียสเป็นเคลวิน
        (Convert temperature from Celsius to Kelvin)

        Args:
            celsius (float): อุณหภูมิในหน่วยเซลเซียส

        Returns:
            float: อุณหภูมิในหน่วยเคลวิน
        """
        return celsius + 273.15

    # =========================================================================
    # Magic Methods (Dunder Methods)
    # =========================================================================

    def __repr__(self):
        """
        แสดงข้อมูล object สำหรับ debugging
        (Display object info for debugging)

        ===== __repr__ =====

        เรียกเมื่อใช้ repr(object) หรือพิมพ์ใน REPL
        ควรคืนค่า string ที่สามารถสร้าง object ใหม่ได้

        Returns:
            str: ข้อมูล object
        """
        return (f"{self.__class__.__name__}("
                f"name='{self._name}', "
                f"pin={self._pin_number}, "
                f"initialized={self._is_initialized})")

    def __str__(self):
        """
        แสดงข้อมูล object สำหรับผู้ใช้
        (Display object info for users)

        ===== __str__ =====

        เรียกเมื่อใช้ str(object) หรือ print(object)
        ควรคืนค่า string ที่อ่านง่ายสำหรับผู้ใช้

        Returns:
            str: ข้อมูล object สำหรับผู้ใช้
        """
        status = "พร้อมใช้งาน (Ready)" if self._is_initialized else "ยังไม่เริ่มต้น (Not initialized)"
        return f"{self._name} at GPIO{self._pin_number} - {status}"


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("BaseSensor - Abstract Base Class สำหรับเซ็นเซอร์")
    print("(BaseSensor - Abstract Base Class for Sensors)")
    print("=" * 60)

    print("\n--- ทดสอบ Static Methods ---")
    print(f"Default samples: {BaseSensor.get_default_samples()}")

    # ทดสอบ static method
    print(f"\n25 C = {BaseSensor.celsius_to_fahrenheit(25):.1f} F")
    print(f"25 C = {BaseSensor.celsius_to_kelvin(25):.2f} K")

    # ทดสอบ validate_pin
    try:
        BaseSensor.validate_pin(25)
        print("GPIO25 ถูกต้อง (GPIO25 is valid)")
    except ValueError as e:
        print(e)

    # ทดสอบสร้าง BaseSensor โดยตรง (จะ error เมื่อเรียก read())
    print("\n--- ทดสอบสร้าง BaseSensor โดยตรง ---")
    sensor = BaseSensor(name="Test Sensor", pin=25)
    print(repr(sensor))
    print(str(sensor))

    # ทดสอบเรียก read() - จะ raise NotImplementedError
    print("\n--- ทดสอบเรียก read() ---")
    try:
        sensor.read()
    except NotImplementedError as e:
        print(f"Error (คาดไว้): {e}")

    print("\n" + "=" * 60)
    print("หมายเหตุ: BaseSensor เป็น Abstract Base Class")
    print("ต้องสร้าง child class (เช่น PHSensor, TempSensor)")
    print("เพื่อใช้งานจริง")
    print("=" * 60)

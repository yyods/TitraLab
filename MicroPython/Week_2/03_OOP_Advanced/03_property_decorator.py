# ==============================================================================
# 03_property_decorator.py - การใช้ @property และ Encapsulation
# (Using @property and Encapsulation)
# ==============================================================================
# เวลาในการสอน: ~45 นาที (Teaching time: ~45 minutes)
#
# โปรแกรมนี้สอนการใช้ @property สำหรับนิสิตเคมี
# This program teaches @property usage for chemistry students
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ @property decorator
#   2. เรียนรู้ @property.setter สำหรับ validation
#   3. เข้าใจ Encapsulation และ private attributes
#   4. เห็นประโยชน์ของการซ่อนข้อมูลภายใน
#
# การเชื่อมโยงกับเคมี (Chemistry Connection):
#   - slope และ intercept ของสมการ calibration ควรถูกควบคุม
#   - flow_rate ต้องเป็นค่าบวกเท่านั้น
#   - ค่า calibration ภายในไม่ควรถูกแก้ไขโดยตรง
#
# ==============================================================================

from machine import Pin, ADC
from time import sleep_ms


# ==============================================================================
# คลาสตัวอย่าง (Example Classes)
# ==============================================================================

class BadSensor:
    """
    ตัวอย่างคลาสที่ไม่ดี - ใช้ public attributes โดยตรง

    ปัญหา:
    - ใครๆ ก็แก้ไข slope, intercept ได้
    - ไม่มีการตรวจสอบค่า
    - ถ้าต้องการเพิ่ม logic ต้องแก้ทุกที่
    """
    def __init__(self):
        self.slope = -5.79       # Public - ใครก็แก้ได้
        self.intercept = 16.77   # Public - ใครก็แก้ได้


class GoodSensor:
    """
    ตัวอย่างคลาสที่ดี - ใช้ @property กับ validation

    ข้อดี:
    - ควบคุมการเข้าถึง slope, intercept
    - มีการตรวจสอบค่าใน setter
    - เปลี่ยน implementation ได้โดยไม่กระทบโค้ดภายนอก
    """

    def __init__(self, slope=-5.79, intercept=16.77):
        # Private attributes (ขึ้นต้นด้วย _)
        self._slope = slope
        self._intercept = intercept
        print(f"[GoodSensor] สร้างเซ็นเซอร์")

    # =========================================================================
    # @property - Getter
    # =========================================================================

    @property
    def slope(self):
        """
        ค่า slope ของสมการ calibration (Getter)

        @property ทำให้ method นี้ถูกเรียกเหมือน attribute:
            value = sensor.slope  # ไม่ต้องใช้ ()

        Returns:
            float: ค่า slope
        """
        return self._slope

    # =========================================================================
    # @property.setter - Setter with Validation
    # =========================================================================

    @slope.setter
    def slope(self, value):
        """
        กำหนดค่า slope ใหม่พร้อม validation (Setter)

        @slope.setter ทำให้กำหนดค่าได้:
            sensor.slope = -6.0  # เรียก setter นี้

        Validation:
        1. ตรวจสอบประเภทข้อมูล
        2. ตรวจสอบว่าค่าสมเหตุสมผล

        Args:
            value: ค่า slope ใหม่

        Raises:
            TypeError: ถ้าค่าไม่ใช่ตัวเลข
        """
        # Validation 1: ตรวจสอบประเภท
        if not isinstance(value, (int, float)):
            raise TypeError("slope ต้องเป็นตัวเลข (slope must be a number)")

        # Validation 2: ตรวจสอบค่าสมเหตุสมผล
        if value > 0:
            print(f"[GoodSensor] คำเตือน: slope ควรเป็นค่าลบ (slope should be negative)")

        self._slope = value
        print(f"[GoodSensor] slope ใหม่: {value}")

    @property
    def intercept(self):
        """ค่า intercept ของสมการ calibration"""
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """กำหนดค่า intercept ใหม่"""
        if not isinstance(value, (int, float)):
            raise TypeError("intercept ต้องเป็นตัวเลข")
        self._intercept = value
        print(f"[GoodSensor] intercept ใหม่: {value}")

    # =========================================================================
    # Read-only Property (ไม่มี setter)
    # =========================================================================

    @property
    def equation(self):
        """
        สมการ calibration - Read-only (ไม่มี setter)

        Computed property: คำนวณจาก slope และ intercept
        อัปเดตอัตโนมัติเมื่อ slope หรือ intercept เปลี่ยน

        Returns:
            str: สมการในรูปแบบ string
        """
        return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"


class pHSensor:
    """
    คลาสเซ็นเซอร์ pH พร้อม @property และ Encapsulation

    การเชื่อมโยงกับเคมี:
    - slope มาจากสมการ Nernst: slope ทฤษฎีที่ 25C = -59.16 mV/pH
    - intercept มาจาก offset ของ reference electrode
    - สมการ: pH = slope * voltage + intercept
    """

    # Constants - ค่าคงที่สำหรับ ADC และ Nernst
    ADC_MAX = 4095
    ADC_VREF = 3.3
    NERNST_SLOPE_25C = -59.16  # mV/pH ที่ 25C

    def __init__(self, pin=25, slope=-5.79, intercept=16.77):
        """
        สร้าง pH Sensor

        Args:
            pin (int): GPIO pin สำหรับ ADC (ค่าเริ่มต้น: 25)
            slope (float): ค่า slope จาก calibration
            intercept (float): ค่า intercept จาก calibration
        """
        # Private attributes
        self._pin_number = pin
        self._slope = slope
        self._intercept = intercept
        self._is_initialized = False
        self._adc = None
        self._read_count = 0
        self._last_ph = None

        print(f"[pHSensor] สร้างที่ GPIO{pin}")
        print(f"[pHSensor] สมการ: {self.calibration_equation}")

    # =========================================================================
    # Read-only Properties
    # =========================================================================

    @property
    def pin_number(self):
        """หมายเลข GPIO pin - Read-only"""
        return self._pin_number

    @property
    def is_initialized(self):
        """สถานะการเริ่มต้น - Read-only"""
        return self._is_initialized

    @property
    def read_count(self):
        """จำนวนครั้งที่อ่าน - Read-only"""
        return self._read_count

    @property
    def last_ph(self):
        """ค่า pH ล่าสุดที่อ่านได้ - Read-only"""
        return self._last_ph

    # =========================================================================
    # Read-write Properties with Validation
    # =========================================================================

    @property
    def slope(self):
        """ค่า slope ของสมการ calibration"""
        return self._slope

    @slope.setter
    def slope(self, value):
        """
        กำหนดค่า slope พร้อม validation

        ในเคมี: slope ควรเป็นค่าลบ (pH สูง = voltage ต่ำ)
        ค่าทฤษฎีที่ 25C = -59.16 mV/pH (แต่หน่วยที่ใช้อาจต่างกัน)
        """
        if not isinstance(value, (int, float)):
            raise TypeError("slope ต้องเป็นตัวเลข")
        if value > 0:
            print("[pHSensor] คำเตือน: slope ควรเป็นค่าลบตามสมการ Nernst")
        self._slope = value
        print(f"[pHSensor] slope ใหม่: {value:.4f}")

    @property
    def intercept(self):
        """ค่า intercept ของสมการ calibration"""
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """กำหนดค่า intercept"""
        if not isinstance(value, (int, float)):
            raise TypeError("intercept ต้องเป็นตัวเลข")
        self._intercept = value
        print(f"[pHSensor] intercept ใหม่: {value:.4f}")

    # =========================================================================
    # Computed Properties
    # =========================================================================

    @property
    def calibration_equation(self):
        """
        สมการ calibration (Computed property)

        คำนวณจาก slope และ intercept
        อัปเดตอัตโนมัติเมื่อค่าเปลี่ยน
        """
        return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"

    @property
    def nernst_slope_theoretical(self):
        """ค่า slope ทฤษฎีตาม Nernst ที่ 25C"""
        return self.NERNST_SLOPE_25C

    # =========================================================================
    # Methods
    # =========================================================================

    def init(self):
        """เริ่มต้น ADC"""
        try:
            self._adc = ADC(Pin(self._pin_number))
            self._adc.atten(ADC.ATTN_11DB)
            self._is_initialized = True
            print("[pHSensor] เริ่มต้น ADC สำเร็จ")
            return True
        except Exception as e:
            print(f"[pHSensor] เริ่มต้นล้มเหลว: {e}")
            return False

    def read_voltage(self):
        """อ่านแรงดัน (V)"""
        if not self._is_initialized:
            print("[pHSensor] ยังไม่ได้เริ่มต้น")
            return None
        raw = self._adc.read()
        voltage = (raw / self.ADC_MAX) * self.ADC_VREF
        return voltage

    def read_ph(self):
        """
        อ่านค่า pH

        ใช้สมการ: pH = slope * voltage + intercept
        """
        voltage = self.read_voltage()
        if voltage is None:
            return None
        ph = self._slope * voltage + self._intercept
        self._read_count += 1
        self._last_ph = ph
        return ph

    def set_calibration(self, slope, intercept):
        """กำหนดค่า calibration ใหม่"""
        self.slope = slope      # ผ่าน setter (มี validation)
        self.intercept = intercept
        print(f"[pHSensor] สมการใหม่: {self.calibration_equation}")


# ==============================================================================
# ส่วนสาธิต (Demonstration Section)
# ==============================================================================

if __name__ == "__main__":
    try:
        # ==============================================================================
        # ส่วนที่ 1: ปัญหาของ Public Attributes (10 นาที)
        # Part 1: Problems with Public Attributes (10 minutes)
        # ==============================================================================

        print("=" * 60)
        print("ส่วนที่ 1: ปัญหาของ Public Attributes")
        print("Part 1: Problems with Public Attributes")
        print("=" * 60)

        print("""
===== ปัญหาของ Public Attributes =====

class BadSensor:
    def __init__(self):
        self.slope = -5.79     # Public attribute
        self.intercept = 16.7   # Public attribute

ปัญหา:
1. ไม่สามารถ validate ค่าได้:
   sensor.slope = "hello"   # ผิดแต่ไม่มี error!

2. ไม่สามารถเพิ่ม logic ได้:
   sensor.slope = 10         # slope ควรเป็นค่าลบ!

3. เปลี่ยน implementation ยาก:
   ถ้าอยากเปลี่ยนเป็นคำนวณ slope ต้องแก้ทุกที่
""")

        # ทดสอบปัญหา
        print("\n--- ทดสอบ BadSensor ---")
        bad_sensor = BadSensor()
        print(f"slope เริ่มต้น: {bad_sensor.slope}")

        # ปัญหา 1: กำหนดค่าผิดประเภท
        print("\nปัญหา 1: กำหนดค่าผิดประเภท")
        bad_sensor.slope = "hello"  # ไม่ error!
        print(f"slope หลังกำหนด 'hello': {bad_sensor.slope}")

        # ปัญหา 2: กำหนดค่าที่ไม่สมเหตุสมผล
        print("\nปัญหา 2: กำหนดค่าที่ไม่สมเหตุสมผล")
        bad_sensor.slope = 100  # slope ควรเป็นค่าลบ แต่ไม่มี warning!
        print(f"slope หลังกำหนด 100: {bad_sensor.slope}")


        # ==============================================================================
        # ส่วนที่ 2: แก้ปัญหาด้วย @property (15 นาที)
        # Part 2: Solving with @property (15 minutes)
        # ==============================================================================

        print("\n" + "=" * 60)
        print("ส่วนที่ 2: แก้ปัญหาด้วย @property")
        print("Part 2: Solving with @property")
        print("=" * 60)

        print("""
===== @property แก้ปัญหาอย่างไร =====

@property ทำให้ method ถูกเรียกเหมือน attribute:
  - ไม่ต้องใช้ parentheses: sensor.slope แทน sensor.slope()
  - สามารถเพิ่ม validation ได้
  - Encapsulate implementation details

รูปแบบ:
  @property           -> getter (อ่านค่า)
  @xxx.setter         -> setter (กำหนดค่า)

ตัวอย่าง:
  value = sensor.slope      # เรียก getter
  sensor.slope = -6.0       # เรียก setter
""")

        # ทดสอบ GoodSensor
        print("\n--- ทดสอบ GoodSensor ---")
        good_sensor = GoodSensor()

        # อ่านค่า (เรียก getter)
        print(f"\nอ่านค่า slope: {good_sensor.slope}")
        print(f"อ่านค่า intercept: {good_sensor.intercept}")
        print(f"อ่านสมการ: {good_sensor.equation}")

        # กำหนดค่าถูกต้อง (เรียก setter)
        print("\n--- กำหนดค่าถูกต้อง ---")
        good_sensor.slope = -6.0
        good_sensor.intercept = 17.0
        print(f"สมการใหม่: {good_sensor.equation}")

        # กำหนดค่า slope เป็นบวก (จะมี warning)
        print("\n--- กำหนด slope เป็นบวก ---")
        good_sensor.slope = 5.0

        # กำหนดค่าผิดประเภท (จะ error)
        print("\n--- กำหนดค่าผิดประเภท ---")
        try:
            good_sensor.slope = "hello"
        except TypeError as e:
            print(f"TypeError: {e}")
            print("(คาดไว้แล้ว - slope ต้องเป็นตัวเลข)")

        # ทดลองแก้ read-only property
        print("\n--- ทดลองแก้ read-only property ---")
        try:
            good_sensor.equation = "pH = 0 * V + 7"
        except AttributeError as e:
            print(f"AttributeError: {e}")
            print("(คาดไว้แล้ว - equation เป็น read-only)")


        # ==============================================================================
        # ส่วนที่ 3: Encapsulation - การห่อหุ้มข้อมูล (10 นาที)
        # Part 3: Encapsulation (10 minutes)
        # ==============================================================================

        print("\n" + "=" * 60)
        print("ส่วนที่ 3: Encapsulation")
        print("Part 3: Encapsulation")
        print("=" * 60)

        print("""
===== Encapsulation คืออะไร? =====

Encapsulation คือการซ่อนรายละเอียดภายในของ class
ป้องกันการเข้าถึงโดยตรง

Python Naming Conventions:
  - variable  : Public - เข้าถึงได้จากภายนอก
  - _variable : Protected - ควรใช้ภายในเท่านั้น (convention)
  - __variable: Private - Python จะ name mangle

ทำไมต้อง Encapsulate?
1. ป้องกันการเข้าถึงโดยตรง
2. สามารถเพิ่ม validation ได้
3. เปลี่ยน implementation ได้โดยไม่กระทบภายนอก
4. Interface คงที่แม้ implementation เปลี่ยน
""")

        print("\n--- ตัวอย่าง Encapsulation ---")
        print(f"good_sensor._slope = {good_sensor._slope}")
        print("(ยังเข้าถึง _slope ได้ แต่ไม่ควรทำ - เป็น convention)")
        print("\nหมายเหตุ: Python ไม่บังคับ private จริงๆ")
        print("แต่ _ นำหน้าบอกว่า 'ไม่ควรเข้าถึงจากภายนอก'")


        # ==============================================================================
        # ส่วนที่ 4: ตัวอย่างจริง - pH Sensor Class (10 นาที)
        # Part 4: Real Example - pH Sensor Class (10 minutes)
        # ==============================================================================

        print("\n" + "=" * 60)
        print("ส่วนที่ 4: ตัวอย่างจริง - pH Sensor Class")
        print("Part 4: Real Example - pH Sensor Class")
        print("=" * 60)

        # ทดสอบ pHSensor
        print("\n--- ทดสอบ pHSensor ---")
        ph_sensor = pHSensor()

        # อ่าน properties
        print(f"\npin_number: {ph_sensor.pin_number}")
        print(f"slope: {ph_sensor.slope}")
        print(f"intercept: {ph_sensor.intercept}")
        print(f"calibration_equation: {ph_sensor.calibration_equation}")

        # เปลี่ยนค่า calibration
        print("\n--- เปลี่ยนค่า calibration ---")
        ph_sensor.set_calibration(-6.0, 17.0)
        print(f"สมการใหม่: {ph_sensor.calibration_equation}")

        # เริ่มต้นและอ่านค่า
        print("\n--- เริ่มต้นและอ่านค่า ---")
        if ph_sensor.init():
            for i in range(3):
                voltage = ph_sensor.read_voltage()
                ph = ph_sensor.read_ph()
                print(f"ครั้งที่ {i+1}: V={voltage:.4f}V, pH={ph:.2f}")
                sleep_ms(500)

            print(f"\nจำนวนครั้งที่อ่าน: {ph_sensor.read_count}")
            print(f"ค่า pH ล่าสุด: {ph_sensor.last_ph:.2f}")


        # ==============================================================================
        # ส่วนที่ 5: สรุป
        # Part 5: Summary
        # ==============================================================================

        print("\n" + "=" * 60)
        print("สรุป (Summary)")
        print("=" * 60)

        print("""
สิ่งที่เรียนรู้ในบทนี้:

1. @property decorator:
   - ทำให้ method ถูกเรียกเหมือน attribute
   - ไม่ต้องใช้ () เมื่อเรียก

2. @xxx.setter:
   - กำหนดค่าผ่าน property
   - สามารถเพิ่ม validation ได้

3. Read-only vs Read-write Properties:
   - Read-only: มีแค่ @property (ไม่มี setter)
   - Read-write: มีทั้ง @property และ @xxx.setter

4. Computed Properties:
   - คำนวณค่าทุกครั้งที่เรียก
   - อัปเดตอัตโนมัติเมื่อค่าที่เกี่ยวข้องเปลี่ยน

5. Encapsulation:
   - ซ่อนข้อมูลภายในด้วย _ prefix
   - เข้าถึงผ่าน @property
   - ป้องกันการแก้ไขโดยตรง

การเชื่อมโยงกับเคมี:
   - slope/intercept = ค่าจาก pH calibration
   - Nernst equation: E = E0 - (2.303RT/nF) * pH
   - ที่ 25C: slope ทฤษฎี = -59.16 mV/pH
   - Validation ช่วยป้องกันค่าที่ไม่สมเหตุสมผล
""")

        print("=" * 60)
        print("จบบทเรียน @property และ Encapsulation")
        print("(End of @property and Encapsulation)")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 50)
        print("หยุดโปรแกรมโดยผู้ใช้ (Stopped by user - Ctrl+C)")
        print("=" * 50)
    except Exception as e:
        print(f"\n*** ข้อผิดพลาด (Error): {e} ***")

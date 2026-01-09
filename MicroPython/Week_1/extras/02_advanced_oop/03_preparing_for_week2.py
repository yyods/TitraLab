# ==============================================================================
# 03_preparing_for_week2.py - เตรียมพร้อมสู่สัปดาห์ที่ 2 (Preparing for Week 2)
# ==============================================================================
# สัปดาห์ที่ 1: ปูพื้นฐานแนวคิดที่จะใช้ในสัปดาห์ถัดไป
# Week 1: Foundation concepts for next week
#
# ไฟล์นี้แนะนำแนวคิดใหม่ที่จะสำคัญในสัปดาห์ที่ 2:
# This file introduces new concepts important for Week 2:
#   1. @property decorator - วิธีสร้าง "computed attribute"
#   2. _underscore convention - การตั้งชื่อตัวแปร private
#   3. Preview of Inheritance - แนวคิดการสืบทอด
#   4. ภาพรวมระบบ TitraLab - Week 1 classes เป็นส่วนหนึ่งของระบบใหญ่
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ @property decorator และประโยชน์
#   2. เข้าใจหลักการ encapsulation ด้วย _underscore
#   3. เห็นภาพรวมว่า inheritance คืออะไร (ยังไม่ implement)
#   4. เชื่อมโยง Week 1 กับระบบไทเทรชันที่จะสร้าง
#
# ==============================================================================


# ==============================================================================
# ส่วนที่ 1: @property Decorator คืออะไร? (What is @property?)
# ==============================================================================
#
# ในห้องปฏิบัติการเคมี บางค่าต้อง "คำนวณ" ไม่ใช่เก็บตรงๆ เช่น:
#   - pH = -log10[H+]  (คำนวณจากความเข้มข้นไฮโดรเจนไอออน)
#   - อุณหภูมิ Fahrenheit = (Celsius * 9/5) + 32
#   - เปอร์เซ็นต์ = (ค่าปัจจุบัน / ค่าสูงสุด) * 100
#
# @property ช่วยให้เราสร้าง "computed attribute" ที่:
#   - ดูเหมือนตัวแปร: sensor.fahrenheit
#   - แต่จริงๆ เป็นการเรียกฟังก์ชัน: get_fahrenheit()
#
# In chemistry lab, some values must be "calculated", not stored directly:
#   - pH = -log10[H+]
#   - Temperature in Fahrenheit = (Celsius * 9/5) + 32
#   - Percentage = (current / max) * 100
#
# @property helps us create "computed attributes" that:
#   - Look like variables: sensor.fahrenheit
#   - But actually call a function: get_fahrenheit()
#
# ==============================================================================


class TemperatureReading:
    """
    ตัวอย่างการใช้ @property (Example of using @property)

    คลาสนี้แสดงวิธีสร้าง "computed attribute" สำหรับแปลงหน่วยอุณหภูมิ

    This class demonstrates creating "computed attributes" for temperature conversion.
    """

    def __init__(self, celsius_value):
        """
        สร้าง TemperatureReading จากค่าองศาเซลเซียส
        (Create TemperatureReading from Celsius value)

        Args:
            celsius_value (float): อุณหภูมิในหน่วยเซลเซียส (temperature in Celsius)
        """
        # เก็บค่าเซลเซียสเป็น "private" ด้วย underscore
        # Store Celsius as "private" with underscore
        self._celsius = celsius_value

    # === @property decorator ===
    # ทำให้ method ดูเหมือนเป็นตัวแปร (attribute)
    # Makes a method look like a variable (attribute)

    @property
    def celsius(self):
        """
        อ่านค่าอุณหภูมิเป็นเซลเซียส (Read temperature in Celsius)

        การใช้งาน (Usage):
            temp = TemperatureReading(25)
            print(temp.celsius)  # 25 - ไม่ต้องใส่วงเล็บ ()!
        """
        return self._celsius

    @property
    def fahrenheit(self):
        """
        อ่านค่าอุณหภูมิเป็นฟาเรนไฮต์ - คำนวณอัตโนมัติ
        (Read temperature in Fahrenheit - calculated automatically)

        สูตร (Formula): F = (C * 9/5) + 32

        การใช้งาน (Usage):
            temp = TemperatureReading(25)
            print(temp.fahrenheit)  # 77.0
        """
        return (self._celsius * 9 / 5) + 32

    @property
    def kelvin(self):
        """
        อ่านค่าอุณหภูมิเป็นเคลวิน - ใช้ในการคำนวณทางเคมี
        (Read temperature in Kelvin - used in chemistry calculations)

        สูตร (Formula): K = C + 273.15

        สำคัญสำหรับเคมี (Important for chemistry):
        - สมการ Nernst ใช้อุณหภูมิเป็น Kelvin
        - ค่าคงที่ก๊าซ R ใช้กับ Kelvin
        """
        return self._celsius + 273.15

    # === @property.setter ===
    # ให้สามารถกำหนดค่าผ่าน property ได้ (Allow setting value via property)

    @celsius.setter
    def celsius(self, value):
        """
        กำหนดค่าอุณหภูมิใหม่ (Set new temperature value)

        การใช้งาน (Usage):
            temp.celsius = 30  # กำหนดค่าใหม่ได้เหมือนตัวแปร
        """
        # ตรวจสอบค่าก่อนบันทึก (Validate before storing)
        if value < -273.15:
            print("ข้อผิดพลาด: อุณหภูมิต่ำกว่า absolute zero ไม่ได้")
            print("(Error: Temperature cannot be below absolute zero)")
            return
        self._celsius = value


# ==============================================================================
# ส่วนที่ 2: _Underscore Convention (หลักการตั้งชื่อ Private)
# ==============================================================================
#
# ใน Python เราใช้ underscore (_) เพื่อบอกว่าตัวแปรเป็น "private":
#
#   self.name       = Public - ใช้ได้จากภายนอก
#   self._pin       = Private - ควรใช้ภายใน class เท่านั้น
#   self.__secret   = Name mangling - Python เปลี่ยนชื่อให้
#
# ทำไมต้องใช้ underscore? (Why use underscore?)
#   1. บอกผู้ใช้ว่า "อย่าแตะตัวแปรนี้โดยตรง"
#   2. ป้องกันการเปลี่ยนค่าโดยไม่ได้ตั้งใจ
#   3. ให้ class ควบคุม "วิธีเข้าถึง" ข้อมูล
#
# In Python, we use underscore (_) to indicate "private" variables:
#
#   self.name       = Public - can be used from outside
#   self._pin       = Private - should only be used inside class
#   self.__secret   = Name mangling - Python changes the name
#
# Why use underscore?
#   1. Tell users "don't touch this variable directly"
#   2. Prevent accidental value changes
#   3. Let the class control "how to access" data
#
# ==============================================================================


class PHSensor:
    """
    ตัวอย่าง Private Variable Convention (Example of Private Variable Convention)

    แสดงการใช้ _underscore เพื่อซ่อนรายละเอียด hardware

    Demonstrates using _underscore to hide hardware details.
    """

    def __init__(self, adc_pin=25):
        """
        สร้าง pH Sensor (Create pH Sensor)

        Args:
            adc_pin (int): หมายเลขขา ADC (ADC pin number)
                          TitraLab ใช้ GPIO25 สำหรับ pH sensor
        """
        # === Public Variables ===
        # ผู้ใช้เข้าถึงได้โดยตรง (User can access directly)
        self.name = "pH Sensor"

        # === Private Variables (ขึ้นต้นด้วย _) ===
        # ผู้ใช้ไม่ควรเข้าถึงโดยตรง (User should not access directly)
        self._adc_pin = adc_pin          # เก็บหมายเลข pin
        self._calibration_offset = 0.0   # ค่าชดเชยจากการ calibrate
        self._calibration_slope = 1.0    # ความชันจากการ calibrate
        self._last_raw_value = 0         # ค่าดิบล่าสุดที่อ่านได้

        # หมายเหตุ: ในโค้ดจริงจะสร้าง ADC object ที่นี่
        # Note: In real code, would create ADC object here
        # self._adc = ADC(Pin(adc_pin))

    @property
    def ph(self):
        """
        อ่านค่า pH (Read pH value)

        ค่า pH คำนวณจาก: raw_voltage * slope + offset
        pH value calculated from: raw_voltage * slope + offset
        """
        # จำลองการอ่านค่า (Simulated reading)
        raw_voltage = 2.5  # จะเป็น self._adc.read_uv() / 1000000 ในโค้ดจริง

        # คำนวณ pH จาก calibration
        ph_value = raw_voltage * self._calibration_slope + self._calibration_offset
        return ph_value

    def calibrate(self, buffer_ph, measured_voltage):
        """
        ปรับเทียบเซ็นเซอร์ (Calibrate sensor)

        Args:
            buffer_ph (float): ค่า pH ของ buffer มาตรฐาน (standard buffer pH)
            measured_voltage (float): แรงดันที่วัดได้ (measured voltage)

        ในห้องปฏิบัติการจริง จะใช้ buffer pH 4.0 และ 7.0
        In real lab, would use pH 4.0 and pH 7.0 buffers
        """
        # อัพเดตค่า calibration (Update calibration values)
        # นี่คือตัวอย่างอย่างง่าย
        self._calibration_offset = buffer_ph - measured_voltage
        print(f"Calibrated: offset = {self._calibration_offset:.2f}")


# ==============================================================================
# ส่วนที่ 3: Preview of Inheritance (แนวคิดการสืบทอด)
# ==============================================================================
#
# Inheritance คืออะไร? (What is Inheritance?)
#
# จินตนาการว่าในห้องปฏิบัติการมีเซ็นเซอร์หลายประเภท:
#   - pH Sensor      -> อ่านค่า pH
#   - Temperature Sensor -> อ่านอุณหภูมิ
#   - Conductivity Sensor -> อ่านค่านำไฟฟ้า
#
# ทุกตัวมีสิ่งที่เหมือนกัน (All have common features):
#   - มีชื่อ (name)
#   - อ่านค่าได้ (read)
#   - ต้อง calibrate
#   - ต้อง cleanup
#
# แทนที่จะเขียนซ้ำ เราสามารถสร้าง "แม่แบบ" (base class):
#   class Sensor:        <- แม่แบบ (base class)
#       name, read(), calibrate()
#
#   class PHSensor(Sensor):       <- ลูก สืบทอดจาก Sensor
#   class TempSensor(Sensor):     <- ลูก สืบทอดจาก Sensor
#
# สัปดาห์ที่ 2 เราจะเรียนรู้การ implement inheritance!
#
# ==============================================================================


# ตัวอย่างแบบ PREVIEW (ยังไม่ต้องเข้าใจทั้งหมด)
# Example as PREVIEW (don't need to understand everything yet)

class Sensor:
    """
    [PREVIEW] Base class สำหรับเซ็นเซอร์ทุกประเภท
    ([PREVIEW] Base class for all sensor types)

    นี่คือตัวอย่างว่า inheritance จะช่วยอย่างไรในสัปดาห์ที่ 2
    This is a preview of how inheritance will help in Week 2
    """

    def __init__(self, name):
        self.name = name
        self._value = 0

    def read(self):
        """อ่านค่า - ลูกจะ override method นี้ (Child will override this)"""
        raise NotImplementedError("Subclass must implement read()")

    def get_status(self):
        """แสดงสถานะ (Show status)"""
        return f"{self.name}: ค่าล่าสุด = {self._value}"


# ในสัปดาห์ที่ 2 เราจะเรียนรู้วิธีสร้าง:
# In Week 2, we will learn to create:
#
# class PHSensor(Sensor):       # สืบทอดจาก Sensor
#     def read(self):
#         # อ่านจาก ADC แล้วแปลงเป็น pH
#         pass
#
# class TempSensor(Sensor):     # สืบทอดจาก Sensor
#     def read(self):
#         # อ่านจาก DS18B20
#         pass


# ==============================================================================
# ส่วนที่ 4: Week 1 Classes ในระบบใหญ่ (Week 1 Classes in the Big Picture)
# ==============================================================================
#
# Classes ที่เรียนในสัปดาห์ที่ 1 จะเป็นส่วนประกอบของระบบไทเทรชัน:
#
# Week 1 classes will be components of the titration system:
#
#   +--------------------------------------------------+
#   |            TitrationSystem (สัปดาห์ 3+)           |
#   +--------------------------------------------------+
#   |                                                  |
#   |  +-------------+  +----------------+             |
#   |  | PHSensor    |  | TempSensor     |  <- Week 2  |
#   |  | (สัปดาห์ 2) |  | (สัปดาห์ 2)    |             |
#   |  +-------------+  +----------------+             |
#   |                                                  |
#   |  +--------+  +--------+  +---------+             |
#   |  | LED    |  | Button |  | Buzzer  |  <- Week 1  |
#   |  +--------+  +--------+  +---------+             |
#   |                                                  |
#   |  +--------+  +--------+  +---------+             |
#   |  | Pump   |  | Display|  | SDCard  |  <- Week 2  |
#   |  +--------+  +--------+  +---------+             |
#   |                                                  |
#   +--------------------------------------------------+
#
# ระบบไทเทรชันอัตโนมัติประกอบด้วย:
# Automatic titration system consists of:
#   - เซ็นเซอร์ (Sensors): pH, Temperature
#   - ตัวทำงาน (Actuators): Pump, LED, Buzzer
#   - อินเทอร์เฟซผู้ใช้ (User Interface): Display, Buttons
#   - เก็บข้อมูล (Data Storage): SD Card
#
# ==============================================================================


# ==============================================================================
# ส่วนที่ 5: ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("เตรียมพร้อมสู่สัปดาห์ที่ 2 (Preparing for Week 2)")
    print("=" * 60)

    # === ทดสอบ @property ===
    print("\n--- ทดสอบ @property decorator ---\n")

    # สร้าง TemperatureReading ด้วยค่าเซลเซียส
    # Create TemperatureReading with Celsius value
    temp = TemperatureReading(25.0)

    # อ่านค่าผ่าน @property (ไม่ต้องใส่วงเล็บ!)
    # Read values via @property (no parentheses needed!)
    print(f"อุณหภูมิ (Temperature):")
    print(f"  Celsius:    {temp.celsius:.1f} C")
    print(f"  Fahrenheit: {temp.fahrenheit:.1f} F")
    print(f"  Kelvin:     {temp.kelvin:.2f} K")

    # เปรียบเทียบ: ถ้าไม่มี @property ต้องเขียน:
    # Compare: without @property, would write:
    #   temp.get_celsius()
    #   temp.get_fahrenheit()
    #   temp.get_kelvin()

    # ทดสอบ setter
    print("\n--- ทดสอบ @property setter ---\n")
    print("เปลี่ยนอุณหภูมิเป็น 100 C (Changing to 100 C)")
    temp.celsius = 100.0

    print(f"  Celsius:    {temp.celsius:.1f} C")
    print(f"  Fahrenheit: {temp.fahrenheit:.1f} F  (น้ำเดือด = 212 F)")
    print(f"  Kelvin:     {temp.kelvin:.2f} K")

    # ทดสอบการตรวจสอบค่า (Test validation)
    print("\n--- ทดสอบการตรวจสอบค่า (Testing validation) ---\n")
    print("ลองตั้งค่าต่ำกว่า absolute zero (-300 C):")
    temp.celsius = -300  # จะแสดง error

    # === ทดสอบ Private Convention ===
    print("\n--- ทดสอบ Private Variable Convention ---\n")

    sensor = PHSensor(25)

    print(f"Public variable - sensor.name: {sensor.name}")
    print(f"@property - sensor.ph: {sensor.ph:.2f}")

    # สามารถเข้าถึง _private ได้ แต่ไม่ควรทำ
    # Can access _private but shouldn't
    print(f"\n[ไม่แนะนำ] sensor._adc_pin: {sensor._adc_pin}")
    print("  ^ Python ยอมให้เข้าถึง แต่ _ บอกว่า 'อย่าแตะ'")
    print("  ^ Python allows access, but _ means 'don't touch'")

    # แสดง calibration
    print("\n--- ทดสอบ calibration ---\n")
    sensor.calibrate(7.0, 2.5)

    # === สรุป ===
    print("\n" + "=" * 60)
    print("สรุปสิ่งที่เรียนรู้ (What we learned):")
    print("=" * 60)
    print("""
1. @property Decorator
   - ทำให้ method ดูเหมือน attribute (variable)
   - ใช้: temp.fahrenheit แทน temp.get_fahrenheit()
   - เหมาะสำหรับ "computed values" ที่คำนวณจากข้อมูลอื่น
   - @property.setter ให้กำหนดค่าได้ พร้อม validation

2. _Underscore Convention
   - self.name    = Public - ใช้ได้จากภายนอก
   - self._pin    = Private - ใช้ภายใน class เท่านั้น
   - เป็น "convention" ไม่ได้บังคับ แต่ควรปฏิบัติตาม

3. Preview: Inheritance
   - Base class = แม่แบบ ที่ลูกสืบทอดได้
   - class Child(Parent): สร้าง class ที่สืบทอด
   - ช่วยลดการเขียนโค้ดซ้ำซ้อน
   - จะเรียนละเอียดในสัปดาห์ที่ 2

4. ภาพรวมระบบ TitraLab
   - Week 1: LED, Button, Buzzer (พื้นฐาน)
   - Week 2: Sensors, Pump, Display (เฉพาะทาง)
   - Week 3+: รวมทุกอย่างเป็นระบบไทเทรชัน

สัปดาห์หน้า (Next Week):
   - Inheritance และ Polymorphism
   - สร้าง Sensor classes ที่ใช้งานจริง
   - เชื่อมต่อกับ hardware มากขึ้น
""")
    print("พร้อมสำหรับสัปดาห์ที่ 2! (Ready for Week 2!)")

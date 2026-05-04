# ==============================================================================
# 01_sensor_inheritance.py - สาธิต Inheritance กับเซ็นเซอร์
# (Inheritance Demo with Sensors)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ Inheritance ในการออกแบบคลาสเซ็นเซอร์
# This program demonstrates Inheritance in sensor class design
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Inheritance: class Child(Parent)
#   2. เรียนรู้ super().__init__() สำหรับเรียก parent constructor
#   3. เข้าใจ Method Overriding
#   4. เห็นประโยชน์ของการ inherit: code reuse
#
# โครงสร้างการ Inherit (Inheritance Structure):
#
#                    BaseSensor
#                   /          \
#              PHSensor      TempSensor
#
# สิ่งที่ PHSensor และ TempSensor ได้รับจาก BaseSensor:
#   - Attributes: _name, _pin_number, _is_initialized, _last_value, _read_count
#   - Properties: name, pin_number, is_initialized, last_value, read_count
#   - Methods: log(), read_averaged(), read_filtered(), init()
#   - Static methods: validate_pin(), celsius_to_fahrenheit()
#
# สิ่งที่ PHSensor และ TempSensor ต้อง override:
#   - read(): อ่านค่าเฉพาะเซ็นเซอร์
#   - _init_hardware(): เริ่มต้นฮาร์ดแวร์เฉพาะ
#
# Hardware Configuration:
#   - GPIO 25: pH Sensor (ADC)
#   - GPIO 16: DS18B20 Temperature Sensor (OneWire)
#
# ==============================================================================

from time import sleep_ms
import sys

# เพิ่ม lib path (Add lib to path)
sys.path.append('lib')

# นำเข้าคลาสเซ็นเซอร์ (Import sensor classes)
from lib.base_sensor import BaseSensor
from lib.ph_sensor import PHSensor
from lib.temp_sensor import TempSensor


# ==============================================================================
# ส่วนที่ 1: แสดงโครงสร้าง Inheritance
# Part 1: Show Inheritance Structure
# ==============================================================================
def demonstrate_inheritance_structure():
    """
    สาธิตโครงสร้างการ Inherit (Demonstrate inheritance structure)

    แสดงให้เห็นว่า PHSensor และ TempSensor สืบทอดจาก BaseSensor
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 1: โครงสร้าง Inheritance")
    print("Part 1: Inheritance Structure")
    print("=" * 60)

    # ตรวจสอบการ inherit (Check inheritance)
    print("\n--- ตรวจสอบการสืบทอด (Check inheritance) ---")

    # issubclass() ตรวจสอบว่า class A สืบทอดจาก class B หรือไม่
    print(f"PHSensor สืบทอดจาก BaseSensor? {issubclass(PHSensor, BaseSensor)}")
    print(f"TempSensor สืบทอดจาก BaseSensor? {issubclass(TempSensor, BaseSensor)}")

    # แสดง MRO (Method Resolution Order)
    print("\n--- Method Resolution Order (MRO) ---")
    print("ลำดับการค้นหา method ของ PHSensor:")
    for i, cls in enumerate(PHSensor.__mro__):
        print(f"  {i+1}. {cls.__name__}")

    print("\nลำดับการค้นหา method ของ TempSensor:")
    for i, cls in enumerate(TempSensor.__mro__):
        print(f"  {i+1}. {cls.__name__}")

    # แสดง attributes ที่สืบทอด
    print("\n--- Attributes ที่สืบทอดจาก BaseSensor ---")
    print("PHSensor และ TempSensor ได้รับ:")
    print("  - _name, _pin_number, _is_initialized")
    print("  - _last_value, _read_count")
    print("  - Properties: name, pin_number, is_initialized")
    print("  - Methods: log(), read_averaged(), read_filtered()")


# ==============================================================================
# ส่วนที่ 2: สร้างและใช้งานเซ็นเซอร์
# Part 2: Create and Use Sensors
# ==============================================================================
def demonstrate_sensor_creation():
    """
    สาธิตการสร้างและใช้งานเซ็นเซอร์ (Demonstrate sensor creation and usage)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 2: สร้างและใช้งานเซ็นเซอร์")
    print("Part 2: Create and Use Sensors")
    print("=" * 60)

    # สร้าง pH sensor
    print("\n--- สร้าง PHSensor ---")
    ph_sensor = PHSensor()

    # isinstance() ตรวจสอบว่า object เป็น instance ของ class หรือไม่
    print(f"\nph_sensor เป็น instance ของ PHSensor? {isinstance(ph_sensor, PHSensor)}")
    print(f"ph_sensor เป็น instance ของ BaseSensor? {isinstance(ph_sensor, BaseSensor)}")

    # สร้าง temperature sensor
    print("\n--- สร้าง TempSensor ---")
    temp_sensor = TempSensor()

    print(f"\ntemp_sensor เป็น instance ของ TempSensor? {isinstance(temp_sensor, TempSensor)}")
    print(f"temp_sensor เป็น instance ของ BaseSensor? {isinstance(temp_sensor, BaseSensor)}")

    return ph_sensor, temp_sensor


# ==============================================================================
# ส่วนที่ 3: สาธิต Properties ที่สืบทอด
# Part 3: Demonstrate Inherited Properties
# ==============================================================================
def demonstrate_inherited_properties(ph_sensor, temp_sensor):
    """
    สาธิต properties ที่สืบทอดจาก BaseSensor
    (Demonstrate properties inherited from BaseSensor)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 3: Properties ที่สืบทอดจาก BaseSensor")
    print("Part 3: Properties Inherited from BaseSensor")
    print("=" * 60)

    print("\n--- PHSensor Properties ---")
    print(f"  name: {ph_sensor.name}")
    print(f"  pin_number: {ph_sensor.pin_number}")
    print(f"  is_initialized: {ph_sensor.is_initialized}")
    print(f"  read_count: {ph_sensor.read_count}")

    print("\n--- PHSensor-specific Properties ---")
    print(f"  slope: {ph_sensor.slope}")
    print(f"  intercept: {ph_sensor.intercept}")
    print(f"  calibration_equation: {ph_sensor.calibration_equation}")

    print("\n--- TempSensor Properties ---")
    print(f"  name: {temp_sensor.name}")
    print(f"  pin_number: {temp_sensor.pin_number}")
    print(f"  is_initialized: {temp_sensor.is_initialized}")
    print(f"  read_count: {temp_sensor.read_count}")

    print("\n--- TempSensor-specific Properties ---")
    print(f"  is_available: {temp_sensor.is_available}")
    print(f"  sensor_count: {temp_sensor.sensor_count}")
    print(f"  default_temperature: {temp_sensor.default_temperature}")


# ==============================================================================
# ส่วนที่ 4: สาธิต Static Methods ที่สืบทอด
# Part 4: Demonstrate Inherited Static Methods
# ==============================================================================
def demonstrate_inherited_methods():
    """
    สาธิต static methods ที่สืบทอดจาก BaseSensor
    (Demonstrate static methods inherited from BaseSensor)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 4: Static Methods ที่สืบทอด")
    print("Part 4: Inherited Static Methods")
    print("=" * 60)

    print("\n--- เรียกจาก BaseSensor ---")
    print(f"BaseSensor.get_default_samples(): {BaseSensor.get_default_samples()}")
    print(f"BaseSensor.celsius_to_fahrenheit(25): {BaseSensor.celsius_to_fahrenheit(25):.1f} F")

    print("\n--- เรียกจาก PHSensor (สืบทอดมา) ---")
    print(f"PHSensor.get_default_samples(): {PHSensor.get_default_samples()}")
    print(f"PHSensor.celsius_to_fahrenheit(25): {PHSensor.celsius_to_fahrenheit(25):.1f} F")

    print("\n--- เรียกจาก TempSensor (สืบทอดมา) ---")
    print(f"TempSensor.get_default_samples(): {TempSensor.get_default_samples()}")
    print(f"TempSensor.celsius_to_fahrenheit(25): {TempSensor.celsius_to_fahrenheit(25):.1f} F")

    print("\n--- PHSensor-specific Static Methods ---")
    print(f"PHSensor.get_buffer_values(): {PHSensor.get_buffer_values()}")
    print(f"PHSensor.calculate_nernst_slope(25): {PHSensor.calculate_nernst_slope(25):.2f} mV/pH")

    print("\n--- TempSensor-specific Class Methods ---")
    print(f"TempSensor.get_conversion_delay(): {TempSensor.get_conversion_delay()} ms")


# ==============================================================================
# ส่วนที่ 5: สาธิต Method Overriding และการอ่านค่า
# Part 5: Demonstrate Method Overriding and Reading
# ==============================================================================
def demonstrate_method_overriding(ph_sensor, temp_sensor):
    """
    สาธิต method overriding: read() ทำงานต่างกันในแต่ละคลาส
    (Demonstrate method overriding: read() works differently in each class)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 5: Method Overriding - read()")
    print("Part 5: Method Overriding - read()")
    print("=" * 60)

    print("\n--- Method Overriding ---")
    print("BaseSensor.read() -> raise NotImplementedError")
    print("PHSensor.read() -> คืนค่า pH")
    print("TempSensor.read() -> คืนค่าอุณหภูมิ")

    # เริ่มต้นเซ็นเซอร์ (Initialize sensors)
    print("\n--- เริ่มต้นเซ็นเซอร์ ---")
    ph_initialized = ph_sensor.init()
    temp_initialized = temp_sensor.init()

    print(f"PHSensor initialized: {ph_initialized}")
    print(f"TempSensor initialized: {temp_initialized}")

    # อ่านค่า
    if ph_initialized:
        print("\n--- อ่านค่า pH ---")
        for i in range(3):
            voltage, ph = ph_sensor.read_with_voltage()
            print(f"  ครั้งที่ {i+1}: V={voltage:.4f}V, pH={ph:.2f}")
            sleep_ms(500)

    if temp_initialized and temp_sensor.is_available:
        print("\n--- อ่านค่าอุณหภูมิ ---")
        for i in range(2):
            temp_c = temp_sensor.read_celsius()
            temp_f = temp_sensor.read_fahrenheit()
            print(f"  ครั้งที่ {i+1}: {temp_c:.2f} C / {temp_f:.2f} F")

    # ใช้ methods ที่สืบทอด (Use inherited methods)
    if ph_initialized:
        print("\n--- ใช้ read_averaged() ที่สืบทอดจาก BaseSensor ---")
        avg_ph = ph_sensor.read_averaged(num_samples=5)
        print(f"  pH เฉลี่ย (5 samples): {avg_ph:.2f}")

        print("\n--- ใช้ read_filtered() ที่สืบทอดจาก BaseSensor ---")
        filtered_ph = ph_sensor.read_filtered(num_samples=7)
        print(f"  pH กรอง (7 samples): {filtered_ph:.2f}")


# ==============================================================================
# ส่วนที่ 6: Polymorphism - ใช้เซ็นเซอร์ต่างชนิดในลักษณะเดียวกัน
# Part 6: Polymorphism - Use Different Sensors in Same Way
# ==============================================================================
def demonstrate_polymorphism(ph_sensor, temp_sensor):
    """
    สาธิต Polymorphism: ใช้เซ็นเซอร์ต่างชนิดผ่าน interface เดียวกัน
    (Demonstrate Polymorphism: use different sensors through same interface)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 6: Polymorphism")
    print("Part 6: Polymorphism")
    print("=" * 60)

    print("\n--- Polymorphism คืออะไร? ---")
    print("Polymorphism คือการใช้งาน objects ต่างชนิดผ่าน interface เดียวกัน")
    print("เนื่องจาก PHSensor และ TempSensor สืบทอดจาก BaseSensor")
    print("เราสามารถเรียก read() ได้กับทั้งคู่โดยไม่ต้องรู้ว่าเป็นเซ็นเซอร์ชนิดไหน")

    # เก็บเซ็นเซอร์ในลิสต์เดียวกัน
    sensors = [ph_sensor, temp_sensor]

    print("\n--- วนลูปอ่านค่าจากทุกเซ็นเซอร์ ---")
    for sensor in sensors:
        print(f"\nSensor: {sensor.name}")
        print(f"  Type: {type(sensor).__name__}")
        print(f"  Pin: GPIO{sensor.pin_number}")

        if sensor.is_initialized:
            value = sensor.read()
            print(f"  Value: {value}")
            print(f"  Read count: {sensor.read_count}")

    print("\n--- ฟังก์ชันที่รับ BaseSensor ใดๆ ---")

    def read_sensor_info(sensor):
        """
        ฟังก์ชันที่รับ BaseSensor ใดๆ (Function accepting any BaseSensor)

        นี่คือประโยชน์ของ Polymorphism:
        - ฟังก์ชันเดียวใช้ได้กับ PHSensor, TempSensor, และเซ็นเซอร์อื่นๆ
        - ที่สืบทอดจาก BaseSensor
        """
        print(f"  Name: {sensor.name}")
        print(f"  Pin: GPIO{sensor.pin_number}")
        print(f"  Initialized: {sensor.is_initialized}")
        if sensor.is_initialized:
            print(f"  Last value: {sensor.last_value}")

    for sensor in sensors:
        print(f"\nข้อมูลของ {type(sensor).__name__}:")
        read_sensor_info(sensor)


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
def main():
    """โปรแกรมหลัก (Main program)"""
    print("=" * 60)
    print("สาธิต Inheritance กับเซ็นเซอร์")
    print("(Inheritance Demo with Sensors)")
    print("=" * 60)

    print("\nโครงสร้างการ Inherit:")
    print("                BaseSensor")
    print("               /          \\")
    print("          PHSensor      TempSensor")

    try:
        # ส่วนที่ 1: แสดงโครงสร้าง
        demonstrate_inheritance_structure()

        # ส่วนที่ 2: สร้างเซ็นเซอร์
        ph_sensor, temp_sensor = demonstrate_sensor_creation()

        # ส่วนที่ 3: Properties ที่สืบทอด
        demonstrate_inherited_properties(ph_sensor, temp_sensor)

        # ส่วนที่ 4: Static methods ที่สืบทอด
        demonstrate_inherited_methods()

        # ส่วนที่ 5: Method overriding
        demonstrate_method_overriding(ph_sensor, temp_sensor)

        # ส่วนที่ 6: Polymorphism
        demonstrate_polymorphism(ph_sensor, temp_sensor)

    except KeyboardInterrupt:
        print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

    except Exception as e:
        print(f"\nข้อผิดพลาด (Error): {e}")

    finally:
        print("\n" + "=" * 60)
        print("สรุป (Summary):")
        print("- Inheritance ช่วยให้ code reuse ได้")
        print("- super().__init__() เรียก constructor ของ parent")
        print("- Method Overriding ปรับแต่งการทำงานใน child class")
        print("- Polymorphism ใช้ objects ต่างชนิดผ่าน interface เดียวกัน")
        print("=" * 60)


# รันโปรแกรม
if __name__ == "__main__":
    main()

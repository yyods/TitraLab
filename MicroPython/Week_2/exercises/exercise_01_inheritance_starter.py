# ==============================================================================
# exercise_01_inheritance_starter.py - แบบฝึกหัด: Inheritance
# (Exercise: Inheritance - Starter Code)
# ==============================================================================
# เวลาโดยประมาณ: 15 นาที (Estimated time: 15 minutes)
#
# นิสิตจะได้ฝึกสร้างคลาสที่สืบทอดจาก BaseSensor
# Students will practice creating a class that inherits from BaseSensor
#
# โจทย์: สร้างคลาส TemperatureSensor ที่สืบทอดจาก BaseSensor
#
# ==============================================================================

from machine import Pin
from time import sleep_ms


class BaseSensor:
    """คลาสพื้นฐานสำหรับเซ็นเซอร์ (ห้ามแก้ไข)"""

    def __init__(self, name, pin):
        self._name = name
        self._pin_number = pin
        self._is_initialized = False
        self._read_count = 0
        print(f"[{name}] สร้างที่ GPIO{pin}")

    @property
    def name(self):
        return self._name

    @property
    def pin_number(self):
        return self._pin_number

    @property
    def is_initialized(self):
        return self._is_initialized

    @property
    def read_count(self):
        return self._read_count

    def read(self):
        """คลาสลูกต้อง override"""
        raise NotImplementedError("คลาสลูกต้อง implement read()")

    def log(self, message):
        print(f"[{self._name}] {message}")


# ==============================================================================
# แบบฝึกหัด: สร้างคลาส TemperatureSensor
# Exercise: Create TemperatureSensor class
# ==============================================================================

class TemperatureSensor(BaseSensor):
    """
    เซ็นเซอร์อุณหภูมิ DS18B20 สืบทอดจาก BaseSensor

    TODO: นิสิตต้องเติมโค้ดให้สมบูรณ์

    สิ่งที่ต้องทำ:
    1. เขียน __init__() พร้อมเรียก super().__init__()
    2. Override read() method
    3. เพิ่ม read_celsius() และ read_fahrenheit()
    4. เพิ่ม property สำหรับ default_temp
    """

    def __init__(self, pin=16, default_temp=25.0):
        """
        สร้าง TemperatureSensor

        TODO: เติมโค้ด
        1. เรียก super().__init__() พร้อม name และ pin
        2. กำหนด self._default_temp

        Args:
            pin (int): GPIO pin สำหรับ DS18B20 (ค่าเริ่มต้น: 16)
            default_temp (float): อุณหภูมิเริ่มต้น (ค่าเริ่มต้น: 25.0)
        """
        # TODO: เรียก parent constructor
        # super().__init__(???, ???)
        pass

        # TODO: กำหนดค่า default temperature
        # self._default_temp = ???
        pass

    @property
    def default_temp(self):
        """
        อุณหภูมิเริ่มต้น (Default temperature)

        TODO: เติม return statement
        """
        # TODO: return ค่า _default_temp
        pass

    def read(self):
        """
        Override read() - อ่านอุณหภูมิเป็นเซลเซียส

        TODO: เติมโค้ด
        1. จำลองค่าอุณหภูมิ (ใช้ default_temp + 0.5)
        2. เพิ่ม self._read_count
        3. return ค่าอุณหภูมิ

        Returns:
            float: อุณหภูมิเป็นเซลเซียส
        """
        # TODO: จำลองการอ่านค่า
        # temp = self._default_temp + 0.5
        pass

        # TODO: เพิ่ม read_count
        # self._read_count += 1
        pass

        # TODO: return ค่าอุณหภูมิ
        pass

    def read_celsius(self):
        """
        อ่านอุณหภูมิเป็นเซลเซียส (Alias for read)

        TODO: เรียก self.read() และ return ค่า
        """
        # TODO: return self.read()
        pass

    def read_fahrenheit(self):
        """
        อ่านอุณหภูมิเป็นฟาเรนไฮต์

        TODO: เติมโค้ด
        สูตร: F = C * 9/5 + 32

        Returns:
            float: อุณหภูมิเป็นฟาเรนไฮต์
        """
        # TODO: อ่านค่าเซลเซียส
        # celsius = self.read()
        pass

        # TODO: แปลงเป็นฟาเรนไฮต์และ return
        # return celsius * 9/5 + 32
        pass


# ==============================================================================
# ทดสอบโค้ด (ไม่ต้องแก้ไข)
# Test code (Do not modify)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ TemperatureSensor")
    print("Testing TemperatureSensor")
    print("=" * 50)

    try:
        # === Original test code ===
        # สร้าง sensor (Create sensor)
        temp_sensor = TemperatureSensor()

        # ทดสอบ properties (Test properties)
        print(f"\nname: {temp_sensor.name}")
        print(f"pin_number: {temp_sensor.pin_number}")
        print(f"default_temp: {temp_sensor.default_temp}")

        # ทดสอบ inheritance (Test inheritance)
        print(f"\nisinstance(temp_sensor, BaseSensor): {isinstance(temp_sensor, BaseSensor)}")
        print(f"issubclass(TemperatureSensor, BaseSensor): {issubclass(TemperatureSensor, BaseSensor)}")

        # ทดสอบ methods (Test methods)
        print("\n--- ทดสอบ read methods ---")
        for i in range(3):
            celsius = temp_sensor.read_celsius()
            fahrenheit = temp_sensor.read_fahrenheit()
            print(f"ครั้งที่ {i+1}: {celsius:.1f} C / {fahrenheit:.1f} F")
            sleep_ms(500)

        print(f"\nread_count: {temp_sensor.read_count}")

        # ทดสอบ log method (จาก BaseSensor)
        temp_sensor.log("ทดสอบ log method จาก BaseSensor")

        print("\n" + "=" * 50)
        print("ทดสอบเสร็จสิ้น!")
        print("=" * 50)

    except NotImplementedError as e:
        print("\n" + "=" * 50)
        print("*** โค้ดยังไม่สมบูรณ์ (Code incomplete) ***")
        print(f"*** ข้อผิดพลาด: {e} ***")
        print("*** กรุณาเติมโค้ดในส่วน TODO ***")
        print("*** Please complete the TODO sections ***")
        print("=" * 50)
    except TypeError as e:
        print(f"\n*** TypeError: {e} ***")
        print("*** ตรวจสอบประเภทข้อมูลที่ส่งให้ฟังก์ชัน ***")
        print("*** Check the data types passed to functions ***")
    except Exception as e:
        print(f"\n*** ข้อผิดพลาดอื่น (Other error): {e} ***")
        print("*** ตรวจสอบโค้ดของคุณอีกครั้ง ***")

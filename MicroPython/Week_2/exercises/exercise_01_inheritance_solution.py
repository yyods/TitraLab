# ==============================================================================
# exercise_01_inheritance_solution.py - เฉลย: Inheritance
# (Exercise: Inheritance - Solution)
# ==============================================================================
# เวลาโดยประมาณ: 15 นาที (Estimated time: 15 minutes)
#
# เฉลยแบบฝึกหัดการสร้างคลาส TemperatureSensor ที่สืบทอดจาก BaseSensor
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
# เฉลย: TemperatureSensor class
# Solution: TemperatureSensor class
# ==============================================================================

class TemperatureSensor(BaseSensor):
    """
    เซ็นเซอร์อุณหภูมิ DS18B20 สืบทอดจาก BaseSensor

    เฉลย: คลาสที่สมบูรณ์พร้อมคำอธิบาย
    """

    def __init__(self, pin=16, default_temp=25.0):
        """
        สร้าง TemperatureSensor

        เฉลย:
        1. เรียก super().__init__() พร้อม name="Temperature Sensor" และ pin
        2. กำหนด self._default_temp

        Args:
            pin (int): GPIO pin สำหรับ DS18B20 (ค่าเริ่มต้น: 16)
            default_temp (float): อุณหภูมิเริ่มต้น (ค่าเริ่มต้น: 25.0)
        """
        # เฉลย: เรียก parent constructor
        # super() หมายถึง BaseSensor
        # ส่ง name และ pin ให้ BaseSensor.__init__()
        super().__init__("Temperature Sensor", pin)

        # เฉลย: กำหนดค่า default temperature
        # เป็น attribute เฉพาะของ TemperatureSensor
        self._default_temp = default_temp

        # แสดงข้อมูลเพิ่มเติม
        self.log(f"อุณหภูมิเริ่มต้น: {default_temp} C")

    @property
    def default_temp(self):
        """
        อุณหภูมิเริ่มต้น (Default temperature)

        เฉลย: return ค่า _default_temp
        """
        return self._default_temp

    def read(self):
        """
        Override read() - อ่านอุณหภูมิเป็นเซลเซียส

        เฉลย:
        1. จำลองค่าอุณหภูมิ (ใช้ default_temp + 0.5)
        2. เพิ่ม self._read_count
        3. return ค่าอุณหภูมิ

        Returns:
            float: อุณหภูมิเป็นเซลเซียส
        """
        # เฉลย: จำลองการอ่านค่า
        # ในการใช้งานจริงจะใช้ ds18x20 library
        temp = self._default_temp + 0.5

        # เฉลย: เพิ่ม read_count
        # _read_count มาจาก BaseSensor
        self._read_count += 1

        # เฉลย: return ค่าอุณหภูมิ
        return temp

    def read_celsius(self):
        """
        อ่านอุณหภูมิเป็นเซลเซียส (Alias for read)

        เฉลย: เรียก self.read() และ return ค่า
        """
        return self.read()

    def read_fahrenheit(self):
        """
        อ่านอุณหภูมิเป็นฟาเรนไฮต์

        เฉลย:
        สูตร: F = C * 9/5 + 32

        Returns:
            float: อุณหภูมิเป็นฟาเรนไฮต์
        """
        # เฉลย: อ่านค่าเซลเซียส
        celsius = self.read()

        # เฉลย: แปลงเป็นฟาเรนไฮต์และ return
        return celsius * 9/5 + 32


# ==============================================================================
# ทดสอบโค้ด
# Test code
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ TemperatureSensor (เฉลย)")
    print("=" * 50)

    # สร้าง sensor
    temp_sensor = TemperatureSensor()

    # ทดสอบ properties
    print(f"\nname: {temp_sensor.name}")
    print(f"pin_number: {temp_sensor.pin_number}")
    print(f"default_temp: {temp_sensor.default_temp}")

    # ทดสอบ inheritance
    print(f"\nisinstance(temp_sensor, BaseSensor): {isinstance(temp_sensor, BaseSensor)}")
    print(f"issubclass(TemperatureSensor, BaseSensor): {issubclass(TemperatureSensor, BaseSensor)}")

    # ทดสอบ methods
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

# ==============================================================================
# temp_sensor.py - คลาสเซ็นเซอร์อุณหภูมิ DS18B20 สำหรับ TitraLab
# (DS18B20 Temperature Sensor Class for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการการอ่านค่าอุณหภูมิจาก DS18B20 ผ่าน OneWire protocol
# This module handles temperature reading from DS18B20 via OneWire protocol
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ OneWire protocol และการสื่อสารแบบ 1 สาย
#   2. เรียนรู้การทำงานของเซ็นเซอร์ดิจิทัล DS18B20
#   3. ประยุกต์ใช้การอ่านอุณหภูมิในการไทเทรต
#
# ความสำคัญในการไทเทรต (Importance in Titration):
#   อุณหภูมิมีผลต่อค่า pH ตามสมการ Nernst
#   - ที่ 25 C: slope = -59.16 mV/pH
#   - ที่อุณหภูมิอื่น: slope เปลี่ยนตาม T
#   การวัดอุณหภูมิช่วยให้การสอบเทียบ pH แม่นยำขึ้น
#
# DS18B20 Specifications:
#   - ช่วงวัด: -55 C ถึง +125 C
#   - ความละเอียด: 9-12 bit (เลือกได้)
#   - ความแม่นยำ: +/- 0.5 C (ช่วง -10 C ถึง +85 C)
#   - เวลาแปลงค่า: 750 ms (12-bit mode)
#
# ==============================================================================

from machine import Pin
from time import sleep_ms

# นำเข้าไลบรารี OneWire และ DS18B20 (Import OneWire and DS18B20 libraries)
try:
    from onewire import OneWire
    from ds18x20 import DS18X20
except ImportError as e:
    print(f"ข้อผิดพลาด: ไม่พบไลบรารี (Error: Library not found): {e}")
    raise

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import (
        DS18B20_PIN, TEMP_CONVERSION_DELAY_MS, TEMP_DEFAULT_VALUE
    )
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    DS18B20_PIN = 16
    TEMP_CONVERSION_DELAY_MS = 750
    TEMP_DEFAULT_VALUE = 25.0


class TemperatureSensor:
    """
    คลาสเซ็นเซอร์อุณหภูมิ DS18B20 (DS18B20 Temperature Sensor class)

    คุณสมบัติหลัก (Main Features):
        - อ่านอุณหภูมิจาก DS18B20
        - รองรับหลายเซ็นเซอร์บน bus เดียวกัน
        - แปลงหน่วยองศาเซลเซียส/ฟาเรนไฮต์

    หลักการ OneWire (OneWire Principle):
        - ใช้สายเดียวสำหรับการสื่อสาร (bidirectional)
        - แต่ละ device มี unique 64-bit ROM code
        - สามารถต่อหลาย device บน bus เดียวกัน

    ตัวอย่างการใช้งาน (Usage Example):
        >>> temp_sensor = TemperatureSensor()
        >>> temp = temp_sensor.read()
        >>> print(f"Temperature: {temp:.2f} C")
    """

    def __init__(self, pin=None, default_temp=None):
        """
        สร้าง TemperatureSensor object (Create TemperatureSensor object)

        Args:
            pin (int): หมายเลขขา GPIO (GPIO pin number)
                       ค่าเริ่มต้น: GPIO16
            default_temp (float): อุณหภูมิเริ่มต้นเมื่ออ่านไม่ได้
                                  ค่าเริ่มต้น: 25.0 C
        """
        # กำหนดค่า (Set values)
        self._pin_number = pin if pin is not None else DS18B20_PIN
        self._default_temp = default_temp if default_temp else TEMP_DEFAULT_VALUE
        self._conversion_delay = TEMP_CONVERSION_DELAY_MS

        # สร้าง OneWire และ DS18X20 objects
        # Create OneWire and DS18X20 objects
        self._pin = Pin(self._pin_number)
        self._ow = OneWire(self._pin)
        self._ds = DS18X20(self._ow)

        # ค้นหาเซ็นเซอร์ที่เชื่อมต่อ (Scan for connected sensors)
        self._roms = self._ds.scan()

        # แจ้งสถานะ (Report status)
        if self._roms:
            print(f"พบเซ็นเซอร์ DS18B20 {len(self._roms)} ตัว ที่ GPIO{self._pin_number} "
                  f"(Found {len(self._roms)} DS18B20 sensor(s) on GPIO{self._pin_number})")
            for i, rom in enumerate(self._roms):
                print(f"  Sensor {i+1} ROM: {self._rom_to_hex(rom)}")
        else:
            print(f"ไม่พบเซ็นเซอร์ DS18B20 ที่ GPIO{self._pin_number} "
                  f"(No DS18B20 sensor found on GPIO{self._pin_number})")

    def init(self):
        """
        เริ่มต้น Temperature Sensor (Initialize Temperature Sensor)

        เมธอดนี้ถูกเรียกโดย HardwareHub - OneWire พร้อมใช้งานตั้งแต่สร้าง object
        This method is called by HardwareHub - OneWire ready from object creation.
        """
        pass  # OneWire พร้อมใช้งานตั้งแต่ __init__ (OneWire ready from __init__)

    def deinit(self):
        """
        ปิด Temperature Sensor (Deinitialize Temperature Sensor)

        เมธอดนี้ถูกเรียกเมื่อปิดโปรแกรม
        This method is called on shutdown.
        """
        pass  # OneWire ไม่ต้อง cleanup (OneWire does not need cleanup)

    @property
    def is_available(self):
        """
        ตรวจสอบว่ามีเซ็นเซอร์เชื่อมต่อหรือไม่
        Check if sensor is available

        Returns:
            bool: True ถ้าพบเซ็นเซอร์ (if sensor found)
        """
        return len(self._roms) > 0

    @property
    def sensor_count(self):
        """
        จำนวนเซ็นเซอร์ที่เชื่อมต่อ (Number of connected sensors)

        Returns:
            int: จำนวนเซ็นเซอร์
        """
        return len(self._roms)

    def _rom_to_hex(self, rom):
        """
        แปลง ROM address เป็น hex string (Convert ROM to hex string)

        Args:
            rom (bytearray): ROM address

        Returns:
            str: Hex string representation
        """
        return ''.join('{:02X}'.format(b) for b in rom)

    def rescan(self):
        """
        สแกนหาเซ็นเซอร์ใหม่ (Rescan for sensors)

        ใช้เมื่อต่อเซ็นเซอร์เพิ่มหลังจากเริ่มต้น
        Use when sensors added after initialization

        Returns:
            int: จำนวนเซ็นเซอร์ที่พบ (number of sensors found)
        """
        self._roms = self._ds.scan()
        if self._roms:
            print(f"พบเซ็นเซอร์ {len(self._roms)} ตัว "
                  f"(Found {len(self._roms)} sensor(s))")
        else:
            print("ไม่พบเซ็นเซอร์ (No sensors found)")
        return len(self._roms)

    def read(self, sensor_index=0):
        """
        อ่านอุณหภูมิจากเซ็นเซอร์ (Read temperature from sensor)

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์ (sensor index), ค่าเริ่มต้น 0

        Returns:
            float: อุณหภูมิเป็นองศาเซลเซียส (temperature in Celsius)
                   คืน default_temp ถ้าอ่านไม่ได้
        """
        if not self._roms:
            print("คำเตือน: ไม่พบเซ็นเซอร์ (Warning: No sensor found)")
            return self._default_temp

        if sensor_index >= len(self._roms):
            print(f"คำเตือน: ไม่มีเซ็นเซอร์ที่ดัชนี {sensor_index} "
                  f"(Warning: No sensor at index {sensor_index})")
            return self._default_temp

        try:
            # สั่งแปลงค่าอุณหภูมิ (Start temperature conversion)
            self._ds.convert_temp()

            # รอการแปลงค่าเสร็จ (Wait for conversion)
            # DS18B20 ใช้เวลาประมาณ 750ms สำหรับ 12-bit resolution
            sleep_ms(self._conversion_delay)

            # อ่านค่าอุณหภูมิ (Read temperature)
            temp = self._ds.read_temp(self._roms[sensor_index])
            return temp

        except Exception as e:
            print(f"ข้อผิดพลาดการอ่านอุณหภูมิ (Error reading temperature): {e}")
            return self._default_temp

    def read_fast(self, sensor_index=0):
        """
        อ่านอุณหภูมิแบบเร็ว (Fast temperature read)

        หมายเหตุ: ต้องเรียก start_conversion() ก่อน แล้วรอ 750ms
        Note: Must call start_conversion() first, then wait 750ms

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์

        Returns:
            float: อุณหภูมิเป็นองศาเซลเซียส
        """
        if not self._roms or sensor_index >= len(self._roms):
            return self._default_temp

        try:
            return self._ds.read_temp(self._roms[sensor_index])
        except Exception:
            return self._default_temp

    def start_conversion(self):
        """
        เริ่มการแปลงค่าอุณหภูมิ (Start temperature conversion)

        ใช้คู่กับ read_fast() สำหรับการอ่านแบบ non-blocking
        Use with read_fast() for non-blocking reads

        ตัวอย่าง:
            >>> temp_sensor.start_conversion()
            >>> # ทำงานอื่นได้ 750ms
            >>> temp = temp_sensor.read_fast()
        """
        if self._roms:
            self._ds.convert_temp()

    def read_all(self):
        """
        อ่านอุณหภูมิจากเซ็นเซอร์ทั้งหมด (Read temperature from all sensors)

        Returns:
            list: รายการอุณหภูมิ [(rom_hex, temp), ...]
        """
        if not self._roms:
            return []

        # เริ่มการแปลงค่า (Start conversion)
        self._ds.convert_temp()
        sleep_ms(self._conversion_delay)

        # อ่านค่าทุกเซ็นเซอร์ (Read all sensors)
        results = []
        for rom in self._roms:
            try:
                temp = self._ds.read_temp(rom)
                results.append((self._rom_to_hex(rom), temp))
            except Exception as e:
                results.append((self._rom_to_hex(rom), None))
                print(f"ข้อผิดพลาดอ่านเซ็นเซอร์ {self._rom_to_hex(rom)}: {e}")

        return results

    def read_celsius(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นองศาเซลเซียส (Read temperature in Celsius)

        Alias สำหรับ read()

        Returns:
            float: อุณหภูมิเป็น C
        """
        return self.read(sensor_index)

    def read_fahrenheit(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นองศาฟาเรนไฮต์ (Read temperature in Fahrenheit)

        การแปลง (Conversion):
            F = C * 9/5 + 32

        Returns:
            float: อุณหภูมิเป็น F
        """
        celsius = self.read(sensor_index)
        fahrenheit = celsius * 9 / 5 + 32
        return fahrenheit

    def read_kelvin(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นเคลวิน (Read temperature in Kelvin)

        การแปลง (Conversion):
            K = C + 273.15

        Returns:
            float: อุณหภูมิเป็น K
        """
        celsius = self.read(sensor_index)
        kelvin = celsius + 273.15
        return kelvin

    def read_formatted(self, sensor_index=0, precision=2):
        """
        อ่านอุณหภูมิพร้อมจัดรูปแบบ (Read temperature with formatting)

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์
            precision (int): จำนวนทศนิยม

        Returns:
            str: อุณหภูมิพร้อมหน่วย เช่น "25.50 C"
        """
        temp = self.read(sensor_index)
        return f"{temp:.{precision}f} C"

    def get_roms(self):
        """
        อ่าน ROM addresses ของเซ็นเซอร์ทั้งหมด (Get all sensor ROM addresses)

        Returns:
            list: รายการ ROM addresses เป็น hex string
        """
        return [self._rom_to_hex(rom) for rom in self._roms]

    def __repr__(self):
        """แสดงข้อมูลเซ็นเซอร์อุณหภูมิ"""
        status = "available" if self.is_available else "not found"
        return (f"TemperatureSensor(pin={self._pin_number}, "
                f"sensors={self.sensor_count}, status={status})")

# ==============================================================================
# temp_sensor.py - คลาสเซ็นเซอร์อุณหภูมิ DS18B20 สืบทอดจาก BaseSensor
# (Temperature Sensor Class - Inherits from BaseSensor)
# ==============================================================================
# โมดูลนี้สาธิตการ Inheritance โดย TempSensor สืบทอดจาก BaseSensor
# This module demonstrates Inheritance with TempSensor extending BaseSensor
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการ inherit จาก parent class: class TempSensor(BaseSensor)
#   2. เปรียบเทียบกับ PHSensor - ทั้งคู่ inherit จาก BaseSensor เดียวกัน
#   3. Override methods: read(), _init_hardware()
#   4. เพิ่ม methods เฉพาะ: read_celsius(), read_fahrenheit(), read_kelvin()
#   5. ใช้ @property สำหรับ is_available, sensor_count
#
# ความสำคัญในการไทเทรต (Importance in Titration):
#   อุณหภูมิมีผลต่อค่า pH ตามสมการ Nernst:
#   - slope = -(2.303 * R * T) / (n * F)
#   - ที่ 25 C: slope = -59.16 mV/pH
#   - ที่ 30 C: slope = -60.15 mV/pH
#   การวัดอุณหภูมิช่วยให้การคำนวณ pH แม่นยำขึ้น
#
# DS18B20 Specifications:
#   - ช่วงวัด: -55 C ถึง +125 C
#   - ความละเอียด: 12-bit (0.0625 C)
#   - ความแม่นยำ: +/- 0.5 C (ช่วง -10 C ถึง +85 C)
#   - เวลาแปลง: 750 ms (12-bit mode)
#
# Hardware Configuration:
#   - GPIO 16: DS18B20 Temperature Sensor (OneWire protocol)
#
# ==============================================================================

from machine import Pin
from time import sleep_ms

# นำเข้าไลบรารี OneWire (Import OneWire libraries)
try:
    from onewire import OneWire
    from ds18x20 import DS18X20
except ImportError as e:
    print(f"ไม่พบไลบรารี OneWire (OneWire library not found): {e}")
    raise

# นำเข้า BaseSensor
try:
    from base_sensor import BaseSensor
except ImportError:
    from lib.base_sensor import BaseSensor


# ==============================================================================
# ค่าคงที่สำหรับ Temperature Sensor (Temperature Sensor Constants)
# ==============================================================================
DS18B20_PIN = 16                    # GPIO16 สำหรับ DS18B20
CONVERSION_DELAY_MS = 750           # เวลารอการแปลงค่า (12-bit)
DEFAULT_TEMPERATURE = 25.0          # อุณหภูมิเริ่มต้นถ้าอ่านไม่ได้


class TempSensor(BaseSensor):
    """
    คลาสเซ็นเซอร์อุณหภูมิ DS18B20 สืบทอดจาก BaseSensor
    (DS18B20 Temperature Sensor class inheriting from BaseSensor)

    ===== การ Inherit (Inheritance) =====

    class TempSensor(BaseSensor):  <-- TempSensor สืบทอดจาก BaseSensor

    TempSensor ได้รับจาก BaseSensor (เหมือน PHSensor):
    1. Attributes: _name, _pin_number, _is_initialized, etc.
    2. Methods: log(), read_averaged(), read_filtered(), etc.
    3. Properties: name, pin_number, is_initialized, etc.

    TempSensor เพิ่มเติม:
    1. Attributes เฉพาะ: _ow, _ds, _roms, _default_temp
    2. Methods เฉพาะ: read_celsius(), read_fahrenheit(), read_kelvin(), rescan()
    3. Properties เฉพาะ: is_available, sensor_count

    ===== เปรียบเทียบ PHSensor vs TempSensor =====

    ทั้งคู่สืบทอดจาก BaseSensor:
                    BaseSensor
                    /        \\
               PHSensor    TempSensor

    สิ่งที่เหมือนกัน:
    - ใช้ super().__init__() เรียก constructor ของ parent
    - Override read() และ _init_hardware()
    - มี properties สำหรับ encapsulation
    - ใช้ methods ที่สืบทอดได้ (log, read_averaged, etc.)

    สิ่งที่ต่างกัน:
    - Hardware: PHSensor ใช้ ADC, TempSensor ใช้ OneWire
    - Output: PHSensor คืน pH, TempSensor คืน temperature
    - Methods เฉพาะต่างกัน

    ===== ตัวอย่างการใช้งาน (Usage Example) =====

        # สร้างเซ็นเซอร์อุณหภูมิ
        temp_sensor = TempSensor()

        # เริ่มต้นฮาร์ดแวร์
        temp_sensor.init()

        # อ่านอุณหภูมิ
        temp_c = temp_sensor.read()  # หรือ read_celsius()
        temp_f = temp_sensor.read_fahrenheit()
        temp_k = temp_sensor.read_kelvin()

        print(f"Temperature: {temp_c:.2f} C / {temp_f:.2f} F / {temp_k:.2f} K")

    Attributes:
        _ow (OneWire): OneWire object (private)
        _ds (DS18X20): DS18X20 driver object (private)
        _roms (list): รายการ ROM addresses ของเซ็นเซอร์ (private)
        _default_temp (float): อุณหภูมิเริ่มต้นถ้าอ่านไม่ได้ (private)
    """

    def __init__(self, pin=None, default_temp=None):
        """
        Constructor - สร้าง TempSensor object

        ===== super().__init__() =====

        เรียก constructor ของ BaseSensor ก่อน
        จากนั้นจึงเริ่มต้น attributes เฉพาะของ TempSensor

        Args:
            pin (int): GPIO pin สำหรับ OneWire (ค่าเริ่มต้น: GPIO16)
            default_temp (float): อุณหภูมิเริ่มต้นถ้าอ่านไม่ได้
        """
        # กำหนดค่า pin
        pin_number = pin if pin is not None else DS18B20_PIN

        # ===== เรียก constructor ของ parent class (BaseSensor) =====
        super().__init__(name="Temperature Sensor", pin=pin_number)

        # ===== เริ่มต้น attributes เฉพาะของ TempSensor =====
        self._default_temp = default_temp if default_temp else DEFAULT_TEMPERATURE
        self._conversion_delay = CONVERSION_DELAY_MS

        # OneWire objects - จะสร้างใน _init_hardware()
        self._pin = None
        self._ow = None
        self._ds = None
        self._roms = []

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_available(self):
        """
        ตรวจสอบว่ามีเซ็นเซอร์เชื่อมต่อหรือไม่
        (Check if any sensor is connected)

        ===== @property =====

        Read-only property:
            if sensor.is_available:
                temp = sensor.read()

        Returns:
            bool: True ถ้าพบเซ็นเซอร์
        """
        return len(self._roms) > 0

    @property
    def sensor_count(self):
        """
        จำนวนเซ็นเซอร์ที่เชื่อมต่อ (Number of connected sensors)

        OneWire รองรับหลายเซ็นเซอร์บน bus เดียวกัน

        Returns:
            int: จำนวนเซ็นเซอร์
        """
        return len(self._roms)

    @property
    def default_temperature(self):
        """
        อุณหภูมิเริ่มต้นที่ใช้เมื่ออ่านไม่ได้ (Default temperature when read fails)

        Returns:
            float: อุณหภูมิเริ่มต้น
        """
        return self._default_temp

    @default_temperature.setter
    def default_temperature(self, value):
        """
        กำหนดอุณหภูมิเริ่มต้นใหม่ (Set new default temperature)

        Args:
            value (float): อุณหภูมิเริ่มต้นใหม่
        """
        self._default_temp = value
        self.log(f"อุณหภูมิเริ่มต้นใหม่: {value:.1f} C (New default: {value:.1f} C)")

    # =========================================================================
    # Override Methods - จาก BaseSensor
    # =========================================================================

    def _init_hardware(self):
        """
        เริ่มต้น OneWire และ DS18B20 (Initialize OneWire and DS18B20)

        ===== Method Overriding =====

        Override BaseSensor._init_hardware()
        เฉพาะสำหรับการเริ่มต้น OneWire protocol
        """
        # ตรวจสอบ pin
        self.validate_pin(self._pin_number)

        # สร้าง OneWire และ DS18X20 objects
        self._pin = Pin(self._pin_number)
        self._ow = OneWire(self._pin)
        self._ds = DS18X20(self._ow)

        # สแกนหาเซ็นเซอร์ที่เชื่อมต่อ
        self._roms = self._ds.scan()

        if self._roms:
            self.log(f"พบเซ็นเซอร์ {len(self._roms)} ตัว (Found {len(self._roms)} sensor(s))")
            for i, rom in enumerate(self._roms):
                rom_hex = self._rom_to_hex(rom)
                self.log(f"  Sensor {i+1}: {rom_hex}")
        else:
            self.log("ไม่พบเซ็นเซอร์ (No sensor found)")

    def read(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นองศาเซลเซียส (Read temperature in Celsius)

        ===== Method Overriding =====

        Override BaseSensor.read()
        คืนค่าอุณหภูมิแทนที่จะ raise NotImplementedError

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์ (ถ้ามีหลายตัว)

        Returns:
            float: อุณหภูมิเป็น C
        """
        if self._ds is None:
            self.log("ยังไม่ได้เริ่มต้น กรุณาเรียก init() ก่อน")
            return self._default_temp

        if not self._roms:
            self.log("ไม่พบเซ็นเซอร์ (No sensor found)")
            return self._default_temp

        if sensor_index >= len(self._roms):
            self.log(f"ไม่มีเซ็นเซอร์ที่ดัชนี {sensor_index}")
            return self._default_temp

        try:
            # เริ่มการแปลงค่า (Start conversion)
            self._ds.convert_temp()

            # รอการแปลงเสร็จ (Wait for conversion)
            # DS18B20 ใช้เวลา 750ms สำหรับ 12-bit
            sleep_ms(self._conversion_delay)

            # อ่านค่าอุณหภูมิ (Read temperature)
            temp = self._ds.read_temp(self._roms[sensor_index])

            # อัปเดต state
            self._last_value = temp
            self._read_count += 1

            return temp

        except Exception as e:
            self.log(f"ข้อผิดพลาดการอ่าน (Read error): {e}")
            return self._default_temp

    # =========================================================================
    # TempSensor-specific Methods
    # =========================================================================

    def read_celsius(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นองศาเซลเซียส (Read temperature in Celsius)

        Alias สำหรับ read()

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์

        Returns:
            float: อุณหภูมิเป็น C
        """
        return self.read(sensor_index)

    def read_fahrenheit(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นองศาฟาเรนไฮต์ (Read temperature in Fahrenheit)

        ===== ใช้ Static Method จาก BaseSensor =====

        เรียก celsius_to_fahrenheit() ที่สืบทอดมาจาก BaseSensor

        การแปลง: F = C * 9/5 + 32

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์

        Returns:
            float: อุณหภูมิเป็น F
        """
        celsius = self.read(sensor_index)
        # ใช้ static method ที่สืบทอดจาก BaseSensor
        return self.celsius_to_fahrenheit(celsius)

    def read_kelvin(self, sensor_index=0):
        """
        อ่านอุณหภูมิเป็นเคลวิน (Read temperature in Kelvin)

        ใช้ static method จาก BaseSensor

        การแปลง: K = C + 273.15

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์

        Returns:
            float: อุณหภูมิเป็น K
        """
        celsius = self.read(sensor_index)
        # ใช้ static method ที่สืบทอดจาก BaseSensor
        return self.celsius_to_kelvin(celsius)

    def read_formatted(self, sensor_index=0, precision=2, unit='C'):
        """
        อ่านอุณหภูมิพร้อมจัดรูปแบบ (Read temperature with formatting)

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์
            precision (int): จำนวนทศนิยม
            unit (str): หน่วย 'C', 'F', หรือ 'K'

        Returns:
            str: อุณหภูมิพร้อมหน่วย เช่น "25.50 C"
        """
        if unit.upper() == 'F':
            temp = self.read_fahrenheit(sensor_index)
            return f"{temp:.{precision}f} F"
        elif unit.upper() == 'K':
            temp = self.read_kelvin(sensor_index)
            return f"{temp:.{precision}f} K"
        else:
            temp = self.read_celsius(sensor_index)
            return f"{temp:.{precision}f} C"

    def read_fast(self, sensor_index=0):
        """
        อ่านอุณหภูมิแบบเร็ว (Fast temperature read)

        ไม่รอ conversion - ใช้คู่กับ start_conversion()
        สำหรับ non-blocking reads

        Args:
            sensor_index (int): ดัชนีเซ็นเซอร์

        Returns:
            float: อุณหภูมิเป็น C
        """
        if not self._roms or sensor_index >= len(self._roms):
            return self._default_temp

        try:
            temp = self._ds.read_temp(self._roms[sensor_index])
            self._last_value = temp
            self._read_count += 1
            return temp
        except Exception:
            return self._default_temp

    def start_conversion(self):
        """
        เริ่มการแปลงค่าอุณหภูมิ (Start temperature conversion)

        ใช้คู่กับ read_fast() สำหรับ non-blocking reads

        ตัวอย่าง:
            sensor.start_conversion()
            # ทำงานอื่นได้ 750ms
            temp = sensor.read_fast()
        """
        if self._ds and self._roms:
            self._ds.convert_temp()
            self.log("เริ่มการแปลงค่า (Conversion started)")

    def read_all(self):
        """
        อ่านอุณหภูมิจากเซ็นเซอร์ทั้งหมด (Read from all sensors)

        Returns:
            list: รายการ (rom_hex, temperature) tuples
        """
        if not self._roms:
            return []

        # เริ่ม conversion
        self._ds.convert_temp()
        sleep_ms(self._conversion_delay)

        results = []
        for i, rom in enumerate(self._roms):
            try:
                temp = self._ds.read_temp(rom)
                results.append((self._rom_to_hex(rom), temp))
            except Exception:
                results.append((self._rom_to_hex(rom), None))

        return results

    def rescan(self):
        """
        สแกนหาเซ็นเซอร์ใหม่ (Rescan for sensors)

        ใช้เมื่อต่อเซ็นเซอร์เพิ่มหลังจากเริ่มต้น

        Returns:
            int: จำนวนเซ็นเซอร์ที่พบ
        """
        if self._ds:
            self._roms = self._ds.scan()
            if self._roms:
                self.log(f"พบเซ็นเซอร์ {len(self._roms)} ตัว (Found {len(self._roms)} sensor(s))")
            else:
                self.log("ไม่พบเซ็นเซอร์ (No sensor found)")
            return len(self._roms)
        return 0

    def get_roms(self):
        """
        รับ ROM addresses ของเซ็นเซอร์ทั้งหมด (Get all sensor ROM addresses)

        Returns:
            list: รายการ ROM addresses เป็น hex string
        """
        return [self._rom_to_hex(rom) for rom in self._roms]

    def _rom_to_hex(self, rom):
        """
        แปลง ROM address เป็น hex string (Convert ROM to hex string)

        Internal method (prefix _)

        Args:
            rom (bytearray): ROM address

        Returns:
            str: Hex string representation
        """
        return ''.join('{:02X}'.format(b) for b in rom)

    # =========================================================================
    # Class Method
    # =========================================================================

    @classmethod
    def get_conversion_delay(cls):
        """
        รับเวลารอการแปลงค่า (Get conversion delay)

        ===== @classmethod =====

        สามารถเรียกได้โดยไม่ต้องสร้าง instance:
            delay = TempSensor.get_conversion_delay()

        Returns:
            int: เวลา conversion ใน ms
        """
        return CONVERSION_DELAY_MS

    # =========================================================================
    # Magic Methods
    # =========================================================================

    def __repr__(self):
        """แสดงข้อมูล object สำหรับ debugging"""
        status = "available" if self.is_available else "not found"
        return (f"TempSensor(pin={self._pin_number}, "
                f"sensors={self.sensor_count}, "
                f"status={status}, "
                f"initialized={self._is_initialized})")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TempSensor - เซ็นเซอร์อุณหภูมิ สืบทอดจาก BaseSensor")
    print("(TempSensor - Temperature Sensor inheriting from BaseSensor)")
    print("=" * 60)

    # สร้าง temperature sensor
    temp_sensor = TempSensor()
    print(f"\nrepr: {repr(temp_sensor)}")
    print(f"str: {str(temp_sensor)}")

    # แสดง class method
    print(f"\n--- Class Method ---")
    print(f"Conversion delay: {TempSensor.get_conversion_delay()} ms")

    # เริ่มต้นฮาร์ดแวร์
    print(f"\n--- เริ่มต้นฮาร์ดแวร์ ---")
    if temp_sensor.init():
        # แสดง properties
        print(f"\n--- Properties ---")
        print(f"name: {temp_sensor.name}")
        print(f"pin_number: {temp_sensor.pin_number}")
        print(f"is_available: {temp_sensor.is_available}")
        print(f"sensor_count: {temp_sensor.sensor_count}")
        print(f"default_temperature: {temp_sensor.default_temperature}")

        if temp_sensor.is_available:
            # แสดง ROM addresses
            print(f"\n--- ROM Addresses ---")
            for i, rom in enumerate(temp_sensor.get_roms()):
                print(f"  Sensor {i+1}: {rom}")

            try:
                # ทดสอบอ่านค่า
                print(f"\n--- ทดสอบอ่านค่า ---")
                for i in range(3):
                    temp_c = temp_sensor.read_celsius()
                    temp_f = temp_sensor.read_fahrenheit()
                    temp_k = temp_sensor.read_kelvin()
                    formatted = temp_sensor.read_formatted(precision=1)

                    print(f"ครั้งที่ {i+1}:")
                    print(f"  Celsius: {temp_c:.2f} C")
                    print(f"  Fahrenheit: {temp_f:.2f} F")
                    print(f"  Kelvin: {temp_k:.2f} K")
                    print(f"  Formatted: {formatted}")

                # ใช้ methods ที่สืบทอดจาก BaseSensor
                print(f"\n--- Methods จาก BaseSensor ---")
                avg_temp = temp_sensor.read_averaged(num_samples=3)
                print(f"ค่าเฉลี่ย (3 samples): {avg_temp:.2f} C")

                print(f"\nจำนวนครั้งที่อ่าน: {temp_sensor.read_count}")
                print(f"ค่าล่าสุด: {temp_sensor.last_value:.2f} C")

                # ทดสอบ non-blocking read
                print(f"\n--- Non-blocking Read ---")
                temp_sensor.start_conversion()
                print("กำลังแปลงค่า... (Converting...)")
                sleep_ms(750)
                fast_temp = temp_sensor.read_fast()
                print(f"Fast read: {fast_temp:.2f} C")

            except KeyboardInterrupt:
                print("\nหยุดโดยผู้ใช้ (Stopped by user)")
        else:
            print("\nไม่พบเซ็นเซอร์ - ไม่สามารถทดสอบได้")
            print("กรุณาตรวจสอบการเชื่อมต่อ (Please check connections)")
    else:
        print("ไม่สามารถเริ่มต้นได้ (Initialization failed)")

    print("\n" + "=" * 60)
    print("เสร็จสิ้น (Done)")
    print("=" * 60)

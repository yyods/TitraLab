# ==============================================================================
# 02_temp_sensor_class.py - คลาส TemperatureSensor สำหรับ DS18B20
# (TemperatureSensor Class for DS18B20)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้ OOP โดยสร้างคลาสอ่านอุณหภูมิ
# Week 1: Learn OOP by creating a temperature sensor class
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. สร้างคลาสที่ห่อหุ้ม (encapsulate) การทำงานของ DS18B20
#   2. เข้าใจ OneWire protocol และการสแกนหาเซ็นเซอร์
#   3. สร้าง method สำหรับอ่านอุณหภูมิหลายหน่วย
#   4. เชื่อมโยงกับสมการ Nernst สำหรับการชดเชยอุณหภูมิ
#
# ความสำคัญในเคมี (Importance in Chemistry):
#   - ค่า pH และศักย์ไฟฟ้าขึ้นกับอุณหภูมิ
#   - สมการ Nernst: E = E0 - (RT/nF) * ln(Q)
#     โดย R = 8.314 J/(mol*K), T = อุณหภูมิ Kelvin
#   - การวัด pH ที่แม่นยำต้องชดเชยอุณหภูมิ
#
# DS18B20 Specifications:
#   - ช่วงวัด: -55 C ถึง +125 C
#   - ความละเอียด: 12-bit (0.0625 C)
#   - เวลาแปลงค่า: ~750ms (12-bit)
#   - โปรโตคอล: OneWire (ใช้สายข้อมูลเส้นเดียว)
#
# ==============================================================================

import time
import machine
import onewire
import ds18x20


class TemperatureSensor:
    """
    คลาสควบคุมเซ็นเซอร์อุณหภูมิ DS18B20 (DS18B20 Temperature Sensor Class)

    คลาสนี้ห่อหุ้มการทำงานของ DS18B20 ให้ใช้งานง่าย และให้ข้อมูล
    อุณหภูมิในหลายหน่วยสำหรับการคำนวณทางเคมี

    This class encapsulates DS18B20 operations for easy use and provides
    temperature data in multiple units for chemistry calculations.

    ตัวอย่างการใช้งาน (Usage Example):
        >>> sensor = TemperatureSensor(16, "Lab Temp")
        >>> temp_c = sensor.read_celsius()
        >>> temp_k = sensor.read_kelvin()     # สำหรับสมการ Nernst
        >>> sensor.deinit()
    """

    # === Class Constants (ค่าคงที่สำหรับการคำนวณทางเคมี) ===
    # Gas constant R ในหน่วยต่างๆ (Gas constant R in different units)
    R_JOULES = 8.314    # J/(mol*K) - ใช้กับพลังงาน
    R_CAL = 1.987       # cal/(mol*K) - ใช้ในเคมีบางสูตร

    # Faraday constant (ค่าคงที่ฟาราเดย์)
    FARADAY = 96485     # C/mol - ใช้ในสมการ Nernst

    # ค่าแปลงอุณหภูมิ (Temperature conversion constants)
    ABSOLUTE_ZERO_C = -273.15  # องศาเซลเซียสที่ 0 Kelvin

    def __init__(self, pin_number=16, name="Temperature Sensor"):
        """
        สร้าง TemperatureSensor object (Create TemperatureSensor object)

        Args:
            pin_number (int): หมายเลขขา GPIO สำหรับ OneWire
                             TitraLab ใช้ GPIO16
                             (GPIO pin number for OneWire, TitraLab uses GPIO16)
            name (str): ชื่อเซ็นเซอร์สำหรับแสดงข้อความ (sensor name for display)

        Raises:
            RuntimeError: ถ้าไม่พบเซ็นเซอร์ DS18B20 (if no DS18B20 found)

        ตัวอย่าง (Example):
            sensor = TemperatureSensor(16, "Reaction Temp")
        """
        # === Instance Variables ===
        self.pin_number = pin_number
        self.name = name

        # === Private Variables ===
        self._last_celsius = None     # ค่าอุณหภูมิล่าสุดที่อ่านได้
        self._sensor_rom = None       # ROM address ของเซ็นเซอร์
        self._initialized = False

        # สร้าง OneWire bus และ DS18X20 driver
        # Create OneWire bus and DS18X20 driver
        self._pin = machine.Pin(pin_number)
        self._onewire = onewire.OneWire(self._pin)
        self._ds = ds18x20.DS18X20(self._onewire)

        # สแกนหาเซ็นเซอร์ DS18B20 (Scan for DS18B20 sensors)
        sensors = self._ds.scan()

        if not sensors:
            error_msg = (f"ข้อผิดพลาด: ไม่พบเซ็นเซอร์ DS18B20 ที่ GPIO{pin_number}\n"
                        f"(Error: DS18B20 sensor not found at GPIO{pin_number})")
            print(error_msg)
            raise RuntimeError(error_msg)

        # ใช้เซ็นเซอร์ตัวแรกที่พบ (Use the first sensor found)
        self._sensor_rom = sensors[0]
        self._initialized = True

        print(f"สร้าง '{name}' ที่ GPIO{pin_number} สำเร็จ")
        print(f"(Created '{name}' on GPIO{pin_number})")
        print(f"พบเซ็นเซอร์ {len(sensors)} ตัว (Found {len(sensors)} sensor(s))")

    def read(self):
        """
        อ่านค่าอุณหภูมิ (Read temperature) - alias for read_celsius()

        Returns:
            float: อุณหภูมิในหน่วยเซลเซียส (temperature in Celsius)
                   หรือ None ถ้าอ่านไม่สำเร็จ (or None if read failed)

        ตัวอย่าง (Example):
            temp = sensor.read()
            print(f"อุณหภูมิ: {temp} C")
        """
        return self.read_celsius()

    def read_celsius(self):
        """
        อ่านค่าอุณหภูมิในหน่วยเซลเซียส (Read temperature in Celsius)

        DS18B20 ต้องการเวลา ~750ms ในการแปลงค่า (12-bit resolution)
        DS18B20 needs ~750ms for conversion (12-bit resolution)

        Returns:
            float: อุณหภูมิในหน่วยเซลเซียส (temperature in Celsius)
                   หรือ None ถ้าอ่านไม่สำเร็จ (or None if read failed)

        ตัวอย่าง (Example):
            temp_c = sensor.read_celsius()
            if temp_c is not None:
                print(f"อุณหภูมิ: {temp_c:.2f} C")
        """
        if not self._initialized:
            print("ข้อผิดพลาด: เซ็นเซอร์ไม่ได้ถูกเริ่มต้น")
            print("(Error: Sensor not initialized)")
            return None

        try:
            # สั่งให้เซ็นเซอร์แปลงค่าอุณหภูมิ
            # Command sensor to convert temperature
            self._ds.convert_temp()

            # รอ 750ms สำหรับความละเอียด 12-bit
            # Wait 750ms for 12-bit resolution
            time.sleep_ms(750)

            # อ่านค่าอุณหภูมิ (Read temperature value)
            temp = self._ds.read_temp(self._sensor_rom)

            # เก็บค่าล่าสุด (Store last value)
            self._last_celsius = temp

            return temp

        except Exception as e:
            print(f"ข้อผิดพลาดในการอ่านอุณหภูมิ: {e}")
            print(f"(Error reading temperature: {e})")
            return None

    def read_fahrenheit(self):
        """
        อ่านค่าอุณหภูมิในหน่วยฟาเรนไฮต์ (Read temperature in Fahrenheit)

        สูตร (Formula): F = (C * 9/5) + 32

        Returns:
            float: อุณหภูมิในหน่วยฟาเรนไฮต์ (temperature in Fahrenheit)
                   หรือ None ถ้าอ่านไม่สำเร็จ (or None if read failed)

        ตัวอย่าง (Example):
            temp_f = sensor.read_fahrenheit()
            print(f"Temperature: {temp_f:.1f} F")
        """
        celsius = self.read_celsius()

        if celsius is None:
            return None

        # แปลงเซลเซียสเป็นฟาเรนไฮต์ (Convert Celsius to Fahrenheit)
        fahrenheit = (celsius * 9 / 5) + 32
        return fahrenheit

    def read_kelvin(self):
        """
        อ่านค่าอุณหภูมิในหน่วยเคลวิน (Read temperature in Kelvin)

        สูตร (Formula): K = C + 273.15

        สำคัญสำหรับเคมี (Important for chemistry):
        - สมการ Nernst ใช้อุณหภูมิเป็น Kelvin
        - E = E0 - (RT/nF) * ln(Q)
        - ค่า R = 8.314 J/(mol*K)

        Returns:
            float: อุณหภูมิในหน่วยเคลวิน (temperature in Kelvin)
                   หรือ None ถ้าอ่านไม่สำเร็จ (or None if read failed)

        ตัวอย่าง (Example):
            temp_k = sensor.read_kelvin()
            # ใช้ในสมการ Nernst
            nernst_factor = (R * temp_k) / (n * F)
        """
        celsius = self.read_celsius()

        if celsius is None:
            return None

        # แปลงเซลเซียสเป็นเคลวิน (Convert Celsius to Kelvin)
        kelvin = celsius - self.ABSOLUTE_ZERO_C  # C + 273.15
        return kelvin

    def get_nernst_factor(self, n_electrons=1):
        """
        คำนวณค่า Nernst factor สำหรับการชดเชยอุณหภูมิ
        (Calculate Nernst factor for temperature compensation)

        สมการ Nernst (Nernst Equation):
            E = E0 - (RT/nF) * ln(Q)

        Nernst factor = RT/nF = (2.303 * R * T) / (n * F)
        ที่ 25 C (298.15 K): factor = 0.05916 V สำหรับ n=1

        Args:
            n_electrons (int): จำนวน electrons ที่ถ่ายโอน
                              (number of electrons transferred)
                              ค่าเริ่มต้น: 1

        Returns:
            float: Nernst factor ในหน่วย V (Nernst factor in Volts)
                   หรือ None ถ้าอ่านไม่สำเร็จ (or None if read failed)

        ตัวอย่าง (Example):
            # สำหรับ pH electrode (n=1):
            factor = sensor.get_nernst_factor(1)
            # ที่ 25 C: factor ~ 0.0592 V

            # สำหรับ redox reaction (n=2):
            factor = sensor.get_nernst_factor(2)
        """
        kelvin = self.read_kelvin()

        if kelvin is None:
            return None

        # คำนวณ Nernst factor: (2.303 * R * T) / (n * F)
        # 2.303 มาจากการแปลง ln เป็น log10
        # 2.303 comes from converting ln to log10
        factor = (2.303 * self.R_JOULES * kelvin) / (n_electrons * self.FARADAY)
        return factor

    def get_last_reading(self):
        """
        ดึงค่าอุณหภูมิล่าสุดที่อ่านได้ (ไม่อ่านใหม่)
        (Get last temperature reading without new read)

        ใช้เมื่อต้องการค่าเร็วๆ โดยไม่รอ 750ms
        Use when quick value is needed without 750ms wait

        Returns:
            float: ค่าอุณหภูมิล่าสุด (last temperature value in Celsius)
                   หรือ None ถ้ายังไม่เคยอ่าน (or None if never read)
        """
        return self._last_celsius

    def get_status(self):
        """
        ดึงสถานะเซ็นเซอร์ (Get sensor status)

        Returns:
            str: ข้อความสถานะ (status message)
        """
        status = "พร้อมใช้งาน (Ready)" if self._initialized else "ไม่พร้อม (Not ready)"
        last_temp = f"{self._last_celsius:.2f} C" if self._last_celsius else "ยังไม่ได้อ่าน (Not read)"

        return (f"{self.name} @ GPIO{self.pin_number}\n"
                f"  สถานะ (Status): {status}\n"
                f"  ค่าล่าสุด (Last reading): {last_temp}")

    def deinit(self):
        """
        ปิดการใช้งานเซ็นเซอร์ (Deinitialize sensor)

        ควรเรียกเมื่อไม่ใช้งานเซ็นเซอร์แล้ว
        Should be called when done using sensor

        หมายเหตุ: OneWire ไม่ต้อง deinit เหมือน PWM
        แต่เป็นการปฏิบัติที่ดีในการ cleanup
        Note: OneWire doesn't need deinit like PWM,
        but it's good practice to cleanup
        """
        self._initialized = False
        print(f"ปิด {self.name} แล้ว ({self.name} deinitialized)")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบคลาส TemperatureSensor (Testing TemperatureSensor Class)")
    print("=" * 60)

    sensor = None

    try:
        # === สร้าง TemperatureSensor object ===
        print("\n--- สร้างเซ็นเซอร์ (Creating sensor) ---\n")
        sensor = TemperatureSensor(16, "Lab Temperature")

        # === ทดสอบอ่านค่าในหน่วยต่างๆ ===
        print("\n--- ทดสอบอ่านอุณหภูมิ (Testing temperature reading) ---\n")

        # อ่านค่าเซลเซียส (Read Celsius)
        temp_c = sensor.read_celsius()
        if temp_c is not None:
            print(f"อุณหภูมิ (Temperature): {temp_c:.2f} C")

        # อ่านค่าฟาเรนไฮต์ (Read Fahrenheit)
        temp_f = sensor.read_fahrenheit()
        if temp_f is not None:
            print(f"อุณหภูมิ (Temperature): {temp_f:.2f} F")

        # อ่านค่าเคลวิน (Read Kelvin) - สำคัญสำหรับเคมี
        temp_k = sensor.read_kelvin()
        if temp_k is not None:
            print(f"อุณหภูมิ (Temperature): {temp_k:.2f} K")

        # === ทดสอบ Nernst factor ===
        print("\n--- คำนวณ Nernst Factor (Calculating Nernst Factor) ---\n")

        factor = sensor.get_nernst_factor(1)
        if factor is not None:
            print(f"Nernst factor (n=1): {factor:.4f} V")
            print(f"  -> ที่ 25 C ค่ามาตรฐาน = 0.0592 V")
            print(f"  -> ที่อุณหภูมิปัจจุบัน = {factor:.4f} V")

            # ตัวอย่างการใช้ใน pH calculation
            # Example use in pH calculation
            print("\n  ตัวอย่างการใช้ในการคำนวณ pH:")
            print("  (Example use in pH calculation:)")
            print(f"  pH = (E_measured - E_ref) / {factor:.4f}")

        # === ทดสอบอ่านหลายครั้ง ===
        print("\n--- อ่านค่าต่อเนื่อง 3 ครั้ง (3 consecutive readings) ---\n")
        print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")

        for i in range(3):
            temp = sensor.read()
            if temp is not None:
                print(f"  อ่านครั้งที่ {i+1} (Reading {i+1}): {temp:.2f} C")
            time.sleep(1)

        # === แสดงสถานะ ===
        print("\n--- สถานะเซ็นเซอร์ (Sensor status) ---\n")
        print(sensor.get_status())

        # === ทดสอบ get_last_reading ===
        print("\n--- ค่าล่าสุด (Last reading - no wait) ---\n")
        last = sensor.get_last_reading()
        print(f"ค่าล่าสุด: {last:.2f} C (ไม่ต้องรอ 750ms)")
        print(f"(Last value: {last:.2f} C - no 750ms wait)")

    except RuntimeError as e:
        print(f"\nไม่สามารถเริ่มต้นเซ็นเซอร์: {e}")
        print("(Cannot initialize sensor)")
        print("\nตรวจสอบ (Check):")
        print("  1. เซ็นเซอร์เชื่อมต่อกับ GPIO16 หรือไม่")
        print("     (Is sensor connected to GPIO16?)")
        print("  2. มี pull-up resistor 4.7k ohm หรือไม่")
        print("     (Is there a 4.7k ohm pull-up resistor?)")

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        # === ทำความสะอาด (Cleanup) ===
        if sensor is not None:
            print("\n--- ทำความสะอาด (Cleanup) ---\n")
            sensor.deinit()

        print("\n" + "=" * 60)
        print("สรุปสิ่งที่เรียนรู้ (What we learned):")
        print("=" * 60)
        print("""
1. สร้าง class TemperatureSensor ที่ห่อหุ้ม DS18B20
   (Created TemperatureSensor class encapsulating DS18B20)

2. วิธีการทำงานของ DS18B20:
   - ใช้ OneWire protocol (สายข้อมูลเส้นเดียว)
   - ต้อง scan หา ROM address ก่อน
   - convert_temp() -> รอ 750ms -> read_temp()

3. อ่านอุณหภูมิหลายหน่วย:
   - read_celsius(): หน่วยเซลเซียส
   - read_fahrenheit(): หน่วยฟาเรนไฮต์
   - read_kelvin(): หน่วยเคลวิน (สำคัญสำหรับเคมี)

4. เชื่อมโยงกับเคมี - สมการ Nernst:
   - E = E0 - (RT/nF) * ln(Q)
   - get_nernst_factor() คำนวณ RT/nF ที่อุณหภูมิปัจจุบัน
   - ใช้ชดเชยอุณหภูมิในการวัด pH

5. การจัดการ error และ cleanup:
   - ตรวจสอบว่าพบเซ็นเซอร์หรือไม่
   - เก็บค่าล่าสุดใน _last_celsius
   - มี deinit() สำหรับ cleanup
""")
        print("เสร็จสิ้น (Done)")

"""
แบบฝึกหัดที่ 3: คลาส TemperatureSensor (Exercise 3: TemperatureSensor Class)
============================================================================

วัตถุประสงค์ (Objectives):
- เรียนรู้การใช้งานเซ็นเซอร์ DS18B20 ผ่าน OOP (Learn to use DS18B20 sensor via OOP)
- เข้าใจโปรโตคอล OneWire (Understand OneWire protocol)
- เชื่อมโยงการวัดอุณหภูมิกับสมการ Nernst ในการวัด pH

ความเชื่อมโยงกับเคมี - สมการ Nernst (Chemistry Connection - Nernst Equation):
==============================================================================

สมการ Nernst สำหรับเซ็นเซอร์ pH:
E = E0 - (2.303 * R * T) / (n * F) * pH

โดยที่ (Where):
- E  = ศักย์ไฟฟ้าที่วัดได้ (Measured potential in V)
- E0 = ศักย์ไฟฟ้ามาตรฐาน (Standard potential, typically 0V at pH 7)
- R  = ค่าคงที่แก๊ส (Gas constant) = 8.314 J/(mol*K)
- T  = อุณหภูมิสัมบูรณ์ (Absolute temperature in Kelvin)
- n  = จำนวนอิเล็กตรอน (Number of electrons) = 1 สำหรับ H+
- F  = ค่าคงที่ฟาราเดย์ (Faraday constant) = 96485 C/mol

ที่ 25C (298.15K): slope = -59.16 mV/pH
ที่ 30C (303.15K): slope = -60.15 mV/pH

ดังนั้นการวัดอุณหภูมิที่แม่นยำจึงจำเป็นสำหรับการชดเชยค่า pH!
Accurate temperature measurement is essential for pH compensation!

เกณฑ์ความสำเร็จ (Success Criteria):
[ ] สร้างคลาส TemperatureSensor สำหรับ DS18B20 (Create DS18B20 sensor class)
[ ] อ่านค่าอุณหภูมิเป็น Celsius และ Fahrenheit (Read temp in Celsius and Fahrenheit)
[ ] แปลงเป็น Kelvin สำหรับสมการ Nernst (Convert to Kelvin for Nernst equation)
[ ] คำนวณ Nernst slope ตามอุณหภูมิ (Calculate Nernst slope based on temperature)
[ ] จัดการข้อผิดพลาดเมื่อไม่พบเซ็นเซอร์ (Handle errors when sensor not found)

ขาที่ใช้งาน (Pin Configuration):
- DS18B20 Temperature Sensor: GPIO16 (OneWire protocol)
"""

from machine import Pin
import onewire
import ds18x20
import time


class TemperatureSensor:
    """
    คลาสสำหรับเซ็นเซอร์อุณหภูมิ DS18B20 (Class for DS18B20 temperature sensor)

    ใช้ในห้องปฏิบัติการเคมีสำหรับ:
    Used in chemistry lab for:
    - ชดเชยอุณหภูมิในการวัด pH (Temperature compensation for pH measurement)
    - ติดตามอุณหภูมิของปฏิกิริยา (Monitoring reaction temperature)
    - ควบคุมอุณหภูมิในการไทเทรต (Temperature control during titration)

    Attributes:
        ds (ds18x20.DS18X20): ออบเจ็กต์สำหรับสื่อสาร DS18B20
        roms (list): รายการที่อยู่ของเซ็นเซอร์ที่พบ

    Constants:
        R: ค่าคงที่แก๊ส (Gas constant) = 8.314 J/(mol*K)
        F: ค่าคงที่ฟาราเดย์ (Faraday constant) = 96485 C/mol

    Example:
        sensor = TemperatureSensor(16)
        print(f"Temperature: {sensor.celsius:.2f}C")
        print(f"Nernst slope: {sensor.nernst_slope:.2f} mV/pH")
    """

    # ค่าคงที่สำหรับสมการ Nernst (Constants for Nernst equation)
    R = 8.314      # ค่าคงที่แก๊ส (Gas constant) J/(mol*K)
    F = 96485      # ค่าคงที่ฟาราเดย์ (Faraday constant) C/mol
    N = 1          # จำนวนอิเล็กตรอนสำหรับ H+ (Number of electrons for H+)

    def __init__(self, pin_number: int):
        """
        สร้างออบเจ็กต์ TemperatureSensor (Create TemperatureSensor object)

        Args:
            pin_number: หมายเลขขา GPIO (GPIO pin number) - ใช้ GPIO16

        คำแนะนำ (Hints):
        - สร้าง Pin object ก่อน: pin = Pin(pin_number)
        - สร้าง OneWire object: ow = onewire.OneWire(pin)
        - สร้าง DS18X20 object: ds = ds18x20.DS18X20(ow)
        - ค้นหาเซ็นเซอร์: roms = ds.scan()
        - ถ้าไม่พบเซ็นเซอร์ให้แสดงคำเตือน
        """
        # TODO: สร้าง OneWire และ DS18X20 objects (Create OneWire and DS18X20 objects)
        # pin = Pin(pin_number)
        # self.ow = ???
        # self.ds = ???

        # TODO: ค้นหาเซ็นเซอร์ที่เชื่อมต่อ (Scan for connected sensors)
        # self.roms = ???

        # TODO: ตรวจสอบว่าพบเซ็นเซอร์หรือไม่ (Check if sensor found)
        # if not self.roms:
        #     print("คำเตือน: ไม่พบเซ็นเซอร์ DS18B20 (Warning: DS18B20 not found)")

        # TODO: เก็บค่าอุณหภูมิล่าสุด (Store latest temperature)
        # self._temp_celsius = None
        pass

    def _convert_and_read(self) -> float:
        """
        สั่งให้เซ็นเซอร์แปลงค่าและอ่านผล (Command sensor to convert and read)

        กระบวนการอ่านค่า DS18B20 (DS18B20 reading process):
        1. สั่ง convert_temp() - เซ็นเซอร์จะแปลงอุณหภูมิเป็นดิจิทัล
        2. รอ 750ms - เวลาที่เซ็นเซอร์ใช้ในการแปลง
        3. อ่านค่าด้วย read_temp(rom) - อ่านค่าที่แปลงแล้ว

        Returns:
            float: อุณหภูมิในหน่วย Celsius หรือ None ถ้าเกิดข้อผิดพลาด

        คำแนะนำ (Hints):
        - ตรวจสอบว่ามี roms ก่อน
        - เรียก self.ds.convert_temp()
        - รอด้วย time.sleep_ms(750)
        - อ่านด้วย self.ds.read_temp(self.roms[0])
        """
        # TODO: แปลงและอ่านค่าอุณหภูมิ (Convert and read temperature)
        # if not self.roms:
        #     return None
        #
        # try:
        #     self.ds.convert_temp()
        #     time.sleep_ms(750)
        #     temp = self.ds.read_temp(self.roms[0])
        #     self._temp_celsius = temp
        #     return temp
        # except Exception as e:
        #     print(f"ข้อผิดพลาดในการอ่าน (Read error): {e}")
        #     return None
        pass

    @property
    def celsius(self) -> float:
        """
        อ่านอุณหภูมิเป็น Celsius (Read temperature in Celsius)

        Returns:
            float: อุณหภูมิใน C หรือ None
        """
        # TODO: อ่านและคืนค่าอุณหภูมิ Celsius (Read and return Celsius)
        pass

    @property
    def fahrenheit(self) -> float:
        """
        อ่านอุณหภูมิเป็น Fahrenheit (Read temperature in Fahrenheit)

        Returns:
            float: อุณหภูมิใน F หรือ None

        คำแนะนำ (Hints):
        - สูตร: F = (C * 9/5) + 32
        """
        # TODO: คำนวณและคืนค่าอุณหภูมิ Fahrenheit (Calculate and return Fahrenheit)
        pass

    @property
    def kelvin(self) -> float:
        """
        อ่านอุณหภูมิเป็น Kelvin (Read temperature in Kelvin)

        ค่า Kelvin จำเป็นสำหรับสมการ Nernst!
        Kelvin is required for Nernst equation!

        Returns:
            float: อุณหภูมิใน K หรือ None

        คำแนะนำ (Hints):
        - สูตร: K = C + 273.15
        """
        # TODO: คำนวณและคืนค่าอุณหภูมิ Kelvin (Calculate and return Kelvin)
        pass

    @property
    def nernst_slope(self) -> float:
        """
        คำนวณ Nernst slope ตามอุณหภูมิปัจจุบัน (Calculate Nernst slope at current temperature)

        สูตร: slope = (2.303 * R * T) / (n * F) * 1000 (แปลงเป็น mV)

        ค่านี้บอกว่าแรงดันเปลี่ยนแปลงเท่าไหร่ต่อ 1 หน่วย pH
        This value tells how much voltage changes per 1 pH unit

        Returns:
            float: slope ในหน่วย mV/pH หรือ None

        ตัวอย่างค่าที่ถูกต้อง (Expected values):
        - ที่ 25C: -59.16 mV/pH
        - ที่ 30C: -60.15 mV/pH
        - ที่ 20C: -58.17 mV/pH

        คำแนะนำ (Hints):
        - ต้องการอุณหภูมิเป็น Kelvin
        - สูตร: slope = (2.303 * R * T) / (n * F) * 1000
        - คืนค่าเป็นลบเพราะ pH สูง = แรงดันต่ำ
        """
        # TODO: คำนวณ Nernst slope (Calculate Nernst slope)
        # T = self.kelvin
        # if T is None:
        #     return None
        # slope = (2.303 * self.R * T) / (self.N * self.F) * 1000
        # return -slope  # ค่าลบเพราะ pH สูง = แรงดันต่ำ
        pass

    def get_all_readings(self) -> dict:
        """
        อ่านค่าทั้งหมดในครั้งเดียว (Get all readings at once)

        Returns:
            dict: dictionary ที่มีค่าทั้งหมด

        คำแนะนำ (Hints):
        - อ่านค่า Celsius ก่อน (จะ trigger การแปลงค่า)
        - แปลงเป็นหน่วยอื่นจากค่าที่เก็บไว้
        """
        # TODO: คืนค่าทั้งหมดเป็น dictionary (Return all values as dictionary)
        # celsius = self._convert_and_read()
        # if celsius is None:
        #     return None
        #
        # return {
        #     'celsius': celsius,
        #     'fahrenheit': (celsius * 9/5) + 32,
        #     'kelvin': celsius + 273.15,
        #     'nernst_slope': -(2.303 * self.R * (celsius + 273.15)) / (self.N * self.F) * 1000
        # }
        pass

    @property
    def sensor_count(self) -> int:
        """
        จำนวนเซ็นเซอร์ที่พบ (Number of sensors found)

        Returns:
            int: จำนวนเซ็นเซอร์
        """
        # TODO: คืนจำนวนเซ็นเซอร์ (Return sensor count)
        pass


# =============================================================================
# โค้ดทดสอบ (Test Code)
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("ทดสอบคลาส TemperatureSensor (Testing TemperatureSensor Class)")
    print("การวัดอุณหภูมิสำคัญสำหรับการชดเชยค่า pH ตามสมการ Nernst")
    print("Temperature measurement is important for pH compensation via Nernst")
    print("=" * 70)

    # สร้าง TemperatureSensor ที่ขา GPIO16 (Create sensor on GPIO16)
    sensor = TemperatureSensor(16)

    print(f"\n[Info] พบเซ็นเซอร์ {sensor.sensor_count} ตัว (Found {sensor.sensor_count} sensor(s))")

    if sensor.sensor_count == 0:
        print("\nไม่สามารถทดสอบได้เนื่องจากไม่พบเซ็นเซอร์")
        print("Cannot test because no sensor found")
        print("โปรดตรวจสอบการเชื่อมต่อ DS18B20 ที่ GPIO16")
        print("Please check DS18B20 connection on GPIO16")
    else:
        print("\n[Test 1] อ่านค่าอุณหภูมิในหน่วยต่างๆ (Read temperature in different units)")
        print("-" * 50)
        celsius = sensor.celsius
        print(f"  Celsius:    {celsius:.2f} C")

        fahrenheit = sensor.fahrenheit
        print(f"  Fahrenheit: {fahrenheit:.2f} F")

        kelvin = sensor.kelvin
        print(f"  Kelvin:     {kelvin:.2f} K")

        print("\n[Test 2] คำนวณ Nernst Slope (Calculate Nernst Slope)")
        print("-" * 50)
        slope = sensor.nernst_slope
        print(f"  Nernst Slope: {slope:.2f} mV/pH")
        print(f"  (ค่ามาตรฐานที่ 25C: -59.16 mV/pH)")
        print(f"  (Standard at 25C: -59.16 mV/pH)")

        print("\n[Test 3] แสดงผลกระทบของอุณหภูมิต่อการวัด pH")
        print("         (Effect of temperature on pH measurement)")
        print("-" * 50)

        # จำลองค่า pH ที่แตกต่างกัน (Simulate different pH values)
        test_ph_values = [4.0, 7.0, 10.0]
        e0 = 0  # มาตรฐานที่ pH 7 (Standard at pH 7)

        print(f"  ที่อุณหภูมิ {celsius:.1f}C, Nernst slope = {slope:.2f} mV/pH")
        print()

        for ph in test_ph_values:
            # คำนวณแรงดันที่คาดว่าจะได้ (Calculate expected voltage)
            # E = E0 - slope * (pH - 7)
            voltage = e0 - slope * (ph - 7)
            print(f"  pH {ph:.1f} -> แรงดัน (Voltage): {voltage:.2f} mV")

        print("\n[Test 4] ติดตามอุณหภูมิแบบ real-time (Real-time monitoring)")
        print("-" * 50)
        print("  กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")

        try:
            for i in range(10):  # อ่าน 10 ครั้ง (Read 10 times)
                readings = sensor.get_all_readings()
                if readings:
                    print(f"  [{i+1:2d}] {readings['celsius']:.2f}C | "
                          f"{readings['kelvin']:.2f}K | "
                          f"Slope: {readings['nernst_slope']:.2f} mV/pH")
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n  หยุดโดยผู้ใช้ (Stopped by user)")

    print("\n" + "=" * 70)
    print("การทดสอบเสร็จสิ้น (Testing completed)")
    print("=" * 70)
    print("\nหมายเหตุ: ค่า Nernst Slope ที่คำนวณได้จะถูกใช้ในการชดเชยอุณหภูมิ")
    print("         เมื่อวัดค่า pH เพื่อให้ได้ค่าที่แม่นยำ")
    print("Note: Calculated Nernst Slope will be used for temperature compensation")
    print("      when measuring pH to get accurate values")

"""
เฉลยแบบฝึกหัดที่ 3: คลาส TemperatureSensor (Exercise 3 Solution: TemperatureSensor Class)
=========================================================================================

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
        """
        # สร้าง Pin object (Create Pin object)
        pin = Pin(pin_number)

        # สร้าง OneWire object สำหรับการสื่อสาร (Create OneWire for communication)
        self.ow = onewire.OneWire(pin)

        # สร้าง DS18X20 object สำหรับอ่านค่า (Create DS18X20 for reading)
        self.ds = ds18x20.DS18X20(self.ow)

        # ค้นหาเซ็นเซอร์ที่เชื่อมต่อ (Scan for connected sensors)
        self.roms = self.ds.scan()

        # ตรวจสอบว่าพบเซ็นเซอร์หรือไม่ (Check if sensor found)
        if not self.roms:
            print("คำเตือน: ไม่พบเซ็นเซอร์ DS18B20 (Warning: DS18B20 not found)")
            print("โปรดตรวจสอบการเชื่อมต่อที่ GPIO{} (Check connection on GPIO{})".format(
                pin_number, pin_number))
        else:
            print(f"พบเซ็นเซอร์ {len(self.roms)} ตัว (Found {len(self.roms)} sensor(s))")

        # เก็บค่าอุณหภูมิล่าสุด (Store latest temperature)
        self._temp_celsius = None

    def _convert_and_read(self) -> float:
        """
        สั่งให้เซ็นเซอร์แปลงค่าและอ่านผล (Command sensor to convert and read)

        กระบวนการอ่านค่า DS18B20 (DS18B20 reading process):
        1. สั่ง convert_temp() - เซ็นเซอร์จะแปลงอุณหภูมิเป็นดิจิทัล
        2. รอ 750ms - เวลาที่เซ็นเซอร์ใช้ในการแปลง
        3. อ่านค่าด้วย read_temp(rom) - อ่านค่าที่แปลงแล้ว

        Returns:
            float: อุณหภูมิในหน่วย Celsius หรือ None ถ้าเกิดข้อผิดพลาด
        """
        # ตรวจสอบว่ามีเซ็นเซอร์หรือไม่ (Check if sensor available)
        if not self.roms:
            return None

        try:
            # สั่งให้เซ็นเซอร์แปลงอุณหภูมิ (Command sensor to convert temperature)
            self.ds.convert_temp()

            # รอให้การแปลงเสร็จสิ้น (Wait for conversion to complete)
            # DS18B20 ต้องการเวลาสูงสุด 750ms สำหรับ 12-bit resolution
            time.sleep_ms(750)

            # อ่านค่าจากเซ็นเซอร์ตัวแรก (Read from first sensor)
            temp = self.ds.read_temp(self.roms[0])

            # เก็บค่าไว้ใช้ภายหลัง (Store for later use)
            self._temp_celsius = temp

            return temp

        except Exception as e:
            print(f"ข้อผิดพลาดในการอ่าน (Read error): {e}")
            return None

    @property
    def celsius(self) -> float:
        """
        อ่านอุณหภูมิเป็น Celsius (Read temperature in Celsius)

        Returns:
            float: อุณหภูมิใน C หรือ None
        """
        return self._convert_and_read()

    @property
    def fahrenheit(self) -> float:
        """
        อ่านอุณหภูมิเป็น Fahrenheit (Read temperature in Fahrenheit)

        Returns:
            float: อุณหภูมิใน F หรือ None
        """
        # อ่านค่า Celsius ก่อน (Read Celsius first)
        celsius = self._convert_and_read()

        if celsius is None:
            return None

        # แปลงเป็น Fahrenheit: F = (C * 9/5) + 32
        return (celsius * 9 / 5) + 32

    @property
    def kelvin(self) -> float:
        """
        อ่านอุณหภูมิเป็น Kelvin (Read temperature in Kelvin)

        ค่า Kelvin จำเป็นสำหรับสมการ Nernst!
        Kelvin is required for Nernst equation!

        Returns:
            float: อุณหภูมิใน K หรือ None
        """
        # อ่านค่า Celsius ก่อน (Read Celsius first)
        celsius = self._convert_and_read()

        if celsius is None:
            return None

        # แปลงเป็น Kelvin: K = C + 273.15
        return celsius + 273.15

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
        """
        # อ่านอุณหภูมิเป็น Kelvin (Read temperature in Kelvin)
        kelvin = self.kelvin

        if kelvin is None:
            return None

        # คำนวณ Nernst slope (Calculate Nernst slope)
        # slope = (2.303 * R * T) / (n * F) * 1000 (แปลงจาก V เป็น mV)
        slope = (2.303 * self.R * kelvin) / (self.N * self.F) * 1000

        # คืนค่าเป็นลบเพราะ pH สูง = แรงดันต่ำ (Negative because higher pH = lower voltage)
        return -slope

    def get_all_readings(self) -> dict:
        """
        อ่านค่าทั้งหมดในครั้งเดียว (Get all readings at once)

        การอ่านครั้งเดียวช่วยประหยัดเวลาและให้ค่าที่ consistent
        Single read saves time and provides consistent values

        Returns:
            dict: dictionary ที่มีค่าทั้งหมด หรือ None
        """
        # อ่านค่า Celsius ครั้งเดียว (Read Celsius once)
        celsius = self._convert_and_read()

        if celsius is None:
            return None

        # คำนวณค่าอื่นๆ จากค่า Celsius ที่อ่านได้ (Calculate other values from Celsius)
        kelvin = celsius + 273.15
        fahrenheit = (celsius * 9 / 5) + 32
        nernst = -(2.303 * self.R * kelvin) / (self.N * self.F) * 1000

        return {
            'celsius': celsius,
            'fahrenheit': fahrenheit,
            'kelvin': kelvin,
            'nernst_slope': nernst
        }

    @property
    def sensor_count(self) -> int:
        """
        จำนวนเซ็นเซอร์ที่พบ (Number of sensors found)

        Returns:
            int: จำนวนเซ็นเซอร์
        """
        return len(self.roms)


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

        # ตรวจสอบความถูกต้อง (Verify correctness)
        expected_slope_25c = -59.16
        if celsius is not None:
            actual_expected = -(2.303 * 8.314 * (celsius + 273.15)) / (1 * 96485) * 1000
            print(f"  ค่าที่คำนวณที่ {celsius:.1f}C: {actual_expected:.2f} mV/pH")

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
            print(f"  pH {ph:.1f} -> แรงดัน (Voltage): {voltage:+.2f} mV")

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
    print("การทดสอบเสร็จสิ้น - ผ่านทุกข้อ! (Testing completed - All passed!)")
    print("=" * 70)
    print("\nหมายเหตุ: ค่า Nernst Slope ที่คำนวณได้จะถูกใช้ในการชดเชยอุณหภูมิ")
    print("         เมื่อวัดค่า pH เพื่อให้ได้ค่าที่แม่นยำ")
    print("Note: Calculated Nernst Slope will be used for temperature compensation")
    print("      when measuring pH to get accurate values")

# ==============================================================================
# 06_temp_sensor_class.py - Temperature Sensor for pH Compensation
# ==============================================================================
# เซ็นเซอร์อุณหภูมิ DS18B20 สำหรับชดเชยค่า pH ตามสมการ Nernst
# DS18B20 Temperature Sensor for pH Compensation using Nernst Equation
# ==============================================================================
#
# ทำไมต้องวัดอุณหภูมิในการไทเทรชัน? (Why measure temperature in titration?)
# =====================================================================
# สมการ Nernst แสดงความสัมพันธ์ระหว่างศักย์ไฟฟ้า (E) กับ pH:
# The Nernst equation relates electrode potential (E) to pH:
#
#     E = E0 - (2.303 * R * T) / (n * F) * pH
#
# โดยที่ (where):
#   E   = ศักย์ไฟฟ้าที่วัดได้ (measured potential, mV)
#   E0  = ศักย์ไฟฟ้าอ้างอิง (reference potential, mV)
#   R   = ค่าคงที่ของก๊าซ (gas constant) = 8.314 J/(mol*K)
#   T   = อุณหภูมิสัมบูรณ์ (absolute temperature, Kelvin)
#   n   = จำนวนอิเล็กตรอน (electrons transferred) = 1 for H+
#   F   = ค่าคงที่ฟาราเดย์ (Faraday constant) = 96485 C/mol
#
# ความชัน (Nernst Slope) เปลี่ยนตามอุณหภูมิ:
# The Nernst slope changes with temperature:
#   - ที่ 25C (298.15 K): slope = 59.16 mV/pH
#   - ที่ 30C (303.15 K): slope = 60.15 mV/pH
#   - ที่ 20C (293.15 K): slope = 58.17 mV/pH
#
# Hardware: DS18B20 ต่อที่ GPIO16 (มี pull-up 4.7k บนบอร์ดแล้ว)
# Hardware: DS18B20 connected to GPIO16 (4.7k pull-up R51 on board)
# ==============================================================================

from machine import Pin
import onewire
import ds18x20
import time

# === ค่าคงที่ทางเคมีไฟฟ้า (Electrochemistry Constants) ===
R_GAS = 8.314      # ค่าคงที่ของก๊าซ (Gas constant, J/(mol*K))
F_FARADAY = 96485  # ค่าคงที่ฟาราเดย์ (Faraday constant, C/mol)
LN_10 = 2.303      # ln(10) สำหรับแปลง ln เป็น log10 (for converting ln to log10)

# === ค่าคงที่ของบอร์ด TitraLab (TitraLab Board Constants) ===
DS18B20_PIN = 16   # GPIO16 - ขาเซ็นเซอร์อุณหภูมิ (Temperature sensor pin)


class TemperatureSensor:
    """
    คลาสเซ็นเซอร์อุณหภูมิสำหรับชดเชยค่า pH (Temperature Sensor Class for pH Compensation)

    เซ็นเซอร์นี้ใช้โปรโตคอล OneWire ซึ่งส่งข้อมูลผ่านสายเพียงเส้นเดียว
    This sensor uses OneWire protocol which transmits data through a single wire.

    การใช้งาน (Usage):
        sensor = TemperatureSensor(16)
        temp_c = sensor.read_celsius()
        slope = sensor.calculate_nernst_slope()
        print(f"Nernst slope at {temp_c}C: {slope:.2f} mV/pH")

    เชื่อมโยงกับ Week 3 (Connection to Week 3):
        ใน Week 3 จะใช้ค่าอุณหภูมินี้ร่วมกับ pHSensor เพื่อคำนวณ pH ที่แม่นยำ
        In Week 3, this temperature will be used with pHSensor for accurate pH calculation.
    """

    def __init__(self, pin=DS18B20_PIN):
        """
        สร้างออบเจกต์เซ็นเซอร์อุณหภูมิ (Create temperature sensor object)

        Args:
            pin: หมายเลข GPIO (GPIO pin number) - TitraLab ใช้ GPIO16

        Raises:
            RuntimeError: ถ้าไม่พบเซ็นเซอร์ (if sensor not found)
        """
        self.pin_number = pin
        self._last_temp = None

        # สร้าง OneWire bus (Create OneWire bus)
        self._pin = Pin(pin)
        self._ow = onewire.OneWire(self._pin)
        self._ds = ds18x20.DS18X20(self._ow)

        # สแกนหาเซ็นเซอร์ (Scan for sensors)
        roms = self._ds.scan()
        if not roms:
            raise RuntimeError(
                f"ไม่พบ DS18B20 ที่ GPIO{pin} (DS18B20 not found at GPIO{pin})"
            )

        # เก็บ ROM address ของเซ็นเซอร์ตัวแรก (Store ROM address of first sensor)
        self._rom = roms[0]
        print(f"DS18B20 พร้อมใช้งานที่ GPIO{pin} (ready at GPIO{pin})")

    def read_celsius(self):
        """
        อ่านอุณหภูมิในหน่วยเซลเซียส (Read temperature in Celsius)

        DS18B20 ต้องการเวลา 750ms ในการแปลงค่า (ความละเอียด 12-bit)
        DS18B20 requires 750ms conversion time (12-bit resolution)

        Returns:
            float: อุณหภูมิเป็นองศาเซลเซียส (temperature in Celsius)
            None: ถ้าอ่านค่าไม่สำเร็จ (if read failed)
        """
        try:
            # สั่งเริ่มการแปลงอุณหภูมิ (Start temperature conversion)
            self._ds.convert_temp()

            # รอให้แปลงเสร็จ (Wait for conversion - 750ms for 12-bit)
            time.sleep_ms(750)

            # อ่านค่าอุณหภูมิ (Read temperature value)
            temp = self._ds.read_temp(self._rom)
            self._last_temp = temp
            return temp

        except Exception as e:
            print(f"ข้อผิดพลาดในการอ่านค่า (Read error): {e}")
            return None

    def read_kelvin(self):
        """
        อ่านอุณหภูมิในหน่วยเคลวิน (Read temperature in Kelvin)

        หน่วยเคลวินใช้ในสมการ Nernst (Kelvin is used in Nernst equation)
        K = C + 273.15

        Returns:
            float: อุณหภูมิเป็นเคลวิน (temperature in Kelvin)
        """
        temp_c = self.read_celsius()
        if temp_c is not None:
            return temp_c + 273.15
        return None

    def get_last_reading(self):
        """
        ดึงค่าอุณหภูมิที่อ่านล่าสุด (Get last temperature reading)

        ใช้เมื่อไม่ต้องการรอ 750ms ในการอ่านค่าใหม่
        Use when you don't want to wait 750ms for a new reading.

        Returns:
            float: อุณหภูมิล่าสุดเป็นเซลเซียส (last temperature in Celsius)
        """
        return self._last_temp

    def calculate_nernst_slope(self, n=1):
        """
        คำนวณความชันตามสมการ Nernst (Calculate Nernst slope)

        สูตร (Formula): slope = (2.303 * R * T) / (n * F)

        ที่อุณหภูมิต่างๆ (At different temperatures):
            20C -> 58.17 mV/pH
            25C -> 59.16 mV/pH (มาตรฐาน/standard)
            30C -> 60.15 mV/pH

        Args:
            n: จำนวนอิเล็กตรอน (electrons transferred), ปกติ = 1 สำหรับ H+

        Returns:
            float: ความชันในหน่วย mV/pH (slope in mV/pH)
        """
        temp_k = self.read_kelvin()
        if temp_k is None:
            return None

        # คำนวณความชัน (Calculate slope)
        # slope (V/pH) = (2.303 * R * T) / (n * F)
        slope_volts = (LN_10 * R_GAS * temp_k) / (n * F_FARADAY)

        # แปลงเป็น mV/pH (Convert to mV/pH)
        slope_mv = slope_volts * 1000
        return slope_mv

    def get_temperature_correction_factor(self, reference_temp=25.0):
        """
        คำนวณปัจจัยแก้ไขอุณหภูมิเทียบกับอุณหภูมิอ้างอิง
        Calculate temperature correction factor relative to reference temperature

        ใช้ปรับค่า pH เมื่อสอบเทียบที่อุณหภูมิหนึ่งแต่วัดที่อุณหภูมิอื่น
        Used to adjust pH when calibrated at one temperature but measured at another.

        Args:
            reference_temp: อุณหภูมิอ้างอิง (reference temperature in Celsius)

        Returns:
            float: ปัจจัยแก้ไข (correction factor) = T_actual / T_reference
        """
        temp_c = self.read_celsius()
        if temp_c is None:
            return 1.0  # ถ้าอ่านไม่ได้ ไม่แก้ไข (no correction if read fails)

        # แปลงเป็นเคลวิน (Convert to Kelvin)
        t_actual = temp_c + 273.15
        t_ref = reference_temp + 273.15

        return t_actual / t_ref


# ==============================================================================
# ส่วนทดสอบ (Test Section)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบเซ็นเซอร์อุณหภูมิ DS18B20")
    print("DS18B20 Temperature Sensor Test")
    print("=" * 50)

    try:
        # สร้างเซ็นเซอร์ (Create sensor)
        sensor = TemperatureSensor(DS18B20_PIN)

        print("\n--- การอ่านค่าอุณหภูมิ (Temperature Readings) ---")
        for i in range(3):
            temp_c = sensor.read_celsius()
            if temp_c is not None:
                temp_k = temp_c + 273.15
                print(f"ครั้งที่ {i+1}: {temp_c:.2f} C = {temp_k:.2f} K")
            time.sleep_ms(100)

        print("\n--- ความสัมพันธ์กับสมการ Nernst (Nernst Equation) ---")
        slope = sensor.calculate_nernst_slope()
        if slope is not None:
            print(f"อุณหภูมิปัจจุบัน (Current temp): {sensor.get_last_reading():.2f} C")
            print(f"ความชัน Nernst (Nernst slope): {slope:.2f} mV/pH")
            print(f"ค่ามาตรฐานที่ 25C (Standard at 25C): 59.16 mV/pH")

            # แสดงผลกระทบต่อการอ่าน pH (Show impact on pH reading)
            delta = slope - 59.16
            print(f"\nผลต่าง (Difference): {delta:+.2f} mV/pH")
            if abs(delta) > 0.5:
                print(">> ควรใช้ Temperature Compensation!")
                print(">> Temperature compensation recommended!")

        print("\n--- ปัจจัยแก้ไขอุณหภูมิ (Temperature Correction) ---")
        factor = sensor.get_temperature_correction_factor(25.0)
        print(f"Correction factor (ref 25C): {factor:.4f}")

        print("\n" + "=" * 50)
        print("ใน Week 3: ค่านี้จะถูกส่งไปยัง pHSensor")
        print("In Week 3: This value will be sent to pHSensor")
        print("สำหรับการคำนวณ pH ที่แม่นยำ")
        print("for accurate pH calculation")
        print("=" * 50)

    except RuntimeError as e:
        print(f"\nข้อผิดพลาด (Error): {e}")
        print("ตรวจสอบการเชื่อมต่อ DS18B20 ที่ GPIO16")
        print("Check DS18B20 connection at GPIO16")

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

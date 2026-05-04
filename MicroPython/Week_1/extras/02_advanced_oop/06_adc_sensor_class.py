# ==============================================================================
# 06_adc_sensor_class.py - คลาส ADCSensor สำหรับอ่านค่า Analog
# (ADCSensor Class for Reading Analog Values)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้ OOP โดยสร้างคลาสอ่านค่า ADC
# Week 1: Learn OOP by creating an ADC reading class
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. สร้างคลาสที่ห่อหุ้ม (encapsulate) การอ่านค่า ADC
#   2. เข้าใจการแปลงค่าดิบเป็นแรงดันไฟฟ้า
#   3. เรียนรู้การตั้งค่า ADC attenuation
#   4. เชื่อมโยงกับการวัด pH sensor
#
# ความสำคัญในเคมี (Importance in Chemistry):
#   - pH sensor ส่งออกแรงดันไฟฟ้าตามค่า pH
#   - ต้องแปลง voltage -> pH ด้วย calibration
#   - ADC อ่านค่าดิบ 0-4095 (12-bit) แล้วแปลงเป็น voltage
#   - Potentiometer ใช้ทดสอบ ADC ก่อนเชื่อมต่อ pH sensor จริง
#
# ESP32 ADC Specifications:
#   - Resolution: 12-bit (0-4095)
#   - ADC1: GPIO32-39 (ใช้งานได้ตลอด)
#   - ADC2: GPIO0,2,4,12-15,25-27 (ใช้ไม่ได้เมื่อ WiFi ทำงาน)
#   - Attenuation settings:
#     - 0dB: 0-1.1V
#     - 2.5dB: 0-1.5V
#     - 6dB: 0-2.2V
#     - 11dB: 0-3.3V (แนะนำสำหรับ TitraLab)
#
# ==============================================================================

from machine import Pin, ADC
import time


class ADCSensor:
    """
    คลาสอ่านค่าจากเซ็นเซอร์ Analog (Analog Sensor Reading Class)

    คลาสนี้ห่อหุ้มการอ่านค่า ADC และแปลงเป็นหน่วยต่างๆ
    เหมาะสำหรับ Potentiometer, pH sensor, และเซ็นเซอร์ analog อื่นๆ

    This class encapsulates ADC reading and conversion to various units.
    Suitable for Potentiometer, pH sensor, and other analog sensors.

    ตัวอย่างการใช้งาน (Usage Example):
        >>> sensor = ADCSensor(25, "pH Sensor")
        >>> raw = sensor.read_raw()        # ค่าดิบ 0-4095
        >>> voltage = sensor.read_voltage() # แรงดัน 0-3.3V
        >>> percent = sensor.read_percent() # เปอร์เซ็นต์ 0-100%
    """

    # === Class Constants ===
    # ค่าคงที่สำหรับการแปลงหน่วย (Constants for unit conversion)
    ADC_MAX_VALUE = 4095       # ค่าสูงสุดของ ADC 12-bit
    ADC_VOLTAGE_MAX = 3.3      # แรงดันสูงสุดที่ ATTN_11DB

    # === Attenuation Presets ===
    # ค่า attenuation ที่ใช้บ่อย (Common attenuation values)
    ATTN_0DB = ADC.ATTN_0DB      # 0-1.1V
    ATTN_2_5DB = ADC.ATTN_2_5DB  # 0-1.5V
    ATTN_6DB = ADC.ATTN_6DB      # 0-2.2V
    ATTN_11DB = ADC.ATTN_11DB    # 0-3.3V (default for TitraLab)

    def __init__(self, pin_number, name="ADC Sensor", attenuation=None):
        """
        สร้าง ADCSensor object (Create ADCSensor object)

        Args:
            pin_number (int): หมายเลขขา GPIO สำหรับ ADC
                             TitraLab pH sensor: GPIO25
                             Potentiometer: GPIO32 หรือ GPIO33
                             (GPIO pin number for ADC)
            name (str): ชื่อเซ็นเซอร์สำหรับแสดงข้อความ (sensor name for display)
            attenuation: ค่า attenuation สำหรับช่วงแรงดัน
                        None = ใช้ ATTN_11DB (0-3.3V) เป็นค่าเริ่มต้น
                        (attenuation for voltage range, None = ATTN_11DB default)

        ตัวอย่าง (Example):
            # Potentiometer ทั่วไป
            pot = ADCSensor(32, "Volume Control")

            # pH Sensor ของ TitraLab
            ph_adc = ADCSensor(25, "pH Analog Input")

            # เซ็นเซอร์ที่ใช้แรงดันต่ำ
            sensor = ADCSensor(34, "Low Voltage", ADC.ATTN_6DB)
        """
        # === Instance Variables ===
        self.pin_number = pin_number
        self.name = name

        # === Private Variables ===
        self._last_raw = 0           # ค่าดิบล่าสุดที่อ่านได้
        self._last_voltage = 0.0     # แรงดันล่าสุดที่อ่านได้

        # ตั้งค่า attenuation (Set attenuation)
        if attenuation is None:
            attenuation = ADC.ATTN_11DB  # ค่าเริ่มต้น 0-3.3V

        self._attenuation = attenuation

        # กำหนดแรงดันสูงสุดตาม attenuation
        # Set max voltage based on attenuation
        self._voltage_max = self._get_voltage_max(attenuation)

        # สร้าง ADC object (Create ADC object)
        self._pin = Pin(pin_number)
        self._adc = ADC(self._pin)

        # ตั้งค่า attenuation (Set attenuation)
        self._adc.atten(attenuation)

        # ตั้งค่า width เป็น 12-bit (Set width to 12-bit)
        # หมายเหตุ: บาง MicroPython version อาจไม่ต้องตั้ง
        # Note: Some MicroPython versions may not require this
        try:
            self._adc.width(ADC.WIDTH_12BIT)
        except AttributeError:
            pass  # บาง version ไม่มี width method

        print(f"สร้าง '{name}' ที่ GPIO{pin_number} สำเร็จ")
        print(f"(Created '{name}' on GPIO{pin_number})")
        print(f"ช่วงแรงดัน (Voltage range): 0-{self._voltage_max:.1f}V")

    def _get_voltage_max(self, attenuation):
        """
        หาค่าแรงดันสูงสุดจาก attenuation setting
        (Get max voltage from attenuation setting)

        Args:
            attenuation: ค่า attenuation

        Returns:
            float: แรงดันสูงสุด (max voltage)
        """
        voltage_map = {
            ADC.ATTN_0DB: 1.1,
            ADC.ATTN_2_5DB: 1.5,
            ADC.ATTN_6DB: 2.2,
            ADC.ATTN_11DB: 3.3,
        }
        return voltage_map.get(attenuation, 3.3)

    def read_raw(self):
        """
        อ่านค่าดิบจาก ADC (Read raw value from ADC)

        ค่าดิบ 0-4095 สำหรับ 12-bit resolution
        Raw value 0-4095 for 12-bit resolution

        Returns:
            int: ค่าดิบจาก ADC (raw ADC value) 0-4095

        ตัวอย่าง (Example):
            raw = sensor.read_raw()
            print(f"ค่าดิบ: {raw}")  # เช่น 2048
        """
        raw = self._adc.read()
        self._last_raw = raw
        return raw

    def read_voltage(self):
        """
        อ่านค่าแรงดันไฟฟ้า (Read voltage value)

        แปลงค่าดิบเป็นแรงดัน: voltage = (raw / 4095) * V_max
        Convert raw to voltage: voltage = (raw / 4095) * V_max

        Returns:
            float: แรงดันไฟฟ้าในหน่วย Volt

        ตัวอย่าง (Example):
            voltage = sensor.read_voltage()
            print(f"แรงดัน: {voltage:.3f} V")
        """
        raw = self.read_raw()
        voltage = (raw / self.ADC_MAX_VALUE) * self._voltage_max
        self._last_voltage = voltage
        return voltage

    def read_percent(self):
        """
        อ่านค่าเป็นเปอร์เซ็นต์ (Read value as percentage)

        แปลงค่าดิบเป็นเปอร์เซ็นต์: percent = (raw / 4095) * 100
        Convert raw to percentage: percent = (raw / 4095) * 100

        Returns:
            float: ค่าเป็นเปอร์เซ็นต์ 0-100%

        ตัวอย่าง (Example):
            percent = sensor.read_percent()
            print(f"ระดับ: {percent:.1f}%")
        """
        raw = self.read_raw()
        percent = (raw / self.ADC_MAX_VALUE) * 100
        return percent

    def read_averaged(self, samples=10, delay_ms=10):
        """
        อ่านค่าเฉลี่ยจากหลายตัวอย่าง (Read averaged value from multiple samples)

        ลด noise โดยอ่านหลายครั้งแล้วหาค่าเฉลี่ย
        Reduce noise by reading multiple times and averaging

        Args:
            samples (int): จำนวนตัวอย่างที่จะอ่าน (number of samples)
                          ค่าเริ่มต้น: 10
            delay_ms (int): เวลาหน่วงระหว่างการอ่าน (delay between reads in ms)
                           ค่าเริ่มต้น: 10ms

        Returns:
            dict: ค่าเฉลี่ยในรูปแบบ {'raw': int, 'voltage': float, 'percent': float}

        ตัวอย่าง (Example):
            result = sensor.read_averaged(20, 5)
            print(f"ค่าเฉลี่ยจาก 20 ตัวอย่าง:")
            print(f"  Raw: {result['raw']}")
            print(f"  Voltage: {result['voltage']:.3f} V")
        """
        total_raw = 0

        for _ in range(samples):
            total_raw += self._adc.read()
            time.sleep_ms(delay_ms)

        avg_raw = total_raw // samples
        avg_voltage = (avg_raw / self.ADC_MAX_VALUE) * self._voltage_max
        avg_percent = (avg_raw / self.ADC_MAX_VALUE) * 100

        # อัพเดตค่าล่าสุด (Update last values)
        self._last_raw = avg_raw
        self._last_voltage = avg_voltage

        return {
            'raw': avg_raw,
            'voltage': avg_voltage,
            'percent': avg_percent
        }

    def estimate_ph(self, calibration_offset=0.0, calibration_slope=1.0):
        """
        ประมาณค่า pH จากแรงดัน (Estimate pH from voltage)

        สำคัญ: นี่เป็นการประมาณเบื้องต้น!
        pH sensor จริงต้อง calibrate ด้วย buffer solutions
        Important: This is a rough estimate!
        Real pH sensor needs calibration with buffer solutions

        สูตรทั่วไป (General formula):
            pH = 7.0 + (V_measured - V_neutral) / slope
            โดย slope ~ -0.05916 V/pH ที่ 25 C (จากสมการ Nernst)

        Args:
            calibration_offset (float): ค่าชดเชย offset (offset compensation)
            calibration_slope (float): ความชันจาก calibration (slope from calibration)

        Returns:
            float: ค่า pH โดยประมาณ (estimated pH value)

        หมายเหตุ (Note):
            - ค่านี้เป็นการประมาณเท่านั้น
            - ต้อง calibrate ด้วย pH buffer 4.0 และ 7.0 สำหรับความแม่นยำ
            - สัปดาห์ที่ 2 จะสร้าง PHSensor class ที่มี calibration เต็มรูปแบบ
        """
        voltage = self.read_voltage()

        # สมมติ: 2.5V = pH 7.0 (neutral)
        # slope จากสมการ Nernst ~ -0.05916 V/pH ที่ 25 C
        # Assume: 2.5V = pH 7.0 (neutral)
        # Nernst slope ~ -0.05916 V/pH at 25 C

        v_neutral = 2.5  # แรงดันที่ pH 7.0
        nernst_slope = -0.05916  # V per pH unit at 25 C

        # คำนวณ pH (Calculate pH)
        ph = 7.0 + ((voltage - v_neutral) * calibration_slope + calibration_offset) / nernst_slope

        return ph

    def get_last_reading(self):
        """
        ดึงค่าล่าสุดที่อ่านได้ (Get last reading without new read)

        Returns:
            dict: {'raw': int, 'voltage': float}
        """
        return {
            'raw': self._last_raw,
            'voltage': self._last_voltage
        }

    def get_status(self):
        """
        ดึงสถานะเซ็นเซอร์ (Get sensor status)

        Returns:
            str: ข้อความสถานะ (status message)
        """
        return (f"{self.name} @ GPIO{self.pin_number}\n"
                f"  ช่วงแรงดัน (Voltage range): 0-{self._voltage_max:.1f}V\n"
                f"  ค่าดิบล่าสุด (Last raw): {self._last_raw}\n"
                f"  แรงดันล่าสุด (Last voltage): {self._last_voltage:.3f}V")

    def deinit(self):
        """
        ปิดการใช้งาน ADC (Deinitialize ADC)

        หมายเหตุ: ADC ของ ESP32 ไม่ต้อง deinit เหมือน PWM
        แต่เป็นการปฏิบัติที่ดีในการทำ cleanup
        Note: ESP32 ADC doesn't need deinit like PWM,
        but it's good practice for cleanup
        """
        self._last_raw = 0
        self._last_voltage = 0.0
        print(f"ปิด {self.name} แล้ว ({self.name} deinitialized)")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบคลาส ADCSensor (Testing ADCSensor Class)")
    print("=" * 60)

    # === สร้าง ADCSensor object ===
    # ใช้ GPIO25 สำหรับ pH sensor (TitraLab pin)
    # หรือใช้ GPIO32 สำหรับ Potentiometer
    # Use GPIO25 for pH sensor (TitraLab pin)
    # Or use GPIO32 for Potentiometer

    print("\n--- สร้างเซ็นเซอร์ (Creating sensors) ---\n")

    # สร้าง sensor สำหรับทดสอบ pH
    # Create sensor for pH testing
    ph_sensor = ADCSensor(25, "pH Analog Input")

    try:
        # === ทดสอบอ่านค่าพื้นฐาน ===
        print("\n--- ทดสอบอ่านค่าพื้นฐาน (Basic reading test) ---\n")

        # อ่านค่าดิบ (Read raw value)
        raw = ph_sensor.read_raw()
        print(f"ค่าดิบ (Raw value): {raw}")

        # อ่านแรงดัน (Read voltage)
        voltage = ph_sensor.read_voltage()
        print(f"แรงดัน (Voltage): {voltage:.3f} V")

        # อ่านเปอร์เซ็นต์ (Read percentage)
        percent = ph_sensor.read_percent()
        print(f"เปอร์เซ็นต์ (Percent): {percent:.1f}%")

        # === ทดสอบอ่านค่าเฉลี่ย ===
        print("\n--- ทดสอบอ่านค่าเฉลี่ย (Averaged reading test) ---\n")

        print("กำลังอ่านค่าเฉลี่ยจาก 20 ตัวอย่าง...")
        print("(Reading average from 20 samples...)")

        result = ph_sensor.read_averaged(20, 5)
        print(f"ค่าเฉลี่ย (Averaged values):")
        print(f"  Raw: {result['raw']}")
        print(f"  Voltage: {result['voltage']:.3f} V")
        print(f"  Percent: {result['percent']:.1f}%")

        # === ทดสอบประมาณค่า pH ===
        print("\n--- ทดสอบประมาณค่า pH (pH estimation test) ---\n")

        print("หมายเหตุ: นี่เป็นค่าประมาณ ต้อง calibrate สำหรับความแม่นยำ")
        print("(Note: This is estimate, calibration needed for accuracy)")
        print()

        # ประมาณค่า pH (Estimate pH)
        estimated_ph = ph_sensor.estimate_ph()
        print(f"แรงดันที่วัดได้ (Measured voltage): {ph_sensor.get_last_reading()['voltage']:.3f} V")
        print(f"ค่า pH โดยประมาณ (Estimated pH): {estimated_ph:.2f}")

        # === ทดสอบอ่านค่าต่อเนื่อง ===
        print("\n--- อ่านค่าต่อเนื่อง 5 ครั้ง (5 consecutive readings) ---\n")
        print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")

        for i in range(5):
            raw = ph_sensor.read_raw()
            voltage = (raw / 4095) * 3.3
            print(f"  อ่านครั้งที่ {i+1} (Reading {i+1}): Raw={raw:4d}, Voltage={voltage:.3f}V")
            time.sleep(0.5)

        # === แสดงสถานะ ===
        print("\n--- สถานะเซ็นเซอร์ (Sensor status) ---\n")
        print(ph_sensor.get_status())

        # === คำอธิบายเชื่อมโยงกับ pH Sensor ===
        print("\n" + "=" * 60)
        print("การเชื่อมโยงกับ pH Sensor (Connection to pH Sensor)")
        print("=" * 60)
        print("""
pH Sensor ของ TitraLab:

1. หลักการทำงาน:
   - pH sensor เป็น electrochemical sensor
   - สร้างแรงดันไฟฟ้าตามสมการ Nernst
   - E = E0 - (RT/nF) * ln([H+])

2. การแปลง Voltage -> pH:
   - ที่ pH 7.0: ~2.5V (neutral)
   - ความชัน (slope): ~59.16 mV per pH unit ที่ 25 C
   - pH = 7 + (V_measured - 2.5) / 0.05916

3. การ Calibration:
   - ใช้ Buffer pH 4.0: จดค่า voltage
   - ใช้ Buffer pH 7.0: จดค่า voltage
   - คำนวณ slope และ offset

4. ใน Week 2:
   - จะสร้าง PHSensor class เต็มรูปแบบ
   - มี calibration 2-point
   - ชดเชยอุณหภูมิอัตโนมัติ
""")

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        # === ทำความสะอาด (Cleanup) ===
        print("\n--- ทำความสะอาด (Cleanup) ---\n")
        ph_sensor.deinit()

        print("\n" + "=" * 60)
        print("สรุปสิ่งที่เรียนรู้ (What we learned):")
        print("=" * 60)
        print("""
1. สร้าง class ADCSensor ที่ห่อหุ้มการอ่าน ADC
   (Created ADCSensor class encapsulating ADC reading)

2. ESP32 ADC Configuration:
   - 12-bit resolution (0-4095)
   - Attenuation settings: 0dB, 2.5dB, 6dB, 11dB
   - ATTN_11DB ให้ช่วง 0-3.3V (เหมาะสำหรับ TitraLab)

3. Methods ที่มีประโยชน์:
   - read_raw(): ค่าดิบ 0-4095
   - read_voltage(): แปลงเป็น Volt
   - read_percent(): แปลงเป็น %
   - read_averaged(): ลด noise ด้วยการเฉลี่ย

4. เชื่อมโยงกับ pH Sensor:
   - pH sensor ส่งออกแรงดัน analog
   - ADC แปลงเป็นค่าดิจิทัล
   - ต้อง calibrate เพื่อแปลงเป็นค่า pH
   - สมการ Nernst อธิบายความสัมพันธ์

5. เตรียมพร้อมสำหรับ Week 2:
   - ADCSensor จะเป็นพื้นฐานของ PHSensor class
   - จะเพิ่ม calibration และ temperature compensation
""")
        print("เสร็จสิ้น (Done)")

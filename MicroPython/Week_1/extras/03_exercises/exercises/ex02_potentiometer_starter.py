"""
แบบฝึกหัดที่ 2: คลาส Potentiometer (Exercise 2: Potentiometer Class)
====================================================================

วัตถุประสงค์ (Objectives):
- เรียนรู้การอ่านค่า Analog (ADC) ผ่าน OOP (Learn to read analog values via OOP)
- เข้าใจการแปลงค่าดิบเป็นค่าที่มีความหมาย (Understand raw value conversion)
- เตรียมความพร้อมสำหรับการอ่านค่าเซ็นเซอร์ pH (Prepare for pH sensor reading)

ความเชื่อมโยงกับเคมี (Chemistry Connection):
===========================================
Potentiometer ทำงานคล้ายกับเซ็นเซอร์ pH:
- ทั้งคู่ส่งแรงดันไฟฟ้า (Voltage) ที่แปรผันตามค่าที่วัด
- Potentiometer: ตำแหน่งการหมุน -> แรงดัน 0-3.3V
- pH Sensor: ความเป็นกรด-ด่าง -> แรงดัน (ผ่านวงจรขยายสัญญาณ)

ในห้องปฏิบัติการเคมี เราใช้ ADC อ่านค่าจาก:
- เซ็นเซอร์ pH (pH electrode)
- เซ็นเซอร์ค่าการนำไฟฟ้า (Conductivity sensor)
- เซ็นเซอร์ออกซิเจนละลาย (Dissolved oxygen sensor)

ADC Resolution บน ESP32:
- 12-bit ADC: 0-4095 (2^12 = 4096 ระดับ)
- แรงดันอ้างอิง: 0-3.3V (เมื่อใช้ ATTN_11DB)

เกณฑ์ความสำเร็จ (Success Criteria):
[ ] สร้างคลาส Potentiometer ที่อ่านค่า ADC ได้ (Create Potentiometer class that reads ADC)
[ ] แปลงค่าดิบเป็นเปอร์เซ็นต์ 0-100% (Convert raw value to 0-100%)
[ ] แปลงค่าดิบเป็นแรงดัน 0-3.3V (Convert raw value to 0-3.3V)
[ ] คำนวณค่าเฉลี่ยจากการอ่านหลายครั้ง (Calculate average from multiple readings)
[ ] Property สำหรับเข้าถึงค่าต่างๆ (Properties for accessing values)

ขาที่ใช้งาน (Pin Configuration):
- Potentiometer/pH Sensor: GPIO25 (ADC input)
"""

from machine import Pin, ADC
import time


class Potentiometer:
    """
    คลาสสำหรับอ่านค่า Potentiometer ผ่าน ADC (Class for reading Potentiometer via ADC)

    หลักการทำงานเหมือนกับการอ่านค่าเซ็นเซอร์ pH
    Works similarly to pH sensor reading

    Attributes:
        adc (ADC): ออบเจ็กต์ ADC สำหรับอ่านค่า (ADC object for reading)
        _raw_value (int): ค่าดิบล่าสุดที่อ่านได้ (Latest raw value)
        max_value (int): ค่าสูงสุดของ ADC (Maximum ADC value)
        ref_voltage (float): แรงดันอ้างอิง (Reference voltage)

    Example:
        pot = Potentiometer(25)  # สร้างที่ขา GPIO25 (Create on GPIO25)
        print(pot.percent)       # อ่านค่าเป็น % (Read as percentage)
        print(pot.voltage)       # อ่านค่าเป็นโวลต์ (Read as voltage)
    """

    # ค่าคงที่ของ ADC (ADC Constants)
    ADC_MAX = 4095          # ค่าสูงสุด 12-bit ADC (Maximum 12-bit ADC value)
    REF_VOLTAGE = 3.3       # แรงดันอ้างอิง (Reference voltage in Volts)

    def __init__(self, pin_number: int):
        """
        สร้างออบเจ็กต์ Potentiometer (Create Potentiometer object)

        Args:
            pin_number: หมายเลขขา GPIO (GPIO pin number) - ใช้ GPIO25

        คำแนะนำ (Hints):
        - สร้าง ADC จาก Pin: ADC(Pin(pin_number))
        - ตั้งค่า attenuation เป็น ADC.ATTN_11DB เพื่อวัดช่วง 0-3.3V
        - เริ่มต้นค่า _raw_value เป็น 0
        """
        # TODO: สร้าง ADC object (Create ADC object)
        # self.adc = ???

        # TODO: ตั้งค่า attenuation สำหรับช่วง 0-3.3V (Set attenuation for 0-3.3V range)
        # self.adc.atten(???)

        # TODO: กำหนดค่าเริ่มต้น (Initialize values)
        # self._raw_value = ???
        pass

    def read_raw(self) -> int:
        """
        อ่านค่าดิบจาก ADC (Read raw value from ADC)

        Returns:
            int: ค่าดิบ 0-4095 (Raw value 0-4095)

        คำแนะนำ (Hints):
        - ใช้ self.adc.read() เพื่ออ่านค่า
        - เก็บค่าไว้ใน self._raw_value ด้วย
        """
        # TODO: อ่านค่าจาก ADC และเก็บไว้ (Read from ADC and store)
        pass

    def read_average(self, samples: int = 10, delay_ms: int = 10) -> int:
        """
        อ่านค่าเฉลี่ยจากหลายตัวอย่าง (Read average from multiple samples)

        การอ่านค่าเฉลี่ยช่วยลดสัญญาณรบกวน (noise) ซึ่งสำคัญมากในการวัด pH
        Averaging helps reduce noise, which is crucial for pH measurement

        Args:
            samples: จำนวนตัวอย่าง (Number of samples)
            delay_ms: เวลาหน่วงระหว่างการอ่าน (Delay between readings in ms)

        Returns:
            int: ค่าเฉลี่ย (Average value)

        คำแนะนำ (Hints):
        - สร้างตัวแปรสะสมค่า total = 0
        - ใช้ for loop อ่านค่าตามจำนวน samples
        - หารด้วยจำนวน samples เพื่อหาค่าเฉลี่ย
        - ใช้ time.sleep_ms() หน่วงเวลาระหว่างการอ่าน
        """
        # TODO: อ่านค่าเฉลี่ย (Read average value)
        # total = 0
        # for i in range(samples):
        #     ???
        # return total // samples
        pass

    @property
    def raw(self) -> int:
        """
        คืนค่าดิบล่าสุด (Return latest raw value)

        Returns:
            int: ค่าดิบ 0-4095
        """
        # TODO: อ่านและคืนค่าดิบ (Read and return raw value)
        pass

    @property
    def percent(self) -> float:
        """
        คืนค่าเป็นเปอร์เซ็นต์ (Return value as percentage)

        Returns:
            float: ค่า 0.0-100.0%

        คำแนะนำ (Hints):
        - percent = (raw / ADC_MAX) * 100
        - อ่านค่าดิบก่อนแล้วค่อยคำนวณ
        """
        # TODO: คำนวณและคืนค่าเปอร์เซ็นต์ (Calculate and return percentage)
        pass

    @property
    def voltage(self) -> float:
        """
        คืนค่าเป็นแรงดันไฟฟ้า (Return value as voltage)

        Returns:
            float: ค่า 0.0-3.3V

        คำแนะนำ (Hints):
        - voltage = (raw / ADC_MAX) * REF_VOLTAGE
        - สูตรนี้เหมือนกับที่ใช้ในการแปลงค่าเซ็นเซอร์ pH

        หมายเหตุทางเคมี (Chemistry Note):
        สำหรับเซ็นเซอร์ pH จะต้องแปลงแรงดันนี้เป็นค่า pH อีกครั้ง
        โดยใช้สมการ Nernst หรือ calibration curve
        """
        # TODO: คำนวณและคืนค่าแรงดัน (Calculate and return voltage)
        pass

    def map_to_range(self, min_val: float, max_val: float) -> float:
        """
        แปลงค่าไปยังช่วงที่กำหนด (Map value to specified range)

        ฟังก์ชันนี้มีประโยชน์มากในการแปลงค่า ADC เป็นค่า pH (0-14)
        This function is very useful for converting ADC to pH value (0-14)

        Args:
            min_val: ค่าต่ำสุดของช่วงเป้าหมาย (Minimum of target range)
            max_val: ค่าสูงสุดของช่วงเป้าหมาย (Maximum of target range)

        Returns:
            float: ค่าที่แปลงแล้ว (Mapped value)

        คำแนะนำ (Hints):
        - สูตร: mapped = min_val + (raw / ADC_MAX) * (max_val - min_val)
        - ตัวอย่าง: map_to_range(0, 14) แปลงเป็นสเกล pH
        """
        # TODO: แปลงค่าไปยังช่วงที่กำหนด (Map value to range)
        pass


# =============================================================================
# โค้ดทดสอบ (Test Code)
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบคลาส Potentiometer (Testing Potentiometer Class)")
    print("คลาสนี้เตรียมพื้นฐานสำหรับการอ่านค่าเซ็นเซอร์ pH")
    print("This class prepares foundation for pH sensor reading")
    print("=" * 60)

    # สร้าง Potentiometer ที่ขา GPIO25 (เหมือนขาเซ็นเซอร์ pH)
    # Create Potentiometer on GPIO25 (same as pH sensor pin)
    pot = Potentiometer(25)

    print("\n[Test 1] อ่านค่าดิบ (Read raw values)")
    for i in range(5):
        raw = pot.raw
        print(f"  การอ่านครั้งที่ {i+1}: {raw}")
        time.sleep(0.2)

    print("\n[Test 2] อ่านค่าเฉลี่ย (Read average values)")
    avg = pot.read_average(samples=20, delay_ms=10)
    print(f"  ค่าเฉลี่ยจาก 20 ตัวอย่าง: {avg}")

    print("\n[Test 3] แปลงเป็นเปอร์เซ็นต์และแรงดัน (Convert to percent and voltage)")
    print(f"  ค่าดิบ (Raw): {pot.raw}")
    print(f"  เปอร์เซ็นต์ (Percent): {pot.percent:.1f}%")
    print(f"  แรงดัน (Voltage): {pot.voltage:.3f}V")

    print("\n[Test 4] จำลองการแปลงเป็นค่า pH (Simulate pH conversion)")
    print("  แปลงค่า ADC เป็นช่วง pH 0-14")
    print("  Converting ADC to pH range 0-14")
    ph_value = pot.map_to_range(0, 14)
    print(f"  ค่า pH จำลอง (Simulated pH): {ph_value:.2f}")

    print("\n[Test 5] ติดตามค่าแบบ real-time (Real-time monitoring)")
    print("  กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
    print("-" * 40)

    try:
        for i in range(20):  # อ่าน 20 ครั้ง (Read 20 times)
            raw = pot.raw
            voltage = pot.voltage
            percent = pot.percent
            ph_sim = pot.map_to_range(0, 14)

            # แสดงแบบ bar graph
            bar_length = int(percent / 5)  # 20 ช่องสำหรับ 100%
            bar = "#" * bar_length + "-" * (20 - bar_length)

            print(f"  [{bar}] {percent:5.1f}% | {voltage:.2f}V | pH~{ph_sim:.1f}")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n  หยุดโดยผู้ใช้ (Stopped by user)")

    print("\n" + "=" * 60)
    print("การทดสอบเสร็จสิ้น (Testing completed)")
    print("=" * 60)

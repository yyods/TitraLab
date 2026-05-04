# ==============================================================================
# 03_adc_ph_basics.py - พื้นฐาน ADC สำหรับเซ็นเซอร์ pH (ADC Basics for pH Sensor)
# ==============================================================================
# สัปดาห์ที่ 1: พื้นฐาน ADC (Week 1: ADC Basics)
# เวลา: ~30 นาที (Time: ~30 minutes)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ ADC: แปลงแรงดัน analog เป็นตัวเลข digital
#   2. เข้าใจสมการ Nernst: E = E0 - 59.16 mV × pH (ที่ 25°C)
#   3. เตรียมพร้อมสำหรับการอ่านค่า pH ใน Week 3
#
# การเชื่อมโยงกับ Week 3 (Connection to Week 3):
#   - GPIO25 = pH Sensor ADC input (from LMC6482 op-amp circuit)
#   - Week 3 ใช้ ADC อ่านค่า pH สำหรับไทเทรชันอัตโนมัติ
#
# ฮาร์ดแวร์ (Hardware):
#   - ใช้ Potentiometer (GPIO32) จำลองสัญญาณ pH
#   - Week 3 ใช้ pH sensor จริง (GPIO25)
# ==============================================================================

from machine import Pin, ADC
import time

# นำเข้าขา GPIO (Import GPIO pins)
try:
    from pins import POT1_PIN, PH_PIN
except ImportError:
    POT1_PIN = 32   # Potentiometer สำหรับฝึก (for practice)
    PH_PIN = 25     # pH Sensor ใน Week 3

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================
ADC_MAX = 4095          # 12-bit ADC (0-4095)
VOLTAGE_MAX = 3.3       # แรงดันสูงสุด (V)
NERNST_SLOPE = -59.16   # mV/pH ที่ 25°C (ตามสมการ Nernst)


# ==============================================================================
# คลาส ADCReader (ADC Reader Class)
# ==============================================================================
class ADCReader:
    """
    คลาสอ่านค่า ADC สำหรับเซ็นเซอร์ (ADC Reader Class for Sensors)

    ใน Week 3 จะใช้สำหรับอ่านค่า pH Sensor
    In Week 3, used for reading pH Sensor values

    ตัวอย่างการใช้ (Usage):
        adc = ADCReader(32)          # Potentiometer
        raw, voltage = adc.read()    # อ่านค่า
    """

    def __init__(self, pin_number, name="ADC"):
        """
        สร้าง ADCReader (Create ADCReader)

        Args:
            pin_number (int): GPIO pin (32=POT1, 25=pH)
            name (str): ชื่อสำหรับแสดงผล
        """
        self.pin_number = pin_number
        self.name = name
        self._adc = ADC(Pin(pin_number))
        self._adc.atten(ADC.ATTN_11DB)  # ช่วง 0-3.3V

    def read_raw(self):
        """อ่านค่าดิบ 0-4095 (Read raw value)"""
        return self._adc.read()

    def read_voltage(self):
        """อ่านค่าเป็น Volt (Read as Voltage)"""
        raw = self.read_raw()
        return (raw / ADC_MAX) * VOLTAGE_MAX

    def read_averaged(self, samples=10):
        """
        อ่านค่าเฉลี่ย (Read averaged value)
        - ช่วยลด noise สำหรับ pH sensor
        """
        total = 0
        for _ in range(samples):
            total += self._adc.read()
            time.sleep_ms(5)
        return total // samples

    def read(self):
        """
        อ่านค่าพร้อมแปลงเป็น Volt (Read with voltage conversion)

        Returns:
            tuple: (raw_value, voltage)
        """
        raw = self.read_raw()
        voltage = (raw / ADC_MAX) * VOLTAGE_MAX
        return raw, voltage


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ADC Basics for pH Sensor")
    print("พื้นฐาน ADC สำหรับเซ็นเซอร์ pH")
    print("=" * 50)
    print()
    print("สมการ Nernst (Nernst Equation):")
    print("  E = E0 - 59.16 mV × pH  (ที่ 25°C)")
    print()
    print("  pH 4 (กรด)  -> แรงดันสูง")
    print("  pH 7 (กลาง) -> แรงดันกลาง")
    print("  pH 10 (เบส) -> แรงดันต่ำ")
    print()
    print(f"กำลังอ่านจาก GPIO{POT1_PIN} (Potentiometer)")
    print("หมุน Potentiometer เพื่อจำลอง pH")
    print("กด Ctrl+C เพื่อหยุด")
    print("-" * 50)

    # สร้าง ADCReader
    adc = ADCReader(POT1_PIN, "Potentiometer")

    try:
        count = 0
        while True:
            count += 1
            raw, voltage = adc.read()
            mv = voltage * 1000  # แปลงเป็น mV

            print(f"[{count:3d}] Raw: {raw:4d}  Voltage: {voltage:.3f}V  ({mv:.1f} mV)")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("สรุป (Summary):")
        print("-" * 50)
        print("  1. ADC แปลง 0-3.3V -> 0-4095")
        print("  2. สมการ Nernst: -59.16 mV/pH")
        print("  3. Week 3: ใช้ GPIO25 อ่าน pH จริง")
        print("=" * 50)

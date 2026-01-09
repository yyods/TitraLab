# ==============================================================================
# 01_adc_basics.py - พื้นฐาน ADC (ADC Basics)
# ==============================================================================
# โปรแกรมนี้สอนพื้นฐานการใช้ ADC (Analog-to-Digital Converter)
# This program teaches the basics of using ADC (Analog-to-Digital Converter)
#
# ADC คืออะไร? (What is ADC?)
#   - ADC แปลงแรงดันไฟฟ้า analog (0-3.3V) เป็นตัวเลขดิจิทัล (0-4095)
#   - ADC converts analog voltage (0-3.3V) to digital number (0-4095)
#   - ESP32 มี ADC ความละเอียด 12-bit (2^12 = 4096 ระดับ)
#   - ESP32 has 12-bit ADC resolution (2^12 = 4096 levels)
#
# ความสำคัญในเคมี (Importance in Chemistry):
#   - เซ็นเซอร์ pH ส่งสัญญาณ analog ออกมา
#   - pH sensor outputs analog signal
#   - เราต้องใช้ ADC อ่านค่าก่อนแปลงเป็น pH
#   - We need ADC to read values before converting to pH
#
# อุปกรณ์ที่ใช้ (Equipment used):
#   - Potentiometer บนบอร์ด TitraLab (GPIO32 หรือ GPIO33)
#   - Potentiometer on TitraLab board (GPIO32 or GPIO33)
#
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

from machine import Pin, ADC
import time

# นำเข้าค่าขา GPIO จากไฟล์ pins.py (Import GPIO pins from pins.py)
# หมายเหตุ: ถ้าไม่มีไฟล์ pins.py ให้ใช้ค่าตรงๆ
# Note: If pins.py is not available, use direct values
try:
    from pins import POT1_PIN, POT2_PIN
except ImportError:
    POT1_PIN = 32  # GPIO32 - Potentiometer 1
    POT2_PIN = 33  # GPIO33 - Potentiometer 2

# ==============================================================================
# การตั้งค่า ADC (ADC Configuration)
# ==============================================================================

# สร้าง ADC object ที่ขา POT1_PIN (GPIO32)
# Create ADC object at POT1_PIN (GPIO32)
adc = ADC(Pin(POT1_PIN))

# ตั้งค่า attenuation เป็น 11dB เพื่อให้อ่านได้ 0-3.3V
# Set attenuation to 11dB to read 0-3.3V range
# หมายเหตุ: ค่า attenuation กำหนดช่วงแรงดันที่อ่านได้
# Note: Attenuation value determines the readable voltage range
adc.atten(ADC.ATTN_11DB)

# ==============================================================================
# ค่าคงที่สำหรับการคำนวณ (Constants for calculation)
# ==============================================================================

ADC_MAX = 4095       # ค่าสูงสุดของ ADC 12-bit (Max value for 12-bit ADC)
VOLTAGE_MAX = 3.3    # แรงดันสูงสุด (Maximum voltage in Volts)

# ==============================================================================
# ฟังก์ชันแปลงค่า ADC เป็นแรงดัน (Function to convert ADC to voltage)
# ==============================================================================

def adc_to_voltage(raw_value):
    """
    แปลงค่าดิบ ADC เป็นแรงดันไฟฟ้า (Convert raw ADC value to voltage)

    สูตร (Formula):
        voltage = (raw_value / ADC_MAX) * VOLTAGE_MAX
        voltage = (raw_value / 4095) * 3.3

    ตัวอย่าง (Examples):
        - raw = 0    -> voltage = 0.00 V
        - raw = 2048 -> voltage = 1.65 V (ครึ่งหนึ่ง / half)
        - raw = 4095 -> voltage = 3.30 V

    Args:
        raw_value (int): ค่าดิบจาก ADC (0-4095)

    Returns:
        float: แรงดันไฟฟ้า (Voltage in Volts)
    """
    voltage = (raw_value / ADC_MAX) * VOLTAGE_MAX
    return voltage

# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================

print("=" * 60)
print("บทเรียน ADC พื้นฐาน (ADC Basics Lesson)")
print("=" * 60)
print()
print("ADC คืออะไร? (What is ADC?)")
print("-" * 40)
print("  - แปลงแรงดัน analog เป็นตัวเลข digital")
print("  - Converts analog voltage to digital number")
print("  - ESP32: 0V -> 0, 3.3V -> 4095 (12-bit)")
print()
print("เตรียมพร้อมสำหรับเซ็นเซอร์ pH! (Preparing for pH sensor!)")
print("  - pH sensor ส่งแรงดันออกมา")
print("  - pH sensor outputs voltage")
print("  - ADC อ่านแรงดัน -> แปลงเป็นค่า pH")
print("  - ADC reads voltage -> convert to pH value")
print()
print(f"กำลังอ่านค่าจาก Potentiometer ที่ GPIO{POT1_PIN}")
print(f"(Reading from Potentiometer at GPIO{POT1_PIN})")
print()
print("หมุน Potentiometer เพื่อดูการเปลี่ยนแปลงค่า")
print("(Turn Potentiometer to see value changes)")
print()
print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
print("=" * 60)
print()

try:
    # ตัวแปรสำหรับนับจำนวนการอ่าน (Counter for readings)
    reading_count = 0

    while True:
        # อ่านค่าดิบจาก ADC (Read raw value from ADC)
        raw_value = adc.read()

        # แปลงเป็นแรงดัน (Convert to voltage)
        voltage = adc_to_voltage(raw_value)

        # คำนวณเปอร์เซ็นต์ (Calculate percentage)
        percent = (raw_value / ADC_MAX) * 100

        # เพิ่มจำนวนการอ่าน (Increment reading count)
        reading_count += 1

        # แสดงผล (Display results)
        print(f"การอ่านครั้งที่ {reading_count:3d} (Reading #{reading_count:3d})")
        print(f"  ค่าดิบ (Raw value) : {raw_value:4d} / {ADC_MAX}")
        print(f"  แรงดัน (Voltage)  : {voltage:.3f} V")
        print(f"  เปอร์เซ็นต์ (%)   : {percent:.1f}%")
        print()

        # หน่วงเวลา 1 วินาที (Delay 1 second)
        time.sleep(1)

except KeyboardInterrupt:
    # เมื่อกด Ctrl+C (When Ctrl+C is pressed)
    print("\n" + "=" * 60)
    print("หยุดโปรแกรม (Program stopped)")
    print("=" * 60)
    print()
    print("สรุปสิ่งที่เรียนรู้ (What you learned):")
    print("-" * 40)
    print("1. ADC แปลง analog -> digital")
    print("   ADC converts analog -> digital")
    print()
    print("2. ESP32 ADC 12-bit: 0-4095")
    print("   ESP32 ADC 12-bit: 0-4095")
    print()
    print("3. สูตรแปลงเป็นแรงดัน:")
    print("   Formula to convert to voltage:")
    print("   voltage = (raw / 4095) * 3.3")
    print()
    print("4. นี่คือพื้นฐานสำหรับ pH sensor!")
    print("   This is the foundation for pH sensor!")
    print()
    print("ต่อไป: 02_adc_averaging.py (การเฉลี่ยค่าเพื่อลด noise)")
    print("Next: 02_adc_averaging.py (Averaging to reduce noise)")
    print("=" * 60)

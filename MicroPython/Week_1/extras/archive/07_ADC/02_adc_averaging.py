# ==============================================================================
# 02_adc_averaging.py - การเฉลี่ยค่า ADC เพื่อลด Noise (ADC Averaging for Noise Reduction)
# ==============================================================================
# โปรแกรมนี้สอนการอ่านค่า ADC หลายครั้งแล้วหาค่าเฉลี่ย
# This program teaches reading ADC multiple times and averaging
#
# ทำไมต้องเฉลี่ยค่า? (Why average values?)
#   - สัญญาณ analog มักมี noise (สัญญาณรบกวน)
#   - Analog signals often have noise (interference)
#   - การเฉลี่ยช่วยให้ค่าเสถียรขึ้น
#   - Averaging makes values more stable
#   - เซ็นเซอร์ pH ต้องการค่าที่เสถียรมาก!
#   - pH sensor needs very stable readings!
#
# หลักการ (Principle):
#   - อ่านค่าหลายครั้ง (เช่น 10 ครั้ง)
#   - Read multiple times (e.g., 10 times)
#   - รวมค่าทั้งหมดแล้วหารด้วยจำนวนครั้ง
#   - Sum all values and divide by count
#   - ค่าที่ได้จะใกล้เคียงค่าจริงมากขึ้น
#   - Result will be closer to true value
#
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

from machine import Pin, ADC
import time

# นำเข้าค่าขา GPIO จากไฟล์ pins.py (Import GPIO pins from pins.py)
try:
    from pins import POT1_PIN
except ImportError:
    POT1_PIN = 32  # GPIO32 - Potentiometer 1

# ==============================================================================
# การตั้งค่า ADC (ADC Configuration)
# ==============================================================================

# สร้าง ADC object (Create ADC object)
adc = ADC(Pin(POT1_PIN))

# ตั้งค่า attenuation สำหรับช่วง 0-3.3V (Set attenuation for 0-3.3V range)
adc.atten(ADC.ATTN_11DB)

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================

ADC_MAX = 4095       # ค่าสูงสุดของ ADC 12-bit
VOLTAGE_MAX = 3.3    # แรงดันสูงสุด (Volts)

# ==============================================================================
# ฟังก์ชันอ่านค่าครั้งเดียว (Function to read single value)
# ==============================================================================

def read_single():
    """
    อ่านค่า ADC ครั้งเดียว (Read single ADC value)

    Returns:
        int: ค่าดิบจาก ADC (raw ADC value) 0-4095
    """
    return adc.read()

# ==============================================================================
# ฟังก์ชันอ่านค่าเฉลี่ย (Function to read averaged value)
# ==============================================================================

def read_averaged(num_samples=10, delay_ms=10):
    """
    อ่านค่า ADC หลายครั้งแล้วหาค่าเฉลี่ย (Read ADC multiple times and average)

    หลักการ (Principle):
        1. อ่านค่าตามจำนวน num_samples ครั้ง
           Read values num_samples times
        2. รวมค่าทั้งหมด (Sum all values)
        3. หารด้วยจำนวนครั้ง (Divide by count)

    สูตร (Formula):
        average = (sum of all readings) / num_samples

    Args:
        num_samples (int): จำนวนครั้งที่จะอ่าน (number of readings)
                          ค่าเริ่มต้น: 10 ครั้ง (default: 10)
        delay_ms (int): เวลาหน่วงระหว่างการอ่าน (delay between readings in ms)
                       ค่าเริ่มต้น: 10 ms (default: 10 ms)

    Returns:
        int: ค่าเฉลี่ย (averaged value)

    ตัวอย่างการเรียกใช้ (Usage examples):
        avg = read_averaged()          # 10 ตัวอย่าง, หน่วง 10ms
        avg = read_averaged(20)        # 20 ตัวอย่าง, หน่วง 10ms
        avg = read_averaged(50, 5)     # 50 ตัวอย่าง, หน่วง 5ms
    """
    # ตัวแปรสำหรับเก็บผลรวม (Variable to store sum)
    total = 0

    # อ่านค่าตามจำนวนที่กำหนด (Read values as specified)
    for i in range(num_samples):
        # อ่านค่าจาก ADC (Read from ADC)
        value = adc.read()

        # บวกเข้าไปในผลรวม (Add to total)
        total = total + value

        # หน่วงเวลาเล็กน้อยระหว่างการอ่าน
        # Small delay between readings
        time.sleep_ms(delay_ms)

    # คำนวณค่าเฉลี่ย (Calculate average)
    # ใช้ // เพื่อให้ได้จำนวนเต็ม (Use // for integer result)
    average = total // num_samples

    return average

# ==============================================================================
# ฟังก์ชันแปลงค่าเป็นแรงดัน (Function to convert to voltage)
# ==============================================================================

def to_voltage(raw_value):
    """
    แปลงค่าดิบเป็นแรงดัน (Convert raw value to voltage)

    Args:
        raw_value (int): ค่าดิบจาก ADC (0-4095)

    Returns:
        float: แรงดัน (Voltage in Volts)
    """
    return (raw_value / ADC_MAX) * VOLTAGE_MAX

# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================

print("=" * 60)
print("บทเรียน ADC Averaging (ADC Averaging Lesson)")
print("=" * 60)
print()
print("ทำไมต้องเฉลี่ยค่า? (Why average values?)")
print("-" * 40)
print("  - สัญญาณ analog มี noise (สัญญาณรบกวน)")
print("  - Analog signals have noise (interference)")
print("  - การเฉลี่ยทำให้ค่าเสถียรขึ้น")
print("  - Averaging makes values more stable")
print()
print("ความสำคัญในเคมี (Importance in Chemistry):")
print("-" * 40)
print("  - pH sensor ต้องการค่าที่แม่นยำ")
print("  - pH sensor needs accurate readings")
print("  - การเปลี่ยนแปลง pH 0.1 มีความหมาย!")
print("  - pH change of 0.1 is significant!")
print()
print(f"กำลังอ่านค่าจาก Potentiometer ที่ GPIO{POT1_PIN}")
print(f"(Reading from Potentiometer at GPIO{POT1_PIN})")
print()
print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
print("=" * 60)
print()

try:
    # ตัวแปรสำหรับนับรอบ (Counter for iterations)
    iteration = 0

    while True:
        iteration += 1
        print(f"--- รอบที่ {iteration} (Iteration {iteration}) ---")
        print()

        # ===== การอ่านค่าครั้งเดียว (Single reading) =====
        single_value = read_single()
        single_voltage = to_voltage(single_value)
        print(f"การอ่านครั้งเดียว (Single reading):")
        print(f"  ค่าดิบ (Raw)   : {single_value:4d}")
        print(f"  แรงดัน (Volt) : {single_voltage:.3f} V")
        print()

        # ===== การอ่านค่าเฉลี่ย 10 ครั้ง (Average of 10 readings) =====
        print("กำลังอ่านค่าเฉลี่ย 10 ตัวอย่าง...")
        print("(Reading average of 10 samples...)")
        avg_10 = read_averaged(10, 10)
        avg_10_voltage = to_voltage(avg_10)
        print(f"ค่าเฉลี่ย 10 ตัวอย่าง (Average of 10):")
        print(f"  ค่าดิบ (Raw)   : {avg_10:4d}")
        print(f"  แรงดัน (Volt) : {avg_10_voltage:.3f} V")
        print()

        # ===== การอ่านค่าเฉลี่ย 50 ครั้ง (Average of 50 readings) =====
        print("กำลังอ่านค่าเฉลี่ย 50 ตัวอย่าง...")
        print("(Reading average of 50 samples...)")
        avg_50 = read_averaged(50, 5)
        avg_50_voltage = to_voltage(avg_50)
        print(f"ค่าเฉลี่ย 50 ตัวอย่าง (Average of 50):")
        print(f"  ค่าดิบ (Raw)   : {avg_50:4d}")
        print(f"  แรงดัน (Volt) : {avg_50_voltage:.3f} V")
        print()

        # ===== เปรียบเทียบผลลัพธ์ (Compare results) =====
        print("เปรียบเทียบ (Comparison):")
        print("-" * 40)
        print(f"  {'วิธี':<20} {'Raw':>6} {'Voltage':>10}")
        print(f"  {'Method':<20} {'':>6} {'':>10}")
        print(f"  {'-'*20} {'-'*6} {'-'*10}")
        print(f"  {'ครั้งเดียว (Single)':<20} {single_value:>6} {single_voltage:>10.3f}")
        print(f"  {'เฉลี่ย 10 (Avg 10)':<20} {avg_10:>6} {avg_10_voltage:>10.3f}")
        print(f"  {'เฉลี่ย 50 (Avg 50)':<20} {avg_50:>6} {avg_50_voltage:>10.3f}")
        print()

        # คำนวณความแตกต่าง (Calculate difference)
        diff_single_avg50 = abs(single_value - avg_50)
        diff_avg10_avg50 = abs(avg_10 - avg_50)

        print("ความแตกต่าง (Difference):")
        print(f"  |ครั้งเดียว - เฉลี่ย50| = {diff_single_avg50}")
        print(f"  |เฉลี่ย10 - เฉลี่ย50|   = {diff_avg10_avg50}")
        print()

        # หน่วงเวลา 3 วินาที (Delay 3 seconds)
        print("รอ 3 วินาที... (Waiting 3 seconds...)")
        print()
        time.sleep(3)

except KeyboardInterrupt:
    # เมื่อกด Ctrl+C (When Ctrl+C is pressed)
    print("\n" + "=" * 60)
    print("หยุดโปรแกรม (Program stopped)")
    print("=" * 60)
    print()
    print("สรุปสิ่งที่เรียนรู้ (What you learned):")
    print("-" * 40)
    print()
    print("1. ทำไมต้องเฉลี่ยค่า (Why average):")
    print("   - สัญญาณ analog มี noise")
    print("   - Analog signals have noise")
    print()
    print("2. วิธีการเฉลี่ย (How to average):")
    print("   - อ่านหลายครั้ง (เช่น 10-50 ครั้ง)")
    print("   - Read multiple times (e.g., 10-50)")
    print("   - รวมค่าแล้วหารด้วยจำนวน")
    print("   - Sum values and divide by count")
    print()
    print("3. ผลของการเฉลี่ย (Effect of averaging):")
    print("   - ยิ่งเฉลี่ยมาก ค่ายิ่งเสถียร")
    print("   - More samples = more stable")
    print("   - แต่ใช้เวลานานขึ้น")
    print("   - But takes longer time")
    print()
    print("4. การประยุกต์ใช้กับ pH sensor:")
    print("   Application for pH sensor:")
    print("   - pH sensor ต้องการค่าเสถียร")
    print("   - pH sensor needs stable values")
    print("   - เราจะใช้การเฉลี่ยใน Week 2")
    print("   - We will use averaging in Week 2")
    print()
    print("ต่อไป: 03_adc_attenuation.py (การตั้งค่า ADC attenuation)")
    print("Next: 03_adc_attenuation.py (ADC attenuation settings)")
    print("=" * 60)

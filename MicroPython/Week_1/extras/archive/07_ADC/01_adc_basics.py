# ==============================================================================
# 01_adc_basics.py - พื้นฐาน ADC สำหรับเซ็นเซอร์ pH (ADC Basics for pH Sensor)
# ==============================================================================
# โปรแกรมนี้สอนพื้นฐาน ADC เพื่อเตรียมความพร้อมสำหรับการอ่านค่า pH ใน Week 3
# This program teaches ADC basics in preparation for pH reading in Week 3
#
# นี่คือพื้นฐานการอ่านค่า pH ที่ใช้ใน Week 3
# This is the basis for pH reading used in Week 3
#
# ==============================================================================
# ADC คืออะไร? (What is ADC?)
# ==============================================================================
#   - ADC แปลงแรงดันไฟฟ้า analog (0-3.3V) เป็นตัวเลขดิจิทัล (0-4095)
#   - ADC converts analog voltage (0-3.3V) to digital number (0-4095)
#   - ESP32 มี ADC ความละเอียด 12-bit (2^12 = 4096 ระดับ)
#   - ESP32 has 12-bit ADC resolution (2^12 = 4096 levels)
#
# ==============================================================================
# ฮาร์ดแวร์เซ็นเซอร์ pH บนบอร์ด TitraLab (pH Sensor Hardware on TitraLab)
# ==============================================================================
#   - PH_PIN = GPIO25 (ADC input)
#   - วงจร pH ใช้ IC LMC6482 dual op-amp สำหรับปรับสัญญาณ
#   - pH circuit uses LMC6482 dual op-amp for signal conditioning
#   - อินพุตจากขั้วต่อ BNC สำหรับโพรบ pH มาตรฐาน
#   - Input from BNC connector for standard pH probe
#   - มี voltage reference TLV431BQFTA เพื่อความแม่นยำ
#   - Has TLV431BQFTA voltage reference for accuracy
#   - ใช้ไฟเลี้ยง 3.3V สะอาดจาก XC6206P121MR (แยกจากวงจรดิจิทัล)
#   - Clean 3.3V supply from XC6206P121MR (separate from digital)
#
# ==============================================================================
# สมการ Nernst: หลักการทำงานของเซ็นเซอร์ pH (Nernst Equation)
# ==============================================================================
#
#   E = E0 - (2.303 * R * T) / (n * F) * pH
#
#   ที่อุณหภูมิ 25 C (At 25 C):
#   E = E0 - 59.16 mV x pH
#
#   โดยที่ (Where):
#     E  = ศักย์ไฟฟ้าที่วัดได้ (Measured potential, mV)
#     E0 = ศักย์ไฟฟ้ามาตรฐาน (Standard potential, typically ~414 mV at pH 0)
#     R  = ค่าคงที่แก๊ส (Gas constant) = 8.314 J/(mol*K)
#     T  = อุณหภูมิสัมบูรณ์ (Absolute temperature, K)
#     n  = จำนวนอิเล็กตรอน (Number of electrons) = 1
#     F  = ค่าคงที่ฟาราเดย์ (Faraday constant) = 96485 C/mol
#
#   ความชันทฤษฎี = -59.16 mV/pH ที่ 25 C
#   Theoretical slope = -59.16 mV/pH at 25 C
#
#   ตัวอย่าง (Example):
#     pH 7 (กลาง/neutral): E = E0 - 59.16 * 7 = E0 - 414.12 mV
#     pH 4 (กรด/acidic):   E = E0 - 59.16 * 4 = E0 - 236.64 mV
#     pH 10 (เบส/basic):   E = E0 - 59.16 * 10 = E0 - 591.60 mV
#
# ==============================================================================
# อุปกรณ์ที่ใช้ในบทเรียนนี้ (Equipment used in this lesson)
# ==============================================================================
#   - Potentiometer บนบอร์ด TitraLab (GPIO32) จำลองสัญญาณ pH
#   - Potentiometer on TitraLab board (GPIO32) simulates pH signal
#   - (Week 3 จะใช้เซ็นเซอร์ pH จริงที่ GPIO25)
#   - (Week 3 will use real pH sensor at GPIO25)
#
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

from machine import Pin, ADC
import time

# นำเข้าค่าขา GPIO จากไฟล์ pins.py (Import GPIO pins from pins.py)
# หมายเหตุ: ถ้าไม่มีไฟล์ pins.py ให้ใช้ค่าตรงๆ
# Note: If pins.py is not available, use direct values
try:
    from pins import POT1_PIN, PH_PIN
except ImportError:
    POT1_PIN = 32  # GPIO32 - Potentiometer 1 (ใช้ในบทเรียนนี้)
    PH_PIN = 25    # GPIO25 - pH Sensor (ใช้ใน Week 3)

# ==============================================================================
# ค่าคงที่สำหรับ ADC และการแปลงค่า (Constants for ADC and Conversion)
# ==============================================================================

# ค่าพื้นฐานของ ADC (Basic ADC values)
ADC_MAX = 4095       # ค่าสูงสุดของ ADC 12-bit (Max value for 12-bit ADC)
VOLTAGE_MAX = 3.3    # แรงดันสูงสุดที่ ATTN_11DB (Max voltage at ATTN_11DB)

# ค่าคงที่สมการ Nernst ที่ 25 C (Nernst equation constants at 25 C)
NERNST_SLOPE = -59.16  # mV ต่อ pH (mV per pH unit)
                       # ค่าลบเพราะ pH เพิ่ม -> แรงดันลด
                       # Negative because pH increases -> voltage decreases

# ตัวอย่างค่าสอบเทียบ pH (Example pH calibration values)
# หมายเหตุ: ค่าจริงต้องได้จากการสอบเทียบในบทเรียน Week 2
# Note: Real values must come from calibration in Week 2 lesson
EXAMPLE_SLOPE = -0.0058    # ค่า m จากการสอบเทียบ (calibration slope)
EXAMPLE_INTERCEPT = 4.5    # ค่า b จากการสอบเทียบ (calibration intercept)

# ==============================================================================
# การตั้งค่า ADC (ADC Configuration)
# ==============================================================================

# สร้าง ADC object ที่ขา POT1_PIN (GPIO32) สำหรับการเรียนรู้
# Create ADC object at POT1_PIN (GPIO32) for learning
adc = ADC(Pin(POT1_PIN))

# ตั้งค่า attenuation เป็น 11dB เพื่อให้อ่านได้ 0-3.3V
# Set attenuation to 11dB to read 0-3.3V range
#
# ตาราง Attenuation (Attenuation table):
#   ADC.ATTN_0DB   -> 0-1.0V   (ความละเอียดดีที่สุด/best resolution)
#   ADC.ATTN_2_5DB -> 0-1.34V
#   ADC.ATTN_6DB   -> 0-2.0V
#   ADC.ATTN_11DB  -> 0-3.3V   (ใช้กับ pH sensor/used with pH sensor)
#
adc.atten(ADC.ATTN_11DB)

# ==============================================================================
# ฟังก์ชันแปลงค่า ADC (ADC Conversion Functions)
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


def voltage_to_mv(voltage):
    """
    แปลงแรงดัน V เป็น mV (Convert voltage V to mV)

    เซ็นเซอร์ pH ให้สัญญาณในหน่วย mV ตามสมการ Nernst
    pH sensor outputs signal in mV according to Nernst equation

    Args:
        voltage (float): แรงดันในหน่วย V (Voltage in Volts)

    Returns:
        float: แรงดันในหน่วย mV (Voltage in milliVolts)
    """
    return voltage * 1000


def simulate_ph_from_voltage(voltage, slope=EXAMPLE_SLOPE, intercept=EXAMPLE_INTERCEPT):
    """
    จำลองการแปลงแรงดันเป็น pH (Simulate voltage to pH conversion)

    สูตรการแปลง (Conversion formula):
        pH = slope * mV + intercept

    หมายเหตุ: นี่คือการจำลองเท่านั้น!
    Note: This is simulation only!
    ค่าจริงต้องได้จากการสอบเทียบที่ Week 2
    Real values must come from Week 2 calibration

    Args:
        voltage (float): แรงดันจาก ADC (Voltage from ADC)
        slope (float): ความชันจากการสอบเทียบ (Calibration slope)
        intercept (float): ค่าตัดแกนจากการสอบเทียบ (Calibration intercept)

    Returns:
        float: ค่า pH จำลอง (Simulated pH value)
    """
    mv = voltage_to_mv(voltage)
    ph = slope * mv + intercept
    # จำกัดค่า pH ให้อยู่ในช่วงที่เป็นไปได้ (Clamp pH to valid range)
    ph = max(0, min(14, ph))
    return ph


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================

print("=" * 60)
print("บทเรียน ADC สำหรับเซ็นเซอร์ pH (ADC for pH Sensor)")
print("=" * 60)
print()
print("นี่คือพื้นฐานการอ่านค่า pH ที่ใช้ใน Week 3")
print("This is the basis for pH reading used in Week 3")
print()
print("-" * 60)
print("หลักการ Nernst Equation:")
print("-" * 60)
print("  E = E0 - 59.16 mV x pH  (ที่ 25 C)")
print()
print("  ความหมาย (Meaning):")
print("  - pH เพิ่มขึ้น 1 หน่วย -> แรงดันลดลง 59.16 mV")
print("  - pH increases by 1 -> voltage decreases by 59.16 mV")
print()
print("-" * 60)
print("ฮาร์ดแวร์บอร์ด TitraLab:")
print("-" * 60)
print("  pH Sensor Pin: GPIO25 (ADC input)")
print("  วงจร: LMC6482 op-amp + TLV431 voltage reference")
print("  ADC Range: 0-4095 (12-bit), 0-3.3V with ATTN_11DB")
print()
print("-" * 60)
print("การทดลอง:")
print("-" * 60)
print(f"  กำลังอ่านค่าจาก Potentiometer ที่ GPIO{POT1_PIN}")
print(f"  Reading from Potentiometer at GPIO{POT1_PIN}")
print()
print("  หมุน Potentiometer เพื่อจำลองการเปลี่ยนแปลงของ pH")
print("  Turn Potentiometer to simulate pH changes")
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

        # แปลงเป็น mV สำหรับการคำนวณ pH (Convert to mV for pH calculation)
        mv = voltage_to_mv(voltage)

        # จำลองค่า pH (Simulate pH value)
        simulated_ph = simulate_ph_from_voltage(voltage)

        # เพิ่มจำนวนการอ่าน (Increment reading count)
        reading_count += 1

        # แสดงผล (Display results)
        print(f"การอ่านครั้งที่ {reading_count:3d} (Reading #{reading_count:3d})")
        print(f"  ค่าดิบ ADC (Raw ADC)   : {raw_value:4d} / {ADC_MAX}")
        print(f"  แรงดัน (Voltage)       : {voltage:.3f} V = {mv:.1f} mV")
        print(f"  pH จำลอง (Simulated)  : {simulated_ph:.2f}")
        print(f"    [หมายเหตุ: ค่า pH จำลองจาก Potentiometer ไม่ใช่ค่าจริง]")
        print(f"    [Note: Simulated pH from Potentiometer, not real value]")
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
    print("-" * 60)
    print()
    print("1. ADC แปลงแรงดัน analog เป็นตัวเลขดิจิทัล")
    print("   ADC converts analog voltage to digital number")
    print("   - ESP32: 0V -> 0, 3.3V -> 4095 (12-bit)")
    print()
    print("2. สมการ Nernst: E = E0 - 59.16 mV x pH")
    print("   Nernst Equation: E = E0 - 59.16 mV x pH")
    print("   - เซ็นเซอร์ pH ส่งแรงดันตามค่า pH")
    print("   - pH sensor outputs voltage based on pH value")
    print()
    print("3. การแปลงแรงดันเป็น pH:")
    print("   Converting voltage to pH:")
    print("   - voltage = (raw / 4095) * 3.3")
    print("   - mV = voltage * 1000")
    print("   - pH = slope * mV + intercept")
    print()
    print("4. ฮาร์ดแวร์ pH บนบอร์ด TitraLab:")
    print("   pH hardware on TitraLab board:")
    print("   - GPIO25 (ADC input)")
    print("   - LMC6482 op-amp สำหรับปรับสัญญาณ")
    print("   - TLV431 voltage reference สำหรับความแม่นยำ")
    print()
    print("-" * 60)
    print("ขั้นตอนต่อไป (Next Steps):")
    print("-" * 60)
    print("  Week 2: การสอบเทียบ pH (pH Calibration)")
    print("          - หาค่า slope และ intercept จริง")
    print("          - Find real slope and intercept values")
    print()
    print("  Week 3: การไทเทรชันอัตโนมัติ (Automatic Titration)")
    print("          - ใช้ค่า pH ควบคุมปั๊ม")
    print("          - Use pH value to control pump")
    print()
    print("ต่อไป: 02_adc_averaging.py (การเฉลี่ยค่าเพื่อลด noise)")
    print("Next: 02_adc_averaging.py (Averaging to reduce noise)")
    print("=" * 60)

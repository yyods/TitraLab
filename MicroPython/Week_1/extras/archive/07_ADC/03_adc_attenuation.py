# ==============================================================================
# 03_adc_attenuation.py - การตั้งค่า ADC Attenuation (ADC Attenuation Settings)
# ==============================================================================
# โปรแกรมนี้อธิบายการตั้งค่า ADC attenuation บน ESP32
# This program explains ADC attenuation settings on ESP32
#
# Attenuation คืออะไร? (What is Attenuation?)
#   - Attenuation กำหนดช่วงแรงดันที่ ADC สามารถอ่านได้
#   - Attenuation determines the voltage range that ADC can read
#   - ESP32 มี 4 ระดับ attenuation ให้เลือก
#   - ESP32 has 4 attenuation levels to choose from
#
# ตาราง Attenuation (Attenuation Table):
#   +-------------+----------------+------------------------+
#   | Attenuation | ช่วงแรงดัน     | การใช้งาน              |
#   | Setting     | Voltage Range  | Use Case               |
#   +-------------+----------------+------------------------+
#   | ATTN_0DB    | 0 - 1.1V       | เซ็นเซอร์แรงดันต่ำ      |
#   | ATTN_2_5DB  | 0 - 1.5V       | Low voltage sensor     |
#   | ATTN_6DB    | 0 - 2.2V       | Medium voltage         |
#   | ATTN_11DB   | 0 - 3.3V       | pH sensor, Pot (ใช้บ่อย)|
#   +-------------+----------------+------------------------+
#
# ทำไม pH Sensor ใช้ ATTN_11DB? (Why ATTN_11DB for pH Sensor?)
#   - pH sensor ส่งออกแรงดัน 0-3.3V (ขึ้นกับรุ่น)
#   - pH sensor outputs 0-3.3V (depends on model)
#   - ATTN_11DB ให้ช่วงกว้างที่สุด (0-3.3V)
#   - ATTN_11DB gives widest range (0-3.3V)
#   - ครอบคลุมทุกค่า pH ที่เป็นไปได้
#   - Covers all possible pH values
#
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

from machine import Pin, ADC
import time

# นำเข้าค่าขา GPIO จากไฟล์ pins.py (Import GPIO pins from pins.py)
try:
    from pins import POT1_PIN, POT2_PIN
except ImportError:
    POT1_PIN = 32  # GPIO32 - Potentiometer 1
    POT2_PIN = 33  # GPIO33 - Potentiometer 2

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================

ADC_MAX = 4095  # ค่าสูงสุดของ ADC 12-bit (Max value for 12-bit ADC)

# ตาราง Attenuation และช่วงแรงดัน (Attenuation and voltage range table)
# คู่: (ค่า attenuation, ชื่อ, แรงดันสูงสุด)
# Tuple: (attenuation value, name, max voltage)
ATTENUATION_TABLE = [
    (ADC.ATTN_0DB,   "ATTN_0DB",   1.1),
    (ADC.ATTN_2_5DB, "ATTN_2_5DB", 1.5),
    (ADC.ATTN_6DB,   "ATTN_6DB",   2.2),
    (ADC.ATTN_11DB,  "ATTN_11DB",  3.3),
]

# ==============================================================================
# สร้าง ADC object (Create ADC object)
# ==============================================================================

# ใช้ POT1_PIN (GPIO32) สำหรับทดสอบ
# Use POT1_PIN (GPIO32) for testing
adc = ADC(Pin(POT1_PIN))

# ==============================================================================
# ฟังก์ชันอ่านค่าและแปลงเป็นแรงดัน (Function to read and convert to voltage)
# ==============================================================================

def read_voltage(voltage_max):
    """
    อ่านค่า ADC และแปลงเป็นแรงดัน (Read ADC and convert to voltage)

    สูตร (Formula):
        voltage = (raw_value / 4095) * voltage_max

    Args:
        voltage_max (float): แรงดันสูงสุดตาม attenuation ที่ตั้ง
                            Max voltage based on attenuation setting

    Returns:
        tuple: (raw_value, voltage)
               raw_value: ค่าดิบ 0-4095
               voltage: แรงดันที่คำนวณได้
    """
    raw_value = adc.read()
    voltage = (raw_value / ADC_MAX) * voltage_max
    return raw_value, voltage

# ==============================================================================
# ฟังก์ชันอ่านค่าเฉลี่ย (Function to read averaged value)
# ==============================================================================

def read_averaged(num_samples, voltage_max):
    """
    อ่านค่าเฉลี่ยจากหลายตัวอย่าง (Read averaged value from multiple samples)

    Args:
        num_samples (int): จำนวนตัวอย่าง (number of samples)
        voltage_max (float): แรงดันสูงสุดตาม attenuation

    Returns:
        tuple: (avg_raw, avg_voltage)
    """
    total = 0
    for _ in range(num_samples):
        total += adc.read()
        time.sleep_ms(5)

    avg_raw = total // num_samples
    avg_voltage = (avg_raw / ADC_MAX) * voltage_max
    return avg_raw, avg_voltage

# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================

print("=" * 60)
print("บทเรียน ADC Attenuation (ADC Attenuation Lesson)")
print("=" * 60)
print()
print("Attenuation คืออะไร? (What is Attenuation?)")
print("-" * 40)
print("  - กำหนดช่วงแรงดันที่ ADC อ่านได้")
print("  - Determines voltage range ADC can read")
print("  - ESP32 มี 4 ระดับ attenuation")
print("  - ESP32 has 4 attenuation levels")
print()
print("ตาราง Attenuation (Attenuation Table):")
print("-" * 40)
print("  +-------------+----------------+")
print("  | Attenuation | ช่วงแรงดัน     |")
print("  | Setting     | Voltage Range  |")
print("  +-------------+----------------+")
print("  | ATTN_0DB    | 0 - 1.1V       |")
print("  | ATTN_2_5DB  | 0 - 1.5V       |")
print("  | ATTN_6DB    | 0 - 2.2V       |")
print("  | ATTN_11DB   | 0 - 3.3V       | <-- pH sensor ใช้อันนี้!")
print("  +-------------+----------------+")
print()
print("ทำไม pH Sensor ใช้ ATTN_11DB? (Why ATTN_11DB for pH?)")
print("-" * 40)
print("  - pH sensor ส่งแรงดัน 0-3V (ขึ้นกับรุ่น)")
print("  - pH sensor outputs 0-3V (depends on model)")
print("  - ATTN_11DB ครอบคลุมทุกค่าที่เป็นไปได้")
print("  - ATTN_11DB covers all possible values")
print()
print(f"กำลังใช้ Potentiometer ที่ GPIO{POT1_PIN}")
print(f"(Using Potentiometer at GPIO{POT1_PIN})")
print()
print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
print("=" * 60)
print()

try:
    # ตัวแปรสำหรับเก็บ attenuation ปัจจุบัน (Current attenuation index)
    current_atten_index = 3  # เริ่มที่ ATTN_11DB (Start with ATTN_11DB)

    # ตัวแปรนับรอบ (Iteration counter)
    iteration = 0

    while True:
        iteration += 1

        print(f"--- รอบที่ {iteration} (Iteration {iteration}) ---")
        print()

        # ===== แสดงการอ่านค่าจากทุก attenuation =====
        # Show readings from all attenuations
        print("เปรียบเทียบทุก Attenuation (Comparing all Attenuations):")
        print("-" * 50)
        print(f"  {'Attenuation':<12} {'ช่วง':>8} {'Raw':>6} {'Voltage':>10} {'หมายเหตุ':<15}")
        print(f"  {'':12} {'Range':>8} {'':>6} {'':>10} {'Note':<15}")
        print(f"  {'-'*12} {'-'*8} {'-'*6} {'-'*10} {'-'*15}")

        for atten, name, v_max in ATTENUATION_TABLE:
            # ตั้งค่า attenuation (Set attenuation)
            adc.atten(atten)

            # รอให้ ADC เสถียร (Wait for ADC to stabilize)
            time.sleep_ms(50)

            # อ่านค่าเฉลี่ย (Read averaged value)
            raw, voltage = read_averaged(10, v_max)

            # กำหนดหมายเหตุ (Set note)
            note = ""
            if raw >= ADC_MAX - 100:
                note = "อิ่มตัว! (Saturated!)"
            elif name == "ATTN_11DB":
                note = "<- pH sensor"

            # แสดงผล (Display)
            print(f"  {name:<12} {'0-'+str(v_max)+'V':>8} {raw:>6} {voltage:>10.3f} {note:<15}")

        print()

        # ===== คำอธิบายเพิ่มเติม (Additional explanation) =====
        print("การตีความ (Interpretation):")
        print("-" * 40)
        print("  - ถ้า Raw ใกล้ 4095 = อิ่มตัว (saturated)")
        print("  - If Raw near 4095 = saturated")
        print("  - ต้องเลือก attenuation ที่ให้ช่วงกว้างพอ")
        print("  - Choose attenuation with wide enough range")
        print()

        # ===== เน้นย้ำ ATTN_11DB (Emphasize ATTN_11DB) =====
        adc.atten(ADC.ATTN_11DB)
        time.sleep_ms(50)
        raw_11db, volt_11db = read_averaged(20, 3.3)

        print("สำหรับ pH Sensor (For pH Sensor):")
        print("-" * 40)
        print(f"  แนะนำ: ATTN_11DB (0-3.3V)")
        print(f"  Recommended: ATTN_11DB (0-3.3V)")
        print(f"  ค่าปัจจุบัน (Current value):")
        print(f"    Raw     : {raw_11db}")
        print(f"    Voltage : {volt_11db:.3f} V")
        print()

        # ===== การประยุกต์ใช้ (Application preview) =====
        print("การประยุกต์ใช้ใน Week 2 (Application in Week 2):")
        print("-" * 40)
        print("  1. ตั้งค่า ADC ด้วย ATTN_11DB")
        print("     Set ADC with ATTN_11DB")
        print("  2. อ่านค่าเฉลี่ยจาก pH sensor")
        print("     Read averaged value from pH sensor")
        print("  3. แปลงแรงดันเป็นค่า pH ด้วย calibration")
        print("     Convert voltage to pH using calibration")
        print()

        # หน่วงเวลา 4 วินาที (Delay 4 seconds)
        print("รอ 4 วินาที... หมุน Potentiometer เพื่อดูการเปลี่ยนแปลง")
        print("(Waiting 4 seconds... Turn Potentiometer to see changes)")
        print()
        time.sleep(4)

except KeyboardInterrupt:
    # เมื่อกด Ctrl+C (When Ctrl+C is pressed)
    print("\n" + "=" * 60)
    print("หยุดโปรแกรม (Program stopped)")
    print("=" * 60)
    print()
    print("สรุปสิ่งที่เรียนรู้ (What you learned):")
    print("-" * 40)
    print()
    print("1. Attenuation คืออะไร (What is Attenuation):")
    print("   - กำหนดช่วงแรงดันที่ ADC อ่านได้")
    print("   - Determines readable voltage range")
    print()
    print("2. ตาราง Attenuation (Attenuation Table):")
    print("   - ATTN_0DB   : 0 - 1.1V")
    print("   - ATTN_2_5DB : 0 - 1.5V")
    print("   - ATTN_6DB   : 0 - 2.2V")
    print("   - ATTN_11DB  : 0 - 3.3V (แนะนำสำหรับ TitraLab)")
    print()
    print("3. ทำไม ATTN_11DB สำหรับ pH? (Why ATTN_11DB for pH?):")
    print("   - pH sensor ส่งแรงดัน 0-3V")
    print("   - pH sensor outputs 0-3V")
    print("   - ATTN_11DB ครอบคลุมทุกค่า")
    print("   - ATTN_11DB covers all values")
    print()
    print("4. ข้อควรระวัง (Caution):")
    print("   - ถ้า Raw ใกล้ 4095 = อิ่มตัว")
    print("   - If Raw near 4095 = saturated")
    print("   - เลือก attenuation ให้เหมาะกับเซ็นเซอร์")
    print("   - Choose attenuation suitable for sensor")
    print()
    print("=" * 60)
    print("เตรียมพร้อมสำหรับ Week 2! (Ready for Week 2!)")
    print("=" * 60)
    print()
    print("ใน Week 2 คุณจะได้:")
    print("(In Week 2 you will:)")
    print("  - ใช้ ADC อ่านค่าจาก pH sensor จริง")
    print("    Use ADC to read real pH sensor")
    print("  - Calibrate pH sensor ด้วย buffer solutions")
    print("    Calibrate pH sensor with buffer solutions")
    print("  - แปลง voltage เป็นค่า pH")
    print("    Convert voltage to pH value")
    print()
    print("ความรู้ที่ได้จากบทเรียน ADC นี้คือพื้นฐานสำคัญ!")
    print("(Knowledge from this ADC lesson is essential foundation!)")
    print("=" * 60)

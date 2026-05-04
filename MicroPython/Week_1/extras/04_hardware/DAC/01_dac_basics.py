# ==============================================================================
# 01_dac_basics.py - พื้นฐาน DAC (Digital-to-Analog Converter Basics)
# ==============================================================================
# [Optional/เสริม] - เนื้อหาเสริม ไม่จำเป็นต้องใช้ในหลักสูตรหลัก
# This is supplementary material - not required for the main curriculum
# ==============================================================================
# DAC คืออะไร? (What is DAC?)
#
# DAC (Digital-to-Analog Converter) แปลงค่าดิจิทัล (0-255) เป็นแรงดันไฟฟ้า (0-3.3V)
# เป็นการทำงานตรงข้ามกับ ADC (Analog-to-Digital Converter)
#
# DAC converts digital values (0-255) to analog voltage (0-3.3V)
# This is the opposite of ADC (Analog-to-Digital Converter)
#
# ESP32 มี DAC 2 ช่อง (ESP32 has 2 DAC channels):
#   - GPIO25 (DAC1) - ใช้กับ pH Sensor ในบอร์ด TitraLab
#   - GPIO26 (DAC2) - ใช้กับ Buzzer ในบอร์ด TitraLab
#
# ในตัวอย่างนี้ใช้ GPIO26 เพื่อหลีกเลี่ยงการรบกวนเซ็นเซอร์ pH
# This example uses GPIO26 to avoid interfering with the pH sensor
# ==============================================================================
# การเปรียบเทียบ ADC vs DAC (Comparison ADC vs DAC):
#
#   ADC: แรงดันไฟฟ้า (0-3.3V) --> ค่าดิจิทัล (0-4095 สำหรับ 12-bit)
#        Voltage (0-3.3V) --> Digital value (0-4095 for 12-bit)
#
#   DAC: ค่าดิจิทัล (0-255) --> แรงดันไฟฟ้า (0-3.3V)
#        Digital value (0-255) --> Voltage (0-3.3V)
#
# สูตรคำนวณ (Calculation formula):
#   Voltage = (DAC_value / 255) * 3.3V
#
#   ตัวอย่าง (Examples):
#   - DAC = 0    --> 0V
#   - DAC = 127  --> 1.64V (ประมาณกึ่งกลาง/approximately half)
#   - DAC = 255  --> 3.3V
# ==============================================================================

from machine import DAC, Pin
import time

# === การกำหนดค่าคงที่ (Constants) ===
# ใช้ GPIO26 สำหรับ DAC (ขา BUZZER_PIN ในบอร์ด TitraLab)
# Using GPIO26 for DAC (BUZZER_PIN on TitraLab board)
DAC_PIN = 26

# === สร้าง DAC object (Create DAC object) ===
# DAC บน ESP32 มี resolution 8-bit (ค่า 0-255)
# ESP32 DAC has 8-bit resolution (values 0-255)
dac = DAC(Pin(DAC_PIN))

def calculate_voltage(dac_value):
    """
    คำนวณแรงดันไฟฟ้าจากค่า DAC (Calculate voltage from DAC value)

    Args:
        dac_value: ค่า DAC (0-255) / DAC value (0-255)

    Returns:
        float: แรงดันไฟฟ้าเป็นโวลต์ (Voltage in Volts)
    """
    return (dac_value / 255) * 3.3


def demo_voltage_levels():
    """
    สาธิตระดับแรงดันไฟฟ้าต่างๆ (Demonstrate different voltage levels)

    ถ้ามี Oscilloscope หรือ Multimeter สามารถวัดแรงดันที่ GPIO26 ได้
    If you have an Oscilloscope or Multimeter, you can measure voltage at GPIO26
    """
    print("=" * 50)
    print("สาธิตระดับแรงดัน DAC (DAC Voltage Level Demo)")
    print("=" * 50)
    print()
    print("ใช้ Multimeter วัดแรงดันที่ GPIO26")
    print("Use Multimeter to measure voltage at GPIO26")
    print()

    # ค่า DAC ที่จะทดสอบ (DAC values to test)
    test_values = [0, 64, 128, 192, 255]

    for dac_value in test_values:
        # กำหนดค่า DAC (Set DAC value)
        dac.write(dac_value)

        # คำนวณแรงดันทฤษฎี (Calculate theoretical voltage)
        voltage = calculate_voltage(dac_value)

        # แสดงผล (Display results)
        print(f"DAC = {dac_value:3d}  -->  แรงดันทฤษฎี (Theory): {voltage:.2f}V")

        # รอให้ผู้ใช้วัดค่า (Wait for user to measure)
        time.sleep(2)

    print()
    print("จบการสาธิต (Demo completed)")


def demo_voltage_ramp():
    """
    สาธิตการเพิ่มแรงดันแบบค่อยๆ เพิ่มขึ้น (Demonstrate gradual voltage increase)

    แรงดันจะเพิ่มจาก 0V ไปถึง 3.3V แบบ smooth
    Voltage increases smoothly from 0V to 3.3V
    """
    print("=" * 50)
    print("สาธิตการเพิ่มแรงดันแบบ Ramp (Voltage Ramp Demo)")
    print("=" * 50)
    print()
    print("กำลังเพิ่มแรงดันจาก 0V ไปถึง 3.3V...")
    print("Ramping voltage from 0V to 3.3V...")
    print()

    # เพิ่มค่า DAC จาก 0 ไป 255 (Increase DAC from 0 to 255)
    for dac_value in range(256):
        dac.write(dac_value)

        # แสดงความก้าวหน้าทุก 32 ค่า (Show progress every 32 values)
        if dac_value % 32 == 0:
            voltage = calculate_voltage(dac_value)
            print(f"DAC = {dac_value:3d}  -->  {voltage:.2f}V")

        # หน่วงเวลาเล็กน้อย (Small delay)
        time.sleep(0.02)

    print()
    print("ถึงค่าสูงสุดแล้ว! (Reached maximum!)")

    # รอสักครู่แล้วลดกลับเป็น 0 (Wait then ramp back to 0)
    time.sleep(1)

    print()
    print("กำลังลดแรงดันกลับเป็น 0V...")
    print("Ramping voltage back to 0V...")
    print()

    for dac_value in range(255, -1, -1):
        dac.write(dac_value)

        if dac_value % 32 == 0:
            voltage = calculate_voltage(dac_value)
            print(f"DAC = {dac_value:3d}  -->  {voltage:.2f}V")

        time.sleep(0.02)

    print()
    print("กลับสู่ 0V แล้ว (Back to 0V)")


def demo_manual_control():
    """
    ให้ผู้ใช้ป้อนค่า DAC เพื่อควบคุมแรงดัน (Manual DAC control)

    พิมพ์ค่า 0-255 เพื่อกำหนดแรงดัน หรือ 'q' เพื่อออก
    Enter values 0-255 to set voltage, or 'q' to quit
    """
    print("=" * 50)
    print("ควบคุมแรงดัน DAC ด้วยตนเอง (Manual DAC Control)")
    print("=" * 50)
    print()
    print("พิมพ์ค่า 0-255 เพื่อกำหนดแรงดัน")
    print("Enter values 0-255 to set voltage")
    print("พิมพ์ 'q' เพื่อออก / Type 'q' to quit")
    print()

    while True:
        try:
            user_input = input("DAC value (0-255): ")

            # ตรวจสอบคำสั่งออก (Check for quit command)
            if user_input.lower() == 'q':
                print("ออกจากโหมดควบคุมด้วยตนเอง (Exiting manual control)")
                break

            # แปลงเป็นตัวเลข (Convert to number)
            dac_value = int(user_input)

            # ตรวจสอบช่วงค่า (Validate range)
            if 0 <= dac_value <= 255:
                dac.write(dac_value)
                voltage = calculate_voltage(dac_value)
                print(f"  --> กำหนดแรงดัน: {voltage:.2f}V (Set voltage: {voltage:.2f}V)")
            else:
                print("  --> ข้อผิดพลาด: ค่าต้องอยู่ระหว่าง 0-255")
                print("      Error: Value must be between 0-255")

        except ValueError:
            print("  --> ข้อผิดพลาด: กรุณาป้อนตัวเลข 0-255 หรือ 'q'")
            print("      Error: Please enter a number 0-255 or 'q'")


# === โปรแกรมหลัก (Main Program) ===
if __name__ == "__main__":
    try:
        print()
        print("=" * 60)
        print("  DAC พื้นฐาน - Digital-to-Analog Converter Basics")
        print("  [Optional/เสริม]")
        print("=" * 60)
        print()
        print(f"ใช้ขา GPIO{DAC_PIN} สำหรับ DAC output")
        print(f"Using GPIO{DAC_PIN} for DAC output")
        print()

        # เมนูเลือกการสาธิต (Demo selection menu)
        print("เลือกการสาธิต (Select demo):")
        print("  1. ระดับแรงดันต่างๆ (Voltage levels)")
        print("  2. เพิ่ม-ลดแรงดันแบบ Ramp (Voltage ramp)")
        print("  3. ควบคุมด้วยตนเอง (Manual control)")
        print()

        choice = input("เลือก (Choose) 1-3: ")
        print()

        if choice == '1':
            demo_voltage_levels()
        elif choice == '2':
            demo_voltage_ramp()
        elif choice == '3':
            demo_manual_control()
        else:
            print("ตัวเลือกไม่ถูกต้อง รันการสาธิต Ramp เป็นค่าเริ่มต้น")
            print("Invalid choice. Running Ramp demo as default")
            demo_voltage_ramp()

    except KeyboardInterrupt:
        # หยุดโปรแกรมด้วย Ctrl+C (Stop with Ctrl+C)
        print("\n")
        print("หยุดโปรแกรมด้วย Ctrl+C (Program stopped with Ctrl+C)")

    finally:
        # ทำความสะอาด - ตั้งค่า DAC เป็น 0 (Cleanup - set DAC to 0)
        dac.write(0)
        print("ตั้งค่า DAC เป็น 0V แล้ว (DAC set to 0V)")
        print()

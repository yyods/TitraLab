# ==============================================================================
# 02_dac_waveform.py - สร้างคลื่นสัญญาณด้วย DAC (Generate Waveforms with DAC)
# ==============================================================================
# [Optional/เสริม] - เนื้อหาเสริม ไม่จำเป็นต้องใช้ในหลักสูตรหลัก
# This is supplementary material - not required for the main curriculum
# ==============================================================================
# โปรแกรมนี้สาธิตการสร้างคลื่นสัญญาณต่างๆ ด้วย DAC:
# This program demonstrates generating various waveforms with DAC:
#
#   1. คลื่นฟันเลื่อย (Sawtooth wave) - แรงดันเพิ่มขึ้นเรื่อยๆ แล้วตกลงทันที
#   2. คลื่นสามเหลี่ยม (Triangle wave) - แรงดันเพิ่มขึ้นแล้วลดลงอย่างสม่ำเสมอ
#   3. คลื่นไซน์ (Sine wave) - คลื่นรูปไซน์เหมือนคลื่นในธรรมชาติ
#
# การประยุกต์ใช้ในเคมี (Chemistry applications):
#   - สร้างสัญญาณกระตุ้นสำหรับเซ็นเซอร์
#   - ทดสอบระบบวัดสัญญาณ
#   - สร้างสัญญาณอ้างอิงสำหรับการสอบเทียบ
# ==============================================================================
# วิธีดูคลื่นสัญญาณ (How to view the waveform):
#
#   1. ต่อ Oscilloscope ที่ GPIO26 และ GND
#      Connect Oscilloscope to GPIO26 and GND
#
#   2. หรือต่อ LED + ตัวต้านทาน 330 ohm ที่ GPIO26
#      Or connect LED + 330 ohm resistor to GPIO26
#      (LED จะค่อยๆ สว่างขึ้น-มืดลง / LED will gradually brighten and dim)
# ==============================================================================

from machine import DAC, Pin
import math
import time

# === การกำหนดค่าคงที่ (Constants) ===
# ใช้ GPIO26 สำหรับ DAC (ขา BUZZER_PIN ในบอร์ด TitraLab)
# Using GPIO26 for DAC (BUZZER_PIN on TitraLab board)
DAC_PIN = 26

# จำนวนจุดข้อมูลในหนึ่งรอบ (Number of samples per cycle)
SAMPLES_PER_CYCLE = 256

# === สร้าง DAC object (Create DAC object) ===
dac = DAC(Pin(DAC_PIN))

# === ตาราง Lookup สำหรับคลื่นไซน์ (Sine wave lookup table) ===
# สร้างตารางล่วงหน้าเพื่อให้ทำงานเร็วขึ้น (Pre-calculate for faster execution)
# คำนวณค่า sine แล้วแปลงเป็นช่วง 0-255 (Calculate sine and scale to 0-255)
sine_table = []
for i in range(SAMPLES_PER_CYCLE):
    # math.sin ให้ค่า -1 ถึง 1 แปลงเป็น 0-255
    # math.sin returns -1 to 1, convert to 0-255
    angle = 2 * math.pi * i / SAMPLES_PER_CYCLE
    value = int((math.sin(angle) + 1) * 127.5)
    sine_table.append(value)


def generate_sawtooth(frequency_hz=1, duration_sec=5):
    """
    สร้างคลื่นฟันเลื่อย (Generate sawtooth wave)

    คลื่นฟันเลื่อยมีลักษณะ: แรงดันเพิ่มจาก 0 ไป 3.3V แล้วตกลงทันที
    Sawtooth wave: voltage rises from 0 to 3.3V then drops instantly

    Args:
        frequency_hz: ความถี่ในหน่วย Hz (Frequency in Hz)
        duration_sec: ระยะเวลาในหน่วยวินาที (Duration in seconds)
    """
    print(f"คลื่นฟันเลื่อย (Sawtooth wave): {frequency_hz} Hz")
    print(f"ระยะเวลา (Duration): {duration_sec} วินาที (seconds)")
    print()

    # คำนวณ delay ต่อ sample (Calculate delay per sample)
    # delay = 1 / (frequency * samples_per_cycle)
    delay_us = int(1_000_000 / (frequency_hz * SAMPLES_PER_CYCLE))

    # จำนวนรอบทั้งหมด (Total number of cycles)
    total_cycles = int(frequency_hz * duration_sec)

    for cycle in range(total_cycles):
        for i in range(SAMPLES_PER_CYCLE):
            # ค่า DAC เพิ่มขึ้นเป็นเส้นตรงจาก 0 ถึง 255
            # DAC value increases linearly from 0 to 255
            dac.write(i)
            time.sleep_us(delay_us)

        # แสดงความก้าวหน้า (Show progress)
        if (cycle + 1) % max(1, total_cycles // 5) == 0:
            print(f"  รอบที่ (Cycle): {cycle + 1}/{total_cycles}")


def generate_triangle(frequency_hz=1, duration_sec=5):
    """
    สร้างคลื่นสามเหลี่ยม (Generate triangle wave)

    คลื่นสามเหลี่ยมมีลักษณะ: แรงดันเพิ่มจาก 0 ไป 3.3V แล้วลดลงเป็น 0 อย่างสม่ำเสมอ
    Triangle wave: voltage rises to 3.3V then falls back to 0 symmetrically

    Args:
        frequency_hz: ความถี่ในหน่วย Hz (Frequency in Hz)
        duration_sec: ระยะเวลาในหน่วยวินาที (Duration in seconds)
    """
    print(f"คลื่นสามเหลี่ยม (Triangle wave): {frequency_hz} Hz")
    print(f"ระยะเวลา (Duration): {duration_sec} วินาที (seconds)")
    print()

    # คำนวณ delay ต่อ sample (Calculate delay per sample)
    # สำหรับคลื่นสามเหลี่ยม มี 2 ส่วน (ขึ้นและลง) ต่อรอบ
    # For triangle wave, there are 2 parts (up and down) per cycle
    samples_total = SAMPLES_PER_CYCLE * 2
    delay_us = int(1_000_000 / (frequency_hz * samples_total))

    # จำนวนรอบทั้งหมด (Total number of cycles)
    total_cycles = int(frequency_hz * duration_sec)

    for cycle in range(total_cycles):
        # ส่วนขาขึ้น: 0 -> 255 (Rising edge: 0 -> 255)
        for i in range(SAMPLES_PER_CYCLE):
            dac.write(i)
            time.sleep_us(delay_us)

        # ส่วนขาลง: 255 -> 0 (Falling edge: 255 -> 0)
        for i in range(SAMPLES_PER_CYCLE - 1, -1, -1):
            dac.write(i)
            time.sleep_us(delay_us)

        # แสดงความก้าวหน้า (Show progress)
        if (cycle + 1) % max(1, total_cycles // 5) == 0:
            print(f"  รอบที่ (Cycle): {cycle + 1}/{total_cycles}")


def generate_sine(frequency_hz=1, duration_sec=5):
    """
    สร้างคลื่นไซน์ (Generate sine wave)

    คลื่นไซน์เป็นคลื่นที่พบมากในธรรมชาติ เช่น คลื่นเสียง คลื่นแสง
    Sine wave is commonly found in nature, such as sound waves, light waves

    Args:
        frequency_hz: ความถี่ในหน่วย Hz (Frequency in Hz)
        duration_sec: ระยะเวลาในหน่วยวินาที (Duration in seconds)
    """
    print(f"คลื่นไซน์ (Sine wave): {frequency_hz} Hz")
    print(f"ระยะเวลา (Duration): {duration_sec} วินาที (seconds)")
    print()

    # คำนวณ delay ต่อ sample (Calculate delay per sample)
    delay_us = int(1_000_000 / (frequency_hz * SAMPLES_PER_CYCLE))

    # จำนวนรอบทั้งหมด (Total number of cycles)
    total_cycles = int(frequency_hz * duration_sec)

    for cycle in range(total_cycles):
        for i in range(SAMPLES_PER_CYCLE):
            # ใช้ตาราง lookup แทนการคำนวณ sine ทุกครั้ง (เร็วกว่า)
            # Use lookup table instead of calculating sine each time (faster)
            dac.write(sine_table[i])
            time.sleep_us(delay_us)

        # แสดงความก้าวหน้า (Show progress)
        if (cycle + 1) % max(1, total_cycles // 5) == 0:
            print(f"  รอบที่ (Cycle): {cycle + 1}/{total_cycles}")


def generate_staircase(steps=8, duration_sec=5):
    """
    สร้างคลื่นขั้นบันได (Generate staircase wave)

    คลื่นขั้นบันไดมีลักษณะ: แรงดันเพิ่มขึ้นเป็นขั้นๆ
    ใช้สำหรับทดสอบการตอบสนองของระบบ หรือสอบเทียบ ADC
    Staircase wave: voltage increases in discrete steps
    Used for testing system response or ADC calibration

    Args:
        steps: จำนวนขั้น (Number of steps)
        duration_sec: ระยะเวลาในหน่วยวินาที (Duration in seconds)
    """
    print(f"คลื่นขั้นบันได (Staircase wave): {steps} ขั้น (steps)")
    print(f"ระยะเวลา (Duration): {duration_sec} วินาที (seconds)")
    print()

    # คำนวณค่า DAC สำหรับแต่ละขั้น (Calculate DAC value for each step)
    step_values = [int(255 * i / (steps - 1)) for i in range(steps)]

    # เวลาต่อขั้น (Time per step)
    time_per_step = duration_sec / steps

    print("ค่า DAC ในแต่ละขั้น (DAC values for each step):")
    for i, value in enumerate(step_values):
        voltage = (value / 255) * 3.3
        dac.write(value)
        print(f"  ขั้นที่ (Step) {i + 1}: DAC = {value:3d}  ({voltage:.2f}V)")
        time.sleep(time_per_step)


def visualize_waveform_text(waveform_type="sine", cycles=2):
    """
    แสดงรูปคลื่นแบบ ASCII (Display waveform as ASCII art)

    ใช้สำหรับทำความเข้าใจรูปร่างของคลื่นโดยไม่ต้องใช้ Oscilloscope
    Use for understanding waveform shapes without Oscilloscope

    Args:
        waveform_type: ชนิดของคลื่น (sine, triangle, sawtooth)
        cycles: จำนวนรอบที่จะแสดง (Number of cycles to display)
    """
    print()
    print(f"รูปคลื่น {waveform_type} ({cycles} รอบ/cycles):")
    print()

    width = 60  # ความกว้างของกราฟ (Graph width)
    height = 10  # ความสูงของกราฟ (Graph height)

    # สร้างข้อมูลคลื่น (Generate waveform data)
    samples = width
    data = []

    for i in range(samples):
        phase = (i / samples) * cycles * 2 * math.pi

        if waveform_type == "sine":
            # คลื่นไซน์ (Sine wave)
            value = (math.sin(phase) + 1) / 2
        elif waveform_type == "triangle":
            # คลื่นสามเหลี่ยม (Triangle wave)
            phase_normalized = (i / samples * cycles) % 1
            if phase_normalized < 0.5:
                value = phase_normalized * 2
            else:
                value = 2 - phase_normalized * 2
        elif waveform_type == "sawtooth":
            # คลื่นฟันเลื่อย (Sawtooth wave)
            value = (i / samples * cycles) % 1
        else:
            value = 0

        data.append(value)

    # วาดกราฟ ASCII (Draw ASCII graph)
    for row in range(height, -1, -1):
        threshold = row / height
        line = ""
        for col in range(samples):
            if abs(data[col] - threshold) < 0.1:
                line += "*"
            elif data[col] >= threshold:
                line += "|" if row == 0 else " "
            else:
                line += " "

        # แสดงสเกลแรงดัน (Show voltage scale)
        voltage = (row / height) * 3.3
        print(f"{voltage:4.1f}V |{line}")

    # แสดงแกนเวลา (Show time axis)
    print("      +" + "-" * samples)
    print("       เวลา (Time) -->")
    print()


# === โปรแกรมหลัก (Main Program) ===
if __name__ == "__main__":
    try:
        print()
        print("=" * 60)
        print("  สร้างคลื่นสัญญาณด้วย DAC (Generate Waveforms with DAC)")
        print("  [Optional/เสริม]")
        print("=" * 60)
        print()
        print(f"ใช้ขา GPIO{DAC_PIN} สำหรับ DAC output")
        print(f"Using GPIO{DAC_PIN} for DAC output")
        print()
        print("ต่อ Oscilloscope หรือ LED+resistor ที่ GPIO26 เพื่อดูสัญญาณ")
        print("Connect Oscilloscope or LED+resistor to GPIO26 to view signal")
        print()

        # เมนูเลือกคลื่น (Waveform selection menu)
        print("เลือกชนิดคลื่น (Select waveform type):")
        print("  1. คลื่นฟันเลื่อย (Sawtooth wave)")
        print("  2. คลื่นสามเหลี่ยม (Triangle wave)")
        print("  3. คลื่นไซน์ (Sine wave)")
        print("  4. คลื่นขั้นบันได (Staircase wave)")
        print("  5. ดูตัวอย่างรูปคลื่นแบบ ASCII (View ASCII waveform preview)")
        print()

        choice = input("เลือก (Choose) 1-5: ")
        print()

        if choice == '1':
            visualize_waveform_text("sawtooth", 2)
            input("กด Enter เพื่อเริ่มสร้างสัญญาณ (Press Enter to start)...")
            generate_sawtooth(frequency_hz=1, duration_sec=10)

        elif choice == '2':
            visualize_waveform_text("triangle", 2)
            input("กด Enter เพื่อเริ่มสร้างสัญญาณ (Press Enter to start)...")
            generate_triangle(frequency_hz=1, duration_sec=10)

        elif choice == '3':
            visualize_waveform_text("sine", 2)
            input("กด Enter เพื่อเริ่มสร้างสัญญาณ (Press Enter to start)...")
            generate_sine(frequency_hz=1, duration_sec=10)

        elif choice == '4':
            generate_staircase(steps=8, duration_sec=16)

        elif choice == '5':
            print("แสดงตัวอย่างรูปคลื่นทั้งหมด:")
            print("Showing all waveform previews:")
            print()
            visualize_waveform_text("sawtooth", 2)
            visualize_waveform_text("triangle", 2)
            visualize_waveform_text("sine", 2)

        else:
            print("ตัวเลือกไม่ถูกต้อง รันคลื่นไซน์เป็นค่าเริ่มต้น")
            print("Invalid choice. Running sine wave as default")
            visualize_waveform_text("sine", 2)
            generate_sine(frequency_hz=1, duration_sec=10)

        print()
        print("เสร็จสิ้น! (Completed!)")

    except KeyboardInterrupt:
        # หยุดโปรแกรมด้วย Ctrl+C (Stop with Ctrl+C)
        print("\n")
        print("หยุดโปรแกรมด้วย Ctrl+C (Program stopped with Ctrl+C)")

    finally:
        # ทำความสะอาด - ตั้งค่า DAC เป็น 0 (Cleanup - set DAC to 0)
        dac.write(0)
        print("ตั้งค่า DAC เป็น 0V แล้ว (DAC set to 0V)")
        print()

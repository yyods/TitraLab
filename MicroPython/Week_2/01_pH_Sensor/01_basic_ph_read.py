# ==============================================================================
# 01_basic_ph_read.py - การวัดค่า pH และอุณหภูมิ (pH and Temperature Measurement)
# ==============================================================================
# โปรแกรมนี้สาธิตการอ่านค่า pH จากเซ็นเซอร์และแสดงผลบนจอ TFT
# พร้อมการชดเชยอุณหภูมิตามสมการ Nernst
# This program demonstrates reading pH from sensor with temperature compensation
# and displaying on TFT display
#
# เวลาที่ใช้สอน (Teaching time): 45-60 นาที
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ทางเคมี (Chemistry Learning Objectives):
# ==============================================================================
# 1. เข้าใจการประยุกต์สมการ Nernst ในการวัด pH จริง
#    (Understand Nernst equation application in real pH measurement)
#
# 2. เรียนรู้ความสำคัญของการชดเชยอุณหภูมิ (Temperature compensation)
#    - ความชัน Nernst ขึ้นกับอุณหภูมิ: slope = -2.303RT/nF
#    - ที่ 25C: -59.16 mV/pH, ที่ 30C: -60.15 mV/pH
#
# 3. เข้าใจการใช้ค่าสอบเทียบ (calibration data) ในการคำนวณ pH
#    pH = (E - E0) / slope  โดย slope = m จากการสอบเทียบ
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้านโปรแกรม (Programming Learning Objectives):
# ==============================================================================
# 1. เรียนรู้การใช้ ADC (Analog-to-Digital Converter) อ่านค่าจากเซ็นเซอร์ pH
# 2. เข้าใจการอ่านไฟล์ข้อมูลการสอบเทียบ (calibration data file)
# 3. ใช้ Timer และ Interrupt สำหรับการบันทึกข้อมูลอัตโนมัติ
# 4. การบันทึกข้อมูลการทดลองลงไฟล์ CSV
#
# ==============================================================================
# หลักการทางเคมี: สมการ Nernst (Nernst Equation)
# ==============================================================================
# หัววัด pH ให้สัญญาณแรงดันไฟฟ้า (mV) ตามสมการ Nernst:
#
#     E_probe = E0 - (2.303RT/nF) x pH
#
# โดย:
#   E_probe = ศักย์ไฟฟ้าจากหัววัด (mV) - ค่าบวกสำหรับกรด, ลบสำหรับเบส
#   E0      = ศักย์ไฟฟ้ามาตรฐาน (mV) - ค่าที่ pH = 0
#   R       = ค่าคงที่ของก๊าซ = 8.314 J/(mol.K)
#   T       = อุณหภูมิสัมบูรณ์ (K) = C + 273.15
#   n       = จำนวนอิเล็กตรอนที่ถ่ายเท = 1 สำหรับ H+
#   F       = ค่าคงที่ฟาราเดย์ = 96485 C/mol
#
# ความชันทฤษฎี (Theoretical slope) ที่อุณหภูมิต่างๆ:
#   20C (293.15K): -58.17 mV/pH
#   25C (298.15K): -59.16 mV/pH
#   30C (303.15K): -60.15 mV/pH
#
# ==============================================================================
# วงจร pH ของ TitraLab: LMC6482 Op-Amp with Offset
# ==============================================================================
# ปัญหา: หัววัด pH ให้แรงดันบวก (กรด) และลบ (เบส) แต่ ADC อ่านได้เฉพาะ 0-3.3V
# Problem: pH probe outputs positive (acid) and negative (base) voltages,
#          but ADC can only read 0-3.3V
#
# วิธีแก้: ใช้ LMC6482 op-amp เลื่อน (offset) สัญญาณ +1650 mV (3.3V/2)
# Solution: Use LMC6482 op-amp to offset the signal by +1650 mV (3.3V/2)
#
#     E_measured = E_probe + OFFSET_MV
#
# ผลลัพธ์ที่ 25C (Results at 25C):
#   pH 4 (กรด/acidic):  E_probe = +177 mV  → E_measured = 1827 mV
#   pH 7 (กลาง/neutral): E_probe =   0 mV  → E_measured = 1650 mV  ← จุดกึ่งกลาง
#   pH 10 (เบส/basic):  E_probe = -177 mV  → E_measured = 1473 mV
#
# สมการเส้นตรงสำหรับการสอบเทียบ (Linear equation for calibration):
#     E_measured = slope_m × pH + intercept_b
#
# โดย intercept_b = OFFSET_MV + 7 × |slope| ≈ 1650 + 414 = 2064 mV (ที่ pH=0)
#
# ==============================================================================
# Hardware Configuration:
# ==============================================================================
# - GPIO 25: pH Sensor (ADC) - สัญญาณจาก LMC6482 (0-3.3V, กึ่งกลางที่ 1.65V)
# - GPIO 16: DS18B20 Temperature Sensor
# - GPIO 34: Button 1 (Start/Stop recording)
# ==============================================================================

from ili9341 import Display, color565
from xglcd_font import XglcdFont
from machine import Pin, SPI, ADC, Timer
import time
import onewire
import ds18x20

# ==============================================================================
# ค่าคงที่ทางเคมี (Chemistry Constants)
# ==============================================================================
R_CONSTANT = 8.314       # ค่าคงที่ของก๊าซ (Gas constant) J/(mol.K)
F_CONSTANT = 96485       # ค่าคงที่ฟาราเดย์ (Faraday constant) C/mol
N_ELECTRONS = 1          # จำนวนอิเล็กตรอนสำหรับ H+ (Electrons for H+)
KELVIN_OFFSET = 273.15   # แปลง Celsius เป็น Kelvin
DEFAULT_TEMP = 25.0      # อุณหภูมิเริ่มต้นเมื่อไม่มีเซ็นเซอร์ (Default when no sensor)

# ==============================================================================
# ค่าคงที่วงจร LMC6482 (LMC6482 Circuit Constants)
# ==============================================================================
# วงจร op-amp เลื่อนสัญญาณ pH probe ให้ 0 mV (pH 7) อยู่ที่กึ่งกลาง ADC
# Op-amp circuit offsets pH probe signal so 0 mV (pH 7) is at ADC midpoint
OFFSET_MV = 1650.0       # แรงดัน offset ที่ pH 7 (Offset voltage at pH 7) = 3.3V / 2

# ==============================================================================
# การตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
# DS18B20 Temperature Sensor Setup
# ==============================================================================
# เซ็นเซอร์ DS18B20 ใช้โปรโตคอล OneWire ที่ GPIO16
# DS18B20 sensor uses OneWire protocol on GPIO16
dat = Pin(16)
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# สแกนหาเซ็นเซอร์ที่เชื่อมต่อ (Scan for connected sensors)
sensors = ds.scan()
use_fallback_temp = False  # ใช้อุณหภูมิเริ่มต้นหรือไม่ (Using fallback temperature?)

if not sensors:
    use_fallback_temp = True
    print("=" * 50)
    print("คำเตือน: ไม่พบเซ็นเซอร์ DS18B20!")
    print("Warning: DS18B20 sensor not found!")
    print(f"ใช้อุณหภูมิเริ่มต้น {DEFAULT_TEMP}C สำหรับการชดเชย")
    print(f"Using default temperature {DEFAULT_TEMP}C for compensation")
    print("=" * 50)
else:
    print(f"พบเซ็นเซอร์ DS18B20 จำนวน {len(sensors)} ตัว")
    print(f"Found {len(sensors)} DS18B20 sensor(s)")

# ==============================================================================
# การตั้งค่าจอแสดงผล TFT ILI9341
# TFT Display Setup (ILI9341)
# ==============================================================================
spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, cs=Pin(15), dc=Pin(27), rst=Pin(0), width=240, height=320, rotation=90)

# โหลดฟอนต์ (Load font)
font = XglcdFont("fonts/EspressoDolce18x24.c", 18, 24)

# ==============================================================================
# การตั้งค่า ADC สำหรับเซ็นเซอร์ pH
# ADC Setup for pH Sensor
# ==============================================================================
# ADC (Analog-to-Digital Converter) แปลงสัญญาณแอนะล็อกเป็นดิจิทัล
# ATTN_11DB ตั้งค่าให้อ่านแรงดัน 0-3.3V (ความละเอียด 12-bit: 0-4095)
adc = ADC(Pin(25))
adc.atten(ADC.ATTN_11DB)

# ==============================================================================
# การตั้งค่าปุ่มกด
# Button Setup
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull-up/pull-down
# Note: GPIO34 is input-only, does NOT support internal pull-up/pull-down
# ต้องใช้ตัวต้านทาน pull-up/pull-down ภายนอก
# Must use external pull-up/pull-down resistor
button_1 = Pin(34, Pin.IN)

# ==============================================================================
# ค่าสอบเทียบเริ่มต้น (Default Calibration Values)
# ==============================================================================
# ค่าเหล่านี้จะถูกโหลดจากไฟล์ data_calibrate.txt ถ้ามี
# These values will be loaded from data_calibrate.txt if available
#
# สมการเส้นตรง (Linear equation): E_measured = slope_m × pH + intercept_b
#
# slope_m: ความชันของเส้นสอบเทียบ (mV/pH) - ค่าลบเพราะ pH สูง = แรงดันต่ำ
# intercept_b: จุดตัดแกน Y (mV ที่ pH = 0) - รวม offset จากวงจร LMC6482
# r_squared: ค่า R^2 จากการถดถอยเชิงเส้น (ควร > 0.99)
# cal_temp: อุณหภูมิขณะสอบเทียบ (C)
#
# การคำนวณ intercept_b เริ่มต้น (Default intercept_b calculation):
#   ที่ pH 7: E_measured = 1650 mV (OFFSET_MV)
#   intercept_b = OFFSET_MV - slope_m × 7 = 1650 - (-59.16 × 7) = 1650 + 414.12 = 2064.12 mV
#
slope_m = -59.16         # ความชันทฤษฎีที่ 25C (Theoretical slope at 25C)
intercept_b = 2064.12    # OFFSET_MV + 7×|slope| (ค่าที่ pH=0 รวม offset)
r_squared = 0.0          # ยังไม่ได้สอบเทียบ (Not calibrated yet)
cal_temp = 25.0          # อุณหภูมิสอบเทียบ (Calibration temperature)

# ==============================================================================
# ฟังก์ชันโหลดค่าสอบเทียบ (Load Calibration Data Function)
# ==============================================================================
def load_calibration():
    """
    โหลดค่าสอบเทียบจากไฟล์ data_calibrate.txt
    Load calibration data from data_calibrate.txt

    รูปแบบไฟล์ (File format):
    slope_m,intercept_b,r_squared,cal_temp
    -58.5,2050.3,0.9985,25.2

    หมายเหตุ (Note):
    - intercept_b ควรอยู่ในช่วง ~2000-2100 mV (รวม offset 1650 mV จากวงจร)
    - intercept_b should be ~2000-2100 mV (includes 1650 mV circuit offset)

    Returns:
        bool: True ถ้าโหลดสำเร็จ (True if loaded successfully)
    """
    global slope_m, intercept_b, r_squared, cal_temp

    try:
        with open('data_calibrate.txt', 'r') as f:
            # ข้ามบรรทัดหัวข้อ (Skip header line)
            f.readline()
            # อ่านค่าสอบเทียบ (Read calibration values)
            data = f.readline().strip().split(',')
            if len(data) >= 4:
                slope_m = float(data[0])
                intercept_b = float(data[1])
                r_squared = float(data[2])
                cal_temp = float(data[3])

                print("=" * 50)
                print("โหลดค่าสอบเทียบสำเร็จ (Calibration loaded)")
                print("=" * 50)
                print(f"  Slope (m): {slope_m:.4f} mV/pH")
                print(f"  Intercept (b): {intercept_b:.2f} mV")
                print(f"  R-squared: {r_squared:.6f}")
                print(f"  Cal. Temp: {cal_temp:.1f} C")

                # ตรวจสอบคุณภาพการสอบเทียบ (Check calibration quality)
                if r_squared < 0.99:
                    print("\nคำเตือน: ค่า R^2 ต่ำกว่า 0.99 ควรสอบเทียบใหม่")
                    print("Warning: R^2 < 0.99, consider recalibration")

                return True
    except OSError:
        print("ไม่พบไฟล์ data_calibrate.txt ใช้ค่าเริ่มต้น")
        print("data_calibrate.txt not found, using defaults")
    except Exception as e:
        print(f"ข้อผิดพลาดในการโหลด (Load error): {e}")

    return False

# ==============================================================================
# ฟังก์ชันคำนวณความชัน Nernst ตามอุณหภูมิ
# Calculate Nernst Slope at Given Temperature
# ==============================================================================
def calculate_nernst_slope(temp_celsius):
    """
    คำนวณความชัน Nernst ที่อุณหภูมิที่กำหนด
    Calculate Nernst slope at given temperature

    สูตร (Formula): slope = -2.303 * R * T / (n * F)

    Args:
        temp_celsius: อุณหภูมิเป็นองศาเซลเซียส (Temperature in Celsius)

    Returns:
        float: ความชันเป็น mV/pH (Slope in mV/pH)

    ตัวอย่าง (Examples):
        20C -> -58.17 mV/pH
        25C -> -59.16 mV/pH
        30C -> -60.15 mV/pH
    """
    temp_kelvin = temp_celsius + KELVIN_OFFSET
    # คำนวณความชัน (Calculate slope)
    slope = -2.303 * R_CONSTANT * temp_kelvin / (N_ELECTRONS * F_CONSTANT)
    # แปลงจาก V เป็น mV (Convert from V to mV)
    return slope * 1000

# ==============================================================================
# ฟังก์ชันอ่านแรงดันไฟฟ้า (mV) จากวงจร pH
# Read Voltage Function (mV) from pH Circuit
# ==============================================================================
def read_voltage_mv():
    """
    อ่านค่า ADC และแปลงเป็นมิลลิโวลต์ (mV)
    Read ADC value and convert to millivolts (mV)

    หมายเหตุวงจร LMC6482 (LMC6482 Circuit Note):
    - ค่าที่อ่านได้รวม offset 1650 mV จากวงจร op-amp แล้ว
    - The reading already includes 1650 mV offset from op-amp circuit
    - ที่ pH 7: ควรอ่านได้ประมาณ 1650 mV (At pH 7: should read ~1650 mV)
    - ที่ pH 4: ควรอ่านได้ประมาณ 1827 mV (At pH 4: should read ~1827 mV)
    - ที่ pH 10: ควรอ่านได้ประมาณ 1473 mV (At pH 10: should read ~1473 mV)

    การคำนวณ (Calculation):
    - ADC 12-bit: 0-4095
    - แรงดันอ้างอิง: 3300 mV (3.3V)
    - voltage_mv = (ADC_value / 4095) x 3300

    Returns:
        float: แรงดันไฟฟ้าเป็น mV รวม offset (Voltage in mV including offset)
    """
    adc_value = adc.read()
    voltage_mv = adc_value * 3300 / 4095
    return voltage_mv

# ==============================================================================
# ฟังก์ชันคำนวณ pH พร้อมชดเชยอุณหภูมิ
# Calculate pH with Temperature Compensation
# ==============================================================================
def calculate_ph_with_temp_compensation(voltage_mv, current_temp):
    """
    คำนวณค่า pH จากแรงดันไฟฟ้าพร้อมชดเชยอุณหภูมิ
    Calculate pH from voltage with temperature compensation

    หลักการ (Principle):
    1. แรงดันที่อ่านได้รวม offset 1650 mV จากวงจร LMC6482 แล้ว
       (Voltage reading already includes 1650 mV offset from LMC6482)
    2. ความชัน Nernst เปลี่ยนตามอุณหภูมิ (Nernst slope varies with temperature)
    3. ใช้อัตราส่วนความชันเพื่อชดเชย (Use slope ratio for compensation)

    สมการ (Equation):
    E_measured = slope_m × pH + intercept_b
    ดังนั้น: pH = (E_measured - intercept_b) / slope_corrected

    โดย:
    - E_measured = แรงดันที่อ่านได้ (รวม offset) / Measured voltage (with offset)
    - intercept_b = OFFSET_MV + 7×|slope| ≈ 2064 mV / Includes circuit offset
    - slope_corrected = slope_m × (slope_at_current_T / slope_at_cal_T)

    Args:
        voltage_mv: แรงดันที่วัดได้รวม offset (mV) / Measured voltage with offset
        current_temp: อุณหภูมิปัจจุบัน (C) / Current temperature

    Returns:
        float: ค่า pH ที่ชดเชยอุณหภูมิแล้ว / Temperature-compensated pH value
    """
    # คำนวณความชัน Nernst ที่อุณหภูมิปัจจุบันและขณะสอบเทียบ
    # Calculate Nernst slope at current and calibration temperatures
    slope_current = calculate_nernst_slope(current_temp)
    slope_cal = calculate_nernst_slope(cal_temp)

    # ชดเชยความชันตามอุณหภูมิ (Temperature compensated slope)
    # นิสิตควรสังเกตว่าความชันเปลี่ยนตามอุณหภูมิอย่างไร
    slope_corrected = slope_m * (slope_current / slope_cal)

    # คำนวณ pH จากสมการเส้นตรง: E = m*pH + b
    # ดังนั้น: pH = (E - b) / m
    # Calculate pH from linear equation: E = m*pH + b
    # Therefore: pH = (E - b) / m
    ph = (voltage_mv - intercept_b) / slope_corrected

    return ph

# ==============================================================================
# ตำแหน่งข้อความบนจอ (Text positions on display)
# ==============================================================================
text1_x = 160 - int(font.measure_text('Temperature:', spacing=1) / 2)
text1_y = 60 - 12 - 15
text2_x = 160 - int(font.measure_text('99.99 C', spacing=1) / 2)
text2_y = 60 - 12 + 15

text3_x = 160 - int(font.measure_text('pH:', spacing=1) / 2)
text3_y = 140 - 12 - 15
text4_x = 160 - int(font.measure_text('00.00', spacing=1) / 2)
text4_y = 140 - 12 + 15

text5_x = 160 - int(font.measure_text('Voltage:', spacing=1) / 2)
text5_y = 210 - 12 - 15
text6_x = 160 - int(font.measure_text('0000.0 mV', spacing=1) / 2)
text6_y = 210 - 12 + 15

# ==============================================================================
# ตัวแปรสถานะ (State variables)
# ==============================================================================
current_temp = None      # ค่าอุณหภูมิปัจจุบัน (Current temperature)
current_ph = None        # ค่า pH ปัจจุบัน (Current pH)
current_mv = None        # ค่าแรงดันปัจจุบัน (Current voltage)
recording = False        # สถานะการบันทึก (Recording state)
ph_data = []             # ข้อมูล pH ที่บันทึก (Recorded pH data)
recording_round = 0      # รอบการบันทึก (Recording round)
timer = None             # Timer object
start_time = 0           # เวลาเริ่มต้นการบันทึก (Recording start time)

# ==============================================================================
# ฟังก์ชันแสดงค่าอุณหภูมิ (Display temperature function)
# ==============================================================================
def show_temperature(temp):
    """
    แสดงค่าอุณหภูมิบนจอ TFT โดยอัปเดตเฉพาะเมื่อค่าเปลี่ยน
    Display temperature on TFT, update only when value changes
    """
    global current_temp

    temp_rounded = round(temp, 1)
    temp_text = f"{temp_rounded:.1f} C"

    if temp_rounded != current_temp:
        current_temp = temp_rounded
        temp_x = 160 - int(font.measure_text(temp_text, spacing=1) / 2)

        # ลบข้อความเก่า (Clear old text)
        display.draw_text(text2_x, text2_y, ' ' * len(f"{99.99:.2f} C"), font,
                         color565(0, 0, 0), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

        # แสดงข้อความใหม่ (Draw new text)
        display.draw_text(temp_x, text2_y, temp_text, font,
                         color565(255, 87, 255), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

# ==============================================================================
# ฟังก์ชันแสดงค่า pH (Display pH function)
# ==============================================================================
def show_ph(ph):
    """
    แสดงค่า pH บนจอ TFT โดยอัปเดตเฉพาะเมื่อค่าเปลี่ยน
    Display pH on TFT, update only when value changes

    เปลี่ยนสีตามค่า pH (Color changes based on pH):
    - pH < 7: สีแดง (กรด/Acidic)
    - pH = 7: สีเขียว (กลาง/Neutral)
    - pH > 7: สีน้ำเงิน (เบส/Basic)
    """
    global current_ph

    ph_rounded = round(ph, 2)
    ph_text = f"{ph_rounded:.2f}"

    if ph_rounded != current_ph:
        current_ph = ph_rounded
        ph_x = 160 - int(font.measure_text(ph_text, spacing=1) / 2)

        # ลบข้อความเก่า (Clear old text)
        display.draw_text(text4_x, text4_y, ' ' * len(f"{00.00:.2f}"), font,
                         color565(0, 0, 0), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

        # กำหนดสีตามค่า pH (Set color based on pH)
        # นิสิตควรสังเกตว่าสีเปลี่ยนตามความเป็นกรด-เบส
        if ph_rounded < 6.5:
            # กรด (Acidic) - สีแดง
            color = color565(255, 100, 100)
        elif ph_rounded > 7.5:
            # เบส (Basic) - สีน้ำเงิน
            color = color565(100, 150, 255)
        else:
            # กลาง (Neutral) - สีเขียว
            color = color565(100, 255, 100)

        # แสดงข้อความใหม่ (Draw new text)
        display.draw_text(ph_x, text4_y, ph_text, font,
                         color, background=color565(0, 0, 0),
                         landscape=False, spacing=1)

# ==============================================================================
# ฟังก์ชันแสดงแรงดันไฟฟ้า (Display voltage function)
# ==============================================================================
def show_voltage(voltage_mv):
    """
    แสดงค่าแรงดันไฟฟ้าบนจอ TFT
    Display voltage on TFT
    """
    global current_mv

    mv_rounded = round(voltage_mv, 1)
    mv_text = f"{mv_rounded:.1f} mV"

    if mv_rounded != current_mv:
        current_mv = mv_rounded
        mv_x = 160 - int(font.measure_text(mv_text, spacing=1) / 2)

        # ลบข้อความเก่า (Clear old text)
        display.draw_text(text6_x, text6_y, ' ' * len(f"{0000.0:.1f} mV"), font,
                         color565(0, 0, 0), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

        # แสดงข้อความใหม่ (Draw new text)
        display.draw_text(mv_x, text6_y, mv_text, font,
                         color565(255, 193, 34), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

# ==============================================================================
# ฟังก์ชันบันทึกค่า pH (Record pH function)
# ==============================================================================
def record_ph(t):
    """
    Callback function สำหรับ Timer - บันทึกค่า pH ทุกวินาที
    Timer callback - records pH every second
    """
    global ph_data, recording, start_time, last_temp

    if recording:
        # อ่านค่าแรงดันไฟฟ้า (Read voltage)
        voltage_mv = read_voltage_mv()

        # คำนวณ pH พร้อมชดเชยอุณหภูมิ (Calculate pH with temperature compensation)
        temp = last_temp if last_temp else DEFAULT_TEMP
        ph = calculate_ph_with_temp_compensation(voltage_mv, temp)

        show_ph(ph)
        show_voltage(voltage_mv)

        elapsed_time = time.time() - start_time
        ph_data.append((elapsed_time, ph, voltage_mv, temp))

        print(f"เวลา: {elapsed_time:.1f}s | pH: {ph:.2f} | {voltage_mv:.1f}mV | {temp:.1f}C")

        # บันทึก 45 วินาทีแล้วหยุด (Stop after 45 seconds)
        if elapsed_time >= 45:
            save_ph_data()
            recording = False
            t.deinit()

# ==============================================================================
# ฟังก์ชันบันทึกข้อมูลลงไฟล์ CSV (Save data to CSV file)
# ==============================================================================
def save_ph_data():
    """
    บันทึกข้อมูล pH ลงไฟล์ CSV พร้อมคำนวณค่าเฉลี่ย
    Save pH data to CSV file with average calculation
    """
    global ph_data, recording_round

    filename = f'ph_data_round_{recording_round}.csv'

    try:
        with open(filename, 'w') as f:
            # เขียนหัวข้อคอลัมน์ (Write column headers)
            f.write('Time(s),pH,Voltage(mV),Temperature(C)\n')

            for elapsed, ph, mv, temp in ph_data:
                f.write(f"{elapsed:.1f},{ph:.3f},{mv:.1f},{temp:.1f}\n")

            # คำนวณค่าเฉลี่ย (Calculate averages)
            if ph_data:
                avg_ph = sum(d[1] for d in ph_data) / len(ph_data)
                avg_mv = sum(d[2] for d in ph_data) / len(ph_data)
                avg_temp = sum(d[3] for d in ph_data) / len(ph_data)

                f.write(f"\nAverage,{avg_ph:.3f},{avg_mv:.1f},{avg_temp:.1f}\n")

        print(f"\nบันทึกข้อมูลสำเร็จ (Data saved): {filename}")
        print(f"ค่าเฉลี่ย pH: {avg_ph:.3f}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด (Error): {e}")

    ph_data.clear()

# ==============================================================================
# ฟังก์ชัน Callback สำหรับปุ่มกด (Button callback function)
# ==============================================================================
def button_callback(pin):
    """
    จัดการเมื่อกดปุ่ม - เริ่ม/หยุดการบันทึกข้อมูล
    Handle button press - start/stop recording
    """
    global recording, start_time, recording_round, timer

    if pin.value() == 0:  # ปุ่มถูกกด (Button pressed)
        if not recording:
            # เริ่มบันทึก (Start recording)
            recording = True
            start_time = time.time()
            recording_round += 1
            print(f"\nเริ่มบันทึกรอบที่ (Start recording round) {recording_round}")
            timer.init(period=1000, mode=Timer.PERIODIC, callback=record_ph)
        else:
            # หยุดบันทึก (Stop recording)
            recording = False
            print(f"หยุดบันทึกรอบที่ (Stop recording round) {recording_round}")
            timer.deinit()
            save_ph_data()

# ==============================================================================
# โปรแกรมหลัก (Main program)
# ==============================================================================
print("=" * 60)
print("การวัดค่า pH และอุณหภูมิ (pH and Temperature Measurement)")
print("พร้อมการชดเชยอุณหภูมิตามสมการ Nernst")
print("With temperature compensation using Nernst equation")
print("=" * 60)

# โหลดค่าสอบเทียบจากไฟล์ (Load calibration from file)
calibration_loaded = load_calibration()

if not calibration_loaded:
    print("\nคำเตือน: ใช้ค่าสอบเทียบเริ่มต้น")
    print("Warning: Using default calibration values")
    print("นิสิตควรรันโปรแกรม 02_calibration.py ก่อนเพื่อสอบเทียบ")
    print("Students should run 02_calibration.py first to calibrate")

print("\nกดปุ่ม 1 เพื่อเริ่ม/หยุดบันทึก (Press Button 1 to start/stop)")
print("=" * 60)

# ตั้งค่า interrupt สำหรับปุ่มกด (Setup button interrupt)
button_1.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)

# สร้าง Timer (Create Timer)
timer = Timer(0)

# ล้างหน้าจอ (Clear display)
display.clear(color565(0, 0, 0))

# แสดงหัวข้อ (Display headers)
display.draw_text(text1_x, text1_y, 'Temperature:', font,
                 color565(255, 251, 104), background=0, landscape=False, spacing=1)
display.draw_text(text3_x, text3_y, 'pH:', font,
                 color565(255, 251, 104), background=0, landscape=False, spacing=1)
display.draw_text(text5_x, text5_y, 'Voltage:', font,
                 color565(255, 251, 104), background=0, landscape=False, spacing=1)

# ตัวแปรเก็บอุณหภูมิล่าสุด (Store last temperature)
last_temp = DEFAULT_TEMP

# แสดงคำเตือนบน TFT ถ้าใช้อุณหภูมิเริ่มต้น (Show warning on TFT if using fallback)
if use_fallback_temp:
    show_temperature(DEFAULT_TEMP)
    # แสดงข้อความเตือน (Display warning message)
    warn_text = "(Default)"
    warn_x = 160 - int(font.measure_text(warn_text, spacing=1) / 2)
    display.draw_text(warn_x, text2_y + 25, warn_text, font,
                     color565(255, 150, 0), background=color565(0, 0, 0),
                     landscape=False, spacing=1)

# ==============================================================================
# Main loop - อ่านและแสดงค่าอุณหภูมิและ pH
# ==============================================================================
try:
    while True:
        # อ่านอุณหภูมิ (Read temperature)
        if sensors:
            ds.convert_temp()
            time.sleep_ms(750)
            for sensor in sensors:
                temp = ds.read_temp(sensor)
                last_temp = temp
                show_temperature(temp)

        # อ่านค่า pH (Read pH) - อัปเดตถ้าไม่ได้อยู่ในโหมดบันทึก
        # Only update if not in recording mode
        if not recording:
            voltage_mv = read_voltage_mv()
            ph = calculate_ph_with_temp_compensation(voltage_mv, last_temp)
            show_ph(ph)
            show_voltage(voltage_mv)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    if timer:
        timer.deinit()
    print("ปิด Timer แล้ว (Timer released)")

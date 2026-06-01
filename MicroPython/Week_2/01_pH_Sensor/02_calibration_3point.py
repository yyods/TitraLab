# ==============================================================================
# 02_calibration_3point.py - การสอบเทียบเซ็นเซอร์ pH แบบ 3 จุด
# 3-Point pH Sensor Calibration
# ==============================================================================
# โปรแกรมนี้สาธิตการสอบเทียบหัววัด pH ด้วยสารละลายกันชนมาตรฐาน 3 จุด
# พร้อมการคำนวณสมการถดถอยเชิงเส้น (Linear Regression) และการตรวจสอบคุณภาพ
# This program demonstrates 3-point pH sensor calibration with standard buffer
# solutions, linear regression calculation, and quality validation
#
# เวลาที่ใช้สอน (Teaching time): 60-90 นาที
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ทางเคมี (Chemistry Learning Objectives):
# ==============================================================================
# 1. เข้าใจหลักการสอบเทียบเซ็นเซอร์ pH ด้วยสารละลายกันชนมาตรฐาน
#    (Understand pH sensor calibration using standard buffer solutions)
#
# 2. เรียนรู้สมการ Nernst และความสัมพันธ์ระหว่างแรงดันไฟฟ้า (mV) กับค่า pH
#    สมการ: E = E0 - (2.303RT/nF) x pH
#    ที่ 25C: ความชันทฤษฎี = -59.16 mV/pH
#
# 3. เข้าใจว่าทำไมต้องใช้สารละลายกันชน 3 จุด (pH 4.00, 7.00, 10.00)
#    - ครอบคลุมช่วง pH ที่ใช้งานจริง (pH 3-11)
#    - ตรวจสอบ linearity ของหัววัด
#    - pH 7.00 เป็นจุด isopotential (จุดที่ไม่ขึ้นกับอุณหภูมิ)
#
# 4. เข้าใจค่า R-squared (R^2) ในการประเมินคุณภาพการสอบเทียบ
#    - R^2 >= 0.99 หมายถึงการสอบเทียบมีคุณภาพดี
#    - R^2 < 0.99 อาจบ่งบอกปัญหาของหัววัด หรือสารละลายกันชน
#
# 5. เรียนรู้ผลของอุณหภูมิต่อการวัด pH
#    - ความชัน Nernst เปลี่ยนตามอุณหภูมิ
#    - ต้องบันทึกอุณหภูมิขณะสอบเทียบเพื่อชดเชยในภายหลัง
#
# ==============================================================================
# วัตถุประสงค์การเรียนรู้ด้านโปรแกรม (Programming Learning Objectives):
# ==============================================================================
# 1. เรียนรู้การคำนวณการถดถอยเชิงเส้น (Linear Regression) แบบ manual
# 2. เข้าใจการบันทึกข้อมูลการสอบเทียบลงไฟล์ (File I/O with exception handling)
# 3. ใช้ state machine ในการควบคุมขั้นตอนการสอบเทียบ
# 4. การแสดงผล real-time บนจอ TFT
# 5. การคำนวณทางสถิติ: ค่าเฉลี่ย, ค่าเบี่ยงเบนมาตรฐาน (Statistics: mean, std dev)
# 6. การใช้ tuple unpacking เช่น voltage, std = read_average_voltage()
# 7. การใช้ list comprehension และ generator expression
#
# ==============================================================================
# หลักการทางเคมี: สมการ Nernst (Nernst Equation)
# ==============================================================================
#
#     E = E0 - (2.303RT/nF) x pH
#
# จัดรูปเป็นสมการใช้งานตรง: pH = slope_m x mV + intercept_b
# โดย:
#   slope_m = 1/(-2.303RT/nF) = ความชัน (pH/mV) ≈ -0.0169 pH/mV ที่ 25C
#   intercept_b = จุดตัดแกน y (pH) ≈ 34-36 (ขึ้นอยู่กับ offset ของวงจร)
#
# ค่าความชันทฤษฎีที่อุณหภูมิต่างๆ:
#   20C: -58.17 mV/pH (Nernst slope efficiency = 100%)
#   25C: -59.16 mV/pH (ค่ามาตรฐานที่ใช้อ้างอิง)
#   30C: -60.15 mV/pH
#
# Nernst Slope Efficiency (%) = (measured slope / theoretical slope) x 100
# - หัววัด pH ที่ดีควรมี efficiency 95-105%
# - Efficiency < 90% หรือ > 110% บ่งบอกว่าหัววัดเสื่อมสภาพ
#
# ค่า Efficiency ตามอายุของหัววัด (Efficiency by probe age):
# - หัววัดใหม่ (New probe): 97-100%
# - หัววัดอายุ 1-2 ปี (1-2 years old): 90-97%
# - หัววัดที่ควรเปลี่ยน (Should replace): < 85%
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
#   pH 4 (กรด/acidic):  E_probe = +177 mV  -> E_measured = 1827 mV
#   pH 7 (กลาง/neutral): E_probe =   0 mV  -> E_measured = 1650 mV  <- จุดกึ่งกลาง
#   pH 10 (เบส/basic):  E_probe = -177 mV  -> E_measured = 1473 mV
#
# สมการสอบเทียบสำหรับใช้งานตรง (Calibration equation for direct usage):
#     pH = slope_m x E_measured + intercept_b
#
# ตัวอย่าง: pH = -0.0169 x 1650 + 34.98 ≈ 7.09 (ที่ 1650 mV ≈ pH 7)
# Example:  pH = -0.0169 x 1827 + 34.98 ≈ 4.09 (ที่ 1827 mV ≈ pH 4)
#
# ==============================================================================
# Hardware Configuration (นิสิตกำหนดขา GPIO เอง / Student assigns GPIO pins):
# - MY_PH_PIN (GPIO 32): pH Sensor (ADC) - รับสัญญาณจาก LMC6482 (0-3.3V)
#                        Receives signal from LMC6482 (0-3.3V, midpoint at 1.65V)
#                        แนะนำ ADC1: GPIO 32, 33, 34, 35, 36, 39
# - GPIO 16: DS18B20 Temperature Sensor (fixed for this example)
# - GPIO 34: Button 1 (Confirm calibration point) - input-only pin
# ==============================================================================

import gc                                 # เก็บกวาดหน่วยความจำก่อน import ไดรเวอร์ใหญ่
from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin, ADC, SPI
# คอมไพล์ไดรเวอร์ใหญ่ (ili9341 ~37KB) ก่อน ขณะที่ heap ยังต่อเนื่องมากที่สุด แล้วค่อย
# import โมดูลเล็ก  ถ้าสลับลำดับ (xglcd ก่อน) heap จะแตกเป็นชิ้น ทำให้คอมไพล์ ili9341
# หา block ต่อเนื่องไม่พอ -> MemoryError  (gc.collect() คั่นเพื่อรวม heap ก่อนแต่ละครั้ง)
# Compile the LARGE driver (ili9341 ~37KB) first while the heap is most contiguous,
# then the small one.  Importing xglcd first fragments the heap and the ili9341
# compile can't find a contiguous block -> MemoryError.  gc.collect() defragments
# between the two heavy compiles.
gc.collect()
from ili9341 import Display, color565
gc.collect()
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20

# ==============================================================================
# การทำงานร่วมกับเฟิร์มแวร์ SciLabPro MicroPad (Interop with MicroPad firmware)
# ==============================================================================
# เฟิร์มแวร์ MicroPad ครอบครองบัส SPI ของจอ TFT (วาด boot splash) จนกว่าสคริปต์
# จะเรียก release_tft()  ถ้าไม่เรียก SPI(1,...) ด้านล่างจะเกิด OSError: SPI host
# already in use  บน MicroPython มาตรฐานเราตั้งค่าเป็น None แล้วข้ามไป
# The MicroPad firmware owns the TFT SPI bus until a script calls release_tft();
# without it SPI(1, ...) below raises OSError: SPI host already in use.  On
# standard MicroPython (no scilabpro module) we fall back to None and skip.
try:
    from scilabpro import release_tft     # ปลดจอ TFT จากเฟิร์มแวร์ (yield TFT)
except ImportError:
    release_tft = None

try:
    from scilabpro import stop_requested  # ให้แอปสั่งหยุดได้ (cooperative stop)
except ImportError:
    stop_requested = None

# ==============================================================================
# ค่าคงที่ทางเคมี (Chemistry Constants)
# ==============================================================================
R_CONSTANT = 8.314       # ค่าคงที่ของก๊าซ (Gas constant) J/(mol.K)
F_CONSTANT = 96485       # ค่าคงที่ฟาราเดย์ (Faraday constant) C/mol
N_ELECTRONS = 1          # จำนวนอิเล็กตรอนสำหรับ H+ (Electrons for H+)
KELVIN_OFFSET = 273.15   # แปลง Celsius เป็น Kelvin

# ==============================================================================
# ค่าคงที่วงจร LMC6482 (LMC6482 Circuit Constants)
# ==============================================================================
# วงจร op-amp เลื่อนสัญญาณ pH probe ให้ 0 mV (pH 7) อยู่ที่กึ่งกลาง ADC
# Op-amp circuit offsets pH probe signal so 0 mV (pH 7) is at ADC midpoint
OFFSET_MV = 1650.0       # แรงดัน offset ที่ pH 7 (Offset voltage at pH 7) = 3.3V / 2

# ==============================================================================
# การตั้งค่า ADC สำหรับเซ็นเซอร์ pH
# ADC Setup for pH Sensor
# ==============================================================================
# นิสิตกำหนดขา GPIO ตามการต่อสายจัมเปอร์ของตนเอง
# Students define GPIO pins based on their own jumper wire connections
# pH Sensor: ต้องการ ADC -> เลือก GPIO ที่รองรับ ADC
# แนะนำ ADC1 (32, 33, 34, 35, 36, 39) เพราะไม่ conflict กับ WiFi
MY_PH_PIN = 32               # ตัวอย่าง: เลือก GPIO32 สำหรับ PH_PROBE

# ADC แปลงสัญญาณแอนะล็อก (0-3.3V) เป็นค่าดิจิทัล (0-4095)
# ADC converts analog signal (0-3.3V) to digital value (0-4095)
pH_adc = ADC(Pin(MY_PH_PIN))
pH_adc.atten(ADC.ATTN_11DB)  # ตั้งค่าให้อ่านแรงดัน 0-3.3V

# ==============================================================================
# การตั้งค่าจอแสดงผล TFT
# TFT Display Setup
# ==============================================================================
# ปลดการครอบครองจอ TFT จากเฟิร์มแวร์ก่อนสร้างบัส SPI ของเราเอง (idempotent)
# Yield the TFT from the firmware BEFORE we create our own SPI bus (idempotent).
if release_tft is not None:
    release_tft()
spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0), width=320, height=240, rotation=90)

# โหลดฟอนต์ (Load font)
font = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)

# ==============================================================================
# การตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
# DS18B20 Temperature Sensor Setup
# ==============================================================================
one_wire_pin = Pin(16)
ds_sensor = DS18X20(OneWire(one_wire_pin))
roms = ds_sensor.scan()

if not roms:
    print("ไม่พบเซ็นเซอร์ DS18B20 (DS18B20 sensor not found)")

# ==============================================================================
# ค่าสารละลายกันชนมาตรฐานสำหรับการสอบเทียบ
# Standard Buffer Solution Values for Calibration
# ==============================================================================
# นิสิตควรทำความเข้าใจว่าทำไมเลือกใช้ค่า pH เหล่านี้:
# - pH 4.00: ตัวแทนช่วงกรด (Acidic range representative)
# - pH 7.00: จุด isopotential - จุดอ้างอิงที่ไม่ขึ้นกับอุณหภูมิ
# - pH 10.00: ตัวแทนช่วงเบส (Basic range representative)
#
# สารละลายกันชนที่ใช้ (Buffer solutions used):
# - pH 4.00: Potassium hydrogen phthalate buffer
# - pH 7.00: Phosphate buffer
# - pH 10.00: Carbonate-bicarbonate buffer
buffer_pH_values = [4.00, 7.00, 10.00]
calibrated_voltages = [0.0, 0.0, 0.0]  # ค่าแรงดันที่วัดได้ (mV)
temperatures = [0.0, 0.0, 0.0]         # ค่าอุณหภูมิขณะสอบเทียบ (C)

# ==============================================================================
# การตั้งค่าปุ่มกด
# Button Setup
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull-up/pull-down
# Note: GPIO34 is input-only, does NOT support internal pull-up/pull-down
button1 = Pin(34, Pin.IN)

# ==============================================================================
# ฟังก์ชันคำนวณความชัน Nernst ทฤษฎี
# Calculate Theoretical Nernst Slope
# ==============================================================================
def calculate_theoretical_nernst_slope(temp_celsius):
    """
    คำนวณความชัน Nernst ทฤษฎีที่อุณหภูมิที่กำหนด
    Calculate theoretical Nernst slope at given temperature

    สูตร (Formula): slope = -2.303 * R * T / (n * F)

    Args:
        temp_celsius: อุณหภูมิเป็นองศาเซลเซียส (Temperature in Celsius)

    Returns:
        float: ความชันทฤษฎีเป็น mV/pH (Theoretical slope in mV/pH)

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
# ฟังก์ชันอ่านแรงดันไฟฟ้า (mV)
# Read Voltage Function (mV)
# ==============================================================================
def read_voltage_mv():
    """
    อ่านค่า ADC และแปลงเป็นมิลลิโวลต์ (mV)
    Read ADC value and convert to millivolts (mV)

    หมายเหตุสำคัญ (Important Note):
    ค่าที่อ่านได้รวม offset จากวงจร LMC6482 แล้ว (+1650 mV)
    The reading includes the offset from the LMC6482 circuit (+1650 mV)

    ตัวอย่างค่าที่คาดหวัง (Expected values):
    - pH 4 (กรด):  ~1827 mV (1650 + 177)
    - pH 7 (กลาง): ~1650 mV (1650 + 0)
    - pH 10 (เบส): ~1473 mV (1650 - 177)

    การคำนวณ (Calculation):
    - ADC 12-bit: 0-4095
    - แรงดันอ้างอิง: 3300 mV (3.3V)
    - voltage_mv = (ADC_value / 4095) x 3300

    Returns:
        float: แรงดันไฟฟ้าเป็น mV (รวม offset แล้ว)
               Voltage in mV (includes LMC6482 offset)
    """
    adc_value = pH_adc.read()
    voltage_mv = adc_value * 3300 / 4095
    return voltage_mv

# ==============================================================================
# ฟังก์ชันอ่านค่าแรงดันเฉลี่ย (หลายครั้ง)
# Read Average Voltage Function (Multiple Readings)
# ==============================================================================
def read_average_voltage(num_readings=10, delay_ms=100):
    """
    อ่านค่าแรงดันหลายครั้งและคำนวณค่าเฉลี่ย
    Read voltage multiple times and calculate average

    เหตุผล: การอ่านหลายครั้งช่วยลด noise และให้ค่าที่เสถียรกว่า
    Reason: Multiple readings reduce noise and give more stable values

    Args:
        num_readings: จำนวนครั้งที่อ่าน (Number of readings)
        delay_ms: ระยะเวลารอระหว่างการอ่าน (Delay between readings in ms)

    Returns:
        tuple: (ค่าเฉลี่ย, ค่าเบี่ยงเบนมาตรฐาน)
               (average, standard deviation)
    """
    readings = []
    for _ in range(num_readings):
        readings.append(read_voltage_mv())
        sleep_ms(delay_ms)

    # คำนวณค่าเฉลี่ย (Calculate average)
    avg = sum(readings) / len(readings)

    # คำนวณค่าเบี่ยงเบนมาตรฐาน (Calculate standard deviation)
    variance = sum((x - avg) ** 2 for x in readings) / len(readings)
    std_dev = variance ** 0.5

    return avg, std_dev

# ==============================================================================
# ฟังก์ชันอ่านอุณหภูมิ
# Read Temperature Function
# ==============================================================================
def read_temperature():
    """
    อ่านค่าอุณหภูมิจากเซ็นเซอร์ DS18B20
    Read temperature from DS18B20 sensor

    หมายเหตุ: อุณหภูมิมีผลต่อค่า pH ตามสมการ Nernst
    - ความชัน Nernst เปลี่ยนประมาณ 0.2 mV/pH ต่อ 1C
    Note: Temperature affects pH according to Nernst equation

    Returns:
        float: อุณหภูมิเป็น C หรือ None ถ้าไม่พบเซ็นเซอร์
    """
    if roms:
        ds_sensor.convert_temp()
        sleep_ms(750)  # รอการแปลงค่า (Wait for conversion)
        return ds_sensor.read_temp(roms[0])
    return None

# ==============================================================================
# ฟังก์ชันคำนวณการถดถอยเชิงเส้น (Linear Regression)
# Linear Regression Calculation Function
# ==============================================================================
def linear_regression(x_values, y_values):
    """
    คำนวณการถดถอยเชิงเส้น y = mx + b พร้อมค่า R-squared
    Calculate linear regression y = mx + b with R-squared

    หลักการ (Principle):
    สำหรับเซ็นเซอร์ pH: pH = slope_m * mV + intercept_b
    - x = mV (แรงดันไฟฟ้าที่วัดได้จาก ADC)
    - y = pH (ค่า pH ของสารละลายกันชน)
    - slope_m = ความชัน (pH/mV) - ใช้คำนวณ pH จาก mV โดยตรง
    - intercept_b = จุดตัดแกน y (pH)

    สูตรการถดถอยเชิงเส้น (Linear regression formulas):
    m = (n*sum(xy) - sum(x)*sum(y)) / (n*sum(x^2) - (sum(x))^2)
    b = (sum(y) - m*sum(x)) / n

    R^2 = 1 - SS_res / SS_tot
    โดย SS_res = sum((y_i - y_pred_i)^2) และ SS_tot = sum((y_i - y_mean)^2)

    Args:
        x_values: ค่าแรงดันที่วัดได้ (Measured voltages in mV)
        y_values: ค่า pH ของสารละลายกันชน (Buffer pH values)

    Returns:
        tuple: (slope_m, intercept_b, r_squared)
               (ความชัน pH/mV, จุดตัดแกน y pH, ค่า R-squared)
    """
    n = len(x_values)

    # ตรวจสอบจำนวนข้อมูล (Check number of data points)
    if n < 2:
        return 0, 0, 0

    # คำนวณค่าที่ต้องใช้ (Calculate required sums)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x ** 2 for x in x_values)

    # คำนวณความชัน (Calculate slope)
    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        return 0, 0, 0

    slope = (n * sum_xy - sum_x * sum_y) / denominator

    # คำนวณจุดตัดแกน y (Calculate intercept)
    intercept = (sum_y - slope * sum_x) / n

    # คำนวณ R-squared (Calculate R-squared)
    y_mean = sum_y / n
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)
    ss_res = sum((y - (slope * x + intercept)) ** 2
                 for x, y in zip(x_values, y_values))

    if ss_tot == 0:
        r_squared = 0
    else:
        r_squared = 1 - (ss_res / ss_tot)

    return slope, intercept, r_squared

# ==============================================================================
# ฟังก์ชันบันทึกค่าสอบเทียบลงไฟล์
# Save Calibration Data to File Function
# ==============================================================================
def save_calibration_data(slope, intercept, r_squared, avg_temp):
    """
    บันทึกค่าสอบเทียบลงไฟล์ data_calibrate.txt
    Save calibration data to data_calibrate.txt

    รูปแบบไฟล์ (File format):
    slope_m,intercept_b,r_squared,cal_temp
    -0.016911,34.9800,0.9985,25.2

    การใช้งาน (Usage): pH = slope_m * mV + intercept_b
    - slope_m: ความชัน (pH/mV) - ค่าลบประมาณ -0.0169 pH/mV
    - intercept_b: จุดตัดแกน y (pH) - ค่าประมาณ 34-36 pH

    ตัวอย่างการใช้ (Example usage):
    pH = -0.016911 * 1650 + 34.98 = 7.08 (ใกล้ pH 7 ที่ 1650 mV)

    Args:
        slope: ความชันที่คำนวณได้ (pH/mV) - ค่าลบประมาณ -0.0169
        intercept: จุดตัดแกน y (pH) - ค่าประมาณ 34-36
        r_squared: ค่า R-squared
        avg_temp: อุณหภูมิเฉลี่ยขณะสอบเทียบ (C)

    Returns:
        bool: True ถ้าบันทึกสำเร็จ (True if saved successfully)
    """
    try:
        with open('data_calibrate.txt', 'w') as f:
            # เขียนหัวข้อ (Write header)
            f.write('slope_m,intercept_b,r_squared,cal_temp\n')
            # เขียนค่าสอบเทียบ (Write calibration values)
            f.write(f'{slope:.6f},{intercept:.4f},{r_squared:.6f},{avg_temp:.2f}\n')

        print("\nบันทึกค่าสอบเทียบสำเร็จ (Calibration saved successfully)")
        print(f"ไฟล์: data_calibrate.txt")
        return True

    except Exception as e:
        print(f"ข้อผิดพลาดในการบันทึก (Save error): {e}")
        return False

# ==============================================================================
# ฟังก์ชันบันทึกรายละเอียดการสอบเทียบ
# Save Detailed Calibration Log Function
# ==============================================================================
def save_calibration_log(slope, intercept, r_squared, efficiency):
    """
    บันทึกรายละเอียดการสอบเทียบลงไฟล์ log
    Save detailed calibration log to file

    สูตร: pH = slope_m x mV + intercept_b
    - slope_m: ประมาณ -0.0169 pH/mV (ค่าลบ เพราะ mV เพิ่ม -> pH ลด)
    - intercept_b: ประมาณ 34-36 pH

    ตัวอย่าง:
    ที่ 1650 mV (pH 7): pH = -0.0169 x 1650 + 34.98 ≈ 7.09
    ที่ 1827 mV (pH 4): pH = -0.0169 x 1827 + 34.98 ≈ 4.09

    Args:
        slope: ความชันที่คำนวณได้ (pH/mV) - ค่าลบประมาณ -0.0169
        intercept: จุดตัดแกน y (pH) - ค่าประมาณ 34-36
        r_squared: ค่า R-squared
        efficiency: Nernst slope efficiency (%)
    """
    try:
        with open('calibration_log.txt', 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("pH Sensor Calibration Log\n")
            f.write("TitraLab 3-Point Calibration\n")
            f.write("=" * 60 + "\n\n")

            f.write("Calibration Data Points:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'pH':>8} | {'Voltage (mV)':>12} | {'Temp (C)':>10}\n")
            f.write("-" * 40 + "\n")

            for i, ph in enumerate(buffer_pH_values):
                f.write(f"{ph:>8.2f} | {calibrated_voltages[i]:>12.2f} | {temperatures[i]:>10.1f}\n")

            f.write("-" * 40 + "\n\n")

            f.write("Linear Regression Results:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Equation: pH = slope_m * mV + intercept_b\n")
            f.write(f"Slope (m):        {slope:.6f} pH/mV\n")
            f.write(f"Intercept (b):    {intercept:.4f} pH\n")
            f.write(f"R-squared:        {r_squared:.6f}\n")
            f.write(f"Slope Efficiency: {efficiency:.1f}%\n")
            f.write("-" * 40 + "\n\n")

            # ประเมินคุณภาพ (Quality assessment)
            f.write("Quality Assessment:\n")
            f.write("-" * 40 + "\n")

            if r_squared >= 0.999:
                f.write("R-squared: EXCELLENT (>= 0.999)\n")
            elif r_squared >= 0.99:
                f.write("R-squared: GOOD (>= 0.99)\n")
            else:
                f.write("R-squared: POOR (< 0.99) - Consider recalibration\n")

            if 95 <= efficiency <= 105:
                f.write("Slope Efficiency: EXCELLENT (95-105%)\n")
            elif 90 <= efficiency <= 110:
                f.write("Slope Efficiency: ACCEPTABLE (90-110%)\n")
            else:
                f.write("Slope Efficiency: POOR - Probe may need replacement\n")

            f.write("\n" + "=" * 60 + "\n")

        print("บันทึก log สำเร็จ: calibration_log.txt")

    except Exception as e:
        print(f"ข้อผิดพลาดในการบันทึก log: {e}")

# ==============================================================================
# ฟังก์ชันแสดงข้อมูลดิบก่อนคำนวณ
# Display Raw Calibration Data Before Calculation
# ==============================================================================
def display_raw_calibration_data():
    """
    แสดงข้อมูลดิบที่เก็บได้จากการสอบเทียบก่อนแสดงผลลัพธ์
    Display raw calibration data before showing calculated results

    วัตถุประสงค์การเรียนรู้ (Learning Objectives):
    - นิสิตเห็นข้อมูลดิบที่ใช้ในการคำนวณ
    - นิสิตสามารถลองคำนวณสมการถดถอยเชิงเส้นด้วยตัวเอง
    - เข้าใจความสัมพันธ์ระหว่าง pH และแรงดันไฟฟ้า

    ข้อมูลที่แสดง (Data displayed):
    - ค่าแรงดันที่วัดได้ (mV) - ตัวแปรอิสระ x
    - ค่า pH ของสารละลายกันชน: 4.00, 7.00, 10.00 - ตัวแปรตาม y
    - ค่าอุณหภูมิขณะวัดแต่ละจุด
    """
    # ==============================================================================
    # แสดงบน Serial Console (Print to Serial Console)
    # ==============================================================================
    print("\n")
    print("=" * 70)
    print("ข้อมูลดิบจากการสอบเทียบ (Raw Calibration Data)")
    print("=" * 70)
    print("")
    print("นิสิตสามารถใช้ข้อมูลนี้คำนวณสมการถดถอยเชิงเส้นด้วยตัวเอง")
    print("Students can use this data to calculate linear regression manually")
    print("")
    print("-" * 70)
    print("  จุดที่  |   Voltage (x) mV   |   pH (y)   |   Temp (C)")
    print("  Point   |                    |            |")
    print("-" * 70)

    for i, ph in enumerate(buffer_pH_values):
        print(f"    {i+1}     |     {calibrated_voltages[i]:10.2f}     |   {ph:6.2f}   |    {temperatures[i]:5.1f}")

    print("-" * 70)
    print("")

    # คำนวณค่าที่ต้องใช้ในสูตร (Calculate intermediate values for formula)
    n = len(buffer_pH_values)
    sum_x = sum(calibrated_voltages)
    sum_y = sum(buffer_pH_values)
    sum_xy = sum(x * y for x, y in zip(calibrated_voltages, buffer_pH_values))
    sum_x2 = sum(x ** 2 for x in calibrated_voltages)

    print("ค่าที่ใช้ในการคำนวณ (Values for calculation):")
    print("-" * 70)
    print(f"  n (จำนวนจุด)           = {n}")
    print(f"  Sum(x)    = Sum(mV)    = {sum_x:.2f}")
    print(f"  Sum(y)    = Sum(pH)    = {sum_y:.2f}")
    print(f"  Sum(x*y)  = Sum(mV*pH) = {sum_xy:.2f}")
    print(f"  Sum(x^2)  = Sum(mV^2)  = {sum_x2:.2f}")
    print("-" * 70)
    print("")

    # แสดงสูตรการคำนวณ (Show calculation formulas)
    print("สูตรการคำนวณ Linear Regression (Formulas):")
    print("สมการ: pH = slope_m * mV + intercept_b")
    print("-" * 70)
    print("")
    print("  วิธีที่ 1: สูตรเต็ม (Full Formula)")
    print("  --------------------------------------")
    print("  slope_m = [n*Sum(xy) - Sum(x)*Sum(y)] / [n*Sum(x^2) - (Sum(x))^2]")
    print("")
    print(f"          = [{n}*{sum_xy:.2f} - {sum_x:.2f}*{sum_y:.2f}] / [{n}*{sum_x2:.2f} - ({sum_x:.2f})^2]")
    print("")
    print("  intercept_b = [Sum(y) - m*Sum(x)] / n")
    print("")
    print("-" * 70)
    print("")
    print("  วิธีที่ 2: แบบลัด 2 จุด (Simplified 2-Point Method)")
    print("  --------------------------------------")
    print("  ใช้จุด mV ที่ pH 4.00 และ pH 10.00:")
    print("")
    print("  slope_m = (pH2 - pH1) / (mV2 - mV1)")
    print(f"          = (10.00 - 4.00) / ({calibrated_voltages[2]:.2f} - {calibrated_voltages[0]:.2f})")
    print(f"          = 6.00 / {calibrated_voltages[2] - calibrated_voltages[0]:.2f}")
    print("")
    print("  intercept_b = pH1 - slope_m * mV1")
    print(f"             = 4.00 - slope_m * {calibrated_voltages[0]:.2f}")
    print("")
    print("-" * 70)
    print("")

    # แสดงค่าทฤษฎีที่คาดหวัง (Show expected theoretical values)
    avg_temp = sum(temperatures) / len(temperatures)
    theoretical_slope = calculate_theoretical_nernst_slope(avg_temp)

    print("ค่าที่คาดหวังทางทฤษฎี (Expected Theoretical Values):")
    print("-" * 70)
    print(f"  อุณหภูมิเฉลี่ย (Avg Temp): {avg_temp:.1f} C")
    print(f"  ความชัน Nernst ทฤษฎี (Theoretical Nernst Slope): {theoretical_slope:.2f} mV/pH")
    print(f"  slope_m ที่คาดหวัง (Expected slope_m): ~{1.0/theoretical_slope:.6f} pH/mV")
    print(f"  intercept_b ที่คาดหวัง (Expected intercept_b): ~34-36 pH")
    print("")
    print("  หมายเหตุ: intercept_b สูงเพราะวงจร LMC6482 offset +1650 mV")
    print("  Note: High intercept_b due to LMC6482 circuit offset of +1650 mV")
    print("-" * 70)
    print("")

    # ==============================================================================
    # แสดงบนจอ TFT (Display on TFT)
    # ==============================================================================
    display.clear()
    display.draw_text(20, 5, "Raw Calibration Data", font, color565(255, 255, 255))

    # แสดงหัวตาราง (Table header) - x=mV, y=pH
    display.draw_text(5, 35, "mV(x)", font, color565(0, 255, 255))
    display.draw_text(100, 35, "pH(y)", font, color565(0, 255, 255))
    display.draw_text(200, 35, "Temp", font, color565(0, 255, 255))

    # แสดงเส้นแบ่ง (Separator line)
    display.fill_rectangle(5, 55, 230, 2, color565(100, 100, 100))

    # แสดงข้อมูลแต่ละจุด (Display each data point)
    y_pos = 65
    for i, ph in enumerate(buffer_pH_values):
        display.draw_text(5, y_pos, f"{calibrated_voltages[i]:.1f}", font, color565(255, 193, 34))
        display.draw_text(110, y_pos, f"{ph:.2f}", font, color565(255, 255, 255))
        display.draw_text(200, y_pos, f"{temperatures[i]:.1f}C", font, color565(0, 191, 255))
        y_pos += 30

    # แสดงข้อความให้นิสิตคำนวณ (Prompt student to calculate)
    display.draw_text(5, 170, "pH = m*mV + b", font, color565(0, 255, 0))
    display.draw_text(5, 200, "Press BTN1 to verify", font, color565(255, 255, 0))


# ==============================================================================
# ฟังก์ชันรอให้นิสิตคำนวณด้วยตัวเอง
# Wait for Student Manual Calculation Function
# ==============================================================================
def wait_for_manual_calculation():
    """
    รอให้นิสิตคำนวณสมการถดถอยเชิงเส้นด้วยตัวเองก่อนแสดงผลลัพธ์
    Wait for students to manually calculate linear regression before showing results

    วัตถุประสงค์ (Objectives):
    - ให้เวลานิสิตลองคำนวณด้วยมือหรือเครื่องคิดเลข
    - เปรียบเทียบคำตอบของนิสิตกับผลจากโปรแกรม
    - เข้าใจกระบวนการคำนวณ Linear Regression
    """
    print("")
    print("=" * 70)
    print("แบบฝึกหัด: ลองคำนวณด้วยตัวเอง (Exercise: Calculate Manually)")
    print("=" * 70)
    print("")
    print("ให้นิสิตคำนวณค่าต่อไปนี้โดยใช้ข้อมูลด้านบน:")
    print("Students should calculate the following using the data above:")
    print("")
    print("  1. slope_m = ? pH/mV")
    print("  2. intercept_b = ? pH")
    print("")
    print("สูตร (Formula):")
    print("  pH = slope_m * mV + intercept_b")
    print("")
    print("-" * 70)
    print("เมื่อคำนวณเสร็จแล้ว กดปุ่ม 1 เพื่อดูคำตอบ")
    print("When finished calculating, press Button 1 to see the answer")
    print("-" * 70)
    print("")

    # แสดงข้อความบนจอ TFT (Display prompt on TFT)
    # จอ TFT ยังแสดงข้อมูลดิบอยู่ - รอการกดปุ่ม
    # TFT still shows raw data - waiting for button press

    # รอให้นิสิตกดปุ่ม (Wait for button press)
    print("รอการกดปุ่ม 1... (Waiting for Button 1...)")

    # รอจนกว่าปุ่มจะถูกกด (Wait until button is pressed)
    while button1.value() == 1:
        sleep_ms(50)

    # รอให้ปล่อยปุ่ม (Wait for button release)
    while button1.value() == 0:
        sleep_ms(50)

    print("")
    print("กำลังแสดงผลลัพธ์... (Showing results...)")
    print("")


# ==============================================================================
# ฟังก์ชันแสดงผลการสอบเทียบ
# Display Calibration Results Function
# ==============================================================================
def display_results(slope, intercept, r_squared, efficiency, avg_temp):
    """
    แสดงผลการสอบเทียบบนจอ TFT และ serial console
    Display calibration results on TFT and serial console

    Args:
        slope: ความชันที่คำนวณได้ (pH/mV)
        intercept: จุดตัดแกน y (pH)
        r_squared: ค่า R-squared
        efficiency: Nernst slope efficiency (%)
        avg_temp: อุณหภูมิเฉลี่ย (C)
    """
    # กำหนดสีตามคุณภาพ (Set color based on quality)
    if r_squared >= 0.99:
        r2_color = color565(0, 255, 0)    # เขียว = ดี (Green = Good)
        quality_text = "GOOD"
    else:
        r2_color = color565(255, 0, 0)    # แดง = ควรทำใหม่ (Red = Redo)
        quality_text = "POOR"

    if 95 <= efficiency <= 105:
        eff_color = color565(0, 255, 0)   # เขียว = ดี
    elif 90 <= efficiency <= 110:
        eff_color = color565(255, 255, 0) # เหลือง = พอใช้ (Yellow = Acceptable)
    else:
        eff_color = color565(255, 0, 0)   # แดง = ควรเปลี่ยนหัววัด

    # แสดงผลบนจอ TFT (Display on TFT)
    display.clear()
    display.draw_text(30, 10, "Calibration Results", font, color565(255, 255, 255))

    display.draw_text(10, 50, f"Slope:", font, color565(200, 200, 200))
    display.draw_text(120, 50, f"{slope:.6f}", font, color565(255, 193, 34))

    display.draw_text(10, 80, f"Intercept:", font, color565(200, 200, 200))
    display.draw_text(120, 80, f"{intercept:.4f}", font, color565(255, 193, 34))

    display.draw_text(10, 110, f"R-squared:", font, color565(200, 200, 200))
    display.draw_text(120, 110, f"{r_squared:.6f}", font, r2_color)

    display.draw_text(10, 140, f"Efficiency:", font, color565(200, 200, 200))
    display.draw_text(120, 140, f"{efficiency:.1f}%", font, eff_color)

    display.draw_text(10, 180, f"Quality: {quality_text}", font, r2_color)
    display.draw_text(10, 210, f"Temp: {avg_temp:.1f}C", font, color565(0, 191, 255))

    # แสดงผลบน serial console (Print to serial console)
    print("\n" + "=" * 60)
    print("ผลการสอบเทียบ (Calibration Results)")
    print("=" * 60)
    print(f"\nสมการสอบเทียบ (Calibration Equation):")
    print(f"pH = {slope:.6f} x mV + {intercept:.4f}")
    print(f"\nตัวอย่าง: pH = {slope:.6f} x 1650 + {intercept:.4f} = {slope * 1650 + intercept:.2f}")

    print(f"\nค่าความชัน (Slope): {slope:.6f} pH/mV")
    print(f"จุดตัดแกน y (Intercept): {intercept:.4f} pH")
    print(f"ค่า R-squared: {r_squared:.6f}")
    print(f"Nernst Slope Efficiency: {efficiency:.1f}%")
    print(f"อุณหภูมิเฉลี่ย (Avg Temp): {avg_temp:.1f}C")

    print("\n" + "-" * 60)
    print("การประเมินคุณภาพ (Quality Assessment):")
    print("-" * 60)

    # ประเมิน R-squared (Assess R-squared)
    if r_squared >= 0.999:
        print(f"R-squared: ดีเยี่ยม (Excellent) - ค่า >= 0.999")
    elif r_squared >= 0.99:
        print(f"R-squared: ดี (Good) - ค่า >= 0.99")
    else:
        print(f"R-squared: ควรสอบเทียบใหม่ (Poor) - ค่า < 0.99")
        print("  สาเหตุที่เป็นไปได้:")
        print("  - สารละลายกันชนเสื่อมสภาพ")
        print("  - หัววัดสกปรกหรือเสื่อมสภาพ")
        print("  - ไม่รอให้ค่าเสถียรก่อนบันทึก")

    # ประเมิน Slope Efficiency (Assess slope efficiency)
    if 95 <= efficiency <= 105:
        print(f"Slope Efficiency: ดีเยี่ยม (Excellent) - 95-105%")
    elif 90 <= efficiency <= 110:
        print(f"Slope Efficiency: พอใช้ได้ (Acceptable) - 90-110%")
    else:
        print(f"Slope Efficiency: ไม่ดี (Poor) - นอกช่วง 90-110%")
        print("  สาเหตุที่เป็นไปได้:")
        print("  - หัววัด pH เสื่อมสภาพ")
        print("  - ต้องเปลี่ยนหัววัดใหม่")

    print("=" * 60)

# ==============================================================================
# ฟังก์ชันสอบเทียบ pH
# pH Calibration Function
# ==============================================================================
def calibrate_pH():
    """
    ดำเนินการสอบเทียบ pH 3 จุด
    Perform 3-point pH calibration

    ขั้นตอนการสอบเทียบ (Calibration Steps):
    1. แช่หัววัดในสารละลายกันชน pH 4.00 -> กดปุ่มบันทึก
    2. แช่หัววัดในสารละลายกันชน pH 7.00 -> กดปุ่มบันทึก
    3. แช่หัววัดในสารละลายกันชน pH 10.00 -> กดปุ่มบันทึก

    หมายเหตุสำหรับนิสิต:
    - ล้างหัววัดด้วยน้ำกลั่นระหว่างเปลี่ยนสารละลายกันชน
    - รอให้ค่าเสถียร (30-60 วินาที) ก่อนกดปุ่มบันทึก
    - ค่า pH ของสารละลายกันชนอาจเปลี่ยนตามอุณหภูมิ

    Returns:
        tuple: (slope, intercept, r_squared, efficiency, avg_temp)
               หรือ None ถ้าล้มเหลว
    """
    global calibrated_voltages, temperatures

    print("\n" + "=" * 60)
    print("การสอบเทียบเซ็นเซอร์ pH แบบ 3 จุด")
    print("3-Point pH Sensor Calibration")
    print("=" * 60)

    print("\nคำแนะนำสำหรับนิสิต (Instructions for students):")
    print("-" * 60)
    print("1. เตรียมสารละลายกันชนมาตรฐาน pH 4.00, 7.00, 10.00")
    print("2. ล้างหัววัดด้วยน้ำกลั่นก่อนแช่ในสารละลายกันชนแต่ละชนิด")
    print("3. รอให้ค่าเสถียร 30-60 วินาที ก่อนกดปุ่มบันทึก")
    print("4. สังเกตค่าแรงดันไฟฟ้า (mV) ที่เปลี่ยนไปตาม pH")
    print("-" * 60)

    for i, buffer_pH in enumerate(buffer_pH_values):
        # แสดงข้อความเตรียมการสอบเทียบ พร้อมค่า mV แบบ real-time
        # Display calibration preparation message with real-time mV reading
        display.clear()
        display.draw_text(20, 10, f"Calibration Point {i+1}/3", font, color565(255, 255, 255))
        display.draw_text(20, 40, f"Buffer pH: {buffer_pH:.2f}", font, color565(0, 255, 255))

        # คำนวณค่า mV ที่คาดหวังสำหรับ buffer นี้
        # Calculate expected mV for this buffer
        expected_mv_map = {4.00: 1827, 7.00: 1650, 10.00: 1473}
        expected_mv = expected_mv_map.get(buffer_pH, 1650)

        # แสดงค่า mV ที่คาดหวัง (Show expected mV)
        display.draw_text(20, 70, f"Expected: ~{expected_mv} mV", font, color565(100, 255, 100))

        # แสดงค่า mV ดิบแบบ real-time บนจอ TFT
        # Show real-time raw mV value on TFT display
        display.draw_text(20, 105, "Raw mV:", font, color565(200, 200, 200))
        # ช่องแสดงค่า mV จะอัปเดตในลูป (mV value area will update in loop)

        display.draw_text(20, 145, "Immerse probe in", font, color565(200, 200, 200))
        display.draw_text(20, 170, "buffer solution", font, color565(200, 200, 200))
        display.draw_text(20, 210, "Press BTN1 when ready", font, color565(0, 255, 0))

        print(f"\n--- จุดสอบเทียบที่ {i+1}/3 ---")
        print(f"แช่หัววัดในสารละลายกันชน pH {buffer_pH:.2f}")
        print(f"Immerse probe in pH {buffer_pH:.2f} buffer solution")

        # แสดงค่า mV ที่คาดหวังสำหรับ buffer นี้
        # Show expected mV for this buffer
        expected_mv_values = {4.00: 1827, 7.00: 1650, 10.00: 1473}
        expected_mv = expected_mv_values.get(buffer_pH, 1650)
        print(f"ค่า mV ที่คาดหวัง (Expected mV): ~{expected_mv} mV (+/- 50 mV)")

        print("กดปุ่ม 1 เมื่อค่าเสถียรแล้ว (Press Button 1 when stable)")

        # แสดงค่า real-time ขณะรอ (Show real-time values while waiting)
        # นิสิตสามารถดูค่า mV ดิบได้ทั้งบนจอ TFT และ Serial Console
        # Students can see raw mV on both TFT display and Serial Console
        print("\nค่า mV แบบ Real-time (สังเกตค่าให้เสถียรก่อนกดปุ่ม):")
        print("Real-time mV readings (watch for stable values before pressing):")
        print("-" * 40)
        last_print_time = ticks_ms()
        reading_count = 0

        while button1.value() == 1:
            # แสดงค่าทุก 500 ms บนจอ TFT และ 1 วินาทีบน Serial
            # Update TFT every 500ms, Serial every 1 second
            current_time = ticks_ms()

            if ticks_diff(current_time, last_print_time) >= 500:
                current_mv = read_voltage_mv()

                # อัปเดตค่า mV บนจอ TFT (Update mV value on TFT)
                # ล้างพื้นที่แสดงค่า mV แล้วเขียนใหม่
                display.fill_rectangle(120, 105, 180, 30, color565(0, 0, 0))
                display.draw_text(120, 105, f"{current_mv:.1f} mV", font, color565(255, 193, 34))

                # แสดงบน Serial Console ทุกวินาที (Print to Serial every second)
                if ticks_diff(current_time, last_print_time) >= 1000:
                    reading_count += 1
                    print(f"  [{reading_count:3d}] Raw mV: {current_mv:7.1f} mV")
                    last_print_time = current_time
                elif reading_count == 0:
                    # แสดงค่าแรก (Show first value)
                    reading_count += 1
                    print(f"  [{reading_count:3d}] Raw mV: {current_mv:7.1f} mV")
                    last_print_time = current_time

            sleep_ms(50)

        # รอให้ปล่อยปุ่ม (Wait for button release)
        while button1.value() == 0:
            sleep_ms(50)

        # แสดงการรอให้ค่าเสถียร (Display stabilization countdown)
        # นิสิตควรสังเกตว่าค่าค่อยๆ เสถียรอย่างไร
        # หมายเหตุ: นิสิตรอ 30-60 วินาทีก่อนกดปุ่ม แล้วโปรแกรมรออีก 10 วินาที
        # Note: Student waits 30-60s before pressing, then program waits 10s more
        stabilization_time = 10  # วินาทีหลังกดปุ่ม (seconds after button press)

        display.clear()
        display.draw_text(30, 30, f"Measuring pH {buffer_pH:.2f}", font, color565(255, 255, 255))
        display.draw_text(30, 70, "Stabilizing...", font, color565(255, 255, 0))
        display.draw_text(30, 120, "Time Left:", font, color565(200, 200, 200))

        print(f"\nกำลังวัดค่า pH {buffer_pH:.2f}...")
        print(f"รอให้ค่าเสถียร {stabilization_time} วินาที")

        start_time = ticks_ms()
        previous_time = None

        while ticks_diff(ticks_ms(), start_time) < stabilization_time * 1000:
            remaining_time = stabilization_time - ticks_diff(ticks_ms(), start_time) // 1000
            if remaining_time != previous_time:
                display.fill_rectangle(180, 120, 100, 30, color565(0, 0, 0))
                display.draw_text(180, 120, f"{remaining_time} s", font, color565(255, 255, 0))

                # แสดงค่าปัจจุบัน (Show current value)
                current_mv = read_voltage_mv()
                display.fill_rectangle(30, 170, 280, 30, color565(0, 0, 0))
                display.draw_text(30, 170, f"Current: {current_mv:.1f} mV", font, color565(255, 193, 34))

                previous_time = remaining_time
            sleep_ms(100)

        # อ่านค่าแรงดันเฉลี่ย (Read average voltage)
        # การอ่านหลายครั้งช่วยลด noise
        print("กำลังอ่านค่าเฉลี่ย (10 readings)...")
        voltage_mv, std_dev = read_average_voltage(num_readings=10, delay_ms=100)
        calibrated_voltages[i] = voltage_mv

        # อ่านอุณหภูมิ (Read temperature)
        temperature = read_temperature()
        if temperature is not None:
            temperatures[i] = temperature
        else:
            temperatures[i] = 25.0  # ค่าเริ่มต้น (Default value)

        # แสดงผลลัพธ์ (Display results)
        display.clear()
        display.draw_text(30, 30, f"pH {buffer_pH:.2f} Recorded!", font, color565(0, 255, 0))
        display.draw_text(30, 80, f"Voltage: {voltage_mv:.1f} mV", font, color565(255, 193, 34))
        display.draw_text(30, 120, f"Std Dev: {std_dev:.2f} mV", font, color565(200, 200, 200))
        display.draw_text(30, 160, f"Temp: {temperatures[i]:.1f} C", font, color565(0, 191, 255))

        print(f"\nบันทึกจุด pH {buffer_pH:.2f}:")
        print(f"  แรงดัน (Voltage): {voltage_mv:.2f} +/- {std_dev:.2f} mV")
        print(f"  อุณหภูมิ (Temp): {temperatures[i]:.1f} C")

        # รอก่อนไปจุดถัดไป (Wait before next point)
        sleep_ms(3000)

    # ==============================================================================
    # แสดงข้อมูลดิบก่อนคำนวณ (Display Raw Data Before Calculation)
    # ==============================================================================
    # นิสิตจะได้เห็นข้อมูลที่เก็บได้ และลองคำนวณสมการเส้นตรงด้วยตัวเอง
    # Students will see collected data and try calculating linear equation manually

    display_raw_calibration_data()

    # รอให้นิสิตคำนวณเสร็จก่อนแสดงผลลัพธ์
    # Wait for students to finish manual calculation before showing results
    wait_for_manual_calculation()

    # ==============================================================================
    # คำนวณการถดถอยเชิงเส้น (Calculate Linear Regression)
    # ==============================================================================
    print("\n" + "-" * 60)
    print("กำลังคำนวณการถดถอยเชิงเส้น...")
    print("Calculating linear regression...")

    # Regression: pH = slope_m * mV + intercept_b (ใช้งานตรง / direct usage)
    # x = mV (ค่าที่วัดได้), y = pH (ค่าที่ต้องการ)
    slope, intercept, r_squared = linear_regression(calibrated_voltages, buffer_pH_values)

    # คำนวณอุณหภูมิเฉลี่ย (Calculate average temperature)
    avg_temp = sum(temperatures) / len(temperatures)

    # คำนวณความชัน Nernst ทฤษฎีที่อุณหภูมิเฉลี่ย
    # Calculate theoretical Nernst slope at average temperature
    theoretical_slope = calculate_theoretical_nernst_slope(avg_temp)

    # คำนวณ Nernst Slope Efficiency
    # นิสิตควรเข้าใจว่า efficiency บอกถึงสภาพของหัววัด
    # slope ปัจจุบันเป็น pH/mV, theoretical_slope เป็น mV/pH
    # ดังนั้น: measured_slope_mV_per_pH = 1/slope
    # efficiency = |measured_slope_mV_per_pH / theoretical_slope| x 100
    efficiency = abs(1.0 / (slope * theoretical_slope)) * 100

    # แสดงผลการสอบเทียบ (Display calibration results)
    display_results(slope, intercept, r_squared, efficiency, avg_temp)

    # บันทึกค่าสอบเทียบลงไฟล์ (Save calibration data to file)
    save_calibration_data(slope, intercept, r_squared, avg_temp)

    # บันทึก log รายละเอียด (Save detailed log)
    save_calibration_log(slope, intercept, r_squared, efficiency)

    return slope, intercept, r_squared, efficiency, avg_temp

# ==============================================================================
# โปรแกรมหลัก (Main program)
# ==============================================================================
try:
    print("\n" + "=" * 60)
    print("TitraLab pH Sensor Calibration Program")
    print("โปรแกรมสอบเทียบเซ็นเซอร์ pH")
    print("=" * 60)

    print("\nหลักการทางเคมี (Chemistry Principle):")
    print("-" * 60)
    print("หัววัด pH ให้สัญญาณแรงดันไฟฟ้าตามสมการ Nernst:")
    print("  E = E0 - (2.303RT/nF) x pH")
    print(f"  ที่ 25C: ความชันทฤษฎี = -59.16 mV/pH")
    print("\nการสอบเทียบ 3 จุดช่วย:")
    print("  1. หาค่าความชัน (slope) จริงของหัววัด")
    print("  2. ตรวจสอบ linearity ของหัววัด")
    print("  3. ประเมินสภาพของหัววัด (Slope Efficiency)")
    print("-" * 60)

    # แสดงค่า mV ที่คาดหวังจากวงจร LMC6482
    # Show expected mV values from LMC6482 circuit
    print("\nค่า mV ที่คาดหวังจากวงจร LMC6482 (Expected mV from LMC6482 circuit):")
    print("-" * 60)
    print("วงจร op-amp เลื่อนสัญญาณ +1650 mV (3.3V/2) เพื่อให้ pH 7 อยู่ตรงกลาง ADC")
    print("Op-amp circuit adds +1650 mV offset so pH 7 is at ADC midpoint")
    print("")
    print("  Buffer pH  |  E_probe (mV)  |  E_measured (mV)")
    print("  -----------|----------------|------------------")
    print("    pH 4.00  |     +177       |    ~1827 mV")
    print("    pH 7.00  |       0        |    ~1650 mV  <- จุดกึ่งกลาง")
    print("   pH 10.00  |     -177       |    ~1473 mV")
    print("-" * 60)
    print("หมายเหตุ: ค่าจริงอาจต่างกัน +/- 50 mV ขึ้นอยู่กับหัววัดและอุณหภูมิ")
    print("Note: Actual values may vary +/- 50 mV depending on probe and temperature")
    print("-" * 60)

    # ทำการสอบเทียบ (Perform calibration)
    result = calibrate_pH()

    if result:
        slope, intercept, r_squared, efficiency, avg_temp = result

        # ตรวจสอบคุณภาพการสอบเทียบ (Check calibration quality)
        if r_squared < 0.99:
            print("\n" + "!" * 60)
            print("คำเตือน: ค่า R^2 < 0.99")
            print("Warning: R^2 < 0.99")
            print("ควรตรวจสอบและทำการสอบเทียบใหม่")
            print("Please check and recalibrate")
            print("!" * 60)

    # รอจนกว่าจะกด Ctrl+C หรือแอปสั่งหยุด
    print("\nการสอบเทียบเสร็จสิ้น (Calibration complete)")
    print("กด Ctrl+C เพื่อออก (Press Ctrl+C to exit)")

    while True:
        # ตรวจคำสั่งหยุดจากแอป Student/Instructor (check for an app stop request)
        if stop_requested is not None and stop_requested():
            print("ได้รับคำสั่งหยุดจากแอป (Stop requested by app)")
            break
        sleep_ms(100)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด (Cleanup)
    display.clear()
    print("ปิดจอแล้ว (Display cleared)")

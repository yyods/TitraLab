# ==============================================================================
# config.py - การกำหนดค่าคงที่และขา GPIO สำหรับ TitraLab
# (Pin Definitions and Constants for TitraLab ESP32 Board)
# ==============================================================================
# ไฟล์นี้รวบรวมการกำหนดขา GPIO และค่าคงที่ทั้งหมดไว้ที่เดียว
# เพื่อให้ง่ายต่อการบำรุงรักษาและป้องกันความผิดพลาดจากการกำหนดขาซ้ำซ้อน
#
# This file centralizes all GPIO pin definitions and constants
# for easy maintenance and preventing duplicate pin assignments
#
# ผู้พัฒนา (Developers):
#   - Hemmawan Saon, Nuttakit Deemon, Saowapak Vchirawongkwin,
#   - Sumrit Wacharasindhu, Viwat Vchirawongkwin
#
# เวอร์ชัน (Version): 2.0.0 (OOP Refactored)
# ==============================================================================
#
# ⚠️ หลักการออกแบบบอร์ด TitraLab: GPIO และ DEVICES แยกกัน!
# ⚠️ TitraLab Board Design: GPIO and DEVICES headers are SEPARATE!
#
# บอร์ดมี 2 แถว header ที่แยกกัน (Board has 2 separate headers):
#
#   GPIO Header (ซ้าย/Left):          DEVICES Header (ขวา/Right):
#   ┌─────────────────────────┐       ┌─────────────────────────────┐
#   │ IO26 IO12 IO2  IO4  ... │       │ RED  GREEN  BUZZER  ...     │
#   │ IO25 IO33 IO32 IO35*... │       │ BUTTON_1 BUTTON_2 BUTTON_3  │
#   │      (* = Input Only)   │       │ DS18B20  PH_PROBE  POT_1    │
#   └─────────────────────────┘       │ CONTROL_1  CONTROL_2  ...   │
#                                     └─────────────────────────────┘
#
# นิสิตต้องต่อสายจัมเปอร์เองจาก GPIO → DEVICES
# Students must connect jumper wires from GPIO → DEVICES
#
# ตัวอย่าง: ต้องการใช้ LED แดง
# Example: Want to use RED LED
#   1. เลือก GPIO ที่รองรับ OUTPUT (ไม่ใช่ input-only 34,35,36,39)
#   2. ต่อสายจัมเปอร์ เช่น GPIO2 → RED บน DEVICES header
#   3. ตั้งค่าในโค้ด: LED_RED = 2
#
# ข้อดี: นิสิตเรียนรู้การเลือก GPIO ที่เหมาะสมกับอุปกรณ์แต่ละชนิด
# Benefit: Students learn to select appropriate GPIO for each device type
#
# ==============================================================================
# ขา GPIO ที่กำหนดตายตัวบน PCB (Fixed GPIO - Hardwired on PCB)
# ==============================================================================
# เฉพาะ TFT Display และ SD Card เท่านั้นที่ต่อตายตัวบน PCB
# Only TFT Display and SD Card are hardwired on PCB
# (ดู Section: TFT Display GPIO และ SD Card GPIO ด้านล่าง)
#
# ==============================================================================
# ⬇️ ขา GPIO ที่นิสิตกำหนดเอง (Student-Assigned GPIO) ⬇️
# ==============================================================================
# ค่าด้านล่างเป็น "ค่าแนะนำ" - นิสิตสามารถเปลี่ยนได้ตามการต่อสายจัมเปอร์
# Values below are "recommended defaults" - students can change based on wiring
#
# กฎการเลือก GPIO (GPIO Selection Rules):
#   - LED, Buzzer, Pump: ต้องใช้ GPIO ที่รองรับ OUTPUT (ไม่ใช่ 34,35,36,39)
#   - Button: ใช้ GPIO ใดก็ได้ (แนะนำ input-only 34,35,39 เพราะเหลือ output ให้อื่น)
#   - pH Sensor: ต้องใช้ GPIO ที่รองรับ ADC (25,32,33,34,35,36,39)
#   - DS18B20: ต้องใช้ GPIO ที่รองรับ digital I/O (ไม่ใช่ input-only)
#   - Pump: ต้องใช้ GPIO ที่รองรับ PWM (ไม่ใช่ input-only 34,35,36,39)
# ==============================================================================

# ==============================================================================
# ขา GPIO สำหรับ LED แสดงสถานะ (Status LED GPIO Pins)
# ==============================================================================
# DEVICES Header: RED, GREEN
# ต้องการ: OUTPUT capability (ห้ามใช้ GPIO 34,35,36,39)
# Required: OUTPUT capability (cannot use GPIO 34,35,36,39)
LED_RED = 2      # GPIO2  → ต่อกับ RED บน DEVICES (connect to RED on DEVICES)
LED_GREEN = 4    # GPIO4  → ต่อกับ GREEN บน DEVICES (connect to GREEN on DEVICES)

# ==============================================================================
# ขา GPIO สำหรับปุ่มกด (Button GPIO Pins)
# ==============================================================================
# DEVICES Header: BUTTON_1, BUTTON_2, BUTTON_3
# ต้องการ: INPUT capability (GPIO ใดก็ได้ - แนะนำ input-only pins)
# Required: INPUT capability (any GPIO works - recommend input-only pins)
#
# หมายเหตุสำคัญ: GPIO34, 35, 39 เป็น input-only pins
# ไม่รองรับ internal pull-up/pull-down resistors
# ต้องใช้ external pull-down resistor (มีบนบอร์ดแล้ว)
#
# IMPORTANT: GPIO34, 35, 39 are input-only pins
# They do NOT support internal pull-up/pull-down resistors
# Must use external pull-down resistor (already on board)
#
# ค่าแนะนำ (Recommended): input-only pins เพราะเหลือ output pins ให้อุปกรณ์อื่น
# input-only pins are recommended because it saves output pins for other devices
#
# ตัวอย่าง: ต่อ GPIO34 → BUTTON_1, GPIO35 → BUTTON_2, GPIO39 → BUTTON_3
# Example: Connect GPIO34 → BUTTON_1, GPIO35 → BUTTON_2, GPIO39 → BUTTON_3
BUTTON_1 = 34    # GPIO34 → BUTTON_1 บน DEVICES (input-only, เลือก/Select)
BUTTON_2 = 35    # GPIO35 → BUTTON_2 บน DEVICES (input-only, เลื่อน/Navigate)
BUTTON_3 = 39    # GPIO39 → BUTTON_3 บน DEVICES (input-only, ออก/Exit 3s hold)

# ค่า debounce สำหรับปุ่มกด (Button debounce value)
BUTTON_DEBOUNCE_MS = 200  # มิลลิวินาที (milliseconds)

# ==============================================================================
# ขา GPIO สำหรับเซ็นเซอร์อุณหภูมิ DS18B20 (Temperature Sensor GPIO)
# ==============================================================================
# DEVICES Header: DS18B20
# ต้องการ: Digital I/O capability (ห้ามใช้ input-only GPIO 34,35,36,39)
# Required: Digital I/O capability (cannot use input-only GPIO 34,35,36,39)
#
# เซ็นเซอร์อุณหภูมิใช้โปรโตคอล OneWire
# Temperature sensor uses OneWire protocol
#
# ตัวอย่าง: ต่อสาย GPIO16 → DS18B20 บน DEVICES header
# Example: Connect GPIO16 → DS18B20 on DEVICES header
DS18B20_PIN = 16  # GPIO16 → DS18B20 บน DEVICES (OneWire protocol)

# ค่าคงที่สำหรับการอ่านอุณหภูมิ (Temperature reading constants)
TEMP_CONVERSION_DELAY_MS = 750  # เวลารอการแปลงค่า (Conversion wait time)
TEMP_DEFAULT_VALUE = 25.0       # ค่าเริ่มต้นเมื่ออ่านไม่ได้ (Default when read fails)

# ==============================================================================
# ขา GPIO สำหรับเซ็นเซอร์ pH (pH Sensor GPIO)
# ==============================================================================
# DEVICES Header: PH_PROBE (also called PH_METER)
# ต้องการ: ADC capability (เฉพาะ GPIO 25,32,33,34,35,36,39)
# Required: ADC capability (only GPIO 25,32,33,34,35,36,39)
#
# เซ็นเซอร์ pH ใช้ ADC สำหรับอ่านค่าแรงดันไฟฟ้า
# pH sensor uses ADC to read voltage
#
# คำแนะนำ ADC (ADC recommendations):
#   ADC1 (GPIO 32,33,34,35,36,39): ใช้งานได้พร้อม WiFi (works with WiFi)
#   ADC2 (GPIO 25,26,27): ขัดแย้งกับ WiFi (conflicts with WiFi)
#   ถ้าไม่ใช้ WiFi → GPIO25 ก็ใช้ได้ (If no WiFi → GPIO25 works fine)
#
# ตัวอย่าง: ต่อสาย GPIO25 → PH_PROBE บน DEVICES header
# Example: Connect GPIO25 → PH_PROBE on DEVICES header
PH_PIN = 25      # GPIO25 → PH_PROBE บน DEVICES (ADC input)

# ค่าคงที่สำหรับ ADC (ADC Constants)
ADC_MAX_VALUE = 4095        # ค่า ADC สูงสุด 12-bit (Maximum 12-bit ADC value)
ADC_REFERENCE_MV = 3300     # แรงดันอ้างอิง 3.3V = 3300mV (Reference voltage)
ADC_SAMPLES = 10            # จำนวนตัวอย่างสำหรับการเฉลี่ย (Samples for averaging)

# ==============================================================================
# ค่าคงที่สำหรับการกรอง ADC แบบ Robust (Robust ADC Filtering Constants)
# ==============================================================================
# ใช้วิธี IQR (Interquartile Range) หรือ Tukey's Fences สำหรับกำจัด outlier
# Uses IQR (Interquartile Range) method or Tukey's Fences for outlier rejection
#
# ปัญหาที่พบ (Problem encountered):
#   - ADC ของ ESP32 มี occasional glitches ทำให้ได้ค่าผิดปกติ
#   - ตัวอย่าง: pH = 26.9 หรือ pH = 0.8 แทนที่จะเป็น ~11.7
#   - วิธี trimmed mean ปกติไม่สามารถกำจัด outlier รุนแรงได้
#
# วิธี IQR (IQR Method):
#   1. เก็บตัวอย่าง 25 ค่า (collect 25 samples)
#   2. เรียงลำดับและหา Q1, Q3 (sort and find Q1, Q3)
#   3. คำนวณ IQR = Q3 - Q1
#   4. กำหนดขอบเขต: lower = Q1 - 1.5*IQR, upper = Q3 + 1.5*IQR
#   5. ตัดค่านอกขอบเขตออก (reject values outside bounds)
#   6. เฉลี่ยค่าที่เหลือ (average remaining values)
#
# เวลาที่ใช้ (Time budget):
#   25 samples x 20ms = 500ms per reading (acceptable for titration)
#
ADC_ROBUST_SAMPLES = 25     # จำนวนตัวอย่างสำหรับ robust reading (samples for robust reading)
ADC_SAMPLE_DELAY_MS = 20    # หน่วงเวลาระหว่างตัวอย่าง (delay between samples in ms)
ADC_IQR_FACTOR = 1.5        # ตัวคูณ IQR มาตรฐาน (standard Tukey factor)

# ค่าบัฟเฟอร์มาตรฐานสำหรับสอบเทียบ pH (Standard buffer pH values for calibration)
PH_BUFFER_VALUES = [4.00, 7.00, 10.00]

# ค่าเริ่มต้นสำหรับสมการเส้นตรง pH (Default linear equation for pH)
# สมการ: pH = slope_m * mV + intercept_b
# โดย:
#   - slope_m มีหน่วยเป็น pH/mV (ค่าลบเพราะ pH สูง = mV ต่ำ)
#   - intercept_b มีหน่วยเป็น pH (ค่า pH ที่ mV = 0)
#   - mV คือแรงดันที่อ่านจาก ADC (0-3300 mV)
#
# Equation: pH = slope_m * mV + intercept_b
# Where:
#   - slope_m is in pH/mV units (negative because higher pH = lower mV)
#   - intercept_b is in pH units (pH value at mV = 0)
#   - mV is the voltage read from ADC (0-3300 mV)
#
# ค่านี้ควรถูกแทนที่ด้วยค่าจากการสอบเทียบจริง
# These should be replaced with actual calibration values
DEFAULT_PH_SLOPE = -0.016911    # slope_m (pH/mV) - ค่าเริ่มต้น (Default slope)
DEFAULT_PH_INTERCEPT = 34.9800  # intercept_b (pH) - ค่าเริ่มต้น (Default intercept)

# ค่า R-squared ขั้นต่ำสำหรับการสอบเทียบที่ยอมรับได้ (Minimum R² for valid calibration)
# ตามสมการ Nernst ความสัมพันธ์ระหว่าง mV และ pH ควรเป็นเส้นตรง
# According to Nernst equation, mV vs pH relationship should be linear
R_SQUARED_THRESHOLD = 0.99

# ==============================================================================
# หลักการทางเคมี: สมการ Nernst (Chemistry: Nernst Equation)
# ==============================================================================
# E = E0 - (2.303 * R * T) / (n * F) * pH
# ที่อุณหภูมิ 25 C (298.15 K):
#   - R = 8.314 J/(mol*K) (ค่าคงที่แก๊ส / Gas constant)
#   - F = 96485 C/mol (ค่าคงที่ฟาราเดย์ / Faraday constant)
#   - n = 1 (จำนวนอิเล็กตรอน / Number of electrons)
#   - Theoretical slope = -59.16 mV/pH unit
#
# ในการสอบเทียบจริง slope อาจแตกต่างเนื่องจาก:
# In real calibration, slope may differ due to:
#   - อายุการใช้งานของหัววัด (Probe age)
#   - สภาพของ reference electrode
#   - อุณหภูมิ (Temperature variations)
NERNST_THEORETICAL_SLOPE = -59.16  # mV/pH ที่ 25 C (mV/pH at 25 C)

# ==============================================================================
# ขา GPIO สำหรับ Buzzer (Buzzer GPIO)
# ==============================================================================
# DEVICES Header: BUZZER
# ต้องการ: PWM capability (ห้ามใช้ input-only GPIO 34,35,36,39)
# Required: PWM capability (cannot use input-only GPIO 34,35,36,39)
#
# Buzzer ใช้ PWM สำหรับสร้างเสียง (Buzzer uses PWM for sound generation)
#
# ตัวอย่าง: ต่อสาย GPIO26 → BUZZER บน DEVICES header
# Example: Connect GPIO26 → BUZZER on DEVICES header
BUZZER_PIN = 26  # GPIO26 → BUZZER บน DEVICES (PWM output)

# ความถี่เสียงสำหรับ Buzzer (Buzzer sound frequencies)
BUZZER_FREQ_LOW = 1000     # เสียงต่ำ (Low tone) - Hz
BUZZER_FREQ_MED = 2000     # เสียงกลาง (Medium tone) - Hz
BUZZER_FREQ_HIGH = 4000    # เสียงสูง (High tone) - Hz
BUZZER_DUTY_ON = 512       # Duty cycle เมื่อเปิดเสียง (Duty when on) - 50%
BUZZER_DUTY_OFF = 0        # Duty cycle เมื่อปิดเสียง (Duty when off)

# ==============================================================================
# ขา GPIO สำหรับปั๊ม (Pump GPIO)
# ==============================================================================
# ปั๊มใช้ PWM สำหรับควบคุมความเร็ว (Pump uses PWM for speed control)
#
# DEVICES Header มี 2 ช่องสำหรับต่อปั๊ม (2 pump connection options):
#   CONTROL_1 (Pin 15) → ต่อสายจัมเปอร์จาก GPIO21
#   CONTROL_2 (Pin 13) → ต่อสายจัมเปอร์จาก GPIO22
#
# นิสิตเลือกต่อปั๊มที่ CONTROL_1 หรือ CONTROL_2 แล้วตั้งค่า PUMP_PIN ให้ตรงกัน
# Students connect pump to CONTROL_1 or CONTROL_2, then set PUMP_PIN accordingly
#
# ตัวอย่าง (Examples):
#   ถ้าต่อปั๊มที่ CONTROL_1 → PUMP_PIN = 21 (GPIO21)
#   ถ้าต่อปั๊มที่ CONTROL_2 → PUMP_PIN = 22 (GPIO22)
#
CONTROL_1_PIN = 21  # GPIO21 - CONTROL_1 on DEVICES header
CONTROL_2_PIN = 22  # GPIO22 - CONTROL_2 on DEVICES header

# ===== ตั้งค่าตาม jumper wire ที่ต่อ (Set according to your wiring) =====
PUMP_PIN = CONTROL_1_PIN  # เปลี่ยนเป็น CONTROL_2_PIN ถ้าต่อที่ CONTROL_2
                          # Change to CONTROL_2_PIN if connected to CONTROL_2

# ค่าคงที่สำหรับ PWM ของปั๊ม (Pump PWM Constants)
PUMP_PWM_FREQ = 1000       # ความถี่ PWM (PWM frequency) - Hz
PUMP_PWM_MAX_DUTY = 1023   # Duty cycle สูงสุด 10-bit (Maximum duty cycle)
PUMP_PWM_MIN_DUTY = 0      # Duty cycle ต่ำสุด (Minimum duty cycle)

# อัตราการไหลเริ่มต้น (Default flow rate)
# ค่านี้ควรถูกแทนที่ด้วยค่าจากการสอบเทียบจริง
# This should be replaced with actual calibration value
#
# ใช้ทศนิยม 4 ตำแหน่งเพราะ:
# - ปริมาตรที่จ่าย = flow_rate * time
# - ความคลาดเคลื่อนสะสมจากทศนิยมน้อยอาจทำให้ปริมาตรผิดพลาดมาก
# - เช่น 0.28 vs 0.2772: ที่ 60s ต่างกัน 0.17 mL (อาจมีผลต่อจุดสมมูล)
#
# Use 4 decimal places because:
# - Volume dispensed = flow_rate * time
# - Rounding errors accumulate and affect transferred volume precision
# - e.g., 0.28 vs 0.2772: at 60s differs by 0.17 mL (affects equivalence point)
DEFAULT_FLOW_RATE_ML_PER_SEC = 0.2772  # mL/s ที่ 100% duty (4 ทศนิยม / 4 decimals)

# ปริมาตรเป้าหมายสำหรับการสอบเทียบอัตราการไหล (Target volume for flow rate calibration)
FLOW_RATE_CALIBRATION_VOLUME_ML = 5.00  # mL

# ปริมาตรคงที่ต่อครั้งสำหรับการไทเทรต (Fixed dose volume per titration step)
# ใช้ปริมาตรคงที่ 0.2 mL ทุกครั้งเพื่อความเรียบง่ายในการเรียนรู้
# Fixed 0.2 mL dose per step for pedagogical simplicity
# - ทุกจุดบนกราฟห่างกัน 0.2 mL เท่ากัน ง่ายต่อการวิเคราะห์
# - Every point on the curve is exactly 0.2 mL apart for easy analysis
DEFAULT_DOSE_VOLUME_ML = 0.2  # mL ต่อ step (mL per step)

# ปริมาตรสารตัวอย่างเริ่มต้น (Default sample volume)
# สำหรับห้องปฏิบัติการเคมีทั่วไป ใช้ 5 mL (Typical teaching lab uses 5 mL)
DEFAULT_SAMPLE_VOLUME_ML = 5.0  # mL ปริมาตรสารตัวอย่าง (sample volume)

# ปริมาตรไทเทรตสูงสุด = 2 เท่าของปริมาตรตัวอย่าง เพื่อให้ได้กราฟไทเทรชันรูป S ที่สมบูรณ์
# Max titration volume = 2x sample volume for a complete S-shaped titration curve
# ตัวอย่าง: 5 mL ตัวอย่าง HCl 0.1M + NaOH 0.1M
#   - จุดสมมูลอยู่ที่ ~5 mL → ต้องไทเทรตไปถึง 10 mL เพื่อเห็นส่วนหลังจุดสมมูล
# Example: 5 mL of 0.1M HCl + 0.1M NaOH
#   - Equivalence point at ~5 mL → titrate to 10 mL to see post-equivalence region
DEFAULT_MAX_VOLUME_ML = 2 * DEFAULT_SAMPLE_VOLUME_ML  # = 10.0 mL (2x sample volume)

# เวลารอให้ pH คงที่ระหว่างแต่ละ dose (Stabilization time between doses)
# pH probe ต้องการ 10-20 วินาทีจึงจะเสถียร (pH probe needs 10-20s to stabilize)
DEFAULT_STABILIZE_TIME_SEC = 10.0  # วินาที (seconds)

# ==============================================================================
# ขา GPIO สำหรับจอแสดงผล TFT ILI9341 (TFT Display GPIO)
# ==============================================================================
# จอ TFT ใช้ SPI Bus 1 (TFT uses SPI Bus 1)
TFT_SPI_BUS = 1           # SPI Bus number
TFT_SCK = 14              # GPIO14 - SPI Clock
TFT_MOSI = 13             # GPIO13 - SPI Data (Master Out Slave In)
TFT_DC = 27               # GPIO27 - Data/Command select
TFT_CS = 15               # GPIO15 - Chip Select
TFT_RST = 0               # GPIO0  - Reset

# การตั้งค่าจอแสดงผล (Display settings)
TFT_WIDTH = 320           # ความกว้างจอ (Display width) - pixels
TFT_HEIGHT = 240          # ความสูงจอ (Display height) - pixels
TFT_ROTATION = 90         # การหมุนจอ (Display rotation) - degrees
TFT_BAUDRATE = 40000000   # ความเร็ว SPI (SPI speed) - 40 MHz

# ไฟล์ฟอนต์ (Font file)
FONT_FILE = 'fonts/EspressoDolce18x24.c'
FONT_WIDTH = 18
FONT_HEIGHT = 24

# ==============================================================================
# ขา GPIO สำหรับ SD Card (SD Card GPIO) - ไม่ใช้งาน (NOT USED)
# ==============================================================================
# หมายเหตุ: ไม่ใช้ SD Card เนื่องจากบอร์ดเชื่อมต่อกับ laptop ตลอดเวลาผ่าน USB
# Note: SD Card NOT USED - board is always connected to laptop via USB
# ไฟล์ CSV บันทึกใน ESP32 flash storage และดาวน์โหลดผ่าน Thonny IDE
# CSV files are saved to ESP32 flash storage and downloaded via Thonny IDE
# รูปแบบ CSV ตรงกับ EquivPoint analysis tool (ใช้ได้โดยตรงไม่ต้องแก้ไข)
# CSV format matches EquivPoint tool (usable directly without modification)
# Header: Volume (mL),pH Value,Time(s),Temperature(C)
#
# เก็บค่าไว้สำหรับอ้างอิงเท่านั้น (Kept for reference only):
# SD_MISO = 19              # GPIO19 - SD Card MISO
# SD_MOSI = 23              # GPIO23 - SD Card MOSI
# SD_SCK = 18               # GPIO18 - SD Card SCK
# SD_CS = 5                 # GPIO5  - SD Card CS
# SD_BAUDRATE = 1000000     # 1 MHz

# ==============================================================================
# ขา GPIO เพิ่มเติม: Potentiometers (Additional GPIO: Potentiometers)
# ==============================================================================
# DEVICES Header: POT_1, POT_2
# ต้องการ: ADC capability (เฉพาะ GPIO 25,32,33,34,35,36,39)
# Required: ADC capability (only GPIO 25,32,33,34,35,36,39)
#
# Potentiometers สำหรับปรับค่า (Potentiometers for value adjustment)
#
# ตัวอย่าง: ต่อสาย GPIO32 → POT_1, GPIO33 → POT_2 บน DEVICES header
# Example: Connect GPIO32 → POT_1, GPIO33 → POT_2 on DEVICES header
POT1_PIN = 32             # GPIO32 → POT_1 บน DEVICES (ADC input)
POT2_PIN = 33             # GPIO33 → POT_2 บน DEVICES (ADC input)

# ==============================================================================
# ขา GPIO เพิ่มเติม: อุปกรณ์ควบคุมเสริม (Additional GPIO: Secondary Controls)
# ==============================================================================
# หมายเหตุ: CONTROL_1_PIN และ CONTROL_2_PIN ถูกกำหนดในส่วนปั๊มด้านบน
# Note: CONTROL_1_PIN and CONTROL_2_PIN are defined in pump section above
# ใช้สำหรับปั๊มหลัก หรืออุปกรณ์เสริมอื่น
# Used for main pump or additional equipment
#
# DEVICES Header: RELAY
# ต้องการ: Digital OUTPUT capability (ห้ามใช้ input-only GPIO 34,35,36,39)
# Required: Digital OUTPUT capability (cannot use input-only GPIO 34,35,36,39)
#
# ตัวอย่าง: ต่อสาย GPIO17 → RELAY บน DEVICES header
# Example: Connect GPIO17 → RELAY on DEVICES header
RELAY_PIN = 17            # GPIO17 → RELAY บน DEVICES (Digital output)

# ==============================================================================
# ชื่อไฟล์สำหรับบันทึกข้อมูล (Data File Names)
# ==============================================================================
CALIBRATION_FILE = "data_calibrate.txt"    # ไฟล์เก็บค่าสอบเทียบ pH
FLOWRATE_FILE = "data_flowrate.txt"        # ไฟล์เก็บค่าอัตราการไหล

# ==============================================================================
# ค่าคงที่สำหรับระบบ (System Constants)
# ==============================================================================
# เวลากดปุ่มค้างเพื่อออกจากเมนู (Hold time to exit menu)
EXIT_HOLD_TIME_SEC = 3

# เวลาสำหรับการทดสอบ pH (pH test duration)
PH_TEST_DURATION_SEC = 10

# สี RGB565 ที่ใช้บ่อย (Common RGB565 colors)
# สามารถใช้ color565(r, g, b) เพื่อสร้างสีเอง
# Use color565(r, g, b) to create custom colors
class Colors:
    """สีมาตรฐานในรูปแบบ RGB (Standard colors in RGB format)"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 193, 34)
    PURPLE = (204, 153, 255)
    LIGHT_BLUE = (102, 255, 255)
    PINK = (255, 51, 218)


# ==============================================================================
# ฟังก์ชันตรวจสอบการกำหนดขา (Pin Assignment Validation)
# ==============================================================================
def validate_pins():
    """
    ตรวจสอบว่าไม่มีขา GPIO ที่ถูกกำหนดซ้ำซ้อน
    Validate that no GPIO pins are assigned more than once

    Returns:
        bool: True ถ้าการกำหนดขาถูกต้อง (if pin assignments are valid)

    Raises:
        ValueError: ถ้ามีขาที่ถูกกำหนดซ้ำ (if duplicate pin assignments found)
    """
    all_pins = {
        'LED_RED': LED_RED,
        'LED_GREEN': LED_GREEN,
        'BUTTON_1': BUTTON_1,
        'BUTTON_2': BUTTON_2,
        'BUTTON_3': BUTTON_3,
        'DS18B20_PIN': DS18B20_PIN,
        'PH_PIN': PH_PIN,
        'BUZZER_PIN': BUZZER_PIN,
        'PUMP_PIN': PUMP_PIN,
        'TFT_SCK': TFT_SCK,
        'TFT_MOSI': TFT_MOSI,
        'TFT_DC': TFT_DC,
        'TFT_CS': TFT_CS,
        'TFT_RST': TFT_RST,
        # SD Card pins removed - ไม่ใช้งาน (not used)
        'POT1_PIN': POT1_PIN,
        'POT2_PIN': POT2_PIN,
        'CONTROL_1_PIN': CONTROL_1_PIN,
        'CONTROL_2_PIN': CONTROL_2_PIN,
        'RELAY_PIN': RELAY_PIN,
    }

    # ตรวจสอบการซ้ำซ้อน (Check for duplicates)
    pin_to_names = {}
    for name, pin in all_pins.items():
        if pin in pin_to_names:
            raise ValueError(
                f"ข้อผิดพลาด: ขา GPIO{pin} ถูกกำหนดซ้ำ "
                f"(Error: GPIO{pin} is assigned to both "
                f"'{pin_to_names[pin]}' and '{name}')"
            )
        pin_to_names[pin] = name

    return True


# ==============================================================================
# ตรวจสอบการกำหนดขาเมื่อ import โมดูล (Validate pins on module import)
# ==============================================================================
if __name__ == "__main__":
    # ทดสอบการกำหนดขาเมื่อรันไฟล์โดยตรง
    # Test pin assignments when running file directly
    try:
        validate_pins()
        print("การกำหนดขา GPIO ถูกต้อง (GPIO pin assignments are valid)")
        print("\n=== สรุปการกำหนดขา (Pin Assignment Summary) ===")
        print(f"LED Red: GPIO{LED_RED}")
        print(f"LED Green: GPIO{LED_GREEN}")
        print(f"Buttons: GPIO{BUTTON_1}, GPIO{BUTTON_2}, GPIO{BUTTON_3} (input-only)")
        print(f"DS18B20: GPIO{DS18B20_PIN}")
        print(f"pH Sensor: GPIO{PH_PIN}")
        print(f"Buzzer: GPIO{BUZZER_PIN}")
        print(f"Pump: GPIO{PUMP_PIN} (CONTROL_1={CONTROL_1_PIN}, CONTROL_2={CONTROL_2_PIN})")
        print(f"TFT: SCK={TFT_SCK}, MOSI={TFT_MOSI}, DC={TFT_DC}, CS={TFT_CS}, RST={TFT_RST}")
        print("SD Card: ไม่ใช้งาน (NOT USED) - ไฟล์บันทึกใน ESP32 flash")
        print(f"Potentiometers: POT1={POT1_PIN}, POT2={POT2_PIN}")
        print(f"Additional: RELAY={RELAY_PIN}")
    except ValueError as e:
        print(e)

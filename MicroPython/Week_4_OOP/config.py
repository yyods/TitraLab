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

# ==============================================================================
# ขา GPIO สำหรับ LED แสดงสถานะ (Status LED GPIO Pins)
# ==============================================================================
# ใช้สำหรับแสดงสถานะการทำงานของระบบ (Used for system status indication)
LED_RED = 2      # GPIO2  - LED สีแดง แสดงข้อผิดพลาด (Red LED for errors)
LED_GREEN = 4    # GPIO4  - LED สีเขียว แสดงสถานะปกติ (Green LED for normal status)

# ==============================================================================
# ขา GPIO สำหรับปุ่มกด (Button GPIO Pins)
# ==============================================================================
# หมายเหตุสำคัญ: GPIO34, 35, 39 เป็น input-only pins
# ไม่รองรับ internal pull-up/pull-down resistors
# ต้องใช้ external pull-down resistor (10K ohm)
#
# IMPORTANT: GPIO34, 35, 39 are input-only pins
# They do NOT support internal pull-up/pull-down resistors
# Must use external pull-down resistor (10K ohm)
BUTTON_1 = 34    # GPIO34 - ปุ่ม 1: เลือก/ยืนยัน (Select/Confirm)
BUTTON_2 = 35    # GPIO35 - ปุ่ม 2: เลื่อนเมนู (Navigate menu)
BUTTON_3 = 39    # GPIO39 - ปุ่ม 3: ย้อนกลับ (กดค้าง 3 วินาที) (Back - hold 3 sec)

# ค่า debounce สำหรับปุ่มกด (Button debounce value)
BUTTON_DEBOUNCE_MS = 200  # มิลลิวินาที (milliseconds)

# ==============================================================================
# ขา GPIO สำหรับเซ็นเซอร์อุณหภูมิ DS18B20 (Temperature Sensor GPIO)
# ==============================================================================
# เซ็นเซอร์อุณหภูมิใช้โปรโตคอล OneWire
# Temperature sensor uses OneWire protocol
DS18B20_PIN = 16  # GPIO16 - เซ็นเซอร์อุณหภูมิ DS18B20 (Temperature sensor)

# ค่าคงที่สำหรับการอ่านอุณหภูมิ (Temperature reading constants)
TEMP_CONVERSION_DELAY_MS = 750  # เวลารอการแปลงค่า (Conversion wait time)
TEMP_DEFAULT_VALUE = 25.0       # ค่าเริ่มต้นเมื่ออ่านไม่ได้ (Default when read fails)

# ==============================================================================
# ขา GPIO สำหรับเซ็นเซอร์ pH (pH Sensor GPIO)
# ==============================================================================
# เซ็นเซอร์ pH ใช้ ADC สำหรับอ่านค่าแรงดันไฟฟ้า
# pH sensor uses ADC to read voltage
PH_PIN = 25      # GPIO25 - เซ็นเซอร์ pH (pH sensor ADC input)

# ค่าคงที่สำหรับ ADC (ADC Constants)
ADC_MAX_VALUE = 4095        # ค่า ADC สูงสุด 12-bit (Maximum 12-bit ADC value)
ADC_REFERENCE_MV = 3300     # แรงดันอ้างอิง 3.3V = 3300mV (Reference voltage)
ADC_SAMPLES = 10            # จำนวนตัวอย่างสำหรับการเฉลี่ย (Samples for averaging)

# ค่าบัฟเฟอร์มาตรฐานสำหรับสอบเทียบ pH (Standard buffer pH values for calibration)
PH_BUFFER_VALUES = [4.00, 7.00, 10.00]

# ค่าเริ่มต้นสำหรับสมการเส้นตรง pH (Default linear equation for pH)
# pH = slope * voltage + intercept
# ค่านี้ควรถูกแทนที่ด้วยค่าจากการสอบเทียบจริง
# These should be replaced with actual calibration values
DEFAULT_PH_SLOPE = -5.7901      # ค่า slope เริ่มต้น (Default slope)
DEFAULT_PH_INTERCEPT = 16.769   # ค่า intercept เริ่มต้น (Default intercept)

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
# Buzzer ใช้ PWM สำหรับสร้างเสียง (Buzzer uses PWM for sound generation)
BUZZER_PIN = 22  # GPIO22 - Buzzer (PWM output)

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
PUMP_PIN = 21    # GPIO21 - ปั๊มไทแทรนต์ (Titrant pump PWM output)

# ค่าคงที่สำหรับ PWM ของปั๊ม (Pump PWM Constants)
PUMP_PWM_FREQ = 1000       # ความถี่ PWM (PWM frequency) - Hz
PUMP_PWM_MAX_DUTY = 1023   # Duty cycle สูงสุด 10-bit (Maximum duty cycle)
PUMP_PWM_MIN_DUTY = 0      # Duty cycle ต่ำสุด (Minimum duty cycle)

# อัตราการไหลเริ่มต้น (Default flow rate)
# ค่านี้ควรถูกแทนที่ด้วยค่าจากการสอบเทียบจริง
# This should be replaced with actual calibration value
DEFAULT_FLOW_RATE_ML_PER_SEC = 0.2772  # mL/วินาที ที่ 100% duty (mL/s at 100% duty)

# ปริมาตรเป้าหมายสำหรับการสอบเทียบอัตราการไหล (Target volume for flow rate calibration)
FLOW_RATE_CALIBRATION_VOLUME_ML = 5.00  # mL

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
FONT_FILE = 'EspressoDolce18x24.c'
FONT_WIDTH = 18
FONT_HEIGHT = 24

# ==============================================================================
# ขา GPIO สำหรับ SD Card (SD Card GPIO)
# ==============================================================================
# SD Card ใช้ SPI (SoftSPI) (SD Card uses SPI)
SD_MISO = 19              # GPIO19 - SD Card MISO (Master In Slave Out)
SD_MOSI = 23              # GPIO23 - SD Card MOSI (Master Out Slave In)
SD_SCK = 18               # GPIO18 - SD Card SCK (Clock)
SD_CS = 5                 # GPIO5  - SD Card CS (Chip Select)

# ความเร็ว SPI สำหรับ SD Card (SD Card SPI speed)
SD_BAUDRATE = 1000000     # 1 MHz

# ==============================================================================
# ขา GPIO เพิ่มเติม: Potentiometers (Additional GPIO: Potentiometers)
# ==============================================================================
# Potentiometers สำหรับปรับค่า (Potentiometers for value adjustment)
POT1_PIN = 32             # GPIO32 - Potentiometer 1
POT2_PIN = 33             # GPIO33 - Potentiometer 2

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
        'SD_MISO': SD_MISO,
        'SD_MOSI': SD_MOSI,
        'SD_SCK': SD_SCK,
        'SD_CS': SD_CS,
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
        print(f"Pump: GPIO{PUMP_PIN}")
        print(f"TFT: SCK={TFT_SCK}, MOSI={TFT_MOSI}, DC={TFT_DC}, CS={TFT_CS}, RST={TFT_RST}")
        print(f"SD Card: MISO={SD_MISO}, MOSI={SD_MOSI}, SCK={SD_SCK}, CS={SD_CS}")
    except ValueError as e:
        print(e)

# ==============================================================================
# pins.py - TitraLab Hardware Pin Configuration
# การกำหนดขา GPIO สำหรับบอร์ด TitraLab
# ==============================================================================
#
# TitraLab เป็นบอร์ดพัฒนาสำหรับการทดลองไทเทรชันอัตโนมัติ ออกแบบมาเพื่อการเรียน
# การสอนในรายวิชาปฏิบัติการเคมีวิเคราะห์ (2302311) ที่จุฬาลงกรณ์มหาวิทยาลัย
#
# TitraLab is an educational development board for automated titration experiments,
# designed for the Integrated Chemistry Laboratory I course (2302311) at
# Chulalongkorn University.
#
# ฮาร์ดแวร์หลัก (Main Hardware Components):
# - ESP32-WROOM-32 Microcontroller
# - 2.4" TFT Display (ILI9341, 320x240 pixels)
# - pH Sensor with LMC6482 op-amp signal conditioning
# - DS18B20 Temperature Sensor (OneWire)
# - Peristaltic Pump (12V, PWM controlled via MOSFET)
# - SD Card slot for data logging
# - 3 push buttons with hardware debouncing (74HC14D Schmitt trigger)
# - Status LEDs (Red/Green) and Buzzer
#
# ==============================================================================

# ==============================================================================
# LED แสดงสถานะ (Status LEDs)
# ==============================================================================
# ใช้แสดงสถานะการทำงานของระบบ เช่น พร้อมใช้งาน/เกิดข้อผิดพลาด
# Used to indicate system status: ready/error conditions
#
# การใช้งานใน Week 3 (Usage in Week 3 Titration System):
# - LED_RED: เปิดเมื่อเกิดข้อผิดพลาด หรือค่า pH ผิดปกติ
#            (Turns on during errors or abnormal pH readings)
# - LED_GREEN: เปิดเมื่อระบบพร้อมทำงาน หรือไทเทรชันสำเร็จ
#              (Turns on when system ready or titration complete)

LED_RED   = 2     # GPIO2  - LED สีแดง แสดงข้อผิดพลาด (Red LED - error indicator)
LED_GREEN = 4     # GPIO4  - LED สีเขียว แสดงสถานะปกติ (Green LED - OK indicator)


# ==============================================================================
# ปุ่มกด (Push Buttons)
# ==============================================================================
# ปุ่มทั้ง 3 ตัวผ่านวงจร Schmitt trigger (74HC14D) เพื่อลด noise จากการกด
# All 3 buttons are hardware debounced via 74HC14D Schmitt trigger IC
#
# ข้อจำกัดทางฮาร์ดแวร์ (Hardware Constraints):
# - GPIO34, GPIO35, GPIO39 เป็นขา input-only (ไม่สามารถใช้เป็น output ได้)
# - ไม่มี internal pull-up resistor ต้องใช้ pull-down ภายนอก
# - These are input-only pins (cannot be used as outputs)
# - No internal pull-up available, external pull-down is used
#
# การใช้งานใน Week 3 (Usage in Week 3 Titration System):
# - BUTTON1 (SELECT): ยืนยันการเลือก, เริ่ม/หยุดไทเทรชัน
#                     (Confirm selection, Start/Stop titration)
# - BUTTON2 (UP): เลื่อนขึ้น, เพิ่มค่า (Navigate up, Increase value)
# - BUTTON3 (DOWN): เลื่อนลง, ลดค่า (Navigate down, Decrease value)

BUTTON1 = 34      # GPIO34 - ปุ่ม SELECT/ยืนยัน (SELECT/Confirm button)
BUTTON2 = 35      # GPIO35 - ปุ่ม UP/เพิ่มค่า (UP/Increase button)
BUTTON3 = 39      # GPIO39 - ปุ่ม DOWN/ลดค่า (DOWN/Decrease button)


# ==============================================================================
# เซ็นเซอร์ (Sensors)
# ==============================================================================

# --- เซ็นเซอร์อุณหภูมิ DS18B20 (Temperature Sensor) ---
# ใช้โปรโตคอล OneWire สำหรับการสื่อสาร
# Uses OneWire protocol for communication
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - มี 4.7k pull-up resistor (R51) บนบอร์ด
# - Has 4.7k pull-up resistor (R51) on board
# - ความละเอียด: 9-12 bit (ค่าเริ่มต้น 12 bit = 0.0625 C)
# - Resolution: 9-12 bit (default 12 bit = 0.0625 C)
#
# การใช้งานในเคมี (Chemistry Application):
# - ชดเชยค่า pH ตามอุณหภูมิ (สมการ Nernst: -59.16 mV/pH ที่ 25C)
# - Temperature compensation for pH readings (Nernst equation: -59.16 mV/pH at 25C)

DS18B20_PIN = 16  # GPIO16 - เซ็นเซอร์อุณหภูมิ DS18B20 (Temperature sensor, OneWire)


# --- เซ็นเซอร์ pH (pH Sensor) ---
# รับสัญญาณจากวงจร op-amp (LMC6482) ที่ขยายสัญญาณจาก pH probe
# Receives signal from LMC6482 op-amp circuit that amplifies pH probe signal
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - ADC input ช่วง 0-3.3V (ต้องตั้ง attenuation = 11dB)
# - ADC input range 0-3.3V (requires attenuation = 11dB)
# - ความละเอียด ADC: 12 bit (0-4095)
# - ADC resolution: 12 bit (0-4095)
#
# การสอบเทียบ (Calibration):
# - ใช้สารละลายบัฟเฟอร์ pH 4.0 และ pH 7.0 (หรือ pH 10.0)
# - Use buffer solutions pH 4.0 and pH 7.0 (or pH 10.0)
# - คำนวณ: pH = slope_m * mV + intercept_b
# - Calculation: pH = slope_m * mV + intercept_b

PH_PIN = 25       # GPIO25 - เซ็นเซอร์ pH (pH sensor ADC input)


# ==============================================================================
# ตัวต้านทานปรับค่าได้ (Potentiometers)
# ==============================================================================
# ใช้สำหรับปรับค่าพารามิเตอร์ต่างๆ ในระบบ
# Used for adjusting various parameters in the system
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - รุ่น RV09AF-40-20K-B1K (1K ohm, linear taper)
# - Model: RV09AF-40-20K-B1K (1K ohm, linear taper)
# - ADC input ช่วง 0-3.3V
# - ADC input range 0-3.3V
#
# การใช้งาน (Usage):
# - POT1: ปรับความเร็วปั๊ม (Adjust pump speed)
# - POT2: ปรับค่าพารามิเตอร์อื่นๆ (Adjust other parameters)

POT1_PIN = 32     # GPIO32 - Potentiometer 1 (ADC input)
POT2_PIN = 33     # GPIO33 - Potentiometer 2 (ADC input)


# ==============================================================================
# อุปกรณ์ควบคุม (Actuators)
# ==============================================================================

# --- Buzzer ---
# ใช้สำหรับแจ้งเตือนด้วยเสียง
# Used for audio alerts and notifications
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - ขับผ่านทรานซิสเตอร์ MMBT3904
# - Driven via MMBT3904 transistor
# - รองรับ PWM สำหรับสร้างเสียงความถี่ต่างๆ
# - Supports PWM for generating different tones
#
# การใช้งานใน Week 3 (Usage in Week 3 Titration System):
# - เสียงสั้น: ยืนยันการกดปุ่ม (Short beep: button press confirmation)
# - เสียงยาว: ถึงจุดสมมูล (Long beep: equivalence point reached)
# - เสียงเตือน: เกิดข้อผิดพลาด (Alarm: error occurred)

BUZZER_PIN = 26   # GPIO26 - Buzzer (PWM output)


# --- ปั๊มสารไทแทรนต์ (Titrant Pump - CONTROL_1) ---
# ปั๊มหลักสำหรับจ่ายสารละลายไทแทรนต์ (NaOH หรือ HCl)
# Main pump for dispensing titrant solution (NaOH or HCl)
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - ควบคุมผ่าน optocoupler และ MOSFET
# - Controlled via optocoupler and MOSFET
# - แรงดันเอาต์พุต: 12V DC
# - Output voltage: 12V DC
# - รองรับ PWM สำหรับควบคุมความเร็ว (ปริมาตรต่อนาที)
# - Supports PWM for speed control (volume per minute)
#
# การใช้งานในเคมี (Chemistry Application):
# - จ่ายสารละลายมาตรฐาน (NaOH 0.1M) ทีละหยด
# - Dispense standard solution (0.1M NaOH) drop by drop
# - ปริมาตรต่อหยด ~0.05 mL (ขึ้นกับ duty cycle)
# - Volume per drop ~0.05 mL (depends on duty cycle)

PUMP_PIN = 21     # GPIO21 - ปั๊มหลัก CONTROL_1 (Main pump, PWM output)


# --- ช่องควบคุมเสริม (Secondary Control - CONTROL_2) ---
# สำหรับปั๊มตัวที่ 2 หรืออุปกรณ์เสริมอื่นๆ
# For secondary pump or other auxiliary equipment
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - วงจรเหมือนกับ CONTROL_1 (optocoupler + MOSFET)
# - Same circuit as CONTROL_1 (optocoupler + MOSFET)
# - แรงดันเอาต์พุต: 12V DC
# - Output voltage: 12V DC

CONTROL_2 = 22    # GPIO22 - ช่องควบคุมเสริม CONTROL_2 (Secondary control output)


# --- รีเลย์ (Relay) ---
# สำหรับควบคุมอุปกรณ์ไฟฟ้ากระแสสลับหรืออุปกรณ์กำลังสูง
# For controlling AC devices or high-power equipment
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - ควบคุมผ่าน optocoupler และทรานซิสเตอร์
# - Controlled via optocoupler and transistor
# - สามารถควบคุมโหลดได้สูงสุดตามพิกัดของรีเลย์
# - Can control loads up to relay rating

RELAY_PIN = 17    # GPIO17 - รีเลย์ควบคุม (Relay control output)


# ==============================================================================
# จอแสดงผล TFT (TFT Display - ILI9341)
# ==============================================================================
# จอ LCD สี 2.4 นิ้ว ความละเอียด 320x240 พิกเซล
# 2.4" Color LCD, 320x240 pixels resolution
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - ใช้ SPI Bus 1 ของ ESP32
# - Uses ESP32 SPI Bus 1
# - ความเร็ว SPI สูงสุด: 40 MHz
# - Maximum SPI speed: 40 MHz
# - TFT_RST ใช้ร่วมกับขา boot mode (GPIO0)
# - TFT_RST shares with boot mode pin (GPIO0)
#
# การใช้งานใน Week 3 (Usage in Week 3 Titration System):
# - แสดงค่า pH และอุณหภูมิแบบ real-time
# - Display real-time pH and temperature values
# - แสดงกราฟไทเทรชัน (titration curve)
# - Display titration curve graph
# - แสดงเมนูและสถานะการทำงาน
# - Display menu and operation status

TFT_SCK  = 14     # GPIO14 - TFT SPI Clock
TFT_MOSI = 13     # GPIO13 - TFT SPI Data Out (MOSI)
TFT_DC   = 27     # GPIO27 - TFT Data/Command select
TFT_CS   = 15     # GPIO15 - TFT Chip Select
TFT_RST  = 0      # GPIO0  - TFT Reset (shared with boot mode pin)
TFT_SPI_BUS = 1   # หมายเลข SPI Bus (SPI Bus number)
TFT_BAUDRATE = 40000000  # ความเร็ว SPI 40 MHz (SPI speed)


# ==============================================================================
# การ์ด SD (SD Card - SoftSPI)
# ==============================================================================
# ใช้สำหรับบันทึกข้อมูลการทดลอง (data logging)
# Used for experiment data logging
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - ใช้ SoftSPI (แยกจาก TFT)
# - Uses SoftSPI (separate from TFT)
# - มี level shifter (SN74LVC125APWR) แปลง 3.3V <-> SD Card
# - Has level shifter (SN74LVC125APWR) for 3.3V <-> SD Card
# - รองรับ SD Card สูงสุด 32GB (FAT32)
# - Supports SD Card up to 32GB (FAT32)
#
# การใช้งานใน Week 3 (Usage in Week 3 Titration System):
# - บันทึกข้อมูล pH, อุณหภูมิ, ปริมาตร ลงไฟล์ CSV
# - Log pH, temperature, volume data to CSV file
# - เก็บค่าสอบเทียบเซ็นเซอร์
# - Store sensor calibration data
# - บันทึกประวัติการทดลอง
# - Record experiment history

SD_MISO = 19      # GPIO19 - SD Card SPI Data In (MISO)
SD_MOSI = 23      # GPIO23 - SD Card SPI Data Out (MOSI)
SD_SCK  = 18      # GPIO18 - SD Card SPI Clock
SD_CS   = 5       # GPIO5  - SD Card Chip Select
SD_BAUDRATE = 1000000  # ความเร็ว SPI 1 MHz (SPI speed for SD Card)


# ==============================================================================
# เซ็นเซอร์ระดับของเหลว (Level Sensors - Optional)
# ==============================================================================
# สำหรับตรวจจับระดับสารละลายในภาชนะ (ติดตั้งเพิ่มเติม)
# For detecting liquid level in containers (optional installation)
#
# ข้อมูลทางฮาร์ดแวร์ (Hardware Details):
# - Active-low พร้อม 5V pull-up resistor
# - Active-low with 5V pull-up resistor
# - ใช้ float switch หรือ capacitive sensor
# - Uses float switch or capacitive sensor
#
# หมายเหตุ: ขายังไม่กำหนดในเวอร์ชันปัจจุบัน
# Note: Pins not assigned in current version

LEVEL_1 = None    # ยังไม่กำหนด - เซ็นเซอร์ระดับ 1 (Not assigned - Level sensor 1)
LEVEL_2 = None    # ยังไม่กำหนด - เซ็นเซอร์ระดับ 2 (Not assigned - Level sensor 2)


# ==============================================================================
# ข้อควรระวังในการใช้งานขา GPIO (GPIO Usage Warnings)
# ==============================================================================
#
# ขาที่ห้ามใช้งานอื่น (Reserved Pins - DO NOT USE for other purposes):
# -----------------------------------------------------------------------------
# GPIO0  - ใช้สำหรับ boot mode และ TFT Reset (boot mode and TFT Reset)
# GPIO2  - LED_RED (จะกระพริบตอน boot) (will blink during boot)
# GPIO5  - SD Card CS (ต้อง HIGH ตอน boot) (must be HIGH during boot)
# GPIO12 - Boot mode pin (ห้ามต่อ pull-up) (no pull-up allowed)
# GPIO15 - TFT CS (ต้อง HIGH ตอน boot) (must be HIGH during boot)
#
# ขา Input-only (Input-only Pins):
# -----------------------------------------------------------------------------
# GPIO34, GPIO35, GPIO36, GPIO39 - ใช้ได้เฉพาะ input เท่านั้น
#                                  (Can only be used as inputs)
#                                - ไม่มี internal pull-up/pull-down
#                                  (No internal pull-up/pull-down)
#
# ขาที่ใช้โดย Flash (Pins used by internal Flash - DO NOT USE):
# -----------------------------------------------------------------------------
# GPIO6, GPIO7, GPIO8, GPIO9, GPIO10, GPIO11 - เชื่อมต่อกับ SPI Flash
#                                               (Connected to SPI Flash)
#
# ==============================================================================


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Examples)
# ==============================================================================
#
# --- นำเข้าและใช้งาน (Import and use) ---
# from pins import LED_RED, LED_GREEN, BUTTON1, PH_PIN
# from machine import Pin, ADC
#
# led = Pin(LED_RED, Pin.OUT)
# btn = Pin(BUTTON1, Pin.IN)  # ไม่ต้องใส่ pull-up (no pull-up needed)
# ph_adc = ADC(Pin(PH_PIN))
# ph_adc.atten(ADC.ATTN_11DB)  # ช่วง 0-3.3V (0-3.3V range)
#
# --- ตัวอย่างการตั้งค่าปั๊ม (Pump setup example) ---
# from pins import PUMP_PIN
# from machine import PWM, Pin
#
# pump = PWM(Pin(PUMP_PIN))
# pump.freq(1000)       # ความถี่ 1 kHz (1 kHz frequency)
# pump.duty(512)        # 50% duty cycle
# # ... ใช้งาน (use) ...
# pump.deinit()         # ต้องเรียกเมื่อเลิกใช้งาน (must call when done)
#
# ==============================================================================

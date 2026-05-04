# ==============================================================================
# pins.py - TitraLab Pin Configuration (Week_2 wrapper)
# การกำหนดขา GPIO สำหรับบอร์ด TitraLab (ไฟล์ wrapper สำหรับ Week_2)
# ==============================================================================
#
# ไฟล์นี้นำเข้าค่าคงที่จาก Week_1/pins.py เพื่อให้มีแหล่งข้อมูลเดียว
# This file imports constants from Week_1/pins.py for single source of truth
#
# สำหรับการใช้งานบน ESP32:
# For ESP32 deployment:
# - คัดลอก Week_1/pins.py ไปยัง root หรือ /lib บนอุปกรณ์
# - Copy Week_1/pins.py to root or /lib directory on device
#
# ==============================================================================

try:
    # พยายามนำเข้าจาก Week_1 (สำหรับการพัฒนาบน PC)
    # Try to import from Week_1 (for PC development)
    import sys
    sys.path.insert(0, '../Week_1')
    from pins import *

except ImportError:
    # ถ้านำเข้าไม่ได้ ให้กำหนดค่าเอง (สำหรับ ESP32 deployment)
    # If import fails, define locally (for ESP32 deployment)

    # ==============================================================================
    # LED แสดงสถานะ (Status LEDs)
    # ==============================================================================
    LED_RED   = 2     # GPIO2  - LED สีแดง (Red LED)
    LED_GREEN = 4     # GPIO4  - LED สีเขียว (Green LED)

    # ==============================================================================
    # ปุ่มกด (Push Buttons) - Input-only, no internal pull-up
    # ==============================================================================
    BUTTON1 = 34      # GPIO34 - ปุ่ม SELECT (SELECT button)
    BUTTON2 = 35      # GPIO35 - ปุ่ม UP (UP button)
    BUTTON3 = 39      # GPIO39 - ปุ่ม DOWN (DOWN button)

    # ==============================================================================
    # เซ็นเซอร์ (Sensors)
    # ==============================================================================
    DS18B20_PIN = 16  # GPIO16 - เซ็นเซอร์อุณหภูมิ DS18B20 (Temperature sensor)
    PH_PIN = 25       # GPIO25 - เซ็นเซอร์ pH (pH sensor ADC input)

    # ==============================================================================
    # ตัวต้านทานปรับค่าได้ (Potentiometers)
    # ==============================================================================
    POT1_PIN = 32     # GPIO32 - Potentiometer 1
    POT2_PIN = 33     # GPIO33 - Potentiometer 2

    # ==============================================================================
    # อุปกรณ์ควบคุม (Actuators)
    # ==============================================================================
    BUZZER_PIN = 26   # GPIO26 - Buzzer (PWM output)
    PUMP_PIN = 21     # GPIO21 - ปั๊มหลัก (Main pump, PWM output)
    CONTROL_2 = 22    # GPIO22 - ช่องควบคุมเสริม (Secondary control)
    RELAY_PIN = 17    # GPIO17 - รีเลย์ (Relay control)

    # ==============================================================================
    # จอแสดงผล TFT (TFT Display - ILI9341)
    # ==============================================================================
    TFT_SCK  = 14     # GPIO14 - TFT SPI Clock
    TFT_MOSI = 13     # GPIO13 - TFT SPI Data Out
    TFT_DC   = 27     # GPIO27 - TFT Data/Command
    TFT_CS   = 15     # GPIO15 - TFT Chip Select
    TFT_RST  = 0      # GPIO0  - TFT Reset
    TFT_SPI_BUS = 1   # SPI Bus 1
    TFT_BAUDRATE = 40000000  # 40 MHz

    # ==============================================================================
    # การ์ด SD (SD Card - SoftSPI)
    # ==============================================================================
    SD_MISO = 19      # GPIO19 - SD Card MISO
    SD_MOSI = 23      # GPIO23 - SD Card MOSI
    SD_SCK  = 18      # GPIO18 - SD Card SCK
    SD_CS   = 5       # GPIO5  - SD Card CS
    SD_BAUDRATE = 1000000  # 1 MHz

    # ==============================================================================
    # เซ็นเซอร์ระดับ (Level Sensors - Optional)
    # ==============================================================================
    LEVEL_1 = None    # ยังไม่กำหนด (Not assigned)
    LEVEL_2 = None    # ยังไม่กำหนด (Not assigned)

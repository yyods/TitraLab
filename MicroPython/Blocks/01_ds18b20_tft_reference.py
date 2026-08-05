# ==============================================================================
# 01_ds18b20_tft_reference.py - โค้ดอ้างอิงของตัวอย่าง Blocks: DS18B20 -> TFT
# Reference code for the Blocks example: DS18B20 temperature on the TFT
# ==============================================================================
# ไฟล์นี้คือ "โค้ด Python ที่บล็อกสร้างขึ้น" ของตัวอย่างใน 01_ds18b20_tft.md
# ใช้เทียบกับแผง Python preview ในแอป หรือรันตรง ๆ เพื่อทดสอบฮาร์ดแวร์
# This is the Python the block program generates (see 01_ds18b20_tft.md).
# Compare it with the app's Python preview, or run it directly to test hardware.
#
# ฮาร์ดแวร์ (Hardware): DS18B20 ที่ GPIO16 (jumper) + ตัวต้านทาน pull-up 4.7 kOhm
# ==============================================================================

import scilabpro as slp
import time

# --- [Raw Python บล็อกที่ 1: เตรียมจอ TFT ทำครั้งเดียว] ---
import gc
gc.collect()
from machine import Pin, SPI
from ili9341 import Display, color565
from xglcd_font import XglcdFont
slp.release_tft()
spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0),
                  width=320, height=240, rotation=90)
font = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
display.clear(color565(0, 0, 0), hlines=2)
display.draw_text(20, 20, 'DS18B20 Temperature', font, color565(0, 255, 255))

# --- [บล็อก Forever] ---
while True:
    if slp.stop_requested():
        break
    # --- [บล็อก Set variable: temp = Read DS18B20 (C) on pin 16] ---
    temp = slp.ds18b20(16).read_c()
    # --- [บล็อก Print value] ---
    print(temp)
    # --- [Raw Python บล็อกที่ 2: แสดงค่าบนจอ] ---
    display.fill_rectangle(20, 70, 280, 30, color565(0, 0, 0))
    display.draw_text(20, 72, 'T = {:.1f} C'.format(temp), font,
                      color565(255, 255, 0))
    # --- [บล็อก Sleep s: 1] ---
    time.sleep(1)

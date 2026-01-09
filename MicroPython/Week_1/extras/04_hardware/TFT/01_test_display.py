# ==============================================================================
# 01_test_display.py - การทดสอบจอ TFT (TFT Display Test)
# ==============================================================================
# โปรแกรมนี้สาธิตการแสดงผลบนจอ TFT ILI9341 ผ่าน SPI
# This program demonstrates displaying on TFT ILI9341 via SPI
# กด Ctrl+C เพื่อหยุดโปรแกรม (Press Ctrl+C to stop)
# ==============================================================================

from time import sleep, ticks_ms
from ili9341 import Display, color565
from machine import Pin, SPI
from xglcd_font import XglcdFont

# ==============================================================================
# การกำหนดขา GPIO สำหรับ LED และปุ่มกด
# GPIO pin assignments for LED and button
# ==============================================================================
led = Pin(2, Pin.OUT)       # LED สีแดง GPIO2 (Red LED)
push_button = Pin(34, Pin.IN)  # ปุ่มกด 1 GPIO34 (Button 1)

# ==============================================================================
# สีที่ใช้งานบ่อย (Commonly used colors)
# รูปแบบ RGB565: color565(R, G, B) โดย R, G, B มีค่า 0-255
# RGB565 format: color565(R, G, B) where R, G, B are 0-255
# ==============================================================================
colors = {
    "RED": color565(255, 0, 0),
    "GREEN": color565(0, 255, 0),
    "BLUE": color565(0, 0, 255),
    "YELLOW": color565(255, 255, 0),
    "AQUA": color565(0, 255, 255),
    "WHITE": color565(255, 255, 255),
    "BLACK": color565(0, 0, 0),
    "ORANGE": color565(255, 128, 0),
    "PURPLE": color565(128, 0, 128),
}

def init_display():
    """
    เริ่มต้นการทำงานของจอ TFT (Initialize TFT display)
    """
    print("กำลังเริ่มต้นจอ TFT... (Initializing TFT display...)")

    # ตั้งค่า SPI Bus 1 ที่ความเร็ว 40 MHz
    # Setup SPI Bus 1 at 40 MHz
    spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))

    # สร้าง Display object
    # Create Display object
    display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0),
                      width=320, height=240, rotation=90)

    return display

def test_display(display):
    """
    ทดสอบการแสดงผลบนจอ TFT (Test TFT display output)
    """
    # โหลดฟอนต์ (Load font)
    print("กำลังโหลดฟอนต์... (Loading font...)")
    arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)

    # แสดงข้อความบนจอ (Display text on screen)
    display.draw_text(120, 20, 'TiTralab', arcadepix, colors["WHITE"])
    display.draw_text(90, 70, 'from Thonny.', arcadepix, colors["YELLOW"])
    display.draw_text(60, 120, 'Press button!', arcadepix, colors["AQUA"])

    print("แสดงผลสำเร็จ (Display successful)")

    return arcadepix

# ==============================================================================
# โปรแกรมหลัก (Main program)
# ==============================================================================
print("=" * 50)
print("ทดสอบจอ TFT ILI9341 (TFT ILI9341 Test)")
print("=" * 50)

# เริ่มต้นจอแสดงผล (Initialize display)
display = init_display()
font = test_display(display)

print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
print("กดปุ่มเพื่อเปิด/ปิด LED (Press button to toggle LED)")

try:
    while True:
        # อ่านสถานะปุ่มกด (Read button state)
        logic_state = push_button.value()

        if logic_state == 1:  # ถ้ากดปุ่ม (if button pressed)
            led.value(1)      # เปิด LED (turn LED on)
        else:                 # ถ้าไม่ได้กดปุ่ม (if button not pressed)
            led.value(0)      # ปิด LED (turn LED off)

        # หน่วงเวลาเล็กน้อย (Small delay)
        sleep(0.01)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ปิด LED (Turn off LED)
    led.value(0)
    print("ปิด LED แล้ว (LED turned off)")

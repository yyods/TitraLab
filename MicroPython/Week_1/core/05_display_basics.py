# ==============================================================================
# 05_display_basics.py - TFT Display Basics for TitraLab
# ==============================================================================
# Week 1 Core: Basic TFT ILI9341 display operations
#
# Chemistry Context: Display shows pH, temperature, volume during titration
#
# TFT Pins (ILI9341 via SPI1):
#   SCK=GPIO14, MOSI=GPIO13, DC=GPIO27, CS=GPIO15, RST=GPIO0
# ==============================================================================

from machine import Pin, SPI
from ili9341 import Display, color565
from xglcd_font import XglcdFont
import time

# Colors (RGB565)
WHITE = color565(255, 255, 255)
BLACK = color565(0, 0, 0)
RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
CYAN = color565(0, 255, 255)


def init_display():
    """เริ่มต้นจอ TFT (Initialize TFT display)"""
    spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0),
                      width=320, height=240, rotation=90)
    print("TFT Display initialized (320x240)")
    return display


def load_font(filename='fonts/EspressoDolce18x24.c'):
    """โหลดฟอนต์ (Load font from fonts/ folder)"""
    return XglcdFont(filename, 18, 24)


# ==============================================================================
# Basic Display Functions
# ==============================================================================

def clear_screen(display, color=BLACK):
    """ล้างจอ (Clear screen)"""
    display.clear(color)


def draw_text(display, font, x, y, text, color=WHITE):
    """วาดข้อความ (Draw text)"""
    display.draw_text(x, y, text, font, color)


def draw_value_box(display, font, x, y, label, value, unit, color=GREEN):
    """วาดกล่องแสดงค่า (Draw labeled value box)"""
    display.fill_rectangle(x, y, 150, 30, BLACK)  # Clear area
    text = f"{label}: {value} {unit}"
    display.draw_text(x, y, text, font, color)


def draw_status_bar(display, font, status):
    """วาดแถบสถานะ (Draw status bar at top)"""
    display.fill_rectangle(0, 0, 320, 30, BLUE)
    display.draw_text(10, 5, status, font, WHITE)


# ==============================================================================
# Demo
# ==============================================================================

if __name__ == "__main__":
    print("=" * 40)
    print("TFT Display Basics Demo")
    print("=" * 40)

    display = init_display()
    font = load_font()

    try:
        clear_screen(display)

        # Status bar
        draw_status_bar(display, font, "TitraLab v1.0")

        # Title
        draw_text(display, font, 80, 50, "Titration Monitor", WHITE)

        # Simulated values
        draw_value_box(display, font, 50, 100, "pH", "7.00", "", GREEN)
        draw_value_box(display, font, 50, 140, "Temp", "25.5", "C", CYAN)
        draw_value_box(display, font, 50, 180, "Vol", "10.5", "mL", YELLOW)

        print("Display ready! Ctrl+C to exit")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        display.clear()
        print("Done!")

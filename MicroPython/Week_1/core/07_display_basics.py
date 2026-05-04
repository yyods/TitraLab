# ==============================================================================
# 07_display_basics.py - TFT Display for pH and Titration Monitoring
# ==============================================================================
# จอแสดงผล TFT ILI9341 สำหรับแสดงค่า pH และข้อมูลการไทเทรชัน
# TFT ILI9341 Display for pH Values and Titration Data Monitoring
# ==============================================================================
#
# ความสำคัญของจอแสดงผลในการไทเทรชัน (Display Importance in Titration):
# ======================================================================
# ในการไทเทรชันอัตโนมัติ จอแสดงผลมีบทบาทสำคัญ:
# In automated titration, the display plays a crucial role:
#
# 1. แสดงค่า pH แบบ real-time (Show real-time pH values)
#    - นักศึกษาสังเกตการเปลี่ยนแปลง pH ได้ทันที
#    - Students can observe pH changes immediately
#
# 2. แสดงอุณหภูมิสำหรับ compensation (Show temperature for compensation)
#    - อุณหภูมิมีผลต่อความชันตามสมการ Nernst
#    - Temperature affects slope per Nernst equation
#
# 3. แสดงปริมาตรสารละลายที่เติม (Show added solution volume)
#    - ติดตามปริมาณสารไทแทรนต์ที่ใช้
#    - Track titrant volume used
#
# 4. แสดงกราฟไทเทรชัน (Show titration curve) - Week 3
#    - วาดกราฟ pH vs Volume แบบ real-time
#    - Draw pH vs Volume graph in real-time
#
# Hardware Connection (การต่อวงจร):
#   TFT_SCK  = GPIO14 (SPI Clock)
#   TFT_MOSI = GPIO13 (SPI Data)
#   TFT_DC   = GPIO27 (Data/Command select)
#   TFT_CS   = GPIO15 (Chip Select)
#   TFT_RST  = GPIO0  (Reset - also boot mode pin)
#   Resolution: 320x240 pixels, 16-bit color (RGB565)
# ==============================================================================

from machine import Pin, SPI
from ili9341 import Display, color565
from xglcd_font import XglcdFont
import time

# === ค่าคงที่ขา GPIO สำหรับ TFT (TFT GPIO Pin Constants) ===
TFT_SCK = 14     # SPI Clock
TFT_MOSI = 13    # SPI Data (Master Out Slave In)
TFT_DC = 27      # Data/Command select
TFT_CS = 15      # Chip Select
TFT_RST = 0      # Reset pin

# === สี RGB565 สำหรับการแสดงผล (RGB565 Colors for Display) ===
# RGB565 format: 5 bits red, 6 bits green, 5 bits blue
BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)
RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
CYAN = color565(0, 255, 255)
ORANGE = color565(255, 165, 0)

# === สีสำหรับแสดงค่า pH (pH Display Colors) ===
# สีตามช่วง pH (Colors based on pH range)
PH_ACIDIC = color565(255, 100, 100)    # แดงอ่อน สำหรับกรด (Light red for acidic)
PH_NEUTRAL = color565(100, 255, 100)   # เขียวอ่อน สำหรับกลาง (Light green for neutral)
PH_BASIC = color565(100, 100, 255)     # น้ำเงินอ่อน สำหรับเบส (Light blue for basic)


def init_display(rotation=90):
    """
    เริ่มต้นจอแสดงผล TFT ILI9341 (Initialize TFT ILI9341 Display)

    การเชื่อมต่อ SPI ใช้ Bus 1 ของ ESP32 ที่ความเร็ว 40 MHz
    SPI connection uses ESP32 Bus 1 at 40 MHz speed.

    Args:
        rotation: มุมหมุนจอ (display rotation) - 0, 90, 180, 270

    Returns:
        Display: ออบเจกต์จอแสดงผล (display object)
    """
    # สร้าง SPI bus สำหรับ TFT (Create SPI bus for TFT)
    spi = SPI(1, baudrate=40000000, sck=Pin(TFT_SCK), mosi=Pin(TFT_MOSI))

    # สร้างออบเจกต์จอแสดงผล (Create display object)
    display = Display(
        spi,
        dc=Pin(TFT_DC),
        cs=Pin(TFT_CS),
        rst=Pin(TFT_RST),
        width=320,
        height=240,
        rotation=rotation
    )

    print(f"TFT Display พร้อมใช้งาน (ready) - 320x240 @ rotation={rotation}")
    return display


def load_font(filename='fonts/EspressoDolce18x24.c'):
    """
    โหลดฟอนต์สำหรับแสดงข้อความ (Load font for text display)

    ฟอนต์ EspressoDolce ขนาด 18x24 pixels เหมาะสำหรับแสดงค่าตัวเลข
    EspressoDolce font 18x24 pixels is suitable for displaying numeric values.

    Args:
        filename: path ไปยังไฟล์ฟอนต์ (path to font file)

    Returns:
        XglcdFont: ออบเจกต์ฟอนต์ (font object)
    """
    try:
        font = XglcdFont(filename, 18, 24)
        print(f"โหลดฟอนต์สำเร็จ (Font loaded): {filename}")
        return font
    except Exception as e:
        print(f"ข้อผิดพลาดโหลดฟอนต์ (Font load error): {e}")
        return None


# ==============================================================================
# ฟังก์ชันพื้นฐาน (Basic Functions)
# ==============================================================================

def clear_screen(display, color=BLACK):
    """
    ล้างหน้าจอด้วยสีที่กำหนด (Clear screen with specified color)

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        color: สีพื้นหลัง (background color)
    """
    display.clear(color)


def draw_text(display, font, x, y, text, color=WHITE):
    """
    วาดข้อความบนจอ (Draw text on display)

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        x, y: ตำแหน่ง (position)
        text: ข้อความ (text string)
        color: สีข้อความ (text color)
    """
    display.draw_text(x, y, text, font, color)


# ==============================================================================
# ฟังก์ชันสำหรับการไทเทรชัน (Titration-Specific Functions)
# ==============================================================================

def get_ph_color(ph_value):
    """
    เลือกสีตามค่า pH (Select color based on pH value)

    ใช้สีเพื่อให้นักศึกษาเข้าใจลักษณะของสารละลายได้ทันที
    Use colors to help students immediately understand solution characteristics.

    pH < 6.5  -> แดง (กรด/acidic)
    pH 6.5-7.5 -> เขียว (กลาง/neutral)
    pH > 7.5  -> น้ำเงิน (เบส/basic)

    Args:
        ph_value: ค่า pH (pH value)

    Returns:
        int: สี RGB565 (RGB565 color)
    """
    if ph_value < 6.5:
        return PH_ACIDIC
    elif ph_value > 7.5:
        return PH_BASIC
    else:
        return PH_NEUTRAL


def draw_ph_display(display, font, ph_value):
    """
    แสดงค่า pH บนหน้าจอ พร้อมสีตามช่วง pH (Display pH value with color coding)

    แสดงค่า pH ขนาดใหญ่ตรงกลางจอ เพื่อให้อ่านค่าได้ง่าย
    Display large pH value in center for easy reading.

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        ph_value: ค่า pH ที่จะแสดง (pH value to display)
    """
    # ล้างพื้นที่แสดง pH (Clear pH display area)
    display.fill_rectangle(80, 80, 160, 50, BLACK)

    # เลือกสีตามค่า pH (Select color based on pH)
    ph_color = get_ph_color(ph_value)

    # แสดงค่า pH (Display pH value)
    ph_text = f"pH {ph_value:.2f}"
    display.draw_text(80, 90, ph_text, font, ph_color)


def draw_temperature_display(display, font, temp_celsius):
    """
    แสดงค่าอุณหภูมิบนหน้าจอ (Display temperature on screen)

    อุณหภูมิสำคัญสำหรับ Nernst compensation
    Temperature is important for Nernst compensation.

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        temp_celsius: อุณหภูมิเป็นเซลเซียส (temperature in Celsius)
    """
    # ล้างพื้นที่แสดงอุณหภูมิ (Clear temperature display area)
    display.fill_rectangle(80, 140, 160, 30, BLACK)

    # แสดงค่าอุณหภูมิ (Display temperature)
    temp_text = f"Temp {temp_celsius:.1f}C"
    display.draw_text(80, 145, temp_text, font, CYAN)


def draw_volume_display(display, font, volume_ml):
    """
    แสดงปริมาตรสารไทแทรนต์ที่เติม (Display added titrant volume)

    ใช้ติดตามปริมาณสารละลายที่ใช้ในการไทเทรชัน
    Used to track solution volume used in titration.

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        volume_ml: ปริมาตรเป็น mL (volume in mL)
    """
    # ล้างพื้นที่แสดงปริมาตร (Clear volume display area)
    display.fill_rectangle(80, 180, 160, 30, BLACK)

    # แสดงค่าปริมาตร (Display volume)
    vol_text = f"Vol {volume_ml:.2f}mL"
    display.draw_text(80, 185, vol_text, font, YELLOW)


def draw_status_bar(display, font, status_text):
    """
    แถบสถานะด้านบนของจอ (Status bar at top of screen)

    แสดงสถานะการทำงานของระบบ เช่น "Calibrating", "Titrating", "Complete"
    Shows system status like "Calibrating", "Titrating", "Complete"

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        status_text: ข้อความสถานะ (status message)
    """
    # วาดพื้นหลังแถบสถานะ (Draw status bar background)
    display.fill_rectangle(0, 0, 320, 30, BLUE)

    # วาดข้อความสถานะ (Draw status text)
    display.draw_text(10, 5, status_text, font, WHITE)


def draw_titration_screen(display, font, ph, temp, volume, status="TitraLab"):
    """
    แสดงหน้าจอไทเทรชันแบบเต็ม (Display complete titration screen)

    รวมข้อมูลทั้งหมดที่จำเป็นสำหรับการไทเทรชันในหน้าจอเดียว
    Combines all necessary titration information in a single screen.

    เชื่อมโยงกับ Week 3 (Connection to Week 3):
        Week 3 จะเพิ่มกราฟไทเทรชันที่ด้านล่างของจอนี้
        Week 3 will add titration graph at the bottom of this screen.

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        ph: ค่า pH (pH value)
        temp: อุณหภูมิเป็น C (temperature in C)
        volume: ปริมาตรเป็น mL (volume in mL)
        status: ข้อความสถานะ (status message)
    """
    # แถบสถานะ (Status bar)
    draw_status_bar(display, font, status)

    # ค่า pH (pH value)
    draw_ph_display(display, font, ph)

    # ค่าอุณหภูมิ (Temperature)
    draw_temperature_display(display, font, temp)

    # ปริมาตร (Volume)
    draw_volume_display(display, font, volume)


def draw_equivalence_point(display, font, volume_ml, ph_value):
    """
    แสดงจุดสมมูลที่ค้นพบ (Display detected equivalence point)

    เมื่อระบบตรวจพบจุดสมมูล จะแสดงข้อมูลนี้บนหน้าจอ
    When the system detects equivalence point, this information is displayed.

    Args:
        display: ออบเจกต์จอแสดงผล (display object)
        font: ออบเจกต์ฟอนต์ (font object)
        volume_ml: ปริมาตรที่จุดสมมูล (volume at equivalence point)
        ph_value: pH ที่จุดสมมูล (pH at equivalence point)
    """
    # แสดงข้อความ "Equivalence Point Found!" (Show message)
    display.fill_rectangle(0, 200, 320, 40, GREEN)
    display.draw_text(10, 205, "EQ POINT!", font, BLACK)
    display.draw_text(120, 205, f"V={volume_ml:.2f}mL", font, BLACK)


# ==============================================================================
# Demo: จำลองการแสดงผลระหว่างไทเทรชัน (Simulated Titration Display)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("TFT Display Demo - Titration Monitor")
    print("จำลองการแสดงผลระหว่างไทเทรชัน")
    print("=" * 50)

    # เริ่มต้นจอแสดงผล (Initialize display)
    display = init_display(rotation=90)
    font = load_font()

    if font is None:
        print("ไม่สามารถโหลดฟอนต์ได้ (Cannot load font)")
        print("ตรวจสอบว่ามีไฟล์ fonts/EspressoDolce18x24.c")
    else:
        try:
            # ล้างจอ (Clear screen)
            clear_screen(display)

            print("\n--- จำลองการไทเทรชัน (Simulating Titration) ---")
            print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")

            # ข้อมูลจำลอง: เส้นโค้งไทเทรชันกรดแก่-เบสแก่
            # Simulated data: Strong acid - strong base titration curve
            titration_data = [
                # (volume, pH) - จำลองการเปลี่ยนแปลง pH
                (0.0, 2.0),
                (2.0, 2.3),
                (4.0, 2.7),
                (6.0, 3.2),
                (8.0, 3.8),
                (9.0, 4.5),
                (9.5, 5.5),
                (10.0, 7.0),   # จุดสมมูล (equivalence point)
                (10.5, 9.5),
                (11.0, 10.5),
                (12.0, 11.2),
                (14.0, 11.8),
            ]

            # อุณหภูมิจำลอง (Simulated temperature)
            temp = 25.5

            for volume, ph in titration_data:
                # แสดงหน้าจอไทเทรชัน (Display titration screen)
                draw_titration_screen(display, font, ph, temp, volume, "Titrating...")

                # แสดงข้อมูลใน console ด้วย (Also show in console)
                ph_type = "acidic" if ph < 6.5 else "basic" if ph > 7.5 else "neutral"
                print(f"Vol: {volume:5.1f} mL | pH: {ph:5.2f} ({ph_type})")

                # ตรวจจับจุดสมมูล (Detect equivalence point)
                if 6.5 <= ph <= 7.5 and volume > 0:
                    draw_equivalence_point(display, font, volume, ph)
                    print(f">>> จุดสมมูลที่ {volume:.2f} mL, pH {ph:.2f}")

                time.sleep(1)

            # สถานะเสร็จสิ้น (Complete status)
            draw_status_bar(display, font, "Complete!")
            print("\n--- การไทเทรชันเสร็จสิ้น (Titration Complete) ---")

            print("\n" + "=" * 50)
            print("ใน Week 3: จอนี้จะแสดงกราฟ pH vs Volume แบบ real-time")
            print("In Week 3: This display will show real-time pH vs Volume graph")
            print("=" * 50)

            # รอจนกว่าจะกด Ctrl+C (Wait until Ctrl+C)
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nหยุดโปรแกรม (Program stopped)")

        finally:
            # ล้างจอก่อนจบ (Clear screen before exit)
            clear_screen(display)
            print("ล้างจอแล้ว (Screen cleared)")

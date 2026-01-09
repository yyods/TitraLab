# ==============================================================================
# display.py - คลาส Display สำหรับจอ TFT ILI9341 (Display Class for ILI9341 TFT)
# ==============================================================================
# โมดูลนี้เป็น wrapper class สำหรับไดรเวอร์ ILI9341 เพื่อให้ใช้งานง่ายขึ้น
# This module is a wrapper class for the ILI9341 driver for easier usage
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การสร้าง wrapper class เพื่อซ่อนความซับซ้อน (Encapsulation)
# 2. เข้าใจการจัดการทรัพยากรฮาร์ดแวร์ (Hardware Resource Management)
# 3. ฝึกการออกแบบ API ที่ใช้งานง่าย (User-friendly API Design)
#
# การเชื่อมต่อฮาร์ดแวร์ (Hardware Connection):
# - SCK:  GPIO14  (SPI Clock)
# - MOSI: GPIO13  (SPI Data Out)
# - DC:   GPIO27  (Data/Command)
# - CS:   GPIO15  (Chip Select)
# - RST:  GPIO0   (Reset)
# - ขนาดจอ: 320x240 pixels (Display Size)
# ==============================================================================

from machine import Pin, SPI
from ili9341 import Display as ILI9341Display, color565

# ==============================================================================
# ค่าคงที่สำหรับสี (Color Constants)
# ==============================================================================
# กำหนดสีมาตรฐานในรูปแบบ RGB565 สำหรับการแสดงผล
# Define standard colors in RGB565 format for display

class Colors:
    """
    คลาสเก็บค่าสีมาตรฐาน (Standard Color Constants Class)

    รูปแบบ RGB565: 5 บิตแดง, 6 บิตเขียว, 5 บิตน้ำเงิน = 16 บิต
    RGB565 format: 5 bits red, 6 bits green, 5 bits blue = 16 bits
    """
    # สีพื้นฐาน (Basic Colors)
    BLACK   = color565(0, 0, 0)
    WHITE   = color565(255, 255, 255)
    RED     = color565(255, 0, 0)
    GREEN   = color565(0, 255, 0)
    BLUE    = color565(0, 0, 255)

    # สีเพิ่มเติม (Additional Colors)
    YELLOW  = color565(255, 255, 0)
    CYAN    = color565(0, 255, 255)
    MAGENTA = color565(255, 0, 255)
    ORANGE  = color565(255, 165, 0)

    # สีสำหรับ UI (UI Colors)
    HEADER_BG    = color565(0, 102, 204)    # พื้นหลังส่วนหัว (Header background)
    HIGHLIGHT    = color565(0, 255, 0)       # ไฮไลท์ (Highlight)
    TEXT_PRIMARY = color565(255, 255, 255)   # ข้อความหลัก (Primary text)
    TEXT_WARNING = color565(255, 193, 34)    # ข้อความเตือน (Warning text)
    TEXT_ERROR   = color565(255, 51, 51)     # ข้อความผิดพลาด (Error text)
    TEXT_SUCCESS = color565(0, 255, 0)       # ข้อความสำเร็จ (Success text)
    TEXT_INFO    = color565(102, 255, 255)   # ข้อความข้อมูล (Info text)


# ==============================================================================
# คลาส Display (Display Class)
# ==============================================================================
class Display:
    """
    คลาส wrapper สำหรับจอ TFT ILI9341 (Wrapper class for ILI9341 TFT display)

    คลาสนี้ห่อหุ้มไดรเวอร์ ILI9341 และเพิ่มฟังก์ชันช่วยเหลือสำหรับ
    การแสดงผล UI ของระบบไทเทรชัน

    This class wraps the ILI9341 driver and adds helper functions for
    titration system UI display.

    Attributes:
        width (int): ความกว้างจอ (Display width) - 320 pixels
        height (int): ความสูงจอ (Display height) - 240 pixels
        font: ฟอนต์สำหรับแสดงข้อความ (Font for text display)
    """

    # ค่าคงที่ขา GPIO (GPIO Pin Constants)
    PIN_SCK  = 14   # SPI Clock
    PIN_MOSI = 13   # SPI Master Out Slave In
    PIN_DC   = 27   # Data/Command
    PIN_CS   = 15   # Chip Select
    PIN_RST  = 0    # Reset

    # ค่าคงที่ขนาดจอ (Display Size Constants)
    WIDTH  = 320
    HEIGHT = 240

    def __init__(self, rotation=90, font=None):
        """
        สร้างออบเจ็กต์ Display (Create Display object)

        Args:
            rotation (int): มุมหมุนจอ 0, 90, 180, 270 องศา (Display rotation)
            font: ออบเจ็กต์ฟอนต์ XglcdFont (XglcdFont object)

        Example:
            from xglcd_font import XglcdFont
            font = XglcdFont('EspressoDolce18x24.c', 18, 24)
            display = Display(rotation=90, font=font)
        """
        # ตั้งค่า SPI สำหรับจอ TFT (Setup SPI for TFT display)
        self._spi = SPI(
            1,  # SPI bus 1
            baudrate=40000000,  # 40 MHz สำหรับความเร็วสูง (for high speed)
            sck=Pin(self.PIN_SCK),
            mosi=Pin(self.PIN_MOSI)
        )

        # สร้างออบเจ็กต์จอแสดงผล (Create display object)
        self._display = ILI9341Display(
            self._spi,
            dc=Pin(self.PIN_DC),
            cs=Pin(self.PIN_CS),
            rst=Pin(self.PIN_RST),
            width=self.WIDTH,
            height=self.HEIGHT,
            rotation=rotation
        )

        # เก็บฟอนต์สำหรับใช้งาน (Store font for usage)
        self.font = font

        # กำหนดขนาดจอตาม rotation (Set display size based on rotation)
        if rotation in (90, 270):
            self.width = self.WIDTH
            self.height = self.HEIGHT
        else:
            self.width = self.HEIGHT
            self.height = self.WIDTH

    # ==========================================================================
    # เมธอดพื้นฐาน (Basic Methods)
    # ==========================================================================

    def clear(self, color=Colors.BLACK):
        """
        ล้างหน้าจอด้วยสีที่กำหนด (Clear screen with specified color)

        Args:
            color (int): สี RGB565 (RGB565 color), default=BLACK
        """
        self._display.clear(color)

    def fill_rect(self, x, y, width, height, color):
        """
        วาดสี่เหลี่ยมทึบ (Draw filled rectangle)

        Args:
            x (int): ตำแหน่ง X เริ่มต้น (Starting X position)
            y (int): ตำแหน่ง Y เริ่มต้น (Starting Y position)
            width (int): ความกว้าง (Width)
            height (int): ความสูง (Height)
            color (int): สี RGB565 (RGB565 color)
        """
        self._display.fill_rectangle(x, y, width, height, color)

    def draw_rect(self, x, y, width, height, color):
        """
        วาดกรอบสี่เหลี่ยม (Draw rectangle outline)

        Args:
            x (int): ตำแหน่ง X เริ่มต้น (Starting X position)
            y (int): ตำแหน่ง Y เริ่มต้น (Starting Y position)
            width (int): ความกว้าง (Width)
            height (int): ความสูง (Height)
            color (int): สี RGB565 (RGB565 color)
        """
        self._display.draw_rectangle(x, y, width, height, color)

    def draw_line(self, x1, y1, x2, y2, color):
        """
        วาดเส้นตรง (Draw line)

        Args:
            x1, y1 (int): จุดเริ่มต้น (Start point)
            x2, y2 (int): จุดสิ้นสุด (End point)
            color (int): สี RGB565 (RGB565 color)
        """
        self._display.draw_line(x1, y1, x2, y2, color)

    def draw_hline(self, x, y, width, color):
        """
        วาดเส้นแนวนอน (Draw horizontal line)

        Args:
            x, y (int): จุดเริ่มต้น (Start point)
            width (int): ความยาวเส้น (Line width)
            color (int): สี RGB565 (RGB565 color)
        """
        self._display.draw_hline(x, y, width, color)

    def draw_vline(self, x, y, height, color):
        """
        วาดเส้นแนวตั้ง (Draw vertical line)

        Args:
            x, y (int): จุดเริ่มต้น (Start point)
            height (int): ความยาวเส้น (Line height)
            color (int): สี RGB565 (RGB565 color)
        """
        self._display.draw_vline(x, y, height, color)

    # ==========================================================================
    # เมธอดแสดงข้อความ (Text Display Methods)
    # ==========================================================================

    def draw_text(self, x, y, text, color=Colors.WHITE, background=Colors.BLACK):
        """
        แสดงข้อความด้วยฟอนต์ที่กำหนด (Display text with specified font)

        Args:
            x (int): ตำแหน่ง X (X position)
            y (int): ตำแหน่ง Y (Y position)
            text (str): ข้อความที่จะแสดง (Text to display)
            color (int): สีข้อความ (Text color)
            background (int): สีพื้นหลัง (Background color)

        Note:
            ต้องกำหนด font ใน constructor ก่อนใช้งาน
            Font must be set in constructor before use
        """
        if self.font is None:
            # ใช้ฟอนต์ 8x8 ในตัว ถ้าไม่มีฟอนต์กำหนด
            # Use built-in 8x8 font if no font specified
            self._display.draw_text8x8(x, y, text, color, background)
        else:
            self._display.draw_text(x, y, text, self.font, color, background)

    def draw_text_centered(self, y, text, color=Colors.WHITE, background=Colors.BLACK):
        """
        แสดงข้อความตรงกลางจอ (Display centered text)

        Args:
            y (int): ตำแหน่ง Y (Y position)
            text (str): ข้อความที่จะแสดง (Text to display)
            color (int): สีข้อความ (Text color)
            background (int): สีพื้นหลัง (Background color)
        """
        # คำนวณตำแหน่ง X ให้อยู่ตรงกลาง (Calculate X position for center)
        if self.font:
            text_width = len(text) * self.font.width
        else:
            text_width = len(text) * 8  # 8x8 font

        x = (self.width - text_width) // 2
        self.draw_text(x, y, text, color, background)

    # ==========================================================================
    # เมธอดสำหรับ UI (UI Methods)
    # ==========================================================================

    def draw_header(self, title, bg_color=Colors.HEADER_BG, text_color=Colors.WHITE):
        """
        วาดส่วนหัวของหน้าจอ (Draw screen header)

        Args:
            title (str): ชื่อหัวข้อ (Header title)
            bg_color (int): สีพื้นหลัง (Background color)
            text_color (int): สีข้อความ (Text color)
        """
        # วาดพื้นหลังส่วนหัว (Draw header background)
        self.fill_rect(0, 0, self.width, 30, bg_color)

        # แสดงข้อความหัวข้อตรงกลาง (Display centered title)
        self.draw_text_centered(5, title, text_color, bg_color)

    def draw_status_bar(self, status_text, color=Colors.TEXT_INFO):
        """
        วาดแถบสถานะด้านล่าง (Draw bottom status bar)

        Args:
            status_text (str): ข้อความสถานะ (Status text)
            color (int): สีข้อความ (Text color)
        """
        # ล้างพื้นที่แถบสถานะ (Clear status bar area)
        self.fill_rect(0, self.height - 25, self.width, 25, Colors.BLACK)

        # แสดงข้อความสถานะ (Display status text)
        self.draw_text(10, self.height - 22, status_text, color)

    def draw_progress_bar(self, x, y, width, height, progress,
                          fg_color=Colors.GREEN, bg_color=Colors.WHITE):
        """
        วาดแถบความคืบหน้า (Draw progress bar)

        Args:
            x, y (int): ตำแหน่ง (Position)
            width, height (int): ขนาด (Size)
            progress (float): ความคืบหน้า 0.0-1.0 (Progress 0.0-1.0)
            fg_color (int): สีแถบ (Bar color)
            bg_color (int): สีพื้นหลัง (Background color)
        """
        # วาดกรอบ (Draw border)
        self.draw_rect(x, y, width, height, bg_color)

        # คำนวณความกว้างแถบ (Calculate bar width)
        bar_width = int((width - 4) * min(max(progress, 0), 1))

        # วาดแถบความคืบหน้า (Draw progress bar)
        if bar_width > 0:
            self.fill_rect(x + 2, y + 2, bar_width, height - 4, fg_color)

    def show_message(self, title, message, color=Colors.WHITE):
        """
        แสดงกล่องข้อความ (Display message box)

        Args:
            title (str): หัวข้อ (Title)
            message (str): ข้อความ (Message)
            color (int): สีข้อความ (Text color)
        """
        self.clear()
        self.draw_header(title)
        self.draw_text_centered(100, message, color)

    def show_error(self, message):
        """
        แสดงข้อความผิดพลาด (Display error message)

        Args:
            message (str): ข้อความผิดพลาด (Error message)
        """
        self.show_message("Error", message, Colors.RED)

    def show_success(self, message):
        """
        แสดงข้อความสำเร็จ (Display success message)

        Args:
            message (str): ข้อความ (Message)
        """
        self.show_message("Success", message, Colors.GREEN)

    # ==========================================================================
    # เมธอดจัดการทรัพยากร (Resource Management Methods)
    # ==========================================================================

    def cleanup(self):
        """
        ทำความสะอาดทรัพยากร (Clean up resources)

        เรียกเมธอดนี้เมื่อเลิกใช้งาน Display
        Call this method when done using Display
        """
        try:
            self._display.clear()
            self._display.display_off()
            self._spi.deinit()
            print("จอแสดงผลถูกปิดแล้ว (Display has been turned off)")
        except Exception as e:
            print(f"ข้อผิดพลาดขณะปิดจอ (Error closing display): {e}")

    def __enter__(self):
        """
        สำหรับใช้กับ with statement (For use with with statement)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        ทำความสะอาดอัตโนมัติเมื่อออกจาก with block
        Auto cleanup when exiting with block
        """
        self.cleanup()
        return False


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    from time import sleep_ms

    try:
        # โหลดฟอนต์ (Load font)
        from xglcd_font import XglcdFont
        font = XglcdFont('EspressoDolce18x24.c', 18, 24)

        # สร้างออบเจ็กต์ Display (Create Display object)
        display = Display(rotation=90, font=font)

        # แสดงตัวอย่าง UI (Display UI example)
        display.clear()
        display.draw_header("TitraLab Demo")
        display.draw_text(20, 50, "pH: 7.00", Colors.GREEN)
        display.draw_text(20, 80, "Temp: 25.0 C", Colors.YELLOW)
        display.draw_text(20, 110, "Volume: 0.0 mL", Colors.CYAN)
        display.draw_progress_bar(20, 150, 280, 20, 0.5)
        display.draw_status_bar("Ready")

        sleep_ms(5000)

    except Exception as e:
        print(f"ข้อผิดพลาด (Error): {e}")

    finally:
        # ทำความสะอาด (Cleanup)
        if 'display' in dir():
            display.cleanup()

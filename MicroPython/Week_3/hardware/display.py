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
# คลาส DisplayManager (Display Manager Class)
# ==============================================================================
class DisplayManager:
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
            font = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
            display = DisplayManager(rotation=90, font=font)
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
    # Lifecycle Methods (init/deinit)
    # ==========================================================================

    def init(self):
        """
        เริ่มต้นจอแสดงผล (Initialize display)

        เมธอดนี้ถูกเรียกโดย HardwareHub เพื่อเตรียมจอให้พร้อมใช้งาน
        This method is called by HardwareHub to prepare the display for use.
        """
        # ล้างจอและแสดงหน้าจอเริ่มต้น (Clear and show initial screen)
        self.clear()

    def deinit(self):
        """
        ปิดจอแสดงผล (Deinitialize display)

        เมธอดนี้ถูกเรียกเมื่อปิดโปรแกรม เพื่อทำความสะอาด resources
        This method is called on shutdown to clean up resources.
        """
        # ล้างจอก่อนปิด (Clear screen before shutdown)
        self.clear()
        # หมายเหตุ: SPI bus จะถูกจัดการโดย MicroPython GC
        # Note: SPI bus is managed by MicroPython garbage collector

    # ==========================================================================
    # เมธอดพื้นฐาน (Basic Methods)
    # ==========================================================================

    def clear(self, color=Colors.BLACK):
        """
        ล้างหน้าจอด้วยสีที่กำหนด (Clear screen with specified color)

        ใช้ hlines=1 เพื่อลดการใช้หน่วยความจำ (320*2*1=640 bytes)
        Uses hlines=1 to reduce memory usage (320*2*1=640 bytes)

        Args:
            color (int): สี RGB565 (RGB565 color), default=BLACK
        """
        self._display.clear(color, hlines=1)

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
            # วาดทีละตัวอักษร เพื่อใช้หน่วยความจำน้อย (128 bytes/ตัว แทน len*128)
            # Draw character-by-character to reduce memory (128 bytes/char vs len*128)
            for ch in text:
                self._display.draw_text8x8(x, y, ch, color, background)
                x += 8
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
        import gc
        gc.collect()
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

    def show_logo(self, title, subtitle=""):
        """
        แสดงหน้าจอโลโก้ (Display logo screen)

        แสดงชื่อโปรแกรมและคำอธิบายตรงกลางจอ
        Shows program title and description centered on screen

        Args:
            title (str): ชื่อโปรแกรม (Program title)
            subtitle (str): คำอธิบาย (Description)
        """
        self.clear()

        # วาดกรอบ (Draw border)
        self.draw_rect(5, 5, self.width - 10, self.height - 10, Colors.CYAN)
        self.draw_rect(8, 8, self.width - 16, self.height - 16, Colors.CYAN)

        # แสดงชื่อโปรแกรม (Show title)
        self.draw_text_centered(80, title, Colors.YELLOW)

        # แสดงคำอธิบาย (Show subtitle)
        if subtitle:
            self.draw_text_centered(120, subtitle, Colors.WHITE)

        # แสดงเวอร์ชัน (Show version)
        self.draw_text_centered(180, "Week 3 - OOP System", Colors.TEXT_INFO)

    # ==========================================================================
    # เมธอดสำหรับ Titration (Titration Display Methods)
    # ==========================================================================

    def show_titration_status(self, step, total_steps, volume, max_volume,
                               ph, temperature=None, status_text=None):
        """
        แสดงสถานะการไทเทรชัน (Display titration status)

        แสดงข้อมูลความคืบหน้าของการไทเทรชันบนหน้าจอ
        Shows titration progress information on screen

        Args:
            step (int): รอบปัจจุบัน (Current step/cycle)
            total_steps (int): รอบทั้งหมด (Total steps)
            volume (float): ปริมาตรที่จ่ายแล้ว (Dispensed volume in mL)
            max_volume (float): ปริมาตรสูงสุด (Maximum volume in mL)
            ph (float): ค่า pH ปัจจุบัน (Current pH value)
            temperature (float): อุณหภูมิ (Temperature in C, optional)
            status_text (str): ข้อความสถานะ (Status text, optional)
        """
        import gc
        gc.collect()
        self.clear()
        self.draw_header("Auto Titration")

        # คำนวณ progress (Calculate progress)
        progress = volume / max_volume if max_volume > 0 else 0

        # แสดง Step (Show step)
        step_text = f"Step: {step}/{total_steps}"
        self.draw_text(10, 40, step_text, Colors.WHITE)

        # แสดงปริมาตร (Show volume)
        vol_text = f"Vol: {volume:.2f}/{max_volume:.1f} mL"
        self.draw_text(10, 70, vol_text, Colors.CYAN)

        # แสดง pH (Show pH) - ขนาดใหญ่และเด่น (Large and prominent)
        ph_text = f"pH: {ph:.2f}"
        self.draw_text(10, 100, ph_text, Colors.GREEN)

        # แสดงอุณหภูมิถ้ามี (Show temperature if available)
        if temperature is not None:
            temp_text = f"Temp: {temperature:.1f} C"
            self.draw_text(180, 100, temp_text, Colors.YELLOW)

        # แสดง Progress Bar (Show progress bar)
        self.draw_text(10, 140, "Progress:", Colors.WHITE)
        self.draw_progress_bar(10, 165, 300, 20, progress, Colors.GREEN, Colors.WHITE)

        # แสดงเปอร์เซ็นต์ (Show percentage)
        percent_text = f"{progress * 100:.0f}%"
        self.draw_text(140, 190, percent_text, Colors.TEXT_INFO)

        # แสดงสถานะ (Show status)
        if status_text:
            self.draw_status_bar(status_text, Colors.TEXT_INFO)
        else:
            self.draw_status_bar("BTN3: Cancel", Colors.TEXT_WARNING)

    def show_titration_ready(self, sample_vol, max_vol, dose_vol, total_steps,
                             flow_rate=None, ph_equation=None):
        """
        แสดงหน้าจอพร้อมเริ่มไทเทรชัน (Display titration ready screen)

        แสดงข้อมูลการตั้งค่าและสถานะการสอบเทียบ รอกดปุ่มเริ่ม
        Shows configuration, calibration status, and waits for start button

        Args:
            sample_vol (float): ปริมาตรตัวอย่าง (Sample volume in mL)
            max_vol (float): ปริมาตรสูงสุด (Maximum volume in mL)
            dose_vol (float): ปริมาตรต่อครั้ง (Dose volume in mL)
            total_steps (int): จำนวน step ทั้งหมด (Total steps)
            flow_rate (float): อัตราการไหล mL/s (Flow rate, optional)
            ph_equation (tuple): (slope, intercept) สมการ pH (pH equation, optional)
        """
        import gc
        gc.collect()
        self.clear()
        self.draw_header("Auto Titration")

        # แสดงข้อมูลการตั้งค่า (Show configuration)
        y = 35
        self.draw_text(10, y, f"Sample: {sample_vol:.1f} mL", Colors.WHITE)
        y += 18
        self.draw_text(10, y, f"Max:{max_vol:.1f} Dose:{dose_vol:.2f}mL", Colors.CYAN)
        y += 18
        self.draw_text(10, y, f"Steps: {total_steps}", Colors.WHITE)
        y += 22

        # แสดงสถานะการสอบเทียบ (Show calibration status)
        if flow_rate is not None:
            self.draw_text(10, y, f"Flow: {flow_rate:.4f} mL/s", Colors.CYAN)
        else:
            self.draw_text(10, y, "Flow: DEFAULT!", Colors.YELLOW)
        y += 18

        if ph_equation is not None:
            slope, intercept = ph_equation
            self.draw_text(10, y, f"pH={slope:.6f}*mV", Colors.CYAN)
            y += 12
            self.draw_text(10, y, f"   +{intercept:.4f}", Colors.CYAN)
        else:
            self.draw_text(10, y, "pH: NOT CALIBRATED!", Colors.YELLOW)
        y += 22

        self.draw_text(10, y, "Press BTN1 to START", Colors.GREEN)

        # gc ก่อน status bar เพราะ fill_rect ต้องการ ~1920 bytes
        # GC before status bar since fill_rect needs ~1920 bytes
        gc.collect()
        self.draw_status_bar("BTN1:Start BTN3:Cancel", Colors.TEXT_WARNING)

    def show_titration_complete(self, total_vol, eq_vol=None, eq_ph=None, filename=None):
        """
        แสดงหน้าจอไทเทรชันเสร็จสิ้น (Display titration complete screen)

        Args:
            total_vol (float): ปริมาตรรวมที่จ่าย (Total dispensed volume in mL)
            eq_vol (float): ปริมาตรจุดสมมูล (Equivalence point volume, optional)
            eq_ph (float): pH จุดสมมูล (Equivalence point pH, optional)
            filename (str): ชื่อไฟล์ที่บันทึก (Saved filename, optional)
        """
        import gc
        gc.collect()
        self.clear()
        self.draw_header("Titration Complete")

        # แสดงปริมาตรรวม (Show total volume)
        self.draw_text(10, 50, f"Total: {total_vol:.2f} mL", Colors.CYAN)

        # แสดงจุดสมมูลถ้ามี (Show equivalence point if available)
        if eq_vol is not None and eq_ph is not None:
            self.draw_text(10, 85, "Equivalence Point:", Colors.YELLOW)
            self.draw_text(10, 115, f"  V = {eq_vol:.3f} mL", Colors.GREEN)
            self.draw_text(10, 145, f"  pH = {eq_ph:.3f}", Colors.GREEN)
        else:
            self.draw_text(10, 85, "Equiv. Point: N/A", Colors.TEXT_WARNING)

        # แสดงชื่อไฟล์ถ้ามี (Show filename if available)
        if filename:
            self.draw_text(10, 180, f"File: {filename}", Colors.TEXT_INFO)

        self.draw_status_bar("BTN1: Return to menu", Colors.WHITE)

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
        font = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)

        # สร้างออบเจ็กต์ DisplayManager (Create DisplayManager object)
        display = DisplayManager(rotation=90, font=font)

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

# ==============================================================================
# screens.py - คลาสสำหรับแสดงหน้าจอต่างๆ (Screen Rendering Classes)
# ==============================================================================
# โมดูลนี้รวบรวมคลาสสำหรับแสดงผลหน้าจอต่างๆ ในระบบไทเทรชัน
# This module contains classes for rendering various screens in titration system
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การออกแบบคลาสแบบ inheritance (Inheritance design)
# 2. เข้าใจการแยกส่วน UI ออกจาก logic (Separation of UI and logic)
# 3. ฝึกการสร้าง reusable UI components (Reusable UI components)
#
# หน้าจอที่รวมอยู่ (Included Screens):
# - MainMenuScreen: หน้าเมนูหลัก (Main menu)
# - CalibrationScreen: หน้าแสดงการสอบเทียบ (Calibration display)
# - TitrationScreen: หน้าแสดงการไทเทรต (Titration display)
# - ResultScreen: หน้าแสดงผลลัพธ์ (Results display)
# ==============================================================================

from time import sleep_ms


# ==============================================================================
# คลาส BaseScreen - คลาสพื้นฐานสำหรับหน้าจอทั้งหมด
# BaseScreen Class - Base class for all screens
# ==============================================================================
class BaseScreen:
    """
    คลาสพื้นฐานสำหรับหน้าจอทั้งหมด (Base class for all screens)

    คลาสนี้กำหนดโครงสร้างพื้นฐานที่หน้าจอทุกหน้าต้องมี
    This class defines the basic structure all screens must have

    Attributes:
        display: ออบเจ็กต์ Display สำหรับแสดงผล (Display object)
        colors: คลาส Colors สำหรับสี (Colors class)
    """

    def __init__(self, display, colors):
        """
        สร้างออบเจ็กต์ BaseScreen (Create BaseScreen object)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors จาก display module (Colors class)
        """
        self.display = display
        self.colors = colors

    def render(self):
        """
        วาดหน้าจอ - ต้อง override ในคลาสลูก (Draw screen - must override)

        Raises:
            NotImplementedError: ถ้าไม่ได้ implement ในคลาสลูก
        """
        raise NotImplementedError("คลาสลูกต้อง implement render() (Subclass must implement render())")

    def update(self, **kwargs):
        """
        อัปเดตเฉพาะส่วนที่เปลี่ยนแปลง (Update only changed parts)

        Args:
            **kwargs: ข้อมูลที่ต้องการอัปเดต (Data to update)
        """
        pass  # Optional override

    def clear(self):
        """
        ล้างหน้าจอ (Clear screen)
        """
        self.display.clear()


# ==============================================================================
# คลาส MainMenuScreen - หน้าเมนูหลัก
# MainMenuScreen Class - Main menu screen
# ==============================================================================
class MainMenuScreen(BaseScreen):
    """
    หน้าเมนูหลักของระบบ (Main menu screen)

    แสดงรายการเมนูทั้งหมดและไฮไลท์ตัวเลือกที่เลือกอยู่
    Displays all menu items and highlights the selected option

    Attributes:
        menu_items (list): รายการเมนู (Menu items list)
        selected_index (int): ดัชนีตัวเลือกที่เลือก (Selected option index)
    """

    # รายการเมนูมาตรฐาน (Standard menu items)
    DEFAULT_MENU_ITEMS = [
        "1. Calibrate pH Sensor",
        "2. pH Sensor Test",
        "3. Calibrate Flow Rate",
        "4. Flow Rate Test",
        "5. Purge",
        "6. Full Auto Titration"
    ]

    def __init__(self, display, colors, menu_items=None):
        """
        สร้างหน้าเมนูหลัก (Create main menu screen)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            menu_items (list): รายการเมนู หรือ None เพื่อใช้ค่าเริ่มต้น
        """
        super().__init__(display, colors)
        self.menu_items = menu_items if menu_items else self.DEFAULT_MENU_ITEMS
        self.selected_index = 0
        self._previous_index = -1  # สำหรับติดตามการเปลี่ยนแปลง (For tracking changes)

    def render(self):
        """
        วาดหน้าเมนูหลักทั้งหมด (Draw complete main menu screen)
        """
        self.display.clear()

        # วาดส่วนหัว (Draw header)
        self.display.draw_header("TitraLab Menu")

        # วาดรายการเมนูทั้งหมด (Draw all menu items)
        for i, item in enumerate(self.menu_items):
            self._draw_menu_item(i)

        # วาดคำแนะนำการใช้งาน (Draw usage instructions)
        self._draw_instructions()

        self._previous_index = self.selected_index

    def _draw_menu_item(self, index):
        """
        วาดรายการเมนูหนึ่งรายการ (Draw single menu item)

        Args:
            index (int): ดัชนีของรายการ (Item index)
        """
        y_position = 45 + index * 28  # ระยะห่างระหว่างรายการ (Item spacing)
        x_position = 20

        # กำหนดสีตามสถานะการเลือก (Set color based on selection)
        is_selected = (index == self.selected_index)
        text_color = self.colors.HIGHLIGHT if is_selected else self.colors.WHITE

        # วาดตัวบ่งชี้การเลือก (Draw selection indicator)
        indicator = ">" if is_selected else " "

        # ล้างพื้นที่เดิมก่อน (Clear previous area)
        self.display.fill_rect(0, y_position, self.display.width, 26, self.colors.BLACK)

        # วาดข้อความ (Draw text)
        self.display.draw_text(x_position, y_position, f"{indicator} {self.menu_items[index]}", text_color)

    def _draw_instructions(self):
        """
        วาดคำแนะนำการใช้งาน (Draw usage instructions)
        """
        y = self.display.height - 22
        self.display.fill_rect(0, y - 3, self.display.width, 25, self.colors.BLACK)
        self.display.draw_text(10, y, "UP/DOWN: Select  SEL: Confirm", self.colors.TEXT_INFO)

    def update(self, selected_index=None, **kwargs):
        """
        อัปเดตเฉพาะรายการที่เปลี่ยนแปลง (Update only changed items)

        Args:
            selected_index (int): ดัชนีใหม่ที่เลือก (New selected index)
        """
        if selected_index is not None and selected_index != self.selected_index:
            old_index = self.selected_index
            self.selected_index = selected_index

            # วาดใหม่เฉพาะรายการที่เปลี่ยน (Redraw only changed items)
            self._draw_menu_item(old_index)
            self._draw_menu_item(self.selected_index)

    def select_next(self):
        """
        เลือกรายการถัดไป (Select next item)

        Returns:
            int: ดัชนีใหม่ (New index)
        """
        new_index = (self.selected_index + 1) % len(self.menu_items)
        self.update(selected_index=new_index)
        return new_index

    def select_previous(self):
        """
        เลือกรายการก่อนหน้า (Select previous item)

        Returns:
            int: ดัชนีใหม่ (New index)
        """
        new_index = (self.selected_index - 1) % len(self.menu_items)
        self.update(selected_index=new_index)
        return new_index

    def get_selected(self):
        """
        รับดัชนีที่เลือกอยู่ (Get currently selected index)

        Returns:
            int: ดัชนีที่เลือก (Selected index)
        """
        return self.selected_index


# ==============================================================================
# คลาส CalibrationScreen - หน้าแสดงการสอบเทียบ
# CalibrationScreen Class - Calibration display screen
# ==============================================================================
class CalibrationScreen(BaseScreen):
    """
    หน้าแสดงผลการสอบเทียบ (Calibration display screen)

    ใช้สำหรับแสดงค่าขณะสอบเทียบ pH หรือ Flow Rate
    Used for displaying values during pH or Flow Rate calibration

    Attributes:
        title (str): หัวข้อหน้าจอ (Screen title)
        calibration_type (str): ประเภทการสอบเทียบ 'ph' หรือ 'flow'
    """

    def __init__(self, display, colors, title="Calibration", calibration_type='ph'):
        """
        สร้างหน้าสอบเทียบ (Create calibration screen)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            title (str): หัวข้อหน้าจอ (Screen title)
            calibration_type (str): 'ph' หรือ 'flow'
        """
        super().__init__(display, colors)
        self.title = title
        self.calibration_type = calibration_type
        self.current_values = {}

    def render(self, step=0, total_steps=3, buffer_ph=7.0, voltage=0.0,
               temperature=25.0, status="Ready"):
        """
        วาดหน้าสอบเทียบ (Draw calibration screen)

        Args:
            step (int): ขั้นตอนปัจจุบัน (Current step)
            total_steps (int): จำนวนขั้นตอนทั้งหมด (Total steps)
            buffer_ph (float): ค่า pH ของบัฟเฟอร์ (Buffer pH value)
            voltage (float): แรงดันไฟฟ้าที่วัดได้ mV (Measured voltage)
            temperature (float): อุณหภูมิ (Temperature)
            status (str): สถานะ (Status message)
        """
        self.display.clear()

        # วาดส่วนหัว (Draw header)
        self.display.draw_header(self.title)

        # แสดงขั้นตอน (Display step)
        step_text = f"Step {step}/{total_steps}"
        self.display.draw_text(20, 40, step_text, self.colors.CYAN)

        if self.calibration_type == 'ph':
            # แสดงค่า pH Buffer (Display pH buffer value)
            self.display.draw_text(20, 70, f"Buffer pH: {buffer_ph:.2f}", self.colors.WHITE)

            # แสดงแรงดันไฟฟ้า (Display voltage)
            self.display.draw_text(20, 100, f"Voltage: {voltage:.1f} mV", self.colors.YELLOW)

            # แสดงอุณหภูมิ (Display temperature)
            self.display.draw_text(20, 130, f"Temp: {temperature:.1f} C", self.colors.CYAN)

        elif self.calibration_type == 'flow':
            # แสดงข้อมูล Flow Rate (Display flow rate info)
            self.display.draw_text(20, 70, f"Run: {step}/{total_steps}", self.colors.WHITE)
            self.display.draw_text(20, 100, f"Volume: {voltage:.2f} mL", self.colors.YELLOW)

        # แสดง Progress Bar (Display progress bar)
        progress = step / total_steps if total_steps > 0 else 0
        self.display.draw_progress_bar(20, 170, 280, 20, progress)

        # แสดงสถานะ (Display status)
        self.display.draw_status_bar(status)

    def update_voltage(self, voltage):
        """
        อัปเดตค่าแรงดันไฟฟ้า (Update voltage display)

        Args:
            voltage (float): ค่าแรงดันใหม่ mV (New voltage value)
        """
        # ล้างพื้นที่แรงดัน (Clear voltage area)
        self.display.fill_rect(120, 100, 150, 24, self.colors.BLACK)
        self.display.draw_text(120, 100, f"{voltage:.1f} mV", self.colors.YELLOW)

    def update_status(self, status, color=None):
        """
        อัปเดตสถานะ (Update status)

        Args:
            status (str): ข้อความสถานะ (Status message)
            color (int): สีข้อความ (Text color)
        """
        if color is None:
            color = self.colors.TEXT_INFO
        self.display.draw_status_bar(status, color)


# ==============================================================================
# คลาส TitrationScreen - หน้าแสดงการไทเทรต
# TitrationScreen Class - Titration display screen
# ==============================================================================
class TitrationScreen(BaseScreen):
    """
    หน้าแสดงผลการไทเทรต (Titration display screen)

    แสดงข้อมูลแบบ real-time ระหว่างการไทเทรตอัตโนมัติ
    Displays real-time data during automatic titration

    Attributes:
        phase (str): เฟสปัจจุบัน 'dosing', 'stabilizing', 'reading', 'endpoint'
    """

    def __init__(self, display, colors):
        """
        สร้างหน้าไทเทรต (Create titration screen)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
        """
        super().__init__(display, colors)
        self.phase = 'ready'
        self._last_ph = -1
        self._last_volume = -1

    def render(self, ph=7.0, volume=0.0, temperature=25.0, phase='ready',
               target_ph=7.0, elapsed_time=0):
        """
        วาดหน้าไทเทรต (Draw titration screen)

        Args:
            ph (float): ค่า pH ปัจจุบัน (Current pH)
            volume (float): ปริมาตรที่จ่าย mL (Dispensed volume)
            temperature (float): อุณหภูมิ (Temperature)
            phase (str): เฟสการไทเทรต (Titration phase)
            target_ph (float): ค่า pH เป้าหมาย (Target pH)
            elapsed_time (int): เวลาที่ผ่านไป วินาที (Elapsed time)
        """
        self.display.clear()

        # วาดส่วนหัว (Draw header)
        header_color = self._get_phase_color(phase)
        self.display.draw_header("Auto Titration", bg_color=header_color)

        # แสดงเฟส (Display phase)
        phase_text = self._get_phase_text(phase)
        self.display.draw_text(20, 40, f"Phase: {phase_text}", self._get_phase_color(phase))

        # แสดงค่า pH ขนาดใหญ่ (Display large pH value)
        self.display.draw_text(20, 70, f"pH: {ph:.2f}", self.colors.GREEN)

        # แสดงค่า pH เป้าหมาย (Display target pH)
        self.display.draw_text(180, 70, f"Target: {target_ph:.1f}", self.colors.TEXT_WARNING)

        # แสดงปริมาตร (Display volume)
        self.display.draw_text(20, 100, f"Volume: {volume:.2f} mL", self.colors.CYAN)

        # แสดงอุณหภูมิ (Display temperature)
        self.display.draw_text(20, 130, f"Temp: {temperature:.1f} C", self.colors.WHITE)

        # แสดงเวลา (Display time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        self.display.draw_text(180, 130, f"Time: {minutes:02d}:{seconds:02d}", self.colors.WHITE)

        # แสดง Progress Bar สำหรับ pH (Display pH progress bar)
        # สมมติว่าเริ่มที่ pH 2 และจบที่ pH 12
        ph_progress = (ph - 2) / 10  # Normalize to 0-1
        self.display.draw_text(20, 165, "pH Scale:", self.colors.WHITE)
        self.display.draw_progress_bar(100, 165, 200, 15, ph_progress,
                                       fg_color=self.colors.GREEN)

        # แสดงสถานะ (Display status)
        self._draw_phase_status(phase)

        self.phase = phase
        self._last_ph = ph
        self._last_volume = volume

    def _get_phase_color(self, phase):
        """
        รับสีตามเฟส (Get color based on phase)

        Args:
            phase (str): เฟสการไทเทรต (Titration phase)

        Returns:
            int: สี RGB565 (RGB565 color)
        """
        phase_colors = {
            'ready': self.colors.HEADER_BG,
            'dosing': self.colors.ORANGE,
            'stabilizing': self.colors.YELLOW,
            'reading': self.colors.CYAN,
            'endpoint': self.colors.GREEN,
            'complete': self.colors.GREEN,
            'error': self.colors.RED
        }
        return phase_colors.get(phase, self.colors.WHITE)

    def _get_phase_text(self, phase):
        """
        รับข้อความตามเฟส (Get text based on phase)

        Args:
            phase (str): เฟสการไทเทรต (Titration phase)

        Returns:
            str: ข้อความเฟส (Phase text)
        """
        phase_texts = {
            'ready': 'Ready',
            'dosing': 'Dosing (0.2 mL)',
            'stabilizing': 'Stabilizing...',
            'reading': 'Reading pH',
            'endpoint': 'Endpoint Reached',
            'complete': 'Complete!',
            'error': 'Error!'
        }
        return phase_texts.get(phase, phase)

    def _draw_phase_status(self, phase):
        """
        วาดสถานะตามเฟส (Draw status based on phase)

        Args:
            phase (str): เฟสการไทเทรต (Titration phase)
        """
        status_messages = {
            'ready': 'Press SELECT to start',
            'dosing': 'Pumping 0.2 mL...',
            'stabilizing': 'Waiting for pH...',
            'reading': 'Reading sensors...',
            'endpoint': 'Endpoint detected!',
            'complete': 'Titration complete!',
            'error': 'Error occurred!'
        }
        status = status_messages.get(phase, '')
        color = self._get_phase_color(phase)
        self.display.draw_status_bar(status, color)

    def update_values(self, ph=None, volume=None, phase=None):
        """
        อัปเดตค่าที่เปลี่ยนแปลง (Update changed values)

        Args:
            ph (float): ค่า pH ใหม่ (New pH)
            volume (float): ปริมาตรใหม่ (New volume)
            phase (str): เฟสใหม่ (New phase)
        """
        if ph is not None and abs(ph - self._last_ph) > 0.01:
            self.display.fill_rect(60, 70, 100, 24, self.colors.BLACK)
            self.display.draw_text(60, 70, f"{ph:.2f}", self.colors.GREEN)
            self._last_ph = ph

        if volume is not None and abs(volume - self._last_volume) > 0.01:
            self.display.fill_rect(100, 100, 100, 24, self.colors.BLACK)
            self.display.draw_text(100, 100, f"{volume:.2f} mL", self.colors.CYAN)
            self._last_volume = volume

        if phase is not None and phase != self.phase:
            self._draw_phase_status(phase)
            self.phase = phase


# ==============================================================================
# คลาส ResultScreen - หน้าแสดงผลลัพธ์
# ResultScreen Class - Results display screen
# ==============================================================================
class ResultScreen(BaseScreen):
    """
    หน้าแสดงผลลัพธ์ (Results display screen)

    แสดงผลลัพธ์หลังจากการสอบเทียบหรือไทเทรตเสร็จสิ้น
    Displays results after calibration or titration is complete

    Attributes:
        result_type (str): ประเภทผลลัพธ์ 'calibration', 'titration'
    """

    def __init__(self, display, colors, result_type='calibration'):
        """
        สร้างหน้าผลลัพธ์ (Create results screen)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            result_type (str): 'calibration' หรือ 'titration'
        """
        super().__init__(display, colors)
        self.result_type = result_type

    def render(self, **results):
        """
        วาดหน้าผลลัพธ์ (Draw results screen)

        Args:
            **results: ผลลัพธ์ที่จะแสดง (Results to display)
                สำหรับ calibration:
                    slope_m (float): ค่า slope (pH/mV)
                    intercept_b (float): ค่า intercept (pH)
                    r_squared (float): ค่า R^2
                    points (list): จุดสอบเทียบ [(ph, voltage), ...]

                สำหรับ titration:
                    endpoint_ph (float): ค่า pH ที่จุดสมมูล
                    volume_used (float): ปริมาตรที่ใช้
                    duration (int): เวลาที่ใช้
                    saved_file (str): ชื่อไฟล์ที่บันทึก
        """
        self.display.clear()

        if self.result_type == 'calibration':
            self._render_calibration_results(**results)
        elif self.result_type == 'titration':
            self._render_titration_results(**results)
        else:
            self._render_generic_results(**results)

    def _render_calibration_results(self, slope=0, intercept=0, r_squared=0,
                                     points=None, calibration_type='ph', **kwargs):
        """
        วาดผลลัพธ์การสอบเทียบ (Draw calibration results)
        """
        title = "pH Calibration Results" if calibration_type == 'ph' else "Flow Calibration Results"
        self.display.draw_header(title)

        y = 40

        if calibration_type == 'ph':
            # แสดงสมการเส้นตรง (Display linear equation)
            self.display.draw_text(20, y, "Linear Equation:", self.colors.WHITE)
            y += 25
            self.display.draw_text(20, y, f"pH = {slope:.4f}*V + {intercept:.4f}", self.colors.YELLOW)
            y += 30

            # แสดงค่า R^2 (Display R^2)
            r2_color = self.colors.GREEN if r_squared >= 0.98 else self.colors.RED
            self.display.draw_text(20, y, f"R-squared: {r_squared:.4f}", r2_color)
            y += 30

            # แสดงจุดสอบเทียบ (Display calibration points)
            if points:
                self.display.draw_text(20, y, "Calibration Points:", self.colors.WHITE)
                y += 25
                for ph, voltage in points:
                    self.display.draw_text(30, y, f"pH {ph:.1f}: {voltage:.1f} mV", self.colors.CYAN)
                    y += 22

        elif calibration_type == 'flow':
            # แสดง Flow Rate (Display flow rate)
            flow_rate = kwargs.get('flow_rate', 0)
            self.display.draw_text(20, y, f"Flow Rate: {flow_rate:.4f} mL/s", self.colors.YELLOW)
            y += 30

            # แสดงค่าเฉลี่ย (Display average)
            if points:
                self.display.draw_text(20, y, "Individual Runs:", self.colors.WHITE)
                y += 25
                for i, (time_sec, volume) in enumerate(points):
                    rate = volume / time_sec if time_sec > 0 else 0
                    self.display.draw_text(30, y, f"Run {i+1}: {rate:.4f} mL/s", self.colors.CYAN)
                    y += 22

        # แสดงสถานะการบันทึก (Display save status)
        valid = r_squared >= 0.98 if calibration_type == 'ph' else True
        status = "Data saved successfully" if valid else "Warning: R^2 < 0.98"
        status_color = self.colors.GREEN if valid else self.colors.RED
        self.display.draw_status_bar(status, status_color)

    def _render_titration_results(self, endpoint_ph=7.0, volume_used=0.0,
                                   duration=0, saved_file="", **kwargs):
        """
        วาดผลลัพธ์การไทเทรต (Draw titration results)
        """
        self.display.draw_header("Titration Results")

        y = 45

        # แสดงค่า pH ที่จุดสมมูล (Display endpoint pH)
        self.display.draw_text(20, y, "Endpoint pH:", self.colors.WHITE)
        self.display.draw_text(180, y, f"{endpoint_ph:.2f}", self.colors.GREEN)
        y += 30

        # แสดงปริมาตรที่ใช้ (Display volume used)
        self.display.draw_text(20, y, "Volume Used:", self.colors.WHITE)
        self.display.draw_text(180, y, f"{volume_used:.2f} mL", self.colors.YELLOW)
        y += 30

        # แสดงเวลาที่ใช้ (Display duration)
        minutes = duration // 60
        seconds = duration % 60
        self.display.draw_text(20, y, "Duration:", self.colors.WHITE)
        self.display.draw_text(180, y, f"{minutes:02d}:{seconds:02d}", self.colors.CYAN)
        y += 30

        # แสดงไฟล์ที่บันทึก (Display saved file)
        if saved_file:
            self.display.draw_text(20, y, "Saved to:", self.colors.WHITE)
            y += 25
            # ตัดชื่อไฟล์ถ้ายาวเกินไป (Truncate filename if too long)
            display_name = saved_file if len(saved_file) <= 25 else "..." + saved_file[-22:]
            self.display.draw_text(30, y, display_name, self.colors.TEXT_INFO)

        # แสดงสถานะ (Display status)
        self.display.draw_status_bar("Press SELECT to continue", self.colors.TEXT_INFO)

    def _render_generic_results(self, title="Results", message="Complete", **kwargs):
        """
        วาดผลลัพธ์ทั่วไป (Draw generic results)
        """
        self.display.draw_header(title)
        self.display.draw_text_centered(100, message, self.colors.GREEN)
        self.display.draw_status_bar("Press SELECT to continue")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    # ตัวอย่างนี้ต้องใช้กับฮาร์ดแวร์จริง
    # This example requires actual hardware
    print("Screen classes loaded successfully")
    print("Available screens: MainMenuScreen, CalibrationScreen, TitrationScreen, ResultScreen")

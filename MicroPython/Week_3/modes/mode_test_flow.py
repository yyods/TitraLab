# ==============================================================================
# mode_test_flow.py - โหมดทดสอบอัตราการไหล (Flow Rate Test Mode)
# ==============================================================================
# โหมดนี้จ่ายสารละลายตามปริมาตรที่กำหนดเพื่อตรวจสอบความแม่นยำ
# This mode dispenses a set volume to verify flow rate accuracy
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การควบคุมปริมาตรด้วยเวลา (Volume control by time)
# 2. เข้าใจความสัมพันธ์ Volume = Flow Rate * Time
# 3. ฝึกการตรวจสอบความถูกต้องของการสอบเทียบ (Calibration verification)
#
# การทำงาน (Operation):
# - ผู้ใช้กำหนดปริมาตรที่ต้องการ (1-10 mL)
# - ระบบคำนวณเวลาจ่ายจากอัตราการไหลที่สอบเทียบ
# - จ่ายสารละลายและหยุดอัตโนมัติ
# - ผู้ใช้ตรวจสอบปริมาตรจริงกับที่ตั้งไว้
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff, ticks_us


class TestFlowMode(BaseMode):
    """
    โหมดทดสอบอัตราการไหล (Flow Rate Test Mode)

    จ่ายสารละลายตามปริมาตรที่กำหนดเพื่อตรวจสอบความแม่นยำ
    Dispenses set volume to verify accuracy

    Attributes:
        pump: ออบเจ็กต์ปั๊ม (Pump object)
        target_volume (float): ปริมาตรเป้าหมาย mL (Target volume)
        flow_rate (float): อัตราการไหล mL/s (Flow rate)
    """

    # ค่าเริ่มต้น (Default values)
    DEFAULT_VOLUME = 5.0     # ปริมาตรเริ่มต้น 5 mL
    MIN_VOLUME = 0.5         # ปริมาตรต่ำสุด 0.5 mL
    MAX_VOLUME = 20.0        # ปริมาตรสูงสุด 20 mL
    VOLUME_STEP = 0.5        # ขั้นการปรับ 0.5 mL

    def __init__(self, display, colors, pump, buzzer=None):
        """
        สร้างโหมดทดสอบอัตราการไหล (Create flow rate test mode)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            pump: ออบเจ็กต์ปั๊ม (Pump object)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object)
        """
        super().__init__(display, colors, "Flow Rate Test")

        self.pump = pump
        self.buzzer = buzzer

        # การตั้งค่า (Settings)
        self.target_volume = self.DEFAULT_VOLUME
        self.flow_rate = 0.0  # จะโหลดจากไฟล์ (Will load from file)

        # สถานะ (State)
        self.state = 'setup'  # 'setup', 'ready', 'dispensing', 'done'

        # ตัวแปรสำหรับการจ่าย (Dispensing variables)
        self._dispense_start_time = 0
        self._dispense_duration = 0  # ระยะเวลาที่ต้องจ่าย (Required dispense time)
        self._is_dispensing = False

    def on_enter(self):
        """
        เริ่มต้นโหมดทดสอบ (Start test mode)
        """
        super().on_enter()

        # โหลดอัตราการไหลจากไฟล์ (Load flow rate from file)
        self._load_flow_rate()

        # รีเซ็ตสถานะ (Reset state)
        self.state = 'setup'
        self._is_dispensing = False
        self.target_volume = self.DEFAULT_VOLUME

        # แสดงหน้าจอตั้งค่า (Display setup screen)
        self._show_setup_screen()

    def update(self):
        """
        อัปเดตสถานะ (Update state)
        """
        if self.state == 'setup':
            self._handle_setup_state()
        elif self.state == 'ready':
            self._handle_ready_state()
        elif self.state == 'dispensing':
            self._handle_dispensing_state()
        elif self.state == 'done':
            self._handle_done_state()

    def on_exit(self):
        """
        ออกจากโหมด (Exit mode)
        """
        # หยุดปั๊ม (Stop pump)
        if self._is_dispensing:
            self._stop_dispense()

        super().on_exit()

    # ==========================================================================
    # State Handlers
    # ==========================================================================

    def _handle_setup_state(self):
        """
        จัดการสถานะตั้งค่า (Handle setup state)
        """
        # ปุ่ม UP - เพิ่มปริมาตร (UP - increase volume)
        if self.check_button('up'):
            self._beep()
            self._adjust_volume(self.VOLUME_STEP)

        # ปุ่ม DOWN - ลดปริมาตร (DOWN - decrease volume)
        elif self.check_button('down'):
            self._beep()
            self._adjust_volume(-self.VOLUME_STEP)

        # ปุ่ม SELECT - ยืนยัน (SELECT - confirm)
        elif self.check_button('select'):
            self._beep()
            self._calculate_dispense_time()
            self._show_ready_screen()
            self.state = 'ready'

    def _handle_ready_state(self):
        """
        จัดการสถานะพร้อม (Handle ready state)
        """
        # ปุ่ม SELECT - เริ่มจ่าย (SELECT - start dispensing)
        if self.check_button('select'):
            self._beep()
            self._start_dispense()

        # ปุ่ม DOWN - กลับไปตั้งค่า (DOWN - back to setup)
        elif self.check_button('down'):
            self._beep()
            self.state = 'setup'
            self._show_setup_screen()

    def _handle_dispensing_state(self):
        """
        จัดการสถานะกำลังจ่าย (Handle dispensing state)
        """
        elapsed = self._get_dispense_elapsed_time()

        # อัปเดตหน้าจอ (Update display)
        self._update_dispense_display(elapsed)

        # ตรวจสอบว่าจ่ายครบหรือยัง (Check if dispensing complete)
        if elapsed >= self._dispense_duration:
            self._stop_dispense()
            self._show_done_screen()
            self.state = 'done'

        # ปุ่ม SELECT - หยุดก่อนกำหนด (SELECT - stop early)
        if self.check_button('select'):
            self._beep()
            self._stop_dispense()
            self._show_done_screen()
            self.state = 'done'

    def _handle_done_state(self):
        """
        จัดการสถานะเสร็จสิ้น (Handle done state)
        """
        # ปุ่ม SELECT - ทดสอบอีกครั้ง (SELECT - test again)
        if self.check_button('select'):
            self._beep()
            self.state = 'setup'
            self._show_setup_screen()

        # ปุ่ม DOWN - ออก (DOWN - exit)
        elif self.check_button('down'):
            self._beep()
            self.set_complete()

    # ==========================================================================
    # Display Methods
    # ==========================================================================

    def _show_setup_screen(self):
        """
        แสดงหน้าจอตั้งค่า (Display setup screen)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        y = 45
        self.display.draw_text(20, y, "Set Target Volume:", self.colors.WHITE)
        y += 35

        # แสดงปริมาตรขนาดใหญ่ (Display large volume)
        self._update_volume_display()

        y = 130
        self.display.draw_text(20, y, f"Flow Rate: {self.flow_rate:.4f} mL/s", self.colors.CYAN)
        y += 30

        if self.flow_rate <= 0:
            self.display.draw_text(20, y, "WARNING: Not calibrated!", self.colors.RED)
        else:
            calc_time = self.target_volume / self.flow_rate
            self.display.draw_text(20, y, f"Est. Time: {calc_time:.2f} s", self.colors.TEXT_INFO)

        self.display.draw_status_bar("UP/DOWN: Adjust  SELECT: Start", self.colors.TEXT_INFO)

    def _update_volume_display(self):
        """
        อัปเดตการแสดงผลปริมาตร (Update volume display)
        """
        self.display.fill_rect(80, 80, 180, 40, self.colors.BLACK)
        vol_text = f"{self.target_volume:.1f} mL"
        self.display.draw_text(100, 85, vol_text, self.colors.GREEN)

        # อัปเดตเวลาโดยประมาณ (Update estimated time)
        if self.flow_rate > 0:
            calc_time = self.target_volume / self.flow_rate
            self.display.fill_rect(130, 160, 120, 24, self.colors.BLACK)
            self.display.draw_text(130, 160, f"{calc_time:.2f} s", self.colors.TEXT_INFO)

    def _show_ready_screen(self):
        """
        แสดงหน้าจอพร้อมจ่าย (Display ready screen)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        y = 50
        self.display.draw_text(20, y, "Ready to Dispense", self.colors.WHITE)
        y += 35

        self.display.draw_text(20, y, f"Volume: {self.target_volume:.1f} mL", self.colors.GREEN)
        y += 30

        self.display.draw_text(20, y, f"Duration: {self._dispense_duration:.2f} s", self.colors.CYAN)
        y += 40

        self.display.draw_text(20, y, "Place tube in container", self.colors.YELLOW)

        self.display.draw_status_bar("SELECT: Start  DOWN: Back", self.colors.TEXT_INFO)

    def _update_dispense_display(self, elapsed):
        """
        อัปเดตหน้าจอขณะจ่าย (Update dispensing display)

        Args:
            elapsed (float): เวลาที่ผ่านไป (Elapsed time)
        """
        # คำนวณปริมาตรที่จ่ายไปแล้ว (Calculate dispensed volume)
        dispensed = elapsed * self.flow_rate

        # อัปเดตเวลา (Update time)
        self.display.fill_rect(150, 85, 150, 24, self.colors.BLACK)
        self.display.draw_text(150, 85, f"{elapsed:.2f} s", self.colors.YELLOW)

        # อัปเดตปริมาตร (Update volume)
        self.display.fill_rect(150, 115, 150, 24, self.colors.BLACK)
        self.display.draw_text(150, 115, f"{dispensed:.2f} mL", self.colors.GREEN)

        # อัปเดต Progress Bar
        progress = elapsed / self._dispense_duration if self._dispense_duration > 0 else 0
        self.display.draw_progress_bar(20, 160, 280, 20, progress, fg_color=self.colors.GREEN)

    def _show_done_screen(self):
        """
        แสดงหน้าจอเสร็จสิ้น (Display done screen)

        หมายเหตุ: ความคลาดเคลื่อนที่แสดงเป็นความแม่นยำของเวลา ไม่ใช่ปริมาตรจริง
        Note: Error shown is timing accuracy, not actual volume accuracy
        ผู้ใช้ควรวัดปริมาตรจริงด้วยกระบอกตวงเพื่อตรวจสอบการสอบเทียบ
        User should measure actual volume with graduated cylinder to verify calibration
        """
        self.display.clear()
        self.display.draw_header("Dispense Complete")

        # เวลาที่จ่ายจริง (Actual elapsed time)
        actual_time = self._get_dispense_elapsed_time()
        # เวลาที่คาดหวัง (Expected time based on calculation)
        expected_time = self._dispense_duration
        # ปริมาตรที่คำนวณจากเวลาจริง (Calculated volume from actual time)
        calculated_volume = actual_time * self.flow_rate

        y = 45
        self.display.draw_text(20, y, "Results:", self.colors.WHITE)
        y += 28

        # แสดงปริมาตรเป้าหมาย (Show target volume)
        self.display.draw_text(20, y, f"Target Vol: {self.target_volume:.2f} mL", self.colors.CYAN)
        y += 23

        # แสดงปริมาตรที่คำนวณได้ (Show calculated volume from actual time)
        self.display.draw_text(20, y, f"Calc Vol:   {calculated_volume:.2f} mL", self.colors.GREEN)
        y += 28

        # แสดงเวลาที่คาดหวังและเวลาจริง (Show expected vs actual time)
        self.display.draw_text(20, y, f"Expected Time: {expected_time:.3f} s", self.colors.TEXT_INFO)
        y += 23
        self.display.draw_text(20, y, f"Actual Time:   {actual_time:.3f} s", self.colors.YELLOW)
        y += 28

        # คำนวณความคลาดเคลื่อนของเวลา (Calculate timing error)
        # เปรียบเทียบเวลาจริง vs เวลาที่คาดหวัง (Compare actual vs expected time)
        timing_error = ((actual_time - expected_time) / expected_time) * 100 if expected_time > 0 else 0
        error_color = self.colors.GREEN if abs(timing_error) < 1 else self.colors.YELLOW if abs(timing_error) < 5 else self.colors.RED
        self.display.draw_text(20, y, f"Timing Error: {timing_error:+.2f}%", error_color)

        self.display.draw_status_bar("SELECT: Again  DOWN: Exit", self.colors.TEXT_INFO)

    # ==========================================================================
    # Control Methods
    # ==========================================================================

    def _load_flow_rate(self):
        """
        โหลดอัตราการไหลจากไฟล์ (Load flow rate from file)
        """
        try:
            with open('data_flowrate.txt', 'r') as f:
                self.flow_rate = float(f.readline().strip())
            print(f"โหลดอัตราการไหล: {self.flow_rate:.4f} mL/s (Flow rate loaded)")
        except:
            # ถ้าไม่มีไฟล์หรือ error ให้ใช้ค่าจากปั๊ม (If no file, use pump value)
            if self.pump:
                self.flow_rate = getattr(self.pump, 'flow_rate', 0.1)
            else:
                self.flow_rate = 0.1  # ค่าเริ่มต้น (Default value)
            print(f"ใช้ค่าเริ่มต้น: {self.flow_rate:.4f} mL/s (Using default)")

    def _adjust_volume(self, delta):
        """
        ปรับปริมาตรเป้าหมาย (Adjust target volume)

        Args:
            delta (float): ค่าที่ปรับ (Adjustment value)
        """
        new_volume = self.target_volume + delta
        self.target_volume = max(self.MIN_VOLUME, min(new_volume, self.MAX_VOLUME))
        self._update_volume_display()

    def _calculate_dispense_time(self):
        """
        คำนวณเวลาที่ต้องจ่าย (Calculate dispense duration)
        """
        if self.flow_rate > 0:
            self._dispense_duration = self.target_volume / self.flow_rate
        else:
            self._dispense_duration = 0
            print("Warning: Flow rate is 0, cannot calculate time")

    def _start_dispense(self):
        """
        เริ่มจ่ายสารละลาย (Start dispensing)
        """
        self._dispense_start_time = ticks_us()
        self._is_dispensing = True
        self.state = 'dispensing'

        # เริ่มปั๊ม (Start pump)
        if self.pump:
            self.pump.set_duty(100)

        # แสดงหน้าจอขณะจ่าย (Display dispensing screen)
        self.display.clear()
        self.display.draw_header("Dispensing...")

        self.display.draw_text(20, 55, "PUMP RUNNING", self.colors.GREEN)
        self.display.draw_text(20, 85, "Elapsed:", self.colors.WHITE)
        self.display.draw_text(20, 115, "Volume:", self.colors.WHITE)

        self.display.draw_status_bar("Press SELECT to stop", self.colors.TEXT_WARNING)

    def _stop_dispense(self):
        """
        หยุดจ่ายสารละลาย (Stop dispensing)
        """
        self._is_dispensing = False

        # หยุดปั๊ม (Stop pump)
        if self.pump:
            self.pump.stop()

    def _get_dispense_elapsed_time(self):
        """
        รับเวลาที่ผ่านไปตั้งแต่เริ่มจ่าย (Get elapsed dispense time)

        Returns:
            float: เวลาในวินาที (Time in seconds)
        """
        if self._dispense_start_time > 0:
            elapsed_us = ticks_diff(ticks_us(), self._dispense_start_time)
            return elapsed_us / 1_000_000
        return 0.0

    def _beep(self):
        """
        เล่นเสียงบี๊ป (Play beep sound)
        """
        if self.buzzer:
            try:
                self.buzzer.beep()
            except:
                pass


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("TestFlowMode Module")
    print("===================")
    print("This mode tests flow rate accuracy by dispensing set volumes.")
    print("")
    print("Process:")
    print("1. Use UP/DOWN to set target volume")
    print("2. Press SELECT to start dispensing")
    print("3. System stops automatically when target reached")
    print("4. Compare actual volume with target")

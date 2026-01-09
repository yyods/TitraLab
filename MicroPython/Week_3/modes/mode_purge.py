# ==============================================================================
# mode_purge.py - โหมดล้างท่อ (Purge/Clean Tubing Mode)
# ==============================================================================
# โหมดนี้ใช้สำหรับล้างท่อและระบบจ่ายสารละลายด้วยการเปิดปั๊มต่อเนื่อง
# This mode is used to clean tubing and dispensing system with continuous pump
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้ความสำคัญของการล้างระบบก่อนใช้งาน (System flushing importance)
# 2. เข้าใจการควบคุมปั๊มแบบ manual (Manual pump control)
# 3. ฝึกการออกแบบ UI สำหรับการควบคุมอุปกรณ์ (Device control UI design)
#
# การใช้งาน (Usage):
# - ก่อนไทเทรต: ล้างฟองอากาศและสารตกค้างในท่อ (Flush air bubbles and residue)
# - หลังไทเทรต: ล้างสารไทแทรนต์ออกจากท่อ (Clean titrant from tubing)
# - เปลี่ยนสาร: เมื่อเปลี่ยนชนิดสารไทแทรนต์ (When changing titrant)
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff


class PurgeMode(BaseMode):
    """
    โหมดล้างท่อ (Purge/Clean Tubing Mode)

    เปิดปั๊มต่อเนื่องเพื่อล้างท่อ สามารถปรับความเร็วได้
    Runs pump continuously to clean tubing, speed adjustable

    Attributes:
        pump: ออบเจ็กต์ปั๊ม (Pump object)
        duty_cycle (int): Duty cycle 0-100% (PWM duty cycle)
    """

    # ค่าเริ่มต้น (Default values)
    DEFAULT_DUTY = 100       # Duty cycle เริ่มต้น 100%
    MIN_DUTY = 20            # Duty cycle ต่ำสุด 20%
    MAX_DUTY = 100           # Duty cycle สูงสุด 100%
    DUTY_STEP = 10           # ขั้นการปรับ 10%

    def __init__(self, display, colors, pump, buzzer=None):
        """
        สร้างโหมดล้างท่อ (Create purge mode)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            pump: ออบเจ็กต์ปั๊ม (Pump object)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object)
        """
        super().__init__(display, colors, "Purge")

        self.pump = pump
        self.buzzer = buzzer

        # การตั้งค่า (Settings)
        self.duty_cycle = self.DEFAULT_DUTY

        # สถานะ (State)
        self.is_pumping = False
        self._pump_start_time = 0
        self._total_pump_time = 0

    def on_enter(self):
        """
        เริ่มต้นโหมดล้างท่อ (Start purge mode)
        """
        super().on_enter()

        # รีเซ็ตสถานะ (Reset state)
        self.is_pumping = False
        self.duty_cycle = self.DEFAULT_DUTY
        self._total_pump_time = 0

        # แสดงหน้าจอ (Display screen)
        self._render_screen()

    def update(self):
        """
        อัปเดตสถานะ (Update state)
        """
        # อัปเดตเวลาถ้าปั๊มกำลังทำงาน (Update time if pump running)
        if self.is_pumping:
            self._update_time_display()

        # จัดการปุ่ม (Handle buttons)
        self._handle_buttons()

    def on_exit(self):
        """
        ออกจากโหมด (Exit mode)
        """
        # หยุดปั๊มถ้ายังทำงานอยู่ (Stop pump if running)
        if self.is_pumping:
            self._stop_pump()

        super().on_exit()

    # ==========================================================================
    # Button Handling
    # ==========================================================================

    def _handle_buttons(self):
        """
        จัดการการกดปุ่ม (Handle button presses)
        """
        # ปุ่ม SELECT - เริ่ม/หยุดปั๊ม (SELECT - start/stop pump)
        if self.check_button('select'):
            self._beep()
            if self.is_pumping:
                self._stop_pump()
            else:
                self._start_pump()

        # ปุ่ม UP - เพิ่ม duty cycle (UP - increase duty cycle)
        elif self.check_button('up'):
            self._beep()
            self._adjust_duty(self.DUTY_STEP)

        # ปุ่ม DOWN ค้าง 3 วินาที - ออก (DOWN long press - exit)
        # ตรวจสอบใน MenuSystem, ที่นี่แค่ตรวจสอบกดสั้น
        # ปุ่ม DOWN - ลด duty cycle (DOWN - decrease duty cycle)
        elif self.check_button('down'):
            self._beep()
            self._adjust_duty(-self.DUTY_STEP)

    # ==========================================================================
    # Display Methods
    # ==========================================================================

    def _render_screen(self):
        """
        วาดหน้าจอทั้งหมด (Render complete screen)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        y = 45
        self.display.draw_text(20, y, "Purge / Clean Tubing", self.colors.WHITE)
        y += 35

        # แสดงสถานะปั๊ม (Display pump status)
        self.display.draw_text(20, y, "Pump Status:", self.colors.WHITE)
        self._update_pump_status_display()
        y += 30

        # แสดง Duty Cycle (Display duty cycle)
        self.display.draw_text(20, y, "Speed:", self.colors.WHITE)
        self._update_duty_display()
        y += 30

        # แสดงเวลาทำงาน (Display run time)
        self.display.draw_text(20, y, "Run Time:", self.colors.WHITE)
        self.display.draw_text(150, y, "0.0 s", self.colors.CYAN)
        y += 40

        # วาด Progress Bar สำหรับ Duty Cycle (Draw duty cycle progress bar)
        self.display.draw_text(20, y, "Duty Cycle:", self.colors.WHITE)
        y += 25
        self._draw_duty_bar()

        # แสดงคำแนะนำ (Display instructions)
        self.display.draw_status_bar("SELECT:Start/Stop UP/DOWN:Speed", self.colors.TEXT_INFO)

    def _update_pump_status_display(self):
        """
        อัปเดตการแสดงผลสถานะปั๊ม (Update pump status display)
        """
        self.display.fill_rect(150, 80, 150, 24, self.colors.BLACK)

        if self.is_pumping:
            self.display.draw_text(150, 80, "RUNNING", self.colors.GREEN)
        else:
            self.display.draw_text(150, 80, "STOPPED", self.colors.RED)

    def _update_duty_display(self):
        """
        อัปเดตการแสดงผล Duty Cycle (Update duty cycle display)
        """
        self.display.fill_rect(150, 110, 100, 24, self.colors.BLACK)
        self.display.draw_text(150, 110, f"{self.duty_cycle}%", self.colors.YELLOW)

    def _update_time_display(self):
        """
        อัปเดตการแสดงผลเวลา (Update time display)
        """
        elapsed = self._get_elapsed_time()
        self.display.fill_rect(150, 140, 100, 24, self.colors.BLACK)
        self.display.draw_text(150, 140, f"{elapsed:.1f} s", self.colors.CYAN)

    def _draw_duty_bar(self):
        """
        วาดแถบ Duty Cycle (Draw duty cycle bar)
        """
        progress = self.duty_cycle / 100.0
        y = 205

        # เลือกสีตาม duty cycle (Choose color based on duty cycle)
        if self.duty_cycle >= 80:
            bar_color = self.colors.GREEN
        elif self.duty_cycle >= 50:
            bar_color = self.colors.YELLOW
        else:
            bar_color = self.colors.ORANGE

        self.display.draw_progress_bar(20, y, 280, 15, progress, fg_color=bar_color)

    # ==========================================================================
    # Pump Control Methods
    # ==========================================================================

    def _start_pump(self):
        """
        เริ่มปั๊ม (Start pump)
        """
        self.is_pumping = True
        self._pump_start_time = ticks_ms()

        # เริ่มปั๊มด้วย duty cycle ที่กำหนด (Start pump with set duty cycle)
        if self.pump:
            self.pump.set_duty(self.duty_cycle)
        else:
            print("Warning: No pump connected")

        # อัปเดตหน้าจอ (Update display)
        self._update_pump_status_display()

        print(f"ปั๊มเริ่มทำงาน @ {self.duty_cycle}% (Pump started)")

    def _stop_pump(self):
        """
        หยุดปั๊ม (Stop pump)
        """
        # บันทึกเวลาทำงาน (Record run time)
        if self.is_pumping:
            self._total_pump_time += self._get_elapsed_time()

        self.is_pumping = False

        # หยุดปั๊ม (Stop pump)
        if self.pump:
            self.pump.stop()

        # อัปเดตหน้าจอ (Update display)
        self._update_pump_status_display()

        print(f"ปั๊มหยุดทำงาน - รวม {self._total_pump_time:.1f} s (Pump stopped)")

    def _adjust_duty(self, delta):
        """
        ปรับ Duty Cycle (Adjust duty cycle)

        Args:
            delta (int): ค่าที่ปรับ (Adjustment value)
        """
        new_duty = self.duty_cycle + delta
        self.duty_cycle = max(self.MIN_DUTY, min(new_duty, self.MAX_DUTY))

        # ถ้าปั๊มกำลังทำงาน อัปเดต duty cycle (If pump running, update duty cycle)
        if self.is_pumping and self.pump:
            self.pump.set_duty(self.duty_cycle)

        # อัปเดตหน้าจอ (Update display)
        self._update_duty_display()
        self._draw_duty_bar()

        print(f"Duty Cycle: {self.duty_cycle}%")

    def _get_elapsed_time(self):
        """
        รับเวลาที่ปั๊มทำงานในรอบนี้ (Get current pump run time)

        Returns:
            float: เวลาในวินาที (Time in seconds)
        """
        if self.is_pumping and self._pump_start_time > 0:
            return ticks_diff(ticks_ms(), self._pump_start_time) / 1000.0
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
    print("PurgeMode Module")
    print("================")
    print("This mode runs the pump continuously to clean tubing.")
    print("")
    print("Controls:")
    print("- SELECT: Start/Stop pump")
    print("- UP: Increase speed (duty cycle)")
    print("- DOWN: Decrease speed (duty cycle)")
    print("- DOWN (hold 3s): Exit mode")
    print("")
    print("Usage scenarios:")
    print("- Before titration: Flush air bubbles")
    print("- After titration: Clean residue")
    print("- When changing titrant: Remove old solution")

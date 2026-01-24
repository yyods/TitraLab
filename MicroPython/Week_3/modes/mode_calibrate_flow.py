# ==============================================================================
# mode_calibrate_flow.py - โหมดสอบเทียบอัตราการไหล (Flow Rate Calibration Mode)
# ==============================================================================
# โหมดนี้ดำเนินการสอบเทียบอัตราการไหลของปั๊มด้วยการวัด 3 รอบ
# This mode performs pump flow rate calibration with 3 measurement runs
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การวัดอัตราการไหล (Flow rate measurement)
# 2. เข้าใจการคำนวณค่าเฉลี่ยและความคลาดเคลื่อน (Mean and deviation calculation)
# 3. ฝึกการควบคุม PWM สำหรับปั๊ม (PWM control for pump)
#
# ขั้นตอนการสอบเทียบ (Calibration Process):
# 1. เปิดปั๊มจนจ่ายสารละลาย 5 mL (หยุดด้วยมือ)
# 2. บันทึกเวลาที่ใช้
# 3. ทำซ้ำ 3 รอบ
# 4. คำนวณอัตราการไหลเฉลี่ย (mL/s)
#
# ความสำคัญในการไทเทรต (Importance in Titration):
# - ต้องรู้อัตราการไหลเพื่อคำนวณปริมาตรที่จ่าย: Volume = flow_rate * time
# - Flow Rate = Volume / Time (mL/s, ใช้ 4 ทศนิยมเพื่อลดความคลาดเคลื่อน)
# - ถ้าใช้ 3 ทศนิยม อาจเกิดความคลาดเคลื่อง ~1.2% ของปริมาตร
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff, ticks_us


class CalibrateFlowMode(BaseMode):
    """
    โหมดสอบเทียบอัตราการไหล (Flow Rate Calibration Mode)

    ดำเนินการสอบเทียบ 3 รอบด้วยปริมาตร 5 mL
    Performs 3-run calibration with 5 mL target volume

    Attributes:
        pump: ออบเจ็กต์ปั๊ม (Pump object)
        target_volume (float): ปริมาตรเป้าหมาย mL (Target volume)
        num_runs (int): จำนวนรอบทดสอบ (Number of test runs)
    """

    # ค่าคงที่ (Constants)
    TARGET_VOLUME_ML = 5.0  # ปริมาตรเป้าหมาย 5 mL
    NUM_RUNS = 3            # จำนวนรอบทดสอบ
    PUMP_DUTY_PERCENT = 100 # Duty cycle สำหรับการทดสอบ

    def __init__(self, display, colors, pump, buzzer=None):
        """
        สร้างโหมดสอบเทียบอัตราการไหล (Create flow rate calibration mode)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            pump: ออบเจ็กต์ปั๊ม (Pump object)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object)
        """
        super().__init__(display, colors, "Calibrate Flow Rate")

        self.pump = pump
        self.buzzer = buzzer

        # การตั้งค่า (Settings)
        self.target_volume = self.TARGET_VOLUME_ML
        self.num_runs = self.NUM_RUNS

        # ข้อมูลการวัด (Measurement data)
        self.run_times = []       # เวลาแต่ละรอบ (Time for each run)
        self.flow_rates = []      # อัตราการไหลแต่ละรอบ (Flow rate for each run)

        # สถานะ (State)
        self.current_run = 0
        self.state = 'ready'      # 'ready', 'running', 'waiting', 'done'

        # ตัวแปรสำหรับการวัดเวลา (Timing variables)
        self._pump_start_time = 0
        self._pump_is_running = False

    def on_enter(self):
        """
        เริ่มต้นการสอบเทียบ (Start calibration)
        """
        super().on_enter()

        # รีเซ็ตข้อมูล (Reset data)
        self.run_times = []
        self.flow_rates = []
        self.current_run = 0
        self.state = 'ready'
        self._pump_is_running = False

        # แสดงหน้าจอเริ่มต้น (Display initial screen)
        self._show_instruction_screen()

    def update(self):
        """
        อัปเดตสถานะ (Update state)
        """
        if self.state == 'ready':
            self._handle_ready_state()
        elif self.state == 'running':
            self._handle_running_state()
        elif self.state == 'waiting':
            self._handle_waiting_state()
        elif self.state == 'done':
            self._handle_done_state()

    def on_exit(self):
        """
        ออกจากโหมด (Exit mode)
        """
        # หยุดปั๊ม (Stop pump)
        if self._pump_is_running:
            self._stop_pump()

        super().on_exit()

    # ==========================================================================
    # State Handlers
    # ==========================================================================

    def _handle_ready_state(self):
        """
        จัดการสถานะพร้อม (Handle ready state)
        """
        # ตรวจสอบปุ่ม SELECT เพื่อเริ่ม (Check SELECT to start)
        if self.check_button('select'):
            self._beep()
            self._start_run()

    def _handle_running_state(self):
        """
        จัดการสถานะกำลังรัน (Handle running state)
        """
        # อัปเดตเวลาที่ผ่านไป (Update elapsed time)
        elapsed = self._get_pump_elapsed_time()
        self._update_time_display(elapsed)

        # ตรวจสอบปุ่ม SELECT เพื่อหยุด (Check SELECT to stop)
        if self.check_button('select'):
            self._beep()
            self._stop_run()

    def _handle_waiting_state(self):
        """
        จัดการสถานะรอ (Handle waiting state)
        """
        # ตรวจสอบปุ่ม SELECT เพื่อเริ่มรอบถัดไป (Check SELECT for next run)
        if self.check_button('select'):
            self._beep()
            if self.current_run < self.num_runs:
                self._start_run()
            else:
                self._calculate_results()
                self._show_results()
                self.state = 'done'

    def _handle_done_state(self):
        """
        จัดการสถานะเสร็จสิ้น (Handle done state)
        """
        # ตรวจสอบปุ่ม SELECT เพื่อบันทึก (Check SELECT to save)
        if self.check_button('select'):
            self._beep()
            self._save_calibration()
            self.set_complete()

    # ==========================================================================
    # Calibration Methods
    # ==========================================================================

    def _show_instruction_screen(self):
        """
        แสดงหน้าจอคำแนะนำ (Display instruction screen)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        y = 40
        self.display.draw_text(20, y, "Flow Rate Calibration", self.colors.WHITE)
        y += 30
        self.display.draw_text(20, y, f"Target: {self.target_volume:.1f} mL per run", self.colors.CYAN)
        y += 25
        self.display.draw_text(20, y, f"Total runs: {self.num_runs}", self.colors.CYAN)
        y += 35

        self.display.draw_text(20, y, "Instructions:", self.colors.YELLOW)
        y += 25
        self.display.draw_text(20, y, "1. Place tube in beaker", self.colors.WHITE)
        y += 22
        self.display.draw_text(20, y, "2. Press SELECT to start pump", self.colors.WHITE)
        y += 22
        self.display.draw_text(20, y, f"3. Stop when {self.target_volume:.0f}mL dispensed", self.colors.WHITE)

        self.display.draw_status_bar("Press SELECT to start Run 1", self.colors.TEXT_INFO)

    def _start_run(self):
        """
        เริ่มรอบการวัด (Start measurement run)
        """
        self.current_run += 1
        self.state = 'running'

        # แสดงหน้าจอการรัน (Display run screen)
        self._show_run_screen()

        # เริ่มปั๊ม (Start pump)
        self._start_pump()

    def _stop_run(self):
        """
        หยุดรอบการวัด (Stop measurement run)
        """
        # หยุดปั๊ม (Stop pump)
        elapsed_time = self._stop_pump()

        # บันทึกเวลา (Record time)
        self.run_times.append(elapsed_time)

        # คำนวณอัตราการไหลของรอบนี้ (Calculate this run's flow rate)
        flow_rate = self.target_volume / elapsed_time if elapsed_time > 0 else 0
        self.flow_rates.append(flow_rate)

        # แสดงผลรอบนี้ (Display this run's result)
        self._show_run_result(elapsed_time, flow_rate)

        # เปลี่ยนสถานะ (Change state)
        if self.current_run >= self.num_runs:
            self.state = 'waiting'
            self.display.draw_status_bar("Press SELECT to view results", self.colors.TEXT_INFO)
        else:
            self.state = 'waiting'
            self.display.draw_status_bar(f"Press SELECT for Run {self.current_run + 1}", self.colors.TEXT_INFO)

    def _show_run_screen(self):
        """
        แสดงหน้าจอขณะรัน (Display running screen)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        self.display.draw_text(20, 45, f"Run {self.current_run}/{self.num_runs}", self.colors.CYAN)
        self.display.draw_text(20, 75, f"Target: {self.target_volume:.1f} mL", self.colors.WHITE)

        self.display.draw_text(20, 110, "Elapsed Time:", self.colors.WHITE)
        self.display.draw_text(180, 110, "0.00 s", self.colors.YELLOW)

        self.display.draw_text(20, 145, "PUMP RUNNING", self.colors.GREEN)

        # วาด Progress Bar (Draw progress bar)
        self.display.draw_progress_bar(20, 180, 280, 20, 0)

        self.display.draw_status_bar(f"Press SELECT when {self.target_volume:.0f}mL reached", self.colors.TEXT_WARNING)

    def _update_time_display(self, elapsed_sec):
        """
        อัปเดตการแสดงผลเวลา (Update time display)

        Args:
            elapsed_sec (float): เวลาที่ผ่านไปในวินาที (Elapsed seconds)
        """
        # อัปเดตเวลา (Update time)
        self.display.fill_rect(180, 110, 120, 24, self.colors.BLACK)
        self.display.draw_text(180, 110, f"{elapsed_sec:.2f} s", self.colors.YELLOW)

        # อัปเดต Progress Bar (สมมติ 30 วินาทีเป็น 100%)
        # Update progress bar (assume 30 seconds is 100%)
        progress = min(elapsed_sec / 30.0, 1.0)
        self.display.draw_progress_bar(20, 180, 280, 20, progress, fg_color=self.colors.GREEN)

    def _show_run_result(self, elapsed_time, flow_rate):
        """
        แสดงผลลัพธ์ของรอบ (Display run result)

        Args:
            elapsed_time (float): เวลาที่ใช้ (Time used)
            flow_rate (float): อัตราการไหล (Flow rate)
        """
        self.display.fill_rect(20, 145, 280, 30, self.colors.BLACK)
        self.display.draw_text(20, 145, "PUMP STOPPED", self.colors.RED)

        self.display.fill_rect(20, 180, 280, 50, self.colors.BLACK)
        self.display.draw_text(20, 180, f"Time: {elapsed_time:.2f} s", self.colors.WHITE)
        self.display.draw_text(20, 205, f"Flow Rate: {flow_rate:.4f} mL/s", self.colors.GREEN)

    def _calculate_results(self):
        """
        คำนวณผลลัพธ์รวม (Calculate overall results)
        """
        if len(self.flow_rates) > 0:
            # คำนวณค่าเฉลี่ย (Calculate mean)
            self.avg_flow_rate = sum(self.flow_rates) / len(self.flow_rates)

            # คำนวณส่วนเบี่ยงเบนมาตรฐาน (Calculate standard deviation)
            if len(self.flow_rates) > 1:
                variance = sum((x - self.avg_flow_rate) ** 2 for x in self.flow_rates) / len(self.flow_rates)
                self.std_dev = variance ** 0.5
            else:
                self.std_dev = 0
        else:
            self.avg_flow_rate = 0
            self.std_dev = 0

        print(f"Average Flow Rate: {self.avg_flow_rate:.4f} +/- {self.std_dev:.4f} mL/s")

    def _show_results(self):
        """
        แสดงผลลัพธ์การสอบเทียบ (Display calibration results)
        """
        self.display.clear()
        self.display.draw_header("Flow Calibration Results")

        y = 40

        # แสดงอัตราการไหลเฉลี่ย (Display average flow rate)
        self.display.draw_text(20, y, "Average Flow Rate:", self.colors.WHITE)
        y += 25
        self.display.draw_text(30, y, f"{self.avg_flow_rate:.4f} mL/s", self.colors.GREEN)
        y += 30

        # แสดงส่วนเบี่ยงเบน (Display standard deviation)
        self.display.draw_text(20, y, f"Std Dev: +/- {self.std_dev:.4f} mL/s", self.colors.CYAN)
        y += 35

        # แสดงแต่ละรอบ (Display individual runs)
        self.display.draw_text(20, y, "Individual Runs:", self.colors.WHITE)
        y += 22

        for i, (time_sec, rate) in enumerate(zip(self.run_times, self.flow_rates)):
            self.display.draw_text(30, y, f"Run {i+1}: {time_sec:.2f}s -> {rate:.4f} mL/s", self.colors.TEXT_INFO)
            y += 20

        # ตั้งค่าผลลัพธ์ (Set results)
        self.set_results(
            flow_rate=self.avg_flow_rate,
            std_dev=self.std_dev,
            points=list(zip(self.run_times, [self.target_volume] * len(self.run_times))),
            calibration_type='flow'
        )

        self.display.draw_status_bar("Press SELECT to save", self.colors.TEXT_INFO)

    def _save_calibration(self):
        """
        บันทึกการสอบเทียบอัตราการไหล (Save flow rate calibration)

        ใช้ 4 ทศนิยมเพื่อลดความคลาดเคลื่อนปริมาตรสะสม
        Uses 4 decimal places to minimize cumulative volume error
        (Volume = flow_rate * time, error accumulates with each dose)
        """
        try:
            with open('data_flowrate.txt', 'w') as f:
                # บันทึก 4 ทศนิยม (Save with 4 decimal places)
                f.write(f"{self.avg_flow_rate:.4f}\n")
                f.write(f"Last saved: Manual calibration\n")

            print(f"บันทึกอัตราการไหล: {self.avg_flow_rate:.4f} mL/s (Flow rate saved)")

            # อัปเดตปั๊ม (Update pump)
            if self.pump:
                self.pump.flow_rate = self.avg_flow_rate

        except Exception as e:
            print(f"ข้อผิดพลาดการบันทึก (Save error): {e}")

    # ==========================================================================
    # Pump Control Methods
    # ==========================================================================

    def _start_pump(self):
        """
        เริ่มปั๊ม (Start pump)
        """
        self._pump_start_time = ticks_us()
        self._pump_is_running = True

        if self.pump:
            self.pump.set_duty(self.PUMP_DUTY_PERCENT)
        else:
            print("Warning: No pump connected")

    def _stop_pump(self):
        """
        หยุดปั๊มและคืนเวลาที่ใช้ (Stop pump and return elapsed time)

        Returns:
            float: เวลาที่ผ่านไปในวินาที (Elapsed time in seconds)
        """
        stop_time = ticks_us()
        self._pump_is_running = False

        if self.pump:
            self.pump.stop()

        # คำนวณเวลาที่ผ่านไป (Calculate elapsed time)
        elapsed_us = ticks_diff(stop_time, self._pump_start_time)
        elapsed_sec = elapsed_us / 1_000_000

        return elapsed_sec

    def _get_pump_elapsed_time(self):
        """
        รับเวลาที่ปั๊มทำงาน (Get pump running time)

        Returns:
            float: เวลาที่ผ่านไปในวินาที (Elapsed seconds)
        """
        if self._pump_is_running:
            elapsed_us = ticks_diff(ticks_us(), self._pump_start_time)
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
    print("CalibrateFlowMode Module")
    print("========================")
    print("This mode performs flow rate calibration.")
    print("")
    print(f"Target volume: {CalibrateFlowMode.TARGET_VOLUME_ML} mL")
    print(f"Number of runs: {CalibrateFlowMode.NUM_RUNS}")
    print("")
    print("Process:")
    print("1. Press SELECT to start pump")
    print("2. Measure dispensed volume manually")
    print("3. Press SELECT when target volume reached")
    print("4. Repeat for all runs")
    print("5. View and save average flow rate")

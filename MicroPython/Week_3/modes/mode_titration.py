# ==============================================================================
# mode_titration.py - โหมดไทเทรตอัตโนมัติ (Full Auto Titration Mode)
# ==============================================================================
# โหมดนี้ดำเนินการไทเทรตอัตโนมัติแบบเต็มรูปแบบ พร้อมบันทึกข้อมูลลง CSV
# This mode performs full automatic titration with CSV data logging
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้หลักการไทเทรตกรด-เบส (Acid-base titration principles)
# 2. เข้าใจการตรวจจับจุดสมมูล (Equivalence point detection)
# 3. ฝึกการบันทึกข้อมูลแบบ real-time (Real-time data logging)
# 4. เรียนรู้การควบคุมแบบหลายเฟส (Multi-phase control)
#
# หลักการทางเคมี (Chemistry Principles):
# - จุดสมมูล (Equivalence Point): จุดที่ปริมาณกรด = ปริมาณเบส (mol)
# - การเปลี่ยนแปลง pH จะรุนแรงใกล้จุดสมมูล (Sharp pH change near equivalence)
# - ใช้ derivative (dpH/dV) ตรวจจับจุดสมมูล (Use derivative for detection)
#
# เฟสการทำงาน (Operation Phases):
# 1. Fast Dosing (100%): เติมเร็วตอนเริ่มต้น ห่างจาก endpoint
# 2. Slow Dosing (50%): เติมช้าเมื่อใกล้ endpoint
# 3. Endpoint: หยุดเมื่อถึงจุดสมมูลหรือ pH เป้าหมาย
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff, ticks_us
import os


class TitrationMode(BaseMode):
    """
    โหมดไทเทรตอัตโนมัติ (Full Auto Titration Mode)

    ดำเนินการไทเทรตอัตโนมัติพร้อมบันทึกข้อมูลลง CSV
    Performs automatic titration with CSV data logging

    Attributes:
        ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
        pump: ออบเจ็กต์ปั๊ม (Pump object)
        temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor object)
        target_ph (float): ค่า pH เป้าหมาย (Target pH)
    """

    # ค่าคงที่สำหรับการไทเทรต (Titration Constants)
    DEFAULT_TARGET_PH = 7.0     # pH เป้าหมายเริ่มต้น (Default target pH)
    PH_THRESHOLD_FAST = 1.5     # ห่างจากเป้าหมาย > 1.5 = fast (Distance for fast)
    PH_THRESHOLD_SLOW = 0.3     # ห่างจากเป้าหมาย < 0.3 = endpoint (Distance for endpoint)

    # Duty Cycles สำหรับแต่ละเฟส (Duty cycles for each phase)
    DUTY_FAST = 100             # 100% สำหรับ fast dosing
    DUTY_SLOW = 50              # 50% สำหรับ slow dosing

    # การบันทึกข้อมูล (Data Logging)
    LOG_INTERVAL_MS = 500       # บันทึกทุก 500 ms
    MAX_VOLUME_ML = 50.0        # ปริมาตรสูงสุด mL (Safety limit)
    MAX_DURATION_SEC = 600      # เวลาสูงสุด 10 นาที (Safety limit)

    def __init__(self, display, colors, ph_sensor, pump, temp_sensor=None, buzzer=None):
        """
        สร้างโหมดไทเทรตอัตโนมัติ (Create auto titration mode)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
            pump: ออบเจ็กต์ปั๊ม (Pump object)
            temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor object)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object)
        """
        super().__init__(display, colors, "Full Auto Titration")

        self.ph_sensor = ph_sensor
        self.pump = pump
        self.temp_sensor = temp_sensor
        self.buzzer = buzzer

        # การตั้งค่า (Settings)
        self.target_ph = self.DEFAULT_TARGET_PH
        self.flow_rate = 0.1  # จะโหลดจากไฟล์ (Will load from file)

        # สถานะ (State)
        self.state = 'setup'  # 'setup', 'ready', 'titrating', 'complete', 'error'
        self.phase = 'ready'  # 'fast', 'slow', 'endpoint'

        # ข้อมูลการไทเทรต (Titration data)
        self.data_log = []    # [(timestamp, volume, pH, temp), ...]
        self.start_time = 0
        self.total_volume = 0.0
        self.endpoint_ph = 0.0
        self.endpoint_volume = 0.0

        # ตัวแปรสำหรับการวัดปริมาตร (Volume measurement variables)
        self._pump_start_time = 0
        self._pump_total_time = 0  # รวมเวลาปั๊มทำงาน (Total pump time)
        self._is_pumping = False

        # ตัวแปรสำหรับการบันทึก (Logging variables)
        self._last_log_time = 0

        # ชื่อไฟล์ (Filename)
        self.csv_filename = ""

    def on_enter(self):
        """
        เริ่มต้นโหมดไทเทรต (Start titration mode)
        """
        super().on_enter()

        # โหลดการตั้งค่า (Load settings)
        self._load_settings()

        # รีเซ็ตข้อมูล (Reset data)
        self.data_log = []
        self.total_volume = 0.0
        self._pump_total_time = 0
        self._is_pumping = False
        self.phase = 'ready'
        self.state = 'setup'

        # แสดงหน้าจอตั้งค่า (Display setup screen)
        self._show_setup_screen()

    def update(self):
        """
        อัปเดตสถานะการไทเทรต (Update titration state)
        """
        if self.state == 'setup':
            self._handle_setup_state()
        elif self.state == 'ready':
            self._handle_ready_state()
        elif self.state == 'titrating':
            self._handle_titrating_state()
        elif self.state == 'complete':
            self._handle_complete_state()
        elif self.state == 'error':
            self._handle_error_state()

    def on_exit(self):
        """
        ออกจากโหมดไทเทรต (Exit titration mode)
        """
        # หยุดปั๊ม (Stop pump)
        if self._is_pumping:
            self._stop_pump()

        super().on_exit()

    # ==========================================================================
    # State Handlers
    # ==========================================================================

    def _handle_setup_state(self):
        """
        จัดการสถานะตั้งค่า (Handle setup state)
        """
        # ปุ่ม UP - เพิ่ม target pH (UP - increase target pH)
        if self.check_button('up'):
            self._beep()
            self._adjust_target_ph(0.5)

        # ปุ่ม DOWN - ลด target pH (DOWN - decrease target pH)
        elif self.check_button('down'):
            self._beep()
            self._adjust_target_ph(-0.5)

        # ปุ่ม SELECT - ยืนยัน (SELECT - confirm)
        elif self.check_button('select'):
            self._beep()
            self._prepare_titration()
            self._show_ready_screen()
            self.state = 'ready'

    def _handle_ready_state(self):
        """
        จัดการสถานะพร้อม (Handle ready state)
        """
        # ปุ่ม SELECT - เริ่มไทเทรต (SELECT - start titration)
        if self.check_button('select'):
            self._beep()
            self._start_titration()

        # ปุ่ม DOWN - กลับไปตั้งค่า (DOWN - back to setup)
        elif self.check_button('down'):
            self._beep()
            self.state = 'setup'
            self._show_setup_screen()

    def _handle_titrating_state(self):
        """
        จัดการสถานะกำลังไทเทรต (Handle titrating state)
        """
        current_time = ticks_ms()

        # อ่านค่า pH ปัจจุบัน (Read current pH)
        current_ph = self._read_ph()

        # คำนวณปริมาตรที่จ่าย (Calculate dispensed volume)
        self.total_volume = self._calculate_volume()

        # บันทึกข้อมูลตามระยะเวลา (Log data at intervals)
        if ticks_diff(current_time, self._last_log_time) >= self.LOG_INTERVAL_MS:
            self._log_data()
            self._last_log_time = current_time

        # อัปเดตหน้าจอ (Update display)
        self._update_titration_display(current_ph)

        # ตรวจสอบเฟสและปรับการจ่าย (Check phase and adjust dosing)
        self._check_and_adjust_phase(current_ph)

        # ตรวจสอบเงื่อนไขความปลอดภัย (Check safety conditions)
        if self._check_safety_limits():
            return

        # ตรวจสอบปุ่ม SELECT เพื่อหยุดก่อนกำหนด (Check SELECT to stop early)
        if self.check_button('select'):
            self._beep()
            self._complete_titration("Manual stop")

    def _handle_complete_state(self):
        """
        จัดการสถานะเสร็จสิ้น (Handle complete state)
        """
        # ปุ่ม SELECT - ออก (SELECT - exit)
        if self.check_button('select'):
            self._beep()
            self.set_complete()

    def _handle_error_state(self):
        """
        จัดการสถานะผิดพลาด (Handle error state)
        """
        # ปุ่ม SELECT - ออก (SELECT - exit)
        if self.check_button('select'):
            self._beep()
            self.set_complete()

    # ==========================================================================
    # Titration Control Methods
    # ==========================================================================

    def _load_settings(self):
        """
        โหลดการตั้งค่าจากไฟล์ (Load settings from files)
        """
        # โหลด flow rate (Load flow rate)
        try:
            with open('data_flowrate.txt', 'r') as f:
                self.flow_rate = float(f.readline().strip())
        except:
            self.flow_rate = 0.1  # ค่าเริ่มต้น (Default value)

        print(f"Flow rate: {self.flow_rate:.4f} mL/s")

    def _prepare_titration(self):
        """
        เตรียมการไทเทรต (Prepare titration)
        """
        # กำหนดชื่อไฟล์ CSV (Generate CSV filename)
        self.csv_filename = self._generate_filename()
        print(f"จะบันทึกข้อมูลลง (Will save to): {self.csv_filename}")

    def _start_titration(self):
        """
        เริ่มการไทเทรต (Start titration)
        """
        self.state = 'titrating'
        self.phase = 'fast'
        self.start_time = ticks_ms()
        self._last_log_time = self.start_time
        self._pump_total_time = 0

        # เริ่มปั๊มในโหมด fast (Start pump in fast mode)
        self._start_pump(self.DUTY_FAST)

        # แสดงหน้าจอไทเทรต (Display titration screen)
        self._show_titration_screen()

        print("เริ่มการไทเทรต (Titration started)")

    def _check_and_adjust_phase(self, current_ph):
        """
        ตรวจสอบและปรับเฟสการจ่าย (Check and adjust dosing phase)

        Args:
            current_ph (float): ค่า pH ปัจจุบัน (Current pH)
        """
        # คำนวณระยะห่างจากเป้าหมาย (Calculate distance from target)
        distance = abs(current_ph - self.target_ph)

        # กำหนดเฟสใหม่ (Determine new phase)
        if distance <= self.PH_THRESHOLD_SLOW:
            # ถึงจุดสมมูล - หยุด (Reached endpoint - stop)
            self._stop_pump()
            self.endpoint_ph = current_ph
            self.endpoint_volume = self.total_volume
            self._complete_titration("Endpoint reached")
            return

        elif distance <= self.PH_THRESHOLD_FAST:
            # ใกล้จุดสมมูล - เปลี่ยนเป็น slow (Near endpoint - switch to slow)
            if self.phase != 'slow':
                self.phase = 'slow'
                self._set_pump_duty(self.DUTY_SLOW)
                print(f"เปลี่ยนเป็น slow dosing @ pH {current_ph:.2f}")

        else:
            # ยังห่าง - ใช้ fast (Still far - use fast)
            if self.phase != 'fast':
                self.phase = 'fast'
                self._set_pump_duty(self.DUTY_FAST)
                print(f"เปลี่ยนเป็น fast dosing @ pH {current_ph:.2f}")

    def _check_safety_limits(self):
        """
        ตรวจสอบเงื่อนไขความปลอดภัย (Check safety conditions)

        Returns:
            bool: True ถ้าเกินขีดจำกัด (True if limit exceeded)
        """
        # ตรวจสอบปริมาตรสูงสุด (Check max volume)
        if self.total_volume >= self.MAX_VOLUME_ML:
            self._stop_pump()
            self._complete_titration("Max volume reached")
            return True

        # ตรวจสอบเวลาสูงสุด (Check max time)
        elapsed = self.get_elapsed_time()
        if elapsed >= self.MAX_DURATION_SEC:
            self._stop_pump()
            self._complete_titration("Max time reached")
            return True

        return False

    def _complete_titration(self, reason):
        """
        เสร็จสิ้นการไทเทรต (Complete titration)

        Args:
            reason (str): เหตุผลที่หยุด (Stop reason)
        """
        # หยุดปั๊ม (Stop pump)
        self._stop_pump()

        # บันทึกข้อมูลสุดท้าย (Log final data)
        self._log_data()

        # บันทึกไฟล์ CSV (Save CSV file)
        self._save_csv()

        # บันทึก endpoint ถ้ายังไม่ได้บันทึก (Record endpoint if not recorded)
        if self.endpoint_volume == 0:
            self.endpoint_ph = self._read_ph()
            self.endpoint_volume = self.total_volume

        # แสดงหน้าจอผลลัพธ์ (Display results screen)
        self._show_results_screen(reason)

        # ตั้งค่าผลลัพธ์ (Set results)
        self.set_results(
            endpoint_ph=self.endpoint_ph,
            volume_used=self.endpoint_volume,
            duration=self.get_elapsed_time(),
            saved_file=self.csv_filename,
            data_points=len(self.data_log)
        )

        self.state = 'complete'
        print(f"ไทเทรตเสร็จสิ้น: {reason} (Titration complete: {reason})")

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
        self.display.draw_text(20, y, "Auto Titration Setup", self.colors.WHITE)
        y += 35

        self.display.draw_text(20, y, "Target pH:", self.colors.WHITE)
        self._update_target_ph_display()
        y += 35

        self.display.draw_text(20, y, f"Flow Rate: {self.flow_rate:.4f} mL/s", self.colors.CYAN)
        y += 30

        # แสดงเฟสการทำงาน (Display phases)
        self.display.draw_text(20, y, "Phases:", self.colors.WHITE)
        y += 22
        self.display.draw_text(30, y, f"Fast: 100% (pH > {self.PH_THRESHOLD_FAST} from target)", self.colors.TEXT_INFO)
        y += 20
        self.display.draw_text(30, y, f"Slow: 50% (pH < {self.PH_THRESHOLD_FAST} from target)", self.colors.TEXT_INFO)

        self.display.draw_status_bar("UP/DOWN: Adjust pH  SELECT: Next", self.colors.TEXT_INFO)

    def _update_target_ph_display(self):
        """
        อัปเดตการแสดงผล target pH (Update target pH display)
        """
        self.display.fill_rect(150, 80, 100, 30, self.colors.BLACK)
        self.display.draw_text(150, 80, f"{self.target_ph:.1f}", self.colors.GREEN)

    def _show_ready_screen(self):
        """
        แสดงหน้าจอพร้อม (Display ready screen)
        """
        self.display.clear()
        self.display.draw_header("Ready to Titrate")

        y = 50
        self.display.draw_text(20, y, f"Target pH: {self.target_ph:.1f}", self.colors.GREEN)
        y += 30

        # อ่านค่า pH ปัจจุบัน (Read current pH)
        current_ph = self._read_ph()
        self.display.draw_text(20, y, f"Current pH: {current_ph:.2f}", self.colors.YELLOW)
        y += 40

        self.display.draw_text(20, y, "Checklist:", self.colors.WHITE)
        y += 25
        self.display.draw_text(30, y, "- Probe in sample", self.colors.TEXT_INFO)
        y += 22
        self.display.draw_text(30, y, "- Titrant ready", self.colors.TEXT_INFO)
        y += 22
        self.display.draw_text(30, y, "- No air bubbles", self.colors.TEXT_INFO)

        self.display.draw_status_bar("SELECT: Start  DOWN: Back", self.colors.TEXT_INFO)

    def _show_titration_screen(self):
        """
        แสดงหน้าจอขณะไทเทรต (Display titrating screen)
        """
        self.display.clear()
        self.display.draw_header("Titrating...")

        # Labels
        self.display.draw_text(20, 45, "Phase:", self.colors.WHITE)
        self.display.draw_text(20, 75, "pH:", self.colors.WHITE)
        self.display.draw_text(20, 105, "Target:", self.colors.WHITE)
        self.display.draw_text(20, 135, "Volume:", self.colors.WHITE)
        self.display.draw_text(20, 165, "Time:", self.colors.WHITE)

        self.display.draw_status_bar("Press SELECT to stop", self.colors.TEXT_WARNING)

    def _update_titration_display(self, current_ph):
        """
        อัปเดตหน้าจอขณะไทเทรต (Update titrating display)

        Args:
            current_ph (float): ค่า pH ปัจจุบัน (Current pH)
        """
        # อัปเดตเฟส (Update phase)
        phase_text = self._get_phase_text()
        phase_color = self._get_phase_color()
        self.display.fill_rect(100, 45, 200, 24, self.colors.BLACK)
        self.display.draw_text(100, 45, phase_text, phase_color)

        # อัปเดต pH (Update pH)
        self.display.fill_rect(100, 75, 150, 24, self.colors.BLACK)
        ph_color = self.colors.GREEN if abs(current_ph - self.target_ph) < 1 else self.colors.YELLOW
        self.display.draw_text(100, 75, f"{current_ph:.2f}", ph_color)

        # อัปเดต Target (Update target)
        self.display.fill_rect(100, 105, 100, 24, self.colors.BLACK)
        self.display.draw_text(100, 105, f"{self.target_ph:.1f}", self.colors.WHITE)

        # อัปเดตปริมาตร (Update volume)
        self.display.fill_rect(100, 135, 150, 24, self.colors.BLACK)
        self.display.draw_text(100, 135, f"{self.total_volume:.2f} mL", self.colors.CYAN)

        # อัปเดตเวลา (Update time)
        elapsed = self.get_elapsed_time()
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.display.fill_rect(100, 165, 100, 24, self.colors.BLACK)
        self.display.draw_text(100, 165, f"{minutes:02.0f}:{seconds:02.0f}", self.colors.WHITE)

        # อัปเดต Progress (pH distance)
        distance = abs(current_ph - self.target_ph)
        progress = max(0, 1 - (distance / 5))  # Assume max distance of 5
        self.display.draw_progress_bar(20, 200, 280, 15, progress)

    def _show_results_screen(self, reason):
        """
        แสดงหน้าจอผลลัพธ์ (Display results screen)

        Args:
            reason (str): เหตุผลที่หยุด (Stop reason)
        """
        self.display.clear()
        self.display.draw_header("Titration Complete")

        y = 45
        self.display.draw_text(20, y, f"Reason: {reason}", self.colors.WHITE)
        y += 30

        self.display.draw_text(20, y, f"Endpoint pH: {self.endpoint_ph:.2f}", self.colors.GREEN)
        y += 25

        self.display.draw_text(20, y, f"Volume Used: {self.endpoint_volume:.2f} mL", self.colors.YELLOW)
        y += 25

        elapsed = self.get_elapsed_time()
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.display.draw_text(20, y, f"Duration: {minutes:02.0f}:{seconds:02.0f}", self.colors.CYAN)
        y += 25

        self.display.draw_text(20, y, f"Data Points: {len(self.data_log)}", self.colors.WHITE)
        y += 30

        self.display.draw_text(20, y, f"Saved: {self.csv_filename}", self.colors.TEXT_INFO)

        self.display.draw_status_bar("Press SELECT to exit", self.colors.TEXT_INFO)

        # เล่นเสียงเสร็จสิ้น (Play completion sound)
        self._play_completion_sound()

    def _get_phase_text(self):
        """
        รับข้อความเฟส (Get phase text)

        Returns:
            str: ข้อความเฟส (Phase text)
        """
        texts = {
            'ready': 'Ready',
            'fast': 'Fast (100%)',
            'slow': 'Slow (50%)',
            'endpoint': 'Endpoint'
        }
        return texts.get(self.phase, self.phase)

    def _get_phase_color(self):
        """
        รับสีตามเฟส (Get phase color)

        Returns:
            int: สี RGB565 (RGB565 color)
        """
        colors = {
            'ready': self.colors.WHITE,
            'fast': self.colors.ORANGE,
            'slow': self.colors.YELLOW,
            'endpoint': self.colors.GREEN
        }
        return colors.get(self.phase, self.colors.WHITE)

    # ==========================================================================
    # Pump Control Methods
    # ==========================================================================

    def _start_pump(self, duty):
        """
        เริ่มปั๊ม (Start pump)

        Args:
            duty (int): Duty cycle 0-100%
        """
        self._pump_start_time = ticks_us()
        self._is_pumping = True

        if self.pump:
            self.pump.set_duty(duty)

    def _stop_pump(self):
        """
        หยุดปั๊ม (Stop pump)
        """
        if self._is_pumping:
            # บันทึกเวลาทำงาน (Record run time)
            elapsed_us = ticks_diff(ticks_us(), self._pump_start_time)
            self._pump_total_time += elapsed_us / 1_000_000

        self._is_pumping = False

        if self.pump:
            self.pump.stop()

    def _set_pump_duty(self, duty):
        """
        ตั้งค่า duty cycle ขณะปั๊มทำงาน (Set duty cycle while pump running)

        Args:
            duty (int): Duty cycle 0-100%
        """
        if self._is_pumping and self.pump:
            self.pump.set_duty(duty)

    def _calculate_volume(self):
        """
        คำนวณปริมาตรที่จ่าย (Calculate dispensed volume)

        Returns:
            float: ปริมาตรใน mL (Volume in mL)
        """
        current_run_time = 0
        if self._is_pumping:
            current_run_time = ticks_diff(ticks_us(), self._pump_start_time) / 1_000_000

        total_time = self._pump_total_time + current_run_time
        return total_time * self.flow_rate

    # ==========================================================================
    # Sensor Methods
    # ==========================================================================

    def _read_ph(self):
        """
        อ่านค่า pH (Read pH)

        Returns:
            float: ค่า pH (pH value)
        """
        if self.ph_sensor:
            try:
                return self.ph_sensor.read_ph()
            except:
                pass
        return 7.0

    def _read_temperature(self):
        """
        อ่านค่าอุณหภูมิ (Read temperature)

        Returns:
            float: อุณหภูมิ (Temperature)
        """
        if self.temp_sensor:
            try:
                return self.temp_sensor.read_temperature()
            except:
                pass
        return 25.0

    # ==========================================================================
    # Data Logging Methods
    # ==========================================================================

    def _log_data(self):
        """
        บันทึกข้อมูลลง log (Log data)
        """
        timestamp = self.get_elapsed_time()
        volume = self.total_volume
        ph = self._read_ph()
        temp = self._read_temperature()

        self.data_log.append((timestamp, volume, ph, temp))

    def _generate_filename(self):
        """
        สร้างชื่อไฟล์ CSV (Generate CSV filename)

        Returns:
            str: ชื่อไฟล์ (Filename)
        """
        # หาหมายเลขรันถัดไปจาก ESP32 flash storage
        # Find next run number from ESP32 flash storage
        run_number = 1
        try:
            # ไฟล์บันทึกใน ESP32 flash storage (root directory)
            # Files saved in ESP32 flash storage (root directory)
            files = os.listdir('.')
            for f in files:
                if f.startswith('titration_data_R') and f.endswith('.csv'):
                    try:
                        num = int(f.replace('titration_data_R', '').replace('.csv', ''))
                        run_number = max(run_number, num + 1)
                    except:
                        pass
        except:
            pass

        return f"titration_data_R{run_number}.csv"

    def _save_csv(self):
        """
        บันทึกข้อมูลลงไฟล์ CSV ใน ESP32 flash storage
        Save data to CSV file in ESP32 flash storage

        หมายเหตุ: ไม่ใช้ SD Card - ข้อมูลบันทึกใน ESP32 flash storage
        Note: SD Card NOT USED - data saved to ESP32 flash storage
        ดาวน์โหลดไฟล์ผ่าน Thonny IDE (Download files via Thonny IDE)
        """
        try:
            # บันทึกใน ESP32 flash storage (root directory)
            # Save to ESP32 flash storage (root directory)
            filepath = self.csv_filename

            # เขียนไฟล์ (Write file)
            with open(filepath, 'w') as f:
                # Header
                f.write("Time(s),Volume(mL),pH,Temperature(C)\n")

                # Data
                for timestamp, volume, ph, temp in self.data_log:
                    f.write(f"{timestamp:.2f},{volume:.3f},{ph:.3f},{temp:.2f}\n")

            print(f"บันทึกข้อมูล {len(self.data_log)} จุดลง {filepath}")
            print(f"Saved {len(self.data_log)} points to {filepath}")
            print(f"ดาวน์โหลดไฟล์ผ่าน Thonny IDE (Download via Thonny IDE)")

        except Exception as e:
            print(f"ข้อผิดพลาดการบันทึก (Save error): {e}")

    # ==========================================================================
    # Helper Methods
    # ==========================================================================

    def _adjust_target_ph(self, delta):
        """
        ปรับ target pH (Adjust target pH)

        Args:
            delta (float): ค่าที่ปรับ (Adjustment value)
        """
        new_ph = self.target_ph + delta
        self.target_ph = max(1.0, min(new_ph, 14.0))
        self._update_target_ph_display()

    def _beep(self):
        """
        เล่นเสียงบี๊ป (Play beep sound)
        """
        if self.buzzer:
            try:
                self.buzzer.beep()
            except:
                pass

    def _play_completion_sound(self):
        """
        เล่นเสียงเสร็จสิ้น (Play completion sound)
        """
        if self.buzzer:
            try:
                self.buzzer.beep()
                sleep_ms(100)
                self.buzzer.beep()
                sleep_ms(100)
                self.buzzer.beep()
            except:
                pass


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("TitrationMode Module")
    print("====================")
    print("This mode performs full automatic acid-base titration.")
    print("")
    print("Features:")
    print("- Two-phase dosing (fast/slow)")
    print("- Automatic endpoint detection")
    print("- Real-time data logging to CSV")
    print("- Safety limits (max volume, max time)")
    print("")
    print("Phases:")
    print(f"- Fast dosing (100%): pH distance > {TitrationMode.PH_THRESHOLD_FAST}")
    print(f"- Slow dosing (50%): pH distance < {TitrationMode.PH_THRESHOLD_FAST}")
    print(f"- Endpoint: pH distance < {TitrationMode.PH_THRESHOLD_SLOW}")

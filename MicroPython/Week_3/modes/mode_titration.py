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
# 4. เรียนรู้การควบคุมปั๊มแบบ stepwise (Stepwise pump control with constant dose)
#
# หลักการทางเคมี (Chemistry Principles):
# - จุดสมมูล (Equivalence Point): จุดที่ปริมาณกรด = ปริมาณเบส (mol)
# - การเปลี่ยนแปลง pH จะรุนแรงใกล้จุดสมมูล (Sharp pH change near equivalence)
# - ใช้ derivative (dpH/dV) ตรวจจับจุดสมมูล (Use derivative for detection)
#
# หลักการทำงาน (Operation Principle):
# ปั๊มปริมาตรคงที่ 0.2 mL ทุกครั้ง → หยุด → รอ pH คงที่ → อ่าน pH → ทำซ้ำ
# Constant 0.2 mL dose → stop → wait for pH stabilization → read pH → repeat
# วิธีนี้เรียบง่ายและช่วยให้นิสิตเข้าใจแนวคิดกราฟไทเทรชันได้ง่าย
# This approach is simpler and helps students understand the titration curve concept
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff
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
    PH_THRESHOLD_STOP = 0.3     # ห่างจากเป้าหมาย < 0.3 = endpoint (Distance for endpoint)

    # ปริมาตรสารตัวอย่างเริ่มต้น (Default sample volume)
    # สำหรับห้องปฏิบัติการเคมีทั่วไป ใช้ 5 mL (Typical teaching lab uses 5 mL)
    DEFAULT_SAMPLE_VOLUME_ML = 5.0  # mL ปริมาตรตัวอย่าง (sample volume)

    # ปริมาตรคงที่ต่อครั้ง (Fixed dose volume per step)
    # ใช้ปริมาตรคงที่ 0.2 mL ทุกครั้งเพื่อความเรียบง่ายในการเรียนรู้
    # Fixed 0.2 mL dose per step for pedagogical simplicity
    DOSE_VOLUME_ML = 0.2        # mL ต่อครั้ง (mL per dose step)
    PUMP_DUTY = 100             # 100% duty cycle ทุกครั้ง (always 100%)

    # เวลารอให้ pH คงที่ระหว่างแต่ละ dose (Stabilization time between doses)
    # pH probe ต้องการ 10-20 วินาทีจึงจะเสถียร (pH probe needs 10-20s to stabilize)
    STABILIZE_TIME_MS = 10000   # 10.0 วินาที (10.0 seconds)

    # ขีดจำกัดความปลอดภัย (Safety limits)
    # ปริมาตรสูงสุด = 2 เท่าของปริมาตรตัวอย่าง (Max = 2x sample volume)
    # คำนวณอัตโนมัติใน __init__ (Auto-calculated in __init__)
    MAX_DURATION_SEC = 600      # เวลาสูงสุด 10 นาที (Safety limit)

    # ค่า dpH/dV ที่ถือว่าถึงจุดสมมูล (Derivative threshold for equivalence point)
    DPHDV_THRESHOLD = 2.0       # |dpH/dV| > 2.0 ถือว่าถึงจุดสมมูล

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
        self.sample_volume = self.DEFAULT_SAMPLE_VOLUME_ML
        # ปริมาตรสูงสุด = 2 เท่าของปริมาตรตัวอย่าง (Max = 2x sample volume)
        # เพื่อให้ได้กราฟไทเทรชันรูป S ที่สมบูรณ์ (for complete S-shaped titration curve)
        self.max_volume = 2 * self.sample_volume
        self.flow_rate = 0.2772  # จะโหลดจากไฟล์ (Will load from file, 4 decimal places)

        # สถานะ (State)
        self.state = 'setup'  # 'setup', 'ready', 'titrating', 'complete', 'error'
        self.phase = 'dosing'  # 'dosing', 'stabilizing', 'reading', 'endpoint'

        # ข้อมูลการไทเทรต (Titration data)
        self.data_log = []    # [(timestamp, volume, pH, temp), ...]
        self.start_time = 0
        self.total_volume = 0.0
        self.endpoint_ph = 0.0
        self.endpoint_volume = 0.0

        # ตัวแปรสำหรับการนับรอบ (Cycle tracking variables)
        self.cycle_count = 0
        self.previous_ph = None     # pH ก่อนหน้าสำหรับคำนวณ derivative
        self._stabilize_start = 0   # เวลาเริ่มต้นช่วง stabilize

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
        self.cycle_count = 0
        self.previous_ph = None
        self._stabilize_start = 0
        self.phase = 'dosing'
        self.state = 'setup'

        # ขั้นตอนการตั้งค่า (Setup steps)
        # step 0: ปรับปริมาตรตัวอย่าง (Adjust sample volume)
        # step 1: ปรับ target pH (Adjust target pH)
        self._setup_step = 0

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
        self._stop_pump()

        super().on_exit()

    # ==========================================================================
    # State Handlers
    # ==========================================================================

    def _handle_setup_state(self):
        """
        จัดการสถานะตั้งค่า (Handle setup state)

        มี 2 ขั้นตอน (2 setup steps):
        - Step 0: ปรับปริมาตรตัวอย่าง (Adjust sample volume)
        - Step 1: ปรับ target pH (Adjust target pH)
        """
        if self._setup_step == 0:
            # --- ขั้นตอนที่ 0: ปรับปริมาตรตัวอย่าง ---
            # --- Step 0: Adjust sample volume ---

            # ปุ่ม UP - เพิ่มปริมาตรตัวอย่าง (UP - increase sample volume)
            if self.check_button('up'):
                self._beep()
                self._adjust_sample_volume(5.0)

            # ปุ่ม DOWN - ลดปริมาตรตัวอย่าง (DOWN - decrease sample volume)
            elif self.check_button('down'):
                self._beep()
                self._adjust_sample_volume(-5.0)

            # ปุ่ม SELECT - ไปขั้นตอนถัดไป (SELECT - next step)
            elif self.check_button('select'):
                self._beep()
                self._setup_step = 1
                self._show_setup_screen()

        elif self._setup_step == 1:
            # --- ขั้นตอนที่ 1: ปรับ target pH ---
            # --- Step 1: Adjust target pH ---

            # ปุ่ม UP - เพิ่ม target pH (UP - increase target pH)
            if self.check_button('up'):
                self._beep()
                self._adjust_target_ph(0.5)

            # ปุ่ม DOWN - ลด target pH (DOWN - decrease target pH)
            elif self.check_button('down'):
                self._beep()
                self._adjust_target_ph(-0.5)

            # ปุ่ม SELECT - ยืนยันและไปหน้า Ready (SELECT - confirm)
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

        หลักการทำงานแบบ stepwise (Stepwise operation principle):
        1. ปั๊ม 0.2 mL (phase='dosing') → 2. รอ pH คงที่ (phase='stabilizing')
        → 3. อ่าน pH และตรวจจับ endpoint (phase='reading') → กลับไป 1.

        ปั๊มปริมาตรคงที่ 0.2 mL ทุกครั้ง → หยุด → รอ pH คงที่ → อ่าน pH → ทำซ้ำ
        Constant 0.2 mL dose → stop → wait for pH stabilization → read pH → repeat
        """
        # ตรวจสอบปุ่ม SELECT เพื่อหยุดก่อนกำหนด (Check SELECT to stop early)
        if self.check_button('select'):
            self._beep()
            self._complete_titration("Manual stop")
            return

        # ตรวจสอบเงื่อนไขความปลอดภัย (Check safety conditions)
        if self._check_safety_limits():
            return

        # --- เฟส 1: ปั๊มปริมาตรคงที่ 0.2 mL (Phase 1: Pump fixed 0.2 mL dose) ---
        if self.phase == 'dosing':
            self.cycle_count += 1
            self._dispense_fixed_dose()
            # เปลี่ยนไปรอ stabilize (Switch to stabilization wait)
            self.phase = 'stabilizing'
            self._stabilize_start = ticks_ms()

        # --- เฟส 2: รอให้ pH คงที่ (Phase 2: Wait for pH stabilization) ---
        elif self.phase == 'stabilizing':
            elapsed = ticks_diff(ticks_ms(), self._stabilize_start)
            if elapsed >= self.STABILIZE_TIME_MS:
                # หมดเวลารอ เปลี่ยนไปอ่าน pH (Stabilization done, switch to reading)
                self.phase = 'reading'

        # --- เฟส 3: อ่าน pH และตรวจจับ endpoint (Phase 3: Read pH and check endpoint) ---
        elif self.phase == 'reading':
            current_ph = self._read_ph()
            temp = self._read_temperature()

            # บันทึกข้อมูล (Log data)
            self._log_data_point(current_ph, temp)

            # อัปเดตหน้าจอ (Update display)
            self._update_titration_display(current_ph)

            # คำนวณ dpH/dV สำหรับตรวจจับจุดสมมูล (Calculate dpH/dV for endpoint detection)
            derivative = self._calculate_derivative(current_ph)

            # แสดงข้อมูลใน console (Print to console)
            print(f"Cycle {self.cycle_count:3d}: V={self.total_volume:6.2f}mL, "
                  f"pH={current_ph:5.2f}, dpH/dV={derivative:+7.3f}")

            # ตรวจสอบ endpoint (Check endpoint conditions)
            if self._check_endpoint(current_ph, derivative):
                self.endpoint_ph = current_ph
                self.endpoint_volume = self.total_volume
                self._complete_titration("Endpoint reached")
                return

            # บันทึก pH ก่อนหน้า (Store previous pH for next derivative)
            self.previous_ph = current_ph

            # กลับไปเฟส dosing (Back to dosing phase)
            self.phase = 'dosing'

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

        อ่าน flow_rate จาก data_flowrate.txt (4 ทศนิยม)
        Reads flow_rate from data_flowrate.txt (4 decimal places)
        """
        # โหลด flow rate (Load flow rate)
        try:
            with open('data_flowrate.txt', 'r') as f:
                self.flow_rate = float(f.readline().strip())
        except:
            # ค่าเริ่มต้น 4 ทศนิยม (Default with 4 decimal places)
            self.flow_rate = 0.2772

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

        เริ่มลูปแบบ stepwise: ปั๊ม 0.2 mL → หยุด → รอ → อ่าน pH → ทำซ้ำ
        Start stepwise loop: pump 0.2 mL → stop → wait → read pH → repeat
        """
        self.state = 'titrating'
        self.phase = 'dosing'
        self.start_time = ticks_ms()
        self.cycle_count = 0
        self.previous_ph = self._read_ph()  # อ่านค่า pH เริ่มต้น (Read initial pH)

        # บันทึกจุดเริ่มต้น (Log initial point)
        self._log_data_point(self.previous_ph, self._read_temperature())

        # แสดงหน้าจอไทเทรต (Display titration screen)
        self._show_titration_screen()

        print("เริ่มการไทเทรต (Titration started)")
        print(f"ปริมาตรตัวอย่าง (Sample volume): {self.sample_volume:.1f} mL")
        print(f"ปริมาตรสูงสุด (Max volume): {self.max_volume:.1f} mL (2x sample)")
        print(f"ปริมาตรคงที่ต่อครั้ง (Fixed dose): {self.DOSE_VOLUME_ML} mL")
        print(f"จำนวน step ทั้งหมด (Total steps): {int(self.max_volume / self.DOSE_VOLUME_ML)}")
        print(f"pH เริ่มต้น (Initial pH): {self.previous_ph:.2f}")

    def _check_endpoint(self, current_ph, derivative):
        """
        ตรวจสอบว่าถึงจุดสมมูลหรือยัง (Check if endpoint is reached)

        เงื่อนไขการหยุด (Stop conditions):
        1. pH ใกล้เป้าหมาย (pH close to target)
        2. |dpH/dV| สูงมาก แสดงว่าผ่านจุดสมมูลแล้ว (Large |dpH/dV| = past equivalence)

        Args:
            current_ph (float): ค่า pH ปัจจุบัน (Current pH)
            derivative (float): ค่า dpH/dV (derivative value)

        Returns:
            bool: True ถ้าถึง endpoint (True if endpoint reached)
        """
        # เงื่อนไข 1: pH ใกล้เป้าหมาย (Condition 1: pH close to target)
        distance = abs(current_ph - self.target_ph)
        if distance <= self.PH_THRESHOLD_STOP:
            print(f"pH ถึงเป้าหมาย (pH reached target) @ pH {current_ph:.2f}")
            return True

        # เงื่อนไข 2: |dpH/dV| สูงมาก = ผ่านจุดสมมูล
        # (Condition 2: Large |dpH/dV| = past equivalence point)
        if self.cycle_count > 3 and abs(derivative) > self.DPHDV_THRESHOLD:
            print(f"ตรวจพบจุดสมมูล (Equivalence point detected) @ pH {current_ph:.2f}, "
                  f"|dpH/dV| = {abs(derivative):.2f}")
            return True

        return False

    def _calculate_derivative(self, current_ph):
        """
        คำนวณ dpH/dV (Calculate dpH/dV)

        วิธีคำนวณ: dpH/dV = (pH_current - pH_previous) / dose_volume
        เนื่องจากใช้ปริมาตรคงที่ทุกครั้ง dose_volume = 0.2 mL
        Since dose volume is constant, dose_volume = 0.2 mL

        Args:
            current_ph (float): ค่า pH ปัจจุบัน (Current pH)

        Returns:
            float: ค่า dpH/dV (derivative value)
        """
        if self.previous_ph is None:
            return 0.0

        delta_ph = current_ph - self.previous_ph
        # ปริมาตรคงที่ทุกครั้ง (Constant volume per step)
        derivative = delta_ph / self.DOSE_VOLUME_ML
        return derivative

    def _dispense_fixed_dose(self):
        """
        จ่ายสารละลายปริมาตรคงที่ 0.2 mL ที่ 100% duty cycle
        Dispense fixed 0.2 mL dose at 100% duty cycle

        คำนวณเวลาปั๊มจาก: time = volume / flow_rate
        Calculate pump time from: time = volume / flow_rate
        """
        # คำนวณเวลาที่ต้องปั๊ม (Calculate pump run time)
        pump_time_sec = self.DOSE_VOLUME_ML / self.flow_rate
        pump_time_ms = int(pump_time_sec * 1000)

        # เปิดปั๊มที่ 100% duty (Start pump at 100% duty)
        if self.pump:
            self.pump.set_duty(self.PUMP_DUTY)

        # รอจนครบเวลา (Wait for pump duration)
        sleep_ms(pump_time_ms)

        # หยุดปั๊ม (Stop pump)
        self._stop_pump()

        # อัปเดตปริมาตรรวม (Update total volume)
        self.total_volume += self.DOSE_VOLUME_ML

    def _check_safety_limits(self):
        """
        ตรวจสอบเงื่อนไขความปลอดภัย (Check safety conditions)

        ปริมาตรสูงสุด = 2 เท่าของปริมาตรตัวอย่าง (Max = 2x sample volume)
        Safety stops if volume exceeds 2x sample volume

        Returns:
            bool: True ถ้าเกินขีดจำกัด (True if limit exceeded)
        """
        # ตรวจสอบปริมาตรสูงสุด (Check max volume = 2x sample volume)
        if self.total_volume >= self.max_volume:
            self._stop_pump()
            self._complete_titration("Max volume reached (2x sample)")
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

        มี 2 ขั้นตอน (2 steps):
        - Step 0: ปรับปริมาตรตัวอย่าง (Adjust sample volume)
        - Step 1: ปรับ target pH (Adjust target pH)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        y = 45

        if self._setup_step == 0:
            # --- ขั้นตอนที่ 0: ตั้งค่าปริมาตรตัวอย่าง ---
            # --- Step 0: Set sample volume ---
            self.display.draw_text(20, y, "Step 1: Sample Volume", self.colors.WHITE)
            y += 30

            # แสดงปริมาตรตัวอย่าง (Display sample volume)
            self.display.draw_text(20, y, "Sample:", self.colors.WHITE)
            self._update_sample_volume_display()
            y += 30

            # แสดงปริมาตรสูงสุดที่คำนวณได้ (Display calculated max volume)
            total_steps = int(self.max_volume / self.DOSE_VOLUME_ML)
            self.display.draw_text(20, y, f"Max titrant: {self.max_volume:.1f} mL (2x)", self.colors.CYAN)
            y += 25
            self.display.draw_text(20, y, f"Dose: {self.DOSE_VOLUME_ML} mL/step", self.colors.TEXT_INFO)
            y += 22
            self.display.draw_text(20, y, f"Total steps: {total_steps}", self.colors.TEXT_INFO)
            y += 30

            self.display.draw_text(20, y, f"Flow Rate: {self.flow_rate:.4f} mL/s", self.colors.CYAN)

            self.display.draw_status_bar("UP/DOWN: Volume  SELECT: Next", self.colors.TEXT_INFO)

        elif self._setup_step == 1:
            # --- ขั้นตอนที่ 1: ตั้งค่า target pH ---
            # --- Step 1: Set target pH ---
            self.display.draw_text(20, y, "Step 2: Target pH", self.colors.WHITE)
            y += 30

            self.display.draw_text(20, y, "Target pH:", self.colors.WHITE)
            self._update_target_ph_display()
            y += 35

            # แสดงสรุปการตั้งค่า (Display settings summary)
            total_steps = int(self.max_volume / self.DOSE_VOLUME_ML)
            self.display.draw_text(20, y, f"Sample: {self.sample_volume:.1f} mL", self.colors.CYAN)
            y += 22
            self.display.draw_text(20, y, f"Max: {self.max_volume:.1f} mL ({total_steps} steps)", self.colors.CYAN)
            y += 30

            # แสดงวิธีการไทเทรต (Display titration method)
            self.display.draw_text(20, y, "Method: Constant Dose", self.colors.WHITE)
            y += 22
            self.display.draw_text(30, y, f"Dose: {self.DOSE_VOLUME_ML} mL per step", self.colors.TEXT_INFO)

            self.display.draw_status_bar("UP/DOWN: Adjust pH  SELECT: Start", self.colors.TEXT_INFO)

    def _update_target_ph_display(self):
        """
        อัปเดตการแสดงผล target pH (Update target pH display)
        """
        self.display.fill_rect(150, 75, 100, 30, self.colors.BLACK)
        self.display.draw_text(150, 75, f"{self.target_ph:.1f}", self.colors.GREEN)

    def _update_sample_volume_display(self):
        """
        อัปเดตการแสดงผลปริมาตรตัวอย่าง (Update sample volume display)
        """
        self.display.fill_rect(120, 75, 150, 30, self.colors.BLACK)
        self.display.draw_text(120, 75, f"{self.sample_volume:.1f} mL", self.colors.GREEN)

    def _show_ready_screen(self):
        """
        แสดงหน้าจอพร้อม (Display ready screen)
        """
        self.display.clear()
        self.display.draw_header("Ready to Titrate")

        y = 45
        # แสดงสรุปการตั้งค่า (Display settings summary)
        total_steps = int(self.max_volume / self.DOSE_VOLUME_ML)
        self.display.draw_text(20, y, f"Sample: {self.sample_volume:.1f} mL", self.colors.CYAN)
        y += 22
        self.display.draw_text(20, y, f"Max: {self.max_volume:.1f} mL (2x, {total_steps} steps)", self.colors.CYAN)
        y += 22
        self.display.draw_text(20, y, f"Target pH: {self.target_ph:.1f}", self.colors.GREEN)
        y += 30

        # อ่านค่า pH ปัจจุบัน (Read current pH)
        current_ph = self._read_ph()
        self.display.draw_text(20, y, f"Current pH: {current_ph:.2f}", self.colors.YELLOW)
        y += 30

        self.display.draw_text(20, y, "Checklist:", self.colors.WHITE)
        y += 22
        self.display.draw_text(30, y, "- Probe in sample", self.colors.TEXT_INFO)
        y += 20
        self.display.draw_text(30, y, "- Titrant ready", self.colors.TEXT_INFO)
        y += 20
        self.display.draw_text(30, y, "- No air bubbles", self.colors.TEXT_INFO)

        self.display.draw_status_bar("SELECT: Start  DOWN: Back", self.colors.TEXT_INFO)

    def _show_titration_screen(self):
        """
        แสดงหน้าจอขณะไทเทรต (Display titrating screen)
        """
        self.display.clear()
        self.display.draw_header("Titrating...")

        # Labels (แสดง Cycle แทน Phase เนื่องจากใช้ stepwise)
        self.display.draw_text(20, 45, "Cycle:", self.colors.WHITE)
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
        # อัปเดตรอบ (Update cycle count)
        cycle_text = f"{self.cycle_count} ({self.DOSE_VOLUME_ML}mL/step)"
        self.display.fill_rect(100, 45, 200, 24, self.colors.BLACK)
        self.display.draw_text(100, 45, cycle_text, self.colors.CYAN)

        # อัปเดต pH (Update pH)
        self.display.fill_rect(100, 75, 150, 24, self.colors.BLACK)
        ph_color = self.colors.GREEN if abs(current_ph - self.target_ph) < 1 else self.colors.YELLOW
        self.display.draw_text(100, 75, f"{current_ph:.2f}", ph_color)

        # อัปเดต Target (Update target)
        self.display.fill_rect(100, 105, 100, 24, self.colors.BLACK)
        self.display.draw_text(100, 105, f"{self.target_ph:.1f}", self.colors.WHITE)

        # อัปเดตปริมาตร (Update volume: current / max)
        self.display.fill_rect(100, 135, 200, 24, self.colors.BLACK)
        self.display.draw_text(100, 135, f"{self.total_volume:.2f}/{self.max_volume:.0f} mL", self.colors.CYAN)

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

    # ==========================================================================
    # Pump Control Methods
    # ==========================================================================

    def _stop_pump(self):
        """
        หยุดปั๊ม (Stop pump)
        """
        if self.pump:
            self.pump.stop()

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

    def _log_data_point(self, ph, temp):
        """
        บันทึกจุดข้อมูลลง log (Log a data point)

        Args:
            ph (float): ค่า pH ที่อ่านได้ (pH value)
            temp (float): อุณหภูมิ (Temperature)
        """
        timestamp = self.get_elapsed_time()
        volume = self.total_volume
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
                # Header - ใช้ชื่อคอลัมน์ที่ตรงกับ EquivPoint analysis tool
                # Column names match EquivPoint tool: "Volume (mL)" and "pH Value"
                f.write("Volume (mL),pH Value,Time(s),Temperature(C)\n")

                # Data - Volume and pH first for EquivPoint compatibility
                for timestamp, volume, ph, temp in self.data_log:
                    f.write(f"{volume:.3f},{ph:.3f},{timestamp:.2f},{temp:.2f}\n")

            print(f"บันทึกข้อมูล {len(self.data_log)} จุดลง {filepath}")
            print(f"Saved {len(self.data_log)} points to {filepath}")
            print(f"ดาวน์โหลดไฟล์ผ่าน Thonny IDE (Download via Thonny IDE)")
            print(f"วิเคราะห์ด้วย: python equiv_point.py {filepath}")
            print(f"Analyze with: python equiv_point.py {filepath}")

        except Exception as e:
            print(f"ข้อผิดพลาดการบันทึก (Save error): {e}")

    # ==========================================================================
    # Helper Methods
    # ==========================================================================

    def _adjust_sample_volume(self, delta):
        """
        ปรับปริมาตรตัวอย่าง (Adjust sample volume)

        ปริมาตรสูงสุดจะถูกคำนวณอัตโนมัติเป็น 2 เท่า
        Max volume is auto-calculated as 2x sample volume

        Args:
            delta (float): ค่าที่ปรับ (Adjustment value in mL)
        """
        new_volume = self.sample_volume + delta
        # จำกัดช่วง 5-100 mL (Limit range 5-100 mL)
        self.sample_volume = max(5.0, min(new_volume, 100.0))
        # คำนวณปริมาตรสูงสุดอัตโนมัติ (Auto-calculate max volume)
        self.max_volume = 2 * self.sample_volume
        # อัปเดตหน้าจอ (Refresh display)
        self._show_setup_screen()

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
    print("Algorithm: Constant Dose Volume")
    print(f"- Dose volume: {TitrationMode.DOSE_VOLUME_ML} mL per step")
    print(f"- Pump duty: {TitrationMode.PUMP_DUTY}% (always)")
    print(f"- Stabilization: {TitrationMode.STABILIZE_TIME_MS} ms between doses")
    print("")
    print("Volume Strategy:")
    print(f"- Default sample volume: {TitrationMode.DEFAULT_SAMPLE_VOLUME_ML} mL")
    print(f"- Max titration volume: 2x sample = {2 * TitrationMode.DEFAULT_SAMPLE_VOLUME_ML} mL")
    print(f"- Total steps: {int(2 * TitrationMode.DEFAULT_SAMPLE_VOLUME_ML / TitrationMode.DOSE_VOLUME_ML)}")
    print("- Adjustable via buttons (5 mL increments, range 5-100 mL)")
    print("")
    print("Chemistry Rationale:")
    print("- Equivalence point ~= sample volume (equimolar titration)")
    print("- 2x sample ensures complete S-curve (before + after equivalence)")
    print("- Example: 25 mL sample -> 50 mL max -> full pH curve 2-12")
    print("")
    print("Features:")
    print("- Constant 0.2 mL dose per step (like manual titration drop-by-drop)")
    print("- Automatic endpoint detection via dpH/dV")
    print("- Real-time data logging to CSV (ESP32 flash)")
    print("- Safety limits (max volume = 2x sample, max time)")
    print("")
    print("Pedagogical Benefits:")
    print("- Every point on the curve is exactly 0.2 mL apart")
    print("- Students can verify: total_volume = dose_count x 0.2 mL")
    print("- Equivalence point is between two consecutive 0.2 mL steps")
    print("- Students learn to choose appropriate sample volume")

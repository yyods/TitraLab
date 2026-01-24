# ==============================================================================
# mode_calibrate_ph.py - โหมดสอบเทียบเซ็นเซอร์ pH (pH Sensor Calibration Mode)
# ==============================================================================
# โหมดนี้ดำเนินการสอบเทียบเซ็นเซอร์ pH แบบ 3 จุดด้วยบัฟเฟอร์มาตรฐาน
# This mode performs 3-point pH sensor calibration with standard buffers
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้หลักการสอบเทียบเซ็นเซอร์ (Sensor calibration principles)
# 2. เข้าใจสมการเส้นตรงและ Linear Regression (Linear equation and regression)
# 3. ฝึกการคำนวณค่า R-squared สำหรับประเมินความแม่นยำ
#
# หลักการทางเคมี (Chemistry Principles):
# - ใช้บัฟเฟอร์มาตรฐาน pH 4.00, 7.00, 10.00
# - สร้างสมการ direct-use: pH = slope_m * mV + intercept_b
#   (slope_m มีหน่วย pH/mV, intercept_b มีหน่วย pH)
# - ตามสมการ Nernst: E = E0 - (2.303RT/nF) * pH
# - ที่ 25°C: slope ทฤษฎี = -59.16 mV/pH → slope_m ≈ -0.0169 pH/mV
#
# การสอบเทียบ 3 จุดช่วยตรวจสอบ linearity ของหัววัด
# 3-point calibration helps verify probe linearity
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff


class CalibratePHMode(BaseMode):
    """
    โหมดสอบเทียบเซ็นเซอร์ pH (pH Sensor Calibration Mode)

    ดำเนินการสอบเทียบ 3 จุดด้วยบัฟเฟอร์ pH 4.00, 7.00, 10.00
    Performs 3-point calibration with pH 4.00, 7.00, 10.00 buffers

    Attributes:
        ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
        temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor object)
        buffer_values (list): ค่า pH ของบัฟเฟอร์ (Buffer pH values)
        measured_voltages (list): แรงดันที่วัดได้ (Measured voltages)
    """

    # ค่าบัฟเฟอร์มาตรฐาน (Standard buffer values)
    BUFFER_PH_VALUES = [4.00, 7.00, 10.00]

    # ระยะเวลารอให้ค่าคงที่ (Stabilization time in ms)
    # pH probe ต้องการ 10-20 วินาทีจึงจะเสถียร (pH probe needs 10-20s to stabilize)
    STABILIZATION_TIME_MS = 10000

    def __init__(self, display, colors, ph_sensor, temp_sensor=None, buzzer=None):
        """
        สร้างโหมดสอบเทียบ pH (Create pH calibration mode)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
            temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor object)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object)
        """
        super().__init__(display, colors, "Calibrate pH Sensor")

        self.ph_sensor = ph_sensor
        self.temp_sensor = temp_sensor
        self.buzzer = buzzer

        # ข้อมูลการสอบเทียบ (Calibration data)
        self.buffer_values = self.BUFFER_PH_VALUES.copy()
        self.measured_voltages = []
        self.measured_temperatures = []

        # สถานะการสอบเทียบ (Calibration state)
        self.current_step = 0
        self.total_steps = len(self.buffer_values)
        self.state = 'waiting'  # 'waiting', 'measuring', 'done'

        # ผลลัพธ์ (Results): pH = slope_m * mV + intercept_b
        self.slope = 0.0       # slope_m (pH/mV)
        self.intercept = 0.0   # intercept_b (pH)
        self.r_squared = 0.0   # R-squared (unitless)

    def on_enter(self):
        """
        เริ่มต้นการสอบเทียบ (Start calibration)
        """
        super().on_enter()

        # รีเซ็ตข้อมูล (Reset data)
        self.measured_voltages = []
        self.measured_temperatures = []
        self.current_step = 0
        self.state = 'waiting'

        # แสดงหน้าจอเริ่มต้น (Display initial screen)
        self._show_calibration_screen()

    def update(self):
        """
        อัปเดตสถานะการสอบเทียบ (Update calibration state)
        """
        if self.state == 'waiting':
            self._handle_waiting_state()
        elif self.state == 'measuring':
            self._handle_measuring_state()
        elif self.state == 'done':
            self._handle_done_state()

    def on_exit(self):
        """
        ออกจากโหมดสอบเทียบ (Exit calibration mode)
        """
        super().on_exit()

    # ==========================================================================
    # State Handlers
    # ==========================================================================

    def _handle_waiting_state(self):
        """
        จัดการสถานะรอผู้ใช้ (Handle waiting state)
        """
        # ตรวจสอบปุ่ม SELECT เพื่อเริ่มวัด (Check SELECT to start measuring)
        if self.check_button('select'):
            self._beep()
            self.state = 'measuring'
            self._start_measurement()

    def _handle_measuring_state(self):
        """
        จัดการสถานะกำลังวัด (Handle measuring state)
        """
        # กระบวนการวัดจะเสร็จสิ้นใน _start_measurement()
        # Measurement process completes in _start_measurement()
        pass

    def _handle_done_state(self):
        """
        จัดการสถานะเสร็จสิ้น (Handle done state)
        """
        # รอการกดปุ่มเพื่อดำเนินการต่อ (Wait for button to continue)
        if self.check_button('select'):
            self._beep()
            # บันทึกข้อมูล (Save data)
            self._save_calibration()
            self.set_complete()

    # ==========================================================================
    # Calibration Methods
    # ==========================================================================

    def _show_calibration_screen(self):
        """
        แสดงหน้าจอสอบเทียบ (Display calibration screen)
        """
        self.display.clear()
        self.display.draw_header(self.name)

        # แสดงขั้นตอน (Display step)
        step_text = f"Step {self.current_step + 1}/{self.total_steps}"
        self.display.draw_text(20, 40, step_text, self.colors.CYAN)

        # แสดงค่าบัฟเฟอร์ (Display buffer value)
        buffer_ph = self.buffer_values[self.current_step]
        self.display.draw_text(20, 70, f"Buffer pH: {buffer_ph:.2f}", self.colors.WHITE)

        # แสดงคำแนะนำ (Display instruction)
        self.display.draw_text(20, 100, "Immerse probe in buffer", self.colors.TEXT_INFO)
        self.display.draw_text(20, 125, "Wait for stable reading", self.colors.TEXT_INFO)

        # แสดงสถานะ (Display status)
        self.display.draw_status_bar("Press SELECT when ready", self.colors.TEXT_INFO)

    def _start_measurement(self):
        """
        เริ่มการวัดค่า (Start measurement)
        """
        buffer_ph = self.buffer_values[self.current_step]

        # แสดงการนับถอยหลัง (Display countdown)
        self.display.fill_rect(0, 150, self.display.width, 40, self.colors.BLACK)
        self.display.draw_text(20, 155, "Measuring...", self.colors.YELLOW)

        countdown_sec = self.STABILIZATION_TIME_MS // 1000
        start_time = ticks_ms()

        # รอและแสดงค่าแรงดันแบบ real-time (Wait and show real-time voltage)
        while ticks_diff(ticks_ms(), start_time) < self.STABILIZATION_TIME_MS:
            # อ่านค่าแรงดัน (Read voltage)
            voltage = self._read_voltage()

            # อัปเดตหน้าจอ (Update display)
            remaining = countdown_sec - (ticks_diff(ticks_ms(), start_time) // 1000)
            self.display.fill_rect(150, 155, 150, 24, self.colors.BLACK)
            self.display.draw_text(150, 155, f"{remaining}s", self.colors.YELLOW)

            self.display.fill_rect(20, 180, 200, 24, self.colors.BLACK)
            self.display.draw_text(20, 180, f"Voltage: {voltage:.1f} mV", self.colors.TEXT_WARNING)

            sleep_ms(100)

        # วัดค่าสุดท้าย (Final measurement)
        final_voltage = self._read_voltage_averaged()
        temperature = self._read_temperature()

        # บันทึกค่า (Record values)
        self.measured_voltages.append(final_voltage)
        self.measured_temperatures.append(temperature)

        # แสดงผลการวัด (Display measurement result)
        self._beep()
        self.display.fill_rect(0, 150, self.display.width, 70, self.colors.BLACK)
        self.display.draw_text(20, 155, f"pH {buffer_ph:.2f} Recorded!", self.colors.GREEN)
        self.display.draw_text(20, 180, f"Voltage: {final_voltage:.1f} mV", self.colors.TEXT_WARNING)
        self.display.draw_text(20, 205, f"Temp: {temperature:.1f} C", self.colors.CYAN)

        sleep_ms(2000)

        # ไปขั้นตอนถัดไป (Go to next step)
        self.current_step += 1

        if self.current_step >= self.total_steps:
            # สอบเทียบเสร็จสิ้น - คำนวณสมการ (Calibration complete - calculate equation)
            self._calculate_calibration()
            self._show_results()
            self.state = 'done'
        else:
            # แสดงขั้นตอนถัดไป (Show next step)
            self.state = 'waiting'
            self._show_calibration_screen()

    def _read_voltage(self):
        """
        อ่านค่าแรงดันไฟฟ้า (Read voltage)

        Returns:
            float: แรงดันใน mV (Voltage in mV)
        """
        if self.ph_sensor:
            return self.ph_sensor.read_voltage()
        return 0.0

    def _read_voltage_averaged(self, samples=10):
        """
        อ่านค่าแรงดันเฉลี่ย (Read averaged voltage)

        Args:
            samples (int): จำนวนตัวอย่าง (Number of samples)

        Returns:
            float: แรงดันเฉลี่ยใน mV (Averaged voltage in mV)
        """
        if self.ph_sensor:
            return self.ph_sensor.read_voltage_averaged(samples)

        # Fallback: อ่านค่าเดียว (Read single value)
        return self._read_voltage()

    def _read_temperature(self):
        """
        อ่านค่าอุณหภูมิ (Read temperature)

        Returns:
            float: อุณหภูมิในเซลเซียส (Temperature in Celsius)
        """
        if self.temp_sensor:
            try:
                return self.temp_sensor.read_temperature()
            except:
                pass
        return 25.0  # ค่าเริ่มต้น (Default value)

    def _calculate_calibration(self):
        """
        คำนวณสมการสอบเทียบ (Calculate calibration equation)

        ใช้ Linear Regression: pH = slope_m * mV + intercept_b
        Uses Linear Regression: pH = slope_m * mV + intercept_b (direct-use form)
        """
        x = self.measured_voltages  # Voltage (mV)
        y = self.buffer_values      # pH

        n = len(x)
        if n < 2:
            print("ข้อผิดพลาด: ข้อมูลไม่เพียงพอ (Error: Insufficient data)")
            return

        # คำนวณค่าเฉลี่ย (Calculate means)
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # คำนวณ Covariance และ Variance (Calculate covariance and variance)
        covariance = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y)) / n
        variance_x = sum((xi - x_mean) ** 2 for xi in x) / n

        # คำนวณ Slope และ Intercept (Calculate slope and intercept)
        if variance_x != 0:
            self.slope = covariance / variance_x
            self.intercept = y_mean - (self.slope * x_mean)
        else:
            self.slope = 0
            self.intercept = y_mean

        # คำนวณ R-squared (Calculate R-squared)
        y_pred = [self.slope * xi + self.intercept for xi in x]
        ss_residual = sum((yi - ypi) ** 2 for yi, ypi in zip(y, y_pred))
        ss_total = sum((yi - y_mean) ** 2 for yi in y)

        if ss_total != 0:
            self.r_squared = 1 - (ss_residual / ss_total)
        else:
            self.r_squared = 0

        print(f"Calibration: pH = {self.slope:.6f} * mV + {self.intercept:.4f}")
        print(f"  (slope_m = {self.slope:.6f} pH/mV, intercept_b = {self.intercept:.4f} pH)")
        print(f"R-squared: {self.r_squared:.6f}")

    def _show_results(self):
        """
        แสดงผลลัพธ์การสอบเทียบ (Display calibration results)
        """
        self.display.clear()
        self.display.draw_header("Calibration Results")

        y = 40

        # แสดงสมการ (Display equation: pH = slope_m * mV + intercept_b)
        self.display.draw_text(20, y, "pH = slope_m*mV + intercept_b", self.colors.WHITE)
        y += 25
        self.display.draw_text(20, y, f"m={self.slope:.6f} b={self.intercept:.4f}", self.colors.YELLOW)
        y += 30

        # แสดงค่า R-squared (Display R-squared)
        r2_color = self.colors.GREEN if self.r_squared >= 0.99 else self.colors.RED
        self.display.draw_text(20, y, f"R2: {self.r_squared:.6f}", r2_color)
        y += 30

        # แสดงจุดสอบเทียบ (Display calibration points)
        self.display.draw_text(20, y, "Calibration Points:", self.colors.WHITE)
        y += 22
        for i, (ph, voltage) in enumerate(zip(self.buffer_values, self.measured_voltages)):
            self.display.draw_text(30, y, f"pH {ph:.1f}: {voltage:.1f} mV", self.colors.CYAN)
            y += 20

        # แสดงสถานะ (Display status)
        # ใช้เกณฑ์ R2 >= 0.99 ตามมาตรฐานการสอบเทียบ pH
        # Use R2 >= 0.99 threshold per pH calibration standard
        valid = self.r_squared >= 0.99
        status = "Press SELECT to save" if valid else "Warning: R^2 < 0.99"
        status_color = self.colors.TEXT_INFO if valid else self.colors.RED
        self.display.draw_status_bar(status, status_color)

        # ตั้งค่าผลลัพธ์ (Set results)
        self.set_results(
            slope_m=self.slope,
            intercept_b=self.intercept,
            r_squared=self.r_squared,
            points=list(zip(self.buffer_values, self.measured_voltages)),
            temperatures=self.measured_temperatures,
            calibration_type='ph'
        )

    def _save_calibration(self):
        """
        บันทึกข้อมูลการสอบเทียบในรูปแบบ CSV
        Save calibration data in CSV format

        รูปแบบไฟล์ (File format):
            slope_m,intercept_b,r_squared,cal_temp
            -0.016911,34.9800,0.999500,25.20
        """
        try:
            # อ่านอุณหภูมิขณะสอบเทียบ (Read calibration temperature)
            cal_temp = 25.0
            if self.measured_temperatures:
                cal_temp = sum(self.measured_temperatures) / len(self.measured_temperatures)

            # บันทึกลงไฟล์ CSV (Save to CSV file)
            with open('data_calibrate.txt', 'w') as f:
                # บรรทัดที่ 1: header (Line 1: header)
                f.write("slope_m,intercept_b,r_squared,cal_temp\n")
                # บรรทัดที่ 2: ข้อมูล (Line 2: data)
                f.write(f"{self.slope:.6f},{self.intercept:.4f},{self.r_squared:.6f},{cal_temp:.2f}\n")

            print(f"บันทึกการสอบเทียบเรียบร้อย (Calibration saved)")
            print(f"  slope_m={self.slope:.6f} pH/mV, intercept_b={self.intercept:.4f} pH")
            print(f"  R2={self.r_squared:.6f}, Temp={cal_temp:.2f} C")

            # อัปเดตเซ็นเซอร์ pH (Update pH sensor)
            if self.ph_sensor:
                self.ph_sensor.set_calibration(self.slope, self.intercept)

        except Exception as e:
            print(f"ข้อผิดพลาดการบันทึก (Save error): {e}")

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
    print("CalibratePHMode Module")
    print("======================")
    print("This mode performs 3-point pH sensor calibration.")
    print("")
    print("Buffer values: pH 4.00, 7.00, 10.00")
    print("")
    print("Process:")
    print("1. Immerse probe in pH 4.00 buffer, press SELECT")
    print("2. Immerse probe in pH 7.00 buffer, press SELECT")
    print("3. Immerse probe in pH 10.00 buffer, press SELECT")
    print("4. View results and save calibration")

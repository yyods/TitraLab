# ==============================================================================
# mode_test_ph.py - โหมดทดสอบเซ็นเซอร์ pH (pH Sensor Test Mode)
# ==============================================================================
# โหมดนี้แสดงค่า pH แบบ real-time เพื่อตรวจสอบการทำงานของเซ็นเซอร์
# This mode displays real-time pH values to verify sensor operation
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การอ่านค่าเซ็นเซอร์แบบ continuous (Continuous sensor reading)
# 2. เข้าใจการแปลงค่า ADC เป็น pH ด้วยสมการสอบเทียบ
# 3. ฝึกการออกแบบ UI แบบ real-time update
#
# การแสดงผล (Display):
# - ค่า pH ปัจจุบัน (Current pH value)
# - แรงดันไฟฟ้า (Voltage in mV)
# - อุณหภูมิ (Temperature)
# - กราฟแนวโน้ม (Trend indicator)
# ==============================================================================

from .base_mode import BaseMode
from time import sleep_ms, ticks_ms, ticks_diff


class TestPHMode(BaseMode):
    """
    โหมดทดสอบเซ็นเซอร์ pH (pH Sensor Test Mode)

    แสดงค่า pH แบบ real-time และข้อมูลประกอบ
    Displays real-time pH values and related information

    Attributes:
        ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
        temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor object)
        update_interval (int): ระยะเวลาอัปเดต ms (Update interval)
    """

    # ระยะเวลาอัปเดตค่า (Update interval in ms)
    UPDATE_INTERVAL_MS = 500

    def __init__(self, display, colors, ph_sensor, temp_sensor=None, buzzer=None):
        """
        สร้างโหมดทดสอบ pH (Create pH test mode)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
            temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor object)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object)
        """
        super().__init__(display, colors, "pH Sensor Test")

        self.ph_sensor = ph_sensor
        self.temp_sensor = temp_sensor
        self.buzzer = buzzer

        # ตัวแปรการอัปเดต (Update variables)
        self._last_update_time = 0
        self._last_ph = 0.0
        self._last_voltage = 0.0
        self._last_temp = 25.0

        # ประวัติค่า pH สำหรับแนวโน้ม (pH history for trend)
        self._ph_history = []
        self._max_history = 10

    def on_enter(self):
        """
        เริ่มต้นโหมดทดสอบ (Start test mode)
        """
        super().on_enter()

        # รีเซ็ตประวัติ (Reset history)
        self._ph_history = []
        self._last_update_time = 0

        # แสดงหน้าจอ (Display screen)
        self._render_screen()

    def update(self):
        """
        อัปเดตค่า pH (Update pH value)
        """
        current_time = ticks_ms()

        # อัปเดตตามระยะเวลาที่กำหนด (Update at specified interval)
        if ticks_diff(current_time, self._last_update_time) >= self.UPDATE_INTERVAL_MS:
            self._last_update_time = current_time
            self._update_values()

        # ตรวจสอบปุ่มเพื่อออก (Check button to exit)
        if self.check_button('select'):
            self._beep()
            self.set_complete()

    def on_exit(self):
        """
        ออกจากโหมดทดสอบ (Exit test mode)
        """
        super().on_exit()

    # ==========================================================================
    # Display Methods
    # ==========================================================================

    def _render_screen(self):
        """
        วาดหน้าจอทั้งหมด (Render complete screen)
        """
        self.display.clear()

        # วาดส่วนหัว (Draw header)
        self.display.draw_header(self.name)

        # วาด labels (Draw labels)
        self.display.draw_text(20, 45, "pH Value:", self.colors.WHITE)
        self.display.draw_text(20, 90, "Voltage:", self.colors.WHITE)
        self.display.draw_text(20, 120, "Temperature:", self.colors.WHITE)
        self.display.draw_text(20, 150, "Trend:", self.colors.WHITE)

        # วาดเส้นแบ่ง (Draw divider)
        self.display.draw_hline(10, 180, 300, self.colors.WHITE)

        # แสดงคำแนะนำ (Display instructions)
        self.display.draw_text(20, 190, "Calibration:", self.colors.WHITE)

        # แสดงสถานะ (Display status)
        self.display.draw_status_bar("Press SELECT to exit", self.colors.TEXT_INFO)

    def _update_values(self):
        """
        อ่านและอัปเดตค่า (Read and update values)
        """
        # อ่านค่าจากเซ็นเซอร์ (Read from sensors)
        voltage = self._read_voltage()
        ph = self._read_ph()
        temperature = self._read_temperature()

        # บันทึกประวัติ (Record history)
        self._ph_history.append(ph)
        if len(self._ph_history) > self._max_history:
            self._ph_history.pop(0)

        # คำนวณแนวโน้ม (Calculate trend)
        trend = self._calculate_trend()

        # อัปเดตหน้าจอ (Update display)
        self._update_ph_display(ph)
        self._update_voltage_display(voltage)
        self._update_temperature_display(temperature)
        self._update_trend_display(trend)
        self._update_calibration_display()

        # บันทึกค่า (Store values)
        self._last_ph = ph
        self._last_voltage = voltage
        self._last_temp = temperature

    def _update_ph_display(self, ph):
        """
        อัปเดตการแสดงผลค่า pH (Update pH display)

        Args:
            ph (float): ค่า pH (pH value)
        """
        # ล้างพื้นที่เดิม (Clear previous area)
        self.display.fill_rect(140, 40, 180, 40, self.colors.BLACK)

        # กำหนดสีตามค่า pH (Set color based on pH)
        if ph < 4:
            color = self.colors.RED
        elif ph < 6:
            color = self.colors.ORANGE
        elif ph < 8:
            color = self.colors.GREEN
        elif ph < 10:
            color = self.colors.CYAN
        else:
            color = self.colors.BLUE

        # แสดงค่า pH ขนาดใหญ่ (Display large pH value)
        ph_text = f"{ph:.2f}"
        self.display.draw_text(140, 45, ph_text, color)

    def _update_voltage_display(self, voltage):
        """
        อัปเดตการแสดงผลแรงดัน (Update voltage display)

        Args:
            voltage (float): แรงดัน mV (Voltage in mV)
        """
        self.display.fill_rect(140, 90, 150, 24, self.colors.BLACK)
        self.display.draw_text(140, 90, f"{voltage:.1f} mV", self.colors.YELLOW)

    def _update_temperature_display(self, temperature):
        """
        อัปเดตการแสดงผลอุณหภูมิ (Update temperature display)

        Args:
            temperature (float): อุณหภูมิ (Temperature)
        """
        self.display.fill_rect(160, 120, 120, 24, self.colors.BLACK)
        self.display.draw_text(160, 120, f"{temperature:.1f} C", self.colors.CYAN)

    def _update_trend_display(self, trend):
        """
        อัปเดตการแสดงผลแนวโน้ม (Update trend display)

        Args:
            trend (str): แนวโน้ม 'up', 'down', 'stable'
        """
        self.display.fill_rect(100, 150, 200, 24, self.colors.BLACK)

        if trend == 'up':
            symbol = "^ Rising"
            color = self.colors.GREEN
        elif trend == 'down':
            symbol = "v Falling"
            color = self.colors.RED
        else:
            symbol = "- Stable"
            color = self.colors.WHITE

        self.display.draw_text(100, 150, symbol, color)

    def _update_calibration_display(self):
        """
        อัปเดตการแสดงผลการสอบเทียบ (Update calibration display)
        """
        self.display.fill_rect(140, 190, 180, 24, self.colors.BLACK)

        if self.ph_sensor:
            slope = getattr(self.ph_sensor, 'slope', 0)
            intercept = getattr(self.ph_sensor, 'intercept', 0)

            if slope != 0:
                self.display.draw_text(140, 190, "Loaded", self.colors.GREEN)
            else:
                self.display.draw_text(140, 190, "Not calibrated", self.colors.RED)
        else:
            self.display.draw_text(140, 190, "No sensor", self.colors.RED)

    # ==========================================================================
    # Sensor Reading Methods
    # ==========================================================================

    def _read_voltage(self):
        """
        อ่านค่าแรงดันไฟฟ้า (Read voltage)

        Returns:
            float: แรงดันใน mV (Voltage in mV)
        """
        if self.ph_sensor:
            try:
                return self.ph_sensor.read_voltage()
            except:
                pass
        return 0.0

    def _read_ph(self):
        """
        อ่านค่า pH (Read pH value)

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
    # Analysis Methods
    # ==========================================================================

    def _calculate_trend(self):
        """
        คำนวณแนวโน้มจากประวัติ (Calculate trend from history)

        Returns:
            str: 'up', 'down', หรือ 'stable'
        """
        if len(self._ph_history) < 3:
            return 'stable'

        # คำนวณความต่างเฉลี่ย (Calculate average difference)
        recent = self._ph_history[-3:]
        diff = recent[-1] - recent[0]

        if diff > 0.1:
            return 'up'
        elif diff < -0.1:
            return 'down'
        else:
            return 'stable'

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
    print("TestPHMode Module")
    print("=================")
    print("This mode displays real-time pH sensor readings.")
    print("")
    print("Display information:")
    print("- Current pH value")
    print("- Raw voltage (mV)")
    print("- Temperature")
    print("- Trend indicator (rising/falling/stable)")
    print("- Calibration status")
    print("")
    print("Press SELECT button to exit the mode.")

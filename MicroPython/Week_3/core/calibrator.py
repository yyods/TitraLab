# ==============================================================================
# calibrator.py - คลาสสอบเทียบสำหรับ TitraLab
# (Calibrator Class for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการการสอบเทียบเซ็นเซอร์ pH และอัตราการไหลของปั๊ม
# This module handles pH sensor and pump flow rate calibration
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจขั้นตอนการสอบเทียบ pH sensor แบบ 3 จุด
#   2. เรียนรู้การคำนวณอัตราการไหลจากเวลาและปริมาตร
#   3. ประยุกต์ใช้ linear regression สำหรับสร้างสมการสอบเทียบ
#
# การสอบเทียบ pH (pH Calibration):
#   ใช้บัฟเฟอร์มาตรฐาน 3 จุด: pH 4.00, 7.00, 10.00
#   วัดแรงดัน (mV) ที่แต่ละจุด แล้วสร้างสมการเส้นตรง
#   pH = slope_m * mV + intercept_b (x=mV, y=pH)
#
# การสอบเทียบอัตราการไหล (Flow Rate Calibration):
#   สูบของเหลวปริมาตรที่ทราบ (เช่น 5 mL) แล้ววัดเวลา
#   flow_rate = volume / time (mL/s)
#
# ==============================================================================

from time import ticks_us, ticks_diff, sleep_ms

# นำเข้าคลาสที่จำเป็น (Import required classes)
try:
    from .math_utils import LinearRegression
    from .data_manager import DataManager
except ImportError:
    from math_utils import LinearRegression
    from data_manager import DataManager

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import (
        PH_BUFFER_VALUES, R_SQUARED_THRESHOLD,
        DEFAULT_FLOW_RATE_ML_PER_SEC, FLOW_RATE_CALIBRATION_VOLUME_ML
    )
except ImportError:
    PH_BUFFER_VALUES = [4.00, 7.00, 10.00]
    R_SQUARED_THRESHOLD = 0.99
    DEFAULT_FLOW_RATE_ML_PER_SEC = 0.2772
    FLOW_RATE_CALIBRATION_VOLUME_ML = 5.00


class Calibrator:
    """
    คลาสสอบเทียบเซ็นเซอร์และปั๊ม (Calibrator class for sensors and pump)

    คุณสมบัติหลัก (Main Features):
        - สอบเทียบ pH sensor แบบ 3 จุด
        - สอบเทียบอัตราการไหลของปั๊ม
        - ตรวจสอบคุณภาพการสอบเทียบด้วย R-squared
        - บันทึกและโหลดข้อมูลสอบเทียบ

    หลักการสอบเทียบ pH (pH Calibration Principle):
        1. แช่หัววัดในบัฟเฟอร์ pH 4.00 -> วัดแรงดัน mV1
        2. แช่หัววัดในบัฟเฟอร์ pH 7.00 -> วัดแรงดัน mV2
        3. แช่หัววัดในบัฟเฟอร์ pH 10.00 -> วัดแรงดัน mV3
        4. ใช้ linear regression หาสมการ pH = slope_m * mV + intercept_b
        5. ตรวจสอบ R-squared >= 0.99

    หลักการสอบเทียบอัตราการไหล (Flow Rate Calibration Principle):
        1. เตรียมภาชนะสำหรับรับของเหลว
        2. สูบของเหลวจนได้ปริมาตรเป้าหมาย (เช่น 5 mL)
        3. วัดเวลาที่ใช้สูบ
        4. คำนวณ flow_rate = volume / time

    ตัวอย่างการใช้งาน (Usage Example):
        >>> cal = Calibrator()
        >>> # สอบเทียบ pH (buffer pH, voltage mV)
        >>> cal.add_ph_point(4.00, 2068.0)   # buffer 4.00, 2068 mV
        >>> cal.add_ph_point(7.00, 1650.0)   # buffer 7.00, 1650 mV
        >>> cal.add_ph_point(10.00, 1290.0)  # buffer 10.00, 1290 mV
        >>> result = cal.calculate_ph_calibration()
        >>> # สอบเทียบ flow rate
        >>> flow_result = cal.calibrate_flow_rate(5.0, 18.05)  # 5mL in 18.05s
    """

    def __init__(self, ph_sensor=None, pump=None, display=None,
                 buttons=None, buzzer=None, data_manager=None):
        """
        สร้าง Calibrator object (Create Calibrator object)

        Args:
            ph_sensor: PHSensor object สำหรับอ่านค่า pH
            pump: Pump object สำหรับควบคุมปั๊ม
            display: DisplayManager สำหรับแสดงผล
            buttons: ButtonManager สำหรับรับ input
            buzzer: Buzzer สำหรับเสียงเตือน
            data_manager (DataManager): DataManager สำหรับบันทึก/โหลดข้อมูล
                                        ถ้าไม่ระบุจะสร้างใหม่
        """
        # Hardware references
        self._ph_sensor = ph_sensor
        self._pump = pump
        self._display = display
        self._buttons = buttons
        self._buzzer = buzzer

        # DataManager สำหรับ persistence
        self._data_manager = data_manager if data_manager else DataManager()

        # LinearRegression สำหรับการคำนวณ pH
        self._ph_regression = LinearRegression()

        # ข้อมูลสอบเทียบ pH (pH calibration data)
        self._ph_points = []  # [(buffer_ph, voltage), ...]
        self._ph_slope = None
        self._ph_intercept = None
        self._ph_r_squared = None
        self._ph_calibrated = False

        # ข้อมูลสอบเทียบ flow rate (Flow rate calibration data)
        self._flow_rate = DEFAULT_FLOW_RATE_ML_PER_SEC
        self._flow_calibrated = False

        # ค่าบัฟเฟอร์มาตรฐาน (Standard buffer values)
        self._buffer_values = PH_BUFFER_VALUES.copy()

        # เกณฑ์ R-squared (R-squared threshold)
        self._r_squared_threshold = R_SQUARED_THRESHOLD

        print("Calibrator พร้อมใช้งาน (Calibrator ready)")
        print(f"  Buffer values: {self._buffer_values}")
        print(f"  R-squared threshold: {self._r_squared_threshold}")

    # ===========================================================================
    # pH Calibration
    # ===========================================================================

    @property
    def ph_slope(self):
        """ค่า slope ของสมการ pH (pH equation slope)"""
        return self._ph_slope

    @property
    def ph_intercept(self):
        """ค่า intercept ของสมการ pH (pH equation intercept)"""
        return self._ph_intercept

    @property
    def ph_r_squared(self):
        """ค่า R-squared ของการสอบเทียบ pH (pH calibration R-squared)"""
        return self._ph_r_squared

    @property
    def is_ph_calibrated(self):
        """ตรวจสอบว่าสอบเทียบ pH แล้วหรือยัง (Check if pH is calibrated)"""
        return self._ph_calibrated

    @property
    def flow_rate(self):
        """อัตราการไหลปัจจุบัน (Current flow rate in mL/s)"""
        return self._flow_rate

    @property
    def is_flow_calibrated(self):
        """ตรวจสอบว่าสอบเทียบ flow rate แล้วหรือยัง"""
        return self._flow_calibrated

    def clear_ph_points(self):
        """
        ล้างจุดสอบเทียบ pH ทั้งหมด (Clear all pH calibration points)
        """
        self._ph_points = []
        self._ph_regression.clear()
        self._ph_slope = None
        self._ph_intercept = None
        self._ph_r_squared = None
        self._ph_calibrated = False
        print("ล้างจุดสอบเทียบ pH แล้ว (pH calibration points cleared)")

    def add_ph_point(self, buffer_ph, voltage_mv):
        """
        เพิ่มจุดสอบเทียบ pH (Add pH calibration point)

        Args:
            buffer_ph (float): ค่า pH ของสารละลายบัฟเฟอร์ (4.00, 7.00, หรือ 10.00)
            voltage_mv (float): แรงดันที่วัดได้ (mV)

        Returns:
            bool: True ถ้าเพิ่มสำเร็จ
        """
        # ตรวจสอบค่า buffer (Validate buffer value)
        if buffer_ph not in self._buffer_values:
            print(f"คำเตือน: ค่า pH {buffer_ph} ไม่ใช่ค่าบัฟเฟอร์มาตรฐาน "
                  f"(Warning: pH {buffer_ph} is not a standard buffer value)")

        # เพิ่มจุด (Add point): x=mV, y=pH
        self._ph_points.append((buffer_ph, voltage_mv))
        self._ph_regression.add_point(voltage_mv, buffer_ph)  # x=mV, y=pH

        print(f"เพิ่มจุดสอบเทียบ: pH {buffer_ph:.2f} = {voltage_mv:.1f} mV "
              f"(Added calibration point)")
        print(f"  รวม {len(self._ph_points)} จุด (Total {len(self._ph_points)} points)")

        return True

    def get_ph_points(self):
        """
        รับจุดสอบเทียบ pH ทั้งหมด (Get all pH calibration points)

        Returns:
            list: รายการ (buffer_ph, voltage)
        """
        return self._ph_points.copy()

    def calculate_ph_calibration(self):
        """
        คำนวณสมการสอบเทียบ pH (Calculate pH calibration equation)

        Returns:
            dict: ผลการคำนวณ containing:
                - slope_m (float): ค่า slope (pH/mV)
                - intercept_b (float): ค่า intercept (pH)
                - r_squared (float): ค่า R-squared
                - is_valid (bool): ผ่านเกณฑ์หรือไม่
                - message (str): ข้อความผลลัพธ์

        Raises:
            ValueError: ถ้ามีจุดน้อยกว่า 2 จุด
        """
        if len(self._ph_points) < 2:
            raise ValueError(
                f"ต้องมีอย่างน้อย 2 จุดสำหรับสอบเทียบ แต่มี {len(self._ph_points)} จุด "
                f"(Need at least 2 points, got {len(self._ph_points)})"
            )

        print("\n=== คำนวณสมการสอบเทียบ pH (Calculating pH Calibration) ===")

        # คำนวณ linear regression
        self._ph_slope, self._ph_intercept, self._ph_r_squared = \
            self._ph_regression.calculate()

        # ตรวจสอบคุณภาพ (Validate quality)
        is_valid = self._ph_r_squared >= self._r_squared_threshold

        if is_valid:
            self._ph_calibrated = True
            message = f"การสอบเทียบถูกต้อง R2={self._ph_r_squared*100:.2f}% (Calibration valid)"
        else:
            message = (f"การสอบเทียบไม่ผ่านเกณฑ์ R2={self._ph_r_squared*100:.2f}% "
                      f"(ต้องการ >= {self._r_squared_threshold*100:.0f}%) "
                      f"(Calibration below threshold)")

        # แสดงผล (Display results)
        print(f"\nผลการคำนวณ (Results):")
        print(f"  สมการ: pH = {self._ph_slope:.6f} * mV + {self._ph_intercept:.4f}")
        print(f"  (slope_m = {self._ph_slope:.6f} pH/mV, intercept_b = {self._ph_intercept:.4f} pH)")
        print(f"  R-squared: {self._ph_r_squared*100:.2f}%")
        print(f"  สถานะ: {message}")

        return {
            'slope': self._ph_slope,
            'intercept': self._ph_intercept,
            'r_squared': self._ph_r_squared,
            'is_valid': is_valid,
            'message': message
        }

    def save_ph_calibration(self, cal_temp=25.0):
        """
        บันทึกข้อมูลสอบเทียบ pH ในรูปแบบ CSV
        Save pH calibration data in CSV format

        Args:
            cal_temp (float): อุณหภูมิขณะสอบเทียบ (calibration temperature, C)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        if not self._ph_calibrated:
            print("ยังไม่ได้สอบเทียบ pH กรุณาสอบเทียบก่อน "
                  "(pH not calibrated, please calibrate first)")
            return False

        return self._data_manager.save_ph_calibration(
            self._ph_slope,
            self._ph_intercept,
            self._ph_r_squared,
            cal_temp
        )

    def load_ph_calibration(self):
        """
        โหลดข้อมูลสอบเทียบ pH (Load pH calibration data)

        Returns:
            tuple: (slope_m, intercept_b, r_squared, cal_temp) หรือ (None, None, None, None)
                slope_m: pH/mV, intercept_b: pH, r_squared: unitless, cal_temp: Celsius
        """
        slope_m, intercept_b, r_squared, cal_temp = self._data_manager.load_ph_calibration()

        if slope_m is not None:
            self._ph_slope = slope_m
            self._ph_intercept = intercept_b
            self._ph_r_squared = r_squared
            self._ph_calibrated = True

        return slope_m, intercept_b, r_squared, cal_temp

    # ===========================================================================
    # Flow Rate Calibration
    # ===========================================================================

    def calibrate_flow_rate(self, volume_ml, time_seconds):
        """
        สอบเทียบอัตราการไหล (Calibrate flow rate)

        การคำนวณ (Calculation):
            flow_rate = volume / time (mL/s)

        Args:
            volume_ml (float): ปริมาตรที่สูบได้ (volume pumped in mL)
            time_seconds (float): เวลาที่ใช้สูบ (time in seconds)

        Returns:
            dict: ผลการสอบเทียบ containing:
                - flow_rate (float): อัตราการไหล mL/s
                - volume (float): ปริมาตร mL
                - time (float): เวลา s
        """
        if time_seconds <= 0:
            raise ValueError("เวลาต้องมากกว่า 0 (Time must be > 0)")

        if volume_ml <= 0:
            raise ValueError("ปริมาตรต้องมากกว่า 0 (Volume must be > 0)")

        # คำนวณอัตราการไหล (Calculate flow rate)
        self._flow_rate = volume_ml / time_seconds
        self._flow_calibrated = True

        print("\n=== สอบเทียบอัตราการไหล (Flow Rate Calibration) ===")
        print(f"ปริมาตร: {volume_ml:.2f} mL")
        print(f"เวลา: {time_seconds:.2f} s")
        print(f"อัตราการไหล: {self._flow_rate:.4f} mL/s")

        return {
            'flow_rate': self._flow_rate,
            'volume': volume_ml,
            'time': time_seconds
        }

    def calibrate_flow_rate_with_timing(self, volume_ml, pump, duty_percent=100):
        """
        สอบเทียบอัตราการไหลโดยวัดเวลาอัตโนมัติ
        Calibrate flow rate with automatic timing

        Args:
            volume_ml (float): ปริมาตรเป้าหมาย (target volume in mL)
            pump (Pump): Pump object สำหรับสูบ
            duty_percent (float): Duty cycle สำหรับสอบเทียบ

        Returns:
            dict: ผลการสอบเทียบ

        หมายเหตุ (Note):
            ฟังก์ชันนี้ต้องใช้กับ Pump class
            และต้องยืนยันปริมาตรด้วยตาหลังจากสูบเสร็จ
        """
        print("\n=== สอบเทียบอัตราการไหลพร้อมจับเวลา ===")
        print(f"เป้าหมาย: {volume_ml:.2f} mL ที่ {duty_percent}% duty")
        print("กรุณาเตรียมภาชนะรับของเหลว...")

        # ใช้อัตราการไหลเริ่มต้นเพื่อประมาณเวลา
        estimated_time = volume_ml / DEFAULT_FLOW_RATE_ML_PER_SEC
        print(f"เวลาประมาณ: {estimated_time:.1f} วินาที")

        # เริ่มสูบและจับเวลา (Start pump and time)
        start_time = ticks_us()
        pump.start(duty_percent)

        # รอจนครบเวลาที่ประมาณ
        # (ในการใช้งานจริง ควรใช้ปุ่มกดหรือ sensor เพื่อหยุด)
        sleep_ms(int(estimated_time * 1000))

        pump.stop()
        end_time = ticks_us()

        # คำนวณเวลาจริง
        actual_time = ticks_diff(end_time, start_time) / 1_000_000

        print(f"\nผู้ใช้ต้องยืนยันปริมาตรจริงที่สูบได้")
        print(f"เวลาที่ใช้: {actual_time:.2f} วินาที")

        # คำนวณอัตราการไหล
        return self.calibrate_flow_rate(volume_ml, actual_time)

    def save_flow_rate(self):
        """
        บันทึกข้อมูลอัตราการไหล (Save flow rate data)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        if not self._flow_calibrated:
            print("ยังไม่ได้สอบเทียบ flow rate กรุณาสอบเทียบก่อน "
                  "(Flow rate not calibrated, please calibrate first)")
            return False

        return self._data_manager.save_flow_rate(self._flow_rate)

    def load_flow_rate(self):
        """
        โหลดข้อมูลอัตราการไหล (Load flow rate data)

        Returns:
            tuple: (flow_rate, date) หรือ (None, None)
        """
        flow_rate, date = self._data_manager.load_flow_rate()

        if flow_rate is not None:
            self._flow_rate = flow_rate
            self._flow_calibrated = True

        return flow_rate, date

    # ===========================================================================
    # Utility Methods
    # ===========================================================================

    def predict_ph(self, voltage_mv):
        """
        ทำนายค่า pH จากแรงดัน (Predict pH from voltage)

        สมการ: pH = slope_m * mV + intercept_b
        Equation: pH = slope_m * mV + intercept_b

        Args:
            voltage_mv (float): แรงดันเป็น mV (voltage in mV)

        Returns:
            float: ค่า pH ที่ทำนาย
        """
        if not self._ph_calibrated:
            raise RuntimeError(
                "ยังไม่ได้สอบเทียบ pH กรุณาสอบเทียบก่อน "
                "(pH not calibrated, please calibrate first)"
            )

        return self._ph_slope * voltage_mv + self._ph_intercept

    def get_calibration_summary(self):
        """
        รับสรุปข้อมูลสอบเทียบทั้งหมด (Get calibration summary)

        Returns:
            dict: สรุปข้อมูลสอบเทียบ
        """
        return {
            'ph': {
                'calibrated': self._ph_calibrated,
                'slope': self._ph_slope,
                'intercept': self._ph_intercept,
                'r_squared': self._ph_r_squared,
                'points': len(self._ph_points)
            },
            'flow_rate': {
                'calibrated': self._flow_calibrated,
                'value': self._flow_rate
            }
        }

    def print_calibration_summary(self):
        """
        แสดงสรุปข้อมูลสอบเทียบ (Print calibration summary)
        """
        print("\n=== สรุปการสอบเทียบ (Calibration Summary) ===")

        # pH calibration
        if self._ph_calibrated:
            print(f"[OK] pH Calibration:")
            print(f"     สมการ: pH = {self._ph_slope:.6f} * mV + {self._ph_intercept:.4f}")
            print(f"     R-squared: {self._ph_r_squared*100:.2f}%")
            print(f"     จุดสอบเทียบ: {len(self._ph_points)}")
        else:
            print("[--] pH Calibration: ยังไม่ได้สอบเทียบ")

        # Flow rate
        if self._flow_calibrated:
            print(f"[OK] Flow Rate: {self._flow_rate:.4f} mL/s")
        else:
            print(f"[--] Flow Rate: ใช้ค่าเริ่มต้น {self._flow_rate:.4f} mL/s")

        print()

    # ===========================================================================
    # Interactive Methods (ใช้โดย main.py)
    # ===========================================================================

    def calibrate_ph(self):
        """
        สอบเทียบ pH แบบ interactive (Interactive pH calibration)

        ขั้นตอน:
        1. วัดค่า mV ใน buffer pH 4.00
        2. วัดค่า mV ใน buffer pH 7.00
        3. วัดค่า mV ใน buffer pH 10.00
        4. คำนวณ linear regression
        5. บันทึกผลลัพธ์
        """
        from time import sleep_ms

        if not self._ph_sensor:
            print("Error: No pH sensor configured")
            return False

        # ล้างข้อมูลเก่า (Clear old data)
        self.clear_ph_points()

        print("\n" + "=" * 50)
        print("เริ่มสอบเทียบ pH (Starting pH Calibration)")
        print("=" * 50)

        if self._display:
            self._display.clear()
            self._display.draw_header("pH Calibration")

        # สอบเทียบแต่ละจุด (Calibrate each point)
        for i, buffer_ph in enumerate(self._buffer_values):
            print(f"\n[{i+1}/3] จุ่มหัววัดใน buffer pH {buffer_ph:.2f}")
            print("กดปุ่ม 1 เมื่อพร้อม, ปุ่ม 3 ยกเลิก (BTN1: Ready, BTN3: Cancel)")

            if self._display:
                self._display.show_message(
                    f"Buffer pH {buffer_ph:.2f}",
                    "BTN1:OK BTN3:Cancel"
                )

            # รอกดปุ่ม (Wait for button)
            if self._buttons:
                while True:
                    if self._buttons.is_pressed(1):
                        sleep_ms(200)  # Debounce
                        break
                    if self._buttons.is_pressed(3):
                        # ยกเลิกการสอบเทียบ (Cancel calibration)
                        print("\n[CANCELLED] ยกเลิกการสอบเทียบ (Calibration cancelled)")
                        if self._display:
                            self._display.show_message("Cancelled", "Returning to menu")
                        if self._buzzer:
                            self._buzzer.error_sound()
                        sleep_ms(1500)
                        return False
                    sleep_ms(50)

            # อ่านค่าเฉลี่ย (Read averaged value)
            print("กำลังอ่านค่า... (Reading...)")
            try:
                if self._display:
                    print("  DEBUG: Calling show_message...")
                    self._display.show_message("Reading...", "Please wait 10s")
                    print("  DEBUG: show_message OK")

                print("  DEBUG: Calling read_voltage_averaged...")
                voltage = self._ph_sensor.read_voltage_averaged(num_samples=20)
                print(f"  DEBUG: voltage = {voltage}")

                print("  DEBUG: Calling add_ph_point...")
                self.add_ph_point(buffer_ph, voltage)
                print(f"Buffer {buffer_ph:.2f}: {voltage:.2f} mV")
            except Exception as e:
                print(f"  DEBUG ERROR: {type(e).__name__}: {e}")
                raise

            if self._buzzer:
                self._buzzer.beep()

        # คำนวณและบันทึก (Calculate and save)
        result = self.calculate_ph_calibration()

        if result['is_valid']:
            self.save_ph_calibration()
            print("\n[SUCCESS] สอบเทียบ pH สำเร็จ!")
            if self._display:
                self._display.show_success("Calibration OK!")
        else:
            print(f"\n[FAILED] {result['message']}")
            if self._display:
                self._display.show_error("Calibration Failed")

        sleep_ms(2000)
        return result['is_valid']

    def test_ph_sensor(self):
        """
        ทดสอบเซ็นเซอร์ pH แบบ real-time (Real-time pH sensor test)

        แสดงค่า pH และ mV แบบต่อเนื่องจนกว่าจะกดปุ่มออก
        """
        from time import sleep_ms

        if not self._ph_sensor:
            print("Error: No pH sensor configured")
            return

        print("\n" + "=" * 50)
        print("ทดสอบเซ็นเซอร์ pH (pH Sensor Test)")
        print("กดปุ่ม 3 เพื่อออก (Press BTN3 to exit)")
        print("=" * 50)

        if self._display:
            self._display.clear()
            self._display.draw_header("pH Sensor Test")

        while True:
            # อ่านค่า (Read values)
            voltage = self._ph_sensor.read_voltage_averaged(num_samples=5)
            ph_value = self._ph_sensor.read_ph()

            print(f"pH: {ph_value:.2f}  |  mV: {voltage:.1f}")

            if self._display:
                self._display.clear()
                self._display.draw_header("pH Sensor Test")
                self._display.draw_text(20, 60, f"pH: {ph_value:.2f}", 0x07E0)
                self._display.draw_text(20, 100, f"mV: {voltage:.1f}", 0xFFFF)
                self._display.draw_status_bar("BTN3: Exit")

            # ตรวจสอบปุ่มออก (Check exit button - BTN3)
            if self._buttons and self._buttons.is_pressed(3):
                break

            sleep_ms(500)

        print("ออกจากการทดสอบ (Exiting test)")

    def calibrate_flow_rate_interactive(self):
        """
        สอบเทียบอัตราการไหลแบบ interactive (Interactive flow rate calibration)

        ขั้นตอน:
        1. เปิดปั๊มจนกว่าจะกดปุ่มหยุด
        2. ผู้ใช้วัดปริมาตรจริงที่สูบได้
        3. คำนวณ flow rate จากปริมาตร/เวลา
        4. บันทึกผลลัพธ์
        """
        from time import sleep_ms, ticks_ms, ticks_diff

        if not self._pump:
            print("Error: No pump configured")
            return False

        print("\n" + "=" * 50)
        print("สอบเทียบอัตราการไหล (Flow Rate Calibration)")
        print("=" * 50)

        if self._display:
            self._display.clear()
            self._display.draw_header("Flow Rate Cal")

        # แสดงคำแนะนำ (Show instructions)
        print("\nคำแนะนำ:")
        print("1. เตรียมกระบอกตวงสำหรับวัดปริมาตร")
        print("2. กดปุ่ม 1 เพื่อเริ่มปั๊ม, ปุ่ม 3 ยกเลิก")
        print("3. กดปุ่ม 1 อีกครั้งเพื่อหยุด")
        print("4. วัดปริมาตรที่ได้และป้อนค่า")
        print("\nInstructions:")
        print("1. Prepare measuring cylinder")
        print("2. BTN1: Start pump, BTN3: Cancel")
        print("3. Press BTN1 again to stop")
        print("4. Measure and enter the volume")

        if self._display:
            self._display.show_message(
                "Flow Cal",
                "BTN1:Start BTN3:Cancel"
            )

        # รอกดปุ่มเริ่ม (Wait for start button)
        if self._buttons:
            while True:
                if self._buttons.is_pressed(1):
                    sleep_ms(200)  # Debounce
                    break
                if self._buttons.is_pressed(3):
                    # ยกเลิก (Cancel)
                    print("\n[CANCELLED] ยกเลิกการสอบเทียบ (Calibration cancelled)")
                    if self._display:
                        self._display.show_message("Cancelled", "Returning to menu")
                    if self._buzzer:
                        self._buzzer.error_sound()
                    sleep_ms(1500)
                    return False
                sleep_ms(50)

        # เริ่มจับเวลาและเปิดปั๊ม (Start timing and pump)
        if self._buzzer:
            self._buzzer.beep()

        print("\nกำลังสูบ... กดปุ่ม 1 หยุด, ปุ่ม 3 ยกเลิก (Pumping... BTN1:Stop BTN3:Cancel)")

        if self._display:
            self._display.show_message(
                "Pumping...",
                "BTN1:Stop BTN3:Cancel"
            )

        start_time = ticks_ms()
        self._pump.start(100)  # Full speed

        # รอกดปุ่มหยุด (Wait for stop button)
        cancelled = False
        if self._buttons:
            while True:
                if self._buttons.is_pressed(1):
                    sleep_ms(200)  # Debounce
                    break
                if self._buttons.is_pressed(3):
                    # ยกเลิก - หยุดปั๊มก่อน (Cancel - stop pump first)
                    cancelled = True
                    break
                sleep_ms(50)

        self._pump.stop()
        end_time = ticks_ms()

        if cancelled:
            print("\n[CANCELLED] ยกเลิกการสอบเทียบ (Calibration cancelled)")
            if self._display:
                self._display.show_message("Cancelled", "Pump stopped")
            if self._buzzer:
                self._buzzer.error_sound()
            sleep_ms(1500)
            return False

        if self._buzzer:
            self._buzzer.beep_beep()

        # คำนวณเวลา (Calculate time)
        elapsed_time_s = ticks_diff(end_time, start_time) / 1000.0

        print(f"\nเวลาที่สูบ: {elapsed_time_s:.2f} วินาที")
        print(f"(Pump time: {elapsed_time_s:.2f} seconds)")

        # ใช้ปริมาตรมาตรฐาน 5 mL (Use standard volume)
        # ผู้ใช้ต้องปรับให้ได้ 5 mL
        target_volume = FLOW_RATE_CALIBRATION_VOLUME_ML

        if self._display:
            self._display.show_message(
                f"Time: {elapsed_time_s:.1f}s",
                f"Volume: {target_volume:.1f} mL"
            )

        print(f"\nใช้ปริมาตรเป้าหมาย: {target_volume:.2f} mL")
        print("กรุณาตรวจสอบว่าปริมาตรจริงใกล้เคียง")
        print(f"(Target volume: {target_volume:.2f} mL)")
        print("Please verify actual volume is similar")

        # คำนวณและบันทึก (Calculate and save)
        result = self.calibrate_flow_rate(target_volume, elapsed_time_s)
        self.save_flow_rate()

        print(f"\n[SUCCESS] Flow rate: {result['flow_rate']:.4f} mL/s")

        if self._display:
            self._display.show_success(
                f"FR: {result['flow_rate']:.4f}"
            )

        sleep_ms(2000)
        return True

    def test_flow_rate(self):
        """
        ทดสอบอัตราการไหลของปั๊ม (Test pump flow rate)

        จ่ายปริมาตร 5 mL โดยคำนวณเวลาจาก flow rate ที่สอบเทียบได้
        Dispense 5 mL with time calculated from calibrated flow rate

        ขั้นตอน (Steps):
        1. แสดงปริมาตรเป้าหมาย (5 mL) และเวลาที่คำนวณ
        2. รอกดปุ่ม 1 เพื่อเริ่ม (Wait for BTN1 to start)
        3. เปิดปั๊มตามเวลาที่คำนวณ (Run pump for calculated time)
        4. กด BTN3 เพื่อยกเลิกได้ (Press BTN3 to cancel)
        """
        from time import sleep_ms, ticks_ms, ticks_diff

        if not self._pump:
            print("Error: No pump configured")
            return

        # ปริมาตรเป้าหมาย (Target volume)
        target_volume_ml = FLOW_RATE_CALIBRATION_VOLUME_ML  # 5.00 mL

        # คำนวณเวลาจาก flow rate (Calculate time from flow rate)
        # time (s) = volume (mL) / flow_rate (mL/s)
        calculated_time_s = target_volume_ml / self._flow_rate
        calculated_time_ms = int(calculated_time_s * 1000)

        print("\n" + "=" * 50)
        print("ทดสอบอัตราการไหล (Flow Rate Test)")
        print("=" * 50)
        print(f"ปริมาตรเป้าหมาย: {target_volume_ml:.2f} mL (Target volume)")
        print(f"อัตราการไหล: {self._flow_rate:.4f} mL/s (Flow rate)")
        print(f"เวลาที่คำนวณ: {calculated_time_s:.2f} s (Calculated time)")
        print("-" * 50)
        print("กดปุ่ม 1 เริ่ม, ปุ่ม 3 ยกเลิก (BTN1:Start BTN3:Cancel)")

        if self._display:
            self._display.clear()
            self._display.draw_header("Flow Rate Test")
            # แสดงข้อมูลทดสอบ (Show test info)
            self._display.draw_text(10, 50, f"Target: {target_volume_ml:.1f} mL", 0xFFFF)
            self._display.draw_text(10, 80, f"Flow: {self._flow_rate:.4f} mL/s", 0xFFFF)
            self._display.draw_text(10, 110, f"Time: {calculated_time_s:.2f} s", 0x07E0)  # Green
            self._display.draw_status_bar("BTN1:Start BTN3:Cancel")

        # รอกดปุ่ม 1 เริ่ม หรือปุ่ม 3 ยกเลิก (Wait for BTN1 to start or BTN3 to cancel)
        if self._buttons:
            while True:
                if self._buttons.is_pressed(1):
                    sleep_ms(200)  # Debounce
                    break
                if self._buttons.is_pressed(3):
                    # ยกเลิก (Cancel)
                    print("\n[CANCELLED] ยกเลิกการทดสอบ (Test cancelled)")
                    if self._display:
                        self._display.show_message("Cancelled", "Returning to menu")
                    if self._buzzer:
                        self._buzzer.error_sound()
                    sleep_ms(1500)
                    return
                sleep_ms(50)

        # เริ่มทดสอบ (Start test)
        print(f"\nกำลังจ่าย {target_volume_ml:.1f} mL ({calculated_time_s:.2f} s)...")
        print("(Dispensing... BTN3 to cancel)")

        if self._display:
            self._display.show_message(
                f"Dispensing...",
                f"{target_volume_ml:.1f}mL / {calculated_time_s:.1f}s"
            )

        if self._buzzer:
            self._buzzer.beep()

        self._pump.start(100)  # Full speed

        # รอตามเวลาที่คำนวณ พร้อมตรวจสอบ BTN3
        # Wait for calculated time with BTN3 check
        start_time = ticks_ms()
        cancelled = False

        while ticks_diff(ticks_ms(), start_time) < calculated_time_ms:
            if self._buttons and self._buttons.is_pressed(3):
                cancelled = True
                break
            sleep_ms(50)

        self._pump.stop()

        if cancelled:
            elapsed_s = ticks_diff(ticks_ms(), start_time) / 1000.0
            dispensed_ml = self._flow_rate * elapsed_s
            print(f"\n[CANCELLED] หยุดที่ {elapsed_s:.2f} s (จ่ายไป ~{dispensed_ml:.2f} mL)")
            print(f"(Stopped at {elapsed_s:.2f}s, dispensed ~{dispensed_ml:.2f} mL)")
            if self._display:
                self._display.show_message("Cancelled", f"~{dispensed_ml:.2f} mL dispensed")
            if self._buzzer:
                self._buzzer.error_sound()
            sleep_ms(1500)
            return

        if self._buzzer:
            self._buzzer.beep_beep()

        print(f"\n[COMPLETE] จ่ายเสร็จ: {target_volume_ml:.2f} mL")
        print(f"กรุณาตรวจสอบปริมาตรจริงในกระบอกตวง")
        print(f"(Please verify actual volume in measuring cylinder)")

        if self._display:
            self._display.show_success(f"Done: {target_volume_ml:.1f} mL")

        sleep_ms(2000)

    def purge_tubing(self):
        """
        ล้างท่อปั๊มแบบ manual (Manual purge pump tubing)

        ขั้นตอน (Steps):
        1. รอกดปุ่ม 1 เพื่อเริ่ม (Wait for BTN1 to start)
        2. ปั๊มทำงานต่อเนื่อง (Pump runs continuously)
        3. กดปุ่ม 1 อีกครั้งเพื่อหยุด (Press BTN1 again to stop)

        หมายเหตุ: BTN3 ยกเลิกก่อนเริ่ม (BTN3 cancels before starting)
        """
        from time import sleep_ms, ticks_ms, ticks_diff

        if not self._pump:
            print("Error: No pump configured")
            return

        print("\n" + "=" * 50)
        print("ล้างท่อปั๊ม (Purge Tubing)")
        print("=" * 50)
        print("กดปุ่ม 1 เริ่ม, ปุ่ม 3 ยกเลิก (BTN1:Start BTN3:Cancel)")

        if self._display:
            self._display.clear()
            self._display.draw_header("Purge Tubing")
            self._display.draw_text(10, 60, "Manual Purge Mode", 0xFFFF)
            self._display.draw_text(10, 100, "BTN1: Start pump", 0x07E0)  # Green
            self._display.draw_status_bar("BTN1:Start BTN3:Cancel")

        # รอกดปุ่ม 1 เริ่ม หรือปุ่ม 3 ยกเลิก (Wait for BTN1 to start or BTN3 to cancel)
        if self._buttons:
            while True:
                if self._buttons.is_pressed(1):
                    sleep_ms(200)  # Debounce
                    break
                if self._buttons.is_pressed(3):
                    # ยกเลิก (Cancel)
                    print("\n[CANCELLED] ยกเลิก (Cancelled)")
                    if self._display:
                        self._display.show_message("Cancelled", "Returning to menu")
                    if self._buzzer:
                        self._buzzer.error_sound()
                    sleep_ms(1500)
                    return
                sleep_ms(50)

        # เริ่มปั๊ม (Start pump)
        print("\nกำลังล้างท่อ... กดปุ่ม 1 หยุด (Purging... BTN1:Stop)")

        if self._display:
            self._display.clear()
            self._display.draw_header("Purge Tubing")
            self._display.draw_text(10, 60, "Purging...", 0x07E0)  # Green
            self._display.draw_text(10, 100, "Pump is running", 0xFFFF)
            self._display.draw_status_bar("BTN1: Stop pump")

        if self._buzzer:
            self._buzzer.beep()

        self._pump.start(100)  # Full speed
        start_time = ticks_ms()

        # รอกดปุ่ม 1 หยุด (Wait for BTN1 to stop)
        if self._buttons:
            while True:
                if self._buttons.is_pressed(1):
                    sleep_ms(200)  # Debounce
                    break
                sleep_ms(50)

        self._pump.stop()
        elapsed_s = ticks_diff(ticks_ms(), start_time) / 1000.0

        if self._buzzer:
            self._buzzer.beep_beep()

        # แสดงเวลาที่ใช้ (Show elapsed time)
        print(f"\n[COMPLETE] ล้างท่อเสร็จ: {elapsed_s:.1f} วินาที")
        print(f"(Purge complete: {elapsed_s:.1f} seconds)")

        if self._display:
            self._display.show_success(f"Done: {elapsed_s:.1f}s")

        sleep_ms(1500)

    def __repr__(self):
        """แสดงข้อมูล Calibrator"""
        ph_status = "OK" if self._ph_calibrated else "--"
        flow_status = "OK" if self._flow_calibrated else "--"
        return f"Calibrator(pH={ph_status}, flow={flow_status})"


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ Calibrator (Testing Calibrator)")
    print("=" * 50)

    # สร้าง Calibrator
    cal = Calibrator()

    # ======= ทดสอบสอบเทียบ pH =======
    print("\n" + "=" * 50)
    print("ทดสอบสอบเทียบ pH (Testing pH Calibration)")
    print("=" * 50)

    # เพิ่มจุดสอบเทียบ (ข้อมูลตัวอย่าง)
    # buffer_ph, voltage_mv (x=mV, y=pH for regression)
    cal.add_ph_point(4.00, 2068.0)   # Buffer pH 4.00 -> 2068 mV
    cal.add_ph_point(7.00, 1650.0)   # Buffer pH 7.00 -> 1650 mV
    cal.add_ph_point(10.00, 1290.0)  # Buffer pH 10.00 -> 1290 mV

    # คำนวณ
    result = cal.calculate_ph_calibration()

    # บันทึก
    if result['is_valid']:
        cal.save_ph_calibration()

    # ทดสอบทำนาย (mV -> pH)
    test_mv = 1850.0
    predicted_ph = cal.predict_ph(test_mv)
    print(f"\nทดสอบทำนาย: {test_mv:.1f} mV -> pH {predicted_ph:.2f}")

    # ======= ทดสอบสอบเทียบ Flow Rate =======
    print("\n" + "=" * 50)
    print("ทดสอบสอบเทียบ Flow Rate")
    print("=" * 50)

    # สอบเทียบ (ข้อมูลตัวอย่าง)
    flow_result = cal.calibrate_flow_rate(5.0, 18.05)

    # บันทึก
    cal.save_flow_rate()

    # แสดงสรุป
    cal.print_calibration_summary()

    print("\nเสร็จสิ้น (Done)")

# ==============================================================================
# calibrator.py - Calibrator Class for TitraLab
# ==============================================================================
# สอบเทียบ pH sensor และ flow rate ของปั๊ม
# Handles pH sensor and pump flow rate calibration
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
    """สอบเทียบ pH sensor และปั๊ม (Calibrator for pH sensor and pump)"""

    def __init__(self, ph_sensor=None, pump=None, display=None,
                 buttons=None, buzzer=None, data_manager=None):
        """สร้าง Calibrator (Create Calibrator)"""
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

    def save_flow_rate(self, calibration_data=None, stats=None, duty_percent=100):
        """
        บันทึกข้อมูลอัตราการไหล (Save flow rate data)

        Args:
            calibration_data (list): รายการ [(time, volume, flow_rate), ...] (optional)
            stats (dict): สถิติ {avg_flow_rate, std_dev, rsd_percent, count} (optional)
            duty_percent (int): Duty cycle ที่ใช้สอบเทียบ (default 100%)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        if not self._flow_calibrated:
            print("ยังไม่ได้สอบเทียบ flow rate กรุณาสอบเทียบก่อน "
                  "(Flow rate not calibrated, please calibrate first)")
            return False

        return self._data_manager.save_flow_rate(
            self._flow_rate,
            calibration_data=calibration_data,
            stats=stats,
            duty_percent=duty_percent
        )

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

    def _get_volume_input(self, max_attempts=3):
        """
        รับค่าปริมาตรจากนิสิตพร้อมตรวจสอบความถูกต้อง
        Get volume input from student with validation

        Args:
            max_attempts (int): จำนวนครั้งสูงสุดที่ให้ลองใหม่ (default 3)

        Returns:
            float: Valid volume in mL, or None if cancelled/failed
        """
        for attempt in range(max_attempts):
            try:
                vol_str = input("พิมพ์ปริมาตรที่วัดได้ (Enter measured volume in mL): ").strip()

                # ตรวจสอบค่าว่าง (Check for empty input)
                if not vol_str:
                    print("ข้อผิดพลาด: กรุณาพิมพ์ค่า (Error: Please enter a value)")
                    continue

                # แปลงเป็นตัวเลข (Convert to number)
                volume = float(vol_str)

                # ตรวจสอบค่าติดลบหรือศูนย์ (Check for negative or zero)
                if volume <= 0:
                    print("ข้อผิดพลาด: ปริมาตรต้องมากกว่า 0 (Error: Volume must be > 0)")
                    continue

                # คำเตือนสำหรับค่าผิดปกติ (Warnings for unusual values)
                if volume > 50:
                    print(f"คำเตือน: ปริมาตร {volume:.1f} mL สูงผิดปกติ "
                          f"(Warning: {volume:.1f} mL is unusually high)")
                elif volume < 0.1:
                    print(f"คำเตือน: ปริมาตร {volume:.2f} mL ต่ำผิดปกติ "
                          f"(Warning: {volume:.2f} mL is unusually low)")

                return volume

            except ValueError:
                print("ข้อผิดพลาด: กรุณาพิมพ์ตัวเลข เช่น 5.2 "
                      "(Error: Enter a number, e.g. 5.2)")
                continue

        print("เกินจำนวนครั้งที่อนุญาต (Max attempts exceeded)")
        return None

    def _calculate_flow_stats(self, calibration_data):
        """
        คำนวณสถิติจากข้อมูลสอบเทียบ
        Calculate statistics from calibration data

        Args:
            calibration_data (list): รายการ [(time, volume, flow_rate), ...]

        Returns:
            dict: {avg_flow_rate, std_dev, rsd_percent, count} หรือ None
        """
        if not calibration_data:
            return None

        flow_rates = [d[2] for d in calibration_data]
        n = len(flow_rates)
        avg = sum(flow_rates) / n

        if n >= 2:
            # คำนวณ standard deviation (population)
            variance = sum((fr - avg) ** 2 for fr in flow_rates) / n
            std_dev = variance ** 0.5
            # คำนวณ RSD% (Relative Standard Deviation)
            rsd = (std_dev / avg) * 100 if avg > 0 else 0
        else:
            std_dev = 0
            rsd = 0

        return {
            'avg_flow_rate': avg,
            'std_dev': std_dev,
            'rsd_percent': rsd,
            'count': n
        }

    def _get_quality_message(self, rsd_percent):
        """
        รับข้อความแนะนำคุณภาพตามค่า RSD
        Get quality guidance message based on RSD value

        Args:
            rsd_percent (float): ค่า RSD%

        Returns:
            tuple: (quality_level, message_th, message_en)
        """
        if rsd_percent <= 3:
            return ('excellent',
                    'ดีมาก! พร้อมบันทึก',
                    'Excellent! Ready to save')
        elif rsd_percent <= 5:
            return ('good',
                    'ดี สามารถบันทึกหรือวัดเพิ่มได้',
                    'Good. Can save or add more measurements')
        else:
            return ('warning',
                    'คำเตือน: ค่าไม่สม่ำเสมอ ควรสอบเทียบใหม่',
                    'Warning: Values inconsistent. Consider recalibration')

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
        """สอบเทียบ flow rate แบบ interactive พร้อมการวัดหลายครั้ง"""
        from time import sleep_ms, ticks_ms, ticks_diff

        if not self._pump:
            print("Error: No pump configured")
            return False

        # ตัวแปรสำหรับการสอบเทียบ (Calibration variables)
        calibration_data = []  # รายการข้อมูลสอบเทียบ [(เวลา, ปริมาตร, flow_rate), ...]
        pump_running = False
        start_time = 0
        elapsed_time = 0
        duty_percent = 100  # Duty Cycle (%) - 100% = เต็มกำลัง (full power)

        # State machine states
        STATE_READY = 'ready'           # พร้อมเริ่ม (Ready to start pump)
        STATE_PUMPING = 'pumping'       # กำลังปั๊ม (Pump running)
        STATE_ENTER_VOL = 'enter_vol'   # รอป้อนปริมาตร (Waiting for volume input)
        STATE_STATS = 'stats'           # แสดงสถิติ (Showing statistics)
        current_state = STATE_READY

        # แสดงหน้าจอเริ่มต้น (Show initial screen)
        print("\n" + "=" * 50)
        print("Flow Rate Calibration (Multi-Measurement)")
        print("BTN1: Start/Stop Pump | BTN2: Record | BTN3: Save/Exit")
        print("=" * 50)

        if self._display:
            self._display.clear()
            self._display.draw_header("Flow Rate Cal")
            self._display.draw_text(10, 50, "Multi-Measurement Mode", 0xFFFF)
            self._display.draw_text(10, 80, "BTN1: Start/Stop Pump", 0x07E0)
            self._display.draw_text(10, 110, "BTN2: Record Volume", 0xFFE0)
            self._display.draw_text(10, 140, "BTN3: Save/Cancel", 0xF81F)
            self._display.draw_status_bar("Ready - BTN1:Start BTN3:Exit")

        # ==================================================================
        # Main calibration loop
        # ==================================================================
        try:
            while True:
                # ----------------------------------------
                # State: READY - พร้อมเริ่มปั๊ม
                # ----------------------------------------
                if current_state == STATE_READY:
                    if self._buttons:
                        # BTN1: เริ่มปั๊ม (Start pump)
                        if self._buttons.is_pressed(1):
                            sleep_ms(200)  # Debounce

                            # เริ่มปั๊มและจับเวลา (Start pump and timer)
                            duty_value = int((duty_percent / 100) * 1023)
                            start_time = ticks_ms()
                            self._pump.start(duty_percent)
                            pump_running = True
                            current_state = STATE_PUMPING

                            if self._buzzer:
                                self._buzzer.beep()

                            print("\nPUMP STARTED - BTN1:Stop BTN3:Cancel")

                            if self._display:
                                self._display.clear()
                                self._display.draw_header("Flow Rate Cal")
                                self._display.draw_text(10, 60, "PUMPING...", 0x07E0)
                                self._display.draw_text(10, 100, "BTN1: Stop pump", 0xFFFF)
                                self._display.draw_status_bar("BTN1:Stop BTN3:Cancel")

                        # BTN3: ยกเลิกและออก (Cancel and exit)
                        elif self._buttons.is_pressed(3):
                            sleep_ms(200)  # Debounce

                            if len(calibration_data) >= 1:
                                # มีข้อมูลแล้ว - ถามว่าจะบันทึกไหม (Has data - ask to save)
                                print("\n" + "=" * 50)
                                print("คุณมีข้อมูล {} ครั้ง".format(len(calibration_data)))
                                print("You have {} measurement(s)".format(len(calibration_data)))
                                print("กดปุ่ม 3 อีกครั้งเพื่อบันทึก หรือ ปุ่ม 1 เพื่อวัดต่อ")
                                print("Press BTN3 again to save, or BTN1 to continue measuring")
                                print("=" * 50)

                                current_state = STATE_STATS
                            else:
                                # ไม่มีข้อมูล - ยกเลิกเลย (No data - cancel)
                                print("\n[CANCELLED] ยกเลิกการสอบเทียบ (Calibration cancelled)")
                                if self._display:
                                    self._display.show_message("Cancelled", "Returning to menu")
                                if self._buzzer:
                                    self._buzzer.error_sound()
                                sleep_ms(1500)
                                return False

                # ----------------------------------------
                # State: PUMPING - กำลังปั๊ม
                # ----------------------------------------
                elif current_state == STATE_PUMPING:
                    if self._buttons:
                        # BTN1: หยุดปั๊ม (Stop pump)
                        if self._buttons.is_pressed(1):
                            sleep_ms(200)  # Debounce

                            # หยุดปั๊มและคำนวณเวลา (Stop pump and calculate time)
                            self._pump.stop()
                            end_time = ticks_ms()
                            pump_running = False
                            elapsed_time = ticks_diff(end_time, start_time) / 1000.0

                            if self._buzzer:
                                self._buzzer.beep_beep()

                            print(f"\nPUMP STOPPED - Time: {elapsed_time:.3f}s - BTN2:Enter volume")

                            current_state = STATE_ENTER_VOL

                            if self._display:
                                self._display.clear()
                                self._display.draw_header("Flow Rate Cal")
                                self._display.draw_text(10, 50, f"Time: {elapsed_time:.2f} s", 0x07E0)
                                self._display.draw_text(10, 90, "Read volume from", 0xFFFF)
                                self._display.draw_text(10, 110, "graduated cylinder", 0xFFFF)
                                self._display.draw_status_bar("BTN2:Enter Volume")

                        # BTN3: ยกเลิกระหว่างปั๊ม (Cancel during pumping)
                        elif self._buttons.is_pressed(3):
                            sleep_ms(200)  # Debounce

                            # หยุดปั๊มและยกเลิก (Stop pump and cancel)
                            self._pump.stop()
                            pump_running = False

                            print("\n[CANCELLED] ยกเลิก - ปั๊มหยุดแล้ว (Cancelled - Pump stopped)")

                            if self._buzzer:
                                self._buzzer.error_sound()

                            # กลับไปหน้า ready (Return to ready state)
                            current_state = STATE_READY

                            if self._display:
                                self._display.show_message("Cancelled", "BTN1:Restart BTN3:Exit")
                            sleep_ms(1000)

                # ----------------------------------------
                # State: ENTER_VOL - รอป้อนปริมาตร
                # ----------------------------------------
                elif current_state == STATE_ENTER_VOL:
                    if self._buttons:
                        # BTN2: บันทึกปริมาตร (Record volume)
                        if self._buttons.is_pressed(2):
                            sleep_ms(200)  # Debounce

                            # รับค่าปริมาตรจากผู้ใช้ (Get volume from user)
                            print(f"\nเวลาที่ปั๊มทำงาน (Elapsed time): {elapsed_time:.3f} s")
                            volume = self._get_volume_input()

                            if volume is not None:
                                # คำนวณ flow rate (Calculate flow rate)
                                flow_rate = volume / elapsed_time

                                # บันทึกข้อมูล (Record data)
                                calibration_data.append((elapsed_time, volume, flow_rate))

                                # คำนวณสถิติ (Calculate statistics)
                                stats = self._calculate_flow_stats(calibration_data)

                                # แสดงผล (Display results)
                                print(f"\n#{len(calibration_data)}: {elapsed_time:.3f}s, {volume:.2f}mL = {flow_rate:.4f} mL/s")
                                print(f"Avg: {stats['avg_flow_rate']:.4f} mL/s", end="")
                                if stats['count'] >= 2:
                                    quality, msg_th, msg_en = self._get_quality_message(stats['rsd_percent'])
                                    print(f", RSD: {stats['rsd_percent']:.2f}% ({quality})")
                                else:
                                    print("")
                                print("BTN1:More | BTN3:Save")

                                if self._buzzer:
                                    self._buzzer.beep()

                                # อัปเดต display
                                if self._display:
                                    self._display.clear()
                                    self._display.draw_header("Flow Rate Cal")
                                    self._display.draw_text(10, 45, f"#{len(calibration_data)}: {flow_rate:.4f} mL/s", 0x07E0)
                                    self._display.draw_text(10, 75, f"Avg: {stats['avg_flow_rate']:.4f} mL/s", 0xFFFF)
                                    if stats['count'] >= 2:
                                        rsd_color = 0x07E0 if stats['rsd_percent'] <= 5 else 0xF800
                                        self._display.draw_text(10, 105, f"RSD: {stats['rsd_percent']:.2f}%", rsd_color)
                                    self._display.draw_text(10, 135, f"Points: {stats['count']}", 0xFFFF)
                                    self._display.draw_status_bar("BTN1:More BTN3:Save")

                                current_state = STATE_STATS
                            else:
                                # ป้อนค่าไม่สำเร็จ - กลับไปหน้า ready
                                print("\nไม่สามารถบันทึกได้ กดปุ่ม 1 เพื่อลองใหม่")
                                print("Could not record. Press BTN1 to try again.")
                                current_state = STATE_READY

                        # BTN1: กลับไปหน้า ready (Return to ready)
                        elif self._buttons.is_pressed(1):
                            sleep_ms(200)  # Debounce
                            print("\nกลับไปหน้า ready (Returning to ready state)")
                            current_state = STATE_READY

                            if self._display:
                                self._display.clear()
                                self._display.draw_header("Flow Rate Cal")
                                n = len(calibration_data)
                                if n > 0:
                                    stats = self._calculate_flow_stats(calibration_data)
                                    self._display.draw_text(10, 60, f"Points: {n}", 0xFFFF)
                                    self._display.draw_text(10, 90, f"Avg: {stats['avg_flow_rate']:.4f}", 0x07E0)
                                self._display.draw_status_bar("BTN1:Start BTN3:Save")

                        # BTN3: บันทึกและออก (Save and exit)
                        elif self._buttons.is_pressed(3):
                            sleep_ms(200)  # Debounce
                            if len(calibration_data) >= 1:
                                current_state = STATE_STATS
                                # จะไปทำการบันทึกใน STATE_STATS
                            else:
                                print("\nต้องมีอย่างน้อย 1 การวัดก่อนบันทึก")
                                print("Need at least 1 measurement before saving")
                                current_state = STATE_READY

                # ----------------------------------------
                # State: STATS - แสดงสถิติและรอบันทึก
                # ----------------------------------------
                elif current_state == STATE_STATS:
                    if self._buttons:
                        # BTN1: วัดเพิ่ม (Add more measurements)
                        if self._buttons.is_pressed(1):
                            sleep_ms(200)  # Debounce
                            print("\nกลับไปวัดเพิ่ม (Adding more measurements)")
                            current_state = STATE_READY

                            if self._display:
                                self._display.clear()
                                self._display.draw_header("Flow Rate Cal")
                                n = len(calibration_data)
                                if n > 0:
                                    stats = self._calculate_flow_stats(calibration_data)
                                    self._display.draw_text(10, 60, f"Points: {n}", 0xFFFF)
                                    self._display.draw_text(10, 90, f"Avg: {stats['avg_flow_rate']:.4f}", 0x07E0)
                                self._display.draw_status_bar("BTN1:Start BTN3:Save")

                        # BTN3: บันทึกและออก (Save and exit)
                        elif self._buttons.is_pressed(3):
                            sleep_ms(200)  # Debounce

                            if len(calibration_data) >= 1:
                                # คำนวณสถิติสุดท้าย (Calculate final statistics)
                                stats = self._calculate_flow_stats(calibration_data)

                                # อัปเดต flow rate ใน calibrator และ pump
                                # Update flow rate in both calibrator and pump
                                self._flow_rate = stats['avg_flow_rate']
                                self._flow_calibrated = True
                                if self._pump:
                                    self._pump.flow_rate = self._flow_rate

                                # บันทึกลงไฟล์พร้อมข้อมูลการวัดทั้งหมด
                                success = self.save_flow_rate(
                                    calibration_data=calibration_data,
                                    stats=stats,
                                    duty_percent=duty_percent
                                )

                                if success:
                                    print(f"\nSAVED: {stats['avg_flow_rate']:.4f} mL/s ({stats['count']} pts)")

                                    if self._display:
                                        self._display.show_success(
                                            f"FR: {stats['avg_flow_rate']:.4f}"
                                        )

                                    if self._buzzer:
                                        self._buzzer.beep_beep()

                                    sleep_ms(2000)
                                    return True
                                else:
                                    print("\n[ERROR] ไม่สามารถบันทึกได้ (Could not save)")
                                    if self._display:
                                        self._display.show_error("Save Failed")
                                    if self._buzzer:
                                        self._buzzer.error_sound()
                                    sleep_ms(1500)
                                    return False
                            else:
                                print("\nต้องมีอย่างน้อย 1 การวัดก่อนบันทึก")
                                print("Need at least 1 measurement before saving")
                                current_state = STATE_READY

                sleep_ms(50)  # ลด CPU usage

        except KeyboardInterrupt:
            # Ctrl+C pressed - cleanup and exit
            if pump_running:
                self._pump.stop()
            print("\n\nหยุดโปรแกรม (Program stopped by user)")

            # แสดงสรุปข้อมูลที่เก็บได้ (Show data summary)
            if len(calibration_data) > 0:
                stats = self._calculate_flow_stats(calibration_data)
                print(f"\nสรุป: เก็บข้อมูล {len(calibration_data)} ครั้ง")
                print(f"Flow Rate เฉลี่ย: {stats['avg_flow_rate']:.4f} mL/s")

            return False

        finally:
            # ตรวจสอบว่าปั๊มปิดแล้ว (Ensure pump is stopped)
            if pump_running:
                self._pump.stop()

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

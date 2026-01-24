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

    def __init__(self, data_manager=None):
        """
        สร้าง Calibrator object (Create Calibrator object)

        Args:
            data_manager (DataManager): DataManager สำหรับบันทึก/โหลดข้อมูล
                                        ถ้าไม่ระบุจะสร้างใหม่
        """
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

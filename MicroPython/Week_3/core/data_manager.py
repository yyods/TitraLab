# ==============================================================================
# data_manager.py - คลาสจัดการข้อมูลสำหรับ TitraLab
# (Data Manager Class for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการการอ่าน-เขียนข้อมูลการสอบเทียบและการไทเทรต
# This module handles reading and writing calibration and titration data
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการจัดการไฟล์ใน MicroPython
#   2. เรียนรู้การ serialize/deserialize ข้อมูล
#   3. ประยุกต์ใช้ pattern สำหรับ data persistence
#
# ไฟล์ที่จัดการ (Managed Files):
#   - data_calibrate.txt: ข้อมูลสอบเทียบ pH (CSV: slope_m, intercept_b, r_squared, cal_temp)
#   - data_flowrate.txt: ข้อมูลอัตราการไหล (flow_rate in mL/s, 4 decimal places)
#
# ==============================================================================

import os

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import CALIBRATION_FILE, FLOWRATE_FILE
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    CALIBRATION_FILE = "data_calibrate.txt"
    FLOWRATE_FILE = "data_flowrate.txt"

# นำเข้า utime สำหรับวันที่ (Import utime for date)
try:
    import utime
    HAS_UTIME = True
except ImportError:
    import time as utime
    HAS_UTIME = False


class DataManager:
    """
    คลาสจัดการข้อมูลการสอบเทียบและการตั้งค่า
    (Data Manager class for calibration and settings)

    คุณสมบัติหลัก (Main Features):
        - บันทึกและโหลดข้อมูลสอบเทียบ pH
        - บันทึกและโหลดข้อมูลอัตราการไหล
        - จัดการวันที่บันทึกล่าสุด
        - รองรับการสำรองข้อมูล

    รูปแบบไฟล์ (File Format):
        data_calibrate.txt (CSV format):
            header: slope_m,intercept_b,r_squared,cal_temp
            data:   -0.016911,34.9800,0.999500,25.20

            slope_m = pH/mV, intercept_b = pH, r_squared = unitless, cal_temp = Celsius

        data_flowrate.txt:
            line 1: flow_rate (float, mL/s, 4 decimal places)

    ตัวอย่างการใช้งาน (Usage Example):
        >>> dm = DataManager()
        >>> dm.save_ph_calibration(slope_m=-0.016911, intercept_b=34.98,
        ...                        r_squared=0.9995, cal_temp=25.2)
        >>> slope_m, intercept_b, r_squared, cal_temp = dm.load_ph_calibration()
        >>> dm.save_flow_rate(0.2772)
        >>> flow_rate = dm.load_flow_rate()
    """

    def __init__(self, calibration_file=None, flowrate_file=None):
        """
        สร้าง DataManager object (Create DataManager object)

        Args:
            calibration_file (str): ชื่อไฟล์สอบเทียบ pH
            flowrate_file (str): ชื่อไฟล์อัตราการไหล
        """
        self._calibration_file = calibration_file or CALIBRATION_FILE
        self._flowrate_file = flowrate_file or FLOWRATE_FILE

        print(f"DataManager พร้อมใช้งาน (DataManager ready)")
        print(f"  pH calibration file: {self._calibration_file}")
        print(f"  Flow rate file: {self._flowrate_file}")

    def _get_current_date(self):
        """
        รับวันที่ปัจจุบันในรูปแบบ YYYY-MM-DD
        Get current date in YYYY-MM-DD format

        Returns:
            str: วันที่ เช่น "2024-03-15"
        """
        try:
            t = utime.localtime()
            return "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])
        except Exception:
            return "N/A"

    def _file_exists(self, filename):
        """
        ตรวจสอบว่าไฟล์มีอยู่หรือไม่ (Check if file exists)

        Args:
            filename (str): ชื่อไฟล์

        Returns:
            bool: True ถ้าไฟล์มีอยู่
        """
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

    # ===========================================================================
    # pH Calibration Data
    # ===========================================================================

    def save_ph_calibration(self, slope_m, intercept_b, r_squared=None, cal_temp=25.0):
        """
        บันทึกข้อมูลสอบเทียบ pH (Save pH calibration data)

        รูปแบบไฟล์ CSV (File format):
            slope_m,intercept_b,r_squared,cal_temp
            -0.016911,34.9800,0.999500,25.20

        Args:
            slope_m (float): slope_m ของสมการ (pH/mV)
            intercept_b (float): intercept_b ของสมการ (pH)
            r_squared (float): ค่า R-squared (optional, default 0.0)
            cal_temp (float): อุณหภูมิขณะสอบเทียบ (calibration temperature, C)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        try:
            if r_squared is None:
                r_squared = 0.0

            with open(self._calibration_file, "w") as f:
                # บรรทัดที่ 1: header (Line 1: header)
                f.write("slope_m,intercept_b,r_squared,cal_temp\n")
                # บรรทัดที่ 2: ข้อมูล (Line 2: data)
                # slope_m: 6 ทศนิยม, intercept_b: 4 ทศนิยม
                # slope_m: 6 decimals, intercept_b: 4 decimals
                f.write(f"{slope_m:.6f},{intercept_b:.4f},{r_squared:.6f},{cal_temp:.2f}\n")

            print(f"บันทึกข้อมูลสอบเทียบ pH สำเร็จ (pH calibration saved)")
            print(f"  slope_m={slope_m:.6f} pH/mV, intercept_b={intercept_b:.4f} pH")
            print(f"  R2={r_squared:.6f}, Temp={cal_temp:.2f} C")
            return True

        except Exception as e:
            print(f"ข้อผิดพลาดบันทึกข้อมูล (Error saving data): {e}")
            return False

    def load_ph_calibration(self):
        """
        โหลดข้อมูลสอบเทียบ pH (Load pH calibration data)

        รูปแบบไฟล์ CSV (File format):
            slope_m,intercept_b,r_squared,cal_temp
            -0.016911,34.9800,0.999500,25.20

        Returns:
            tuple: (slope_m, intercept_b, r_squared, cal_temp)
                   คืน (None, None, None, None) ถ้าไม่พบข้อมูล
        """
        if not self._file_exists(self._calibration_file):
            print(f"ไม่พบไฟล์สอบเทียบ: {self._calibration_file} "
                  f"(Calibration file not found)")
            return None, None, None, None

        try:
            with open(self._calibration_file, "r") as f:
                lines = f.readlines()

            # ข้ามบรรทัด header (Skip header line)
            # หาบรรทัดข้อมูล (Find data line)
            data_line = None
            for line in lines:
                stripped = line.strip()
                # ข้ามบรรทัดว่างและ header (Skip empty lines and header)
                if stripped and not stripped.startswith("slope_m"):
                    data_line = stripped
                    break

            if data_line is None:
                print("ไม่พบข้อมูลในไฟล์ (No data found in file)")
                return None, None, None, None

            # แยกค่าด้วยเครื่องหมายจุลภาค (Split by comma)
            parts = data_line.split(",")
            slope_m = float(parts[0])
            intercept_b = float(parts[1])
            r_squared = float(parts[2]) if len(parts) > 2 else 0.0
            cal_temp = float(parts[3]) if len(parts) > 3 else 25.0

            print(f"โหลดข้อมูลสอบเทียบ pH สำเร็จ (pH calibration loaded)")
            print(f"  slope_m={slope_m:.6f} pH/mV, intercept_b={intercept_b:.4f} pH")
            print(f"  R2={r_squared:.6f}, Temp={cal_temp:.2f} C")

            return slope_m, intercept_b, r_squared, cal_temp

        except Exception as e:
            print(f"ข้อผิดพลาดโหลดข้อมูล (Error loading data): {e}")
            return None, None, None, None

    def get_ph_calibration_info(self):
        """
        รับข้อมูลสรุปการสอบเทียบ pH
        Get pH calibration summary info

        Returns:
            dict: ข้อมูลสอบเทียบ หรือ None ถ้าไม่พบ
        """
        slope_m, intercept_b, r_squared, cal_temp = self.load_ph_calibration()
        if slope_m is not None:
            return {
                'slope_m': slope_m,
                'intercept_b': intercept_b,
                'r_squared': r_squared,
                'cal_temp': cal_temp
            }
        return None

    # ===========================================================================
    # Flow Rate Data
    # ===========================================================================

    def save_flow_rate(self, flow_rate, calibration_data=None, stats=None, duty_percent=100):
        """
        บันทึกข้อมูลอัตราการไหล (Save flow rate data)

        รองรับ 2 รูปแบบ (Supports 2 formats):
        1. Simple: flow_rate เพียงค่าเดียว (single flow_rate value)
        2. Extended: รวมข้อมูลการวัดแต่ละครั้งและสถิติ (with individual measurements and stats)

        Args:
            flow_rate (float): อัตราการไหลเฉลี่ย mL/s (average flow rate)
            calibration_data (list): รายการ [(time, volume, flow_rate), ...] (optional)
            stats (dict): สถิติ {avg_flow_rate, std_dev, rsd_percent, count} (optional)
            duty_percent (int): Duty cycle ที่ใช้สอบเทียบ (default 100%)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        try:
            current_date = self._get_current_date()

            with open(self._flowrate_file, "w") as f:
                # Header comments
                f.write("# TitraLab Pump Flow Rate Calibration Data\n")
                f.write("# ข้อมูลการสอบเทียบอัตราการไหลของปั๊ม\n")

                if calibration_data and len(calibration_data) > 0:
                    # Extended format: รวมข้อมูลการวัดแต่ละครั้ง
                    f.write(f"# จำนวนข้อมูล (Data points): {len(calibration_data)}\n")
                    f.write(f"# Duty Cycle: {duty_percent}%\n")
                    f.write(f"# Date: {current_date}\n")
                    f.write("#\n")
                    f.write("# รายละเอียดการวัดแต่ละครั้ง (Individual measurements):\n")
                    f.write("# Time(s), Volume(mL), FlowRate(mL/s)\n")
                    for i, (t, v, fr) in enumerate(calibration_data, 1):
                        f.write(f"# {i}: {t:.3f}, {v:.2f}, {fr:.4f}\n")
                    f.write("#\n")

                    # Statistics
                    if stats:
                        f.write(f"# Average: {stats['avg_flow_rate']:.4f} mL/s\n")
                        if stats['count'] >= 2:
                            f.write(f"# Std Dev: {stats['std_dev']:.4f} mL/s\n")
                            f.write(f"# RSD: {stats['rsd_percent']:.2f}%\n")
                    f.write("#\n")
                else:
                    # Simple format: ค่าเดียว (single value)
                    f.write(f"# Date: {current_date}\n")
                    f.write("#\n")

                # ค่า flow_rate หลักสำหรับใช้งาน (Main flow_rate value for use)
                f.write(f"flow_rate={flow_rate:.4f}\n")

            print(f"บันทึกข้อมูลอัตราการไหลสำเร็จ (Flow rate saved)")
            print(f"  flow_rate={flow_rate:.4f} mL/s")
            if calibration_data:
                print(f"  Data points: {len(calibration_data)}")
            if stats and stats['count'] >= 2:
                print(f"  RSD: {stats['rsd_percent']:.2f}%")
            print(f"  Date: {current_date}")
            return True

        except Exception as e:
            print(f"ข้อผิดพลาดบันทึกข้อมูล (Error saving data): {e}")
            return False

    def load_flow_rate(self):
        """
        โหลดข้อมูลอัตราการไหล (Load flow rate data)

        รองรับทั้งรูปแบบเก่าและใหม่ (Supports both old and new formats):
        - Old format: flow_rate value on first line
        - New format: flow_rate=value line

        Returns:
            tuple: (flow_rate, last_saved_date)
                   คืน (None, None) ถ้าไม่พบข้อมูล
        """
        if not self._file_exists(self._flowrate_file):
            print(f"ไม่พบไฟล์อัตราการไหล: {self._flowrate_file} "
                  f"(Flow rate file not found)")
            return None, None

        try:
            with open(self._flowrate_file, "r") as f:
                lines = f.readlines()

            flow_rate = None
            last_saved = None

            for line in lines:
                stripped = line.strip()

                # ข้ามบรรทัดว่าง (Skip empty lines)
                if not stripped:
                    continue

                # หา flow_rate=value (New format)
                if stripped.startswith("flow_rate="):
                    flow_rate = float(stripped.replace("flow_rate=", ""))

                # หาวันที่ (Find date)
                elif stripped.startswith("# Date:"):
                    last_saved = stripped.replace("# Date:", "").strip()

                # รองรับ format เก่า "Last saved:" (Support old format)
                elif stripped.startswith("Last saved:"):
                    last_saved = stripped.replace("Last saved:", "").strip()

                # รองรับ format เก่ามากๆ ที่มีตัวเลขบรรทัดแรก (Support very old format)
                elif flow_rate is None and not stripped.startswith("#"):
                    try:
                        flow_rate = float(stripped)
                    except ValueError:
                        pass

            if flow_rate is not None:
                print(f"โหลดข้อมูลอัตราการไหลสำเร็จ (Flow rate loaded)")
                print(f"  flow_rate={flow_rate:.4f} mL/s")
                print(f"  Date: {last_saved or 'N/A'}")
                return flow_rate, last_saved
            else:
                print("ไม่พบค่า flow_rate ในไฟล์ (No flow_rate found in file)")
                return None, None

        except Exception as e:
            print(f"ข้อผิดพลาดโหลดข้อมูล (Error loading data): {e}")
            return None, None

    def get_flow_rate_date(self):
        """
        รับเฉพาะวันที่สอบเทียบอัตราการไหลล่าสุด
        Get only the last flow rate calibration date

        Returns:
            str: วันที่สอบเทียบ หรือ "N/A"
        """
        _, date = self.load_flow_rate()
        return date or "N/A"

    # ===========================================================================
    # Utility Methods
    # ===========================================================================

    def has_ph_calibration(self):
        """
        ตรวจสอบว่ามีข้อมูลสอบเทียบ pH หรือไม่
        Check if pH calibration data exists

        Returns:
            bool: True ถ้ามีข้อมูล
        """
        return self._file_exists(self._calibration_file)

    def has_flow_rate(self):
        """
        ตรวจสอบว่ามีข้อมูลอัตราการไหลหรือไม่
        Check if flow rate data exists

        Returns:
            bool: True ถ้ามีข้อมูล
        """
        return self._file_exists(self._flowrate_file)

    def delete_ph_calibration(self):
        """
        ลบข้อมูลสอบเทียบ pH (Delete pH calibration data)

        Returns:
            bool: True ถ้าลบสำเร็จ
        """
        if not self._file_exists(self._calibration_file):
            print("ไม่พบไฟล์สอบเทียบ pH (pH calibration file not found)")
            return False

        try:
            os.remove(self._calibration_file)
            print(f"ลบไฟล์สอบเทียบ pH แล้ว (pH calibration deleted)")
            return True
        except Exception as e:
            print(f"ข้อผิดพลาดลบไฟล์ (Error deleting file): {e}")
            return False

    def delete_flow_rate(self):
        """
        ลบข้อมูลอัตราการไหล (Delete flow rate data)

        Returns:
            bool: True ถ้าลบสำเร็จ
        """
        if not self._file_exists(self._flowrate_file):
            print("ไม่พบไฟล์อัตราการไหล (Flow rate file not found)")
            return False

        try:
            os.remove(self._flowrate_file)
            print(f"ลบไฟล์อัตราการไหลแล้ว (Flow rate deleted)")
            return True
        except Exception as e:
            print(f"ข้อผิดพลาดลบไฟล์ (Error deleting file): {e}")
            return False

    def backup_calibration_data(self, backup_suffix="_backup"):
        """
        สำรองข้อมูลสอบเทียบทั้งหมด (Backup all calibration data)

        Args:
            backup_suffix (str): ส่วนต่อท้ายชื่อไฟล์สำรอง

        Returns:
            bool: True ถ้าสำรองสำเร็จ
        """
        success = True

        # สำรอง pH calibration
        if self._file_exists(self._calibration_file):
            try:
                backup_name = self._calibration_file.replace(".txt", f"{backup_suffix}.txt")
                with open(self._calibration_file, "r") as src:
                    content = src.read()
                with open(backup_name, "w") as dst:
                    dst.write(content)
                print(f"สำรอง pH calibration: {backup_name}")
            except Exception as e:
                print(f"ข้อผิดพลาดสำรอง pH calibration: {e}")
                success = False

        # สำรอง flow rate
        if self._file_exists(self._flowrate_file):
            try:
                backup_name = self._flowrate_file.replace(".txt", f"{backup_suffix}.txt")
                with open(self._flowrate_file, "r") as src:
                    content = src.read()
                with open(backup_name, "w") as dst:
                    dst.write(content)
                print(f"สำรอง flow rate: {backup_name}")
            except Exception as e:
                print(f"ข้อผิดพลาดสำรอง flow rate: {e}")
                success = False

        return success

    def get_all_calibration_status(self):
        """
        รับสถานะการสอบเทียบทั้งหมด (Get all calibration status)

        Returns:
            dict: สถานะการสอบเทียบ
        """
        # โหลดข้อมูล pH (4 ค่า: slope_m, intercept_b, r_squared, cal_temp)
        ph_slope_m, ph_intercept_b, ph_r_squared, ph_cal_temp = self.load_ph_calibration()

        # โหลดข้อมูล flow rate
        flow_rate, flow_date = self.load_flow_rate()

        return {
            'ph_calibrated': ph_slope_m is not None,
            'ph_slope_m': ph_slope_m,
            'ph_intercept_b': ph_intercept_b,
            'ph_r_squared': ph_r_squared,
            'ph_cal_temp': ph_cal_temp,
            'flow_rate_calibrated': flow_rate is not None,
            'flow_rate': flow_rate,
            'flow_rate_date': flow_date
        }

    def print_calibration_status(self):
        """
        แสดงสถานะการสอบเทียบทั้งหมด (Print all calibration status)
        """
        print("\n=== สถานะการสอบเทียบ (Calibration Status) ===")

        status = self.get_all_calibration_status()

        # pH calibration
        if status['ph_calibrated']:
            print(f"[OK] pH Calibration:")
            print(f"     สมการ: pH = {status['ph_slope_m']:.6f} * mV + {status['ph_intercept_b']:.4f}")
            print(f"     R2={status['ph_r_squared']:.6f}, Temp={status['ph_cal_temp']:.2f} C")
        else:
            print("[--] pH Calibration: ยังไม่ได้สอบเทียบ (Not calibrated)")

        # Flow rate
        if status['flow_rate_calibrated']:
            print(f"[OK] Flow Rate: {status['flow_rate']:.4f} mL/s")
            print(f"     Last saved: {status['flow_rate_date'] or 'N/A'}")
        else:
            print("[--] Flow Rate: ยังไม่ได้สอบเทียบ (Not calibrated)")

        print()

    def __repr__(self):
        """แสดงข้อมูล DataManager"""
        ph_ok = "OK" if self.has_ph_calibration() else "--"
        flow_ok = "OK" if self.has_flow_rate() else "--"
        return f"DataManager(pH={ph_ok}, flow={flow_ok})"

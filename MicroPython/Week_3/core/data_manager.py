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
#   - data_calibrate.txt: ข้อมูลสอบเทียบ pH (slope, intercept, date)
#   - data_flowrate.txt: ข้อมูลอัตราการไหล (flow_rate, date)
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
        data_calibrate.txt:
            line 1: slope (float)
            line 2: intercept (float)
            line 3: Last saved: YYYY-MM-DD

        data_flowrate.txt:
            line 1: flow_rate (float, mL/s)
            line 2: Last saved: YYYY-MM-DD

    ตัวอย่างการใช้งาน (Usage Example):
        >>> dm = DataManager()
        >>> dm.save_ph_calibration(-5.79, 16.77)
        >>> slope, intercept, date = dm.load_ph_calibration()
        >>> dm.save_flow_rate(0.2772)
        >>> flow_rate, date = dm.load_flow_rate()
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

    def save_ph_calibration(self, slope, intercept, r_squared=None):
        """
        บันทึกข้อมูลสอบเทียบ pH (Save pH calibration data)

        Args:
            slope (float): ค่า slope ของสมการ
            intercept (float): ค่า intercept ของสมการ
            r_squared (float): ค่า R-squared (optional)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        try:
            current_date = self._get_current_date()

            with open(self._calibration_file, "w") as f:
                f.write(f"{slope}\n")
                f.write(f"{intercept}\n")
                f.write(f"Last saved: {current_date}\n")
                if r_squared is not None:
                    f.write(f"R-squared: {r_squared}\n")

            print(f"บันทึกข้อมูลสอบเทียบ pH สำเร็จ (pH calibration saved)")
            print(f"  slope={slope:.4f}, intercept={intercept:.4f}")
            print(f"  Date: {current_date}")
            return True

        except Exception as e:
            print(f"ข้อผิดพลาดบันทึกข้อมูล (Error saving data): {e}")
            return False

    def load_ph_calibration(self):
        """
        โหลดข้อมูลสอบเทียบ pH (Load pH calibration data)

        Returns:
            tuple: (slope, intercept, last_saved_date)
                   คืน (None, None, None) ถ้าไม่พบข้อมูล
        """
        if not self._file_exists(self._calibration_file):
            print(f"ไม่พบไฟล์สอบเทียบ: {self._calibration_file} "
                  f"(Calibration file not found)")
            return None, None, None

        try:
            with open(self._calibration_file, "r") as f:
                lines = f.readlines()

            slope = float(lines[0].strip())
            intercept = float(lines[1].strip())

            # อ่านวันที่ (Read date)
            last_saved = None
            if len(lines) > 2:
                date_line = lines[2].strip()
                if date_line.startswith("Last saved:"):
                    last_saved = date_line.replace("Last saved:", "").strip()

            print(f"โหลดข้อมูลสอบเทียบ pH สำเร็จ (pH calibration loaded)")
            print(f"  slope={slope:.4f}, intercept={intercept:.4f}")
            print(f"  Date: {last_saved or 'N/A'}")

            return slope, intercept, last_saved

        except Exception as e:
            print(f"ข้อผิดพลาดโหลดข้อมูล (Error loading data): {e}")
            return None, None, None

    def get_ph_calibration_date(self):
        """
        รับเฉพาะวันที่สอบเทียบ pH ล่าสุด
        Get only the last pH calibration date

        Returns:
            str: วันที่สอบเทียบ หรือ "N/A"
        """
        _, _, date = self.load_ph_calibration()
        return date or "N/A"

    # ===========================================================================
    # Flow Rate Data
    # ===========================================================================

    def save_flow_rate(self, flow_rate):
        """
        บันทึกข้อมูลอัตราการไหล (Save flow rate data)

        Args:
            flow_rate (float): อัตราการไหล mL/s

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        try:
            current_date = self._get_current_date()

            with open(self._flowrate_file, "w") as f:
                f.write(f"{flow_rate}\n")
                f.write(f"Last saved: {current_date}\n")

            print(f"บันทึกข้อมูลอัตราการไหลสำเร็จ (Flow rate saved)")
            print(f"  flow_rate={flow_rate:.4f} mL/s")
            print(f"  Date: {current_date}")
            return True

        except Exception as e:
            print(f"ข้อผิดพลาดบันทึกข้อมูล (Error saving data): {e}")
            return False

    def load_flow_rate(self):
        """
        โหลดข้อมูลอัตราการไหล (Load flow rate data)

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

            flow_rate = float(lines[0].strip())

            # อ่านวันที่ (Read date)
            last_saved = None
            if len(lines) > 1:
                date_line = lines[1].strip()
                if date_line.startswith("Last saved:"):
                    last_saved = date_line.replace("Last saved:", "").strip()

            print(f"โหลดข้อมูลอัตราการไหลสำเร็จ (Flow rate loaded)")
            print(f"  flow_rate={flow_rate:.4f} mL/s")
            print(f"  Date: {last_saved or 'N/A'}")

            return flow_rate, last_saved

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
        # โหลดข้อมูล pH
        ph_slope, ph_intercept, ph_date = self.load_ph_calibration()

        # โหลดข้อมูล flow rate
        flow_rate, flow_date = self.load_flow_rate()

        return {
            'ph_calibrated': ph_slope is not None,
            'ph_slope': ph_slope,
            'ph_intercept': ph_intercept,
            'ph_date': ph_date,
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
            print(f"     slope={status['ph_slope']:.4f}, intercept={status['ph_intercept']:.4f}")
            print(f"     Last saved: {status['ph_date'] or 'N/A'}")
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


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ DataManager (Testing DataManager)")
    print("=" * 50)

    # สร้าง DataManager
    dm = DataManager()

    # แสดงสถานะปัจจุบัน
    dm.print_calibration_status()

    # ทดสอบบันทึก pH calibration
    print("\n--- ทดสอบบันทึก pH Calibration ---")
    dm.save_ph_calibration(-5.7901, 16.769, 0.9999)

    # ทดสอบโหลด pH calibration
    print("\n--- ทดสอบโหลด pH Calibration ---")
    slope, intercept, date = dm.load_ph_calibration()

    # ทดสอบบันทึก flow rate
    print("\n--- ทดสอบบันทึก Flow Rate ---")
    dm.save_flow_rate(0.2772)

    # ทดสอบโหลด flow rate
    print("\n--- ทดสอบโหลด Flow Rate ---")
    flow_rate, date = dm.load_flow_rate()

    # แสดงสถานะหลังบันทึก
    dm.print_calibration_status()

    # ทดสอบสำรองข้อมูล
    print("\n--- ทดสอบสำรองข้อมูล ---")
    dm.backup_calibration_data()

    print("\nเสร็จสิ้น (Done)")

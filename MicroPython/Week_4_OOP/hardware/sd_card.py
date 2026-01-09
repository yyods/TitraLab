# ==============================================================================
# sd_card.py - คลาสสำหรับจัดการ SD Card (SD Card Management Class)
# ==============================================================================
# โมดูลนี้จัดการการอ่าน/เขียนข้อมูลลง SD Card สำหรับบันทึกผลการไทเทรชัน
# This module handles SD Card read/write operations for titration data logging
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การใช้ SPI เชื่อมต่อกับ SD Card
# 2. เข้าใจการจัดการไฟล์ (file system) บน MicroPython
# 3. บันทึกข้อมูลในรูปแบบ CSV สำหรับการวิเคราะห์
#
# Hardware Configuration:
# - SCK:  GPIO18 (SPI Clock)
# - MOSI: GPIO23 (Master Out Slave In)
# - MISO: GPIO19 (Master In Slave Out)
# - CS:   GPIO5  (Chip Select)
# ==============================================================================

import os
from machine import Pin, SPI

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import SD_SCK, SD_MOSI, SD_MISO, SD_CS, SD_BAUDRATE
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    SD_SCK = 18
    SD_MOSI = 23
    SD_MISO = 19
    SD_CS = 5
    SD_BAUDRATE = 1000000

# นำเข้า sdcard driver (Import SD Card driver)
try:
    import sdcard
except ImportError:
    print("ข้อผิดพลาด: ไม่พบไลบรารี sdcard (Error: sdcard library not found)")
    sdcard = None


class SDCardManager:
    """
    คลาสจัดการ SD Card สำหรับบันทึกข้อมูลการไทเทรชัน
    SD Card manager class for titration data logging

    คุณสมบัติ (Features):
    - เชื่อมต่อ/ถอด SD Card อัตโนมัติ (Auto mount/unmount)
    - บันทึกข้อมูลในรูปแบบ CSV (CSV format logging)
    - ระบบตั้งชื่อไฟล์เวอร์ชัน (Versioned file naming)
    - ตรวจสอบพื้นที่ว่าง (Free space checking)
    """

    # ขา GPIO สำหรับ SD Card (GPIO pins for SD Card)
    # ใช้ค่าจาก config.py (Use values from config.py)
    SD_SCK_PIN = SD_SCK     # SPI Clock (GPIO18)
    SD_MOSI_PIN = SD_MOSI   # Master Out Slave In (GPIO23)
    SD_MISO_PIN = SD_MISO   # Master In Slave Out (GPIO19)
    SD_CS_PIN = SD_CS       # Chip Select (GPIO5)

    # ค่าตั้งต้น (Default values)
    MOUNT_POINT = '/sd'
    DEFAULT_BAUDRATE = SD_BAUDRATE  # 1 MHz สำหรับความเสถียร (for stability)

    def __init__(self, mount_point=None):
        """
        กำหนดค่าเริ่มต้น SD Card Manager
        Initialize SD Card Manager

        Args:
            mount_point: จุดเมาท์ SD Card (SD Card mount point), default '/sd'
        """
        self.mount_point = mount_point or self.MOUNT_POINT
        self.spi = None
        self.sd = None
        self.cs_pin = None
        self._is_mounted = False

    def init(self):
        """
        เริ่มต้นการเชื่อมต่อ SD Card
        Initialize SD Card connection

        Returns:
            bool: True ถ้าสำเร็จ (if successful)
        """
        if sdcard is None:
            print("ข้อผิดพลาด: ไม่มีไลบรารี sdcard (Error: sdcard library not available)")
            return False

        try:
            # ตั้งค่า SPI สำหรับ SD Card (Setup SPI for SD Card)
            self.spi = SPI(
                2,  # ใช้ SPI bus 2 (Use SPI bus 2)
                baudrate=self.DEFAULT_BAUDRATE,
                sck=Pin(self.SD_SCK_PIN),
                mosi=Pin(self.SD_MOSI_PIN),
                miso=Pin(self.SD_MISO_PIN)
            )

            # ตั้งค่าขา CS (Setup CS pin)
            self.cs_pin = Pin(self.SD_CS_PIN, Pin.OUT)

            # สร้าง SD Card object (Create SD Card object)
            self.sd = sdcard.SDCard(self.spi, self.cs_pin)

            # เมาท์ SD Card (Mount SD Card)
            os.mount(self.sd, self.mount_point)
            self._is_mounted = True

            print(f"SD Card พร้อมใช้งานที่ {self.mount_point} (SD Card ready at {self.mount_point})")
            return True

        except OSError as e:
            print(f"ข้อผิดพลาด: ไม่สามารถเชื่อมต่อ SD Card (Error: Cannot mount SD Card): {e}")
            self._is_mounted = False
            return False
        except Exception as e:
            print(f"ข้อผิดพลาดทั่วไป (General error): {e}")
            self._is_mounted = False
            return False

    @property
    def is_mounted(self):
        """
        ตรวจสอบสถานะการเมาท์ SD Card
        Check SD Card mount status

        Returns:
            bool: True ถ้าเมาท์แล้ว (if mounted)
        """
        return self._is_mounted

    def list_files(self, path=None):
        """
        แสดงรายการไฟล์ใน SD Card
        List files on SD Card

        Args:
            path: พาธที่ต้องการดู (Path to list), default is mount point

        Returns:
            list: รายชื่อไฟล์ (List of filenames)
        """
        if not self._is_mounted:
            print("ข้อผิดพลาด: SD Card ยังไม่ได้เมาท์ (Error: SD Card not mounted)")
            return []

        try:
            target_path = path or self.mount_point
            files = os.listdir(target_path)
            return files
        except OSError as e:
            print(f"ข้อผิดพลาด: ไม่สามารถอ่านรายการไฟล์ (Error: Cannot list files): {e}")
            return []

    def get_next_version(self, base_filename):
        """
        หาเวอร์ชันถัดไปของไฟล์ (เช่น titration_data_R1.csv -> R2.csv)
        Find next version number for file (e.g., titration_data_R1.csv -> R2.csv)

        Args:
            base_filename: ชื่อไฟล์พื้นฐาน (Base filename without version)

        Returns:
            str: ชื่อไฟล์พร้อมเวอร์ชัน (Filename with version)
        """
        if not self._is_mounted:
            return f"{base_filename}_R1.csv"

        files = self.list_files()
        version = 1

        # หาเวอร์ชันสูงสุดที่มีอยู่ (Find highest existing version)
        for f in files:
            if f.startswith(base_filename) and f.endswith('.csv'):
                try:
                    # แยกหมายเลขเวอร์ชันจากชื่อไฟล์ (Extract version number)
                    # รูปแบบ: base_filename_R{n}.csv
                    parts = f.replace('.csv', '').split('_R')
                    if len(parts) >= 2:
                        v = int(parts[-1])
                        if v >= version:
                            version = v + 1
                except (ValueError, IndexError):
                    pass

        return f"{base_filename}_R{version}.csv"

    def write_csv_header(self, filename, headers):
        """
        เขียนส่วนหัวของไฟล์ CSV
        Write CSV file header

        Args:
            filename: ชื่อไฟล์ (Filename)
            headers: รายการหัวคอลัมน์ (List of column headers)

        Returns:
            bool: True ถ้าสำเร็จ (if successful)
        """
        if not self._is_mounted:
            print("ข้อผิดพลาด: SD Card ยังไม่ได้เมาท์ (Error: SD Card not mounted)")
            return False

        try:
            filepath = f"{self.mount_point}/{filename}"
            with open(filepath, 'w') as f:
                header_line = ','.join(headers)
                f.write(header_line + '\n')
            print(f"สร้างไฟล์ CSV: {filename} (Created CSV file: {filename})")
            return True
        except OSError as e:
            print(f"ข้อผิดพลาด: ไม่สามารถเขียนไฟล์ (Error: Cannot write file): {e}")
            return False

    def append_csv_row(self, filename, data):
        """
        เพิ่มแถวข้อมูลลงไฟล์ CSV
        Append data row to CSV file

        Args:
            filename: ชื่อไฟล์ (Filename)
            data: รายการข้อมูล (List of data values)

        Returns:
            bool: True ถ้าสำเร็จ (if successful)
        """
        if not self._is_mounted:
            print("ข้อผิดพลาด: SD Card ยังไม่ได้เมาท์ (Error: SD Card not mounted)")
            return False

        try:
            filepath = f"{self.mount_point}/{filename}"
            with open(filepath, 'a') as f:
                # แปลงข้อมูลเป็น string (Convert data to strings)
                row = ','.join(str(d) for d in data)
                f.write(row + '\n')
            return True
        except OSError as e:
            print(f"ข้อผิดพลาด: ไม่สามารถเขียนข้อมูล (Error: Cannot write data): {e}")
            return False

    def read_file(self, filename):
        """
        อ่านเนื้อหาไฟล์ทั้งหมด
        Read entire file content

        Args:
            filename: ชื่อไฟล์ (Filename)

        Returns:
            str: เนื้อหาไฟล์ (File content) หรือ None ถ้าล้มเหลว
        """
        if not self._is_mounted:
            print("ข้อผิดพลาด: SD Card ยังไม่ได้เมาท์ (Error: SD Card not mounted)")
            return None

        try:
            filepath = f"{self.mount_point}/{filename}"
            with open(filepath, 'r') as f:
                content = f.read()
            return content
        except OSError as e:
            print(f"ข้อผิดพลาด: ไม่สามารถอ่านไฟล์ (Error: Cannot read file): {e}")
            return None

    def file_exists(self, filename):
        """
        ตรวจสอบว่าไฟล์มีอยู่หรือไม่
        Check if file exists

        Args:
            filename: ชื่อไฟล์ (Filename)

        Returns:
            bool: True ถ้าไฟล์มีอยู่ (if file exists)
        """
        if not self._is_mounted:
            return False

        try:
            filepath = f"{self.mount_point}/{filename}"
            os.stat(filepath)
            return True
        except OSError:
            return False

    def delete_file(self, filename):
        """
        ลบไฟล์จาก SD Card
        Delete file from SD Card

        Args:
            filename: ชื่อไฟล์ (Filename)

        Returns:
            bool: True ถ้าสำเร็จ (if successful)
        """
        if not self._is_mounted:
            print("ข้อผิดพลาด: SD Card ยังไม่ได้เมาท์ (Error: SD Card not mounted)")
            return False

        try:
            filepath = f"{self.mount_point}/{filename}"
            os.remove(filepath)
            print(f"ลบไฟล์สำเร็จ: {filename} (File deleted: {filename})")
            return True
        except OSError as e:
            print(f"ข้อผิดพลาด: ไม่สามารถลบไฟล์ (Error: Cannot delete file): {e}")
            return False

    def get_free_space(self):
        """
        ตรวจสอบพื้นที่ว่างใน SD Card
        Check free space on SD Card

        Returns:
            tuple: (total_bytes, free_bytes) หรือ (0, 0) ถ้าล้มเหลว
        """
        if not self._is_mounted:
            return (0, 0)

        try:
            stats = os.statvfs(self.mount_point)
            block_size = stats[0]
            total_blocks = stats[2]
            free_blocks = stats[3]

            total_bytes = block_size * total_blocks
            free_bytes = block_size * free_blocks

            return (total_bytes, free_bytes)
        except OSError:
            return (0, 0)

    def deinit(self):
        """
        ยกเลิกการเชื่อมต่อ SD Card
        Unmount and cleanup SD Card connection
        """
        if self._is_mounted:
            try:
                os.umount(self.mount_point)
                print(f"ยกเลิกการเมาท์ SD Card (SD Card unmounted)")
            except OSError as e:
                print(f"ข้อผิดพลาด: ไม่สามารถยกเลิกการเมาท์ (Error: Cannot unmount): {e}")
            finally:
                self._is_mounted = False

        if self.spi:
            try:
                self.spi.deinit()
            except Exception:
                pass
            self.spi = None

        self.sd = None
        self.cs_pin = None


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("ทดสอบ SDCardManager (Testing SDCardManager)")
    print("=" * 50)

    # สร้าง SD Card Manager (Create SD Card Manager)
    sd_manager = SDCardManager()

    try:
        # เริ่มต้นการเชื่อมต่อ (Initialize connection)
        if sd_manager.init():
            # แสดงรายการไฟล์ (List files)
            print("\nไฟล์ใน SD Card (Files on SD Card):")
            files = sd_manager.list_files()
            for f in files:
                print(f"  - {f}")

            # ตรวจสอบพื้นที่ว่าง (Check free space)
            total, free = sd_manager.get_free_space()
            print(f"\nพื้นที่ทั้งหมด (Total): {total // 1024} KB")
            print(f"พื้นที่ว่าง (Free): {free // 1024} KB")

            # ทดสอบเขียนไฟล์ CSV (Test CSV writing)
            test_filename = sd_manager.get_next_version('test_data')
            headers = ['Cycle', 'Time(s)', 'Volume(mL)', 'pH', 'Temperature(C)']

            if sd_manager.write_csv_header(test_filename, headers):
                # เพิ่มข้อมูลทดสอบ (Add test data)
                test_data = [1, 0.0, 0.0, 7.00, 25.0]
                sd_manager.append_csv_row(test_filename, test_data)
                print(f"\nเขียนไฟล์ทดสอบสำเร็จ: {test_filename}")
                print("(Test file written successfully)")

    except Exception as e:
        print(f"ข้อผิดพลาด (Error): {e}")

    finally:
        # ทำความสะอาด (Cleanup)
        sd_manager.deinit()
        print("\nปิดการเชื่อมต่อ SD Card (SD Card connection closed)")

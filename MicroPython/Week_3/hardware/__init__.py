# ==============================================================================
# hardware/__init__.py - แพ็คเกจฮาร์ดแวร์และ HardwareHub สำหรับ TitraLab
# (Hardware Package and HardwareHub for TitraLab)
# ==============================================================================
# โมดูลนี้รวบรวมคลาสฮาร์ดแวร์ทั้งหมดและจัดการผ่าน HardwareHub
# This module aggregates all hardware classes and manages via HardwareHub
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Python package และ __init__.py
#   2. เรียนรู้ pattern การรวม (aggregation) ของ objects
#   3. ประยุกต์ใช้ dependency injection
#
# การใช้งาน (Usage):
#   from hardware import HardwareHub
#   hw = HardwareHub()
#   hw.pump.start(100)
#   hw.buzzer.beep()
#
# ==============================================================================

# นำเข้าคลาสจากโมดูลย่อย (Import classes from submodules)
from .pump import Pump
from .buttons import Button, ButtonManager
from .buzzer import Buzzer
from .ph_sensor import PHSensor
from .temp_sensor import TemperatureSensor
from .display import DisplayManager, Colors
from .leds import LED, LEDManager
# หมายเหตุ: ไม่นำเข้า SDCardManager เนื่องจากไม่ใช้งาน
# Note: SDCardManager not imported - not used (board connected to laptop via USB)

# กำหนดสิ่งที่ export เมื่อใช้ from hardware import *
# Define what to export when using from hardware import *
__all__ = [
    'Pump',
    'Button',
    'ButtonManager',
    'Buzzer',
    'PHSensor',
    'TemperatureSensor',
    'DisplayManager',
    'Colors',
    'LED',
    'LEDManager',
    'HardwareHub'
]


class HardwareHub:
    """
    คลาสรวมศูนย์ฮาร์ดแวร์ทั้งหมด (Central Hardware Aggregation Class)

    HardwareHub ทำหน้าที่:
        1. สร้างและจัดการ hardware objects ทั้งหมด
        2. จัดการ lifecycle (initialization/cleanup)
        3. ให้ interface รวมสำหรับเข้าถึง hardware

    ข้อดี (Benefits):
        - Centralized management
        - Easy cleanup via single deinit()
        - Dependency injection friendly
        - Testable (can mock hardware)

    ตัวอย่างการใช้งาน (Usage Example):
        >>> hw = HardwareHub()
        >>> hw.pump.start(100)           # ควบคุมปั๊ม
        >>> temp = hw.temp_sensor.read() # อ่านอุณหภูมิ
        >>> voltage, ph = hw.ph_sensor.read()  # อ่าน pH
        >>> hw.buzzer.beep()             # เสียง beep
        >>> if hw.buttons.select.is_pressed():
        ...     print("Selected!")
        >>> hw.deinit()                  # ทำความสะอาด
    """

    def __init__(self, init_all=True, skip_missing=True):
        """
        สร้าง HardwareHub และ initialize hardware ทั้งหมด
        Create HardwareHub and initialize all hardware

        Args:
            init_all (bool): True = initialize hardware ทั้งหมด
                             False = ไม่ initialize (ต้องเรียก init_* เอง)
            skip_missing (bool): True = ข้ามถ้า hardware ไม่พร้อม
                                 False = raise error ถ้า hardware ไม่พร้อม
        """
        print("=" * 50)
        print("กำลังเริ่มต้น HardwareHub (Initializing HardwareHub)")
        print("=" * 50)

        self._skip_missing = skip_missing

        # Hardware objects (เริ่มต้นเป็น None)
        self._pump = None
        self._buttons = None
        self._buzzer = None
        self._ph_sensor = None
        self._temp_sensor = None
        # หมายเหตุ: ไม่ใช้ SD Card - บอร์ดเชื่อมต่อ laptop ตลอดเวลาผ่าน USB
        # Note: SD Card NOT USED - board always connected to laptop via USB

        # ติดตาม hardware ที่ initialized สำเร็จ
        # Track successfully initialized hardware
        self._initialized = {
            'pump': False,
            'buttons': False,
            'buzzer': False,
            'ph_sensor': False,
            'temp_sensor': False
        }

        # Initialize ถ้ากำหนด (Initialize if requested)
        if init_all:
            self.init_all()

        print("=" * 50)
        print("HardwareHub พร้อมใช้งาน (HardwareHub ready)")
        print("=" * 50)

    def init_all(self):
        """
        Initialize hardware ทั้งหมด (Initialize all hardware)
        หมายเหตุ: ไม่รวม SD Card - ข้อมูลบันทึกใน ESP32 flash
        Note: SD Card excluded - data saved to ESP32 flash storage
        """
        self.init_pump()
        self.init_buttons()
        self.init_buzzer()
        self.init_ph_sensor()
        self.init_temp_sensor()

    def init_pump(self):
        """Initialize ปั๊ม (Initialize pump)"""
        try:
            self._pump = Pump()
            self._initialized['pump'] = True
        except Exception as e:
            print(f"ข้อผิดพลาดเริ่มต้นปั๊ม (Pump init error): {e}")
            if not self._skip_missing:
                raise

    def init_buttons(self):
        """Initialize ปุ่มกด (Initialize buttons)"""
        try:
            self._buttons = ButtonManager()
            self._initialized['buttons'] = True
        except Exception as e:
            print(f"ข้อผิดพลาดเริ่มต้นปุ่ม (Buttons init error): {e}")
            if not self._skip_missing:
                raise

    def init_buzzer(self):
        """Initialize buzzer"""
        try:
            self._buzzer = Buzzer()
            self._initialized['buzzer'] = True
        except Exception as e:
            print(f"ข้อผิดพลาดเริ่มต้น Buzzer (Buzzer init error): {e}")
            if not self._skip_missing:
                raise

    def init_ph_sensor(self):
        """Initialize เซ็นเซอร์ pH (Initialize pH sensor)"""
        try:
            self._ph_sensor = PHSensor()
            self._initialized['ph_sensor'] = True
        except Exception as e:
            print(f"ข้อผิดพลาดเริ่มต้น pH sensor (pH sensor init error): {e}")
            if not self._skip_missing:
                raise

    def init_temp_sensor(self):
        """Initialize เซ็นเซอร์อุณหภูมิ (Initialize temperature sensor)"""
        try:
            self._temp_sensor = TemperatureSensor()
            self._initialized['temp_sensor'] = True
        except Exception as e:
            print(f"ข้อผิดพลาดเริ่มต้น temp sensor (Temp sensor init error): {e}")
            if not self._skip_missing:
                raise

    # หมายเหตุ: init_sd_card() ถูกลบแล้ว - ไม่ใช้ SD Card
    # Note: init_sd_card() removed - SD Card NOT USED
    # ไฟล์ CSV จะบันทึกใน ESP32 flash storage และดาวน์โหลดผ่าน Thonny IDE
    # CSV files saved to ESP32 flash storage and downloaded via Thonny IDE

    # === Properties สำหรับเข้าถึง hardware ===
    # === Properties for accessing hardware ===

    @property
    def pump(self):
        """
        เข้าถึงปั๊ม (Access pump)

        Returns:
            Pump: Pump object
        """
        if self._pump is None:
            raise RuntimeError("ปั๊มยังไม่ได้ initialize (Pump not initialized)")
        return self._pump

    @property
    def buttons(self):
        """
        เข้าถึง ButtonManager (Access ButtonManager)

        Returns:
            ButtonManager: ButtonManager object
        """
        if self._buttons is None:
            raise RuntimeError("ปุ่มยังไม่ได้ initialize (Buttons not initialized)")
        return self._buttons

    @property
    def buzzer(self):
        """
        เข้าถึง Buzzer (Access Buzzer)

        Returns:
            Buzzer: Buzzer object
        """
        if self._buzzer is None:
            raise RuntimeError("Buzzer ยังไม่ได้ initialize (Buzzer not initialized)")
        return self._buzzer

    @property
    def ph_sensor(self):
        """
        เข้าถึงเซ็นเซอร์ pH (Access pH sensor)

        Returns:
            PHSensor: PHSensor object
        """
        if self._ph_sensor is None:
            raise RuntimeError("pH sensor ยังไม่ได้ initialize (pH sensor not initialized)")
        return self._ph_sensor

    @property
    def temp_sensor(self):
        """
        เข้าถึงเซ็นเซอร์อุณหภูมิ (Access temperature sensor)

        Returns:
            TemperatureSensor: TemperatureSensor object
        """
        if self._temp_sensor is None:
            raise RuntimeError("Temp sensor ยังไม่ได้ initialize (Temp sensor not initialized)")
        return self._temp_sensor

    # หมายเหตุ: sd_card property ถูกลบแล้ว - ไม่ใช้ SD Card
    # Note: sd_card property removed - SD Card NOT USED
    # ข้อมูลบันทึกใน ESP32 flash storage แทน
    # Data saved to ESP32 flash storage instead

    # === Utility Methods ===

    def get_status(self):
        """
        อ่านสถานะ hardware ทั้งหมด (Get status of all hardware)

        Returns:
            dict: สถานะของแต่ละ hardware
        """
        return self._initialized.copy()

    def is_ready(self, hardware_name=None):
        """
        ตรวจสอบว่า hardware พร้อมใช้งานหรือไม่
        Check if hardware is ready

        Args:
            hardware_name (str): ชื่อ hardware ที่ต้องการตรวจสอบ
                                 None = ตรวจสอบทั้งหมด

        Returns:
            bool: True ถ้าพร้อม (if ready)
        """
        if hardware_name is None:
            return all(self._initialized.values())
        return self._initialized.get(hardware_name, False)

    def print_status(self):
        """
        แสดงสถานะ hardware ทั้งหมด (Print status of all hardware)
        """
        print("\n=== สถานะ Hardware (Hardware Status) ===")
        for name, status in self._initialized.items():
            status_str = "พร้อม (Ready)" if status else "ไม่พร้อม (Not Ready)"
            icon = "[OK]" if status else "[--]"
            print(f"{icon} {name}: {status_str}")
        print()

    def deinit(self):
        """
        ปิดการใช้งาน hardware ทั้งหมด (Deinitialize all hardware)

        ควรเรียกเมื่อจบการทำงาน
        Should be called when done
        """
        print("\n=== กำลังปิด HardwareHub (Shutting down HardwareHub) ===")

        # ปิดปั๊ม (Deinitialize pump)
        if self._pump is not None:
            try:
                self._pump.deinit()
            except Exception as e:
                print(f"ข้อผิดพลาดปิดปั๊ม: {e}")
            self._pump = None
            self._initialized['pump'] = False

        # ปิด Buzzer (Deinitialize buzzer)
        if self._buzzer is not None:
            try:
                self._buzzer.deinit()
            except Exception as e:
                print(f"ข้อผิดพลาดปิด Buzzer: {e}")
            self._buzzer = None
            self._initialized['buzzer'] = False

        # หมายเหตุ: SD Card deinit ถูกลบแล้ว - ไม่ใช้ SD Card
        # Note: SD Card deinit removed - SD Card NOT USED

        # ปุ่มและเซ็นเซอร์ไม่ต้อง deinit เพราะเป็น input-only
        # Buttons and sensors don't need deinit (input-only)
        self._buttons = None
        self._initialized['buttons'] = False

        self._ph_sensor = None
        self._initialized['ph_sensor'] = False

        self._temp_sensor = None
        self._initialized['temp_sensor'] = False

        print("HardwareHub ปิดแล้ว (HardwareHub shut down)")

    def __del__(self):
        """
        Destructor - ทำความสะอาดเมื่อ object ถูกลบ
        Destructor - cleanup when object is deleted
        """
        self.deinit()

    def __repr__(self):
        """แสดงข้อมูล HardwareHub"""
        ready_count = sum(self._initialized.values())
        total_count = len(self._initialized)
        return f"HardwareHub({ready_count}/{total_count} ready)"

    # === Context Manager Support ===
    # รองรับการใช้ with statement

    def __enter__(self):
        """
        เข้าสู่ context (Enter context)

        ใช้กับ with statement:
            with HardwareHub() as hw:
                hw.pump.start(100)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ออกจาก context (Exit context)"""
        self.deinit()
        return False

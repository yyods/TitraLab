# ==============================================================================
# leds.py - คลาสควบคุม LED สำหรับ TitraLab
# (LED Control Classes for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการ LED แสดงสถานะสำหรับระบบไทเทรชัน
# This module manages status LEDs for the titration system
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจหลักการควบคุม GPIO แบบ output
#   2. เรียนรู้การออกแบบคลาสแบบ composition (LED + LEDManager)
#   3. ประยุกต์ใช้ pattern การจัดการทรัพยากร hardware
#
# หลักการทำงานของ LED (LED Working Principle):
#   - LED (Light Emitting Diode) เปล่งแสงเมื่อมีกระแสไฟฟ้าไหลผ่าน
#   - ต่อกับ GPIO ผ่าน resistor จำกัดกระแส (330-470 ohm)
#   - Active HIGH: GPIO = 1 -> LED สว่าง
#   - Active LOW: GPIO = 0 -> LED สว่าง (ขึ้นกับการต่อวงจร)
#
# การใช้งานใน TitraLab (Usage in TitraLab):
#   - LED สีเขียว (Green): แสดงสถานะปกติ/กำลังทำงาน
#   - LED สีแดง (Red): แสดงข้อผิดพลาด/เตือน
#
# ==============================================================================

from machine import Pin
from time import sleep_ms

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import LED_RED, LED_GREEN
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    LED_RED = 2      # GPIO2 - LED สีแดง (Red LED)
    LED_GREEN = 4    # GPIO4 - LED สีเขียว (Green LED)


class LED:
    """
    คลาสควบคุม LED เดี่ยว (Single LED Control Class)

    คุณสมบัติหลัก (Main Features):
        - เปิด/ปิด LED
        - สลับสถานะ (toggle)
        - กระพริบ (blink) ตามจำนวนครั้งและความเร็วที่กำหนด
        - ตรวจสอบสถานะปัจจุบัน

    หลักการ GPIO Output:
        - Pin.OUT กำหนดให้ขาเป็น output
        - pin.value(1) หรือ pin.on() = ส่งสัญญาณ HIGH (3.3V)
        - pin.value(0) หรือ pin.off() = ส่งสัญญาณ LOW (0V)

    การต่อวงจร LED แบบ Active HIGH:
        GPIO ---- [Resistor 330R] ---- [LED] ---- GND
        เมื่อ GPIO = HIGH -> LED สว่าง

    ตัวอย่างการใช้งาน (Usage Example):
        >>> led = LED(2, name="Red")
        >>> led.on()                    # เปิด LED
        >>> led.off()                   # ปิด LED
        >>> led.toggle()                # สลับสถานะ
        >>> led.blink(3, 200)           # กระพริบ 3 ครั้ง ห่างกัน 200ms
        >>> print(led.is_on)            # ตรวจสอบสถานะ
    """

    def __init__(self, pin_number, name="LED", active_high=True):
        """
        สร้าง LED object (Create LED object)

        Args:
            pin_number (int): หมายเลขขา GPIO (GPIO pin number)
            name (str): ชื่อ LED สำหรับแสดงข้อความ (LED name for display)
            active_high (bool): True ถ้า GPIO HIGH = LED สว่าง
                               (True if GPIO HIGH = LED on)
                               ค่าเริ่มต้น: True (สำหรับ TitraLab)
        """
        self._pin_number = pin_number
        self._name = name
        self._active_high = active_high

        # สร้าง Pin object เป็น output (Create Pin object as output)
        self._pin = Pin(pin_number, Pin.OUT)

        # สถานะเริ่มต้น: ปิด LED (Initial state: LED off)
        self._state = False
        self.off()

        print(f"LED '{name}' พร้อมใช้งานที่ GPIO{pin_number} "
              f"(LED '{name}' ready on GPIO{pin_number})")

    @property
    def name(self):
        """ชื่อ LED (LED name)"""
        return self._name

    @property
    def pin_number(self):
        """หมายเลข GPIO (GPIO pin number)"""
        return self._pin_number

    @property
    def is_on(self):
        """
        ตรวจสอบว่า LED สว่างอยู่หรือไม่ (Check if LED is on)

        Returns:
            bool: True ถ้า LED สว่าง (if LED is on)
        """
        return self._state

    @property
    def state(self):
        """
        อ่านสถานะ LED (Get LED state)

        Returns:
            bool: True = สว่าง, False = ดับ (True = on, False = off)
        """
        return self._state

    def on(self):
        """
        เปิด LED (Turn LED on)

        ตั้งค่า GPIO เป็น HIGH (สำหรับ active_high=True)
        Set GPIO to HIGH (for active_high=True)
        """
        if self._active_high:
            self._pin.value(1)
        else:
            self._pin.value(0)
        self._state = True

    def off(self):
        """
        ปิด LED (Turn LED off)

        ตั้งค่า GPIO เป็น LOW (สำหรับ active_high=True)
        Set GPIO to LOW (for active_high=True)
        """
        if self._active_high:
            self._pin.value(0)
        else:
            self._pin.value(1)
        self._state = False

    def toggle(self):
        """
        สลับสถานะ LED (Toggle LED state)

        ถ้าสว่างอยู่จะปิด ถ้าดับอยู่จะเปิด
        If on, turn off. If off, turn on.

        Returns:
            bool: สถานะใหม่หลัง toggle (new state after toggle)
        """
        if self._state:
            self.off()
        else:
            self.on()
        return self._state

    def blink(self, times=1, interval_ms=200):
        """
        กระพริบ LED ตามจำนวนครั้งที่กำหนด (Blink LED specified number of times)

        Args:
            times (int): จำนวนครั้งที่กระพริบ (number of blinks)
                         ค่าเริ่มต้น: 1 ครั้ง
            interval_ms (int): ระยะเวลาแต่ละช่วง (เปิด/ปิด) มิลลิวินาที
                              (duration of each phase in ms)
                              ค่าเริ่มต้น: 200ms

        ตัวอย่าง (Example):
            blink(3, 200) = กระพริบ 3 ครั้ง
            แต่ละครั้ง: สว่าง 200ms -> ดับ 200ms
        """
        # บันทึกสถานะเดิม (Save original state)
        original_state = self._state

        for _ in range(times):
            self.on()
            sleep_ms(interval_ms)
            self.off()
            sleep_ms(interval_ms)

        # คืนสู่สถานะเดิม (Restore original state)
        if original_state:
            self.on()

    def pulse(self, duration_ms=100):
        """
        กระพริบสั้นๆ หนึ่งครั้ง (Short single pulse)

        ใช้สำหรับแสดง feedback สั้นๆ เช่น รับสัญญาณ
        Used for short feedback like acknowledgment

        Args:
            duration_ms (int): ระยะเวลาที่สว่าง (duration LED is on in ms)
        """
        self.on()
        sleep_ms(duration_ms)
        self.off()

    def set_state(self, state):
        """
        กำหนดสถานะ LED (Set LED state)

        Args:
            state (bool): True = เปิด, False = ปิด (True = on, False = off)
        """
        if state:
            self.on()
        else:
            self.off()

    def init(self):
        """
        เริ่มต้น LED (Initialize LED)

        เมธอดนี้ถูกเรียกเพื่อเตรียม LED ให้พร้อมใช้งาน
        This method is called to prepare the LED for use.
        """
        pass  # LED พร้อมใช้งานตั้งแต่ __init__ (LED ready from __init__)

    def deinit(self):
        """
        ปิดการใช้งานและคืนทรัพยากร (Deinitialize and release resources)

        ควรเรียกเมื่อไม่ใช้งาน LED แล้ว
        Should be called when LED is no longer needed
        """
        try:
            self.off()  # ปิด LED ก่อน (Turn off LED first)
            print(f"ปิด LED '{self._name}' GPIO{self._pin_number} แล้ว "
                  f"(LED '{self._name}' GPIO{self._pin_number} deinitialized)")
        except Exception as e:
            print(f"ข้อผิดพลาดขณะปิด LED (Error during LED deinit): {e}")

    def __repr__(self):
        """แสดงข้อมูล LED (Display LED info)"""
        state_str = "ON" if self._state else "OFF"
        return f"LED('{self._name}', pin={self._pin_number}, {state_str})"


class LEDManager:
    """
    คลาสจัดการ LED ทั้งหมดสำหรับ TitraLab
    (LED Manager Class for all TitraLab LEDs)

    จัดการ LED 2 ดวง:
        - LED สีเขียว (Green): GPIO4 - แสดงสถานะปกติ
        - LED สีแดง (Red): GPIO2 - แสดงข้อผิดพลาด

    ข้อดีของ LEDManager:
        - รวมศูนย์การจัดการ LED ทั้งหมด
        - มีฟังก์ชัน all_on(), all_off() สำหรับควบคุมพร้อมกัน
        - ง่ายต่อการ cleanup ด้วย deinit() เดียว

    ตัวอย่างการใช้งาน (Usage Example):
        >>> leds = LEDManager()
        >>> leds.init()
        >>> leds.green.on()              # เปิด LED เขียว
        >>> leds.red.blink(2)            # กระพริบ LED แดง 2 ครั้ง
        >>> leds.all_on()                # เปิด LED ทั้งหมด
        >>> leds.all_off()               # ปิด LED ทั้งหมด
        >>> leds.deinit()                # ทำความสะอาด
    """

    def __init__(self, red_pin=None, green_pin=None):
        """
        สร้าง LEDManager (Create LEDManager)

        Args:
            red_pin (int): GPIO สำหรับ LED สีแดง (GPIO for red LED)
                          ค่าเริ่มต้น: GPIO2
            green_pin (int): GPIO สำหรับ LED สีเขียว (GPIO for green LED)
                            ค่าเริ่มต้น: GPIO4
        """
        # กำหนดค่าเริ่มต้น (Set defaults)
        self._red_pin = red_pin if red_pin is not None else LED_RED
        self._green_pin = green_pin if green_pin is not None else LED_GREEN

        # LED objects (เริ่มต้นเป็น None จนกว่าจะเรียก init)
        # LED objects (initialized as None until init() is called)
        self._red = None
        self._green = None

        # สถานะการ initialize (Initialization status)
        self._initialized = False

    def init(self):
        """
        เริ่มต้น LED ทั้งหมด (Initialize all LEDs)

        สร้าง LED objects และตั้งค่าเริ่มต้น
        Create LED objects and set initial state
        """
        try:
            # สร้าง LED แดง (Create red LED)
            self._red = LED(self._red_pin, name="Red")

            # สร้าง LED เขียว (Create green LED)
            self._green = LED(self._green_pin, name="Green")

            # ตั้งสถานะเริ่มต้น: ปิด LED ทั้งหมด (Initial state: all LEDs off)
            self.all_off()

            self._initialized = True
            print("LEDManager พร้อมใช้งาน (LEDManager ready)")

        except Exception as e:
            print(f"LEDManager init error: {e}")
            raise

    @property
    def red(self):
        """
        เข้าถึง LED สีแดง (Access red LED)

        Returns:
            LED: Red LED object

        Raises:
            RuntimeError: ถ้ายังไม่ได้ initialize
        """
        if self._red is None:
            raise RuntimeError(
                "LED ยังไม่ได้ initialize กรุณาเรียก init() ก่อน "
                "(LEDs not initialized, please call init() first)"
            )
        return self._red

    @property
    def green(self):
        """
        เข้าถึง LED สีเขียว (Access green LED)

        Returns:
            LED: Green LED object

        Raises:
            RuntimeError: ถ้ายังไม่ได้ initialize
        """
        if self._green is None:
            raise RuntimeError(
                "LED ยังไม่ได้ initialize กรุณาเรียก init() ก่อน "
                "(LEDs not initialized, please call init() first)"
            )
        return self._green

    @property
    def is_initialized(self):
        """ตรวจสอบว่า LEDManager ได้ initialize แล้วหรือไม่"""
        return self._initialized

    def all_on(self):
        """
        เปิด LED ทั้งหมด (Turn all LEDs on)
        """
        if not self._initialized:
            print("คำเตือน: LEDManager ยังไม่ได้ initialize "
                  "(Warning: LEDManager not initialized)")
            return

        self._red.on()
        self._green.on()

    def all_off(self):
        """
        ปิด LED ทั้งหมด (Turn all LEDs off)
        """
        if not self._initialized:
            print("คำเตือน: LEDManager ยังไม่ได้ initialize "
                  "(Warning: LEDManager not initialized)")
            return

        if self._red:
            self._red.off()
        if self._green:
            self._green.off()

    def all_toggle(self):
        """
        สลับสถานะ LED ทั้งหมด (Toggle all LEDs)
        """
        if not self._initialized:
            print("คำเตือน: LEDManager ยังไม่ได้ initialize "
                  "(Warning: LEDManager not initialized)")
            return

        self._red.toggle()
        self._green.toggle()

    def all_blink(self, times=1, interval_ms=200):
        """
        กระพริบ LED ทั้งหมดพร้อมกัน (Blink all LEDs together)

        Args:
            times (int): จำนวนครั้งที่กระพริบ (number of blinks)
            interval_ms (int): ระยะเวลาแต่ละช่วง (interval in ms)
        """
        if not self._initialized:
            print("คำเตือน: LEDManager ยังไม่ได้ initialize "
                  "(Warning: LEDManager not initialized)")
            return

        for _ in range(times):
            self.all_on()
            sleep_ms(interval_ms)
            self.all_off()
            sleep_ms(interval_ms)

    def indicate_success(self):
        """
        แสดงสถานะสำเร็จ (Indicate success)

        กระพริบ LED เขียว 3 ครั้ง
        Blink green LED 3 times
        """
        if self._initialized and self._green:
            self._green.blink(3, 150)

    def indicate_error(self):
        """
        แสดงสถานะข้อผิดพลาด (Indicate error)

        กระพริบ LED แดง 3 ครั้ง
        Blink red LED 3 times
        """
        if self._initialized and self._red:
            self._red.blink(3, 150)

    def indicate_working(self):
        """
        แสดงสถานะกำลังทำงาน (Indicate working/busy)

        เปิด LED เขียวค้างไว้
        Turn green LED on and keep it on
        """
        if self._initialized and self._green:
            self._green.on()

    def indicate_warning(self):
        """
        แสดงสถานะเตือน (Indicate warning)

        เปิด LED แดงค้างไว้
        Turn red LED on and keep it on
        """
        if self._initialized and self._red:
            self._red.on()

    def indicate_ready(self):
        """
        แสดงสถานะพร้อมใช้งาน (Indicate ready)

        ปิด LED ทั้งหมด (ระบบพร้อมใช้งาน รอคำสั่ง)
        Turn all LEDs off (system ready, waiting for command)
        """
        self.all_off()

    def get_status(self):
        """
        อ่านสถานะ LED ทั้งหมด (Get status of all LEDs)

        Returns:
            dict: สถานะของแต่ละ LED
                  {'red': bool, 'green': bool, 'initialized': bool}
        """
        return {
            'initialized': self._initialized,
            'red': self._red.is_on if self._red else None,
            'green': self._green.is_on if self._green else None
        }

    def deinit(self):
        """
        ปิดการใช้งาน LED ทั้งหมดและคืนทรัพยากร
        Deinitialize all LEDs and release resources

        ควรเรียกเมื่อจบการทำงาน
        Should be called when done
        """
        print("กำลังปิด LEDManager (Shutting down LEDManager)...")

        # ปิด LED ทั้งหมดก่อน (Turn all LEDs off first)
        self.all_off()

        # Deinitialize แต่ละ LED (Deinitialize each LED)
        if self._red is not None:
            try:
                self._red.deinit()
            except Exception as e:
                print(f"ข้อผิดพลาดปิด LED แดง (Error closing red LED): {e}")
            self._red = None

        if self._green is not None:
            try:
                self._green.deinit()
            except Exception as e:
                print(f"Error closing green LED: {e}")
            self._green = None

        self._initialized = False
        print("LEDManager ปิดแล้ว (LEDManager shut down)")

    def __del__(self):
        """
        Destructor - ทำความสะอาดเมื่อ object ถูกลบ
        Destructor - cleanup when object is deleted
        """
        if self._initialized:
            self.deinit()

    def __repr__(self):
        """แสดงข้อมูล LEDManager (Display LEDManager info)"""
        if not self._initialized:
            return "LEDManager(not initialized)"

        red_state = "ON" if self._red and self._red.is_on else "OFF"
        green_state = "ON" if self._green and self._green.is_on else "OFF"
        return f"LEDManager(red={red_state}, green={green_state})"

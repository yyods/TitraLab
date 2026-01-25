# ==============================================================================
# buttons.py - คลาสจัดการปุ่มกดสำหรับ TitraLab
# (Button Manager Class for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการปุ่มกด 3 ปุ่มพร้อม debounce
# This module manages 3 buttons with debounce functionality
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจปัญหา button bounce และวิธีแก้ไข
#   2. เรียนรู้การใช้ GPIO ในโหมด input-only
#   3. ประยุกต์ใช้ pattern การตรวจจับการกดค้าง
#
# ข้อจำกัดของ GPIO34, 35, 39 (Limitations of GPIO34, 35, 39):
#   - เป็น input-only pins (ใช้เป็น output ไม่ได้)
#   - ไม่มี internal pull-up/pull-down resistors
#   - ต้องใช้ external pull-down resistor (แนะนำ 10K ohm)
#
# ==============================================================================

from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import (
        BUTTON_1, BUTTON_2, BUTTON_3,
        BUTTON_DEBOUNCE_MS, EXIT_HOLD_TIME_SEC
    )
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    BUTTON_1 = 34
    BUTTON_2 = 35
    BUTTON_3 = 39
    BUTTON_DEBOUNCE_MS = 200
    EXIT_HOLD_TIME_SEC = 3


class Button:
    """
    คลาสจัดการปุ่มกดเดี่ยว (Single Button Management Class)

    รองรับ:
        - Debounce เพื่อป้องกันการอ่านค่าผิดพลาด
        - ตรวจจับการกดสั้นและกดค้าง
        - Callback function เมื่อกดปุ่ม

    ปัญหา Button Bounce:
        เมื่อกดปุ่ม หน้าสัมผัสจะสั่นทำให้สัญญาณกระโดด 0-1 หลายครั้ง
        ก่อนจะนิ่ง ทำให้อ่านค่าผิดพลาดว่ากดหลายครั้ง

        แก้ไขโดย: รอเวลา debounce หลังตรวจจับการกดครั้งแรก
        ก่อนยอมรับการกดครั้งถัดไป

    ตัวอย่างการใช้งาน (Usage Example):
        >>> btn = Button(34, name="Select")
        >>> if btn.is_pressed():
        ...     print("Button pressed!")
        >>> if btn.is_held(3):  # กดค้าง 3 วินาที
        ...     print("Button held for 3 seconds!")
    """

    def __init__(self, pin_number, name="Button", debounce_ms=None,
                 active_high=True):
        """
        สร้าง Button object (Create Button object)

        Args:
            pin_number (int): หมายเลข GPIO (GPIO pin number)
            name (str): ชื่อปุ่มสำหรับแสดงข้อความ (button name for display)
            debounce_ms (int): เวลา debounce มิลลิวินาที (debounce time in ms)
            active_high (bool): True ถ้าปุ่มกดแล้วเป็น HIGH
                               (True if pressed = HIGH)
                               สำหรับ TitraLab ใช้ external pull-down
                               ดังนั้น active_high=True (กดแล้ว = 1)
        """
        self._pin_number = pin_number
        self._name = name
        self._debounce_ms = debounce_ms if debounce_ms else BUTTON_DEBOUNCE_MS
        self._active_high = active_high

        # สร้าง Pin object (Create Pin object)
        # หมายเหตุ: GPIO34, 35, 39 เป็น input-only ไม่รองรับ pull-up/down
        # Note: GPIO34, 35, 39 are input-only, no internal pull-up/down
        self._pin = Pin(pin_number, Pin.IN)

        # ตัวแปรสถานะ (State variables)
        self._last_press_time = 0
        self._press_start_time = 0
        self._is_pressed_flag = False
        self._was_pressed = False

        print(f"ปุ่ม '{name}' พร้อมใช้งานที่ GPIO{pin_number} "
              f"(Button '{name}' ready on GPIO{pin_number})")

    @property
    def name(self):
        """ชื่อปุ่ม (Button name)"""
        return self._name

    @property
    def pin_number(self):
        """หมายเลข GPIO (GPIO pin number)"""
        return self._pin_number

    def raw_value(self):
        """
        อ่านค่าดิบจากปุ่ม (Read raw value from button)

        Returns:
            int: 0 หรือ 1 (0 or 1)
        """
        return self._pin.value()

    def is_active(self):
        """
        ตรวจสอบว่าปุ่มถูกกดอยู่หรือไม่ (ไม่มี debounce)
        Check if button is currently pressed (no debounce)

        Returns:
            bool: True ถ้าปุ่มถูกกดอยู่ (if button is pressed)
        """
        value = self._pin.value()
        if self._active_high:
            return value == 1
        else:
            return value == 0

    def is_pressed(self):
        """
        ตรวจจับการกดปุ่มพร้อม debounce (Detect button press with debounce)

        ฟังก์ชันนี้จะคืน True เพียงครั้งเดียวต่อการกดหนึ่งครั้ง
        This function returns True only once per press

        Returns:
            bool: True ถ้าตรวจจับการกดปุ่มใหม่ (if new press detected)
        """
        current_time = ticks_ms()
        is_active = self.is_active()

        # ตรวจสอบการกดใหม่ (Check for new press)
        if is_active and not self._was_pressed:
            # ตรวจสอบ debounce (Check debounce)
            if ticks_diff(current_time, self._last_press_time) > self._debounce_ms:
                self._last_press_time = current_time
                self._press_start_time = current_time
                self._was_pressed = True
                return True

        # รีเซ็ตเมื่อปล่อยปุ่ม (Reset when button released)
        if not is_active:
            self._was_pressed = False

        return False

    def wait_for_release(self, timeout_ms=5000):
        """
        รอจนกว่าปุ่มจะถูกปล่อย (Wait until button is released)

        Args:
            timeout_ms (int): เวลา timeout มิลลิวินาที (timeout in ms)

        Returns:
            bool: True ถ้าปุ่มถูกปล่อย, False ถ้า timeout
                  (True if released, False if timeout)
        """
        start_time = ticks_ms()

        while self.is_active():
            if ticks_diff(ticks_ms(), start_time) > timeout_ms:
                return False
            sleep_ms(10)

        return True

    def is_held(self, seconds):
        """
        ตรวจสอบว่าปุ่มถูกกดค้างตามเวลาที่กำหนด
        Check if button is held for specified duration

        Args:
            seconds (float): เวลาที่ต้องกดค้าง (hold duration in seconds)

        Returns:
            bool: True ถ้าถูกกดค้างครบเวลา (if held for specified time)
        """
        if not self.is_active():
            self._press_start_time = 0
            return False

        # บันทึกเวลาเริ่มกด (Record press start time)
        if self._press_start_time == 0:
            self._press_start_time = ticks_ms()

        # ตรวจสอบเวลาที่กดค้าง (Check hold duration)
        held_time_ms = ticks_diff(ticks_ms(), self._press_start_time)
        return held_time_ms >= (seconds * 1000)

    def get_hold_time(self):
        """
        อ่านเวลาที่ปุ่มถูกกดค้าง (Get button hold time)

        Returns:
            float: เวลาที่กดค้างเป็นวินาที (hold time in seconds)
                   คืน 0 ถ้าปุ่มไม่ได้ถูกกด
        """
        if not self.is_active() or self._press_start_time == 0:
            return 0

        return ticks_diff(ticks_ms(), self._press_start_time) / 1000

    def wait_for_press(self, timeout_ms=None):
        """
        รอจนกว่าปุ่มจะถูกกด (Wait until button is pressed)

        Args:
            timeout_ms (int): เวลา timeout มิลลิวินาที (timeout in ms)
                              None = รอไม่มีกำหนด (wait indefinitely)

        Returns:
            bool: True ถ้าปุ่มถูกกด, False ถ้า timeout
                  (True if pressed, False if timeout)
        """
        start_time = ticks_ms()

        while True:
            if self.is_pressed():
                return True

            if timeout_ms is not None:
                if ticks_diff(ticks_ms(), start_time) > timeout_ms:
                    return False

            sleep_ms(10)

    def __repr__(self):
        """แสดงข้อมูลปุ่ม (Display button info)"""
        return f"Button('{self._name}', pin={self._pin_number})"


class ButtonManager:
    """
    คลาสจัดการปุ่มทั้ง 3 ปุ่มสำหรับ TitraLab
    (Button Manager Class for all 3 TitraLab buttons)

    ปุ่มและหน้าที่:
        - Button 1 (GPIO34): เลือก/ยืนยัน (Select/Confirm)
        - Button 2 (GPIO35): เลื่อนเมนู (Navigate)
        - Button 3 (GPIO39): ย้อนกลับ/ออก (Back/Exit - hold 3 sec)

    ตัวอย่างการใช้งาน (Usage Example):
        >>> buttons = ButtonManager()
        >>> while True:
        ...     if buttons.select.is_pressed():
        ...         print("Select pressed!")
        ...     if buttons.navigate.is_pressed():
        ...         print("Navigate pressed!")
        ...     if buttons.is_exit_held():
        ...         print("Exit!")
        ...         break
    """

    def __init__(self, btn1_pin=None, btn2_pin=None, btn3_pin=None,
                 debounce_ms=None):
        """
        สร้าง ButtonManager (Create ButtonManager)

        Args:
            btn1_pin (int): GPIO สำหรับปุ่ม 1 (GPIO for button 1)
            btn2_pin (int): GPIO สำหรับปุ่ม 2 (GPIO for button 2)
            btn3_pin (int): GPIO สำหรับปุ่ม 3 (GPIO for button 3)
            debounce_ms (int): เวลา debounce (debounce time in ms)
        """
        # กำหนดค่าเริ่มต้น (Set defaults)
        btn1 = btn1_pin if btn1_pin is not None else BUTTON_1
        btn2 = btn2_pin if btn2_pin is not None else BUTTON_2
        btn3 = btn3_pin if btn3_pin is not None else BUTTON_3
        debounce = debounce_ms if debounce_ms is not None else BUTTON_DEBOUNCE_MS

        # สร้างปุ่มทั้ง 3 (Create all 3 buttons)
        self._button1 = Button(btn1, "Select", debounce)
        self._button2 = Button(btn2, "Navigate", debounce)
        self._button3 = Button(btn3, "Back", debounce)

        # เวลาสำหรับการกดค้างเพื่อออก (Hold time for exit)
        self._exit_hold_time = EXIT_HOLD_TIME_SEC

        print("ButtonManager พร้อมใช้งาน (ButtonManager ready)")

    def init(self):
        """
        เริ่มต้น ButtonManager (Initialize ButtonManager)

        เมธอดนี้ถูกเรียกโดย HardwareHub - ปุ่มพร้อมใช้งานตั้งแต่สร้าง object
        This method is called by HardwareHub - buttons are ready from object creation.
        """
        pass  # ปุ่มพร้อมใช้งานตั้งแต่ __init__ (Buttons ready from __init__)

    def deinit(self):
        """
        ปิด ButtonManager (Deinitialize ButtonManager)

        เมธอดนี้ถูกเรียกเมื่อปิดโปรแกรม
        This method is called on shutdown.
        """
        pass  # ไม่มี resources ที่ต้อง cleanup (No resources to cleanup)

    @property
    def select(self):
        """ปุ่ม 1 - เลือก/ยืนยัน (Button 1 - Select/Confirm)"""
        return self._button1

    @property
    def navigate(self):
        """ปุ่ม 2 - เลื่อนเมนู (Button 2 - Navigate)"""
        return self._button2

    @property
    def back(self):
        """ปุ่ม 3 - ย้อนกลับ (Button 3 - Back)"""
        return self._button3

    # Aliases สำหรับความเข้ากันได้ (Aliases for compatibility)
    @property
    def button1(self):
        """Alias for select button"""
        return self._button1

    @property
    def button2(self):
        """Alias for navigate button"""
        return self._button2

    @property
    def button3(self):
        """Alias for back button"""
        return self._button3

    def is_exit_held(self):
        """
        ตรวจสอบว่าปุ่ม Back ถูกกดค้าง 3 วินาทีหรือไม่
        Check if Back button is held for 3 seconds

        Returns:
            bool: True ถ้าถูกกดค้างครบ 3 วินาที
                  (True if held for 3 seconds)
        """
        return self._button3.is_held(self._exit_hold_time)

    def check_exit_with_countdown(self, callback=None):
        """
        ตรวจสอบการกดค้างปุ่ม Back พร้อมแสดง countdown
        Check Back button hold with countdown display

        Args:
            callback (function): ฟังก์ชันเรียกเมื่อนับถอยหลัง
                                 รับ parameter เป็นวินาทีที่เหลือ
                                 (Called during countdown with remaining seconds)

        Returns:
            bool: True ถ้ากดค้างครบ 3 วินาที (if held for 3 seconds)
        """
        if not self._button3.is_active():
            return False

        # เริ่มนับเวลา (Start counting)
        hold_count = 0
        while self._button3.is_active():
            hold_count += 1
            if callback:
                remaining = self._exit_hold_time - hold_count
                callback(remaining)

            if hold_count >= self._exit_hold_time:
                return True

            sleep_ms(1000)

        return False

    def wait_for_any_press(self, timeout_ms=None):
        """
        รอจนกว่าปุ่มใดปุ่มหนึ่งจะถูกกด
        Wait until any button is pressed

        Args:
            timeout_ms (int): เวลา timeout (timeout in ms)
                              None = รอไม่มีกำหนด

        Returns:
            int: หมายเลขปุ่มที่ถูกกด (1, 2, 3) หรือ 0 ถ้า timeout
                 (button number pressed or 0 if timeout)
        """
        start_time = ticks_ms()

        while True:
            if self._button1.is_pressed():
                return 1
            if self._button2.is_pressed():
                return 2
            if self._button3.is_pressed():
                return 3

            if timeout_ms is not None:
                if ticks_diff(ticks_ms(), start_time) > timeout_ms:
                    return 0

            sleep_ms(10)

    def get_navigation_delta(self):
        """
        อ่านการเคลื่อนที่ในเมนู (Get menu navigation delta)

        ใช้สำหรับเมนูที่ต้องเลื่อนขึ้น-ลง
        Used for up-down menu navigation

        Returns:
            int: 1 ถ้ากดปุ่ม Navigate (เลื่อนลง)
                 0 ถ้าไม่มีการกด
                 (1 if Navigate pressed, 0 if no press)
        """
        if self._button2.is_pressed():
            return 1
        return 0

    def is_pressed(self, button_number):
        """
        ตรวจสอบว่าปุ่มที่ระบุถูกกดหรือไม่ (Check if specified button is pressed)

        Args:
            button_number (int): หมายเลขปุ่ม 1, 2, หรือ 3
                                 (Button number: 1=Select, 2=Navigate, 3=Back)

        Returns:
            bool: True ถ้าปุ่มถูกกด (True if button is pressed)
        """
        if button_number == 1:
            return self._button1.is_pressed()
        elif button_number == 2:
            return self._button2.is_pressed()
        elif button_number == 3:
            return self._button3.is_pressed()
        return False

    def update(self):
        """
        อัพเดตสถานะปุ่มทั้งหมด (Update all button states)

        เรียกฟังก์ชันนี้ใน main loop เพื่ออัพเดตสถานะ
        Call this in main loop to update states
        """
        # อ่านค่าเพื่ออัพเดต internal state
        # Read values to update internal state
        _ = self._button1.is_active()
        _ = self._button2.is_active()
        _ = self._button3.is_active()

    def __repr__(self):
        """แสดงข้อมูล ButtonManager"""
        return (f"ButtonManager(select=GPIO{self._button1.pin_number}, "
                f"navigate=GPIO{self._button2.pin_number}, "
                f"back=GPIO{self._button3.pin_number})")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ ButtonManager (Testing ButtonManager)")
    print("=" * 50)
    print("ปุ่ม 1: เลือก (Select)")
    print("ปุ่ม 2: เลื่อน (Navigate)")
    print("ปุ่ม 3: ออก - กดค้าง 3 วินาที (Exit - hold 3 sec)")
    print("=" * 50)

    # สร้าง ButtonManager (Create ButtonManager)
    buttons = ButtonManager()
    print(buttons)

    menu_index = 0
    menu_items = ["Option A", "Option B", "Option C", "Option D"]

    try:
        while True:
            # ตรวจสอบปุ่ม Select (Check Select button)
            if buttons.select.is_pressed():
                print(f"เลือก: {menu_items[menu_index]} (Selected: {menu_items[menu_index]})")

            # ตรวจสอบปุ่ม Navigate (Check Navigate button)
            if buttons.navigate.is_pressed():
                menu_index = (menu_index + 1) % len(menu_items)
                print(f"เลื่อนไป: {menu_items[menu_index]} (Navigate to: {menu_items[menu_index]})")

            # ตรวจสอบการกดค้างปุ่ม Back (Check Back button hold)
            if buttons.back.is_active():
                hold_time = buttons.back.get_hold_time()
                if hold_time > 0:
                    print(f"กดค้าง: {hold_time:.1f} วินาที (Holding: {hold_time:.1f} sec)")

                if buttons.is_exit_held():
                    print("ออกจากโปรแกรม (Exiting program)")
                    break

            sleep_ms(100)

    except KeyboardInterrupt:
        print("\nหยุดโดยผู้ใช้ (Stopped by user)")

    print("เสร็จสิ้น (Done)")

# ==============================================================================
# base_mode.py - คลาสพื้นฐานสำหรับทุกโหมด (Base Class for All Modes)
# ==============================================================================
# โมดูลนี้กำหนดคลาสพื้นฐาน (Abstract Base Class) ที่ทุกโหมดต้อง inherit
# This module defines the Abstract Base Class that all modes must inherit
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้ Abstract Base Class (ABC) และ interface design
# 2. เข้าใจ lifecycle methods (on_enter, on_exit, update)
# 3. ฝึกการออกแบบ API ที่สอดคล้องกัน (Consistent API design)
#
# Lifecycle ของโหมด (Mode Lifecycle):
# 1. on_enter() - เรียกเมื่อเข้าโหมด (Called when entering mode)
# 2. update() - เรียกทุก loop iteration (Called every loop iteration)
# 3. is_complete() - ตรวจสอบว่าโหมดเสร็จสิ้นหรือยัง (Check if mode is complete)
# 4. on_exit() - เรียกเมื่อออกจากโหมด (Called when exiting mode)
# ==============================================================================

from time import ticks_ms, ticks_diff, sleep_ms
from machine import Pin


# ==============================================================================
# คลาส BaseMode - คลาสพื้นฐานสำหรับทุกโหมด
# BaseMode Class - Base class for all modes
# ==============================================================================
class BaseMode:
    """
    คลาสพื้นฐานสำหรับทุกโหมด (Abstract Base Class for all modes)

    คลาสนี้กำหนด interface และ lifecycle ที่ทุกโหมดต้องปฏิบัติตาม
    This class defines the interface and lifecycle all modes must follow

    Attributes:
        display: ออบเจ็กต์ Display (Display object)
        colors: คลาส Colors (Colors class)
        name (str): ชื่อโหมด (Mode name)
        is_running (bool): สถานะการทำงาน (Running state)
        _complete (bool): สถานะเสร็จสิ้น (Completion state)
        _results (dict): ผลลัพธ์จากโหมด (Results from mode)

    Example:
        class MyMode(BaseMode):
            def __init__(self, display, colors):
                super().__init__(display, colors, "My Mode")

            def on_enter(self):
                self.display.clear()
                self.display.draw_header(self.name)

            def update(self):
                # ทำงานโหมด (Do mode work)
                pass

            def on_exit(self):
                # ทำความสะอาด (Cleanup)
                pass
    """

    # ค่าคงที่ขาปุ่ม (Button Pin Constants)
    PIN_SELECT = 34
    PIN_UP     = 35
    PIN_DOWN   = 39

    def __init__(self, display, colors, name="Base Mode"):
        """
        สร้างออบเจ็กต์ BaseMode (Create BaseMode object)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            colors: คลาส Colors (Colors class)
            name (str): ชื่อโหมด (Mode name)
        """
        self.display = display
        self.colors = colors
        self.name = name

        # สถานะโหมด (Mode state)
        self.is_running = False
        self._complete = False
        self._results = {}

        # ปุ่มกด (Buttons)
        self._btn_select = Pin(self.PIN_SELECT, Pin.IN)
        self._btn_up = Pin(self.PIN_UP, Pin.IN)
        self._btn_down = Pin(self.PIN_DOWN, Pin.IN)

        # เวลาเริ่มต้น (Start time)
        self._start_time = 0

        # Debounce
        self._last_button_time = 0
        self._debounce_ms = 200

    # ==========================================================================
    # Lifecycle Methods - ต้อง override ในคลาสลูก
    # ==========================================================================

    def on_enter(self):
        """
        เรียกเมื่อเข้าโหมด (Called when entering mode)

        เมธอดนี้ควร:
        - ตั้งค่าเริ่มต้น (Initialize settings)
        - แสดงหน้าจอเริ่มต้น (Display initial screen)
        - เตรียมฮาร์ดแวร์ (Prepare hardware)

        Must override in subclass.
        """
        self.is_running = True
        self._complete = False
        self._results = {}
        self._start_time = ticks_ms()
        print(f"เข้าโหมด: {self.name} (Entering mode: {self.name})")

    def update(self):
        """
        เรียกทุก loop iteration (Called every loop iteration)

        เมธอดนี้ควร:
        - ตรวจสอบ input (Check input)
        - อัปเดตสถานะ (Update state)
        - อัปเดตหน้าจอ (Update display)

        Must override in subclass.
        """
        raise NotImplementedError("คลาสลูกต้อง implement update() (Subclass must implement update())")

    def on_exit(self):
        """
        เรียกเมื่อออกจากโหมด (Called when exiting mode)

        เมธอดนี้ควร:
        - ทำความสะอาดทรัพยากร (Clean up resources)
        - หยุดฮาร์ดแวร์ (Stop hardware)
        - บันทึกข้อมูลถ้าจำเป็น (Save data if needed)

        Must override in subclass.
        """
        self.is_running = False
        print(f"ออกจากโหมด: {self.name} (Exiting mode: {self.name})")

    # ==========================================================================
    # State Methods
    # ==========================================================================

    def is_complete(self):
        """
        ตรวจสอบว่าโหมดเสร็จสิ้นหรือยัง (Check if mode is complete)

        Returns:
            bool: True ถ้าโหมดเสร็จสิ้น (True if mode is complete)
        """
        return self._complete

    def set_complete(self, complete=True):
        """
        ตั้งค่าสถานะเสร็จสิ้น (Set completion state)

        Args:
            complete (bool): สถานะเสร็จสิ้น (Completion state)
        """
        self._complete = complete

    def get_results(self):
        """
        รับผลลัพธ์จากโหมด (Get results from mode)

        Returns:
            dict: ผลลัพธ์ (Results dictionary)
        """
        return self._results

    def set_results(self, **kwargs):
        """
        ตั้งค่าผลลัพธ์ (Set results)

        Args:
            **kwargs: ผลลัพธ์เป็น key-value pairs
        """
        self._results.update(kwargs)

    # ==========================================================================
    # Helper Methods - ใช้ได้ในคลาสลูก
    # ==========================================================================

    def get_elapsed_time(self):
        """
        รับเวลาที่ผ่านไปตั้งแต่เริ่มโหมด (Get elapsed time since mode start)

        Returns:
            int: เวลาในวินาที (Time in seconds)
        """
        if self._start_time == 0:
            return 0
        return ticks_diff(ticks_ms(), self._start_time) // 1000

    def wait_button_press(self, button_name='select', timeout_ms=None):
        """
        รอการกดปุ่ม (Wait for button press)

        Args:
            button_name (str): 'select', 'up', 'down'
            timeout_ms (int): timeout ใน ms หรือ None ไม่มี timeout

        Returns:
            bool: True ถ้ากดปุ่ม, False ถ้า timeout (True if pressed, False if timeout)
        """
        button = self._get_button(button_name)
        if button is None:
            return False

        start = ticks_ms()
        while True:
            if button.value() == 1:
                self._wait_release(button)
                return True

            if timeout_ms and ticks_diff(ticks_ms(), start) >= timeout_ms:
                return False

            sleep_ms(10)

    def check_button(self, button_name='select'):
        """
        ตรวจสอบปุ่มพร้อม debounce (Check button with debounce)

        Args:
            button_name (str): 'select', 'up', 'down'

        Returns:
            bool: True ถ้ากดปุ่ม (True if pressed)
        """
        button = self._get_button(button_name)
        if button is None:
            return False

        current_time = ticks_ms()
        if button.value() == 1:
            if ticks_diff(current_time, self._last_button_time) >= self._debounce_ms:
                self._last_button_time = current_time
                return True
        return False

    def _get_button(self, button_name):
        """
        รับออบเจ็กต์ปุ่มตามชื่อ (Get button object by name)

        Args:
            button_name (str): ชื่อปุ่ม (Button name)

        Returns:
            Pin or None: ออบเจ็กต์ Pin หรือ None
        """
        buttons = {
            'select': self._btn_select,
            'up': self._btn_up,
            'down': self._btn_down
        }
        return buttons.get(button_name)

    def _wait_release(self, button):
        """
        รอจนกว่าปุ่มจะถูกปล่อย (Wait for button release)

        Args:
            button: ออบเจ็กต์ Pin (Pin object)
        """
        while button.value() == 1:
            sleep_ms(10)

    def show_countdown(self, seconds, message="Starting in"):
        """
        แสดงการนับถอยหลัง (Display countdown)

        Args:
            seconds (int): จำนวนวินาที (Number of seconds)
            message (str): ข้อความ (Message)
        """
        for i in range(seconds, 0, -1):
            self.display.fill_rect(0, 100, self.display.width, 30, self.colors.BLACK)
            self.display.draw_text_centered(100, f"{message} {i}s", self.colors.YELLOW)
            sleep_ms(1000)

    def show_instruction(self, title, message, wait_button=True):
        """
        แสดงคำแนะนำและรอการกดปุ่ม (Display instruction and wait for button)

        Args:
            title (str): หัวข้อ (Title)
            message (str): ข้อความ (Message)
            wait_button (bool): รอปุ่มหรือไม่ (Wait for button or not)

        Returns:
            bool: True ถ้ากดปุ่ม (True if button pressed)
        """
        self.display.clear()
        self.display.draw_header(title)
        self.display.draw_text_centered(80, message, self.colors.WHITE)
        self.display.draw_status_bar("Press SELECT to continue", self.colors.TEXT_INFO)

        if wait_button:
            return self.wait_button_press('select')
        return True


# ==============================================================================
# ตัวอย่างการ implement (Implementation Example)
# ==============================================================================
class ExampleMode(BaseMode):
    """
    ตัวอย่างการ implement BaseMode (Example BaseMode implementation)

    นี่คือตัวอย่างโหมดง่ายๆ ที่แสดงการใช้งาน lifecycle methods
    This is a simple example mode showing lifecycle methods usage
    """

    def __init__(self, display, colors):
        super().__init__(display, colors, "Example Mode")
        self.counter = 0

    def on_enter(self):
        super().on_enter()
        self.counter = 0
        self.display.clear()
        self.display.draw_header(self.name)
        self.display.draw_text(20, 60, "Counter: 0", self.colors.WHITE)
        self.display.draw_status_bar("Press SELECT to increment")

    def update(self):
        if self.check_button('select'):
            self.counter += 1
            self.display.fill_rect(100, 60, 100, 24, self.colors.BLACK)
            self.display.draw_text(100, 60, str(self.counter), self.colors.GREEN)

            # เสร็จสิ้นเมื่อนับถึง 10 (Complete when count reaches 10)
            if self.counter >= 10:
                self.set_results(final_count=self.counter)
                self.set_complete()

        # ตรวจสอบปุ่ม DOWN เพื่อยกเลิก (Check DOWN to cancel)
        if self.check_button('down'):
            self.set_complete()

    def on_exit(self):
        super().on_exit()
        print(f"Final counter: {self.counter}")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("BaseMode Module")
    print("===============")
    print("This module provides the abstract base class for all operation modes.")
    print("")
    print("Lifecycle methods:")
    print("1. on_enter() - Called when entering mode")
    print("2. update() - Called every loop iteration")
    print("3. is_complete() - Check if mode is complete")
    print("4. on_exit() - Called when exiting mode")
    print("")
    print("Helper methods:")
    print("- wait_button_press(button_name, timeout_ms)")
    print("- check_button(button_name)")
    print("- show_countdown(seconds, message)")
    print("- show_instruction(title, message, wait_button)")
    print("- get_elapsed_time()")
    print("- get_results() / set_results(**kwargs)")

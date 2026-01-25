# ==============================================================================
# menu.py - ระบบเมนูและ State Machine (Menu System and State Machine)
# ==============================================================================
# โมดูลนี้จัดการการนำทางเมนูและสถานะของแอปพลิเคชัน
# This module handles menu navigation and application state
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การออกแบบ State Machine (State Machine Design)
# 2. เข้าใจการจัดการ Input จากปุ่ม (Button Input Handling)
# 3. ฝึกการสร้างระบบนำทางแบบ modular (Modular Navigation System)
#
# State Machine:
# - MAIN_MENU: หน้าเมนูหลัก (Main menu)
# - MODE_RUNNING: กำลังทำงานในโหมดที่เลือก (Running selected mode)
# - RESULT_DISPLAY: แสดงผลลัพธ์ (Displaying results)
#
# การเชื่อมต่อปุ่ม (Button Connections):
# - UP:     GPIO35 (Button 2)
# - DOWN:   GPIO39 (Button 3)
# - SELECT: GPIO34 (Button 1)
# ==============================================================================

from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms


# ==============================================================================
# Enum สำหรับสถานะเมนู (Menu State Enum)
# ==============================================================================
class MenuState:
    """
    สถานะของระบบเมนู (Menu System States)

    ใช้แทน enum เนื่องจาก MicroPython ไม่มี enum built-in
    Used instead of enum as MicroPython doesn't have built-in enum

    Attributes:
        MAIN_MENU (int): หน้าเมนูหลัก
        MODE_RUNNING (int): กำลังทำงานในโหมด
        RESULT_DISPLAY (int): แสดงผลลัพธ์
    """
    MAIN_MENU = 0
    MODE_RUNNING = 1
    RESULT_DISPLAY = 2

    @staticmethod
    def name(state):
        """
        รับชื่อสถานะ (Get state name)

        Args:
            state (int): รหัสสถานะ (State code)

        Returns:
            str: ชื่อสถานะ (State name)
        """
        names = {
            0: 'MAIN_MENU',
            1: 'MODE_RUNNING',
            2: 'RESULT_DISPLAY'
        }
        return names.get(state, 'UNKNOWN')


# ==============================================================================
# คลาส ButtonHandler - จัดการปุ่มกด
# ButtonHandler Class - Button Press Handler
# ==============================================================================
class ButtonHandler:
    """
    คลาสจัดการปุ่มกดพร้อม debounce (Button handler with debounce)

    จัดการการกดปุ่มหลายปุ่มพร้อมกันและป้องกันการกดซ้ำ
    Handles multiple button presses and prevents repeated triggers

    Attributes:
        buttons (dict): พจนานุกรมปุ่ม {name: Pin}
        debounce_ms (int): เวลา debounce มิลลิวินาที
    """

    # ค่าคงที่ขา GPIO (GPIO Pin Constants)
    PIN_SELECT = 34  # Button 1 - Select/Confirm
    PIN_UP     = 35  # Button 2 - Up/Previous
    PIN_DOWN   = 39  # Button 3 - Down/Next

    def __init__(self, debounce_ms=200):
        """
        สร้าง ButtonHandler (Create ButtonHandler)

        Args:
            debounce_ms (int): เวลา debounce (ms)

        Note:
            GPIO 34, 35, 39 เป็น input-only ไม่มี internal pull-up/down
            GPIO 34, 35, 39 are input-only without internal pull-up/down
            ต้องใช้ external pull-down resistor
            Must use external pull-down resistor
        """
        # กำหนดขาปุ่ม (Define button pins)
        self.buttons = {
            'select': Pin(self.PIN_SELECT, Pin.IN),
            'up': Pin(self.PIN_UP, Pin.IN),
            'down': Pin(self.PIN_DOWN, Pin.IN)
        }

        self.debounce_ms = debounce_ms

        # เก็บเวลากดล่าสุดของแต่ละปุ่ม (Store last press time for each button)
        self._last_press = {name: 0 for name in self.buttons}

        # สถานะการกดค้าง (Long press state)
        self._press_start = {name: 0 for name in self.buttons}
        self._was_pressed = {name: False for name in self.buttons}

    def is_pressed(self, button_name):
        """
        ตรวจสอบว่าปุ่มถูกกดหรือไม่ (พร้อม debounce)
        Check if button is pressed (with debounce)

        Args:
            button_name (str): ชื่อปุ่ม 'select', 'up', 'down'

        Returns:
            bool: True ถ้าปุ่มถูกกด (True if button pressed)
        """
        if button_name not in self.buttons:
            return False

        button = self.buttons[button_name]
        current_time = ticks_ms()

        # ตรวจสอบสถานะปุ่ม (HIGH = pressed with pull-down)
        # Check button state (HIGH = pressed with pull-down)
        if button.value() == 1:
            # ตรวจสอบ debounce (Check debounce)
            if ticks_diff(current_time, self._last_press[button_name]) >= self.debounce_ms:
                self._last_press[button_name] = current_time
                return True

        return False

    def wait_release(self, button_name):
        """
        รอจนกว่าปุ่มจะถูกปล่อย (Wait until button is released)

        Args:
            button_name (str): ชื่อปุ่ม (Button name)
        """
        if button_name not in self.buttons:
            return

        button = self.buttons[button_name]
        while button.value() == 1:
            sleep_ms(10)

    def is_long_pressed(self, button_name, duration_ms=3000):
        """
        ตรวจสอบการกดค้าง (Check for long press)

        Args:
            button_name (str): ชื่อปุ่ม (Button name)
            duration_ms (int): ระยะเวลากดค้าง (Long press duration)

        Returns:
            bool: True ถ้ากดค้างนานพอ (True if pressed long enough)
        """
        if button_name not in self.buttons:
            return False

        button = self.buttons[button_name]
        current_time = ticks_ms()

        if button.value() == 1:
            # เริ่มนับเวลาถ้ายังไม่ได้เริ่ม (Start counting if not started)
            if not self._was_pressed[button_name]:
                self._press_start[button_name] = current_time
                self._was_pressed[button_name] = True

            # ตรวจสอบระยะเวลา (Check duration)
            if ticks_diff(current_time, self._press_start[button_name]) >= duration_ms:
                return True
        else:
            # รีเซ็ตเมื่อปล่อยปุ่ม (Reset when button released)
            self._was_pressed[button_name] = False
            self._press_start[button_name] = 0

        return False

    def get_any_pressed(self):
        """
        รับปุ่มที่ถูกกด (Get any pressed button)

        Returns:
            str or None: ชื่อปุ่มที่กด หรือ None (Pressed button name or None)
        """
        for name in self.buttons:
            if self.is_pressed(name):
                return name
        return None


# ==============================================================================
# คลาส MenuSystem - ระบบเมนูหลัก
# MenuSystem Class - Main Menu System
# ==============================================================================
class MenuSystem:
    """
    ระบบเมนูพร้อม State Machine (Menu System with State Machine)

    จัดการการนำทางระหว่างหน้าจอและโหมดต่างๆ
    Manages navigation between screens and modes

    Attributes:
        state (int): สถานะปัจจุบัน (Current state)
        selected_mode (int): โหมดที่เลือก (Selected mode)
        modes (list): รายการโหมด (List of modes)
    """

    # รายการเมนู TitraLab (TitraLab menu items)
    MENU_ITEMS = [
        "1. Calibrate pH",
        "2. Test pH Sensor",
        "3. Calibrate Flow",
        "4. Test Flow Rate",
        "5. Purge Tubing",
        "6. Auto Titration"
    ]

    def __init__(self, display, buttons=None, screen_main_menu=None, modes=None, buzzer=None):
        """
        สร้าง MenuSystem (Create MenuSystem)

        Args:
            display: ออบเจ็กต์ Display (Display object)
            buttons: ออบเจ็กต์ ButtonManager (ButtonManager object)
            screen_main_menu: ออบเจ็กต์ MainMenuScreen (optional, MainMenuScreen object)
            modes (list): รายการออบเจ็กต์ BaseMode (List of BaseMode objects)
            buzzer: ออบเจ็กต์ Buzzer สำหรับเสียง (Buzzer object for sound)
        """
        self.display = display
        self.hw_buttons = buttons  # ButtonManager from hardware
        self.main_menu_screen = screen_main_menu
        self.modes = modes if modes else []
        self.buzzer = buzzer

        # Simple menu state (สถานะเมนูแบบง่าย)
        self._selected_index = 0
        self._menu_items = self.MENU_ITEMS.copy()

        # State Machine (ใช้สำหรับ advanced mode)
        self.state = MenuState.MAIN_MENU
        self.previous_state = None
        self.selected_mode = 0
        self.current_mode = None

        # Button Handler (ใช้สำหรับ advanced mode)
        self.buttons = ButtonHandler()

        # ผลลัพธ์จากโหมด (Results from mode)
        self.last_results = None

        # สถานะการทำงาน (Running flag)
        self._running = True

    # ==========================================================================
    # Simple API (ใช้โดย main.py)
    # ==========================================================================

    def show(self):
        """
        แสดงเมนูบนจอ TFT (Display menu on TFT screen)

        แสดงรายการเมนูพร้อมไฮไลท์รายการที่เลือก
        Shows menu items with highlighted selection
        """
        try:
            # ล้างจอและวาดหัวข้อ (Clear and draw header)
            self.display.clear()
            self.display.draw_header("TitraLab Menu")

            # วาดรายการเมนู (Draw menu items)
            y_start = 50
            line_height = 28

            for i, item in enumerate(self._menu_items):
                y = y_start + (i * line_height)

                # ไฮไลท์รายการที่เลือก (Highlight selected item)
                if i == self._selected_index:
                    # วาดพื้นหลังไฮไลท์ (Draw highlight background)
                    self.display.fill_rect(5, y - 2, 310, line_height, 0x001F)  # Blue
                    self.display.draw_text(10, y, f"> {item}", 0xFFFF)  # White text
                else:
                    self.display.draw_text(10, y, f"  {item}", 0xFFFF)  # White text

            # แสดงคำแนะนำ (Show instructions)
            self.display.draw_status_bar("BTN1:Select BTN2:Up BTN3:Down/Exit")

        except Exception as e:
            print(f"Menu display error: {e}")

    def get_selected(self):
        """
        รับหมายเลขเมนูที่เลือก (Get selected menu number)

        Returns:
            int: หมายเลขเมนู 1-6 (Menu number 1-6)
        """
        return self._selected_index + 1  # Convert 0-based to 1-based

    def move_up(self):
        """
        เลื่อนขึ้น (Move selection up)
        """
        if self._selected_index > 0:
            self._selected_index -= 1
        else:
            # วนกลับไปรายการสุดท้าย (Wrap to last item)
            self._selected_index = len(self._menu_items) - 1

    def move_down(self):
        """
        เลื่อนลง (Move selection down)
        """
        if self._selected_index < len(self._menu_items) - 1:
            self._selected_index += 1
        else:
            # วนกลับไปรายการแรก (Wrap to first item)
            self._selected_index = 0

    def _beep(self):
        """
        เล่นเสียงบี๊ปสั้น (Play short beep)
        """
        if self.buzzer:
            try:
                self.buzzer.beep()
            except:
                pass  # ข้ามถ้าไม่มี buzzer (Skip if no buzzer)

    def set_state(self, new_state):
        """
        เปลี่ยนสถานะ (Change state)

        Args:
            new_state (int): สถานะใหม่จาก MenuState (New state from MenuState)
        """
        self.previous_state = self.state
        self.state = new_state
        print(f"State changed: {MenuState.name(self.previous_state)} -> {MenuState.name(new_state)}")

    def handle_main_menu(self):
        """
        จัดการสถานะ MAIN_MENU (Handle MAIN_MENU state)

        ตรวจสอบการกดปุ่มและอัปเดตเมนู
        Check button presses and update menu
        """
        # ตรวจสอบปุ่ม UP (Check UP button)
        if self.buttons.is_pressed('up'):
            self._beep()
            self.main_menu_screen.select_previous()
            self.buttons.wait_release('up')

        # ตรวจสอบปุ่ม DOWN (Check DOWN button)
        elif self.buttons.is_pressed('down'):
            self._beep()
            self.main_menu_screen.select_next()
            self.buttons.wait_release('down')

        # ตรวจสอบปุ่ม SELECT (Check SELECT button)
        elif self.buttons.is_pressed('select'):
            self._beep()
            self.selected_mode = self.main_menu_screen.get_selected()
            self.buttons.wait_release('select')

            # เริ่มโหมดที่เลือก (Start selected mode)
            if self.selected_mode < len(self.modes):
                self._start_mode(self.selected_mode)

    def _start_mode(self, mode_index):
        """
        เริ่มโหมดที่เลือก (Start selected mode)

        Args:
            mode_index (int): ดัชนีโหมด (Mode index)
        """
        if mode_index >= len(self.modes):
            print(f"ข้อผิดพลาด: ไม่พบโหมด {mode_index} (Error: Mode {mode_index} not found)")
            return

        self.current_mode = self.modes[mode_index]

        # เรียก on_enter ของโหมด (Call mode's on_enter)
        try:
            self.current_mode.on_enter()
            self.set_state(MenuState.MODE_RUNNING)
        except Exception as e:
            print(f"ข้อผิดพลาดเริ่มโหมด (Error starting mode): {e}")
            self.display.show_error(str(e))
            sleep_ms(2000)
            self._return_to_menu()

    def handle_mode_running(self):
        """
        จัดการสถานะ MODE_RUNNING (Handle MODE_RUNNING state)

        ทำงานโหมดปัจจุบันและตรวจสอบการยกเลิก
        Run current mode and check for cancellation
        """
        if self.current_mode is None:
            self._return_to_menu()
            return

        # ตรวจสอบการกดค้างปุ่ม DOWN เพื่อยกเลิก (Check long press DOWN to cancel)
        if self.buttons.is_long_pressed('down', 3000):
            print("ยกเลิกโหมด (Mode cancelled)")
            self._beep()
            self.current_mode.on_exit()
            self._return_to_menu()
            return

        # อัปเดตโหมด (Update mode)
        try:
            self.current_mode.update()

            # ตรวจสอบว่าโหมดเสร็จสิ้นหรือยัง (Check if mode is complete)
            if self.current_mode.is_complete():
                self.last_results = self.current_mode.get_results()
                self.current_mode.on_exit()
                self.set_state(MenuState.RESULT_DISPLAY)

        except Exception as e:
            print(f"ข้อผิดพลาดในโหมด (Error in mode): {e}")
            self.display.show_error(str(e))
            sleep_ms(2000)
            self.current_mode.on_exit()
            self._return_to_menu()

    def handle_result_display(self):
        """
        จัดการสถานะ RESULT_DISPLAY (Handle RESULT_DISPLAY state)

        แสดงผลลัพธ์และรอการกดปุ่มเพื่อกลับเมนู
        Display results and wait for button press to return to menu
        """
        # ตรวจสอบปุ่ม SELECT เพื่อกลับเมนู (Check SELECT to return to menu)
        if self.buttons.is_pressed('select'):
            self._beep()
            self.buttons.wait_release('select')
            self._return_to_menu()

    def _return_to_menu(self):
        """
        กลับไปหน้าเมนูหลัก (Return to main menu)
        """
        self.current_mode = None
        self.last_results = None
        self.set_state(MenuState.MAIN_MENU)
        self.main_menu_screen.render()

    def run(self):
        """
        เริ่มทำงานระบบเมนู (Start menu system)

        ลูปหลักของแอปพลิเคชัน
        Main application loop
        """
        print("เริ่มระบบเมนู (Starting menu system)")

        # แสดงเมนูหลักครั้งแรก (Display main menu first time)
        self.main_menu_screen.render()

        while self._running:
            try:
                # จัดการตามสถานะปัจจุบัน (Handle based on current state)
                if self.state == MenuState.MAIN_MENU:
                    self.handle_main_menu()

                elif self.state == MenuState.MODE_RUNNING:
                    self.handle_mode_running()

                elif self.state == MenuState.RESULT_DISPLAY:
                    self.handle_result_display()

                # หน่วงเวลาเล็กน้อยเพื่อลด CPU usage (Small delay to reduce CPU usage)
                sleep_ms(10)

            except KeyboardInterrupt:
                print("\nหยุดโปรแกรม (Program stopped)")
                self._running = False
                break

            except Exception as e:
                print(f"ข้อผิดพลาด (Error): {e}")
                sleep_ms(1000)

    def stop(self):
        """
        หยุดระบบเมนู (Stop menu system)
        """
        self._running = False
        if self.current_mode:
            self.current_mode.on_exit()
        print("ระบบเมนูหยุดทำงาน (Menu system stopped)")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("Menu System Module")
    print("==================")
    print("Available classes:")
    print("- MenuState: State constants (MAIN_MENU, MODE_RUNNING, RESULT_DISPLAY)")
    print("- ButtonHandler: Button input with debounce")
    print("- MenuSystem: Main menu state machine")
    print("")
    print("Button mapping:")
    print(f"- SELECT: GPIO{ButtonHandler.PIN_SELECT}")
    print(f"- UP:     GPIO{ButtonHandler.PIN_UP}")
    print(f"- DOWN:   GPIO{ButtonHandler.PIN_DOWN}")

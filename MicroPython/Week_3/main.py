# ==============================================================================
# main.py - โปรแกรมหลักระบบไทเทรชันอัตโนมัติ (Main Titration System)
# ==============================================================================
# ไฟล์นี้เป็นจุดเริ่มต้นของระบบไทเทรชัน TitraLab
# This is the entry point for the TitraLab titration system
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การออกแบบโปรแกรมแบบ modular (Modular program design)
# 2. เข้าใจ dependency injection (การส่งผ่าน dependencies)
# 3. จัดการ hardware lifecycle ด้วย try/finally (Hardware lifecycle management)
#
# ระบบเมนู (Menu System):
# 1. Calibrate pH Sensor   - สอบเทียบเซ็นเซอร์ pH
# 2. pH Sensor Test        - ทดสอบเซ็นเซอร์ pH
# 3. Calibrate Flow Rate   - สอบเทียบอัตราการไหล
# 4. Flow Rate Test        - ทดสอบอัตราการไหล
# 5. Purge                 - ล้างท่อ
# 6. Full Auto Titration   - ไทเทรชันอัตโนมัติ
# ==============================================================================

from time import sleep_ms, ticks_ms, ticks_diff

# นำเข้า Hardware Modules (Import Hardware Modules)
from hardware.display import DisplayManager
from hardware.buttons import ButtonManager
from hardware.pump import Pump
from hardware.ph_sensor import PHSensor
from hardware.temp_sensor import TemperatureSensor
from hardware.buzzer import Buzzer
from hardware.leds import LEDManager
# หมายเหตุ: ไม่ใช้ SD Card เนื่องจากบอร์ดเชื่อมต่อกับ laptop ตลอดเวลา
# Note: SD Card not used - board is always connected to laptop via USB
# ไฟล์ CSV จะบันทึกใน ESP32 flash storage และดาวน์โหลดผ่าน Thonny IDE
# CSV files are saved to ESP32 flash storage and downloaded via Thonny IDE

# นำเข้า Core Modules (Import Core Modules)
from core.calibrator import Calibrator
from core.data_manager import DataManager
from core.titration import TitrationController

# นำเข้า UI Modules (Import UI Modules)
from ui.menu import MenuSystem


# ==============================================================================
# Hardware Hub - ศูนย์รวม Hardware ทั้งหมด
# ==============================================================================
class HardwareHub:
    """
    ศูนย์รวมการจัดการ Hardware ทั้งหมด
    Central hub for all hardware management
    """

    def __init__(self):
        """สร้าง Hardware Hub (Create Hardware Hub)"""
        # สร้าง hardware objects (Create hardware objects)
        self.display = DisplayManager()
        self.buttons = ButtonManager()
        self.pump = Pump()
        self.ph_sensor = PHSensor()
        self.temp_sensor = TemperatureSensor()
        self.buzzer = Buzzer()
        self.leds = LEDManager()

    def init_all(self):
        """
        เริ่มต้น Hardware ทั้งหมด
        Initialize all hardware
        """
        print("=" * 50)
        print("กำลังเริ่มต้น Hardware (Initializing Hardware)")
        print("=" * 50)

        # เริ่มต้นจอแสดงผล (Initialize display)
        print("[1/7] จอแสดงผล (Display)...", end=" ")
        self.display.init()
        print("OK")

        # เริ่มต้นปุ่มกด (Initialize buttons)
        print("[2/7] ปุ่มกด (Buttons)...", end=" ")
        self.buttons.init()
        print("OK")

        # เริ่มต้น LED (Initialize LEDs)
        print("[3/7] LED...", end=" ")
        self.leds.init()
        print("OK")

        # เริ่มต้น Buzzer (Initialize buzzer)
        print("[4/7] Buzzer...", end=" ")
        self.buzzer.init()
        print("OK")

        # เริ่มต้นเซ็นเซอร์ pH (Initialize pH sensor)
        print("[5/7] เซ็นเซอร์ pH (pH Sensor)...", end=" ")
        self.ph_sensor.init()
        print("OK")

        # เริ่มต้นเซ็นเซอร์อุณหภูมิ (Initialize temperature sensor)
        print("[6/7] เซ็นเซอร์อุณหภูมิ (Temperature Sensor)...", end=" ")
        self.temp_sensor.init()
        print("OK")

        # เริ่มต้นปั๊ม (Initialize pump)
        print("[7/7] ปั๊ม (Pump)...", end=" ")
        self.pump.init()
        print("OK")

        print("=" * 50)
        print("Hardware พร้อมใช้งาน (Hardware Ready)")
        print("ไฟล์ข้อมูลบันทึกใน ESP32 (Data files saved on ESP32)")
        print("=" * 50)

        # ส่งเสียง Buzzer (Beep buzzer)
        self.buzzer.beep(frequency=1000, duration_ms=100)

    def deinit_all(self):
        """
        ปิด Hardware ทั้งหมด
        Cleanup all hardware
        """
        print("\nกำลังปิด Hardware (Shutting down hardware)...")

        # ปิดปั๊ม (Stop pump)
        if self.pump:
            self.pump.stop()
            self.pump.deinit()

        # ปิด Buzzer (Stop buzzer)
        if self.buzzer:
            self.buzzer.deinit()

        # ปิด LED (Turn off LEDs)
        if self.leds:
            self.leds.all_off()
            self.leds.deinit()

        # ปิดจอแสดงผล (Clear display)
        if self.display:
            self.display.clear()
            self.display.deinit()

        print("ปิด Hardware เสร็จสิ้น (Hardware shutdown complete)")


# ==============================================================================
# Main Application - แอปพลิเคชันหลัก
# ==============================================================================
def main():
    """
    ฟังก์ชันหลักของโปรแกรม
    Main function of the program
    """
    # สร้าง Hardware Hub (Create Hardware Hub)
    hardware = HardwareHub()

    try:
        # เริ่มต้น Hardware ทั้งหมด (Initialize all hardware)
        hardware.init_all()

        # สร้าง Data Manager (Create Data Manager)
        # บันทึกข้อมูลใน ESP32 flash storage (Save data to ESP32 flash storage)
        data_manager = DataManager()

        # สร้าง Calibrator (Create Calibrator)
        calibrator = Calibrator(
            ph_sensor=hardware.ph_sensor,
            pump=hardware.pump,
            display=hardware.display,
            buttons=hardware.buttons,
            buzzer=hardware.buzzer,
            data_manager=data_manager
        )

        # สร้าง Titration Controller (Create Titration Controller)
        # บันทึก CSV ใน ESP32 flash (CSV saved to ESP32 flash)
        titration = TitrationController(
            pump=hardware.pump,
            ph_sensor=hardware.ph_sensor,
            temp_sensor=hardware.temp_sensor,
            display=hardware.display,
            buzzer=hardware.buzzer,
            led_indicator=hardware.leds.green
        )

        # สร้าง Menu System (Create Menu System)
        menu = MenuSystem(
            display=hardware.display,
            buttons=hardware.buttons,
            buzzer=hardware.buzzer
        )

        # กำหนด Menu Actions (Define Menu Actions)
        menu_actions = {
            1: lambda: calibrator.calibrate_ph(),        # สอบเทียบ pH
            2: lambda: calibrator.test_ph_sensor(),      # ทดสอบ pH
            3: lambda: calibrator.calibrate_flow_rate(), # สอบเทียบ Flow Rate
            4: lambda: calibrator.test_flow_rate(),      # ทดสอบ Flow Rate
            5: lambda: hardware.pump.purge(),            # ล้างท่อ
            6: lambda: titration.run_titration()         # ไทเทรชันอัตโนมัติ
        }

        # แสดงหน้าจอต้อนรับ (Show welcome screen)
        hardware.display.show_logo("TitraLab", "Chemistry Automation")
        sleep_ms(2000)

        # ลูปหลักของโปรแกรม (Main program loop)
        print("\nเข้าสู่โหมดเมนูหลัก (Entering main menu mode)")
        print("กดปุ่ม 3 ค้าง 3 วินาทีเพื่อออก (Hold Button 3 for 3s to exit)")

        running = True
        while running:
            # แสดงเมนู (Show menu)
            menu.show()

            # รอการกดปุ่ม (Wait for button press)
            button_pressed = None
            button_hold_start = 0

            while button_pressed is None:
                # ตรวจสอบปุ่ม SELECT (Check SELECT button - Button 1)
                if hardware.buttons.is_pressed(1):
                    hardware.buzzer.beep(duration_ms=50)
                    selected = menu.get_selected()
                    if selected in menu_actions:
                        # ดำเนินการตามเมนูที่เลือก (Execute selected action)
                        hardware.leds.green.on()
                        try:
                            menu_actions[selected]()
                        except Exception as e:
                            print(f"ข้อผิดพลาด (Error): {e}")
                            hardware.leds.red.on()
                            hardware.buzzer.beep(frequency=500, duration_ms=500)
                            sleep_ms(1000)
                            hardware.leds.red.off()
                        finally:
                            hardware.leds.green.off()
                    # รอปล่อยปุ่ม (Wait for button release)
                    while hardware.buttons.is_pressed(1):
                        sleep_ms(10)
                    button_pressed = 1

                # ตรวจสอบปุ่ม UP (Check UP button - Button 2)
                elif hardware.buttons.is_pressed(2):
                    hardware.buzzer.beep(duration_ms=30)
                    menu.move_up()
                    while hardware.buttons.is_pressed(2):
                        sleep_ms(10)
                    button_pressed = 2

                # ตรวจสอบปุ่ม DOWN (Check DOWN button - Button 3)
                elif hardware.buttons.is_pressed(3):
                    # ตรวจสอบการกดค้าง (Check for long press)
                    if button_hold_start == 0:
                        button_hold_start = ticks_ms()

                    # ถ้ากดค้าง 3 วินาที ให้ออก (Exit if held for 3 seconds)
                    if ticks_diff(ticks_ms(), button_hold_start) > 3000:
                        print("\nออกจากโปรแกรม (Exiting program)")
                        running = False
                        button_pressed = 3
                    sleep_ms(10)

                else:
                    # รีเซ็ตตัวนับการกดค้าง (Reset hold counter)
                    if button_hold_start > 0:
                        # ถ้าปล่อยก่อน 3 วินาที ให้เลื่อนเมนู (Move down if released before 3s)
                        hardware.buzzer.beep(duration_ms=30)
                        menu.move_down()
                        button_pressed = 3
                    button_hold_start = 0

                sleep_ms(50)

    except KeyboardInterrupt:
        print("\nหยุดโปรแกรมด้วย Ctrl+C (Program stopped by Ctrl+C)")

    except Exception as e:
        print(f"\nข้อผิดพลาดร้ายแรง (Fatal error): {e}")

    finally:
        # ทำความสะอาด Hardware (Cleanup hardware)
        hardware.deinit_all()
        print("\nโปรแกรมสิ้นสุด (Program ended)")


# ==============================================================================
# จุดเริ่มต้นโปรแกรม (Program Entry Point)
# ==============================================================================
if __name__ == '__main__':
    main()

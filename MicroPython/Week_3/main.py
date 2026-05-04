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
import gc  # สำหรับ garbage collection (for garbage collection)

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

# หมายเหตุ: Core และ UI Modules จะนำเข้าภายใน main() เพื่อประหยัดหน่วยความจำ
# Note: Core and UI Modules are imported inside main() to save memory
# เนื่องจาก display ต้องการหน่วยความจำต่อเนื่อง 5120 bytes สำหรับ buffer
# Because display needs 5120 bytes contiguous memory for its buffer


# ==============================================================================
# Hardware Hub - ศูนย์รวม Hardware ทั้งหมด
# ==============================================================================
class HardwareHub:
    """ศูนย์รวม Hardware (Central hardware hub)"""

    def __init__(self):
        """สร้าง Hardware Hub (Create Hardware Hub)"""
        # เก็บกวาดหน่วยความจำก่อนสร้าง hardware (GC before creating hardware)
        gc.collect()

        # สร้าง hardware objects ที่ใช้หน่วยความจำน้อยก่อน
        # Create low-memory objects first
        self.buttons = ButtonManager()
        self.pump = Pump()
        self.buzzer = Buzzer()
        self.leds = LEDManager()
        self.ph_sensor = PHSensor()
        self.temp_sensor = TemperatureSensor()

        # เก็บกวาดหน่วยความจำก่อนสร้าง display (GC before display - needs most RAM)
        gc.collect()
        self.display = DisplayManager()

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
        self.buzzer.play_tone(1000, 100)

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
            try:
                gc.collect()  # เก็บกวาดก่อน clear เพื่อให้มี buffer เพียงพอ
                self.display.clear()
            except MemoryError:
                pass  # ข้ามถ้าหน่วยความจำไม่พอ (Skip if out of memory)
            self.display.deinit()

        print("ปิด Hardware เสร็จสิ้น (Hardware shutdown complete)")


# ==============================================================================
# Main Application
# ==============================================================================
def main():
    """Main function"""
    # เก็บกวาดหน่วยความจำก่อนเริ่ม (GC before starting)
    gc.collect()
    print(f"Free memory: {gc.mem_free()} bytes")

    # สร้าง Hardware Hub (Create Hardware Hub)
    hardware = HardwareHub()

    try:
        # เริ่มต้น Hardware ทั้งหมด (Initialize all hardware)
        hardware.init_all()

        # นำเข้า Core/UI Modules หลังจาก hardware พร้อมแล้ว (เพื่อประหยัด RAM)
        # Import Core/UI Modules AFTER hardware init (to save RAM for display buffer)
        # นำเข้าทีละกลุ่มพร้อม gc.collect() เพื่อลด memory fragmentation
        # Import in stages with gc.collect() to reduce memory fragmentation
        gc.collect()
        print(f"Free memory before imports: {gc.mem_free()} bytes")
        from core.data_manager import DataManager
        gc.collect()
        from core.calibrator import Calibrator
        gc.collect()
        from ui.menu import MenuSystem
        gc.collect()
        print(f"Free memory after imports: {gc.mem_free()} bytes")
        # หมายเหตุ: TitrationController จะนำเข้าเมื่อเลือก Menu 6 เท่านั้น
        # Note: TitrationController imported only when Menu 6 is selected (saves ~15KB RAM)

        # สร้าง Data Manager (Create Data Manager)
        # บันทึกข้อมูลใน ESP32 flash storage (Save data to ESP32 flash storage)
        data_manager = DataManager()

        # โหลดค่าสอบเทียบ pH จากไฟล์ (ถ้ามี) (Load pH calibration from file if exists)
        # FIX: ก่อนหน้านี้ค่าสอบเทียบไม่ถูกโหลดเมื่อเริ่มโปรแกรมใหม่
        # FIX: Previously calibration was not loaded when program restarted
        slope_m, intercept_b, r_squared, cal_temp = data_manager.load_ph_calibration()
        if slope_m is not None and intercept_b is not None:
            hardware.ph_sensor.set_calibration(slope_m, intercept_b)
            print(f"นำค่าสอบเทียบ pH มาใช้แล้ว (pH calibration applied)")
        else:
            print("ใช้ค่าสอบเทียบ pH เริ่มต้น (Using default pH calibration)")

        # โหลดค่าอัตราการไหลจากไฟล์ (ถ้ามี) (Load flow rate from file if exists)
        flow_rate, _ = data_manager.load_flow_rate()
        if flow_rate is not None:
            hardware.pump.flow_rate = flow_rate
            print(f"นำค่าอัตราการไหลมาใช้แล้ว (Flow rate applied): {flow_rate:.4f} mL/s")
        else:
            print("ใช้ค่าอัตราการไหลเริ่มต้น (Using default flow rate)")

        # สร้าง Calibrator (Create Calibrator)
        calibrator = Calibrator(
            ph_sensor=hardware.ph_sensor,
            pump=hardware.pump,
            display=hardware.display,
            buttons=hardware.buttons,
            buzzer=hardware.buzzer,
            data_manager=data_manager
        )

        # ซิงค์ค่าอัตราการไหลที่โหลดจากไฟล์ไปยัง Calibrator ด้วย
        # Sync loaded flow rate to Calibrator (it has its own _flow_rate copy)
        if flow_rate is not None:
            calibrator._flow_rate = flow_rate
            calibrator._flow_calibrated = True

        # สร้าง Titration Controller แบบ lazy (สร้างเมื่อเลือก Menu 6 เท่านั้น)
        # Create TitrationController lazily (only when Menu 6 is selected)
        # เพื่อประหยัด RAM ~15KB สำหรับเมนูอื่นที่ไม่ต้องใช้
        # Saves ~15KB RAM for other menus that don't need it
        _titration = [None]  # ใช้ list เพื่อให้ lambda เข้าถึงได้ (use list for lambda access)

        def _run_titration():
            """สร้าง TitrationController ครั้งแรกที่ใช้ แล้วรัน (Create on first use, then run)"""
            gc.collect()
            if _titration[0] is None:
                from core.titration import TitrationController
                gc.collect()
                _titration[0] = TitrationController(
                    pump=hardware.pump,
                    ph_sensor=hardware.ph_sensor,
                    temp_sensor=hardware.temp_sensor,
                    display=hardware.display,
                    buzzer=hardware.buzzer,
                    led_indicator=hardware.leds.green,
                    buttons=hardware.buttons
                )
                _titration[0].configure(
                    stabilize_time=10.0,
                    alert_volume=4.80
                )
            return _titration[0].run_titration()

        # เก็บกวาดหน่วยความจำก่อนสร้าง Menu (GC before Menu creation)
        gc.collect()

        # สร้าง Menu System (Create Menu System)
        menu = MenuSystem(
            display=hardware.display,
            buttons=hardware.buttons,
            buzzer=hardware.buzzer
        )

        # กำหนด Menu Actions (Define Menu Actions)
        # ทุกเมนูรองรับ BTN3 เพื่อยกเลิก (All menus support BTN3 to cancel)
        menu_actions = {
            1: lambda: calibrator.calibrate_ph(),                    # สอบเทียบ pH
            2: lambda: calibrator.test_ph_sensor(),                  # ทดสอบ pH
            3: lambda: calibrator.calibrate_flow_rate_interactive(), # สอบเทียบ Flow Rate
            4: lambda: calibrator.test_flow_rate(),                  # ทดสอบ Flow Rate
            5: lambda: calibrator.purge_tubing(),                    # ล้างท่อ (with BTN3)
            6: lambda: _run_titration()                              # ไทเทรชันอัตโนมัติ (lazy load)
        }

        # เก็บกวาดหน่วยความจำก่อนแสดงผล (GC before display operations)
        gc.collect()

        # แสดงหน้าจอต้อนรับ (Show welcome screen)
        hardware.display.show_logo("TitraLab", "Chemistry Automation")
        sleep_ms(2000)

        # ลูปหลักของโปรแกรม (Main program loop)
        print("\nเข้าสู่โหมดเมนูหลัก (Entering main menu mode)")
        print("กดปุ่ม 3 ค้าง 3 วินาทีเพื่อออก (Hold Button 3 for 3s to exit)")

        running = True
        while running:
            # เก็บกวาดหน่วยความจำก่อนแสดงเมนู (Garbage collect before showing menu)
            gc.collect()

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
                            hardware.buzzer.play_tone(500, 500)
                            sleep_ms(1000)
                            hardware.leds.red.off()
                        finally:
                            hardware.leds.green.off()
                            # เก็บกวาดหน่วยความจำหลังทำงานเสร็จ (Garbage collect after action)
                            gc.collect()
                            # ร้องขอให้วาดเมนูใหม่ (Request menu redraw)
                            menu.request_redraw()
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

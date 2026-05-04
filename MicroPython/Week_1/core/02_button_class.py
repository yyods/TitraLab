# ==============================================================================
# 02_button_class.py - คลาส Button สำหรับระบบ TitraLab (Button Class for TitraLab)
# ==============================================================================
# สัปดาห์ที่ 1: การอ่านปุ่มกดด้วย OOP (Week 1: Button Reading with OOP)
# เวลา: ~30 นาที (Time: ~30 minutes)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการอ่าน GPIO Input (Understand GPIO Input reading)
#   2. เข้าใจหลักการ Debounce (Understand debounce principle)
#   3. เชื่อมโยงกับการควบคุมเมนูในระบบไทเทรชัน (Connect to menu control)
#
# บริบทการใช้งานจริง - เหมือนการควบคุมเมนูใน Week 3 (Real Application Context):
#   - ปุ่ม 1 (GPIO34): SELECT - เลือก/ยืนยัน (Select/Confirm)
#   - ปุ่ม 2 (GPIO35): UP - เลื่อนขึ้น/เพิ่มค่า (Scroll up/Increase)
#   - ปุ่ม 3 (GPIO39): DOWN - เลื่อนลง/ลดค่า (Scroll down/Decrease)
#
# หมายเหตุสำคัญเกี่ยวกับฮาร์ดแวร์ (Important Hardware Notes):
#   - GPIO34, 35, 39 เป็นขา Input-only (ไม่มี internal pull-up)
#   - บอร์ด TitraLab มี hardware debounce ผ่าน 74HC14D Schmitt trigger
#   - จึงไม่จำเป็นต้องทำ software debounce แต่เพิ่มไว้เพื่อความปลอดภัย
#
# ==============================================================================

from machine import Pin
import time


class Button:
    """
    คลาสอ่านปุ่มกดสำหรับระบบควบคุมไทเทรชัน
    (Button Class for Titration Control System)

    ในระบบ TitraLab เต็มรูปแบบ (Week 3) ปุ่มจะใช้สำหรับ:
    (In the full TitraLab system, buttons are used for:)
      - ควบคุมเมนูการตั้งค่า (Control settings menu)
      - เริ่ม/หยุดการไทเทรชัน (Start/Stop titration)
      - ยืนยันจุด calibration (Confirm calibration points)
      - เลือกโหมดการทำงาน (Select operation mode)

    คุณสมบัติของ TitraLab (TitraLab Features):
      - Hardware debounce ผ่าน IC 74HC14D (Schmitt trigger)
      - ปุ่มกดแล้วอ่านค่า HIGH (Active-high logic)
      - Pull-down resistor ภายนอก (External pull-down)

    ตัวอย่างการใช้งาน (Usage Example):
        btn = Button(34, "SELECT")
        if btn.is_pressed():
            print("Button pressed!")
    """

    def __init__(self, pin_number, name="Button", debounce_ms=50):
        """
        สร้าง Button object (Create Button object)

        พารามิเตอร์ (Parameters):
            pin_number (int): หมายเลข GPIO (34, 35, หรือ 39)
            name (str): ชื่อปุ่มสำหรับแสดงผล (Button name for display)
            debounce_ms (int): เวลา debounce (มิลลิวินาที)
                              - TitraLab มี hardware debounce แล้ว
                              - ค่านี้เป็นการป้องกันเพิ่มเติม

        หมายเหตุ (Note):
            GPIO34, 35, 39 เป็นขา Input-only บน ESP32
            ไม่สามารถใช้ Pin.PULL_UP ได้ (ต้องใช้ resistor ภายนอก)
        """
        self.pin_number = pin_number
        self.name = name
        self.debounce_ms = debounce_ms

        # สร้าง Pin เป็น INPUT (ไม่มี pull-up ภายใน)
        # Create Pin as INPUT (no internal pull-up available)
        self._pin = Pin(pin_number, Pin.IN)

        # ตัวแปรสำหรับ debounce (Variables for debounce)
        self._last_press_time = 0      # เวลาที่กดครั้งล่าสุด (Last press time)
        self._was_pressed = False      # สถานะกดค้าง (Was button held)

        print(f"Button '{name}' พร้อมใช้งานที่ GPIO{pin_number} (ready)")
        print(f"  - ขา Input-only (ไม่มี internal pull-up)")
        print(f"  - Hardware debounce: 74HC14D Schmitt trigger")

    def is_active(self):
        """
        ตรวจสอบว่าปุ่มถูกกดอยู่หรือไม่ (Check if button is currently pressed)

        คืนค่า (Returns):
            True ถ้ากำลังกดอยู่ (if currently pressed)
            False ถ้าไม่ได้กด (if not pressed)

        ใช้สำหรับ (Use for):
            - ตรวจสอบการกดค้าง (Detect held button)
            - รอให้ปล่อยปุ่ม (Wait for button release)
        """
        # บอร์ด TitraLab: กด = HIGH (1), ไม่กด = LOW (0)
        return self._pin.value() == 1

    def is_pressed(self):
        """
        ตรวจจับการกดปุ่มครั้งใหม่พร้อม debounce
        (Detect new button press with debounce)

        คืนค่า True เพียงครั้งเดียวต่อการกดหนึ่งครั้ง
        (Returns True only ONCE per press)

        การทำงาน (How it works):
            1. ตรวจสอบว่ากดอยู่หรือไม่
            2. ตรวจสอบว่าเป็นการกดใหม่ (ไม่ใช่กดค้าง)
            3. ตรวจสอบเวลา debounce

        ใช้สำหรับ (Use for):
            - นับจำนวนครั้งที่กด (Count button presses)
            - การเลือกเมนู (Menu selection)
            - การยืนยันค่า (Value confirmation)
        """
        current_time = time.ticks_ms()
        is_active_now = self.is_active()

        # ตรวจสอบว่าเป็นการกดใหม่ (ไม่ใช่กดค้างจากครั้งก่อน)
        # Check if this is a new press (not held from before)
        if is_active_now and not self._was_pressed:
            # ตรวจสอบว่าผ่านเวลา debounce แล้ว
            # Check if debounce time has passed
            if time.ticks_diff(current_time, self._last_press_time) > self.debounce_ms:
                self._last_press_time = current_time
                self._was_pressed = True
                return True

        # รีเซ็ตสถานะเมื่อปล่อยปุ่ม (Reset state when button released)
        if not is_active_now:
            self._was_pressed = False

        return False

    def wait_for_press(self, timeout_ms=None):
        """
        รอจนกว่าปุ่มจะถูกกด (Wait until button is pressed)

        พารามิเตอร์ (Parameters):
            timeout_ms (int): เวลารอสูงสุด (None = รอไม่จำกัด)

        คืนค่า (Returns):
            True ถ้ากดปุ่ม (if button pressed)
            False ถ้าหมดเวลา (if timeout)

        ใช้สำหรับ (Use for):
            - รอยืนยันการ calibration (Wait for calibration confirm)
            - รอเริ่มการไทเทรชัน (Wait to start titration)
        """
        start_time = time.ticks_ms()
        print(f"รอการกดปุ่ม {self.name}... (Waiting for {self.name}...)")

        while True:
            if self.is_pressed():
                return True

            # ตรวจสอบ timeout (Check for timeout)
            if timeout_ms is not None:
                elapsed = time.ticks_diff(time.ticks_ms(), start_time)
                if elapsed > timeout_ms:
                    print("หมดเวลา! (Timeout!)")
                    return False

            time.sleep_ms(10)  # หน่วงเวลาเล็กน้อยประหยัดพลังงาน (Small delay to save power)

    def wait_for_release(self):
        """
        รอจนกว่าปุ่มจะถูกปล่อย (Wait until button is released)

        ใช้สำหรับ (Use for):
            - ป้องกันการกดซ้ำ (Prevent repeated presses)
            - รอให้ action เสร็จก่อนรับคำสั่งใหม่
        """
        while self.is_active():
            time.sleep_ms(10)


# ==============================================================================
# โค้ดทดสอบ - จำลองการควบคุมเมนูไทเทรชัน (Test Code - Simulate Menu Control)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบคลาส Button - จำลองการควบคุมเมนูไทเทรชัน")
    print("Button Class Test - Simulate Titration Menu Control")
    print("=" * 60)
    print("\nคำอธิบายปุ่ม (Button Description):")
    print("  - ปุ่ม 1 (GPIO34): SELECT - เลือก/ยืนยัน")
    print("  - ปุ่ม 2 (GPIO35): UP - เลื่อนขึ้น")
    print("  - ปุ่ม 3 (GPIO39): DOWN - เลื่อนลง")
    print("\nกด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
    print("-" * 60)

    # สร้าง Button objects (Create Button objects)
    # ชื่อปุ่มตรงกับการใช้งานใน Week 3
    btn_select = Button(34, "SELECT")   # ยืนยัน/เลือก
    btn_up = Button(35, "UP")           # เลื่อนขึ้น
    btn_down = Button(39, "DOWN")       # เลื่อนลง

    # จำลองตัวเลือกเมนู (Simulate menu options)
    menu_items = [
        "1. เริ่มไทเทรชัน (Start Titration)",
        "2. สอบเทียบ pH (Calibrate pH)",
        "3. ตั้งค่าปั๊ม (Pump Settings)",
        "4. ดูประวัติ (View History)"
    ]
    current_index = 0  # ตำแหน่งเมนูปัจจุบัน (Current menu position)

    def show_menu():
        """แสดงเมนูพร้อมตัวชี้ (Display menu with pointer)"""
        print("\n" + "=" * 40)
        print("เมนูหลัก (Main Menu)")
        print("=" * 40)
        for i, item in enumerate(menu_items):
            pointer = ">>>" if i == current_index else "   "
            print(f"{pointer} {item}")
        print("-" * 40)

    # แสดงเมนูครั้งแรก (Show menu initially)
    show_menu()

    try:
        while True:
            # ตรวจสอบปุ่ม SELECT (Check SELECT button)
            if btn_select.is_pressed():
                selected = menu_items[current_index]
                print(f"\n*** เลือก: {selected} ***")
                print("(ในระบบจริงจะเข้าสู่ฟังก์ชันที่เลือก)")
                print("*** Selected - Would execute function ***")
                time.sleep(0.5)
                show_menu()

            # ตรวจสอบปุ่ม UP (Check UP button)
            if btn_up.is_pressed():
                current_index = (current_index - 1) % len(menu_items)
                print(f"เลื่อนขึ้น -> ตำแหน่ง {current_index + 1}")
                show_menu()

            # ตรวจสอบปุ่ม DOWN (Check DOWN button)
            if btn_down.is_pressed():
                current_index = (current_index + 1) % len(menu_items)
                print(f"เลื่อนลง -> ตำแหน่ง {current_index + 1}")
                show_menu()

            # หน่วงเวลาเล็กน้อยเพื่อลดการใช้ CPU (Small delay to reduce CPU usage)
            time.sleep_ms(20)

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("หยุดโปรแกรม (Program stopped by user)")
        print("=" * 60)


# ==============================================================================
# แบบฝึกหัด (Exercises)
# ==============================================================================
#
# แบบฝึกหัดที่ 1: เพิ่มฟังก์ชัน long_press()
# (Exercise 1: Add long_press() function)
#   - ตรวจจับการกดค้างนานกว่า 1 วินาที
#   - ใช้สำหรับ: ยกเลิก, รีเซ็ตระบบ
#   - คำแนะนำ: ใช้ time.ticks_diff() เทียบเวลา
#
# แบบฝึกหัดที่ 2: สร้างคลาส MenuController
# (Exercise 2: Create MenuController class)
#   - รวมปุ่ม 3 ปุ่มเข้าด้วยกัน
#   - จัดการเมนูอัตโนมัติ
#   - มี callback function เมื่อเลือกเมนู
#
# แบบฝึกหัดที่ 3: เพิ่มระบบนับค่าด้วยปุ่ม UP/DOWN
# (Exercise 3: Add value counter with UP/DOWN buttons)
#   - กด UP = เพิ่มค่าทีละ 1
#   - กด DOWN = ลดค่าทีละ 1
#   - กด SELECT = ยืนยันค่า
#   - ใช้สำหรับ: ตั้งค่าปริมาตร, ตั้งค่าความเร็วปั๊ม
#
# ==============================================================================
#
# ข้อมูลทางเทคนิคเพิ่มเติม (Additional Technical Information)
# ==============================================================================
#
# ทำไม GPIO34, 35, 39 ถึงเป็น Input-only?
# (Why are GPIO34, 35, 39 input-only?)
#   - ESP32 แบ่ง GPIO เป็นหลายกลุ่ม
#   - GPIO34-39 เชื่อมต่อกับ ADC1 เท่านั้น
#   - ไม่มีวงจร output driver
#   - ไม่มี internal pull-up/pull-down resistor
#
# Hardware Debounce บนบอร์ด TitraLab:
# (Hardware Debounce on TitraLab board:)
#   - ใช้ IC 74HC14D (Hex Schmitt Trigger Inverter)
#   - Schmitt trigger มี hysteresis ช่วยกรองสัญญาณรบกวน
#   - ไม่ต้องเขียนโค้ด debounce ซับซ้อน
#   - แต่ยังใส่ software debounce เผื่อความปลอดภัย
#
# ==============================================================================

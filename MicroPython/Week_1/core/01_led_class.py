# ==============================================================================
# 01_led_class.py - คลาส LED สำหรับระบบ TitraLab (LED Class for TitraLab)
# ==============================================================================
# สัปดาห์ที่ 1: การควบคุม LED ด้วย OOP (Week 1: LED Control with OOP)
# เวลา: ~30 นาที (Time: ~30 minutes)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการสร้างคลาสและออบเจกต์ใน MicroPython (Understand class/object creation)
#   2. ควบคุม GPIO Output สำหรับ LED (Control GPIO Output for LED)
#   3. เชื่อมโยงกับการแสดงสถานะในระบบไทเทรชัน (Connect to titration status display)
#
# บริบทการใช้งานจริง - เหมือนการแสดงสถานะปั๊มใน Week 3 (Real Application Context):
#   - LED สีเขียว (GPIO4): ปั๊มกำลังทำงาน/ระบบพร้อม (Pump running/System ready)
#   - LED สีแดง (GPIO2): ถึงจุดสมมูล/เกิดข้อผิดพลาด (Endpoint reached/Error)
#
# ขาที่ใช้ (Pin Configuration):
#   - LED_RED   = GPIO2  (แสดงข้อผิดพลาดหรือจุดสมมูล)
#   - LED_GREEN = GPIO4  (แสดงสถานะปกติหรือกำลังทำงาน)
# ==============================================================================

from machine import Pin
import time


class LED:
    """
    คลาสควบคุม LED สำหรับแสดงสถานะระบบไทเทรชัน
    (LED Control Class for Titration System Status Display)

    ในระบบ TitraLab เต็มรูปแบบ (Week 3) LED จะแสดงสถานะ:
    (In the full TitraLab system, LEDs indicate status:)
      - เขียวติด = ปั๊มกำลังหยดสาร (Green ON = Pump dispensing)
      - เขียวกระพริบ = รอคำสั่ง (Green blink = Waiting for input)
      - แดงติด = ถึงจุดสมมูล (Red ON = Endpoint reached)
      - แดงกระพริบ = เตือน/ผิดพลาด (Red blink = Warning/Error)

    ตัวอย่างการใช้งาน (Usage Example):
        led = LED(2, "Red")
        led.on()          # เปิด LED
        led.blink(3)      # กระพริบ 3 ครั้ง
        led.off()         # ปิด LED
    """

    def __init__(self, pin_number, name="LED"):
        """
        สร้าง LED object (Create LED object)

        พารามิเตอร์ (Parameters):
            pin_number (int): หมายเลข GPIO (2=แดง, 4=เขียว)
            name (str): ชื่อ LED สำหรับแสดงผล (LED name for display)
        """
        # เก็บค่าพารามิเตอร์ไว้ใช้ภายหลัง (Store parameters for later use)
        self.pin_number = pin_number
        self.name = name
        self.is_on = False  # ติดตามสถานะ LED (Track LED state)

        # สร้าง Pin เป็น OUTPUT (Create Pin as OUTPUT)
        # Pin.OUT หมายความว่าจะส่งสัญญาณออกไปควบคุม LED
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)  # เริ่มต้นปิด LED (Start with LED off)

        print(f"LED '{name}' พร้อมใช้งานที่ GPIO{pin_number} (ready)")

    def on(self):
        """
        เปิด LED (Turn LED on)
        ใช้เมื่อ: เริ่มทำงาน, ถึงจุดสมมูล (Use when: Starting, Endpoint reached)
        """
        self._pin.value(1)  # ส่งสัญญาณ HIGH (3.3V) ไปที่ LED
        self.is_on = True

    def off(self):
        """
        ปิด LED (Turn LED off)
        ใช้เมื่อ: หยุดทำงาน, รีเซ็ตระบบ (Use when: Stopping, Reset system)
        """
        self._pin.value(0)  # ส่งสัญญาณ LOW (0V) ไปที่ LED
        self.is_on = False

    def toggle(self):
        """
        สลับสถานะ LED (Toggle LED state)
        ใช้สำหรับ: การกระพริบ, การสลับโหมด (Use for: Blinking, Mode toggle)

        คืนค่า (Returns): True ถ้า LED ติดอยู่ (if LED is on)
        """
        if self.is_on:
            self.off()
        else:
            self.on()
        return self.is_on

    def blink(self, times=1, delay_sec=0.3):
        """
        กระพริบ LED ตามจำนวนครั้งที่กำหนด (Blink LED specified number of times)

        การใช้งานในระบบไทเทรชัน (Titration system usage):
          - กระพริบ 3 ครั้ง = เริ่มต้นสำเร็จ (3 blinks = Init success)
          - กระพริบเร็ว = เตือนใกล้จุดสมมูล (Fast blink = Near endpoint warning)

        พารามิเตอร์ (Parameters):
            times (int): จำนวนครั้งที่กระพริบ (number of blinks)
            delay_sec (float): เวลาหน่วงระหว่างติด/ดับ (delay between on/off)
        """
        for i in range(times):
            self._pin.value(1)  # เปิด (ON)
            time.sleep(delay_sec)
            self._pin.value(0)  # ปิด (OFF)
            time.sleep(delay_sec)
        self.is_on = False  # สถานะสุดท้ายคือปิด (Final state is off)

    def deinit(self):
        """
        ปิด LED และคืนทรัพยากร (Turn off LED and cleanup)

        สำคัญ: ควรเรียกใน finally block เสมอ
        (Important: Always call in finally block)
        """
        self.off()


# ==============================================================================
# โค้ดทดสอบ - จำลองสถานะระบบไทเทรชัน (Test Code - Simulate Titration Status)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบคลาส LED - จำลองสถานะระบบไทเทรชัน")
    print("LED Class Test - Simulate Titration System Status")
    print("=" * 50)

    # สร้าง LED objects (Create LED objects)
    # เหมือนที่จะใช้ใน Week 3 สำหรับแสดงสถานะปั๊ม
    led_red = LED(2, "Red-Error")      # LED แดง = ข้อผิดพลาด/จุดสมมูล
    led_green = LED(4, "Green-Status") # LED เขียว = สถานะปกติ

    try:
        # ----- การทดสอบที่ 1: เปิด/ปิด (Test 1: On/Off) -----
        print("\n--- ทดสอบ on/off (Test on/off) ---")
        print("เขียวติด = ระบบพร้อม (Green ON = System ready)")
        led_green.on()
        time.sleep(1)
        led_green.off()

        # ----- การทดสอบที่ 2: กระพริบ (Test 2: Blink) -----
        print("\n--- ทดสอบ blink (Test blink) ---")
        print("กระพริบเขียว 3 ครั้ง = เริ่มต้นสำเร็จ (3 green blinks = Init OK)")
        led_green.blink(3, 0.2)
        time.sleep(0.5)

        # ----- การทดสอบที่ 3: จำลองปั๊มทำงาน (Test 3: Simulate Pump Running) -----
        print("\n--- จำลองปั๊มกำลังทำงาน (Simulate pump running) ---")
        print("เขียวติดค้าง = ปั๊มกำลังหยดสาร (Green ON = Dispensing)")
        led_green.on()

        # นับปริมาตรจำลอง (Simulate volume count)
        for vol in range(5):
            print(f"  ปริมาตร (Volume): {vol + 1} mL")
            time.sleep(0.5)

        led_green.off()
        print("หยุดหยดสาร (Stop dispensing)")

        # ----- การทดสอบที่ 4: จำลองถึงจุดสมมูล (Test 4: Simulate Endpoint) -----
        print("\n--- จำลองถึงจุดสมมูล (Simulate endpoint reached) ---")
        print("แดงติด + เขียวดับ = ถึงจุดสมมูล!")
        led_green.off()
        led_red.on()
        time.sleep(1)

        # กระพริบแดงเตือน (Red warning blink)
        print("แดงกระพริบ = เตือนจุดสมมูล (Red blink = Endpoint alert)")
        led_red.blink(5, 0.15)

        # ----- การทดสอบที่ 5: จำลองข้อผิดพลาด (Test 5: Simulate Error) -----
        print("\n--- จำลองข้อผิดพลาด (Simulate error state) ---")
        print("แดง-เขียว สลับกัน = ข้อผิดพลาดร้ายแรง")
        for _ in range(4):
            led_red.on()
            led_green.off()
            time.sleep(0.2)
            led_red.off()
            led_green.on()
            time.sleep(0.2)

        print("\n" + "=" * 50)
        print("ทดสอบเสร็จสิ้น! (Test completed!)")
        print("=" * 50)

    except KeyboardInterrupt:
        # กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)
        print("\n\nหยุดโปรแกรม (Program stopped by user)")

    finally:
        # ทำความสะอาดทรัพยากร - สำคัญมาก! (Cleanup resources - Very important!)
        led_red.deinit()
        led_green.deinit()
        print("ปิด LED ทั้งหมดแล้ว (All LEDs turned off)")


# ==============================================================================
# แบบฝึกหัด (Exercises)
# ==============================================================================
#
# แบบฝึกหัดที่ 1: เพิ่มเมธอด warning_blink()
# (Exercise 1: Add warning_blink() method)
#   - กระพริบเร็ว 10 ครั้ง (0.1 วินาที)
#   - ใช้เตือนเมื่อ pH ใกล้จุดสมมูล
#
# แบบฝึกหัดที่ 2: สร้างคลาส StatusIndicator
# (Exercise 2: Create StatusIndicator class)
#   - รวม LED แดงและเขียวเข้าด้วยกัน
#   - มีเมธอด: ready(), running(), error(), endpoint()
#
# แบบฝึกหัดที่ 3: เพิ่ม brightness control ด้วย PWM
# (Exercise 3: Add brightness control with PWM)
#   - ใช้ PWM แทน Pin.OUT
#   - เพิ่มเมธอด set_brightness(percent)
#
# ==============================================================================

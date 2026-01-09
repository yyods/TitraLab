"""
แบบฝึกหัดที่ 1: คลาส StatusLED (Exercise 1: StatusLED Class)
============================================================

วัตถุประสงค์ (Objectives):
- เรียนรู้การสร้างคลาสใน MicroPython (Learn to create classes in MicroPython)
- เข้าใจ __init__, methods, และ attributes (Understand __init__, methods, and attributes)
- ควบคุม LED ผ่านการเขียนโปรแกรมเชิงวัตถุ (Control LED using OOP)

ความเชื่อมโยงกับเคมี (Chemistry Connection):
- LED สีแดง/เขียว ใช้แสดงสถานะการทำงาน เช่น pH ปกติ (เขียว) หรือ pH ผิดปกติ (แดง)
- Red/Green LEDs indicate system status, e.g., pH normal (green) or pH abnormal (red)

เกณฑ์ความสำเร็จ (Success Criteria):
[ ] สร้างคลาส StatusLED ได้ถูกต้อง (Create StatusLED class correctly)
[ ] เมธอด on() เปิด LED ได้ (on() method turns LED on)
[ ] เมธอด off() ปิด LED ได้ (off() method turns LED off)
[ ] เมธอด toggle() สลับสถานะ LED ได้ (toggle() method switches LED state)
[ ] เมธอด blink() กระพริบ LED ตามจำนวนครั้งที่กำหนด (blink() flashes LED specified times)
[ ] property is_on คืนค่าสถานะปัจจุบัน (is_on property returns current state)

ขาที่ใช้งาน (Pin Configuration):
- LED สีแดง (Red LED): GPIO2
- LED สีเขียว (Green LED): GPIO4
"""

from machine import Pin
import time


class StatusLED:
    """
    คลาสสำหรับควบคุม LED แสดงสถานะ (Class for controlling status LED)

    ใช้งานในห้องปฏิบัติการเคมีเพื่อแสดงสถานะการทำงาน
    Used in chemistry lab to indicate operational status

    Attributes:
        pin (Pin): ขา GPIO ที่เชื่อมต่อกับ LED (GPIO pin connected to LED)
        _state (bool): สถานะปัจจุบันของ LED (Current state of LED)

    Example:
        led = StatusLED(2)  # สร้าง LED ที่ขา GPIO2 (Create LED on GPIO2)
        led.on()            # เปิด LED (Turn on)
        led.off()           # ปิด LED (Turn off)
    """

    def __init__(self, pin_number: int):
        """
        สร้างออบเจ็กต์ StatusLED (Create StatusLED object)

        Args:
            pin_number: หมายเลขขา GPIO (GPIO pin number)

        คำแนะนำ (Hints):
        - ใช้ Pin(pin_number, Pin.OUT) สำหรับกำหนดเป็น output
        - เก็บสถานะเริ่มต้นเป็น False (LED ปิด)
        """
        # TODO: สร้าง Pin object สำหรับ LED (Create Pin object for LED)
        # self.pin = ???

        # TODO: กำหนดสถานะเริ่มต้น (Set initial state)
        # self._state = ???

        # TODO: ปิด LED เมื่อเริ่มต้น (Turn off LED on initialization)
        pass

    def on(self):
        """
        เปิด LED (Turn on LED)

        คำแนะนำ (Hints):
        - ใช้ self.pin.value(1) หรือ self.pin.on()
        - อย่าลืมอัปเดต self._state
        """
        # TODO: เปิด LED และอัปเดตสถานะ (Turn on LED and update state)
        pass

    def off(self):
        """
        ปิด LED (Turn off LED)

        คำแนะนำ (Hints):
        - ใช้ self.pin.value(0) หรือ self.pin.off()
        - อย่าลืมอัปเดต self._state
        """
        # TODO: ปิด LED และอัปเดตสถานะ (Turn off LED and update state)
        pass

    def toggle(self):
        """
        สลับสถานะ LED (Toggle LED state)

        ถ้า LED เปิดอยู่ให้ปิด, ถ้าปิดอยู่ให้เปิด
        If LED is on, turn off; if off, turn on

        คำแนะนำ (Hints):
        - ตรวจสอบ self._state ก่อน
        - เรียกใช้ self.on() หรือ self.off() ตามสถานะ
        """
        # TODO: สลับสถานะ LED (Toggle LED state)
        pass

    def blink(self, times: int = 3, delay_ms: int = 200):
        """
        กระพริบ LED ตามจำนวนครั้งที่กำหนด (Blink LED specified number of times)

        Args:
            times: จำนวนครั้งที่กระพริบ (Number of blinks)
            delay_ms: ระยะเวลาหน่วง (มิลลิวินาที) (Delay in milliseconds)

        คำแนะนำ (Hints):
        - ใช้ for loop วนตาม times
        - ใช้ time.sleep_ms() สำหรับหน่วงเวลา
        - แต่ละรอบ: on -> delay -> off -> delay
        """
        # TODO: กระพริบ LED (Blink LED)
        # for i in range(times):
        #     ???
        pass

    @property
    def is_on(self) -> bool:
        """
        ตรวจสอบว่า LED เปิดอยู่หรือไม่ (Check if LED is on)

        Returns:
            bool: True ถ้า LED เปิด, False ถ้าปิด

        คำแนะนำ (Hints):
        - ใช้ @property decorator เพื่อเข้าถึงเหมือน attribute
        - คืนค่า self._state
        """
        # TODO: คืนค่าสถานะ LED (Return LED state)
        pass


# =============================================================================
# โค้ดทดสอบ (Test Code)
# =============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบคลาส StatusLED (Testing StatusLED Class)")
    print("=" * 50)

    # สร้าง LED สีแดงและสีเขียว (Create red and green LEDs)
    led_red = StatusLED(2)    # GPIO2 - LED สีแดง (Red LED)
    led_green = StatusLED(4)  # GPIO4 - LED สีเขียว (Green LED)

    print("\n[Test 1] ทดสอบเปิด LED สีแดง (Test turning on red LED)")
    led_red.on()
    print(f"  LED สีแดงเปิด: {led_red.is_on}")  # ควรเป็น True (Should be True)
    time.sleep(1)

    print("\n[Test 2] ทดสอบปิด LED สีแดง (Test turning off red LED)")
    led_red.off()
    print(f"  LED สีแดงเปิด: {led_red.is_on}")  # ควรเป็น False (Should be False)
    time.sleep(1)

    print("\n[Test 3] ทดสอบ toggle LED สีเขียว (Test toggling green LED)")
    print(f"  ก่อน toggle: {led_green.is_on}")  # ควรเป็น False
    led_green.toggle()
    print(f"  หลัง toggle ครั้งที่ 1: {led_green.is_on}")  # ควรเป็น True
    time.sleep(0.5)
    led_green.toggle()
    print(f"  หลัง toggle ครั้งที่ 2: {led_green.is_on}")  # ควรเป็น False
    time.sleep(1)

    print("\n[Test 4] ทดสอบกระพริบ LED สีแดง 5 ครั้ง (Test blinking red LED 5 times)")
    led_red.blink(times=5, delay_ms=300)

    print("\n[Test 5] แสดงสถานะเหมือนในห้องปฏิบัติการ (Lab status indication)")
    print("  สีเขียว = ระบบปกติ, สีแดง = มีข้อผิดพลาด")
    print("  Green = System OK, Red = Error detected")

    # จำลองสถานะ pH ปกติ (Simulate normal pH status)
    print("\n  จำลอง: pH ปกติ (Simulating: Normal pH)")
    led_green.on()
    led_red.off()
    time.sleep(2)

    # จำลองสถานะ pH ผิดปกติ (Simulate abnormal pH status)
    print("  จำลอง: pH ผิดปกติ! (Simulating: Abnormal pH!)")
    led_green.off()
    led_red.blink(times=3, delay_ms=200)
    led_red.on()
    time.sleep(2)

    # ปิด LED ทั้งหมด (Turn off all LEDs)
    led_red.off()
    led_green.off()

    print("\n" + "=" * 50)
    print("การทดสอบเสร็จสิ้น (Testing completed)")
    print("=" * 50)

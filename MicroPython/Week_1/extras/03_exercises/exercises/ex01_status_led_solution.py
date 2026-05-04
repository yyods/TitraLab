"""
เฉลยแบบฝึกหัดที่ 1: คลาส StatusLED (Exercise 1 Solution: StatusLED Class)
=========================================================================

วัตถุประสงค์ (Objectives):
- เรียนรู้การสร้างคลาสใน MicroPython (Learn to create classes in MicroPython)
- เข้าใจ __init__, methods, และ attributes (Understand __init__, methods, and attributes)
- ควบคุม LED ผ่านการเขียนโปรแกรมเชิงวัตถุ (Control LED using OOP)

ความเชื่อมโยงกับเคมี (Chemistry Connection):
- LED สีแดง/เขียว ใช้แสดงสถานะการทำงาน เช่น pH ปกติ (เขียว) หรือ pH ผิดปกติ (แดง)
- Red/Green LEDs indicate system status, e.g., pH normal (green) or pH abnormal (red)

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
        """
        # สร้าง Pin object สำหรับ LED โหมด output (Create Pin object for LED in output mode)
        self.pin = Pin(pin_number, Pin.OUT)

        # กำหนดสถานะเริ่มต้นเป็น False (LED ปิด) (Set initial state to False - LED off)
        self._state = False

        # ปิด LED เมื่อเริ่มต้นเพื่อให้แน่ใจว่าสถานะตรงกัน (Turn off LED on init to ensure state matches)
        self.pin.value(0)

    def on(self):
        """
        เปิด LED (Turn on LED)
        """
        # เปิด LED โดยส่งค่า 1 ไปที่ขา (Turn on LED by sending 1 to pin)
        self.pin.value(1)

        # อัปเดตสถานะภายใน (Update internal state)
        self._state = True

    def off(self):
        """
        ปิด LED (Turn off LED)
        """
        # ปิด LED โดยส่งค่า 0 ไปที่ขา (Turn off LED by sending 0 to pin)
        self.pin.value(0)

        # อัปเดตสถานะภายใน (Update internal state)
        self._state = False

    def toggle(self):
        """
        สลับสถานะ LED (Toggle LED state)

        ถ้า LED เปิดอยู่ให้ปิด, ถ้าปิดอยู่ให้เปิด
        If LED is on, turn off; if off, turn on
        """
        # ตรวจสอบสถานะปัจจุบันและสลับ (Check current state and toggle)
        if self._state:
            self.off()
        else:
            self.on()

    def blink(self, times: int = 3, delay_ms: int = 200):
        """
        กระพริบ LED ตามจำนวนครั้งที่กำหนด (Blink LED specified number of times)

        Args:
            times: จำนวนครั้งที่กระพริบ (Number of blinks)
            delay_ms: ระยะเวลาหน่วง (มิลลิวินาที) (Delay in milliseconds)
        """
        # บันทึกสถานะก่อนกระพริบ (Save state before blinking)
        original_state = self._state

        # กระพริบตามจำนวนครั้งที่กำหนด (Blink specified number of times)
        for i in range(times):
            self.on()                    # เปิด LED (Turn on)
            time.sleep_ms(delay_ms)      # รอ (Wait)
            self.off()                   # ปิด LED (Turn off)
            time.sleep_ms(delay_ms)      # รอ (Wait)

        # คืนสถานะเดิม (Restore original state)
        if original_state:
            self.on()

    @property
    def is_on(self) -> bool:
        """
        ตรวจสอบว่า LED เปิดอยู่หรือไม่ (Check if LED is on)

        Returns:
            bool: True ถ้า LED เปิด, False ถ้าปิด
        """
        return self._state


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
    assert led_red.is_on == True, "ข้อผิดพลาด: LED ควรเปิด (Error: LED should be on)"
    time.sleep(1)

    print("\n[Test 2] ทดสอบปิด LED สีแดง (Test turning off red LED)")
    led_red.off()
    print(f"  LED สีแดงเปิด: {led_red.is_on}")  # ควรเป็น False (Should be False)
    assert led_red.is_on == False, "ข้อผิดพลาด: LED ควรปิด (Error: LED should be off)"
    time.sleep(1)

    print("\n[Test 3] ทดสอบ toggle LED สีเขียว (Test toggling green LED)")
    print(f"  ก่อน toggle: {led_green.is_on}")  # ควรเป็น False
    assert led_green.is_on == False, "ข้อผิดพลาด: LED ควรปิดตอนเริ่มต้น"

    led_green.toggle()
    print(f"  หลัง toggle ครั้งที่ 1: {led_green.is_on}")  # ควรเป็น True
    assert led_green.is_on == True, "ข้อผิดพลาด: LED ควรเปิดหลัง toggle"
    time.sleep(0.5)

    led_green.toggle()
    print(f"  หลัง toggle ครั้งที่ 2: {led_green.is_on}")  # ควรเป็น False
    assert led_green.is_on == False, "ข้อผิดพลาด: LED ควรปิดหลัง toggle ครั้งที่ 2"
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
    print("การทดสอบเสร็จสิ้น - ผ่านทุกข้อ! (Testing completed - All passed!)")
    print("=" * 50)

# ==============================================================================
# 02_led_class.py - LED Class for TitraLab
# ==============================================================================
# Week 1 Core: Simple LED control using OOP
# Time: ~20 minutes
#
# Chemistry Context (บริบทเคมี):
#   - Green LED (GPIO4): Ready/Running - กำลังหยดสารละลาย
#   - Red LED (GPIO2): Endpoint reached - ถึงจุดสมมูล
# ==============================================================================

from machine import Pin
import time


class LED:
    """
    คลาสควบคุม LED (LED Control Class)

    ตัวอย่าง (Example):
        led = LED(2, "Red")
        led.on()
        led.blink(3)
        led.off()
    """

    def __init__(self, pin_number, name="LED"):
        """
        สร้าง LED object (Create LED object)

        Args:
            pin_number (int): GPIO pin (2=Red, 4=Green)
            name (str): ชื่อ LED (LED name for display)
        """
        self.pin_number = pin_number
        self.name = name
        self.is_on = False

        # สร้าง Pin เป็น OUTPUT (Create Pin as OUTPUT)
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)  # เริ่มต้นปิด (Start off)

        print(f"LED '{name}' ready at GPIO{pin_number}")

    def on(self):
        """เปิด LED (Turn LED on)"""
        self._pin.value(1)
        self.is_on = True

    def off(self):
        """ปิด LED (Turn LED off)"""
        self._pin.value(0)
        self.is_on = False

    def toggle(self):
        """สลับสถานะ (Toggle state)"""
        if self.is_on:
            self.off()
        else:
            self.on()
        return self.is_on

    def blink(self, times=1, delay_sec=0.3):
        """
        กระพริบ LED (Blink LED)

        Args:
            times (int): จำนวนครั้ง (number of blinks)
            delay_sec (float): เวลาหน่วง (delay between on/off)
        """
        for _ in range(times):
            self._pin.value(1)
            time.sleep(delay_sec)
            self._pin.value(0)
            time.sleep(delay_sec)
        self.is_on = False

    def deinit(self):
        """ปิดและคืนทรัพยากร (Cleanup)"""
        self.off()


# ==============================================================================
# Test Code (โค้ดทดสอบ)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 40)
    print("LED Class Test")
    print("=" * 40)

    # สร้าง LED (Create LEDs)
    led_red = LED(2, "Red")
    led_green = LED(4, "Green")

    try:
        # ทดสอบ on/off
        print("\n--- Test on/off ---")
        led_red.on()
        time.sleep(0.5)
        led_red.off()

        # ทดสอบ toggle
        print("\n--- Test toggle ---")
        for i in range(4):
            led_green.toggle()
            time.sleep(0.3)

        # ทดสอบ blink
        print("\n--- Test blink ---")
        led_red.blink(3, 0.2)

        # สลับกัน (Alternate)
        print("\n--- Alternating LEDs ---")
        for _ in range(5):
            led_red.on()
            led_green.off()
            time.sleep(0.3)
            led_red.off()
            led_green.on()
            time.sleep(0.3)

    finally:
        led_red.deinit()
        led_green.deinit()
        print("\nDone!")

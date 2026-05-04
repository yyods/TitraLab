# ==============================================================================
# ex_status_led.py - In-Class Exercise: StatusLED Class
# ==============================================================================
# Week 1 Exercise: Create your own LED class (~15 minutes)
#
# Chemistry Context:
#   - Green (GPIO4): pH normal / system running
#   - Red (GPIO2): pH abnormal / endpoint reached
# ==============================================================================

from machine import Pin
import time


class StatusLED:
    """
    คลาสควบคุม LED แสดงสถานะ (Status LED Class)

    Example:
        led = StatusLED(2)
        led.on()
        led.blink(3)
        led.off()
    """

    def __init__(self, pin_number):
        """
        สร้าง StatusLED (Create StatusLED)

        TODO: Complete this method
        - Create Pin: self.pin = Pin(pin_number, Pin.OUT)
        - Initialize: self._state = False
        - Turn off LED
        """
        # TODO: Create Pin object
        # self.pin = ???
        # self._state = ???
        pass

    def on(self):
        """
        เปิด LED (Turn on)

        TODO: Set pin to 1, update _state to True
        """
        pass

    def off(self):
        """
        ปิด LED (Turn off)

        TODO: Set pin to 0, update _state to False
        """
        pass

    def blink(self, times=3, delay_ms=200):
        """
        กระพริบ LED (Blink LED)

        TODO: Loop 'times' times: on->delay->off->delay
        """
        pass

    @property
    def is_on(self):
        """ตรวจสอบสถานะ (Check state) - return self._state"""
        pass


# ==============================================================================
# Test Code - Do not modify
# ==============================================================================

if __name__ == "__main__":
    print("=" * 40)
    print("StatusLED Exercise Test")
    print("=" * 40)

    led_red = StatusLED(2)
    led_green = StatusLED(4)

    print("\n[Test 1] Turn on red LED")
    led_red.on()
    print(f"  is_on: {led_red.is_on}")  # Should be True
    time.sleep(1)

    print("\n[Test 2] Turn off red LED")
    led_red.off()
    print(f"  is_on: {led_red.is_on}")  # Should be False
    time.sleep(1)

    print("\n[Test 3] Blink green LED 5 times")
    led_green.blink(times=5, delay_ms=200)

    print("\n[Test 4] Lab simulation")
    print("  Green = Normal pH")
    led_green.on()
    time.sleep(2)

    print("  Red = pH Alert!")
    led_green.off()
    led_red.blink(3)
    led_red.on()
    time.sleep(2)

    led_red.off()
    led_green.off()

    print("\nTest completed!")

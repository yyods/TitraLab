# ==============================================================================
# 03_button_class.py - Button Class for TitraLab
# ==============================================================================
# Week 1 Core: Button reading with debounce
#
# Chemistry Context:
#   - Button 1 (GPIO34): Start/Stop titration
#   - Button 2 (GPIO35): Confirm calibration
#   - Button 3 (GPIO39): Cancel/Exit
#
# Note: GPIO34, 35, 39 are input-only (no internal pull-up)
#       TitraLab uses external pull-down resistors
# ==============================================================================

from machine import Pin
import time


class Button:
    """
    คลาสอ่านปุ่มกดพร้อม Debounce (Button class with debounce)

    Example:
        btn = Button(34, "Start")
        if btn.is_pressed():
            print("Button pressed!")
    """

    def __init__(self, pin_number, name="Button", debounce_ms=200):
        """
        สร้าง Button (Create Button object)

        Args:
            pin_number: GPIO pin (34, 35, or 39)
            name: ชื่อปุ่ม (button name)
            debounce_ms: debounce time in ms
        """
        self.pin_number = pin_number
        self.name = name
        self.debounce_ms = debounce_ms
        self._pin = Pin(pin_number, Pin.IN)
        self._last_press_time = 0
        self._was_pressed = False
        print(f"Button '{name}' ready at GPIO{pin_number}")

    def is_active(self):
        """ตรวจสอบว่ากดอยู่ (Check if currently pressed)"""
        return self._pin.value() == 1

    def is_pressed(self):
        """
        ตรวจจับการกดใหม่พร้อม debounce
        Returns True only ONCE per press
        """
        current_time = time.ticks_ms()
        is_active_now = self.is_active()

        if is_active_now and not self._was_pressed:
            if time.ticks_diff(current_time, self._last_press_time) > self.debounce_ms:
                self._last_press_time = current_time
                self._was_pressed = True
                return True

        if not is_active_now:
            self._was_pressed = False
        return False

    def wait_for_press(self, timeout_ms=None):
        """รอจนกว่าจะกด (Wait until pressed)"""
        start = time.ticks_ms()
        print(f"Waiting for {self.name}...")
        while True:
            if self.is_pressed():
                return True
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                print("Timeout!")
                return False
            time.sleep_ms(10)


# ==============================================================================
# Test Code
# ==============================================================================

if __name__ == "__main__":
    print("=" * 40)
    print("Button Class Test - Ctrl+C to stop")
    print("=" * 40)

    btn1 = Button(34, "Start")
    btn2 = Button(35, "Confirm")
    btn3 = Button(39, "Exit")

    count1, count2 = 0, 0

    try:
        while True:
            if btn1.is_pressed():
                count1 += 1
                print(f"Start: {count1}")
            if btn2.is_pressed():
                count2 += 1
                print(f"Confirm: {count2}")
            if btn3.is_active():
                print("Exit held")
                while btn3.is_active():
                    time.sleep_ms(50)
            time.sleep_ms(50)

    except KeyboardInterrupt:
        print(f"\nTotal: Start={count1}, Confirm={count2}")

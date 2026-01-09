# ==============================================================================
# titralab_simple.py - ไลบรารีฮาร์ดแวร์พื้นฐาน TitraLab (Simple TitraLab Library)
# ==============================================================================
# สัปดาห์ที่ 1: รวม class LED, Button, Buzzer ไว้ในไฟล์เดียว
# Week 1: Combines LED, Button, Buzzer classes in one file
#
# ไฟล์นี้เป็นไลบรารีง่ายๆ ที่นักเรียนสามารถ import ไปใช้ได้
# This file is a simple library that students can import and use
#
# วิธีใช้ (How to use):
#     from titralab_simple import LED, Button, Buzzer
#
#     led = LED(2, "Red")
#     btn = Button(35, "Select")
#     buzzer = Buzzer(26)
#
# เปรียบเทียบกับ Week 3:
#   - Week 1: คลาสง่ายๆ พื้นฐาน
#   - Week 3: คลาสที่ซับซ้อนขึ้น มี inheritance, composition
#
# ==============================================================================

from machine import Pin, PWM
import time


# ==============================================================================
# GPIO Pin Configuration สำหรับ TitraLab
# GPIO Pin Configuration for TitraLab
# ==============================================================================

# LED pins
LED_RED = 2      # GPIO2 - LED สีแดง (Red LED)
LED_GREEN = 4    # GPIO4 - LED สีเขียว (Green LED)

# Button pins (input-only, ไม่มี internal pull-up)
BUTTON_1 = 34    # GPIO34 - ปุ่ม 1
BUTTON_2 = 35    # GPIO35 - ปุ่ม 2
BUTTON_3 = 39    # GPIO39 - ปุ่ม 3

# Buzzer pin
BUZZER_PIN = 26  # GPIO26 - Buzzer (PWM)


# ==============================================================================
# LED Class
# ==============================================================================

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
        """สร้าง LED object (Create LED object)"""
        self.pin_number = pin_number
        self.name = name
        self.is_on = False
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)

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

    def blink(self, times=1, delay_sec=0.5):
        """กระพริบ (Blink)"""
        for _ in range(times):
            self.on()
            time.sleep(delay_sec)
            self.off()
            time.sleep(delay_sec)

    def deinit(self):
        """ทำความสะอาด (Cleanup)"""
        self.off()


# ==============================================================================
# Button Class
# ==============================================================================

class Button:
    """
    คลาสอ่านปุ่มกดพร้อม Debounce (Button Class with Debounce)

    ตัวอย่าง (Example):
        btn = Button(35, "Select")
        if btn.is_pressed():
            print("Pressed!")
    """

    def __init__(self, pin_number, name="Button", debounce_ms=200):
        """สร้าง Button object (Create Button object)"""
        self.pin_number = pin_number
        self.name = name
        self.debounce_ms = debounce_ms
        self._pin = Pin(pin_number, Pin.IN)
        self._last_press_time = 0
        self._was_pressed = False

    def read(self):
        """อ่านค่าดิบ (Read raw value)"""
        return self._pin.value()

    def is_active(self):
        """ตรวจว่ากดอยู่ไหม (Check if pressed)"""
        return self._pin.value() == 1

    def is_pressed(self):
        """ตรวจจับการกดใหม่ พร้อม debounce (Detect new press with debounce)"""
        current_time = time.ticks_ms()
        is_active_now = self.is_active()

        if is_active_now and not self._was_pressed:
            time_diff = time.ticks_diff(current_time, self._last_press_time)
            if time_diff > self.debounce_ms:
                self._last_press_time = current_time
                self._was_pressed = True
                return True

        if not is_active_now:
            self._was_pressed = False

        return False

    def wait_for_press(self, timeout_ms=None):
        """รอจนกว่าจะกด (Wait until pressed)"""
        start_time = time.ticks_ms()
        while True:
            if self.is_pressed():
                return True
            if timeout_ms is not None:
                if time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                    return False
            time.sleep_ms(10)


# ==============================================================================
# Buzzer Class
# ==============================================================================

class Buzzer:
    """
    คลาสควบคุม Buzzer ด้วย PWM (Buzzer Control Class using PWM)

    ตัวอย่าง (Example):
        buzzer = Buzzer(26)
        buzzer.beep()
        buzzer.success_sound()
        buzzer.deinit()
    """

    NOTES = {
        'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349,
        'G4': 392, 'A4': 440, 'B4': 494, 'C5': 523,
    }

    def __init__(self, pin_number=26, default_freq=2000):
        """สร้าง Buzzer object (Create Buzzer object)"""
        self.pin_number = pin_number
        self.default_freq = default_freq
        self._pin = Pin(pin_number, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(default_freq)
        self._pwm.duty(0)
        self._is_initialized = True

    def play_tone(self, frequency, duration_ms, duty=512):
        """เล่นเสียง (Play tone)"""
        self._pwm.freq(frequency)
        self._pwm.duty(duty)
        time.sleep_ms(duration_ms)
        self._pwm.duty(0)

    def play_note(self, note_name, duration_ms):
        """เล่นโน้ต (Play note by name)"""
        if note_name in self.NOTES:
            self.play_tone(self.NOTES[note_name], duration_ms)

    def beep(self, duration_ms=100):
        """เสียง beep สั้น (Short beep)"""
        self.play_tone(self.default_freq, duration_ms)

    def success_sound(self):
        """เสียงสำเร็จ (Success sound)"""
        for note in ['C4', 'E4', 'G4', 'C5']:
            self.play_note(note, 100)

    def error_sound(self):
        """เสียงผิดพลาด (Error sound)"""
        for freq in [800, 400, 200]:
            self.play_tone(freq, 100)

    def mute(self):
        """ปิดเสียง (Mute)"""
        self._pwm.duty(0)

    def deinit(self):
        """ทำความสะอาด (Cleanup)"""
        if self._is_initialized:
            self.mute()
            self._pwm.deinit()
            self._is_initialized = False


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบ titralab_simple library")
    print("(Testing titralab_simple library)")
    print("=" * 60)

    # สร้าง objects
    led_red = LED(LED_RED, "Red")
    led_green = LED(LED_GREEN, "Green")
    btn = Button(BUTTON_2, "Select")
    buzzer = Buzzer(BUZZER_PIN)

    print("\nกดปุ่ม 2 (GPIO35) เพื่อทดสอบ หรือ Ctrl+C เพื่อหยุด")
    print("(Press Button 2 to test, or Ctrl+C to stop)")

    try:
        count = 0
        while count < 5:
            if btn.is_pressed():
                count += 1
                print(f"\nกดครั้งที่ {count} (Press #{count})")

                # LED กระพริบ
                led_red.on()
                buzzer.beep()
                time.sleep(0.1)
                led_red.off()
                led_green.on()
                time.sleep(0.2)
                led_green.off()

            time.sleep_ms(10)

        print("\nครบ 5 ครั้ง - เล่นเสียงสำเร็จ")
        buzzer.success_sound()

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        led_red.deinit()
        led_green.deinit()
        buzzer.deinit()
        print("เสร็จสิ้น (Done)")

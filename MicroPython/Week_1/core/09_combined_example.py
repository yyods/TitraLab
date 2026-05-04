# ==============================================================================
# 09_combined_example.py - Integrated Titration Monitor
# ==============================================================================
# Week 1 Core: Combining LED + Button + TempSensor + Display
# Demonstrates "Composition" - combining multiple objects
# ==============================================================================

from machine import Pin, SPI
import time
import onewire
import ds18x20
from ili9341 import Display, color565
from xglcd_font import XglcdFont

# Simplified inline classes (คลาสแบบย่อ)
class LED:
    def __init__(self, pin):
        self._pin = Pin(pin, Pin.OUT)
        self._pin.value(0)
    def on(self): self._pin.value(1)
    def off(self): self._pin.value(0)

class Button:
    def __init__(self, pin, debounce=200):
        self._pin = Pin(pin, Pin.IN)
        self._debounce = debounce
        self._last = 0
        self._was = False

    def is_pressed(self):
        now = time.ticks_ms()
        active = self._pin.value() == 1
        if active and not self._was and time.ticks_diff(now, self._last) > self._debounce:
            self._last, self._was = now, True
            return True
        if not active: self._was = False
        return False

class TempSensor:
    def __init__(self, pin=16):
        self._ds = ds18x20.DS18X20(onewire.OneWire(Pin(pin)))
        roms = self._ds.scan()
        if not roms: raise RuntimeError("DS18B20 not found!")
        self._rom = roms[0]

    def read(self):
        self._ds.convert_temp()
        time.sleep_ms(750)
        return self._ds.read_temp(self._rom)

# Colors
WHITE, BLACK = color565(255,255,255), color565(0,0,0)
GREEN, RED = color565(0,255,0), color565(255,0,0)
YELLOW, BLUE = color565(255,255,0), color565(0,0,255)

# ==============================================================================
# Titration Monitor (ระบบติดตามการไทเทรชัน)
# ==============================================================================
class TitrationMonitor:
    """Simple titration monitor - shows temp, button toggles state, LEDs show status"""

    def __init__(self):
        print("Initializing Titration Monitor...")
        self.led_green, self.led_red = LED(4), LED(2)
        self.btn = Button(34)

        try:
            self.sensor = TempSensor(16)
            self.sensor_ok = True
        except RuntimeError:
            print("Warning: No temp sensor")
            self.sensor_ok = False

        spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
        self.display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0),
                               width=320, height=240, rotation=90)
        self.font = XglcdFont('EspressoDolce18x24.c', 18, 24)
        self.running = False
        print("Ready! Button 1 to toggle, Ctrl+C to exit")

    def draw_ui(self):
        self.display.clear()
        self.display.fill_rectangle(0, 0, 320, 35, BLUE)
        self.display.draw_text(60, 8, "Titration Monitor", self.font, WHITE)
        self._draw_status()

    def _draw_status(self):
        self.display.fill_rectangle(0, 180, 320, 60, BLACK)
        status, color = ("MONITORING", GREEN) if self.running else ("STOPPED", RED)
        self.display.draw_text(100, 200, status, self.font, color)

    def _draw_temp(self, temp):
        self.display.fill_rectangle(50, 80, 220, 80, BLACK)
        if temp:
            self.display.draw_text(100, 100, f"{temp:.2f} C", self.font, GREEN)
            self.display.draw_text(90, 130, f"({temp+273.15:.1f} K)", self.font, YELLOW)
        else:
            self.display.draw_text(80, 100, "No Sensor", self.font, RED)

    def toggle(self):
        self.running = not self.running
        if self.running:
            self.led_green.on(); self.led_red.off()
        else:
            self.led_green.off(); self.led_red.on()
        self._draw_status()

    def run(self):
        self.draw_ui()
        self.led_red.on()  # Start stopped
        last_update = 0

        try:
            while True:
                if self.btn.is_pressed():
                    self.toggle()

                now = time.ticks_ms()
                if self.running and time.ticks_diff(now, last_update) > 2000:
                    last_update = now
                    temp = self.sensor.read() if self.sensor_ok else None
                    if temp: print(f"Temp: {temp:.2f} C")
                    self._draw_temp(temp)

                time.sleep_ms(50)
        except KeyboardInterrupt:
            pass

    def cleanup(self):
        self.led_green.off(); self.led_red.off()
        self.display.clear()

# ==============================================================================
if __name__ == "__main__":
    monitor = TitrationMonitor()
    try:
        monitor.run()
    finally:
        monitor.cleanup()
        print("Done!")

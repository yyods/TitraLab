import machine
import time

led_red = machine.Pin(16, machine.Pin.OUT)
for i in range(10):
    led_red.on()
    time.sleep(0.5)
    led_red.off()
    time.sleep(0.5)
import machine
import time

led_red = machine.Pin(16, machine.Pin.OUT)
led_green = machine.Pin(22, machine.Pin.OUT)

while True:
    led_red.on()
    led_green.off()
    time.sleep(0.5)
    
    led_red.off()
    led_green.on()
    time.sleep(0.5)
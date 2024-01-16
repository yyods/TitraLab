import machine
import time

adc = machine.ADC(machine.Pin(34))

adc.width(machine.ADC.WIDTH_12BIT)

while True:
    pot_value = adc.read()
    print("Potentiometer Value:", pot_value)
    time.sleep(1)
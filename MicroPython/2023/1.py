import machine
from time import ticks_ms, sleep_ms
from ili9341 import Display, color565
from machine import Pin, SPI
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20

ONE_WIRE_BUS = 16
ow = OneWire(Pin(ONE_WIRE_BUS))
ds = DS18X20(ow)

SPI_BUS = 1
SCK_PIN = 14
MOSI_PIN = 13
DC_PIN = 27
CS_PIN = 15
RST_PIN = 0

spi = SPI(SPI_BUS, baudrate=40000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
display = Display(spi, dc=Pin(DC_PIN), cs=Pin(CS_PIN), rst=Pin(RST_PIN), width=320, height=240, rotation=90)

arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)

button1_pin = machine.Pin(34, machine.Pin.IN)
led1_pin = machine.Pin(21, machine.Pin.OUT)
button2_pin = machine.Pin(35, machine.Pin.IN)
led2_pin = machine.Pin(22, machine.Pin.OUT)

roms = ds.scan()

last_temp_update = 0

while True:
    current_time = ticks_ms()
    
    if current_time - last_temp_update >= 3000:  # ตรวจสอบเวลาทุก 3 วินาที
        last_temp_update = current_time

        for rom in roms:
            ds.convert_temp()
            sleep_ms(750)
            temp = ds.read_temp(rom)
            temp_str = "{:.2f} C".format(temp)
            
            display.clear(color=0, hlines=8)
            display.draw_text(90, 20, 'Temperature:', arcadepix, color565(255, 255, 255))
            display.draw_text(120, 70, temp_str, arcadepix, color565(0, 128, 0))

    if button1_pin.value() == 1:
        led1_pin.on()
    else:
        led1_pin.off()

    if button2_pin.value() == 1:
        led2_pin.on()
    else:
        led2_pin.off()
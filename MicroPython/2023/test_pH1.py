import machine
from time import ticks_ms, sleep_ms
from ili9341 import Display, color565
from machine import Pin, SPI, ADC
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

analog_pin = 25

# สร้างอ็อบเจกต์ ADC
adc = ADC(Pin(analog_pin))

# กำหนดค่าแอตเทนชันสำหรับแอนะล็อก
adc.atten(ADC.ATTN_11DB)
lastTime = 0

while True:
    # อ่านค่าแอนะล็อกและแปลงเป็นโวลต์
    analog_value = adc.read()
    voltage = analog_value

    # แสดงค่า voltage บนหน้าจอ ili9341
    display.clear(color=0, hlines=8)  # ลบหน้าจอ
    display.draw_text(90, 20, 'Voltage:', arcadepix, color565(255, 255, 255))  # แสดงข้อความ "Voltage:"
    display.draw_text(120, 70, "{:.2f} V".format(voltage), arcadepix, color565(0, 128, 0))  # แสดงค่า voltage

    # รอสักครู่ก่อนที่จะอ่านค่าใหม่
    sleep_ms(3000)

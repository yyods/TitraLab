from machine import Pin, ADC, PWM
from time import ticks_ms, sleep_ms
from ili9341 import Display, color565
from machine import Pin, SPI
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20

# กำหนดขาที่เชื่อมต่อกับไฟไฟหรี่
LIGHT_PIN = 12

# กำหนดขาที่เชื่อมต่อกับอนาล็อกอินพุท (potentiometer)
POT_PIN = 33

# กำหนดขาที่เชื่อมต่อกับ SPI
SPI_BUS = 1
SCK_PIN = 14
MOSI_PIN = 13
DC_PIN = 27
CS_PIN = 15
RST_PIN = 0

# สร้างอ็อบเจกต์ ADC สำหรับอ่านค่าอนาล็อกอินพุท
potentiometer = ADC(Pin(POT_PIN))
potentiometer.atten(ADC.ATTN_11DB)

# สร้างอ็อบเจกต์ PWM สำหรับควบคุมความสว่าง
light_pwm = PWM(Pin(LIGHT_PIN), freq=1000, duty=0)

# สร้างอ็อบเจกต์ SPI
spi = SPI(SPI_BUS, baudrate=40000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
display = Display(spi, dc=Pin(DC_PIN), cs=Pin(CS_PIN), rst=Pin(RST_PIN), width=320, height=240, rotation=90)

arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)

last_temp_update = 0

while True:
    current_time = ticks_ms()
    
    if current_time - last_temp_update >= 1:
        last_temp_update = current_time

        pot_value = potentiometer.read()
        pot_value = 4095 - pot_value
        light_duty = int((pot_value / 4095) * 1023)
        light_percentage = int((pot_value / 4095) * 100)
        light_pwm.duty(light_duty)

        # แสดงค่าการหมุนบนหน้าจอ
        """display.clear(color=0, hlines=8)"""
        display.draw_text(90, 90, 'Flow Rate:', arcadepix, color565(255, 255, 255))
        display.draw_text(120, 120,'{}%  '.format(light_percentage), arcadepix, color565(0, 128, 0))


from time import sleep, ticks_ms
from ili9341 import Display, color565
from machine import Pin, SPI
from xglcd_font import XglcdFont

led = Pin(17, Pin.OUT)    # 22 number in is Output
push_button = Pin(36, Pin.IN)  # 23 number pin is input

colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "AQUA": (0, 255, 255),
    "MAROON": (128, 0, 0),
    "DARKGREEN": (0, 128, 0),
    "NAVY": (0, 0, 128),
    "TEAL": (0, 128, 128),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 128, 0),
    "DEEP_PINK": (255, 0, 128),
    "CYAN": (128, 255, 255),
}

def test():
    print('This demo is for ILI9341')
    # Baud rate of 40000000 seems about the max
    spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0), width=320, height=240, rotation=90)
    
    print('Loading fonts...')
    print('Loading arcadepix')
    arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)
    
    display.draw_text(120, 20, 'TiTralab', arcadepix, color565(255, 255, 255))
    display.draw_text(90, 70, 'from Thonny.', arcadepix, color565(255, 255, 100))
    
    #sleep(5)
    #display.cleanup()
    
test()

while True:
  
  logic_state = push_button.value()
  if logic_state == True:     # if pressed the push_button
      led.value(1)             # led will turn ON
  else:                       # if push_button not pressed
      led.value(0)             # led will turn OFF
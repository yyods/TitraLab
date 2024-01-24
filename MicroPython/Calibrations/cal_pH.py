import machine 
from time import ticks_ms, sleep_ms, sleep_us
from ili9341 import Display, color565
from machine import Pin, ADC, PWM, SPI, Timer
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20
import uos


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
led1_pin = machine.Pin(2, machine.Pin.OUT)
button2_pin = machine.Pin(35, machine.Pin.IN)
led2_pin = machine.Pin(4, machine.Pin.OUT)
button3_pin = machine.Pin(39, machine.Pin.IN)

buzzer = PWM(machine.Pin(26, machine.Pin.OUT), freq=1000, duty=0)


POT1_PIN = 32
POT2_PIN = 33
pH_pin = 25
phValue = 0.00
voltage = 0.00
r_squared = 0.00
amount = 0.0

a=0
b,t,p,m=0,0,1,0
Time_avr = 40.97
ms=0
Flow5=0
TFlow02 = 0.0
TimeF = 0
TimeWA = 0.0


slope_m=-5.7901
intercept_b=16.769
Time1,Time2,Time3,TimeF2, = 0.0,0.0,0.0,0.0

x1=0.0
y1=0.0

x2=0.0
y2=0.0

x3=0.0
y3=0.0

Offset = 0.00
avgValue = 0

    
pH = ADC(Pin(pH_pin))
pH.atten(ADC.ATTN_11DB)


def calLinear(x1,y1,x2,y2,x3,y3):
    x=[x1, x2, x3]
    y=[y1, y2, y3]
    
    x_avr = (x[0]+x[1]+x[2])/3
    y_avr = (y[0]+y[1]+y[2])/3

    covariance = ((x[0]-x_avr)*(y[0]-y_avr)+(x[1]-x_avr)*(y[1]-y_avr)+(x[2]-x_avr)*(y[2]-y_avr))/2
    variance_x = (pow((x[0]-x_avr),2) + pow((x[1]-x_avr),2) + pow((x[2]-x_avr),2))/2
    variance_y = (pow((y[0]-y_avr),2) + pow((y[1]-y_avr),2) + pow((y[2]-y_avr),2))/2

    slope_m = covariance/variance_x
    intercept_b = y_avr-(slope_m*x_avr)

    #liner_y = slope_m*voltage+intercept_b สมการเส้นตรง
    liner_y = "y = "+str("{:.4f}".format(slope_m))+"x"+"+"+str("{:.4f}".format(intercept_b)) #สมการเส้นตรง

    y_pred1 = slope_m*x[0]+intercept_b
    y_pred2 = slope_m*x[1]+intercept_b
    y_pred3 = slope_m*x[2]+intercept_b

    variance_y_pred = (pow((y_pred1-y_avr),2) +pow((y_pred2-y_avr),2) +pow((y_pred3-y_avr),2) )/2

    r_square = variance_y_pred/variance_y
    
    return slope_m,intercept_b,r_square

def GetpH(slope_m,intercept_b):
    buf = [0] * 10
    for i in range(10):
        buf[i] = pH.read()
        sleep_ms(10)
    
    for i in range(9):
        for j in range(i+1, 10):
            if buf[i] > buf[j]:
                temps = buf[i]
                buf[i] = buf[j]
                buf[j] = temps
    
    avgValue = 0
    for i in range(2, 8):
        avgValue += buf[i]
    
    voltage = float(avgValue) * 3.5 / 4095 /6
    phValue = (slope_m * voltage + intercept_b)
    
    return voltage,phValue

def Phcaldisplays():           
    display.draw_text(65, 10, 'calibate pH sensor', arcadepix, color565(255, 255, 255))    
    display.draw_text(30, 35, 'pH voltage :', arcadepix, color565(255, 255, 255))  
    display.draw_text(20, 65, 'standardpH', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 65, 'voltage', arcadepix, color565(255, 255, 255))

    display.draw_text(60, 95, '4.00', arcadepix, color565(255, 193, 34))
    display.draw_text(60, 125, '7.00', arcadepix, color565(255, 193, 34))
    display.draw_text(60, 155, '10.00', arcadepix, color565(255, 193, 34))
    
    display.draw_text(190, 95, "{:.3f} V  ".format(x1), arcadepix, color565(255, 193, 34))
    display.draw_text(190, 125, "{:.3f} V  ".format(x2), arcadepix, color565(255, 193, 34))
    display.draw_text(190, 155, "{:.3f} V  ".format(x3), arcadepix, color565(255, 193, 34))


def soundIn():
    buzzer.freq(1000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.freq(3000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)
def soundOut():
    buzzer.freq(4000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.freq(1000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.freq(500)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)
def soundCal():
    buzzer.freq(4000)
    buzzer.duty(512)
    sleep_ms(300)
    buzzer.freq(1000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)
def beep():
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(50)
    buzzer.duty(0)
    
def beepbeep():
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)
    sleep_ms(100)
    buzzer.freq(2000)
    buzzer.duty(0)
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)
    sleep_ms(100)
    buzzer.freq(2000)
    buzzer.duty(0)
    
def beeeep():
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(1000)
    buzzer.duty(0)

Phcaldisplays()



while True:

    voltage,phValue = GetpH(slope_m,intercept_b)
    display.draw_text(180, 35, "{:.3f} V  ".format(voltage), arcadepix, color565(255, 193, 34))


    if x1 !=0 and y1 !=0 and x2 !=0 and y2 !=0 and x3 !=0 and y3 !=0:
        slope_m,intercept_b,r_squared = calLinear(x1,y1,x2,y2,x3,y3)
        voltage,phValue = GetpH(slope_m,intercept_b)
        display.draw_text(10, 185, 'r-squared = ', arcadepix, color565(255, 255, 255))
        display.draw_text(170, 185, " {:.3f} %".format(r_squared*100), arcadepix, color565(255, 193, 34))    

    if button2_pin.value() == 1:
        sleep_ms(5)
        beep()
        b=b+1
        if b > 2:
            b = 0
        
    if b == 0:
        display.draw_text(37, 155, '  ', arcadepix, color565(255, 193, 34))
        display.draw_text(37, 95,'>', arcadepix, color565(0, 255, 0))
        if button1_pin.value() == 1:
            soundCal()
            x1 = voltage
            y1 = 4.00
            display.clear()
            display.draw_text(60, 70, 'calibated for 4.00', arcadepix, color565(255, 255, 255))
            display.draw_text(30, 100, 'pH voltage :', arcadepix, color565(255, 255, 255))  
            display.draw_text(180, 100, "{:.3f} V  ".format(voltage), arcadepix, color565(255, 193, 34))
            sleep_ms(1500)
            display.clear()  
            Phcaldisplays()
        
            
    elif b == 1:
        display.draw_text(37, 95, '  ', arcadepix, color565(255, 193, 34))
        display.draw_text(37, 125,'>', arcadepix, color565(0, 255, 0))
        if button1_pin.value() == 1:
            soundCal()
            x2 = voltage
            y2 = 7.00
            display.clear()
            display.draw_text(60, 70, 'calibated for 7.00', arcadepix, color565(255, 255, 255))
            display.draw_text(30, 100, 'pH voltage :', arcadepix, color565(255, 255, 255))  
            display.draw_text(180, 100, "{:.3f} V  ".format(voltage), arcadepix, color565(255, 193, 34))
            sleep_ms(1500)
            display.clear()                       
            Phcaldisplays()
            
        
        
        
    elif b == 2:
        display.draw_text(37, 125, '  ', arcadepix, color565(255, 193, 34))
        display.draw_text(37, 155,'>', arcadepix, color565(0, 255, 0))
        if button1_pin.value() == 1:
            soundCal()
            x3 = voltage
            y3 = 10.00
            display.clear()
            display.draw_text(60, 70, 'calibated for 10.00', arcadepix, color565(255, 255, 255))
            display.draw_text(30, 100, 'pH voltage :', arcadepix, color565(255, 255, 255))  
            display.draw_text(180, 100, "{:.3f} V  ".format(voltage), arcadepix, color565(255, 193, 34))
            sleep_ms(1500)
            display.clear()
            Phcaldisplays()
            
            

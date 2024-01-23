import machine 
from time import ticks_ms, sleep_ms, sleep_us
from ili9341 import Display, color565
from machine import Pin, ADC, PWM, SPI, Timer
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20
import uos

timer_0 = Timer(0) # Between 0-3 for ESP32
timer_count = 0 # global variable
timer_secs = 0

ONE_WIRE_BUS = 16
ow = OneWire(Pin(ONE_WIRE_BUS))
ds = DS18X20(ow)
csv_filename1 = "data.csv"
csv_filename2 = "data2.csv"

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
TFlow5=0
TFlow02 = 0.0
TimeF = 0
TimeWA = 0.0
FlowRM2 = 0.0
mins=0
sec=0
Timerun=0

four=4.01
seven=7.01
ten=10.01

slope_m=-5.7901
intercept_b=16.769
Time1,Time2,Time3,TimeF2, = 0.0,0.0,0.0,0.0

x1=0.0
y1=0.0

x2=0.0
y2=0.0

x3=0.0
y3=0.0

secTmr = Timer(0)


potentiometer2 = ADC(Pin(POT2_PIN))
potentiometer2.atten(ADC.ATTN_11DB)
light2_pwm = PWM(machine.Pin(22, machine.Pin.OUT), freq=4000, duty=0)

Offset = 0.00
avgValue = 0

    
pH = ADC(Pin(pH_pin))
pH.atten(ADC.ATTN_11DB)

roms = ds.scan()

last_temp_update = 0

def motors():
    
    pot2_value = potentiometer2.read()
    pot2_value = 4095 - pot2_value
    light2_duty = int((pot2_value / 4095) * 1023)
    light2_percentage = int((pot2_value / 4095) * 100)
    
    
    return light2_percentage,light2_duty

    
def calFlowRatedisplays():
    display.draw_text(60, 10, 'Calibrate Flow Rate', arcadepix, color565(255, 255, 255))
                  
    display.draw_text(60, 55, 'Flow Rate:', arcadepix, color565(255, 255, 255))
    
    display.draw_text(40, 80, 'Time1 :', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 80,'{:.1f} sec  '.format(Time1/10), arcadepix, color565(255, 193, 34))
    
    display.draw_text(40, 105, 'Time2 :', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 105,'{:.1f} sec  '.format(Time2/10), arcadepix, color565(255, 193, 34))
    
    display.draw_text(40, 130, 'Time3 :', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 130,'{:.1f} sec  '.format(Time3/10), arcadepix, color565(255, 193, 34))

    
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
    
def T1(pin):
    global timer_count
    global timer_secs
    timer_count += 1
    timer_secs += 1


timer_0.init(mode=Timer.PERIODIC, period=1, callback=T1)  
   

    
calFlowRatedisplays()


"""................................cal flow rate...................................................""" 
while True:
    
    light2_percentage,light2_duty = motors()
    display.draw_text(190, 55,'{}%  '.format(light2_percentage), arcadepix, color565(255, 193, 34))
        
    if button2_pin.value() == 1:
        while button2_pin.value() == 1:
            sleep_ms(1)
        beep()
        b = b+1
        if b > 2:
            b = 0
    
    if button3_pin.value() == 1:
            beep()
            Time1=0
            Time2=0
            Time3=0
            display.draw_text(190, 80,'{:.2f} sec  '.format(Time1*0.001), arcadepix, color565(255, 193, 34))
            display.draw_text(190, 105,'{:.2f} sec  '.format(Time2*0.001), arcadepix, color565(255, 193, 34))
            display.draw_text(190, 130,'{:.2f} sec  '.format(Time2*0.001), arcadepix, color565(255, 193, 34))
    
    if b == 0:
        timer_count = Time1
        if button1_pin.value() == 1:
            while button1_pin.value() == 1:
                sleep_ms(5)
            t=1
            beep()
            
            while t==1:
                if button1_pin.value() == 1:
                    timer_count = Time1
                    beep()
                    t=0
                Time1 = timer_count
                light2_pwm.duty(light2_duty)
                display.draw_text(190, 80,'{:.2f} sec  '.format(Time1*0.001), arcadepix, color565(255, 193, 34))
        light2_pwm.duty(0)
        
        display.draw_text(15, 130, '  ', arcadepix, color565(255, 255, 255))
        display.draw_text(15, 80, '>', arcadepix, color565(0, 255, 0))
        
    if b == 1:
        timer_count = Time2
        if button1_pin.value() == 1:
            while button1_pin.value() == 1:
                sleep_ms(5)
            t=1
            beep()
            
            while t==1:
                if button1_pin.value() == 1:   
                    t=0
                    beep()  
                Time2 = timer_count
                light2_pwm.duty(light2_duty)
                display.draw_text(190, 105,'{:.2f} sec  '.format(Time2*0.001), arcadepix, color565(255, 193, 34))
        light2_pwm.duty(0)
                    
        display.draw_text(12, 80, '  ', arcadepix, color565(255, 255, 255))
        display.draw_text(15, 102, '>', arcadepix, color565(0, 255, 0))
        
    if b == 2:
        timer_count = Time3
        if button1_pin.value() == 1:
            while button1_pin.value() == 1:
                sleep_ms(5)
                t=1
            beep()
            
            while t==1:
                if button1_pin.value() == 1:
                    t=0
                    beep()
                Time3 = timer_count
                light2_pwm.duty(light2_duty)
                display.draw_text(190, 130,'{:.2f} sec  '.format(Time3*0.001), arcadepix, color565(255, 193, 34))
        light2_pwm.duty(0)
        
        display.draw_text(12, 105, '  ', arcadepix, color565(255, 255, 255))
        display.draw_text(15, 130, '>', arcadepix, color565(0, 255, 0))
       
    if Time1 != 0 and Time1 != 0 and Time3 != 0:
        Time_avr = ((Time1*0.001)+(Time2*0.001)+(Time3*0.001))/3
        TFlow5 = ((5.0*60)/Time_avr)*(light2_percentage/100)
        display.draw_text(20, 160, 'Time avr = ', arcadepix, color565(255, 255, 255))
        display.draw_text(160, 160, '{:.2f} sec  '.format(Time_avr), arcadepix, color565(255, 255, 255))
        display.draw_text(10, 190, 'Flow Rate = ', arcadepix, color565(255, 255, 255))
        display.draw_text(170, 190, '{:.2f} mL/min  '.format(TFlow5), arcadepix, color565(255, 255, 255))
        
    elif Time1 == 0 or Time1 == 0 or Time3 == 0:
        display.draw_text(20, 160, '                 ', arcadepix, color565(255, 255, 255))
        display.draw_text(160, 160, '                '.format(Time_avr), arcadepix, color565(255, 255, 255))
        display.draw_text(10, 190, '                 ', arcadepix, color565(255, 255, 255))
        display.draw_text(170, 190, '                '.format(TFlow5), arcadepix, color565(255, 255, 255))

        
    
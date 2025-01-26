import machine 
from time import ticks_ms, sleep_ms, sleep_us
from ili9341 import Display, color565
from machine import Pin, ADC, PWM, SPI, Timer, SoftSPI
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20
import os



timer_0 = Timer(0) # Between 0-3 for ESP32
timer_count = 0 # global variable
timer_secs = 0

ONE_WIRE_BUS = 16
ow = OneWire(Pin(ONE_WIRE_BUS))
ds = DS18X20(ow)
csv_filename1 = "Mode1.csv"
csv_filename2 = "Mode2.csv"

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


POT1_PIN = 25
POT2_PIN = 33
pH_pin = 32
potentiometer2 = ADC(Pin(POT2_PIN))
potentiometer2.atten(ADC.ATTN_11DB)
light2_pwm = PWM(machine.Pin(22, machine.Pin.OUT), freq=4000, duty=0)

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

four=4.00
seven=7.00
ten=10.00

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
    
def tempR():
    ds.convert_temp()
    sleep_ms(10)
    temp = ds.read_temp(rom)
    temp_str = " {:.2f} C ".format(temp)
    return temp_str

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
    
   
    """------------------------------------------------"""
    

def Homedisplays(): 
    display.draw_text(10, 20, 'Temp =', arcadepix, color565(255, 255, 255)) 
    display.draw_text(190, 20, 'pH =', arcadepix, color565(255, 255, 255))
    
    display.draw_text(50, 60, 'Mode 1', arcadepix, color565(255, 255, 255))
    display.draw_text(50, 90, 'Mode 2', arcadepix, color565(255, 255, 255))
    display.draw_text(50, 120, 'Calibrate pH sensor', arcadepix, color565(255, 255, 255))
    display.draw_text(50, 150, 'Calibrate Flow Rate', arcadepix, color565(255, 255, 255))
    display.draw_text(50, 180, 'Test PUMP', arcadepix, color565(255, 255, 255))
    display.draw_text(30, 60, '>', arcadepix, color565(0, 255, 0))
    
def dynamicHomedisplays():
    display.draw_text(90, 20, temp_str , arcadepix, color565(255, 193, 34))
    display.draw_text(230, 20, " {:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
    
def Phcaldisplays():         
    display.draw_text(55, 10, 'Calibrate pH sensor', arcadepix, color565(255, 255, 255))    
    display.draw_text(60, 35, 'pH Voltage:', arcadepix, color565(255, 255, 255))  
    display.draw_text(50, 65, 'Buffer', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 65, 'Voltage', arcadepix, color565(255, 255, 255))

    display.draw_text(60, 95, "{:.2f}" .format(four), arcadepix, color565(255, 193, 34))
    display.draw_text(60, 125, "{:.2f}" .format(seven), arcadepix, color565(255, 193, 34))
    display.draw_text(60, 155, "{:.2f}" .format(ten), arcadepix, color565(255, 193, 34))
    
    display.draw_text(190, 95, "{:.3f} V  ".format(x1), arcadepix, color565(255, 193, 34))
    display.draw_text(190, 125, "{:.3f} V  ".format(x2), arcadepix, color565(255, 193, 34))
    display.draw_text(190, 155, "{:.3f} V  ".format(x3), arcadepix, color565(255, 193, 34))
    
    display.draw_text(193, 215, 'Finish', arcadepix, color565(255, 255, 255))
    
def calFlowRatedisplays():
    display.draw_text(60, 10, 'Calibrate Flow Rate', arcadepix, color565(255, 255, 255))
                  
    display.draw_text(60, 55, 'Flow Rate:', arcadepix, color565(255, 255, 255))
    
    display.draw_text(40, 80, 'Time1 :', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 80,'{:.1f} sec  '.format(Time1/10), arcadepix, color565(255, 193, 34))
    
    display.draw_text(40, 105, 'Time2 :', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 105,'{:.1f} sec  '.format(Time2/10), arcadepix, color565(255, 193, 34))
    
    display.draw_text(40, 130, 'Time3 :', arcadepix, color565(255, 255, 255))
    display.draw_text(190, 130,'{:.1f} sec  '.format(Time3/10), arcadepix, color565(255, 193, 34))
    
    display.draw_text(193, 215, 'Finish', arcadepix, color565(255, 255, 255))

def Mode1displays():
    display.draw_text(120, 10, 'Mode 1', arcadepix, color565(255, 255, 255))
    display.draw_text(60, 45, 'Flow Rate 100% ONLY', arcadepix, color565(255, 255, 255))
    display.draw_text(10, 70, "FlowRate:", arcadepix, color565(255, 255, 255))
    display.draw_text(185, 70, "sec/0.2mL", arcadepix, color565(255, 255, 255))
    display.draw_text(185, 95, "sec", arcadepix, color565(255, 255, 255))
    display.draw_text(10, 95,"Time Spent:", arcadepix, color565(255, 255, 255))
    display.draw_text(150, 95,"{:}" .format(TimeF2), arcadepix, color565(255, 193, 34))
    display.draw_text(10, 120, "Value = ", arcadepix, color565(255, 255, 255))
    display.draw_text(80, 145, "Pause: 30 sec ", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 170, "pH value = ", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 195, "Last pH  = ", arcadepix, color565(255, 255, 255))
    
def Mode2displays():
    display.draw_text(120, 10, 'Mode 2', arcadepix, color565(255, 255, 255))
    display.draw_text(20, 45, 'Flow Rate ', arcadepix, color565(255, 255, 255))
    display.draw_text(210, 45, '%', arcadepix, color565(255, 255, 255))
    display.draw_text(20, 70, "Flow Rate:", arcadepix, color565(255, 255, 255))
    display.draw_text(210, 70, "mL/min", arcadepix, color565(255, 255, 255))
    display.draw_text(210, 95, "mL", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 95, "Value = ", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 145, "Time: ", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 170, "pH value = ", arcadepix, color565(255, 255, 255))
    display.draw_text(135, 145, "0 : 0 ", arcadepix, color565(255, 255, 255))
    display.draw_text(150, 95, "0.0 " .format(amount),  arcadepix, color565(255, 193, 34))
    display.draw_text(50, 195, "Last pH  = ", arcadepix, color565(255, 255, 255))

def testpumpDisplay():
    display.draw_text(120, 10, 'Test PUMP', arcadepix, color565(255, 255, 255))
    display.draw_text(20, 45, 'StatusPump :', arcadepix, color565(255, 255, 255))
    display.draw_text(210, 45, 'OFF', arcadepix, color565(255, 193, 34))
    display.draw_text(20, 75, 'TIME :', arcadepix, color565(255, 255, 255))
    display.draw_text(210, 75, '2 : 00', arcadepix, color565(255, 193, 34))
    
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
    
ii=0 
def make_headM1():
    try:
        with open(csv_filename1, "r") as f:
            f.read()
        ii=1
        
    except Exception as ENOENT:
        try:
            with open(csv_filename1, "w") as file:
                file.write("\nmL(x),pH(y)\n")
            print("สร้างไฟล์สำเร็จ")
        except Exception as e:
            print("ข้อผิดพลาดในการเปิดไฟล์ CSV:", e)
        ii=0
        
    if ii == 1:
        try:
            with open(csv_filename1, "a") as file:
                file.write("\nmL(x),pH(y)\n")
            print("เพิ่มไฟล์สำเร็จ")
        except Exception as e:
            print("ข้อผิดพลาดในการเปิดไฟล์ CSV:", e)
        sleep_ms(10)
    
def write_data_to_csvM1(pH, mL,):
    try:
        with open(csv_filename1, "a") as file:
            file.write("{},{}\n".format(mL, pH,))
        print("บันทึกข้อมูลลงใน CSV สำเร็จ")
    except Exception as e:
        print("ข้อผิดพลาดในการเขียนลงใน CSV:", e)


def make_headM2():
    try:
        with open(csv_filename2, "r") as f:
            f.read()
        ii=1
        print(ii)
    except Exception as ENOENT:
        try:
            with open(csv_filename2, "w") as file:
                file.write("\nmL(x),pH(y)\n")
            print("สร้างไฟล์สำเร็จ")
        except Exception as e:
            print("ข้อผิดพลาดในการเปิดไฟล์ CSV:", e)   
        ii=0
    if ii == 1:
        try:
            with open(csv_filename2, "a") as file:
                file.write("\nmL(x),pH(y)\n")
            print("เพิ่มไฟล์สำเร็จ")
        except Exception as e:
            print("ข้อผิดพลาดในการเปิดไฟล์ CSV:", e)
        sleep_ms(10)    
            
def write_data_to_csvM2(pH, mL,):
    try:
        with open(csv_filename2, "a") as file:
            file.write("{},{}\n".format(mL, pH,))
        print("บันทึกข้อมูลลงใน CSV สำเร็จ")
    except Exception as e:
        print("ข้อผิดพลาดในการเขียนลงใน CSV:", e)


timer_0.init(mode=Timer.PERIODIC, period=1, callback=T1)  
Homedisplays()
led1_pin.value(0)                           
led2_pin.value(0)

while True:
    current_time = ticks_ms()
    
    if current_time - last_temp_update >= 1:  #check every 1 sec 
        last_temp_update = current_time

        for rom in roms:
            temp_str = tempR()
            dynamicHomedisplays()                                          
            voltage,phValue = GetpH(slope_m,intercept_b)             

            if button2_pin.value() == 1:     
                while button2_pin.value() == 1:
                    sleep_ms(1)
                beep()
                p=p+1
                if p > 5:
                    p=1
                if p == 1:
                    display.draw_text(27, 180, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(27, 60, '>', arcadepix, color565(0, 255, 0))
                if p == 2:
                    display.draw_text(27, 60, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(27, 90, '>', arcadepix, color565(0, 255, 0))
                if p == 3:
                    display.draw_text(27, 90, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(27, 120, '>', arcadepix, color565(0, 255, 0))
                if p == 4:
                    display.draw_text(27, 120, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(27, 150, '>', arcadepix, color565(0, 255, 0))
                if p == 5:
                    display.draw_text(27, 150, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(27, 180, '>', arcadepix, color565(0, 255, 0))
       
            if button1_pin.value() == 1:        
                while button1_pin.value() == 1:
                    sleep_ms(1)
                beep()
                if p == 1:
                    m=1
                    display.clear()
                    Mode1displays()
                if p == 2:
                    m=2
                    display.clear()
                    Mode2displays()
                if p == 3:
                    m=3
                    display.clear()
                    Phcaldisplays()
                if p == 4:
                    m=4
                    display.clear()
                    calFlowRatedisplays()
                if p == 5:
                    m=5
                    display.clear()
                    testpumpDisplay()
                        

            """........................................cal PH..................................................."""           
            while m==3:
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
                    if b > 3:
                        b = 0
                    
                if b == 0:
                    display.draw_text(172, 215, '  ', arcadepix, color565(255, 193, 34))
                    display.draw_text(37, 95,'>', arcadepix, color565(0, 255, 0))
                    if button1_pin.value() == 1:
                        soundCal()
                        x1 = voltage
                        y1 = four
                        display.clear()
                        display.draw_text(60, 70, 'Calibrated for {:.2f}' .format(four), arcadepix, color565(255, 255, 255))
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
                        y2 = seven
                        display.clear()
                        display.draw_text(60, 70, 'Calibrated for {:.2f}' .format(seven), arcadepix, color565(255, 255, 255))
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
                        y3 = ten
                        display.clear()
                        display.draw_text(60, 70, 'Calibrated for {:.2f}' .format(ten), arcadepix, color565(255, 255, 255))
                        display.draw_text(30, 100, 'pH voltage :', arcadepix, color565(255, 255, 255))  
                        display.draw_text(180, 100, "{:.3f} V  ".format(voltage), arcadepix, color565(255, 193, 34))
                        sleep_ms(1500)
                        display.clear()
                        Phcaldisplays()
                        
                elif b == 3:
                    display.draw_text(34, 155, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(172, 215, '>', arcadepix, color565(0, 255, 0))
                    if button1_pin.value() == 1:
                        while button1_pin.value() == 1:
                            sleep_ms(1)
                        beep()
                        b=0
                        m=0
                        p=1
                        display.clear()
                        soundOut()
                        Homedisplays() 
                
            """................................cal flow rate...................................................""" 
            while m==4:
                
                light2_percentage,light2_duty = motors()
                display.draw_text(190, 55,'{}%  '.format(light2_percentage), arcadepix, color565(255, 193, 34))
                    
                if button2_pin.value() == 1:
                    while button2_pin.value() == 1:
                        sleep_ms(1)
                    beep()
                    b = b+1
                    if b > 3:
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
                    
                    display.draw_text(172, 215, '  ', arcadepix, color565(255, 255, 255))
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
                    display.draw_text(170, 190, '{:.2f} ML/min  '.format(TFlow5), arcadepix, color565(255, 255, 255))
                    
                elif Time1 == 0 or Time1 == 0 or Time3 == 0:
                    display.draw_text(20, 160, '                 ', arcadepix, color565(255, 255, 255))
                    display.draw_text(160, 160, '                '.format(Time_avr), arcadepix, color565(255, 255, 255))
                    display.draw_text(10, 190, '                 ', arcadepix, color565(255, 255, 255))
                    display.draw_text(170, 190, '                '.format(TFlow5), arcadepix, color565(255, 255, 255))
                    
                if b == 3:
                    display.draw_text(12, 130, '  ', arcadepix, color565(255, 255, 255))
                    display.draw_text(175, 215, '>', arcadepix, color565(0, 255, 0))
                    if button1_pin.value() == 1:
                        while button1_pin.value() == 1:
                            sleep_ms(1)
                        beep()
                        b=0
                        m=0
                        p=1
                        display.clear()
                        soundOut()
                        Homedisplays()
                    
                """..........................................mode1.....................................................""" 
                    
            while m==1:
                voltage,phValue = GetpH(slope_m,intercept_b)
                TFlow02 = "{:.1f} ".format(((0.2/5.0)*Time_avr))
                display.draw_text(150, 70, TFlow02, arcadepix, color565(255, 193, 34))
                display.draw_text(170, 170, " {:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                
                if button3_pin.value() == 1:
                    i = 0
                    while button3_pin.value() == 1:
                        i = i+1
                        sleep_ms(1000) 
                        if i == 3:
                            t=0
                            b=0
                            a=0
                            m=0
                            p=1
                            led1_pin.value(0)
                            led2_pin.value(0)
                            display.clear()
                            soundOut()
                            Homedisplays()                           
                                        
                if button1_pin.value() == 1:
                    while button1_pin.value() == 1:
                        sleep_ms(5)
                    make_headM1()
                    t=1
                    b=1
                    beep()
                    timer_count = 0
                    display.draw_text(170,195, "        ", arcadepix, color565(255, 193, 34))
                    display.draw_text(150, 120, "        ",  arcadepix, color565(255, 255, 255))
                    while t==1:
                        light2_pwm.duty(1023)
                        led1_pin.value(1)
                        led2_pin.value(0)
                        TimeF = timer_count
                        sleep_ms(1)
                        TimeF2 = '%.1f' %(TimeF*0.001)
                        sleep_ms(10)
                        TimeWA = '%.1f' %(((0.2/5.0)*Time_avr)*b)
                        sleep_ms(1)
                        display.draw_text(150, 95,"{:} " .format(TimeF2), arcadepix, color565(255, 193, 34))
                        sleep_ms(10)
                        if TimeF2 == TimeWA : 
                            sleep_ms(10)
                            light2_pwm.duty(0)
                            beepbeep()
                            a = 1
                            b += 1.0
                            while a == 1:
                                a = 0
                                timer_count = 1000
                                amount = ((TimeF*0.001)*5.0)/Time_avr
                                sleep_ms(1)
                                
                                display.draw_text(150, 120, "{:.2f} mL " .format(amount),  arcadepix, color565(255, 255, 255))
                                while timer_count < 30000:
                                    if button2_pin.value() == 1:
                                        sleep_ms(5)
                                        timer_count = 31000
                                        a=0
                                        t=0
                                        beeeep() 
                                        light2_pwm.duty(0)
                                        led1_pin.value(0)
                                        led2_pin.value(1)
                                        write_data_to_csvM1("{:.2f}".format(phValue), "{:.2f}".format(amount))
                                        display.draw_text(80, 145, "pause : 30 sec  ", arcadepix, color565(255, 255, 255))
                                        display.draw_text(170,195, "{:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                                    voltage,phValue = GetpH(slope_m,intercept_b)
                                    amount = ((TimeF*0.001)*5.0)/Time_avr
                                    display.draw_text(150, 120, "{:.2f} ML " .format(amount),  arcadepix, color565(255, 193, 34))
                                    display.draw_text(170, 170, " {:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                                    sleep_ms(1)
                                    display.draw_text(80, 145, "pause : {:} sec  " .format(int(timer_count*0.001)), arcadepix, color565(255, 255, 255))
                                if t == 0:
                                    display.draw_text(80, 145, "pause : 30 sec  " , arcadepix, color565(255, 255, 255))
                                    timer_count = TimeF
                                else:
                                    write_data_to_csvM1("{:.2f}".format(phValue), "{:.2f}".format(amount))
                                    display.draw_text(80, 145, "pause : 30 sec  " , arcadepix, color565(255, 255, 255))
                                    timer_count = TimeF    
                                
                        if button2_pin.value() == 1:
                            sleep_ms(5)
                            timer_count = 29000
                            a=0
                            t=0
                            beeeep() 
                            light2_pwm.duty(0)
                            led1_pin.value(0)
                            led2_pin.value(1)
                            write_data_to_csvM1("{:.2f}".format(phValue), "{:.2f}".format(amount))
                            display.draw_text(170,195, "{:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                            display.draw_text(80, 145, "pause : 30 sec ", arcadepix, color565(255, 255, 255))
                            amount = ((TimeF*0.001)*5.0)/Time_avr
                            display.draw_text(150, 120, "{:.2f} mL " .format(amount),  arcadepix, color565(255, 193, 34))
                            display.draw_text(170,195, "{:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                            
                    """...........................................Mode2.......................................................""" 
                    
            while m==2:
                light2_percentage,light2_duty = motors()
                voltage,phValue = GetpH(slope_m,intercept_b)
                
                FlowRM2 =  ((5.0*60.0)/Time_avr)*(float(light2_percentage)/100.00)
                display.draw_text(155, 45,"{:} ".format(light2_percentage), arcadepix, color565(255, 193, 34))
                display.draw_text(150, 70, "{:.2f} ".format(FlowRM2), arcadepix, color565(255, 193, 34))
                
                display.draw_text(170, 170, "{:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                
                if button3_pin.value() == 1:
                    i = 0
                    while button3_pin.value() == 1:
                        i = i+1
                        sleep_ms(1000)
                        if i == 3:
                            t=0
                            b=0
                            a=0
                            m=0
                            p=1
                            led1_pin.value(0)
                            led2_pin.value(0)
                            display.clear()
                            soundOut()
                            Homedisplays()                            
                                        
                if button1_pin.value() == 1:
                    while button1_pin.value() == 1:
                        sleep_ms(5)
                    make_headM2()
                    if light2_percentage == 0:
                        display.clear()
                        display.draw_text(20, 95, 'Please adjust FlowRate', arcadepix, color565(255, 255, 255))
                        sleep_ms(1500)
                        display.clear()
                        Mode2displays()
                    else:
                        t=1
                        beep()
                        timer_count = 0
                        timer_secs = 0
                        display.draw_text(170,195, "        ", arcadepix, color565(255, 193, 34))
                        display.draw_text(150, 95, "    ",  arcadepix, color565(255, 193, 34))
                        while t==1:
                            light2_pwm.duty(light2_duty)
                            led1_pin.value(1)
                            led2_pin.value(0)
                            TimeF = timer_count
                            Timerun = timer_secs
                            sec = Timerun*0.001
                            if int(sec) > 59:
                                timer_secs = 0
                                mins +=1
                            sleep_ms(10)
                            amount = (FlowRM2/60)*(TimeF*0.001)
                            sleep_ms(1)
                            display.draw_text(150, 95, "{:.2f} mL " .format(amount),  arcadepix, color565(255, 193, 34))
                            display.draw_text(135, 145, "{} : {} " .format(mins,int(sec)), arcadepix, color565(255, 255, 255))
                            if amount - b >= 1 :
                                write_data_to_csvM2("{:.2f}".format(phValue), "{:.2f}".format(amount))
                                beepbeep()
                                b +=1
  
                            if button2_pin.value() == 1:
                                sleep_ms(5)
                                a=0
                                t=0
                                b=0
                                mins = 0
                                beeeep() 
                                light2_pwm.duty(0)
                                led1_pin.value(0)
                                led2_pin.value(1)
                                write_data_to_csvM2("{:.2f}".format(phValue), "{:.2f}".format(amount))
                                display.draw_text(170,195, "{:.2f} ".format(phValue), arcadepix, color565(255, 193, 34))
                            
         #mode3-----------------Test Pump----------------------------------------------------------------------------
                            
            while m==5:
                light2_percentage,light2_duty = motors()
                light2_pwm.duty(0)
                display.draw_text(210, 45, 'OFF ', arcadepix, color565(255, 193, 34))
                
                if button1_pin.value() == 1:
                    while button1_pin.value() == 1:
                        sleep_ms(5)
                    secs = 0
                    mins = 2
                    p=1
                    t=0
                    timer_count = 0
                    timer_secs = 0
                while p==1:
                    if t==0:
                        mins = 1
                        secs = 59
                        t=1
                    
                    light2_pwm.duty(1023)
                    display.draw_text(210, 45, 'ON ', arcadepix, color565(255, 193, 34))
                    TimeF = timer_count
                    Timerun = timer_secs
                    sec = (Timerun*0.001)
                    print(int(sec))
                    if int(sec) == 1:
                       secs -=1
                       timer_secs = 0
                       if secs < 0 :
                           mins -= 1
                           secs = 59
                    display.draw_text(210, 75, "{} : {} " .format(mins,secs), arcadepix, color565(255, 193, 34))
                    
                    if mins == 0 and secs == 0 :
                        p=0
                        display.draw_text(210, 75, '2 : 00', arcadepix, color565(255, 193, 34))
                        
                    
                    if button2_pin.value() == 1:
                        while button2_pin.value() == 1:
                            sleep_ms(5)
                        p=0
                        display.draw_text(210, 75, '2 : 00', arcadepix, color565(255, 193, 34))                        
                    
                if button3_pin.value() == 1:
                    i = 0
                    while button3_pin.value() == 1:
                        i = i+1
                        sleep_ms(1000)
                        if i == 3:
                            p=0 
                            m=0                    
                            display.clear()
                            soundOut()
                            Homedisplays()
                
                    
                        
                    
                    
                
                
                
                            



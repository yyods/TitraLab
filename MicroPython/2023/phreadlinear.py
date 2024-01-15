import machine
from time import ticks_ms, sleep_ms
from ili9341 import Display, color565
from machine import Pin, ADC, PWM, SPI

pH_pin = 25
phValue = 0.00
voltage = 0.00

Offset = 0.00
avgValue = 0

pH = ADC(Pin(pH_pin))
pH.atten(ADC.ATTN_11DB)

m=0.0
c=0.0

x=2.54
y=6.86

x1=3.04
y1=4.01

x2=2.01
y2=10.01



def calLinear(x,y,x1,y1): 
    m = (y-y1)/(x-x1)
    c = y-m*x
    return m,c
m,c = calLinear(x,y,x1,y1)    
print(m,c)

while True:
    buf = [0] * 10
    for i in range(10):
        buf[i] = pH.read()
        sleep_ms(10)

    for i in range(9):
        for j in range(i+1, 10):
            if buf[i] > buf[j]:
                temp = buf[i]
                buf[i] = buf[j]
                buf[j] = temp

    avgValue = 0
    for i in range(2, 8):
        avgValue += buf[i]

    votage = float(avgValue) * 3.5 / 4095 /6
    phValue = 3.5 * votage + 0
    print(votage)



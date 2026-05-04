# ==============================================================================
# cal_flowrate.py - การสอบเทียบอัตราการไหลของปั๊ม (Pump Flow Rate Calibration)
# ==============================================================================
# โปรแกรมนี้ใช้สอบเทียบอัตราการไหลของปั๊มโดยวัดเวลาที่ใช้ปั๊มน้ำ 5 mL
# This program calibrates pump flow rate by measuring time to pump 5 mL
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การวัดอัตราการไหล (flow rate) ของปั๊ม
# 2. เข้าใจความสัมพันธ์ระหว่าง duty cycle กับอัตราการไหล
# 3. ใช้การวัดซ้ำ 3 ครั้งเพื่อหาค่าเฉลี่ย (precision)
#
# ความสำคัญในการไทเทรต (Importance in Titration):
# - ต้องทราบอัตราการไหลที่แม่นยำเพื่อคำนวณปริมาตรสารไทแทรนต์
# - อัตราการไหล (mL/min) = (ปริมาตร × 60) / เวลา
# - การ calibrate ที่หลาย duty cycle ช่วยเลือกความเร็วที่เหมาะสม
#
# Hardware Configuration:
# - GPIO 21: Pump (PWM output)
# - GPIO 34: Button 1 (Start/Stop timer) - input-only
# - GPIO 35: Button 2 (Select time slot) - input-only
# - GPIO 39: Button 3 (Reset) - input-only
# - GPIO 32: Potentiometer 2 (Adjust duty cycle)
# - GPIO 26: Buzzer (PWM output)
# ==============================================================================

import machine
from time import ticks_ms, sleep_ms, sleep_us
from ili9341 import Display, color565
from machine import Pin, ADC, PWM, SPI, Timer
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20
import uos

# ==============================================================================
# การตั้งค่า Timer (Timer Setup)
# ==============================================================================
timer_0 = Timer(0)  # ESP32 Timer 0-3
timer_count = 0     # ตัวนับมิลลิวินาที (Millisecond counter)
timer_secs = 0      # ตัวนับวินาที (Second counter)

# ==============================================================================
# การตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20 (Temperature Sensor Setup)
# ==============================================================================
ONE_WIRE_BUS = 16   # GPIO16 สำหรับ DS18B20 (GPIO16 for DS18B20)
ow = OneWire(Pin(ONE_WIRE_BUS))
ds = DS18X20(ow)
csv_filename1 = "data.csv"
csv_filename2 = "data2.csv"

# ==============================================================================
# การตั้งค่าจอแสดงผล TFT ILI9341 (TFT Display Setup)
# ==============================================================================
SPI_BUS = 1
SCK_PIN = 14    # GPIO14 - SPI Clock
MOSI_PIN = 13   # GPIO13 - SPI Data
DC_PIN = 27     # GPIO27 - Data/Command
CS_PIN = 15     # GPIO15 - Chip Select
RST_PIN = 0     # GPIO0  - Reset

spi = SPI(SPI_BUS, baudrate=40000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
display = Display(spi, dc=Pin(DC_PIN), cs=Pin(CS_PIN), rst=Pin(RST_PIN),
                  width=320, height=240, rotation=90)

# โหลดฟอนต์ (Load font)
arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)

# ==============================================================================
# การตั้งค่าปุ่มกด (Button Setup)
# ==============================================================================
# หมายเหตุ: GPIO34/35/39 เป็น input-only pins ไม่รองรับ internal pull resistors
# Note: GPIO34/35/39 are input-only, do NOT support internal pull resistors
# ต้องใช้ตัวต้านทาน pull-down ภายนอก (10K ohm)
# Must use external pull-down resistor (10K ohm)
button1_pin = machine.Pin(34, machine.Pin.IN)  # ปุ่ม 1 (Start/Stop)
led1_pin = machine.Pin(2, machine.Pin.OUT)     # LED สีแดง (Red LED)
button2_pin = machine.Pin(35, machine.Pin.IN)  # ปุ่ม 2 (Select)
led2_pin = machine.Pin(4, machine.Pin.OUT)     # LED สีเขียว (Green LED)
button3_pin = machine.Pin(39, machine.Pin.IN)  # ปุ่ม 3 (Reset)

# ==============================================================================
# การตั้งค่า Buzzer (Buzzer Setup)
# ==============================================================================
buzzer = PWM(machine.Pin(26, machine.Pin.OUT), freq=1000, duty=0)

# ==============================================================================
# การตั้งค่า ADC และ PWM (ADC and PWM Setup)
# ==============================================================================
POT1_PIN = 32   # Potentiometer 1
POT2_PIN = 33   # Potentiometer 2 - ปรับ duty cycle (Adjust duty cycle)
pH_pin = 25     # pH sensor pin

phValue = 0.00
voltage = 0.00
r_squared = 0.00
amount = 0.0

# ตัวแปรสถานะและการนับ (State and counting variables)
a = 0
b, t, p, m = 0, 0, 1, 0
Time_avr = 40.97  # เวลาเฉลี่ยเริ่มต้น (Initial average time)
ms = 0
TFlow5 = 0        # อัตราการไหลที่ 5 mL (Flow rate at 5 mL)
TFlow02 = 0.0
TimeF = 0
TimeWA = 0.0
FlowRM2 = 0.0
mins = 0
sec = 0
Timerun = 0

# ค่า pH มาตรฐาน (Standard pH values)
four = 4.01
seven = 7.01
ten = 10.01

# สมการเส้นตรง pH calibration (pH calibration linear equation)
slope_m = -5.7901
intercept_b = 16.769

# ตัวแปรเก็บเวลา 3 ครั้ง (Variables for 3 time measurements)
Time1, Time2, Time3, TimeF2 = 0.0, 0.0, 0.0, 0.0

# ค่า calibration points
x1, y1 = 0.0, 0.0
x2, y2 = 0.0, 0.0
x3, y3 = 0.0, 0.0

secTmr = Timer(0)

# ==============================================================================
# การตั้งค่า Potentiometer และ Pump PWM (Potentiometer and Pump PWM Setup)
# ==============================================================================
potentiometer2 = ADC(Pin(POT2_PIN))
potentiometer2.atten(ADC.ATTN_11DB)  # อ่านแรงดัน 0-3.3V (Read 0-3.3V)

# สำคัญ: ใช้ GPIO21 สำหรับปั๊ม (ไม่ใช่ GPIO22)
# IMPORTANT: Use GPIO21 for pump (not GPIO22)
pump_pwm = PWM(machine.Pin(21, machine.Pin.OUT), freq=4000, duty=0)

Offset = 0.00
avgValue = 0

# ==============================================================================
# การตั้งค่า ADC สำหรับ pH Sensor (pH Sensor ADC Setup)
# ==============================================================================
pH = ADC(Pin(pH_pin))
pH.atten(ADC.ATTN_11DB)

# สแกนหาเซ็นเซอร์อุณหภูมิ (Scan for temperature sensors)
roms = ds.scan()

last_temp_update = 0

# ==============================================================================
# ฟังก์ชันอ่าน Potentiometer (Read Potentiometer Function)
# ==============================================================================
def motors():
    """
    อ่านค่า potentiometer และแปลงเป็น duty cycle
    Read potentiometer value and convert to duty cycle

    Returns:
    - light2_percentage: เปอร์เซ็นต์ความเร็ว (0-100%)
    - light2_duty: ค่า duty cycle (0-1023)
    """
    pot2_value = potentiometer2.read()
    pot2_value = 4095 - pot2_value  # กลับค่า (Invert value)
    light2_duty = int((pot2_value / 4095) * 1023)
    light2_percentage = int((pot2_value / 4095) * 100)

    return light2_percentage, light2_duty


# ==============================================================================
# ฟังก์ชันแสดงผลหน้าจอ Calibration (Calibration Display Function)
# ==============================================================================
def calFlowRatedisplays():
    """
    แสดงหน้าจอสำหรับ calibrate flow rate
    Display flow rate calibration screen
    """
    display.draw_text(60, 10, 'Calibrate Flow Rate', arcadepix,
                      color565(255, 255, 255))

    display.draw_text(60, 55, 'Flow Rate:', arcadepix,
                      color565(255, 255, 255))

    display.draw_text(40, 80, 'Time1 :', arcadepix,
                      color565(255, 255, 255))
    display.draw_text(190, 80, '{:.1f} sec  '.format(Time1/10), arcadepix,
                      color565(255, 193, 34))

    display.draw_text(40, 105, 'Time2 :', arcadepix,
                      color565(255, 255, 255))
    display.draw_text(190, 105, '{:.1f} sec  '.format(Time2/10), arcadepix,
                      color565(255, 193, 34))

    display.draw_text(40, 130, 'Time3 :', arcadepix,
                      color565(255, 255, 255))
    display.draw_text(190, 130, '{:.1f} sec  '.format(Time3/10), arcadepix,
                      color565(255, 193, 34))


# ==============================================================================
# ฟังก์ชันเสียง (Sound Functions)
# ==============================================================================
def soundIn():
    """เสียงเริ่มต้น (Start sound)"""
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
    """เสียงหยุด (Stop sound)"""
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
    """เสียงบันทึก calibration (Calibration saved sound)"""
    buzzer.freq(4000)
    buzzer.duty(512)
    sleep_ms(300)
    buzzer.freq(1000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)

def beep():
    """เสียง beep สั้น (Short beep)"""
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(50)
    buzzer.duty(0)

def beepbeep():
    """เสียง beep สองครั้ง (Double beep)"""
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)
    sleep_ms(100)
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(100)
    buzzer.duty(0)

def beeeep():
    """เสียง beep ยาว (Long beep)"""
    buzzer.freq(2000)
    buzzer.duty(512)
    sleep_ms(1000)
    buzzer.duty(0)


# ==============================================================================
# Timer Callback (Timer Interrupt)
# ==============================================================================
def T1(pin):
    """
    Timer callback - นับเวลาทุก 1 ms
    Timer callback - count every 1 ms
    """
    global timer_count, timer_secs
    timer_count += 1
    timer_secs += 1


# ==============================================================================
# เริ่มต้น Timer (Initialize Timer)
# ==============================================================================
timer_0.init(mode=Timer.PERIODIC, period=1, callback=T1)

# แสดงหน้าจอเริ่มต้น (Display initial screen)
calFlowRatedisplays()

print("=" * 50)
print("การสอบเทียบอัตราการไหล (Flow Rate Calibration)")
print("ปุ่ม 1: เริ่ม/หยุดจับเวลา (Button 1: Start/Stop timer)")
print("ปุ่ม 2: เลือกช่องเวลา (Button 2: Select time slot)")
print("ปุ่ม 3: รีเซ็ต (Button 3: Reset)")
print("=" * 50)

# ==============================================================================
# โปรแกรมหลัก - Calibrate Flow Rate (Main Program)
# ==============================================================================
try:
    while True:

        # อ่านค่า potentiometer (Read potentiometer)
        light2_percentage, light2_duty = motors()
        display.draw_text(190, 55, '{}%  '.format(light2_percentage), arcadepix,
                          color565(255, 193, 34))

        # ปุ่ม 2: เลือกช่องเวลา (Button 2: Select time slot)
        if button2_pin.value() == 1:
            while button2_pin.value() == 1:
                sleep_ms(1)
            beep()
            b = b + 1
            if b > 2:
                b = 0

        # ปุ่ม 3: รีเซ็ตค่าเวลาทั้งหมด (Button 3: Reset all times)
        if button3_pin.value() == 1:
            beep()
            Time1 = 0
            Time2 = 0
            Time3 = 0
            display.draw_text(190, 80, '{:.2f} sec  '.format(Time1*0.001), arcadepix,
                              color565(255, 193, 34))
            display.draw_text(190, 105, '{:.2f} sec  '.format(Time2*0.001), arcadepix,
                              color565(255, 193, 34))
            display.draw_text(190, 130, '{:.2f} sec  '.format(Time3*0.001), arcadepix,
                              color565(255, 193, 34))

        # ช่องเวลาที่ 1 (Time slot 1)
        if b == 0:
            timer_count = Time1
            if button1_pin.value() == 1:
                while button1_pin.value() == 1:
                    sleep_ms(5)
                t = 1
                beep()

                while t == 1:
                    if button1_pin.value() == 1:
                        timer_count = Time1
                        beep()
                        t = 0
                    Time1 = timer_count
                    pump_pwm.duty(light2_duty)
                    display.draw_text(190, 80, '{:.2f} sec  '.format(Time1*0.001), arcadepix,
                                      color565(255, 193, 34))
            pump_pwm.duty(0)

            display.draw_text(15, 130, '  ', arcadepix, color565(255, 255, 255))
            display.draw_text(15, 80, '>', arcadepix, color565(0, 255, 0))

        # ช่องเวลาที่ 2 (Time slot 2)
        if b == 1:
            timer_count = Time2
            if button1_pin.value() == 1:
                while button1_pin.value() == 1:
                    sleep_ms(5)
                t = 1
                beep()

                while t == 1:
                    if button1_pin.value() == 1:
                        t = 0
                        beep()
                    Time2 = timer_count
                    pump_pwm.duty(light2_duty)
                    display.draw_text(190, 105, '{:.2f} sec  '.format(Time2*0.001), arcadepix,
                                      color565(255, 193, 34))
            pump_pwm.duty(0)

            display.draw_text(12, 80, '  ', arcadepix, color565(255, 255, 255))
            display.draw_text(15, 102, '>', arcadepix, color565(0, 255, 0))

        # ช่องเวลาที่ 3 (Time slot 3)
        if b == 2:
            timer_count = Time3
            if button1_pin.value() == 1:
                while button1_pin.value() == 1:
                    sleep_ms(5)
                    t = 1
                beep()

                while t == 1:
                    if button1_pin.value() == 1:
                        t = 0
                        beep()
                    Time3 = timer_count
                    pump_pwm.duty(light2_duty)
                    display.draw_text(190, 130, '{:.2f} sec  '.format(Time3*0.001), arcadepix,
                                      color565(255, 193, 34))
            pump_pwm.duty(0)

            display.draw_text(12, 105, '  ', arcadepix, color565(255, 255, 255))
            display.draw_text(15, 130, '>', arcadepix, color565(0, 255, 0))

        # คำนวณค่าเฉลี่ยและอัตราการไหลเมื่อมีค่าครบ 3 ค่า
        # Calculate average and flow rate when all 3 values are available
        # แก้ไข: เดิม Time1 != 0 and Time1 != 0 → Time1 != 0 and Time2 != 0
        # Fixed: was Time1 != 0 and Time1 != 0 → Time1 != 0 and Time2 != 0
        if Time1 != 0 and Time2 != 0 and Time3 != 0:
            # คำนวณเวลาเฉลี่ย (Calculate average time)
            Time_avr = ((Time1*0.001) + (Time2*0.001) + (Time3*0.001)) / 3
            # คำนวณอัตราการไหล (mL/min) (Calculate flow rate)
            # สูตร: (5 mL × 60 s/min) / เวลา(s) × (duty%/100)
            TFlow5 = ((5.0 * 60) / Time_avr) * (light2_percentage / 100)
            display.draw_text(20, 160, 'Time avr = ', arcadepix,
                              color565(255, 255, 255))
            display.draw_text(160, 160, '{:.2f} sec  '.format(Time_avr), arcadepix,
                              color565(255, 255, 255))
            display.draw_text(10, 190, 'Flow Rate = ', arcadepix,
                              color565(255, 255, 255))
            display.draw_text(170, 190, '{:.2f} mL/min  '.format(TFlow5), arcadepix,
                              color565(255, 255, 255))

        # ลบค่าเมื่อไม่ครบ 3 ค่า (Clear values when not all 3 available)
        # แก้ไข: เดิม Time1 == 0 or Time1 == 0 → Time1 == 0 or Time2 == 0
        # Fixed: was Time1 == 0 or Time1 == 0 → Time1 == 0 or Time2 == 0
        elif Time1 == 0 or Time2 == 0 or Time3 == 0:
            display.draw_text(20, 160, '                 ', arcadepix,
                              color565(255, 255, 255))
            display.draw_text(160, 160, '                ', arcadepix,
                              color565(255, 255, 255))
            display.draw_text(10, 190, '                 ', arcadepix,
                              color565(255, 255, 255))
            display.draw_text(170, 190, '                ', arcadepix,
                              color565(255, 255, 255))

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    pump_pwm.duty(0)
    pump_pwm.deinit()
    buzzer.duty(0)
    buzzer.deinit()
    timer_0.deinit()
    display.clear()
    print("ปิด PWM, Buzzer และ Timer แล้ว (PWM, Buzzer and Timer released)")

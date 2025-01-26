"""
Project: SciLabPro
Author: [ Hemmawan Saon, Nuttakit Deemon, Saowapak Vchirawongkwin, Sumrit Wacharasindhu and Viwat Vchirawongkwin ]
Email: [ sumrit.w@chula.ac.th  ]
Version: 1.0.0
License: SciLabPro License
Description: A powerful tool for automatic titration and sensor calibration.
Github: [https://github.com/yyods/TitraLab]
"""

from time import ticks_ms, sleep_ms, ticks_us, ticks_diff  # นำเข้า time เพื่อใช้จัดการเวลาหน่วยมิลลิวินาทีและไมโครวินาที
from ili9341 import Display, color565  # นำเข้า Display และ color565 จากไลบรารี ili9341 สำหรับจัดการจอแสดงผล
from machine import Pin, ADC, PWM, SPI, Timer # นำเข้า Pin, ADC, PWM, SPI, Timer สำหรับควบคุมพอร์ตและอุปกรณ์อื่นๆ
from xglcd_font import XglcdFont  # นำเข้า XglcdFont สำหรับการแสดงผลฟอนต์บนจอ
from onewire import OneWire  # นำเข้า OneWire สำหรับเชื่อมต่อกับเซ็นเซอร์ที่ใช้การสื่อสารแบบ 1-wire
from ds18x20 import DS18X20  # นำเข้า DS18X20 เพื่ออ่านข้อมูลจากเซ็นเซอร์วัดอุณหภูมิ DS18B20
import os     # นำเข้า os เพื่อจัดการไฟล์
import utime  # Import MicroPython's time module
import math   # สำหรับปัดเศษตัวเลข
import uasyncio as asyncio  # ใช้ asyncio เพื่อเพิ่มประสิทธิภาพการควบคุมแบบ asynchronous
import gc

#------------------ตัวเลือก สามารถ เติมข้อมูลเอง จาก mV จาก buffer pH 4.00,7.00,10.00 (การทดลอง week 2) ---------------------#

# กำหนดค่าเริ่มต้นการตั้งค่าสำหรับสมการเส้นตรง(มีหรือไม่มีข้อมูลก็ได้)

slope_m     = -5.7901  # ค่าสโลปเริ่มต้นของสมการเส้นตรง 
intercept_b = 16.769   # ค่า intercept เริ่มต้นของสมการเส้นตรง 

#----------------------------------------------------------------#

# ตั้งค่าฟอนต์สำหรับการแสดงผลบนจอ
arcadepix = XglcdFont('EspressoDolce18x24.c', 18, 24)  # ฟอนต์สำหรับการแสดงผล
# กำหนดค่า Timer ที่จะใช้ในระบบ โดยใช้ Timer 0 ของ ESP32
timer_0     = Timer(0)
timer_count = 0  # ตัวแปร global เพื่อเก็บค่าการนับเวลาของ timer
timer_secs  = 0  # ตัวแปร global เก็บเวลานับเป็นวินาที
selected_option = 1  # ตัวเลือกเริ่มต้น

#-------------------------------ตั้งค่า PIN--------------------------------#

# ตั้งค่า Pin และ SPI สำหรับจอแสดงผล
SPI_BUS  = 1   # กำหนดใช้ SPI bus ที่ 1
SCK_PIN  = 14  # Pin SCK (clock) ใช้ GPIO14
MOSI_PIN = 13  # Pin MOSI ใช้ GPIO13
DC_PIN   = 27  # Pin Data/Command ใช้ GPIO27
CS_PIN   = 15  # Pin Chip Select ใช้ GPIO15
RST_PIN  = 0   # Pin Reset ใช้ GPIO0

# ตั้งค่า Pin สำหรับเซ็นเซอร์ temp DS18B20
ONE_WIRE_BUS = 16                          # ใช้ Pin GPIO16 สำหรับการสื่อสาร OneWire
ow           = OneWire(Pin(ONE_WIRE_BUS))  # กำหนดให้ Pin 16 เป็น OneWire bus
ds           = DS18X20(ow)                 # สร้าง object ds สำหรับอ่านข้อมูลจากเซ็นเซอร์temp DS18B20

# ค้นหา OneWire อุปกรณ์ที่เชื่อมต่อกับ DS18B20
roms = ds.scan()

# ตั้งค่า Pin สำหรับปุ่ม และ LED
led1_pin    = Pin( 2, Pin.OUT)  # ไฟ LED 1 ที่ GPIO2
led2_pin    = Pin( 4, Pin.OUT)  # ไฟ LED 2 ที่ GPIO4
button1_pin = Pin(34, Pin.IN)   # ปุ่ม 1     ที่ GPIO34
button2_pin = Pin(35, Pin.IN)   # ปุ่ม 2     ที่ GPIO35
button3_pin = Pin(39, Pin.IN)   # ปุ่ม 3     ที่ GPIO39

# ตั้งค่า Pin และ PWM สำหรับ Buzzer
buzzer = PWM(Pin(26, Pin.OUT), freq=1000, duty=0)  # Buzzer ที่ GPIO26

# ตั้งค่า Pin สำหรับ potentiometer และ pH sensor
POT1_PIN = 32  # Pin Potentiometer ตัวที่ 1 ใช้ GPIO25
POT2_PIN = 33  # Pin Potentiometer ตัวที่ 2 ใช้ GPIO33
pH_pin   = 25  # Pin pH sensor           ใช้ GPIO32
light2_pwm = PWM(Pin(21, Pin.OUT), freq=4000, duty=0)  # pump ตั้งค่า PWM บน GPIO22 สำหรับไฟ LED

# กำหนดค่า SPI bus และ Display
spi     = SPI(SPI_BUS, baudrate=40000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))  # กำหนดการเชื่อมต่อ SPI bus
display = Display(spi, dc=Pin(DC_PIN), cs=Pin(CS_PIN), rst=Pin(RST_PIN), width=320, height=240, rotation=90) 

# ตั้งค่า ADC สำหรับการวัดค่า pH sensor
pH = ADC(Pin(pH_pin))
pH.atten(ADC.ATTN_11DB)

# ---------------------------------- ฟังก์ชันวัดค่าอุณหภูมิจากเซ็นเซอร์ DS18B20 ---------------------------------- #

def tempR():
    if roms:                                   # Check if there are any detected sensors
        ds.convert_temp()
        sleep_ms(10)                           # Wait for the temperature conversion to complete
        temp = ds.read_temp(roms[0])           # Read temperature using the first ROM address
        temp_str = " {:.2f} C ".format(temp)
        return temp_str
    else:
        return "  0.00"
# ---------------------------------- ฟังก์ชันสำหรับการ load ค่า ที่calibrate ไว้ก่อนหน้า ---------------------------------- #
# ฟังก์ชันโหลดค่าที Calibration pH
def load_calibrationpH():
    global last_saved_time  # กำหนดตัวแปรเพื่อเก็บวันที่
    try:
        with open("data_calibrate.txt", "r") as file:
            lines = file.readlines()
            slope = float(lines[0].strip())
            intercept = float(lines[1].strip())
            # อ่านวันที่
            if len(lines) > 2:
                last_saved_time = lines[2].strip().replace("Last saved: ", "")
            else:
                last_saved_time = "N/A"
            print(f"Calibration pH loaded: {slope, intercept} ")
            return slope, intercept
    except Exception as e:
        print(f"Error loading calibration data: {e}")
        last_saved_time = None
        return None, None

# ฟังก์ชันโหลดค่า Flow Rate
def load_flowrate():
    global last_saved_flowrate_time  # ใช้ตัวแปร global เก็บวันที่
    try:
        with open("data_flowrate.txt", "r") as file:
            lines = file.readlines()
            flow_rate = float(lines[0].strip())
            # โหลดวันที่ที่บันทึกไว้
            if len(lines) > 1:
                last_saved_flowrate_time = lines[1].strip().replace("Last saved: ", "")
            else:
                last_saved_flowrate_time = "N/A"
            print(f"Flow rate loaded: {flow_rate} ml/sec")
            return flow_rate
    except Exception as e:
        print(f"Error loading flow rate data: {e}")
        last_saved_flowrate_time = None
        return None
    
# โหลดค่า Flow Rate เมื่อเริ่มต้นโปรแกรม
data_flowrate = load_flowrate()
if data_flowrate is None:
    print("No flow rate data found. Please calibrate first.")

# ---------------------------------- ฟังก์ชันสำหรับการคำนวน pH ---------------------------------- #

# pH Calibration เมื่อเริ่มต้นโปรแกรม
slope_m, intercept_b = load_calibrationpH()
if slope_m is None or intercept_b is None:
    print("No calibration data found. Using default values.")
    slope_m = -5.7901  # ค่าสโลปเริ่มต้น
    intercept_b = 16.769  # ค่า intercept เริ่มต้น

def GetpH(slope_m,intercept_b): 
    buf = [0] * 10 #[บันทึกไปใน list ทั้งหมด 10 ค่า]
    for i in range(10):
        buf[i] = pH.read() 
        sleep_ms(10)
    # การจัดเรียงค่าในลิสต์จากน้อยไปมากเพื่อใช้คำนวณค่าเฉลี่ย
    for i in range(9):
        for j in range(i+1, 10):
            if buf[i] > buf[j]:  
                temps = buf[i]
                buf[i] = buf[j]
                buf[j] = temps
    #เลือกค่าระหว่าง 2-8 มาคำนวณเพื่อลดค่าที่สูงสุดและต่ำสุดเพื่อเพิ่มความแม่นยำมากขึ้น
    avgValue = 0
    for i in range(2, 8): # คำนวณค่าเฉลี่ยโดยไม่รวมค่าที่มากสุดและน้อยสุด
        avgValue += buf[i]
    voltage = float(avgValue) * 3.3 / 4095 /6   # แปลงค่า ADC เป็นค่าแรงดันไฟฟ้า
    phValue = (slope_m * voltage + intercept_b) # คำนวณค่า pH จากสมการเส้นตรง
    return voltage,phValue # ส่งค่าแรงดันและค่า pH กลับไป

# ---------------------------------- ฟังก์ชันแสดงผล Display ---------------------------------- #
def dynamicHomedisplays():
    temp_value = tempR()  # อ่านค่าอุณหภูมิจากเซ็นเซอร์
    voltage, phValue = GetpH(slope_m, intercept_b)  # ใช้ค่า slope และ intercept จากไฟล์ Calibration
    # แสดงค่า Temp ใหม่
    display.draw_text(25, 35, "Temp={} ".format(temp_value), arcadepix, color565(255, 255, 0))
    display.draw_text(200, 35, "pH= {:.2f}".format(phValue), arcadepix, color565(255, 0, 0))  # แสดงค่า pH
    
# ฟังก์ชันแสดงผลหน้า Homedisplay ครั้งแรก
def Homedisplays_initial():
    global menu_items
    display.clear()  # ล้างหน้าจอเฉพาะครั้งแรก
    # ส่วนหัว (Header)
    display.fill_rectangle(0, 0, 319, 30, color565(0, 102, 204))
    display.draw_text(90, 3, "Home Display", arcadepix, color565(255, 255, 255))

    # แสดงตัวเลือกทั้งหมดพร้อมกัน
    for i, item in enumerate(menu_items, start=1):
        y_position = 60 + (i - 1) * 30  # คำนวณตำแหน่ง Y
        color = color565(0, 255, 0) if i == selected_option else color565(255, 255, 255)
        display.draw_text(20, y_position, f"{'>' if i == selected_option else '  '} {item}", arcadepix, color)
        
# ฟังก์ชันแสดงผลหน้าจอ LCD ในหน้าจอแสดงผลหลัก
menu_items = [
    "1. Calibrate pH sensor",
    "2. pH sensor Test",
    "3. Calibrate Flow Rate",
    "4. Flow Rate Test",
    "5. Purge",
    "6. Full Auto Titration"
]
selected_option = 1  # ตัวเลือกเริ่มต้น

# ฟังก์ชันแสดงผลหน้าจอเมนู
def Homedisplays(selected_option, previous_option=None):
    global menu_items

    # ส่วนหัว (Header)
    if previous_option is None:  # แสดงส่วนหัวเฉพาะครั้งแรก
        display.fill_rectangle(0, 0, 319, 30, color565(0, 102, 204))
        display.draw_text(90, 3, "Home Display", arcadepix, color565(255, 255, 255))

    # อัปเดตเฉพาะตำแหน่งที่เปลี่ยน
    for i, item in enumerate(menu_items, start=1):
        y_position = 60 + (i - 1) * 30  # คำนวณตำแหน่ง Y สำหรับแต่ละรายการ
        x_position = 20  # ตำแหน่ง X เริ่มต้น
        is_selected = i == selected_option
        was_selected = i == previous_option
        color = color565(0, 255, 0) if is_selected else color565(255, 255, 255)

        # อัปเดตเฉพาะตำแหน่งที่เปลี่ยน
        if was_selected or is_selected:
            display.fill_rectangle(0, y_position, 319, 30, color565(0, 0, 0))  # ลบข้อความเก่า
            display.draw_text(x_position, y_position, f"{'>' if is_selected else '  '} {item}", arcadepix, color)

#โชว์โลโก้ ก่อนการใช้งาน
def draw_gradient_background():
    for y in range(240):
        red = int((30 + (y / 240) * 100))  # ไล่สีแดง
        blue = int((80 + (y / 240) * 150))  # ไล่สีฟ้า
        display.draw_hline(0, y, 320, color565(red, 0, blue))

def draw_logo_and_effects():
    # วาดข้อความโลโก้
    display.draw_text(105, 70, "SciLabPro", arcadepix, color565(255, 255, 255))
    display.draw_text(13, 160, "Elevating Scientific Learning", arcadepix, color565(0, 255, 255))
    
    # เพิ่มเส้น Grid
    for x in range(0, 320, 20):
        for y in range(0, 240, 20):
            display.draw_pixel(x, y, color565(50, 255, 255))

    # วาด Glow รอบโลโก้
    for i in range(5):  # วาดขอบ Glow หลายชั้น
        display.draw_circle(155, 80, 60 + i, color565(0, 200 - i * 40, 255))
    sleep_ms(1000)
    
#-------------------------------------------ฟังก์ชันแสดงหน้า Tutor Setup------------------------------------------#

def show_tutor_screen():
    
    options = ["YES", "NO"]
    selected_option = 0  # เริ่มต้นที่ตัวเลือกแรก

    display.clear()  # ล้างหน้าจอก่อนครั้งแรก
    display.draw_text(30, 30, "Would you like guidance ", arcadepix, color565(255, 51, 218))
    display.draw_text(15, 60, "before using the system?", arcadepix, color565(255, 51, 218))
    display.draw_text(85, 150, "YES", arcadepix, color565(0, 255, 0) if selected_option == 0 else color565(255, 255, 255))
    display.draw_text(185, 150, "NO", arcadepix, color565(0, 255, 0) if selected_option == 1 else color565(255, 255, 255))

    while True:
        # ตรวจจับการเลื่อนเมนูด้วย button2
        if button2_pin.value() == 1:
            while button2_pin.value() == 1:
                sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม
            beep()
            selected_option = (selected_option + 1) % len(options)  # สลับระหว่าง YES และ NO
            # อัปเดตเฉพาะตัวเลือกที่เปลี่ยน
            display.draw_text(85, 150, "YES", arcadepix, color565(0, 255, 0) if selected_option == 0 else color565(255, 255, 255))
            display.draw_text(185, 150, "NO", arcadepix, color565(0, 255, 0) if selected_option == 1 else color565(255, 255, 255))

        # ตรวจจับการเลือกตัวเลือกด้วย button1
        if button1_pin.value() == 1:
            while button1_pin.value() == 1:
                sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม
            beep()
            if selected_option == 0:  # หากเลือก YES
                show_device_setup_guide()
            elif selected_option == 1:  # หากเลือก NO
                display.clear()
            break  # ออกจากลูปและเริ่ม Homedisplay ทันที

# ฟังก์ชันแสดง Device Setup Guide ก่อนเข้า home display
def show_device_setup_guide():
    setup_steps = [
        "LED1         to Pin 02",
        "LED2         to Pin 04",
        "DS18B20      to Pin 16",
        "CONTROL_1    to Pin 21",
        "CONTROL_2    to Pin 22",
        "PH_PROBE     to Pin 25",
        "BUZZER       to Pin 26",
        "POT_1         to Pin 32",
        "POT_2        to Pin 33",
        "Button_1      to Pin 34",
        "Button_2     to pin 35",
        "Button_3     to pin 39",
        "-----> Button guide <-----", 
        "> Press Button_1 ",
        "to select an option",
        "> Press Button_2",
        "to move to the next item",
        "> Hold Button_3 for 3 sec",
        "to return to the main menu"
    ]

    items_per_page = 5  # จำนวนข้อความต่อหน้า
    total_pages = (len(setup_steps) + items_per_page - 1) // items_per_page
    current_page = 0  # เริ่มต้นที่หน้าแรก

    while True:
        display.clear()  # ล้างหน้าจอทุกครั้งที่เปลี่ยนหน้า

        # วาดกรอบรอบข้อความทั้งหมด
        display.fill_rectangle(5, 40, 310, 190, color565(0, 0,0))  # พื้นหลังกรอบ
        display.draw_rectangle(5, 40, 310, 190, color565(255, 255, 255))  # เส้นกรอบสีขาว

        # แสดงหัวข้อ
        display.fill_rectangle(0, 0, 319, 35, color565(0, 102, 204))  # สีพื้นหลังหัวข้อ
        display.draw_text(50, 5, "Device Setup Guide", arcadepix, color565(255, 255, 255))  # ชื่อหัวข้อ

        # คำนวณข้อความที่จะอยู่ในหน้านี้
        start_index = current_page * items_per_page
        end_index = min(start_index + items_per_page, len(setup_steps))
        y_position = 50

        # แสดงข้อความในหน้านี้
        for step in setup_steps[start_index:end_index]:
            display.draw_text(20, y_position, step, arcadepix, color565(102, 255, 255))
            y_position += 28

        # แสดงคำแนะนำการกดปุ่ม
        if current_page < total_pages - 1:
            display.draw_text(28, 195, "Press Button_1 for next", arcadepix, color565(0, 255, 0))
        else:
            display.draw_text(28, 195, "Press Button_1 to start", arcadepix, color565(0, 255, 0))

        # ตรวจจับการกดปุ่ม
        while True:
            if button1_pin.value() == 1:
                while button1_pin.value() == 1:
                    sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม
                beep()

                # หากยังไม่ใช่หน้าสุดท้าย เลื่อนไปหน้าถัดไป
                if current_page < total_pages - 1:
                    current_page += 1
                else:
                    display.clear()
                    return  # ออกจากฟังก์ชันเมื่อจบหน้าสุดท้าย
                break

#------------------------------------------ ตั้งค่า Buzzer ----------------------------------------------#

# ฟังก์ชันการเล่นเสียงเมื่อมีการอินพุตเข้า
def soundIn():
    buzzer.freq(1000)  # ตั้งความถี่เสียงที่ 1000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังของเสียงที่ 512
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.freq(2000)  # เปลี่ยนความถี่เสียงเป็น 2000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียงใหม่
    sleep_ms(100)      # หน่วงเวลาอีกครั้ง
    buzzer.freq(3000)  # เปลี่ยนความถี่เสียงเป็น 3000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียงใหม่
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.duty(0)     # หยุดการทำงานของเสียง (ความดัง 0)

# ฟังก์ชันการเล่นเสียงเมื่อมีการปิดระบบ
def soundOut():
    buzzer.freq(4000)  # ตั้งความถี่เสียงที่ 4000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียงที่ 512
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.freq(1000)  # เปลี่ยนความถี่เป็น 1000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียงใหม่
    sleep_ms(100)      # หน่วงเวลาอีกครั้ง
    buzzer.freq(500)   # เปลี่ยนความถี่เป็น 500 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียงใหม่
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.duty(0)     # หยุดการทำงานของเสียง

# ฟังก์ชันการเล่นเสียงสำหรับการปรับเทียบ
def soundCal():
    buzzer.freq(4000)  # ตั้งความถี่เสียงที่ 4000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียง
    sleep_ms(300)      # หน่วงเวลา 300 มิลลิวินาที
    buzzer.freq(1000)  # เปลี่ยนความถี่เสียงเป็น 1000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียงใหม่
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.duty(0)     # หยุดการทำงานของเสียง

# ฟังก์ชันเสียงสั้น ๆ
def beep():
    buzzer.freq(2000)  # ตั้งความถี่เสียงที่ 2000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียง
    sleep_ms(50)       # หน่วงเวลา 50 มิลลิวินาที
    buzzer.duty(0)     # หยุดการทำงานของเสียง

# ฟังก์ชันเสียงสั้น ๆ 2 ครั้ง
def beepbeep():
    buzzer.freq(2000)  # ตั้งความถี่เสียงที่ 2000 Hz
    buzzer.duty(512)   # ตั้งระดับความดังเสียง
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.duty(0)     # หยุดการทำงานของเสียง
    sleep_ms(100)      # หน่วงเวลาอีกครั้ง
    buzzer.freq(2000)  # ตั้งความถี่เสียงที่ 2000 Hz
    buzzer.duty(0)     # หยุดเสียงชั่วคราว
    buzzer.freq(2000)  # ตั้งความถี่เสียงเดิม
    buzzer.duty(512)   # เปิดเสียงใหม่
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.duty(0)     # หยุดเสียง
    sleep_ms(100)      # หน่วงเวลา 100 มิลลิวินาที
    buzzer.freq(2000)  # ตั้งความถี่เสียงที่ 2000 Hz
    buzzer.duty(0)     # หยุดการทำงานของเสียง

# ฟังก์ชันเล่นเสียงเป็นระยะยาว
def beeep():
    buzzer.freq(2000)  # ตั้งความถี่เสียงที่ 2000 Hz
    buzzer.duty(512)   # ตั้งความดังเสียงที่ 512
    sleep_ms(1000)     # หน่วงเวลา 1000 มิลลิวินาที (1 วินาที)
    buzzer.duty(0)     # หยุดการทำงานของเสียง

# --------------------------------- ฟังก์ชันการแสดงผลหน้าจอภายใน mode 1 (Calibrate pH sensor)---------------------------# 

r_squared = 0.00  # ค่า r-squared สำหรับการคำนวณ

# ฟังก์ชันแสดงผลของ Mode 1 calibrate pH
# กำหนดค่า buffer สำหรับการเทียบค่าสำหรับการปรับเทียบ pH
four  = 4.00
seven = 7.00
ten   = 10.00

# ตัวแปรสำหรับการคำนวณสมการเส้นตรง
x1 = 0.0
y1 = 0.0
x2 = 0.0
y2 = 0.0
x3 = 0.0
y3 = 0.0

previous_voltage = 0.0  # กำหนดค่าเริ่มต้นให้ previous_voltage

def calphdisplays(selected_sub_option):
    global last_saved_time  # เพิ่มตัวแปรเพื่อเก็บวันที่และเวลา
    
    # แสดงชื่อเมนูและหัวข้อที่ไม่เปลี่ยนแปลง
    display.draw_text(55, 10, 'Calibrate pH Sensor', arcadepix, color565(255, 255, 255))
    display.draw_text(60, 35, 'pH Voltage:', arcadepix, color565(255, 51, 51))
    display.draw_text(260, 35, "V", arcadepix, color565(255, 51, 51))
    display.draw_text(50, 65, 'Buffer', arcadepix, color565(204, 153, 255))
    display.draw_text(190, 65, 'Voltage', arcadepix, color565(204, 153, 255))

    # สีตัวเลือกที่เลือกเป็นสีเขียว ที่เหลือเป็นสีขาว
    color_options = [color565(0, 255, 0) if i == selected_sub_option else color565(255, 255, 255) for i in range(4)]

    # แสดงค่า pH Buffer พร้อมการเปลี่ยนสี
    display.draw_text(60, 95, "{:.2f}".format(four), arcadepix, color_options[0])
    display.draw_text(60, 125, "{:.2f}".format(seven), arcadepix, color_options[1])
    display.draw_text(60, 155, "{:.2f}".format(ten), arcadepix, color_options[2])
    display.draw_text(130, 185, "Finish", arcadepix, color_options[3])

    # แสดงค่า Voltage โดยไม่เปลี่ยนสี
    display.draw_text(190, 95, "{:.3f} V".format(x1), arcadepix, color565(255, 193, 34))
    display.draw_text(190, 125, "{:.3f} V".format(x2), arcadepix, color565(255, 193, 34))
    display.draw_text(190, 155, "{:.3f} V".format(x3), arcadepix, color565(255, 193, 34))

     # แสดงวันที่และเวลาที่บันทึกล่าสุด
    if last_saved_time:
        display.draw_text(30, 210, f"Last Calibrate: {last_saved_time}", arcadepix, color565(102, 255, 255))
    else:
        display.draw_text(70, 210, "Last Calibrate: N/A", arcadepix, color565(255, 0, 0))

def validate_calibration(r_squared):
    if r_squared >= 0.98:
        display.draw_text(75, 200, "Calibration Valid", arcadepix, color565(0, 255, 0))  # สีเขียว
    else:
        display.draw_text(75, 200, "Calibration Poor", arcadepix, color565(255, 0, 0))  # สีแดง
    sleep_ms(2000)

# ฟังก์ชันคำนวณสมการเส้นตรงจากจุดที่กำหนด
def calLinear(x1, y1, x2, y2, x3, y3):
    x = [x1, x2, x3]
    y = [y1, y2, y3]
    x_avr = sum(x) / len(x)  # ค่าเฉลี่ย x
    y_avr = sum(y) / len(y)  # ค่าเฉลี่ย y

    # คำนวณ covariance และ variance
    covariance = sum([(xi - x_avr) * (yi - y_avr) for xi, yi in zip(x, y)]) / len(x)
    variance_x = sum([(xi - x_avr) ** 2 for xi in x]) / len(x)

    slope_m = covariance / variance_x if variance_x != 0 else 0  # ตรวจสอบว่า variance_x != 0
    intercept_b = y_avr - (slope_m * x_avr)

    # คำนวณค่า y ที่คาดการณ์
    y_pred = [(slope_m * xi + intercept_b) for xi in x]

    # คำนวณ SS_residual และ SS_total
    ss_residual = sum([(yi - yi_pred) ** 2 for yi, yi_pred in zip(y, y_pred)])
    ss_total = sum([(yi - y_avr) ** 2 for yi in y])

    # คำนวณ R^2
    r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0

    if r_squared < 0.98:  # หากค่า r-squared ต่ำกว่า 0.98
        print("Warning: Low R-squared value. Calibration may not be accurate.")

    return slope_m, intercept_b, r_squared

# ฟังก์ชันอัปเดตค่า Voltage
def update_voltage_display(voltage):
    global previous_voltage  # เรียกใช้งานตัวแปร global
    if abs(voltage - previous_voltage) >= 0.002:  # อัปเดตเมื่อค่าเปลี่ยนมากกว่า 0.002
        # ลบพื้นที่เฉพาะค่า Voltage เดิม
        display.fill_rectangle(222, 35, 37, 30, color565(0, 0, 0))
        # แสดงค่า Voltage ใหม่
        display.draw_text(190, 35, "{:.3f} ".format(voltage), arcadepix, color565(255, 51, 51))
        previous_voltage = voltage  # อัปเดตค่า voltage ล่าสุด
        sleep_ms(50)  # เพิ่มความหน่วงเล็กน้อย

# Function to save calibration data to a file
def save_calibration(slope, intercept):
    try:
        with open("data_calibrate.txt", "w") as file:
            file.write(f"{slope}\n")
            file.write(f"{intercept}\n")
            # Get the current date only
            current_time = utime.localtime()
            formatted_date = "{:04d}-{:02d}-{:02d}".format(
                current_time[0], current_time[1], current_time[2]
            )
            file.write(f"Last saved: {formatted_date}\n")
        print("Calibration data saved successfully.")
    except Exception as e:
        print(f"Error saving calibration data: {e}")

# ฟังก์ชันสำหรับการ Calibrate pH Sensor
def menu1_loop():
    global b, m, x1, x2, x3, y1, y2, y3, slope_m, intercept_b, r_squared

    b = 0  # เริ่มต้นตำแหน่งที่ Buffer 4.00
    m = 1  # เปิดใช้งานโหมด Calibrate
    calphdisplays(selected_sub_option=b)  # แสดงตำแหน่งเริ่มต้น

    while m == 1:
        voltage, phValue = GetpH(slope_m, intercept_b)  # อ่านค่า Voltage และ pH
        update_voltage_display(voltage)  # อัปเดตค่า Voltage บนหน้าจอ
        
        if button2_pin.value() == 1:  # เปลี่ยนตำแหน่งการเลือก
            while button2_pin.value() == 1:
                sleep_ms(1)
            b = (b + 1) % 4  # วนตำแหน่งการเลือก (Buffer 4.00, 7.00, 10.00, Finish)
            beep()
            calphdisplays(selected_sub_option=b)  # อัปเดตตำแหน่งสีที่เลือก

        if button1_pin.value() == 1:  # เลือกตำแหน่งที่ต้องการ
            while button1_pin.value() == 1:
                sleep_ms(1)

            if b == 0:  # Calibrate Buffer 4.00
                soundCal()
                x1 = voltage
                y1 = four
                display.clear()
                display.draw_text(60, 70, 'Calibrated for {:.2f}'.format(four), arcadepix, color565(255, 255, 255))
                display.draw_text(55, 100, 'pH voltage:', arcadepix, color565(255, 255, 255))
                display.draw_text(185, 100, "{:.3f} V".format(voltage), arcadepix, color565(255, 193, 34))
                sleep_ms(1500)
                display.clear()
                calphdisplays(selected_sub_option=b)

            elif b == 1:  # Calibrate Buffer 7.00
                soundCal()
                x2 = voltage
                y2 = seven
                display.clear()
                display.draw_text(60, 70, 'Calibrated for {:.2f}'.format(seven), arcadepix, color565(255, 255, 255))
                display.draw_text(55, 100, 'pH voltage:', arcadepix, color565(255, 255, 255))
                display.draw_text(185, 100, "{:.3f} V".format(voltage), arcadepix, color565(255, 193, 34))
                sleep_ms(1500)
                display.clear()
                calphdisplays(selected_sub_option=b)

            elif b == 2:  # Calibrate Buffer 10.00
                soundCal()
                x3 = voltage
                y3 = ten
                display.clear()
                display.draw_text(60, 70, 'Calibrated for {:.2f}'.format(ten), arcadepix, color565(255, 255, 255))
                display.draw_text(55, 100, 'pH voltage:', arcadepix, color565(255, 255, 255))
                display.draw_text(185, 100, "{:.3f} V".format(voltage), arcadepix, color565(255, 193, 34))
                sleep_ms(1500)
                display.clear()
                calphdisplays(selected_sub_option=b)

            if b == 3:  # Finish Calibration
                if x1 != 0 and x2 != 0 and x3 != 0:  # ตรวจสอบค่าทั้งหมด
                    slope_m, intercept_b, r_squared = calLinear(x1, y1, x2, y2, x3, y3)
                    save_calibration(slope_m, intercept_b)  # บันทึกค่าคาลิเบรต
                    display.clear()
                    display.draw_text(50, 70, 'Calibration Complete', arcadepix, color565(255, 255, 255))
                    display.draw_text(40, 100, 'R-squared:', arcadepix, color565(255, 255, 255))
                    display.draw_text(175, 100, "{:.2f} %".format(r_squared * 100), arcadepix, color565(255, 193, 34))
                    validate_calibration(r_squared)
                    sleep_ms(3000)

                beep()
                m = 0  # ออกจากโหมด
                display.clear()
                soundOut()
                Homedisplays_initial()

        if button3_pin.value() == 1:  # ตรวจจับการกด button_3
            i = 0
            while button3_pin.value() == 1:
                i += 1
                sleep_ms(1000)
                if i == 3:  # กดค้าง 3 วินาทีเพื่อออกจากโหมด
                    beep()
                    light2_pwm.duty(0)  # หยุดการทำงานของปั๊ม
                    display.clear()  # ล้างหน้าจอ
                    display.draw_text(110, 110, "Exiting...", arcadepix, color565(255, 0, 0))
                    sleep_ms(750)  # แสดงข้อความ "Exiting..."
                    Homedisplays_initial()  # กลับไปหน้า Home Display
                    return
               
# --------------------------------- ฟังก์ชันการแสดงผลหน้าจอภายใน mode 2 (pH sensor Test) ---------------------------#

# ตัวแปรสำหรับ Mode 2
test_running = False  # สถานะการทำงาน
start_time_mode2 = 0  # เวลาที่เริ่มต้น
measured_ph = None  # ค่า pH ที่วัดได้
elapsed_time_mode2 = 0  # เวลาที่ผ่านไป
previous_measured_ph = None  # ค่า pH ก่อนหน้า
previous_timer = None  # ตัวจับเวลาที่แสดงบนหน้าจอ
previous_status = None  # สถานะก่อนหน้า

# ฟังก์ชันแสดงผลใน Mode 2
def phsensortestdisplays(update_ph=True, update_timer=True, update_status=True, update_start_button=True):
    global measured_ph, elapsed_time_mode2, previous_measured_ph, previous_timer, previous_status

    # ชื่อโหมด
    display.draw_text(75, 10, "pH Sensor Test", arcadepix, color565(255, 255, 255))
    display.draw_text(120, 60, "pH :", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 110, "Time Left :", arcadepix, color565(255, 255, 255))
    display.draw_text(50, 160, "Status :", arcadepix, color565(255, 255, 255))

    # Smooth update สำหรับ Timer (แสดงเวลาถอยหลังทันที)
    if update_timer:
        remaining_time = max(0, int(10 - elapsed_time_mode2))
        if previous_timer != remaining_time:  # อัปเดตเฉพาะเมื่อค่าต่างกัน
            display.fill_rectangle(180, 110, 100, 30, color565(0, 0, 0))  # ลบค่าเก่า
            display.draw_text(180, 110, f"{remaining_time} s", arcadepix, color565(204, 153, 255))
            previous_timer = remaining_time

    # Smooth update สำหรับค่า pH (ไม่อัปเดต N/A ซ้ำ)
    if update_ph:
        if measured_ph is None:  # หากยังไม่มีค่า pH
            if previous_measured_ph != "N/A":  # แสดง N/A ครั้งเดียว
                display.fill_rectangle(180, 60, 100, 30, color565(0, 0, 0))  # ลบค่าเก่า
                display.draw_text(180, 60, "N/A", arcadepix, color565(255, 0, 0))
                previous_measured_ph = "N/A"
        else:
            if previous_measured_ph != measured_ph:  # อัปเดตเฉพาะเมื่อค่าต่างกัน
                display.fill_rectangle(180, 60, 100, 30, color565(0, 0, 0))  # ลบค่าเก่า
                display.draw_text(180, 60, f"{measured_ph:.2f}", arcadepix, color565(255, 193, 34))
                previous_measured_ph = measured_ph

    # แสดงสถานะ
    if update_status:
        new_status = "Running" if test_running else "Stopped"
        if previous_status != new_status:  # อัปเดตเฉพาะเมื่อสถานะเปลี่ยน
            display.fill_rectangle(150, 160, 140, 30, color565(0, 0, 0))  # ลบสถานะเดิม
            status_color = color565(0, 255, 0) if new_status == "Running" else color565(255, 0, 0)
            display.draw_text(150, 160, f"{new_status}", arcadepix, status_color)
            previous_status = new_status

    # แสดงปุ่ม START
    if update_start_button:
        display.draw_text(120, 210, "START", arcadepix, color565(0, 255, 0))

# ฟังก์ชันเริ่มการวัดค่า pH
def start_ph_test():
    global test_running, start_time_mode2
    test_running = True
    start_time_mode2 = ticks_ms()  # บันทึกเวลาที่เริ่มต้น
    phsensortestdisplays(update_status=True, update_start_button=False)  # อัปเดตสถานะ

# ฟังก์ชันหยุดการวัดค่า pH
def stop_ph_test():
    global test_running
    test_running = False
    phsensortestdisplays(update_status=True, update_start_button=True)  # อัปเดตสถานะ

# ฟังก์ชันการทำงาน Mode 2
def menu2_loop():
    global test_running, start_time_mode2, elapsed_time_mode2, measured_ph, previous_measured_ph, previous_timer, previous_status

    # รีเซ็ตค่าที่เกี่ยวข้องเมื่อเริ่มต้น Mode 2 ใหม่
    test_running = False
    start_time_mode2 = 0
    elapsed_time_mode2 = 0
    measured_ph = None  # กำหนดค่าเริ่มต้นให้ไม่มีค่า pH
    previous_measured_ph = None
    previous_timer = None
    previous_status = None

    # แสดงผลเริ่มต้น พร้อมแสดง N/A
    phsensortestdisplays(update_ph=True, update_timer=True, update_status=True, update_start_button=True)

    while True:
        # หากกำลังวัดค่า pH
        if test_running:
            elapsed_time_mode2 = ticks_diff(ticks_ms(), start_time_mode2) / 1000.0  # เวลาที่ผ่านไปในวินาที
            if elapsed_time_mode2 >= 10:  # ครบ 10 วินาที
                voltage, measured_ph = GetpH(slope_m, intercept_b)  # คำนวณค่า pH
                stop_ph_test()  # หยุดการวัด
                phsensortestdisplays(update_ph=True)  # อัปเดตค่า pH
            else:
                phsensortestdisplays(update_timer=True)  # อัปเดตเวลาที่เหลือ

        # ตรวจจับการกดปุ่ม Start
        if button1_pin.value() == 1:
            while button1_pin.value() == 1:
                sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม
            if not test_running:
                start_ph_test()

        # ตรวจจับการกดปุ่มออก (Button 3)
        if button3_pin.value() == 1:  # กดค้างเพื่อออก
            i = 0
            while button3_pin.value() == 1:
                i += 1
                sleep_ms(1000)
                if i == 3:  # กดค้าง 3 วินาที
                    beep()
                    display.clear()  # ล้างหน้าจอ
                    display.draw_text(110, 110, "Exiting...", arcadepix, color565(255, 0, 0))
                    sleep_ms(750)  # แสดงข้อความ "Exiting..."
                    Homedisplays_initial()  # กลับไปหน้า Home Display
                    return  # ออกจากลูป Mode 2
    
# ---------------------------------- ฟังก์ชันการทำงาน และ การแสดงผลหน้าจอ ใน mode 3 (Calibrate Flow Rate) -----------------------------------# 

# ตัวแปรสำหรับจัดการสถานะ
current_sub_option = 1  # ตำแหน่งเริ่มต้น
pump_running = False  # สถานะปั๊ม
start_time = 0  # เวลาที่ปั๊มเริ่มทำงาน
elapsed_time = 0  # ระยะเวลาที่ปั๊มทำงาน
target_volume = 5.00  # ปริมาณเป้าหมายสำหรับการคำนวณ Flowrate

# ฟังก์ชันแสดงผลของ Calibrate Flow Rate (ลบส่วนที่แสดง data_flowrate)
def calflowratedisplays(update_time=True, update_flowrate=True, update_option=True, update_status=True):
    global elapsed_time, target_volume

    # แสดงข้อความหัวข้อและข้อมูลที่ไม่เปลี่ยนแปลง
    display.draw_text(60, 10, 'Calibrate Flow Rate', arcadepix, color565(255, 255, 255))
    display.draw_text(45, 55, 'Target Volume 5.00 ml', arcadepix, color565(204, 153, 255))

    if update_time:
        # ลบพื้นที่เฉพาะสำหรับตัวเลขเวลา
        display.fill_rectangle(160, 90, 50, 30, color565(0, 0, 0))
        display.draw_text(88, 90, 'Time :', arcadepix, color565(255, 255, 255))
        display.draw_text(230, 90, 'sec', arcadepix, color565(255, 255, 255))
        display.draw_text(160, 90, '{:.2f}'.format(elapsed_time), arcadepix, color565(255, 193, 34))

    if update_flowrate:
        # ลบพื้นที่เฉพาะสำหรับ flow rate
        display.fill_rectangle(160, 120, 70, 30, color565(0, 0, 0))
        display.draw_text(30, 120, 'Flow Rate :', arcadepix, color565(255, 255, 255))
        display.draw_text(230, 120, 'ml/sec', arcadepix, color565(255, 255, 255))
        flow_rate = target_volume / elapsed_time if elapsed_time > 0 else 0
        display.draw_text(160, 120, '{:.3f}'.format(flow_rate), arcadepix, color565(255, 193, 34))

    if update_option:
        # แสดงตัวเลือก Start และ Reset 
        #display.fill_rectangle(60, 170, 105, 35, color565(0, 0, 0))  # ลบพื้นที่ตัวเลือกเดิม
        display.draw_text(55, 150, 'Start/Stop', arcadepix, color565(0, 255, 0) if current_sub_option == 1 else color565(255, 255, 255))
        display.draw_text(205, 150, 'Reset', arcadepix, color565(0, 255, 0) if current_sub_option == 2 else color565(255, 255, 255))

    if update_status:
        # ลบพื้นที่ข้อความ Status Pump ทั้งหมด
        display.fill_rectangle(200, 180, 120, 30, color565(0, 0, 0))  # ลบพื้นที่ข้อความเดิม
        display.draw_text(30, 180, 'Status:', arcadepix, color565(255, 255, 255))  # แสดงข้อความ Status ใหม่
        # แสดงสถานะปั๊ม Running หรือ Stopped
        status_text = 'Pump  Running' if pump_running else 'Pump Stopped'
        display.draw_text(130, 180, status_text, arcadepix, color565(0, 255, 0) if pump_running else color565(255, 0, 0))

    if last_saved_flowrate_time:
        display.draw_text(30, 216, f"Last Calibrate: {last_saved_flowrate_time}", arcadepix, color565(102, 255, 255))
    else:
        display.draw_text(70, 216, "Last Calibrate: N/A", arcadepix, color565(255, 0, 0))

# ฟังก์ชันบันทึกค่า Flow Rate
def save_flowrate(flow_rate):
    try:
        with open("data_flowrate.txt", "w") as file:
            file.write(f"{flow_rate}\n")
            # บันทึกวันที่ล่าสุด
            current_time = utime.localtime()
            formatted_date = "{:04d}-{:02d}-{:02d}".format(
                current_time[0], current_time[1], current_time[2]
            )
            file.write(f"Last saved: {formatted_date}\n")
        print("Flow rate data saved successfully.")
    except Exception as e:
        print(f"Error saving flow rate data: {e}")

# ฟังก์ชันเริ่มการทำงานของปั๊ม
def start_pump():
    global pump_running, start_time
    pump_running = True
    start_time = ticks_ms()
    light2_pwm.duty(1023)  # เริ่มด้วย Duty Cycle สูงสุด 100%
    calflowratedisplays(update_status=True)  # อัปเดตสถานะ

# ฟังก์ชันหยุดการทำงานของปั๊มและบันทึก Flow Rate
def stop_pump():
    global pump_running, elapsed_time, data_flowrate
    pump_running = False
    elapsed_time = (ticks_diff(ticks_ms(), start_time)) / 1000  # คำนวณเวลาที่ปั๊มทำงาน
    light2_pwm.duty(0)  # หยุดปั๊ม
    calflowratedisplays(update_status=True, update_flowrate=True, update_time=True)  # อัปเดตสถานะและค่า

    # บันทึกค่า Flow Rate
    data_flowrate = target_volume / elapsed_time if elapsed_time > 0 else 0
    save_flowrate(data_flowrate)

    # แสดงข้อความใน Shell
    print(f"Flow Rate: {data_flowrate:.3f} ml/sec recorded in data_flowrate.txt")
    
# ฟังก์ชัน Reset ค่า
def reset_flow_rate():
    global elapsed_time, data_flowrate
    elapsed_time = 0
    data_flowrate = None  # ลบค่าที่บันทึกไว้ในตัวแปร

    # ลบข้อมูลในไฟล์ data_flowrate.txt
    try:
        with open("data_flowrate.txt", "w") as file:
            file.write("")  # เขียนไฟล์ว่างเพื่อลบข้อมูลเก่า
        print("Flow rate data in file has been reset.")
    except Exception as e:
        print(f"Error resetting flow rate file: {e}")

# ฟังก์ชันวนลูปสำหรับใช้ใน Menu 3
def menu3_loop():
    global current_sub_option, pump_running, elapsed_time
    calflowratedisplays(update_time=True, update_flowrate=True, update_option=True)  # แสดงเมนูเริ่มต้น

    while True:
        if button2_pin.value() == 1:  # เปลี่ยนตำแหน่ง >
            while button2_pin.value() == 1:
                sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม
            current_sub_option = (current_sub_option % 2) + 1  # เลื่อนระหว่าง Start และ Reset
            beep()
            calflowratedisplays(update_option=True, update_time=False, update_flowrate=False, update_status=False)  # อัปเดตเฉพาะตำแหน่งลูกศร

        if button1_pin.value() == 1:  # เลือกตัวเลือกในตำแหน่ง >
            while button1_pin.value() == 1:
                sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม

            if current_sub_option == 1:  # กด Start
                if not pump_running:
                    start_pump()
                else:
                    stop_pump()  # หากปั๊มทำงานอยู่ ให้หยุด
                calflowratedisplays(update_time=True, update_flowrate=True, update_option=False, update_status=True)  # อัปเดตเวลาและ Flow Rate
            elif current_sub_option == 2:  # กด Reset
                reset_flow_rate()  # รีเซ็ตค่า
                calflowratedisplays(update_time=True, update_flowrate=True, update_option=False, update_status=True)  # อัปเดตเวลาและ Flow Rate

        if button3_pin.value() == 1:  # กลับหน้าหลัก
            i = 0
            while button3_pin.value() == 1:
                i += 1
                sleep_ms(1000)
                if i == 3:  # กดค้าง 3 วินาที
                    beep()
                    display.clear()

                    # รีเซ็ตค่า current_sub_option และ selected_option
                    current_sub_option = 1
                    pump_running = False
                    elapsed_time = 0

                    display.draw_text(110, 110, "Exiting...", arcadepix, color565(255, 0, 0))
                    sleep_ms(750)  # แสดงข้อความ "Exiting..."
                    Homedisplays_initial()  # กลับไปหน้า Home Display
                    return  # ออกจาก loop ของ Menu 3

# --------------------------------- ฟังก์ชันการแสดงผลหน้าจอภายใน mode 4 (Flow Rate Test) ---------------------------#
# ตัวแปรสำหรับ Mode 4
current_sub_option_mode4 = 1  
target_volumes = [3.00, 5.00, 8.00, 10.00]  # ตัวเลือกปริมาตรเป้าหมาย
selected_target_volume = target_volumes[0]  # ปริมาตรเป้าหมายที่เลือกเริ่มต้น
pump_running_mode4 = False  # สถานะปั๊ม
elapsed_time_mode4 = 0  # เวลาที่ปั๊มทำงาน
flow_rate_mode4 = 0.00  # ค่า Flow Rate ที่คำนวณได้

# ฟังก์ชันแสดงผลของ Mode 4
def flowratetestdisplays(update_time=False, update_status=True, update_option=True, update_flowrate=True):
    global flow_rate_mode4

    # แสดงข้อความหัวข้อ
    display.draw_text(75, 10, 'Flow Rate Test', arcadepix, color565(255, 255, 255))
    display.draw_text(16, 40, 'Flow Rate:', arcadepix, color565(255, 255, 255))
    display.draw_text(240, 40, 'ml/sec', arcadepix, color565(255, 255, 255))
    display.draw_text(16, 65, 'Choose your target volume', arcadepix, color565(204, 153, 255))

    if update_flowrate:
    # แสดง Flow Rate ที่ดึงมาจาก Mode 3 (คงค่าไว้จนกว่าจะเปลี่ยน)
        if data_flowrate:
            display.fill_rectangle(160, 40, 70, 20, color565(0, 0, 0))  # ลบพื้นที่ Flow Rate เดิม
            display.draw_text(150, 40, f"{data_flowrate:.3f}", arcadepix, color565(255, 193, 34))
        else:
            display.fill_rectangle(160, 40, 70, 20, color565(0, 0, 0))  # ลบพื้นที่ Flow Rate เดิม
            display.draw_text(150, 40, "N/A", arcadepix, color565(255, 0, 0))

        # แสดงตัวเลือกปริมาตรเป้าหมาย
    for i, volume in enumerate(target_volumes):
        y_position = 95 + (i * 30)
        color = color565(0, 255, 0) if current_sub_option_mode4 == (i + 1) else color565(255, 255, 255)
        display.draw_text(40, y_position, f"{volume:.2f} ml", arcadepix, color)

    # แสดงสถานะปั๊ม
    if update_status:
        display.fill_rectangle(180, 150, 140, 40, color565(0, 0, 0))  # ลบข้อความเก่าที่เกี่ยวข้อง
        display.draw_text(160, 120, "Status Pump:", arcadepix, color565(255, 255, 255))
        status_text = " Running" if pump_running_mode4 else "Stopped"
        status_color = color565(0, 255, 0) if pump_running_mode4 else color565(255, 0, 0)
        display.draw_text(180, 150, status_text, arcadepix, status_color)
        
# ฟังก์ชันเริ่มการทำงานของปั๊มใน Mode 4
def start_pump_mode4():
    global pump_running_mode4, start_time_mode4, selected_target_volume, data_flowrate, elapsed_time_mode4

    if not data_flowrate:  # หากไม่มีค่า Flow Rate ที่บันทึกจาก Mode 3
        beepbeep()  # ส่งเสียงเตือน
        print("Cannot start pump. No stored flow rate available.")
        return

    pump_running_mode4 = True
    start_time_mode4 = ticks_ms()

    # คำนวณเวลาที่ปั๊มต้องทำงานโดยใช้ Flow Rate
    elapsed_time_mode4 = selected_target_volume / data_flowrate if data_flowrate > 0 else 0
    print(f"Pump will run for {elapsed_time_mode4:.2f} seconds for {selected_target_volume} mL target.")

    light2_pwm.duty(1023)  # เปิดปั๊มด้วย Duty Cycle สูงสุด
    flowratetestdisplays(update_status=True)  # อัปเดตสถานะ

# ฟังก์ชันหยุดการทำงานของปั๊มใน Mode 4
def stop_pump_mode4():
    global pump_running_mode4

    pump_running_mode4 = False
    light2_pwm.duty(0)  # ปิดปั๊มทันที
    print(f"Pump stopped after completing {selected_target_volume} mL target.")
    flowratetestdisplays(update_status=True)  # อัปเดตสถานะ
            
def monitor_pump_mode4():
    global pump_running_mode4, start_time_mode4, elapsed_time_mode4

    if pump_running_mode4:
        elapsed_time = ticks_diff(ticks_ms(), start_time_mode4) / 1000.0  # คำนวณเวลาที่ผ่านไป
        draw_smooth_battery_indicator(elapsed_time, elapsed_time_mode4)  # วาดแบตเตอรี่แบบลื่นไหล
        if elapsed_time >= elapsed_time_mode4:
            stop_pump_mode4()  # หยุดปั๊มเมื่อเวลาที่กำหนดสิ้นสุด

# เพิ่มตัวแปร global สำหรับการจัดการสถานะการแสดงผลของแบตเตอรี่
battery_status = []  # เก็บสถานะแต่ละช่องของแบตเตอรี่
def draw_smooth_battery_indicator(current_time, total_time, bar_height=15):
    """
    วาดแบตเตอรี่แบบลื่นไหลตามเวลาที่ปั๊มทำงาน
    current_time: เวลาในหน่วยวินาทีที่ผ่านไป
    total_time: เวลารวมที่ปั๊มจะทำงาน
    """
    global battery_status  # ใช้ตัวแปร global เพื่อเก็บสถานะแบตเตอรี่
    # กำหนดตำแหน่งและขนาดของแบตเตอรี่
    y_start = 213  # ตำแหน่ง Y ของแบตเตอรี่
    spacing = 1  # ระยะห่างระหว่างแท่ง
    total_bars = 100  # จำนวนแท่งแบตเตอรี่ทั้งหมด

    # คำนวณขนาดของแท่งให้พอดีกับจำนวน Cycle
    available_width = 319  # ความกว้างทั้งหมดของหน้าจอ
    bar_width = (available_width - (spacing * (total_bars - 1))) // total_bars

    # คำนวณ progress และสีของแบตเตอรี่
    progress_fraction = current_time / total_time if total_time > 0 else 0
    bars_to_fill = int(progress_fraction * total_bars)

    # ถ้า battery_status ยังไม่ถูกสร้างหรือมีขนาดไม่ตรงกัน ให้รีเซ็ต
    if len(battery_status) != total_bars:
        battery_status = [False] * total_bars

    # วาดแบตเตอรี่แต่ละช่อง
    for i in range(total_bars):
        x_position = i * (bar_width + spacing)

        if i < bars_to_fill and not battery_status[i]:  # ถ้าช่องนี้ยังไม่ถูกเติมสี
            # คำนวณสีตาม progress
            red = int(255 * (1 - (i / total_bars)))  # แดงลดลง
            green = int(255 * (i / total_bars))      # เขียวเพิ่มขึ้น
            color = color565(red, green, 0)

            # เติมสีเฉพาะช่องที่ยังไม่ได้อัปเดต
            display.fill_rectangle(x_position, y_start, bar_width, bar_height, color)
            battery_status[i] = True  # อัปเดตสถานะว่าช่องนี้ถูกเติมแล้ว

        elif i >= bars_to_fill and battery_status[i]:  # ถ้าช่องนี้ควรจะว่าง
            # ลบสีเฉพาะช่องที่เคยถูกเติมและไม่ควรเติมแล้ว
            display.fill_rectangle(x_position, y_start, bar_width, bar_height, color565(0, 0, 0))
            battery_status[i] = False  # อัปเดตสถานะว่าช่องนี้ว่าง

# ฟังก์ชันการทำงานของ Mode 4
def menu4_loop():
    global current_sub_option_mode4, selected_target_volume, pump_running_mode4, elapsed_time_mode4, flow_rate_mode4
    flowratetestdisplays(update_time=False)  # แสดงผลเริ่มต้นของ Mode 4 (ไม่แสดง Time)

    while True:
        monitor_pump_mode4()  # ตรวจสอบการทำงานของปั๊มในลูป

        if button2_pin.value() == 1:  # เลื่อนตำแหน่ง >
            while button2_pin.value() == 1:
                sleep_ms(1)
            previous_option = current_sub_option_mode4
            current_sub_option_mode4 = (current_sub_option_mode4 % len(target_volumes)) + 1
            selected_target_volume = target_volumes[current_sub_option_mode4 - 1]

            # อัปเดตเฉพาะปริมาตรที่เลือก
            y_previous = 95 + ((previous_option - 1) * 30)
            y_current = 95 + ((current_sub_option_mode4 - 1) * 30)
            display.fill_rectangle(40, y_previous, 120, 30, color565(0, 0, 0))
            display.draw_text(40, y_previous, f"{target_volumes[previous_option - 1]:.2f} ml", arcadepix, color565(255, 255, 255))
            display.draw_text(40, y_current, f"{target_volumes[current_sub_option_mode4 - 1]:.2f} ml", arcadepix, color565(0, 255, 0))

        if button1_pin.value() == 1:  # เริ่มหรือหยุดการทำงานของปั๊ม
            while button1_pin.value() == 1:
                sleep_ms(1)

            if not data_flowrate:  # หากไม่มีค่า Flow Rate ที่บันทึกจาก Mode 3
                beepbeep()  # ส่งเสียงเตือน
                print("No valid flow rate. Pump will not run.")
                continue

            if not pump_running_mode4:
                start_pump_mode4()
            else:
                stop_pump_mode4()
            
        if button3_pin.value() == 1:  # กลับหน้าหลัก
            i = 0
            while button3_pin.value() == 1:
                i += 1
                sleep_ms(1000)
                if i == 3:  # กดค้าง 3 วินาทีเพื่อกลับหน้าหลัก
                    beep()  # เล่นเสียง
                    display.clear()  # ล้างหน้าจอ
                    display.draw_text(110, 110, "Exiting...", arcadepix, color565(255, 0, 0))
                    sleep_ms(750)  # แสดงข้อความ "Exiting..."
                    Homedisplays_initial()  # กลับไปหน้า Home Display
                    return  # ออกจากลูปของ Mode 4

#-------------------------------- ฟังก์ชันแสดงผลหน้าจอ mode 5 Purge กำหนด duty,Volume ----------------------------# 

# เพิ่มการอ่านค่า potentiometer และอัปเดต Duty Cycle แบบเรียลไทม์ใน Mode 5
potentiometer1 = ADC(Pin(POT1_PIN))  # ตั้งค่า ADC บน Pin GPIO33
potentiometer1.atten(ADC.ATTN_11DB)  # ตั้งค่าให้ ADC สามารถอ่านค่าได้เต็มช่วง
current_duty = 0
current_percentage = 0
pump_running_mode5 = False
previous_duty = -1  # ค่า Duty Cycle ก่อนหน้า (เริ่มต้นให้ไม่เหมือนค่าใดๆ)
previous_status = None  # สถานะก่อนหน้า
previous_option = None  # ตัวเลือกก่อนหน้า

# ฟังก์ชันแสดงผลใน Mode 5
def purgedisplay(update_duty=True, update_status=True, update_option=True):
    global current_duty, current_percentage, pump_running_mode5, previous_duty, previous_status, previous_option
     
    # แสดงชื่อโหมด
    display.draw_text(135, 10, 'Purge', arcadepix, color565(255, 255, 255))
    display.draw_text(20, 45, 'Status Pump :', arcadepix, color565(255, 255, 255))
    display.draw_text(20, 75, 'Duty Cycle  :', arcadepix, color565(255, 255, 255))
    display.draw_text(20, 105, 'Pump Power  :', arcadepix, color565(255, 255, 255))

    # แสดงตัวเลือก Start และ Stop
    if update_option and current_sub_option != previous_option:
        display.draw_text(70, 160, 'Start', arcadepix, color565(0, 255, 0) if current_sub_option == 1 else color565(255, 255, 255))
        display.draw_text(190, 160, 'Stop', arcadepix, color565(0, 255, 0) if current_sub_option == 2 else color565(255, 255, 255))
        previous_option = current_sub_option  # อัปเดตตัวเลือก

    # แสดงสถานะปั๊ม
    if update_status:
        display.fill_rectangle(180, 45, 100, 30, color565(0, 0, 0))  # ลบสถานะเก่า
        status_text = 'Running' if pump_running_mode5 else 'Stopped'
        status_color = color565(0, 255, 0) if pump_running_mode5 else color565(255, 0, 0)
        display.draw_text(190, 45, status_text, arcadepix, status_color)

    # แสดง Duty Cycle และ Pump Power
    if update_duty:
        display.fill_rectangle(220, 75, 70, 30, color565(0, 0, 0))  # ลบ Duty Cycle เก่า
        display.fill_rectangle(225, 105, 50, 30, color565(0, 0, 0))  # ลบ Power เก่า
        display.draw_text(210, 75, f'{current_duty}', arcadepix, color565(255, 193, 34))
        display.draw_text(210, 105, f'{current_percentage}%', arcadepix, color565(255, 193, 34))

# ฟังก์ชันอัปเดต Duty Cycle และ Pump Power %
def update_pump_duty():
    global current_duty, current_percentage

    pot_value = potentiometer1.read()  # อ่านค่า ADC จาก Pot_1
    new_duty = int((pot_value / 4095) * 1023)  # แปลงค่าเป็น Duty Cycle (0-1023)
    new_percentage = int((pot_value / 4095) * 100)  # แปลงค่าเป็นเปอร์เซ็นต์ (0-100)

    # ตรวจสอบว่าค่า Duty Cycle เปลี่ยนแปลงหรือไม่
    if new_duty != current_duty or new_percentage != current_percentage:
        current_duty = new_duty
        current_percentage = new_percentage
        purgedisplay(update_duty=True)  # อัปเดตข้อมูลบนหน้าจอ (ไม่เริ่มปั๊ม)

# ฟังก์ชันเริ่มการทำงานของปั๊ม
def start_pump_mode5():
    global pump_running_mode5
    pump_running_mode5 = True
    light2_pwm.duty(current_duty)  # ใช้ค่า Duty Cycle ที่คำนวณจาก Pot_1
    purgedisplay(update_status=True)  # อัปเดตสถานะ

# ฟังก์ชันหยุดการทำงานของปั๊ม
def stop_pump_mode5():
    global pump_running_mode5
    pump_running_mode5 = False
    light2_pwm.duty(0)  # หยุดปั๊ม
    purgedisplay(update_status=True)  # อัปเดตสถานะ
    
# ฟังก์ชันการวนลูปสำหรับ Mode 5
def menu5_loop():
    global current_duty, current_percentage, pump_running_mode5, current_sub_option, previous_option
    
    # รีเซ็ตสถานะตัวเลือกและสถานะปั๊ม
    current_sub_option = 1  # ตัวเลือกเริ่มต้นคือ Start
    pump_running_mode5 = False  # ตั้งสถานะปั๊มเริ่มต้นเป็นหยุดทำงาน
    previous_option = None  # รีเซ็ตตัวเลือกก่อนหน้า
    
    display.clear()  # ล้างหน้าจอเมื่อเข้าสู่ Mode 5
    purgedisplay(update_option=True)  # แสดงผลเริ่มต้น

    while True:
        update_pump_duty()  # อัปเดตค่า Duty Cycle และ Power %

        if pump_running_mode5:
            # หากปั๊มกำลังทำงาน ให้อัปเดต PWM ของปั๊มแบบเรียลไทม์
            light2_pwm.duty(current_duty)

        if button2_pin.value() == 1:  # เปลี่ยนตำแหน่ง 
            while button2_pin.value() == 1:
                sleep_ms(1)
            current_sub_option = (current_sub_option % 2) + 1  # สลับระหว่าง Start และ Stop
            purgedisplay(update_option=True)  # อัปเดตตำแหน่งตัวเลือก

        if button1_pin.value() == 1:  # เริ่มหรือหยุดปั๊ม
            while button1_pin.value() == 1:
                sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม

            if current_sub_option == 1:  # หากเลือก Start
                start_pump_mode5()
            elif current_sub_option == 2:  # หากเลือก Stop
                stop_pump_mode5()

        # ตรวจจับการกด Button_3 ค้าง
        if button3_pin.value() == 1:  # กลับหน้าหลักด้วย Button 3 (กดค้าง 3 วินาที)
            i = 0
            while button3_pin.value() == 1:
                i += 1
                sleep_ms(500)
                if i == 3:
                    # ตรวจสอบว่าปั๊มหยุดทำงานหรือไม่
                    if pump_running_mode5:
                        beepbeep()  # แจ้งเตือนด้วยเสียง
                        # แสดงข้อความเตือนบนจอ
                        display.fill_rectangle(50, 200, 220, 30, color565(0, 0, 0))  # ลบข้อความเก่า
                        display.draw_text(50, 200, "Pump is still running!", arcadepix, color565(255, 0, 0))
                        print("Cannot exit. Pump is still running!")
                        sleep_ms(2000)  # แสดงข้อความเตือน 2 วินาที
                        # ลบข้อความเตือนหลังจากแสดง
                        display.fill_rectangle(50, 200, 220, 30, color565(0, 0, 0))
                    else:
                        beep()
                        display.clear()  # ล้างหน้าจอ
                        display.draw_text(110, 110, "Exiting...", arcadepix, color565(255, 0, 0))
                        sleep_ms(1000)  # แสดงข้อความ "Exiting..."
                        Homedisplays_initial()  # กลับไปหน้า Home Display
                        return  # ออกจากลูปของ Menu 5

#-------------------------------- ฟังก์ชันแสดงผลหน้าจอใน mode 6 Full Auto titration--------------------------------- #

# ตัวแปร global สำหรับ Full Auto Displays
previous_flowrate = None
previous_elapsed_time = None
previous_pH = None
previous_pause_time = None
previous_cycle = None
previous_running_status = None

async def fullautodisplays(pH, flowrate, current_cycle, total_cycles, pause_time=None, is_running=False):
    global previous_flowrate, previous_pH, previous_cycle, previous_pause_time, previous_running_status

    # ส่วนหัว (Header)
    if previous_running_status is None:  # แสดงครั้งแรกเท่านั้น
        display.draw_rectangle(5, 40, 310, 160, color565(255, 255, 255))  # เส้นกรอบสีขาว
        display.fill_rectangle(0, 0, 319, 30, color565(0, 102, 204))
        display.draw_text(40, 3, "Full Auto Titration Mode", arcadepix, color565(255, 255, 255))

    # Static Text
    display.draw_text(30, 50, "Cycle:", arcadepix, color565(255, 255, 255))
    display.draw_text(30, 80, "Duty cycle:", arcadepix, color565(255, 255, 255))
    display.draw_text(30, 110, "Flowrate:", arcadepix, color565(255, 255, 255))
    display.draw_text(30, 140, "pH Value:", arcadepix, color565(255, 255, 255))
    display.draw_text(30, 170, "Pause Time:", arcadepix, color565(255, 255, 255))

    # Dynamic Text
    if current_cycle != previous_cycle:
        display.fill_rectangle(150, 50, 140, 20, color565(0, 0, 0))
        display.draw_text(180, 50, f"{current_cycle}/{total_cycles}", arcadepix, color565(255, 255, 0))
        previous_cycle = current_cycle

    display.draw_text(180, 80, "100% ", arcadepix, color565(102, 255, 255))

    if flowrate != previous_flowrate:
        display.fill_rectangle(180, 110, 130, 20, color565(0, 0, 0))
        flowrate_text = f"{flowrate:.3f} mL/s" if flowrate else "N/A"
        display.draw_text(180, 110, flowrate_text, arcadepix, color565(255, 193, 34))
        previous_flowrate = flowrate

    # **ตรวจสอบค่า pH และแสดงผล**
    if pH != previous_pH:
        display.fill_rectangle(180, 140, 130, 20, color565(0, 0, 0))
        pH_text = "N/A" if pH is None else f"{pH:.2f}"  # เพิ่มเงื่อนไข pH เป็น None
        display.draw_text(180, 140, pH_text, arcadepix, color565(255, 0, 0))
        previous_pH = pH

    if pause_time is not None and pause_time != previous_pause_time:
        display.fill_rectangle(180, 170, 130, 20, color565(0, 0, 0))
        pause_time_text = f"{int(pause_time)} s"
        display.draw_text(180, 170, pause_time_text, arcadepix, color565(204, 153, 255))
        previous_pause_time = pause_time
        
    # Footer     
    if is_running != previous_running_status:
    
        if is_running:
            display.fill_rectangle(30, 208, 270, 30, color565(0, 0, 0))
        else:
            display.fill_rectangle(30, 208, 270, 30, color565(0, 0, 0))
            display.draw_text(30, 208, "Press Button_1 for start", arcadepix, color565(0, 255, 0))
        previous_running_status = is_running

# ฟังก์ชันวัดค่า pH แบบ async
async def measure_pH():
    try:
        voltage, pH_value = GetpH(slope_m, intercept_b)  # วัดค่า pH
        return voltage, pH_value
    except Exception as e:
        print(f"Error in measure_pH: {e}")
        return None, None

def save_data_to_csv(file_base_name, data):
    index = 1
    while True:
        file_name = f"{file_base_name}_R{index}.csv"

        # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
        existing_files = os.listdir()  # ดึงรายชื่อไฟล์ทั้งหมดในโฟลเดอร์ปัจจุบัน
        if file_name not in existing_files:  # ถ้าไฟล์ไม่มีอยู่
            try:
                with open(file_name, "w") as file:  # ใช้ "w" เพื่อสร้างไฟล์ใหม่
                    file.write("Volume (mL),pH Value\n")  # เขียน header ของไฟล์
                    
                    # บันทึกข้อมูลทีละบรรทัด
                    for row in data:
                        file.write(",".join([f"{item:.3f}" for item in row]) + "\n")
                    
                print(f"Data saved to {file_name}")
                return file_name  # คืนชื่อไฟล์ที่บันทึกสำเร็จ
            except Exception as e:
                print(f"Error saving data to {file_name}: {e}")
                return None  # คืนค่า None หากเกิดข้อผิดพลาด
        else:
            index += 1  # เพิ่มดัชนีหากไฟล์มีอยู่แล้ว

async def check_button3_mode6():
    if button3_pin.value() == 1:  # ตรวจจับการกดปุ่ม Button_3
        button_hold_time = ticks_ms()  # บันทึกเวลาที่เริ่มกดปุ่ม
        while button3_pin.value() == 1:  # ตรวจสอบว่าปุ่มยังถูกกดอยู่
            if ticks_diff(ticks_ms(), button_hold_time) > 3000:  # กดค้างไว้นานกว่า 3 วินาที
                print("Button 3 hold for 3 seconds. Exiting without saving.")
                light2_pwm.duty(0)  # หยุดปั๊มทันที
                display.clear()  # ล้างหน้าจอ
                display.draw_text(110, 110, "Exiting...", arcadepix, color565(255, 0, 0))
                sleep_ms(750)  # แสดงข้อความ "Exiting..."
                Homedisplays_initial()  # กลับไปหน้า Home Display
                return True  # ระบุว่าออกจากโหมด
    return False  # ไม่ได้กดค้าง

async def draw_battery_indicator(current_cycle, total_cycles):
    """แสดง Cycle Indicator แบบไล่สีจากแดงไปเขียว"""
    # กำหนดขนาดและตำแหน่ง
    y_start = 213  # ตำแหน่ง Y
    spacing = 2  # ระยะห่างระหว่างแท่ง

    # คำนวณขนาดของแท่งให้พอดีกับจำนวน Cycle
    available_width = 319  # ความกว้างทั้งหมดของหน้าจอ
    bar_width = (available_width - (spacing * (total_cycles - 1))) // total_cycles
    bar_height = 15  # ความสูงของแท่ง

    # คำนวณจุดเริ่มต้น X เพื่อให้แบตเตอรี่อยู่ตรงกลาง
    total_battery_width = (bar_width * total_cycles) + (spacing * (total_cycles - 1))
    x_start = (available_width - total_battery_width) // 2

    # วาดแท่งแต่ละช่อง
    for i in range(total_cycles):
        x_position = x_start + i * (bar_width + spacing)

        if i < current_cycle:  # แท่งที่เต็มแล้ว
            # คำนวณสีตาม Cycle
            red = int(255 * (1 - (i / total_cycles)))  # แดงลดลง
            green = int(255 * (i / total_cycles))      # เขียวเพิ่มขึ้น
            color = color565(red, green, 0)
            display.fill_rectangle(x_position, y_start, bar_width, bar_height, color)  # สีไล่ระดับ
        else:  # แท่งที่ยังว่าง
            display.draw_rectangle(x_position, y_start, bar_width, bar_height, color565(0,0,0)) 
    
async def control_pump(duration):
    start_time = ticks_us()
    light2_pwm.duty(1023)  # เปิดปั๊ม
    while ticks_diff(ticks_us(), start_time) < int(duration * 1_000_000):  
        if ticks_diff(ticks_us(), start_time) >= int(duration * 1_000_000 * 0.98):  # ปิดปั๊มล่วงหน้า 2%
            light2_pwm.duty(500)  # ลด PWM เพื่อเบรกปั๊ม
        await asyncio.sleep(0.0001)  # ปรับ sleep เป็น microsecond เพื่อความแม่นยำ
    light2_pwm.duty(0)  # ปิดปั๊ม

async def alert_before_cycle_25(current_cycle, total_cycles):
    if current_cycle == 24 and total_cycles >= 25:  # ตรวจสอบว่ากำลังเข้าสู่รอบที่ 25
        print("Alert: Cycle 25 is coming up!")
        for _ in range(3):  # เล่นเสียงเตือน 3 ครั้ง
            beeep()
            await asyncio.sleep(0.75)  #เสียงเตือน

# ฟังก์ชันสำหรับ Mode 6 Full Auto Titration
async def menu6_loop():
    global previous_flowrate, previous_pH, previous_cycle, previous_pause_time, previous_running_status
    previous_flowrate = None
    previous_pH = None
    previous_cycle = None
    previous_pause_time = None
    previous_running_status = None

    target_volume = 10.0  # ปริมาตรเป้าหมาย
    target_volume_per_cycle = 0.200  # ปริมาตรเป้าหมายต่อรอบ (mL)
    pause_time_between_cycles = 10 # เวลาหยุดพักระหว่างรอบ (ตั้งค่าได้ที่นี่)
    pH_value = None  # ค่าเริ่มต้นของ pH เป็น None
    accumulated_volume = 0.0
    measurement_data = []  # เก็บข้อมูล Volume และ pH

    # ตรวจสอบว่า Flow Rate มีค่าหรือไม่
    if data_flowrate is None or data_flowrate <= 0:
        display.draw_text(30, 100, "Error: No flowrate data", arcadepix, color565(255, 0, 0))
        await asyncio.sleep(2)  # รอ 2 วินาที
        display.clear()
        Homedisplays_initial()
        return

    # คำนวณจำนวน Cycle
    total_cycles = math.ceil(target_volume / target_volume_per_cycle)

    # แสดงค่าเริ่มต้น
    await fullautodisplays(
        pH=pH_value,
        flowrate=data_flowrate,
        current_cycle=0,
        total_cycles=total_cycles,
        pause_time=pause_time_between_cycles,
        is_running=False
    )
    gc.collect()  # คืนหน่วยความจำ

    # รอการเริ่มต้น
    while button1_pin.value() == 0:
        if await check_button3_mode6():  # ตรวจจับการกดปุ่ม 3 ค้าง
            return
        await asyncio.sleep(0.01)

    # เมื่อกดปุ่ม Button_1 ให้ลบข้อความ "Press Button_1 for start" และเริ่มนับเวลา
    display.fill_rectangle(30, 208, 270, 30, color565(0, 0, 0))  # ลบข้อความ

    for remaining in range(pause_time_between_cycles, 0, -1):
        await fullautodisplays(
            pH=pH_value,
            flowrate=data_flowrate,
            current_cycle=0,
            total_cycles=total_cycles,
            pause_time=remaining,
            is_running=False
        )
        await asyncio.sleep(1)

    current_cycle = 1
    while current_cycle <= total_cycles:
        if await check_button3_mode6():  # ตรวจจับการกดปุ่ม 3 ค้างระหว่างการทำงาน
            return

        # ตรวจสอบและเล่นเสียงเตือนหากถึงรอบที่ 24
        await alert_before_cycle_25(current_cycle, total_cycles)

        # วัดค่า pH ก่อนปั๊มเริ่มทำงาน
        if current_cycle == 1:  # วัดเฉพาะรอบแรกก่อนปั๊มทำงาน
            voltage, pH_value = await measure_pH()
            measurement_data.append([accumulated_volume, pH_value])

        # แสดงข้อมูลปัจจุบัน
        await fullautodisplays(
            pH=pH_value,
            flowrate=data_flowrate,
            current_cycle=current_cycle,
            total_cycles=total_cycles,
            pause_time=None,
            is_running=True
        )
        await draw_battery_indicator(current_cycle, total_cycles)

        gc.collect()  # คืนหน่วยความจำ

        # เริ่มปั๊มทำงาน
        work_time = target_volume_per_cycle / data_flowrate  # คำนวณเวลาที่ปั๊มทำงาน (s)
        await control_pump(work_time)  # เรียกปั๊มให้ทำงาน
        accumulated_volume += target_volume_per_cycle  # อัปเดตปริมาตรที่สะสม

        # รอระหว่างรอบ
        for remaining in range(pause_time_between_cycles, 0, -1):
            await fullautodisplays(
                pH=pH_value,
                flowrate=data_flowrate,
                current_cycle=current_cycle,
                total_cycles=total_cycles,
                pause_time=remaining,
                is_running=True
            )
            await asyncio.sleep(1)

        # วัดค่า pH หลังปั๊มทำงาน
        voltage, pH_value = await measure_pH()
        measurement_data.append([accumulated_volume, pH_value])

        # แสดงข้อมูลปัจจุบัน
        await fullautodisplays(
            pH=pH_value,
            flowrate=data_flowrate,
            current_cycle=current_cycle,
            total_cycles=total_cycles,
            pause_time=None,
            is_running=True
        )

        gc.collect()  # คืนหน่วยความจำ

        # เพิ่มรอบปัจจุบันหลังจากจบรอบนี้
        current_cycle += 1

    # แสดงผลการทำงานเสร็จสิ้น
    saved_file_name = save_data_to_csv("titration_data", measurement_data)
    light2_pwm.duty(0)
    display.clear()
    display.draw_text(55, 50, "Titration Complete", arcadepix, color565(0, 255, 0))
    display.draw_text(40, 80, f"Total Volume: {target_volume:.2f} mL", arcadepix, color565(255, 193, 34))
    if saved_file_name:
        display.draw_text(95, 120, "Saved to:", arcadepix, color565(102, 255, 255))
        display.draw_text(40, 150, f"{saved_file_name}", arcadepix, color565(102, 255, 255))
    else:
        display.draw_text(40, 120, "Error saving file", arcadepix, color565(255, 0, 0))
    await asyncio.sleep(5)
    gc.collect()  # คืนหน่วยความจำ
    display.fill_rectangle(0, 0, 320, 240, color565(0, 0, 0))  # ล้างหน้าจอ
    Homedisplays_initial()

#-------------------------------# เริ่มการทำงานการวนลูปหลัก #--------------------------#

#เรียกแสดงผลเมนูครั้งแรก
display.clear()  # ล้างหน้าจอก่อน
draw_gradient_background()
draw_logo_and_effects()
show_tutor_screen()
Homedisplays_initial()

 #------------------------------# ลูปหลักสำหรับการทำงาน #------------------------------#

current_mode = None  # ตัวแปรเก็บโหมดปัจจุบัน
button2_last_state = 0 # ตัวแปรสำหรับเก็บสถานะของปุ่ม

while True:
    if current_mode is None:  # อัปเดตค่า Temp/pH เฉพาะในหน้าหลัก
        dynamicHomedisplays()

    # ตรวจจับการกดปุ่มเลือกเมนู
    if button1_pin.value() == 1:  # เมื่อกดปุ่มเลือกเมนู
        while button1_pin.value() == 1:
            sleep_ms(1)  # รอจนกว่าจะปล่อยปุ่ม
        beep()  # เล่นเสียงยืนยันการเลือกเมนู
        display.clear()  # ล้างหน้าจอ Homedisplay

        if   selected_option == 1:
            menu1_loop()  # เรียกเมนู Calibrate pH sensor
        elif selected_option == 2:
            menu2_loop()  # เรียกเมนู pH sensor Test
        elif selected_option == 3:
            menu3_loop()  # เรียกเมนู Calibrate Flow Rate
        elif selected_option == 4:
            menu4_loop()  # เรียกเมนู Flow Rate Test
        elif selected_option == 5:
            menu5_loop()  # เรียกเมนู Purge
        elif selected_option == 6:
            asyncio.run(menu6_loop())  # เรียกเมนู Full Auto Mode

    # ตรวจจับการกดปุ่มเลื่อนเมนู
    if button2_pin.value() == 1 and button2_last_state == 0:  # เมื่อกดปุ่มเลื่อนเมนู และสถานะเปลี่ยน
        button2_last_state = 1  # อัปเดตสถานะเป็นกดแล้ว
        beep()  # เล่นเสียงยืนยันการเลื่อนเมนู

        previous_option = selected_option  # เก็บตัวเลือกก่อนหน้า
        selected_option = (selected_option % 6) + 1  # เลื่อนตำแหน่งเมนู (วนลูป 1-6)
        Homedisplays(selected_option, previous_option)  # อัปเดตเฉพาะข้อความที่เปลี่ยน

    if button2_pin.value() == 0:  # เมื่อปุ่มไม่ได้ถูกกด
        button2_last_state = 0  # อัปเดตสถานะเป็นไม่ได้กด


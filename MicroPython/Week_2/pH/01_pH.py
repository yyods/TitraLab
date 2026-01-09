# ==============================================================================
# 01_pH.py - การวัดค่า pH และอุณหภูมิ (pH and Temperature Measurement)
# ==============================================================================
# โปรแกรมนี้สาธิตการอ่านค่า pH จากเซ็นเซอร์และแสดงผลบนจอ TFT
# This program demonstrates reading pH from sensor and displaying on TFT
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การใช้ ADC (Analog-to-Digital Converter) อ่านค่าจากเซ็นเซอร์ pH
# 2. เข้าใจการบันทึกข้อมูลการทดลองลงไฟล์ CSV
# 3. ใช้ Timer และ Interrupt สำหรับการบันทึกข้อมูลอัตโนมัติ
#
# หลักการทางเคมี (Chemistry Principles):
# หัววัด pH ให้สัญญาณแรงดันไฟฟ้า (mV) ตามสมการ Nernst:
# E = E0 - (2.303RT/nF) × pH
# ที่ 25°C: ความชันทฤษฎี = -59.16 mV/pH
#
# Hardware Configuration:
# - GPIO 25: pH Sensor (ADC)
# - GPIO 16: DS18B20 Temperature Sensor
# - GPIO 34: Button 1 (Start/Stop recording)
# ==============================================================================

from ili9341 import Display, color565
from xglcd_font import XglcdFont
from machine import Pin, SPI, ADC, Timer
import time
import onewire
import ds18x20

# ==============================================================================
# การตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
# DS18B20 Temperature Sensor Setup
# ==============================================================================
# เซ็นเซอร์ DS18B20 ใช้โปรโตคอล OneWire ที่ GPIO16
# DS18B20 sensor uses OneWire protocol on GPIO16
dat = Pin(16)
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# สแกนหาเซ็นเซอร์ที่เชื่อมต่อ (Scan for connected sensors)
sensors = ds.scan()
if not sensors:
    print("ไม่พบเซ็นเซอร์ DS18B20 (DS18B20 sensor not found)")

# ==============================================================================
# การตั้งค่าจอแสดงผล TFT ILI9341
# TFT Display Setup (ILI9341)
# ==============================================================================
spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, cs=Pin(15), dc=Pin(27), rst=Pin(0), width=240, height=320, rotation=90)

# โหลดฟอนต์ (Load font)
font = XglcdFont("EspressoDolce18x24.c", 18, 24)

# ==============================================================================
# การตั้งค่า ADC สำหรับเซ็นเซอร์ pH
# ADC Setup for pH Sensor
# ==============================================================================
# ADC (Analog-to-Digital Converter) แปลงสัญญาณแอนะล็อกเป็นดิจิทัล
# ATTN_11DB ตั้งค่าให้อ่านแรงดัน 0-3.3V (ความละเอียด 12-bit: 0-4095)
adc = ADC(Pin(25))
adc.atten(ADC.ATTN_11DB)

# ==============================================================================
# การตั้งค่าปุ่มกด
# Button Setup
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull-up/pull-down
# Note: GPIO34 is input-only, does NOT support internal pull-up/pull-down
# ต้องใช้ตัวต้านทาน pull-up/pull-down ภายนอก
# Must use external pull-up/pull-down resistor
button_1 = Pin(34, Pin.IN)

# ==============================================================================
# ตำแหน่งข้อความบนจอ (Text positions on display)
# ==============================================================================
text1_x = 160 - int(font.measure_text('Temperature:', spacing=1) / 2)
text1_y = 80 - 12 - 15
text2_x = 160 - int(font.measure_text('99.99 C', spacing=1) / 2)
text2_y = 80 - 12 + 15

text3_x = 160 - int(font.measure_text('pH:', spacing=1) / 2)
text3_y = 160 - 12 - 15
text4_x = 160 - int(font.measure_text('0.00', spacing=1) / 2)
text4_y = 160 - 12 + 15

# ==============================================================================
# ตัวแปรสถานะ (State variables)
# ==============================================================================
current_temp = None      # ค่าอุณหภูมิปัจจุบัน (Current temperature)
current_ph = None        # ค่า pH ปัจจุบัน (Current pH)
recording = False        # สถานะการบันทึก (Recording state)
ph_data = []             # ข้อมูล pH ที่บันทึก (Recorded pH data)
recording_round = 0      # รอบการบันทึก (Recording round)
timer = None             # Timer object
start_time = 0           # เวลาเริ่มต้นการบันทึก (Recording start time)

# ==============================================================================
# ฟังก์ชันแสดงค่าอุณหภูมิ (Display temperature function)
# ==============================================================================
def show_temperature(temp):
    """
    แสดงค่าอุณหภูมิบนจอ TFT โดยอัปเดตเฉพาะเมื่อค่าเปลี่ยน
    Display temperature on TFT, update only when value changes
    """
    global current_temp

    temp_text = f"{temp:.2f} C"

    if temp != current_temp:
        current_temp = temp
        temp_x = 160 - int(font.measure_text(temp_text, spacing=1) / 2)

        # ลบข้อความเก่า (Clear old text)
        display.draw_text(text2_x, text2_y, ' ' * len(f"{99.99:.2f} C"), font,
                         color565(0, 0, 0), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

        # แสดงข้อความใหม่ (Draw new text)
        display.draw_text(temp_x, text2_y, temp_text, font,
                         color565(255, 87, 255), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

# ==============================================================================
# ฟังก์ชันแสดงค่า pH (Display pH function)
# ==============================================================================
def show_ph(ph):
    """
    แสดงค่า pH บนจอ TFT โดยอัปเดตเฉพาะเมื่อค่าเปลี่ยน
    Display pH on TFT, update only when value changes
    """
    global current_ph

    ph_text = f"{ph:.2f}"

    if ph != current_ph:
        current_ph = ph
        ph_x = 160 - int(font.measure_text(ph_text, spacing=1) / 2)

        # ลบข้อความเก่า (Clear old text)
        display.draw_text(text4_x, text4_y, ' ' * len(f"{0.00:.2f}"), font,
                         color565(0, 0, 0), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

        # แสดงข้อความใหม่ (Draw new text)
        display.draw_text(ph_x, text4_y, ph_text, font,
                         color565(87, 255, 255), background=color565(0, 0, 0),
                         landscape=False, spacing=1)

# ==============================================================================
# ฟังก์ชันบันทึกค่า pH (Record pH function)
# ==============================================================================
def record_ph(t):
    """
    Callback function สำหรับ Timer - บันทึกค่า pH ทุกวินาที
    Timer callback - records pH every second
    """
    global ph_data, recording, start_time

    if recording:
        # อ่านค่า ADC จากเซ็นเซอร์ pH (Read ADC value from pH sensor)
        # หมายเหตุ: ค่านี้เป็นค่า ADC ดิบ (0-4095) ยังไม่แปลงเป็น pH จริง
        # Note: This is raw ADC value (0-4095), not converted to actual pH
        ph_value = adc.read()
        ph = ph_value  # ต้องใช้สมการ calibration เพื่อแปลงเป็น pH จริง

        show_ph(ph)
        elapsed_time = time.time() - start_time
        ph_data.append(ph)

        print(f"เวลา (Time): {elapsed_time:.2f} s, pH: {ph:.2f}")

        # บันทึก 45 วินาทีแล้วหยุด (Stop after 45 seconds)
        if elapsed_time >= 45:
            save_ph_data()
            recording = False
            t.deinit()

# ==============================================================================
# ฟังก์ชันบันทึกข้อมูลลงไฟล์ CSV (Save data to CSV file)
# ==============================================================================
def save_ph_data():
    """
    บันทึกข้อมูล pH ลงไฟล์ CSV พร้อมคำนวณค่าเฉลี่ย
    Save pH data to CSV file with average calculation
    """
    global ph_data, recording_round

    filename = f'ph_data_round_{recording_round}.csv'

    try:
        with open(filename, 'w') as f:
            f.write('Time,pH\n')
            for i, ph in enumerate(ph_data):
                f.write(f"{i},{ph}\n")

            # คำนวณค่าเฉลี่ย (Calculate average)
            avg_ph = sum(ph_data) / len(ph_data) if ph_data else 0
            f.write(f"\nAverage pH,{avg_ph:.2f}\n")

        print(f"บันทึกข้อมูลสำเร็จ (Data saved): {filename}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด (Error): {e}")

    ph_data.clear()

# ==============================================================================
# ฟังก์ชัน Callback สำหรับปุ่มกด (Button callback function)
# ==============================================================================
def button_callback(pin):
    """
    จัดการเมื่อกดปุ่ม - เริ่ม/หยุดการบันทึกข้อมูล
    Handle button press - start/stop recording
    """
    global recording, start_time, recording_round, timer

    if pin.value() == 0:  # ปุ่มถูกกด (Button pressed)
        if not recording:
            # เริ่มบันทึก (Start recording)
            recording = True
            start_time = time.time()
            recording_round += 1
            print(f"เริ่มบันทึกรอบที่ (Start recording round) {recording_round}")
            timer.init(period=1000, mode=Timer.PERIODIC, callback=record_ph)
        else:
            # หยุดบันทึก (Stop recording)
            recording = False
            print(f"หยุดบันทึกรอบที่ (Stop recording round) {recording_round}")
            timer.deinit()
            save_ph_data()

# ==============================================================================
# โปรแกรมหลัก (Main program)
# ==============================================================================
print("=" * 50)
print("การวัดค่า pH และอุณหภูมิ (pH and Temperature Measurement)")
print("กดปุ่ม 1 เพื่อเริ่ม/หยุดบันทึก (Press Button 1 to start/stop)")
print("=" * 50)

# ตั้งค่า interrupt สำหรับปุ่มกด (Setup button interrupt)
button_1.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)

# สร้าง Timer (Create Timer)
timer = Timer(0)

# ล้างหน้าจอ (Clear display)
display.clear(color565(0, 0, 0))

# แสดงหัวข้อ (Display headers)
display.draw_text(text1_x, text1_y, 'Temperature:', font,
                 color565(255, 251, 104), background=0, landscape=False, spacing=1)
display.draw_text(text3_x, text3_y, 'pH:', font,
                 color565(255, 251, 104), background=0, landscape=False, spacing=1)

# ==============================================================================
# Main loop - อ่านและแสดงค่าอุณหภูมิ
# ==============================================================================
try:
    while True:
        if sensors:
            ds.convert_temp()
            time.sleep_ms(750)
            for sensor in sensors:
                temp = ds.read_temp(sensor)
                show_temperature(temp)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    if timer:
        timer.deinit()
    print("ปิด Timer แล้ว (Timer released)")

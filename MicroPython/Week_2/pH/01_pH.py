from ili9341 import Display, color565
from xglcd_font import XglcdFont
from machine import Pin, SPI, ADC, Timer
import time
import onewire
import ds18x20

# กำหนดขาข้อมูล DS18B20 ที่เชื่อมต่อกับขา P16
dat = Pin(16)
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# สแกนเซ็นเซอร์ DS18B20 ที่เชื่อมต่อ
sensors = ds.scan()

# กำหนด SPI และการแสดงผลบนจอ ILI9341
spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, cs=Pin(15), dc=Pin(27), rst=Pin(0), width=240, height=320, rotation=90)

# โหลดฟอนต์ EspressoDolce18x24
font = XglcdFont("EspressoDolce18x24.c", 18, 24)

# กำหนดขา ADC สำหรับเซ็นเซอร์ pH
adc = ADC(Pin(25))
adc.atten(ADC.ATTN_11DB)

# กำหนดปุ่ม button_1
button_1 = Pin(34, Pin.IN, Pin.PULL_UP)

# ตำแหน่งเริ่มต้นของข้อความ
text1_x = 160 - int(font.measure_text('Temperature:', spacing=1) / 2)
text1_y = 80 - 12 - 15
text2_x = 160 - int(font.measure_text('99.99 C', spacing=1) / 2)
text2_y = 80 - 12 + 15

text3_x = 160 - int(font.measure_text('pH:', spacing=1) / 2)
text3_y = 160 - 12 - 15
text4_x = 160 - int(font.measure_text('0.00', spacing=1) / 2)
text4_y = 160 - 12 + 15

# ตัวแปรเพื่อติดตามค่าอุณหภูมิและ pH ปัจจุบัน
current_temp = None
current_ph = None

# ตัวแปรสำหรับการจัดการเวลา
recording = False
ph_data = []
recording_round = 0
timer = None

# ฟังก์ชันแสดงค่าอุณหภูมิโดยไม่มีการกระพริบ
def show_temperature(temp):
    global current_temp
    
    # แปลงอุณหภูมิเป็นข้อความ
    temp_text = f"{temp:.2f} C"
    
    # เฉพาะการอัปเดตจอหากมีการเปลี่ยนแปลงของอุณหภูมิ
    if temp != current_temp:
        current_temp = temp
        
        # คำนวณตำแหน่งที่จะวาดข้อความกลางจอ
        temp_x = 160 - int(font.measure_text(temp_text, spacing=1) / 2)
        temp_y = text2_y
        
        # ลบข้อความอุณหภูมิเก่าด้วยการวาดพื้นหลังสีดำทับ
        display.draw_text(text2_x, text2_y, ' ' * len(f"{99.99:.2f} C"), font, color565(0, 0, 0), background=color565(0, 0, 0), landscape=False, spacing=1)
        
        # วาดข้อความอุณหภูมิใหม่
        display.draw_text(temp_x, temp_y, temp_text, font, color565(255, 87, 255), background=color565(0, 0, 0), landscape=False, spacing=1)

# ฟังก์ชันแสดงค่าพีเอชโดยไม่มีการกระพริบ
def show_ph(ph):
    global current_ph
    
    # แปลงค่าพีเอชเป็นข้อความ
    ph_text = f"{ph:.2f}"
    
    # เฉพาะการอัปเดตจอหากมีการเปลี่ยนแปลงของพีเอช
    if ph != current_ph:
        current_ph = ph
        
        # คำนวณตำแหน่งที่จะวาดข้อความกลางจอ
        ph_x = 160 - int(font.measure_text(ph_text, spacing=1) / 2)
        ph_y = text4_y
        
        # ลบข้อความพีเอชเก่าด้วยการวาดพื้นหลังสีดำทับ
        display.draw_text(text4_x, text4_y, ' ' * len(f"{0.00:.2f}"), font, color565(0, 0, 0), background=color565(0, 0, 0), landscape=False, spacing=1)
        
        # วาดข้อความพีเอชใหม่
        display.draw_text(ph_x, ph_y, ph_text, font, color565(87, 255, 255), background=color565(0, 0, 0), landscape=False, spacing=1)

# ฟังก์ชันสำหรับการบันทึกค่าพีเอช
def record_ph(timer):
    global ph_data, recording
    
    if recording:
        # อ่านค่าพีเอชจากเซ็นเซอร์ pH
        ph_value = adc.read()
        ph = (ph_value)  # แปลงค่า ADC เป็นค่า pH (สมมุติให้ช่วง 0-14)
        show_ph(ph)
        elapsed_time = time.time() - start_time
        ph_data.append(ph)
        print(f"Time: {elapsed_time:.2f} s, pH: {ph:.2f}")  # แสดงผลใน Shell
        if elapsed_time >= 45:  # บันทึกข้อมูลเป็นเวลา 45 วินาที
            save_ph_data()
            recording = False
            timer.deinit()

# ฟังก์ชันสำหรับการบันทึกข้อมูล pH ลงในไฟล์ CSV
def save_ph_data():
    global ph_data, recording_round
    filename = f'ph_data_round_{recording_round}.csv'
    with open(filename, 'w') as f:
        f.write('Time,pH\n')
        for i, ph in enumerate(ph_data):
            f.write(f"{i},{ph}\n")
        avg_ph = sum(ph_data) / len(ph_data) if ph_data else 0
        f.write(f"\nAverage pH,{avg_ph:.2f}\n")
    print(f"pH data saved to {filename}.")
    ph_data.clear()

# ฟังก์ชัน callback สำหรับปุ่ม button_1
def button_callback(pin):
    global recording, start_time, recording_round, timer
    
    if pin.value() == 0:  # ตรวจสอบว่าปุ่มถูกกด
        if not recording:  # หากยังไม่ได้บันทึกข้อมูล
            recording = True
            start_time = time.time()
            recording_round += 1
            print(f"Start recording pH data, round {recording_round}.")
            timer.init(period=1000, mode=Timer.PERIODIC, callback=record_ph)
        else:  # หากกำลังบันทึกข้อมูล ให้รีเซ็ต
            recording = False
            print(f"Stop recording pH data, round {recording_round}.")
            timer.deinit()
            save_ph_data()

# กำหนดการเรียก callback เมื่อปุ่มถูกกด
button_1.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)

# ตั้งค่า Timer
timer = Timer(0)

# ล้างหน้าจอให้ดำสนิท
display.clear(color565(0, 0, 0))

# แสดงข้อความเริ่มต้น 'Temperature:' และ 'pH:'
display.draw_text(text1_x, text1_y, 'Temperature:', font, color565(255, 251, 104), background=0, landscape=False, spacing=1)
display.draw_text(text3_x, text3_y, 'pH:', font, color565(255, 251, 104), background=0, landscape=False, spacing=1)

while True:
    ds.convert_temp()
    time.sleep_ms(750)
    for sensor in sensors:
        temp = ds.read_temp(sensor)
        show_temperature(temp)
    time.sleep(2)


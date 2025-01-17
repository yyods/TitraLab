from time import sleep_ms, ticks_ms, ticks_diff  # นำเข้าโมดูลสำหรับจัดการเวลา
from machine import Pin, ADC, SPI  # นำเข้า Pin, ADC, SPI สำหรับควบคุมฮาร์ดแวร์
from xglcd_font import XglcdFont  # นำเข้า XglcdFont สำหรับจัดการฟอนต์
from ili9341 import Display, color565  # นำเข้า Display และ color565 สำหรับจัดการจอแสดงผล
from onewire import OneWire  # นำเข้า OneWire สำหรับสื่อสารกับเซ็นเซอร์
from ds18x20 import DS18X20  # นำเข้า DS18X20 สำหรับจัดการเซ็นเซอร์ DS18B20

# ตั้งค่า ADC สำหรับเซ็นเซอร์วัด pH
adc_pin = 25  # Pin สำหรับเชื่อมต่อเซ็นเซอร์ pH
pH_adc = ADC(Pin(adc_pin))  # สร้างอ็อบเจกต์ ADC สำหรับอ่านค่าจาก pH sensor
pH_adc.atten(ADC.ATTN_11DB)  # ตั้งค่า ADC ให้สามารถอ่านค่าได้เต็มช่วง

# ตั้งค่าจอแสดงผล
spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))  # กำหนด SPI bus และพินที่ใช้
display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0), width=320, height=240, rotation=90)  # สร้างอ็อบเจกต์สำหรับจอแสดงผล

# โหลดฟอนต์สำหรับแสดงข้อความบนจอ
font = XglcdFont('EspressoDolce18x24.c', 18, 24)  # โหลดฟอนต์ EspressoDolce18x24

# ตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
one_wire_pin = Pin(16)  # Pin สำหรับการเชื่อมต่อ OneWire
ds_sensor = DS18X20(OneWire(one_wire_pin))  # สร้างอ็อบเจกต์ DS18B20 สำหรับอ่านค่าอุณหภูมิ
roms = ds_sensor.scan()  # สแกนอุปกรณ์ที่เชื่อมต่อ

# ค่าเริ่มต้นสำหรับ pH Buffer และผลการวัด
buffer_pH_values = [4.00, 7.00, 10.00]  # ค่า pH Buffer ที่ต้องใช้สอบเทียบ
calibrated_voltages = [0.0, 0.0, 0.0]  # ค่าแรงดันไฟฟ้าที่ได้จากการสอบเทียบ
temperatures = [0.0, 0.0, 0.0]  # ค่าอุณหภูมิที่วัดได้ระหว่างการสอบเทียบ

# ตั้งค่าปุ่มสำหรับเริ่มการวัด
button1 = Pin(34, Pin.IN, Pin.PULL_UP)  # ปุ่ม Button1 เชื่อมต่อกับ GPIO34 และดึงค่าเริ่มต้นขึ้น

# ฟังก์ชันสำหรับอ่านแรงดันไฟฟ้าจาก pH sensor
def read_voltage():
    adc_value = pH_adc.read()  # อ่านค่า ADC จากเซ็นเซอร์
    voltage = adc_value * 3.5 / 4095 / 6  # แปลงค่า ADC เป็นแรงดันไฟฟ้า
    return voltage  # ส่งคืนค่าแรงดันไฟฟ้า

# ฟังก์ชันสำหรับอ่านค่าอุณหภูมิจากเซ็นเซอร์ DS18B20
def read_temperature():
    if roms:  # ตรวจสอบว่ามีเซ็นเซอร์เชื่อมต่อ
        ds_sensor.convert_temp()  # เริ่มการวัดอุณหภูมิ
        sleep_ms(750)  # รอให้การวัดเสร็จสิ้น
        temperature = ds_sensor.read_temp(roms[0])  # อ่านค่าอุณหภูมิจากเซ็นเซอร์ตัวแรก
        return temperature  # ส่งคืนค่าอุณหภูมิ
    return None  # หากไม่มีเซ็นเซอร์เชื่อมต่อ ส่งคืนค่า None

# ฟังก์ชันสำหรับสอบเทียบค่า pH
def calibrate_pH():
    global calibrated_voltages, temperatures  # ใช้ตัวแปร global สำหรับผลการวัด

    for i, buffer_pH in enumerate(buffer_pH_values):  # วนลูปสำหรับค่า pH แต่ละตัว
        # แสดงข้อความเตรียมการสอบเทียบ
        display.clear()  # ล้างหน้าจอ
        display.draw_text(70, 70, f"Prepare pH {buffer_pH:.2f}", font, color565(255, 255, 255))  # แสดงข้อความเตรียมการ
        display.draw_text(40, 140, "Press Button_1 to start", font, color565(0, 255, 0))  # แสดงข้อความรอการกดปุ่ม

        while button1.value() == 1:  # รอจนกว่าผู้ใช้จะกดปุ่ม
            sleep_ms(50)  # หน่วงเวลาเพื่อประหยัดทรัพยากร

        while button1.value() == 0:  # รอจนกว่าผู้ใช้จะปล่อยปุ่ม
            sleep_ms(50)

        # เริ่มนับถอยหลัง
        countdown_time = 10  # ตั้งค่าระยะเวลานับถอยหลัง (10 วินาที)
        display.clear()
        display.draw_text(50, 70, f"Calibrating pH {buffer_pH:.2f}", font, color565(255, 255, 255))  # แสดงข้อความเริ่มการสอบเทียบ
        display.draw_text(50, 140, "Time Left:", font, color565(255, 255, 255))  # แสดงข้อความนับถอยหลัง

        start_time = ticks_ms()  # บันทึกเวลาเริ่มต้น
        previous_time = None  # ใช้สำหรับเก็บเวลาที่แสดงก่อนหน้า

        while ticks_diff(ticks_ms(), start_time) < countdown_time * 1000:  # ตรวจสอบว่านับถอยหลังครบ 10 วินาทีหรือยัง
            remaining_time = countdown_time - ticks_diff(ticks_ms(), start_time) // 1000  # คำนวณเวลาที่เหลือ
            if remaining_time != previous_time:  # อัปเดตเฉพาะเมื่อเวลาที่เหลือเปลี่ยน
                display.fill_rectangle(180, 140, 80, 30, color565(0, 0, 0))  # ลบตัวเลขเก่า
                display.draw_text(180, 140, f"{remaining_time} s", font, color565(255, 255, 0))  # แสดงเวลาที่เหลือใหม่
                previous_time = remaining_time  # อัปเดตค่าเวลาที่แสดงล่าสุด

            sleep_ms(100)  # ลดการอัปเดตที่ไม่จำเป็น

        # อ่านแรงดันไฟฟ้าหลังจากครบ 10 วินาที
        voltage = read_voltage()
        calibrated_voltages[i] = voltage  # บันทึกค่าแรงดันไฟฟ้าที่วัดได้

        # อ่านค่าอุณหภูมิ
        temperature = read_temperature()
        temperatures[i] = temperature if temperature is not None else "N/A"  # บันทึกค่าอุณหภูมิ

        # แสดงผลการวัดค่า
        display.clear()
        display.draw_text(50, 50, f"pH {buffer_pH:.2f} Measured!", font, color565(0, 255, 0))  # แสดงข้อความผลการวัด
        display.draw_text(50, 100, f"Voltage: {voltage:.3f} V", font, color565(255, 193, 34))  # แสดงค่าแรงดันไฟฟ้า
        display.draw_text(50, 150, f"Temp: {temperature:.1f} C", font, color565(0, 191, 255))  # แสดงค่าอุณหภูมิ
        print(f"pH {buffer_pH:.2f}: Voltage = {voltage:.3f} V, Temp = {temperature:.2f} C")  # พิมพ์ค่าลง Shell

        sleep_ms(4000)  # หน่วงเวลาแสดงผล 4 วินาที

    # แสดงหน้าสรุปเมื่อวัดค่าครบทุก pH
    display.clear()
    display.draw_text(50, 30, "Calibration Complete!", font, color565(0, 255, 0))  # แสดงข้อความการสอบเทียบเสร็จสิ้น
    for i, buffer_pH in enumerate(buffer_pH_values):  # วนลูปแสดงผลสรุป
        y_offset = 70 + i * 40
        display.draw_text(30, y_offset, f"pH {buffer_pH:.2f}:", font, color565(255, 255, 255))  # แสดงค่า pH
        display.draw_text(120, y_offset, f"{calibrated_voltages[i]:.3f} V", font, color565(255, 193, 34))  # แสดงแรงดันไฟฟ้าที่วัดได้
        display.draw_text(210, y_offset, f"{temperatures[i]:.2f} C", font, color565(0, 191, 255))  # แสดงค่าอุณหภูมิที่วัดได้

    while True:  # ค้างหน้าสรุปเพื่อให้ผู้ใช้ตรวจสอบ
        sleep_ms(100)  # หน่วงเวลาการวนลูปเพื่อประหยัดทรัพยากร

# เรียกใช้ฟังก์ชันสอบเทียบค่า pH
calibrate_pH()

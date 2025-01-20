from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin, ADC, SPI
from xglcd_font import XglcdFont
from ili9341 import Display, color565
from onewire import OneWire
from ds18x20 import DS18X20

# ตั้งค่า ADC สำหรับเซ็นเซอร์วัด pH
adc_pin = 25
pH_adc = ADC(Pin(adc_pin))
pH_adc.atten(ADC.ATTN_11DB)  # ตั้งค่า ADC ให้อ่านค่าได้เต็มช่วง

# ตั้งค่าจอแสดงผล
spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0), width=320, height=240, rotation=90)

# โหลดฟอนต์สำหรับแสดงข้อความบนจอ
font = XglcdFont('EspressoDolce18x24.c', 18, 24)

# ตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
one_wire_pin = Pin(16)
ds_sensor = DS18X20(OneWire(one_wire_pin))
roms = ds_sensor.scan()

# ค่า pH Buffer สำหรับการสอบเทียบ
buffer_pH_values = [4.00, 7.00, 10.00]
calibrated_voltages = [0.0, 0.0, 0.0]  # ค่าแรงดันไฟฟ้า (mV)
temperatures = [0.0, 0.0, 0.0]  # ค่าอุณหภูมิ

# ตั้งค่าปุ่มกด
button1 = Pin(34, Pin.IN, Pin.PULL_UP)

# ฟังก์ชันอ่านแรงดันไฟฟ้าเป็น **mV**
def read_voltage_mv():
    adc_value = pH_adc.read()
    voltage_mv = adc_value * 3300 / 4095  # แปลงค่า ADC เป็นมิลลิโวลต์
    return voltage_mv

# ฟังก์ชันอ่านอุณหภูมิ
def read_temperature():
    if roms:
        ds_sensor.convert_temp()
        sleep_ms(750)
        return ds_sensor.read_temp(roms[0])
    return None

# ฟังก์ชันสอบเทียบค่า pH
def calibrate_pH():
    global calibrated_voltages, temperatures

    for i, buffer_pH in enumerate(buffer_pH_values):
        # แสดงข้อความเตรียมการสอบเทียบ
        display.clear()
        display.draw_text(70, 70, f"Prepare pH {buffer_pH:.2f}", font, color565(255, 255, 255))
        display.draw_text(40, 140, "Press Button_1 to start", font, color565(0, 255, 0))

        while button1.value() == 1:
            sleep_ms(50)
        while button1.value() == 0:
            sleep_ms(50)

        # เริ่มนับถอยหลัง
        countdown_time = 1
        display.clear()
        display.draw_text(50, 70, f"Calibrating pH {buffer_pH:.2f}", font, color565(255, 255, 255))
        display.draw_text(50, 140, "Time Left:", font, color565(255, 255, 255))

        start_time = ticks_ms()
        previous_time = None

        while ticks_diff(ticks_ms(), start_time) < countdown_time * 1000:
            remaining_time = countdown_time - ticks_diff(ticks_ms(), start_time) // 1000
            if remaining_time != previous_time:
                display.fill_rectangle(180, 140, 80, 30, color565(0, 0, 0))
                display.draw_text(180, 140, f"{remaining_time} s", font, color565(255, 255, 0))
                previous_time = remaining_time

            sleep_ms(100)

        # อ่านแรงดันไฟฟ้าเป็น mV
        voltage_mv = read_voltage_mv()
        calibrated_voltages[i] = voltage_mv

        # อ่านอุณหภูมิ
        temperature = read_temperature()
        temperatures[i] = temperature if temperature is not None else "N/A"

        # แสดงผล
        display.clear()
        display.draw_text(50, 50, f"pH {buffer_pH:.2f} Measured!", font, color565(0, 255, 0))
        display.draw_text(50, 100, f"Voltage: {voltage_mv:.1f} mV", font, color565(255, 193, 34))  # เปลี่ยนเป็น mV
        display.draw_text(50, 150, f"Temp: {temperature:.1f} C", font, color565(0, 191, 255))

        print(f"pH {buffer_pH:.2f}: Voltage = {voltage_mv:.1f} mV, Temp = {temperature:.2f} C")

        sleep_ms(4000)

    # แสดงหน้าสรุป
    display.clear()
    display.draw_text(55, 30, "Calibration Complete!", font, color565(0, 255, 0))
    for i, buffer_pH in enumerate(buffer_pH_values):
        y_offset = 70 + i * 40
        display.draw_text(20, y_offset, f"pH {buffer_pH:.1f}:", font, color565(255, 255, 255))
        display.draw_text(100, y_offset, f"{calibrated_voltages[i]:.3f} mV", font, color565(255, 193, 34))  # ใช้ mV
        display.draw_text(230, y_offset, f"{temperatures[i]:.2f} C", font, color565(0, 191, 255))

    while True:
        sleep_ms(100)

# เรียกใช้ฟังก์ชันสอบเทียบค่า pH
calibrate_pH()


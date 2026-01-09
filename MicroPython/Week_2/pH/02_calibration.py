# ==============================================================================
# 02_calibration.py - การสอบเทียบเซ็นเซอร์ pH (pH Sensor Calibration)
# ==============================================================================
# โปรแกรมนี้สาธิตการสอบเทียบหัววัด pH ด้วยสารละลายบัฟเฟอร์มาตรฐาน 3 จุด
# This program demonstrates 3-point pH sensor calibration with buffer solutions
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้หลักการสอบเทียบ (calibration) เซ็นเซอร์
# 2. เข้าใจความสัมพันธ์ระหว่างแรงดันไฟฟ้า (mV) และค่า pH
# 3. ใช้สารละลายบัฟเฟอร์มาตรฐาน pH 4.00, 7.00, 10.00
#
# หลักการทางเคมี (Chemistry Principles):
# การสอบเทียบ 3 จุดใช้สารละลายบัฟเฟอร์มาตรฐาน (standard buffer solutions)
# เพื่อสร้างกราฟความสัมพันธ์ระหว่างแรงดันไฟฟ้า (mV) กับค่า pH
#
# ตามสมการ Nernst: E = E0 - (2.303RT/nF) × pH
# - ที่ 25°C: slope ทฤษฎี = -59.16 mV/pH
# - การสอบเทียบ 3 จุดช่วยตรวจสอบ linearity ของหัววัด
#
# Hardware Configuration:
# - GPIO 25: pH Sensor (ADC)
# - GPIO 16: DS18B20 Temperature Sensor
# - GPIO 34: Button 1 (Confirm calibration point)
# ==============================================================================

from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin, ADC, SPI
from xglcd_font import XglcdFont
from ili9341 import Display, color565
from onewire import OneWire
from ds18x20 import DS18X20

# ==============================================================================
# การตั้งค่า ADC สำหรับเซ็นเซอร์ pH
# ADC Setup for pH Sensor
# ==============================================================================
# ADC แปลงสัญญาณแอนะล็อก (0-3.3V) เป็นค่าดิจิทัล (0-4095)
# ADC converts analog signal (0-3.3V) to digital value (0-4095)
adc_pin = 25
pH_adc = ADC(Pin(adc_pin))
pH_adc.atten(ADC.ATTN_11DB)  # ตั้งค่าให้อ่านแรงดัน 0-3.3V

# ==============================================================================
# การตั้งค่าจอแสดงผล TFT
# TFT Display Setup
# ==============================================================================
spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0), width=320, height=240, rotation=90)

# โหลดฟอนต์ (Load font)
font = XglcdFont('EspressoDolce18x24.c', 18, 24)

# ==============================================================================
# การตั้งค่าเซ็นเซอร์อุณหภูมิ DS18B20
# DS18B20 Temperature Sensor Setup
# ==============================================================================
one_wire_pin = Pin(16)
ds_sensor = DS18X20(OneWire(one_wire_pin))
roms = ds_sensor.scan()

if not roms:
    print("ไม่พบเซ็นเซอร์ DS18B20 (DS18B20 sensor not found)")

# ==============================================================================
# ค่าบัฟเฟอร์มาตรฐานสำหรับการสอบเทียบ
# Standard Buffer Values for Calibration
# ==============================================================================
# ใช้สารละลายบัฟเฟอร์ pH 4.00, 7.00, 10.00 เพื่อครอบคลุมช่วง pH ที่ใช้งาน
# Use pH 4.00, 7.00, 10.00 buffer solutions to cover working pH range
buffer_pH_values = [4.00, 7.00, 10.00]
calibrated_voltages = [0.0, 0.0, 0.0]  # ค่าแรงดันที่วัดได้ (mV)
temperatures = [0.0, 0.0, 0.0]         # ค่าอุณหภูมิขณะสอบเทียบ

# ==============================================================================
# การตั้งค่าปุ่มกด
# Button Setup
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull-up/pull-down
# Note: GPIO34 is input-only, does NOT support internal pull-up/pull-down
button1 = Pin(34, Pin.IN)

# ==============================================================================
# ฟังก์ชันอ่านแรงดันไฟฟ้า (mV)
# Read Voltage Function (mV)
# ==============================================================================
def read_voltage_mv():
    """
    อ่านค่า ADC และแปลงเป็นมิลลิโวลต์ (mV)
    Read ADC value and convert to millivolts (mV)

    การคำนวณ (Calculation):
    - ADC 12-bit: 0-4095
    - แรงดันอ้างอิง: 3300 mV (3.3V)
    - voltage_mv = (ADC_value / 4095) × 3300
    """
    adc_value = pH_adc.read()
    voltage_mv = adc_value * 3300 / 4095
    return voltage_mv

# ==============================================================================
# ฟังก์ชันอ่านอุณหภูมิ
# Read Temperature Function
# ==============================================================================
def read_temperature():
    """
    อ่านค่าอุณหภูมิจากเซ็นเซอร์ DS18B20
    Read temperature from DS18B20 sensor

    หมายเหตุ: อุณหภูมิมีผลต่อค่า pH ตามสมการ Nernst
    Note: Temperature affects pH according to Nernst equation
    """
    if roms:
        ds_sensor.convert_temp()
        sleep_ms(750)  # รอการแปลงค่า (Wait for conversion)
        return ds_sensor.read_temp(roms[0])
    return None

# ==============================================================================
# ฟังก์ชันสอบเทียบ pH
# pH Calibration Function
# ==============================================================================
def calibrate_pH():
    """
    ดำเนินการสอบเทียบ pH 3 จุด
    Perform 3-point pH calibration

    ขั้นตอน (Steps):
    1. แช่หัววัดในบัฟเฟอร์ pH 4.00 → กดปุ่มบันทึก
    2. แช่หัววัดในบัฟเฟอร์ pH 7.00 → กดปุ่มบันทึก
    3. แช่หัววัดในบัฟเฟอร์ pH 10.00 → กดปุ่มบันทึก
    """
    global calibrated_voltages, temperatures

    print("=" * 50)
    print("เริ่มการสอบเทียบ pH (Starting pH Calibration)")
    print("=" * 50)

    for i, buffer_pH in enumerate(buffer_pH_values):
        # แสดงข้อความเตรียมการสอบเทียบ
        # Display calibration preparation message
        display.clear()
        display.draw_text(70, 70, f"Prepare pH {buffer_pH:.2f}", font, color565(255, 255, 255))
        display.draw_text(40, 140, "Press Button_1 to start", font, color565(0, 255, 0))

        print(f"\nแช่หัววัดในบัฟเฟอร์ pH {buffer_pH:.2f}")
        print(f"Immerse probe in pH {buffer_pH:.2f} buffer")
        print("กดปุ่ม 1 เมื่อพร้อม (Press Button 1 when ready)")

        # รอการกดปุ่ม (Wait for button press)
        while button1.value() == 1:
            sleep_ms(50)
        while button1.value() == 0:
            sleep_ms(50)

        # แสดงการนับถอยหลัง (Display countdown)
        countdown_time = 3  # วินาที (seconds)
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

        # อ่านแรงดันไฟฟ้า (Read voltage)
        voltage_mv = read_voltage_mv()
        calibrated_voltages[i] = voltage_mv

        # อ่านอุณหภูมิ (Read temperature)
        temperature = read_temperature()
        if temperature is not None:
            temperatures[i] = temperature
        else:
            temperatures[i] = 25.0  # ค่าเริ่มต้น (Default value)

        # แสดงผลลัพธ์ (Display results)
        display.clear()
        display.draw_text(50, 50, f"pH {buffer_pH:.2f} Measured!", font, color565(0, 255, 0))
        display.draw_text(50, 100, f"Voltage: {voltage_mv:.1f} mV", font, color565(255, 193, 34))
        display.draw_text(50, 150, f"Temp: {temperatures[i]:.1f} C", font, color565(0, 191, 255))

        print(f"pH {buffer_pH:.2f}: แรงดัน = {voltage_mv:.1f} mV, อุณหภูมิ = {temperatures[i]:.2f} C")

        sleep_ms(3000)

    # แสดงหน้าสรุป (Display summary)
    display.clear()
    display.draw_text(55, 30, "Calibration Complete!", font, color565(0, 255, 0))

    for i, buffer_pH in enumerate(buffer_pH_values):
        y_offset = 70 + i * 40
        display.draw_text(20, y_offset, f"pH {buffer_pH:.1f}:", font, color565(255, 255, 255))
        display.draw_text(100, y_offset, f"{calibrated_voltages[i]:.1f} mV", font, color565(255, 193, 34))
        display.draw_text(230, y_offset, f"{temperatures[i]:.1f} C", font, color565(0, 191, 255))

    print("\n" + "=" * 50)
    print("การสอบเทียบเสร็จสิ้น (Calibration Complete)")
    print("=" * 50)
    print("\nผลลัพธ์ (Results):")
    for i, buffer_pH in enumerate(buffer_pH_values):
        print(f"  pH {buffer_pH:.2f}: {calibrated_voltages[i]:.1f} mV @ {temperatures[i]:.1f}°C")

    print("\nสามารถนำค่าเหล่านี้ไปใช้คำนวณสมการ calibration")
    print("Use these values to calculate calibration equation")

# ==============================================================================
# โปรแกรมหลัก (Main program)
# ==============================================================================
try:
    calibrate_pH()

    # รอจนกว่าจะกด Ctrl+C
    print("\nกด Ctrl+C เพื่อออก (Press Ctrl+C to exit)")
    while True:
        sleep_ms(100)

except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")

finally:
    # ทำความสะอาด (Cleanup)
    display.clear()
    print("ปิดจอแล้ว (Display cleared)")

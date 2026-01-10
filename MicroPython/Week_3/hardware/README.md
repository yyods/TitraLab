# Hardware Layer (Layer 1)
# ชั้น Hardware Abstraction Layer

---

## ภาพรวม (Overview)

โฟลเดอร์ `hardware/` คือชั้นต่ำสุดของสถาปัตยกรรม TitraLab ทำหน้าที่ **ห่อหุ้ม (encapsulate)** การเข้าถึง hardware ทั้งหมด ให้ชั้นที่สูงกว่าไม่ต้องรู้รายละเอียดของ GPIO, ADC, PWM, SPI โดยตรง

The `hardware/` folder is the lowest layer of the TitraLab architecture. It **encapsulates** all hardware access, so higher layers don't need to know the details of GPIO, ADC, PWM, or SPI directly.

### หลักการสำคัญ (Key Principles)

1. **Abstraction/การห่อหุ้ม**: ซ่อนรายละเอียดการเข้าถึง hardware
2. **Single Responsibility/หน้าที่เดียว**: แต่ละคลาสควบคุม hardware ชิ้นเดียว
3. **Consistent Interface/Interface สอดคล้อง**: ทุกคลาสมี `init()` และ `deinit()`

---

## โครงสร้างไฟล์ (File Structure)

```
hardware/
├── __init__.py       # Package initialization, HardwareHub class
├── pump.py           # คลาสควบคุมปั๊ม (Pump control)
├── ph_sensor.py      # คลาสเซ็นเซอร์ pH (pH sensor)
├── temp_sensor.py    # คลาสเซ็นเซอร์อุณหภูมิ (Temperature sensor)
├── display.py        # คลาสจอ TFT ILI9341 (TFT display)
├── buttons.py        # คลาสจัดการปุ่มกด (Button management)
├── buzzer.py         # คลาส Buzzer (Buzzer control)
├── leds.py           # คลาสจัดการ LED (LED management)
└── sd_card.py        # คลาส SD Card (SD card management)
```

---

## คำอธิบายแต่ละไฟล์ (File Descriptions)

### pump.py - คลาสควบคุมปั๊ม (Pump Control Class)

**GPIO**: 21 (PWM Output)

**หน้าที่**: ควบคุมปั๊มเพอริสตาลติกสำหรับหยดสารไทแทรนต์ (titrant)

**ความเชื่อมโยงกับเคมี**: ปั๊มหยดสารไทแทรนต์ลงในสารละลายตัวอย่าง โดยควบคุมอัตราการไหลด้วย PWM duty cycle

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.pump import Pump

pump = Pump()
pump.start(duty_percent=100)    # เริ่มปั๊มที่ 100%
pump.set_duty(50)               # ลดเป็น 50% ใกล้จุดสมมูล
result = pump.stop()            # หยุดและรับข้อมูลเวลา/ปริมาตร
pump.run_for_volume(2.0)        # สูบ 2 mL แล้วหยุดอัตโนมัติ
pump.purge(duration_ms=3000)    # ล้างท่อ 3 วินาที
pump.deinit()                   # คืนทรัพยากร PWM
```

**Methods สำคัญ**:
| Method | คำอธิบาย |
|--------|----------|
| `start(duty_percent)` | เริ่มปั๊มที่ความเร็วที่กำหนด |
| `stop()` | หยุดปั๊ม คืนค่าเวลาและปริมาตร |
| `set_duty(percent)` | ปรับ duty cycle ขณะทำงาน |
| `run_for_volume(mL)` | สูบปริมาตรที่กำหนดแล้วหยุด |
| `purge(duration_ms)` | ล้างท่อเป็นเวลาที่กำหนด |
| `deinit()` | คืนทรัพยากร PWM |

---

### ph_sensor.py - คลาสเซ็นเซอร์ pH (pH Sensor Class)

**GPIO**: 25 (ADC Input)

**หน้าที่**: อ่านค่าแรงดันจากหัววัด pH และแปลงเป็นค่า pH

**ความเชื่อมโยงกับเคมี**: ใช้สมการ Nernst ในการแปลงแรงดันเป็นค่า pH

```
สมการ (Equation): pH = slope * voltage + intercept
โดย slope และ intercept ได้จากการสอบเทียบ (calibration)
```

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.ph_sensor import PHSensor

ph_sensor = PHSensor()
voltage, ph = ph_sensor.read()          # อ่านค่าแรงดันและ pH
voltage = ph_sensor.read_voltage()      # อ่านเฉพาะแรงดัน
ph_sensor.set_calibration(slope, intercept)  # ตั้งค่าสอบเทียบ
```

**Methods สำคัญ**:
| Method | คำอธิบาย |
|--------|----------|
| `read()` | คืนค่า (voltage, pH) |
| `read_voltage()` | อ่านค่าแรงดัน mV |
| `read_ph()` | คำนวณค่า pH จากแรงดัน |
| `set_calibration(slope, intercept)` | ตั้งค่าสมการสอบเทียบ |

---

### temp_sensor.py - คลาสเซ็นเซอร์อุณหภูมิ (Temperature Sensor Class)

**GPIO**: 16 (OneWire)

**หน้าที่**: อ่านอุณหภูมิจาก DS18B20

**ความเชื่อมโยงกับเคมี**: อุณหภูมิส่งผลต่อ slope ของสมการ Nernst (59.16 mV/pH ที่ 25 C)

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.temp_sensor import TemperatureSensor

temp_sensor = TemperatureSensor()
temp_c = temp_sensor.read()             # อ่านอุณหภูมิ (Celsius)
temp_k = temp_sensor.read_kelvin()      # อ่านอุณหภูมิ (Kelvin)
available = temp_sensor.is_available    # ตรวจสอบว่าเซ็นเซอร์พร้อมใช้งาน
```

---

### display.py - คลาสจอ TFT ILI9341 (TFT Display Class)

**GPIO**: SPI Bus 1 (SCK=14, MOSI=13, DC=27, CS=15, RST=0)

**หน้าที่**: แสดงข้อมูลบนจอ TFT 320x240 pixels

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.display import Display, Colors

display = Display()
display.clear()                         # ล้างจอ
display.draw_header("Title")            # วาดหัวข้อ
display.draw_text(10, 50, "pH: 7.00", Colors.WHITE)
display.show_menu(["Item 1", "Item 2"], selected=0)
```

---

### buttons.py - คลาสจัดการปุ่มกด (Button Management Class)

**GPIO**: 34 (Select), 35 (Up), 39 (Down) - Input-only pins

**หน้าที่**: อ่านสถานะปุ่มกดพร้อม debounce

**หมายเหตุ**: GPIO 34, 35, 39 เป็น input-only ไม่มี internal pull-up/down ต้องใช้ external pull-down resistor

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.buttons import ButtonManager

buttons = ButtonManager()
if buttons.is_pressed('select'):        # ตรวจสอบปุ่ม select
    print("Select pressed!")
if buttons.is_long_pressed('down', 3000):  # กดค้าง 3 วินาที
    print("Long press detected!")
```

---

### buzzer.py - คลาส Buzzer (Buzzer Control Class)

**GPIO**: 22 (PWM Output)

**หน้าที่**: สร้างเสียงเตือนด้วย PWM

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.buzzer import Buzzer

buzzer = Buzzer()
buzzer.beep()                           # บี๊ปสั้น
buzzer.beep(frequency=2000, duration_ms=500)  # บี๊ปยาว
buzzer.beep_beep()                      # บี๊ปสองครั้ง
buzzer.deinit()                         # คืนทรัพยากร PWM
```

---

### leds.py - คลาสจัดการ LED (LED Management Class)

**GPIO**: 2 (Red), 4 (Green)

**หน้าที่**: ควบคุม LED แสดงสถานะ

**ความเชื่อมโยงกับเคมี**:
- LED สีเขียว = ระบบกำลังทำงาน (System running)
- LED สีแดง = ถึงจุดสมมูล หรือเกิดข้อผิดพลาด (Equivalence point / Error)

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.leds import LEDManager

leds = LEDManager()
leds.green.on()                         # เปิด LED เขียว
leds.red.blink(times=3)                 # กระพริบ LED แดง 3 ครั้ง
leds.all_off()                          # ปิด LED ทั้งหมด
```

---

### sd_card.py - คลาส SD Card (SD Card Management Class)

**GPIO**: SoftSPI (MISO=19, MOSI=23, SCK=18, CS=5)

**หน้าที่**: อ่าน/เขียนไฟล์บน SD Card

**ความเชื่อมโยงกับเคมี**: บันทึกข้อมูลการไทเทรต (Volume, pH, Temperature) ลงไฟล์ CSV

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware.sd_card import SDCardManager

sd = SDCardManager()
if sd.init():                           # Mount SD Card
    sd.write_file('/sd/data.csv', 'Volume,pH\n')
    content = sd.read_file('/sd/data.csv')
    sd.append_file('/sd/data.csv', '1.0,7.02\n')
sd.deinit()                             # Unmount
```

---

## HardwareHub - ศูนย์รวม Hardware

`HardwareHub` คือคลาสที่รวม hardware objects ทั้งหมดเข้าด้วยกัน ทำให้ง่ายต่อการ initialize และ cleanup

```python
# ตัวอย่างการใช้งาน (Usage Example)
from hardware import HardwareHub

# วิธีที่ 1: ใช้งานโดยตรง
hw = HardwareHub()
hw.pump.start(100)
hw.buzzer.beep()
hw.deinit()

# วิธีที่ 2: ใช้ with statement (แนะนำ)
with HardwareHub() as hw:
    hw.pump.start(100)
    hw.buzzer.beep()
# hardware ถูก deinit อัตโนมัติ
```

---

## ตารางสรุป GPIO (GPIO Summary Table)

| คลาส | GPIO | ประเภท | Protocol |
|------|------|--------|----------|
| Pump | 21 | Output | PWM |
| PHSensor | 25 | Input | ADC |
| TemperatureSensor | 16 | Input | OneWire |
| Buzzer | 22 | Output | PWM |
| LED (Red) | 2 | Output | Digital |
| LED (Green) | 4 | Output | Digital |
| Button (Select) | 34 | Input-only | Digital |
| Button (Up) | 35 | Input-only | Digital |
| Button (Down) | 39 | Input-only | Digital |
| TFT Display | 14,13,27,15,0 | Output | SPI Bus 1 |
| SD Card | 19,23,18,5 | I/O | SoftSPI |

---

## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

หลังจากศึกษาโฟลเดอร์นี้ นักศึกษาจะสามารถ:

1. **เข้าใจ Hardware Abstraction Layer (HAL)**: การห่อหุ้ม hardware เพื่อซ่อนความซับซ้อน
2. **ออกแบบ Class สำหรับ Hardware**: กำหนด interface ที่ชัดเจน (init, deinit, methods)
3. **จัดการ Resources อย่างถูกต้อง**: เรียก deinit() เพื่อคืนทรัพยากร PWM/SPI
4. **ใช้ Dependency Injection**: ส่ง hardware objects เข้าไปในคลาสอื่น

---

## ลำดับการศึกษาแนะนำ (Recommended Study Order)

1. `leds.py` - เริ่มจากง่ายที่สุด (Digital Output)
2. `buttons.py` - Digital Input พร้อม debounce
3. `buzzer.py` - PWM Output อย่างง่าย
4. `pump.py` - PWM Output ที่ซับซ้อนกว่า
5. `ph_sensor.py` - ADC Input พร้อม calibration
6. `temp_sensor.py` - OneWire Protocol
7. `display.py` - SPI Communication
8. `sd_card.py` - File I/O
9. `__init__.py` - HardwareHub pattern

---

*TitraLab Week 3 - Hardware Abstraction Layer*

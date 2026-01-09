# Week 1: Introduction to OOP / สัปดาห์ที่ 1: บทนำสู่ OOP

## Overview / ภาพรวม

**Duration / ระยะเวลา:** 3 hours / 3 ชั่วโมง

เรียนรู้การเขียนโปรแกรมเชิงวัตถุ (Object-Oriented Programming/OOP) ผ่านการควบคุมอุปกรณ์ในห้องปฏิบัติการ ได้แก่ LED, Button, Temperature Sensor และ TFT Display

Learn Object-Oriented Programming (OOP) through controlling laboratory equipment: LED, Button, Temperature Sensor, and TFT Display.

---

## Learning Objectives / วัตถุประสงค์การเรียนรู้

1. **Understand Class vs Object** - เข้าใจความแตกต่างระหว่าง Class (พิมพ์เขียว) และ Object (สิ่งที่สร้างจากพิมพ์เขียว)
2. **Write simple classes** - เขียน class ที่มี `__init__` และ methods ได้
3. **Control LED with OOP** - ควบคุม LED ด้วย class (on, off, toggle, blink)
4. **Handle Button input** - อ่านปุ่มกดพร้อม debounce
5. **Read temperature sensor** - อ่านค่าอุณหภูมิจาก DS18B20 ในหลายหน่วย (C, K)
6. **Display data on TFT** - แสดงข้อมูลบนจอ TFT ILI9341

---

## 3-Hour Teaching Schedule / ตารางเรียน 3 ชั่วโมง

| Time / เวลา | Topic / หัวข้อ | File / ไฟล์ |
|-------------|----------------|-------------|
| 0:00-0:15 | Setup & Introduction | - |
| 0:15-0:40 | OOP Concepts (Class, Object, `__init__`, self) | `00_OOP_Basics/00_intro_oop.py` |
| 0:40-0:50 | **Break / พัก** | - |
| 0:50-1:15 | LED Class | `01_Blink/05_led_class.py` |
| 1:15-1:40 | Button Class | `02_Button/05_button_class.py` |
| 1:40-1:50 | **Break / พัก** | - |
| 1:50-2:10 | Temperature Sensor (DS18B20) | `03_DS18B20/02_temp_sensor_class.py` |
| 2:10-2:30 | TFT Display Basics | `05_TFT/01_test_display.py` |
| 2:30-2:50 | Combined Example | `00_OOP_Basics/01_combined_example.py` |
| 2:50-3:00 | Summary & Q/A | - |

---

## Folder Structure / โครงสร้างโฟลเดอร์

```
Week_1/
├── 00_OOP_Basics/          # Core OOP teaching files
│   ├── 00_intro_oop.py     # OOP introduction (Beaker class example)
│   ├── 01_combined_example.py  # Lab Alert System
│   └── exercises/          # Practice exercises with solutions
├── 01_Blink/               # LED control examples
│   └── 05_led_class.py     # LED class
├── 02_Button/              # Button input examples
│   └── 05_button_class.py  # Button class with debounce
├── 03_DS18B20/             # Temperature sensor
│   └── 02_temp_sensor_class.py  # TemperatureSensor class
├── 05_TFT/                 # TFT Display
│   ├── 01_test_display.py  # Display basics
│   └── ili9341.py, xglcd_font.py  # Libraries
├── 06_Buzzer/              # Audio feedback
│   └── 02_buzzer_class.py  # Buzzer class
└── pins.py                 # GPIO pin definitions
```

---

## Hardware GPIO / ขา GPIO

| Component / อุปกรณ์ | GPIO | Notes / หมายเหตุ |
|---------------------|------|------------------|
| **LEDs** | | |
| LED Red / แดง | 2 | Output - Status indicator |
| LED Green / เขียว | 4 | Output - Status indicator |
| **Buttons** | | |
| Button 1 | 34 | Input-only, external pull-down |
| Button 2 | 35 | Input-only, external pull-down |
| Button 3 | 39 | Input-only, external pull-down |
| **Sensors** | | |
| DS18B20 Temp | 16 | OneWire protocol |
| **TFT Display (SPI)** | | |
| TFT SCK | 14 | SPI Clock |
| TFT MOSI | 13 | SPI Data |
| TFT DC | 27 | Data/Command |
| TFT CS | 15 | Chip Select |
| TFT RST | 0 | Reset |
| **Others** | | |
| Buzzer | 26 | PWM output |

---

## Quick OOP Reference / อ้างอิง OOP ด่วน

### Class Definition / นิยาม Class

```python
class ClassName:
    """Class = พิมพ์เขียว (Blueprint)"""

    def __init__(self, parameter):
        """Constructor - ทำงานอัตโนมัติเมื่อสร้าง object"""
        self.attribute = parameter  # Instance variable

    def method_name(self):
        """Method = ฟังก์ชันใน class"""
        return self.attribute
```

### Understanding `self` / ทำความเข้าใจ self

**`self`** = ตัวอ้างอิงถึง object ปัจจุบัน (reference to current object)

- `self.pin_number` หมายถึง `pin_number` ของ object นี้
- เมื่อมี LED 2 ดวง แต่ละดวงมี `self.pin_number` ของตัวเอง

### Creating & Using Objects / สร้างและใช้งาน Object

```python
# Class = พิมพ์เขียว, Object = สิ่งที่สร้างจากพิมพ์เขียว
led_red = LED(2, "Red")      # Object 1
led_green = LED(4, "Green")  # Object 2

led_red.on()    # เรียก method ของ object
led_green.off()
```

### LED Class Example / ตัวอย่าง LED Class

```python
from machine import Pin

class LED:
    def __init__(self, pin_number, name="LED"):
        self.pin_number = pin_number
        self.name = name
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)

    def on(self):
        self._pin.value(1)

    def off(self):
        self._pin.value(0)

    def toggle(self):
        if self._pin.value():
            self.off()
        else:
            self.on()
```

### Button Class Example / ตัวอย่าง Button Class

```python
from machine import Pin
import time

class Button:
    def __init__(self, pin_number, name="Button"):
        self.pin_number = pin_number
        self._pin = Pin(pin_number, Pin.IN)
        self._last_press = 0

    def is_active(self):
        return self._pin.value() == 1

    def is_pressed(self, debounce_ms=200):
        if self.is_active():
            if time.ticks_diff(time.ticks_ms(), self._last_press) > debounce_ms:
                self._last_press = time.ticks_ms()
                return True
        return False
```

### Temperature Sensor - Chemistry Connection / เชื่อมโยงเคมี

```python
class TemperatureSensor:
    R_JOULES = 8.314   # J/(mol*K)
    FARADAY = 96485    # C/mol

    def read_kelvin(self):
        """สำหรับสมการ Nernst: E = E0 - (RT/nF)ln(Q)"""
        celsius = self.read_celsius()
        return celsius + 273.15

    def get_nernst_factor(self, n=1):
        """คำนวณ RT/nF ที่อุณหภูมิปัจจุบัน"""
        T = self.read_kelvin()
        return (2.303 * self.R_JOULES * T) / (n * self.FARADAY)
```

---

## Chemistry Connection / เชื่อมโยงกับเคมี

| Programming Concept | Chemistry Application / การใช้งานทางเคมี |
|---------------------|------------------------------------------|
| Class LED | แสดงสถานะการไทเทรต (เขียว=running, แดง=endpoint) |
| Class Button | ควบคุมการเริ่ม/หยุดหยดสาร |
| Class TemperatureSensor | ชดเชยอุณหภูมิในสมการ Nernst: E = E0 - (RT/nF)ln(Q) |
| TFT Display | แสดง pH, อุณหภูมิ, titration curve |

---

## Self-Study Materials / สื่อศึกษาเพิ่มเติม

**Basic Examples (Procedural style):**
- `01_Blink/01_basic.py` - LED on/off basics
- `02_Button/01_basic.py` - Button reading basics
- `03_DS18B20/01_readTemp.py` - Temperature reading

**OOP Examples:**
- `01_Blink/06_comparing_styles.py` - Procedural vs OOP comparison
- `06_Buzzer/02_buzzer_class.py` - Buzzer class

**Practice Exercises (in `00_OOP_Basics/exercises/`):**
- `ex01_status_led` - Create StatusLED class
- `ex02_potentiometer` - Create ADC sensor class
- `ex03_temp_sensor` - Temperature display exercise

---

## Connection to Week 2 / เชื่อมต่อสัปดาห์ที่ 2

ในสัปดาห์ที่ 2 จะเรียนรู้ **Inheritance (การสืบทอด)** - การสร้าง class ใหม่จาก class ที่มีอยู่ เช่น สร้าง `StatusLED` ที่สืบทอดจาก `LED` และเพิ่มความสามารถในการกระพริบตามสถานะการไทเทรต นอกจากนี้จะเรียน **Composition** - การรวม objects หลายตัวเป็นระบบเดียว เช่น `TitrationSystem` ที่ประกอบด้วย PHSensor, Pump, Display

Week 2 covers **Inheritance** (creating new classes from existing ones) and **Composition** (combining multiple objects into one system).

---

## Quick Start / เริ่มต้นเร็ว

```python
# 1. Import
from machine import Pin
import time

# 2. Define Class
class LED:
    def __init__(self, pin):
        self._pin = Pin(pin, Pin.OUT)
    def on(self):
        self._pin.value(1)
    def off(self):
        self._pin.value(0)

# 3. Create Object
led = LED(2)

# 4. Use Object
led.on()
time.sleep(1)
led.off()
```

---

*TitraLab - 2302311 Instrumental Analysis Laboratory*
*Department of Chemistry, Chulalongkorn University*

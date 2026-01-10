# TitraLab Week 3: Object-Oriented Programming (OOP)
# TitraLab สัปดาห์ที่ 3: การเขียนโปรแกรมเชิงวัตถุ

---

## สารบัญ (Table of Contents)

1. [เริ่มต้นที่นี่ (Quick Start)](#เริ่มต้นที่นี่-quick-start)
2. [สถาปัตยกรรมระบบ (System Architecture)](#สถาปัตยกรรมระบบ-system-architecture)
3. [ความรู้พื้นฐานจาก Week 1-2 (Prerequisites from Week 1-2)](#ความรู้พื้นฐานจาก-week-1-2-prerequisites-from-week-1-2)
4. [วัตถุประสงค์ (Objectives)](#วัตถุประสงค์-objectives)
5. [ความรู้พื้นฐาน (Prerequisites)](#ความรู้พื้นฐาน-prerequisites)
6. [แนวคิดหลัก (Key Concepts)](#แนวคิดหลัก-key-concepts)
7. [โครงสร้างโฟลเดอร์ (Directory Structure)](#โครงสร้างโฟลเดอร์-directory-structure)
8. [การกำหนดขา GPIO (Hardware Configuration)](#การกำหนดขา-gpio-hardware-configuration)
9. [โหมดการทำงาน 6 โหมด (The 6 Operating Modes)](#โหมดการทำงาน-6-โหมด-the-6-operating-modes)
10. [แผนภาพคลาส (Class Diagram)](#แผนภาพคลาส-class-diagram)
11. [คำอธิบายไฟล์สำคัญ (File Descriptions)](#คำอธิบายไฟล์สำคัญ-file-descriptions)
12. [คู่มือเริ่มต้นใช้งาน (Quick Start Guide)](#คู่มือเริ่มต้นใช้งาน-quick-start-guide)
13. [การแก้ไขปัญหา (Troubleshooting)](#การแก้ไขปัญหา-troubleshooting)
14. [โค้ดตัวอย่าง (Example Code)](#โค้ดตัวอย่าง-example-code)
15. [อ้างอิง (References)](#อ้างอิง-references)

---

## เริ่มต้นที่นี่ (Quick Start)

> **สำหรับนักศึกษาที่ต้องการเริ่มต้นเร็ว** (For students who want to start quickly)

### ขั้นตอนที่ 1: ตรวจสอบความพร้อม (Check Prerequisites)

ก่อนเริ่ม Week 3 ตรวจสอบว่าคุณมีความรู้เหล่านี้จาก Week 1-2:

| หัวข้อ | ที่มา | ตรวจสอบตัวเอง |
|--------|-------|---------------|
| ควบคุม LED ด้วย GPIO | Week 1 | `led.on()`, `led.off()` ทำงานได้ |
| อ่านค่า ADC จากเซ็นเซอร์ | Week 1 | เข้าใจ `adc.read()` ค่า 0-4095 |
| ควบคุม PWM | Week 1 | เข้าใจ duty cycle 0-1023 |
| อ่านค่า pH และ calibration | Week 2 | สร้างสมการ `pH = slope * mV + intercept` |
| ควบคุมปั๊มและ flow rate | Week 2 | คำนวณ `flow_rate (mL/s)` |
| OOP พื้นฐาน (Class, Object) | Week 1-2 | สร้าง class และ object ได้ |

### ขั้นตอนที่ 2: อัปโหลดไฟล์ทั้งหมด (Upload All Files)

```bash
# ใช้ Thonny IDE อัปโหลดโฟลเดอร์ Week_3 ทั้งหมดไปยัง ESP32
# Upload entire Week_3 folder to ESP32 using Thonny IDE
```

### ขั้นตอนที่ 3: รันโปรแกรม (Run the Program)

```python
# ใน Thonny หรือ REPL
>>> import main
>>> main.main()
```

### ขั้นตอนที่ 4: ใช้งานเมนู (Use the Menu)

```
+----------------------------------+
|          TitraLab Menu           |
+----------------------------------+
| > 1. Calibrate pH Sensor         |
|   2. pH Sensor Test              |
|   3. Calibrate Flow Rate         |
|   4. Flow Rate Test              |
|   5. Purge                       |
|   6. Full Auto Titration         |
+----------------------------------+
|  [UP/DOWN] Navigate  [SEL] Enter |
|  Hold DOWN 3s to exit            |
+----------------------------------+
```

### เส้นทางการเรียนรู้ (Learning Path)

```
1. เริ่มจาก main.py         → ดูภาพรวมการทำงาน
2. ศึกษา config.py          → เข้าใจการตั้งค่า GPIO
3. ศึกษา hardware/          → เรียนรู้ Hardware Abstraction Layer
4. ศึกษา core/              → เข้าใจ Logic และ Math
5. ศึกษา modes/             → ดูการทำงานแต่ละโหมด
6. ศึกษา ui/                → เรียนรู้ State Machine
```

> **ดูรายละเอียดเพิ่มเติม**: อ่าน [LEARNING_PATH.md](LEARNING_PATH.md) สำหรับคู่มือการเรียนรู้ทีละขั้นตอน

---

## สถาปัตยกรรมระบบ (System Architecture)

Week 3 ใช้สถาปัตยกรรมแบบ **4 ชั้น (4-Layer Architecture)** เพื่อจัดระเบียบโค้ดและทำให้ง่ายต่อการบำรุงรักษา

### แผนภาพสถาปัตยกรรม (Architecture Diagram)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MAIN APPLICATION                                 │
│                           main.py                                        │
│                     (Entry Point/จุดเริ่มต้น)                            │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: USER INTERFACE (UI)                                ui/        │
│  ┌─────────────────────┐  ┌─────────────────────────────────────────┐  │
│  │    MenuSystem       │  │           State Machine                  │  │
│  │  menu.py            │  │  MAIN_MENU → MODE_RUNNING → RESULT      │  │
│  └─────────────────────┘  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         screens.py                               │   │
│  │     BaseScreen, MainMenuScreen, CalibrationScreen, etc.          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: OPERATING MODES                                   modes/      │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      BaseMode (Abstract)                          │  │
│  │              on_enter() → update() → on_exit()                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│         │           │           │           │           │              │
│         ▼           ▼           ▼           ▼           ▼              │
│  ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐         │
│  │Calibrate ││ Test pH  ││Calibrate ││  Purge   ││Titration │         │
│  │   pH     ││          ││  Flow    ││          ││          │         │
│  │ Mode 1   ││ Mode 2   ││ Mode 3-4 ││ Mode 5   ││ Mode 6   │         │
│  └──────────┘└──────────┘└──────────┘└──────────┘└──────────┘         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: CORE LOGIC                                        core/       │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │  Calibrator   │ │  math_utils   │ │ DataManager   │ │ Titration  │  │
│  │               │ │               │ │               │ │ Controller │  │
│  │ - pH calibr.  │ │ - Linear Reg. │ │ - Save/Load   │ │ - Auto     │  │
│  │ - Flow calibr.│ │ - Statistics  │ │ - File I/O    │ │ - Detect   │  │
│  └───────────────┘ └───────────────┘ └───────────────┘ └────────────┘  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: HARDWARE ABSTRACTION                              hardware/   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐ │
│  │  Pump  │ │pH Sensor│ │Temp    │ │Display │ │Buttons │ │   Buzzer   │ │
│  │        │ │        │ │Sensor  │ │        │ │        │ │            │ │
│  │ GPIO21 │ │ GPIO25 │ │ GPIO16 │ │  SPI1  │ │ 34,35, │ │   GPIO22   │ │
│  │  PWM   │ │  ADC   │ │OneWire │ │ILI9341 │ │   39   │ │    PWM     │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────────┘ │
│  ┌────────┐ ┌─────────────────────────────────────────────────────────┐ │
│  │  LEDs  │ │                        SD Card                          │ │
│  │GPIO2,4 │ │                    GPIO 5,18,19,23                      │ │
│  └────────┘ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          ESP32 Hardware                                  │
│                    (Physical TitraLab Board)                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### คำอธิบายแต่ละชั้น (Layer Descriptions)

| ชั้น (Layer) | โฟลเดอร์ | หน้าที่ | ไฟล์สำคัญ |
|:------------:|----------|---------|-----------|
| **Layer 4** | `ui/` | จัดการส่วนติดต่อผู้ใช้ และ State Machine | `menu.py`, `screens.py` |
| **Layer 3** | `modes/` | กำหนดพฤติกรรมของแต่ละโหมดการทำงาน | `base_mode.py`, `mode_*.py` |
| **Layer 2** | `core/` | Logic ทางคณิตศาสตร์ และการจัดการข้อมูล | `calibrator.py`, `math_utils.py` |
| **Layer 1** | `hardware/` | ห่อหุ้มการเข้าถึง Hardware ทั้งหมด | `pump.py`, `ph_sensor.py`, etc. |

### ข้อดีของสถาปัตยกรรมนี้ (Benefits of This Architecture)

1. **Separation of Concerns/การแยกความรับผิดชอบ**: แต่ละชั้นทำหน้าที่เฉพาะทาง
2. **Reusability/ใช้ซ้ำได้**: คลาสใน hardware/ สามารถนำไปใช้ในโปรเจกต์อื่น
3. **Testability/ทดสอบได้**: สามารถ mock hardware layer เพื่อทดสอบ logic
4. **Maintainability/บำรุงรักษาง่าย**: แก้ไขชั้นใดชั้นหนึ่งโดยไม่กระทบชั้นอื่น

---

## ความรู้พื้นฐานจาก Week 1-2 (Prerequisites from Week 1-2)

### จาก Week 1: พื้นฐาน Hardware และ OOP

```python
# สิ่งที่นักศึกษาต้องรู้จาก Week 1
# What students should know from Week 1

# 1. ควบคุม LED (GPIO Digital Output)
led = LED(2)
led.on()
led.off()

# 2. อ่านปุ่มกด (GPIO Digital Input)
button = Button(34)
if button.is_pressed():
    print("Button pressed!")

# 3. อ่านค่า ADC (Analog Input)
adc = ADC(Pin(25))
adc.atten(ADC.ATTN_11DB)
raw = adc.read()  # 0-4095
voltage = raw / 4095 * 3.3

# 4. ควบคุม PWM (Analog-like Output)
pwm = PWM(Pin(21), freq=1000)
pwm.duty(512)  # 50% duty cycle
```

### จาก Week 2: การสอบเทียบและการวัด pH

```python
# สิ่งที่นักศึกษาต้องรู้จาก Week 2
# What students should know from Week 2

# 1. สมการสอบเทียบ pH (pH Calibration Equation)
# pH = slope * voltage + intercept
# slope และ intercept ได้จาก Linear Regression

# 2. การคำนวณ Flow Rate
# flow_rate = volume / time  (mL/s)

# 3. Linear Regression
# y = mx + b
# m = covariance(x,y) / variance(x)
# b = mean(y) - m * mean(x)
# R² = 1 - (SS_res / SS_tot)
```

### ความเชื่อมโยงกับ Week 3 (Connection to Week 3)

| Week 1-2 | Week 3 | การพัฒนาต่อ |
|----------|--------|-------------|
| `LED` class พื้นฐาน | `LEDManager` | รวม LED หลายดวงเข้าด้วยกัน |
| `Button` class | `ButtonManager` | จัดการปุ่มหลายปุ่มพร้อม debounce |
| `ADC.read()` | `PHSensor` class | ห่อหุ้มการอ่านค่าพร้อม calibration |
| `PWM.duty()` | `Pump` class | ควบคุมปั๊มพร้อมคำนวณปริมาตร |
| Calibration script | `Calibrator` class | รวม pH และ flow calibration |
| - | `BaseMode` | Abstract class สำหรับทุกโหมด |
| - | `MenuSystem` | State Machine สำหรับนำทาง |

---

## วัตถุประสงค์ (Objectives)

หลังจากเรียนจบบทเรียนนี้ นักศึกษาจะสามารถ:

1. **เข้าใจหลักการ OOP (Object-Oriented Programming/การเขียนโปรแกรมเชิงวัตถุ)**
   - เรียนรู้การสร้าง Class/คลาส และ Object/ออบเจ็กต์
   - เข้าใจ Inheritance/การสืบทอด และ Encapsulation/การห่อหุ้ม
   - ประยุกต์ใช้ Properties และ Methods

2. **ควบคุม Hardware สำหรับระบบไทเทรชัน**
   - อ่านค่า pH ผ่าน ADC (Analog-to-Digital Converter/ตัวแปลงสัญญาณแอนะล็อกเป็นดิจิทัล)
   - ควบคุมปั๊มด้วย PWM (Pulse Width Modulation/การมอดูเลตความกว้างพัลส์)
   - จัดการ State Machine/เครื่องจักรสถานะ สำหรับระบบเมนู

3. **สร้างระบบไทเทรชันอัตโนมัติ (Automatic Titration)**
   - สอบเทียบ pH sensor แบบ 3 จุด (3-point calibration/การสอบเทียบ 3 จุด)
   - ตรวจจับจุดสมมูล (Equivalence Point/จุดสมมูล) ด้วยวิธี Derivative
   - บันทึกข้อมูลการทดลองลง CSV

---

## ความรู้พื้นฐาน (Prerequisites)

### ความรู้ทางเคมี (Chemistry Knowledge)
- หลักการไทเทรตกรด-เบส (Acid-base titration)
- สมการ Nernst และการทำงานของ pH electrode
- ความหมายของจุดสมมูล (Equivalence point) และจุดยุติ (Endpoint)
- การใช้สารละลายบัฟเฟอร์มาตรฐาน (Standard buffer solutions)

### ความรู้การเขียนโปรแกรม (Programming Knowledge)
- Python พื้นฐาน (Variables/ตัวแปร, Functions/ฟังก์ชัน, Loops/ลูป)
- การทำงานกับ GPIO และ ADC บน ESP32 (จากสัปดาห์ที่ 1-2)

---

## แนวคิดหลัก (Key Concepts)

### 1. Object-Oriented Programming (OOP)

OOP เปรียบเสมือนการจัดระเบียบห้องปฏิบัติการเคมี:

| แนวคิด OOP | เปรียบเทียบกับห้องแลป |
|------------|----------------------|
| Class (คลาส) | แบบพิมพ์เขียวของอุปกรณ์ เช่น "pH Meter" |
| Object (ออบเจ็กต์) | อุปกรณ์จริง เช่น pH Meter เครื่องที่ 1 |
| Attribute (คุณสมบัติ) | ค่าที่อ่านได้ เช่น pH = 7.0, voltage = 2.1V |
| Method (เมธอด) | การกระทำ เช่น read_ph(), calibrate() |
| Inheritance (การสืบทอด) | Mode ต่างๆ สืบทอดจาก BaseMode |

### 2. สมการ Nernst สำหรับการวัด pH

```
E = E0 - (2.303 * R * T) / (n * F) * pH
```

**ที่อุณหภูมิ 25 C (298.15 K):**
- R = 8.314 J/(mol*K) - ค่าคงที่แก๊ส (Gas constant)
- F = 96485 C/mol - ค่าคงที่ฟาราเดย์ (Faraday constant)
- n = 1 - จำนวนอิเล็กตรอน
- **Theoretical slope = -59.16 mV/pH unit**

โค้ดคำนวณ slope ทฤษฎี:
```python
def calculate_nernst_slope(temperature_c=25.0):
    """คำนวณ slope ทฤษฎีตามสมการ Nernst"""
    R = 8.314       # Gas constant (J/(mol*K))
    F = 96485       # Faraday constant (C/mol)
    n = 1           # Number of electrons
    T = temperature_c + 273.15  # Convert to Kelvin

    slope = -(2.303 * R * T) / (n * F) * 1000  # mV/pH
    return slope
```

### 3. Linear Regression สำหรับการสอบเทียบ

การสอบเทียบ pH sensor ใช้สมการเส้นตรง:
```
pH = slope * voltage + intercept
```

**การคำนวณ:**
```python
slope = covariance(x, y) / variance(x)
intercept = mean(y) - slope * mean(x)
R_squared = 1 - (SS_residual / SS_total)
```

**เกณฑ์ R-squared:**
- R2 >= 0.99: Excellent (ผ่านเกณฑ์สำหรับการสอบเทียบ pH)
- R2 >= 0.95: Acceptable
- R2 < 0.95: ควรสอบเทียบใหม่

### 4. วิธี Derivative สำหรับหาจุดสมมูล

จุดสมมูล (Equivalence Point) คือจุดที่ **|dpH/dV| มีค่าสูงสุด**

```python
def calculate_derivative(index):
    """คำนวณ dpH/dV ณ จุดที่กำหนด"""
    delta_v = volume[index] - volume[index-1]
    delta_ph = pH[index] - pH[index-1]

    if abs(delta_v) < 0.0001:
        return 0.0

    return delta_ph / delta_v
```

---

## โครงสร้างโฟลเดอร์ (Directory Structure)

```
Week_3/
|
|-- main.py                 # โปรแกรมหลัก (Main entry point)
|-- config.py               # การตั้งค่า GPIO และค่าคงที่ (Configuration)
|
|-- hardware/               # คลาสควบคุม Hardware
|   |-- __init__.py
|   |-- display.py          # จัดการจอ TFT ILI9341
|   |-- buttons.py          # จัดการปุ่มกดพร้อม debounce
|   |-- pump.py             # ควบคุมปั๊มด้วย PWM
|   |-- ph_sensor.py        # อ่านค่า pH จาก ADC
|   |-- temp_sensor.py      # อ่านอุณหภูมิ DS18B20
|   |-- buzzer.py           # ควบคุม Buzzer
|   |-- leds.py             # ควบคุม LED แสดงสถานะ
|   |-- sd_card.py          # จัดการ SD Card
|
|-- core/                   # คลาสตรรกะหลัก (Core Logic)
|   |-- __init__.py
|   |-- calibrator.py       # การสอบเทียบ pH และ flow rate
|   |-- math_utils.py       # Linear Regression, สถิติ
|   |-- data_manager.py     # บันทึก/โหลดข้อมูล
|   |-- titration.py        # ควบคุมการไทเทรชัน
|
|-- ui/                     # User Interface
|   |-- __init__.py
|   |-- menu.py             # ระบบเมนูและ State Machine
|   |-- screens.py          # หน้าจอต่างๆ
|
|-- modes/                  # โหมดการทำงาน
|   |-- __init__.py
|   |-- base_mode.py        # Abstract Base Class สำหรับทุกโหมด
|   |-- mode_calibrate_ph.py    # Mode 1: สอบเทียบ pH
|   |-- mode_test_ph.py         # Mode 2: ทดสอบ pH
|   |-- mode_calibrate_flow.py  # Mode 3: สอบเทียบอัตราการไหล
|   |-- mode_test_flow.py       # Mode 4: ทดสอบอัตราการไหล
|   |-- mode_purge.py           # Mode 5: ล้างท่อ
|   |-- mode_titration.py       # Mode 6: ไทเทรชันอัตโนมัติ
|
|-- async_support/          # การทำงานแบบ Asynchronous (ขั้นสูง)
    |-- __init__.py
    |-- scheduler.py        # Task Scheduler
    |-- async_pump.py       # Async pump control
    |-- async_titration.py  # Async titration
```

---

## การกำหนดขา GPIO (Hardware Configuration)

### แผนผัง GPIO สำหรับ TitraLab ESP32 Board

```
                    +------------------+
                    |    ESP32 Board   |
                    |                  |
    Red LED    <----|  GPIO2           |
    Green LED  <----|  GPIO4           |
                    |                  |
    TFT SCK    <----|  GPIO14          |
    TFT MOSI   <----|  GPIO13          |
    TFT CS     <----|  GPIO15          |
    TFT DC     <----|  GPIO27          |
    TFT RST    <----|  GPIO0           |
                    |                  |
    DS18B20    <----|  GPIO16          |
                    |                  |
    Pump PWM   <----|  GPIO21          |
    Buzzer PWM <----|  GPIO22          |
                    |                  |
    pH Sensor  ---->|  GPIO25 (ADC)    |
                    |                  |
    Button 1   ---->|  GPIO34 (Input)  |  <- Select/Confirm
    Button 2   ---->|  GPIO35 (Input)  |  <- Up/Navigate
    Button 3   ---->|  GPIO39 (Input)  |  <- Down/Back (hold 3s)
                    |                  |
    SD MISO    ---->|  GPIO19          |
    SD MOSI    <----|  GPIO23          |
    SD SCK     <----|  GPIO18          |
    SD CS      <----|  GPIO5           |
                    +------------------+
```

### ตารางสรุปการกำหนดขา GPIO

| อุปกรณ์ | GPIO | ประเภท | หมายเหตุ |
|---------|------|--------|----------|
| **LED** |
| LED สีแดง (Error) | GPIO2 | Output | แสดงข้อผิดพลาด |
| LED สีเขียว (Status) | GPIO4 | Output | แสดงสถานะปกติ |
| **Buttons** |
| Button 1 (Select) | GPIO34 | Input-only | ต้องใช้ external pull-down 10K |
| Button 2 (Up) | GPIO35 | Input-only | ต้องใช้ external pull-down 10K |
| Button 3 (Down/Back) | GPIO39 | Input-only | ต้องใช้ external pull-down 10K |
| **Sensors** |
| pH Sensor | GPIO25 | ADC | อ่านแรงดัน 0-3.3V |
| Temperature DS18B20 | GPIO16 | OneWire | ต้องใช้ pull-up 4.7K |
| **Actuators** |
| Pump | GPIO21 | PWM | ความถี่ 1000 Hz, 10-bit (0-1023) |
| Buzzer | GPIO22 | PWM | สร้างเสียงเตือน |
| **TFT Display (SPI Bus 1)** |
| SCK | GPIO14 | SPI Clock | 40 MHz |
| MOSI | GPIO13 | SPI Data | Master Out Slave In |
| DC | GPIO27 | Digital | Data/Command Select |
| CS | GPIO15 | Digital | Chip Select |
| RST | GPIO0 | Digital | Reset |
| **SD Card (SoftSPI)** |
| SCK | GPIO18 | SPI Clock | 1 MHz |
| MOSI | GPIO23 | SPI Data | Master Out Slave In |
| MISO | GPIO19 | SPI Data | Master In Slave Out |
| CS | GPIO5 | Digital | Chip Select |

### ข้อควรระวังสำคัญ (Important Notes)

**GPIO34, 35, 39 เป็น Input-Only:**
```python
# GPIO เหล่านี้ไม่รองรับ internal pull-up/pull-down
# ต้องใช้ external pull-down resistor (10K ohm)
BUTTON_1 = 34    # Input-only, need external pull-down
BUTTON_2 = 35    # Input-only, need external pull-down
BUTTON_3 = 39    # Input-only, need external pull-down
```

---

## โหมดการทำงาน 6 โหมด (The 6 Operating Modes)

### Mode 1: Calibrate pH Sensor (สอบเทียบเซ็นเซอร์ pH)

**วัตถุประสงค์:** สร้างสมการความสัมพันธ์ระหว่างแรงดันและ pH

**ขั้นตอน:**
1. แช่หัววัดในบัฟเฟอร์ pH 4.00 -> วัดแรงดัน V1
2. แช่หัววัดในบัฟเฟอร์ pH 7.00 -> วัดแรงดัน V2
3. แช่หัววัดในบัฟเฟอร์ pH 10.00 -> วัดแรงดัน V3
4. คำนวณ Linear Regression: `pH = slope * V + intercept`
5. ตรวจสอบ R-squared >= 0.99

```python
# ตัวอย่างการใช้งาน
calibrator = Calibrator()
calibrator.add_ph_point(4.00, 1.500)   # Buffer pH 4
calibrator.add_ph_point(7.00, 2.000)   # Buffer pH 7
calibrator.add_ph_point(10.00, 2.500)  # Buffer pH 10

result = calibrator.calculate_ph_calibration()
# result = {'slope': 6.0, 'intercept': -5.0, 'r_squared': 1.0}
```

---

### Mode 2: Test pH Sensor (ทดสอบเซ็นเซอร์ pH)

**วัตถุประสงค์:** ตรวจสอบการทำงานของหัววัด pH แบบ real-time

**การทำงาน:**
- แสดงค่า pH และแรงดันแบบต่อเนื่อง
- ใช้ตรวจสอบความเสถียรของการอ่านค่า
- ทดสอบก่อนการไทเทรตจริง

```python
# Loop/ลูป สำหรับการอ่านค่าต่อเนื่อง
while True:
    voltage, ph = ph_sensor.read()
    print(f"Voltage: {voltage:.4f} V, pH: {ph:.2f}")
    sleep_ms(1000)  # อ่านทุก 1 วินาที
```

---

### Mode 3: Calibrate Flow Rate (สอบเทียบอัตราการไหล)

**วัตถุประสงค์:** วัดอัตราการไหลที่แท้จริงของปั๊ม

**สูตรการคำนวณ:**
```
flow_rate (mL/s) = volume (mL) / time (s)
```

**ขั้นตอน:**
1. เตรียมภาชนะสำหรับรับของเหลว
2. สูบของเหลวปริมาตรเป้าหมาย (เช่น 5.00 mL)
3. วัดเวลาที่ใช้
4. คำนวณอัตราการไหล

```python
# ตัวอย่าง: สูบ 5 mL ใน 18.05 วินาที
result = calibrator.calibrate_flow_rate(5.0, 18.05)
# flow_rate = 5.0 / 18.05 = 0.2770 mL/s
```

---

### Mode 4: Test Flow Rate (ทดสอบอัตราการไหล)

**วัตถุประสงค์:** ยืนยันความแม่นยำของการสอบเทียบอัตราการไหล

**การทำงาน:**
- สูบปริมาตรที่กำหนด
- วัดปริมาตรจริงที่ได้
- คำนวณเปอร์เซ็นต์ความคลาดเคลื่อน

---

### Mode 5: Purge (ล้างท่อ)

**วัตถุประสงค์:** ไล่อากาศและทำความสะอาดท่อปั๊ม

**การทำงาน:**
- เปิดปั๊ม 100% เป็นเวลาที่กำหนด (default: 3 วินาที)
- ใช้ก่อนการไทเทรตเพื่อให้แน่ใจว่าไม่มีฟองอากาศ

```python
pump.purge(duration_ms=3000, duty_percent=100)
```

---

### Mode 6: Full Auto Titration (ไทเทรชันอัตโนมัติเต็มรูปแบบ)

**วัตถุประสงค์:** ดำเนินการไทเทรตอัตโนมัติพร้อมตรวจจับจุดสมมูล

**เฟสการทำงาน:**

| เฟส | Duty Cycle | เงื่อนไข |
|-----|------------|----------|
| Fast Dosing | 100% | ระยะห่างจาก target pH > 1.5 |
| Slow Dosing | 50% | ระยะห่างจาก target pH < 1.5 |
| Endpoint | หยุด | ระยะห่างจาก target pH < 0.3 |

**การตรวจจับจุดสมมูล:**
```python
# ใช้วิธี derivative: หาจุดที่ |dpH/dV| สูงสุด
for i in range(1, len(data_points)):
    derivative = (pH[i] - pH[i-1]) / (V[i] - V[i-1])
    if abs(derivative) > max_derivative:
        max_derivative = abs(derivative)
        equivalence_point = (V[i], pH[i])
```

**Safety Limits:**
- ปริมาตรสูงสุด: 50 mL
- เวลาสูงสุด: 10 นาที

---

## แผนภาพคลาส (Class Diagram)

```
                           +----------------+
                           |   HardwareHub  |
                           +----------------+
                           | - display      |
                           | - buttons      |
                           | - pump         |
                           | - ph_sensor    |
                           | - temp_sensor  |
                           | - buzzer       |
                           | - leds         |
                           | - sd_card      |
                           +----------------+
                           | + init_all()   |
                           | + deinit_all() |
                           +----------------+
                                   |
          +------------------------+------------------------+
          |                        |                        |
    +----------+            +------------+           +-------------+
    |  Pump    |            | PHSensor   |           | Calibrator  |
    +----------+            +------------+           +-------------+
    | - pin    |            | - pin      |           | - ph_points |
    | - pwm    |            | - adc      |           | - flow_rate |
    | - flow_  |            | - slope    |           +-------------+
    |   rate   |            | - intercept|           | + add_point |
    +----------+            +------------+           | + calculate |
    | + start()|            | + read()   |           | + validate()|
    | + stop() |            | + read_ph()|           +-------------+
    | + purge()|            +------------+
    +----------+

                           +----------------+
                           |   BaseMode     |  <-- Abstract Base Class
                           +----------------+
                           | - display      |
                           | - is_running   |
                           | - _complete    |
                           +----------------+
                           | + on_enter()   |
                           | + update()     |  <-- Must override
                           | + on_exit()    |
                           | + is_complete()|
                           +----------------+
                                   ^
                                   | Inheritance
          +-------------+----------+----------+-------------+
          |             |          |          |             |
    +----------+  +----------+  +----------+  +----------+  +----------+
    | Calibrate|  | Test pH  |  | Calibrate|  | Purge    |  | Titration|
    | pH Mode  |  | Mode     |  | Flow Mode|  | Mode     |  | Mode     |
    +----------+  +----------+  +----------+  +----------+  +----------+

                           +----------------+
                           |  MenuSystem    |
                           +----------------+
                           | - state        |
                           | - modes[]      |
                           | - buttons      |
                           +----------------+
                           | + run()        |
                           | + handle_*()   |
                           +----------------+
                                   |
                           +----------------+
                           |  MenuState     |
                           +----------------+
                           | MAIN_MENU = 0  |
                           | MODE_RUNNING=1 |
                           | RESULT_DISP=2  |
                           +----------------+
```

---

## คำอธิบายไฟล์สำคัญ (File Descriptions)

### Hardware Layer

| ไฟล์ | คำอธิบาย |
|------|----------|
| `pump.py` | ควบคุมปั๊มด้วย PWM: start(), stop(), run_for_volume(), purge() |
| `ph_sensor.py` | อ่านค่า pH จาก ADC: read(), read_ph(), read_voltage() |
| `temp_sensor.py` | อ่านอุณหภูมิ DS18B20 ผ่าน OneWire protocol |
| `display.py` | จัดการจอ TFT ILI9341: clear(), draw_text(), show_menu() |
| `buttons.py` | จัดการปุ่มพร้อม debounce และ long press detection |
| `buzzer.py` | สร้างเสียงเตือนด้วย PWM |

### Core Layer

| ไฟล์ | คำอธิบาย |
|------|----------|
| `calibrator.py` | จัดการการสอบเทียบ pH และ flow rate |
| `math_utils.py` | Linear Regression, mean, std, R-squared |
| `titration.py` | ควบคุมการไทเทรชัน, หาจุดสมมูล, บันทึกข้อมูล |
| `data_manager.py` | บันทึก/โหลดข้อมูลสอบเทียบจากไฟล์ |

### Mode Layer

| ไฟล์ | คำอธิบาย |
|------|----------|
| `base_mode.py` | Abstract Base Class กำหนด lifecycle: on_enter(), update(), on_exit() |
| `mode_calibrate_ph.py` | Mode 1: สอบเทียบ 3 จุดพร้อมตรวจสอบ R-squared |
| `mode_test_ph.py` | Mode 2: แสดงค่า pH real-time |
| `mode_calibrate_flow.py` | Mode 3: วัดอัตราการไหล |
| `mode_test_flow.py` | Mode 4: ทดสอบความแม่นยำ |
| `mode_purge.py` | Mode 5: ล้างท่อ |
| `mode_titration.py` | Mode 6: ไทเทรชันอัตโนมัติ |

---

## คู่มือเริ่มต้นใช้งาน (Quick Start Guide)

### 1. ติดตั้ง MicroPython บน ESP32

```bash
# ดาวน์โหลด MicroPython firmware จาก micropython.org
# ใช้ esptool.py เพื่อ flash firmware

esptool.py --chip esp32 --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-xxx.bin
```

### 2. อัปโหลดไฟล์ไปยัง ESP32

ใช้ Thonny IDE หรือ ampy:

```bash
# อัปโหลดโฟลเดอร์ทั้งหมด
ampy --port COM3 put Week_4_OOP /

# หรืออัปโหลดทีละไฟล์
ampy --port COM3 put main.py
ampy --port COM3 put config.py
ampy --port COM3 mkdir hardware
ampy --port COM3 put hardware/pump.py hardware/pump.py
# ... (ทำซ้ำสำหรับไฟล์อื่นๆ)
```

### 3. รันโปรแกรม

```python
# ใน Thonny หรือ REPL
>>> import main
>>> main.main()

# หรือให้รันอัตโนมัติเมื่อบูต
# เปลี่ยนชื่อ main.py เป็น boot.py
```

### 4. การใช้งานเมนู

```
+----------------------------------+
|          TitraLab Menu           |
+----------------------------------+
| > 1. Calibrate pH Sensor         |
|   2. pH Sensor Test              |
|   3. Calibrate Flow Rate         |
|   4. Flow Rate Test              |
|   5. Purge                       |
|   6. Full Auto Titration         |
+----------------------------------+
|  [UP/DOWN] Navigate  [SEL] Enter |
+----------------------------------+
```

- **Button 2 (UP):** เลื่อนขึ้น
- **Button 3 (DOWN):** เลื่อนลง / กดค้าง 3 วินาที = ออก
- **Button 1 (SELECT):** เลือก/ยืนยัน

---

## การแก้ไขปัญหา (Troubleshooting)

### ปัญหา: ไม่สามารถอ่านค่า pH ได้

**สาเหตุที่เป็นไปได้:**
1. ขา GPIO ไม่ถูกต้อง
2. ADC attenuation ไม่ถูกตั้งค่า
3. หัววัด pH เสียหรือไม่ได้ต่อ

**วิธีแก้:**
```python
# ตรวจสอบการอ่าน ADC โดยตรง
from machine import Pin, ADC

adc = ADC(Pin(25))
adc.atten(ADC.ATTN_11DB)  # สำคัญ! ต้องตั้งค่านี้
raw = adc.read()
voltage = (raw / 4095) * 3.3
print(f"Raw: {raw}, Voltage: {voltage:.4f} V")
```

---

### ปัญหา: ปุ่มกดไม่ทำงาน

**สาเหตุที่เป็นไปได้:**
1. GPIO34, 35, 39 ไม่มี internal pull-up/down
2. ไม่มี external pull-down resistor

**วิธีแก้:**
- ต่อ external pull-down resistor 10K ohm จาก GPIO ไป GND
- ตรวจสอบว่าปุ่มต่อจาก GPIO ไป 3.3V

```python
# ทดสอบการอ่านปุ่ม
from machine import Pin
btn = Pin(34, Pin.IN)
print(f"Button value: {btn.value()}")  # 0 = ไม่กด, 1 = กด
```

---

### ปัญหา: R-squared ต่ำเกินไป (< 0.99)

**สาเหตุที่เป็นไปได้:**
1. สารละลายบัฟเฟอร์หมดอายุหรือปนเปื้อน
2. หัววัด pH เสื่อมสภาพ
3. ล้างหัววัดไม่สะอาดระหว่างเปลี่ยนบัฟเฟอร์
4. อ่านค่าก่อนที่หัววัดจะเสถียร

**วิธีแก้:**
- ใช้บัฟเฟอร์ใหม่
- ล้างหัววัดด้วยน้ำ DI ก่อนเปลี่ยนบัฟเฟอร์
- รอ 30-60 วินาทีให้ค่าเสถียรก่อนบันทึก
- ตรวจสอบประสิทธิภาพหัววัด (ควร > 90%)

---

### ปัญหา: ปั๊มไม่ทำงาน

**สาเหตุที่เป็นไปได้:**
1. PWM ไม่ถูกตั้งค่า
2. Duty cycle เป็น 0
3. แหล่งจ่ายไฟไม่เพียงพอ

**วิธีแก้:**
```python
from machine import Pin, PWM

pwm = PWM(Pin(21), freq=1000)
pwm.duty(1023)  # 100% duty cycle
# ปั๊มควรทำงาน

pwm.duty(0)  # หยุด
```

---

### ปัญหา: SD Card อ่าน/เขียนไม่ได้

**สาเหตุที่เป็นไปได้:**
1. การ์ดไม่ได้ format เป็น FAT32
2. การเชื่อมต่อ SPI ไม่ถูกต้อง
3. การ์ดเสียหาย

**วิธีแก้:**
- Format การ์ดเป็น FAT32
- ตรวจสอบสายเชื่อมต่อ
- ลองการ์ดใหม่

```python
import os
try:
    files = os.listdir('/sd')
    print(f"SD Card OK: {files}")
except:
    print("SD Card not mounted")
```

---

## โค้ดตัวอย่าง (Example Code)

### ตัวอย่าง: อ่านค่า pH อย่างต่อเนื่อง

```python
"""
ตัวอย่างการอ่านค่า pH แบบต่อเนื่อง
Example: Continuous pH reading
"""
from hardware.ph_sensor import PHSensor
from time import sleep_ms

# สร้าง pH sensor object
ph_sensor = PHSensor()

# Loop อ่านค่าทุก 1 วินาที
print("กด Ctrl+C เพื่อหยุด (Press Ctrl+C to stop)")
try:
    while True:
        voltage, ph = ph_sensor.read()
        print(f"Voltage: {voltage:.4f} V | pH: {ph:.2f}")
        sleep_ms(1000)
except KeyboardInterrupt:
    print("หยุดการอ่าน (Reading stopped)")
```

### ตัวอย่าง: สอบเทียบ pH 3 จุด

```python
"""
ตัวอย่างการสอบเทียบ pH 3 จุด
Example: 3-point pH calibration
"""
from core.calibrator import Calibrator
from core.math_utils import LinearRegression

# สร้าง Calibrator
cal = Calibrator()

# เพิ่มจุดสอบเทียบ (ตัวอย่างข้อมูล)
# voltage -> pH
cal.add_ph_point(4.00, 1.500)   # Buffer pH 4.00
cal.add_ph_point(7.00, 2.000)   # Buffer pH 7.00
cal.add_ph_point(10.00, 2.500)  # Buffer pH 10.00

# คำนวณสมการ
result = cal.calculate_ph_calibration()

print(f"สมการ: pH = {result['slope']:.4f} * V + {result['intercept']:.4f}")
print(f"R-squared: {result['r_squared']*100:.2f}%")
print(f"ผ่านเกณฑ์: {'ใช่' if result['is_valid'] else 'ไม่'}")

# บันทึกถ้าผ่านเกณฑ์
if result['is_valid']:
    cal.save_ph_calibration()
    print("บันทึกข้อมูลสอบเทียบแล้ว")
```

### ตัวอย่าง: ควบคุมปั๊มด้วย PWM

```python
"""
ตัวอย่างการควบคุมปั๊มด้วย PWM
Example: Pump control with PWM
"""
from hardware.pump import Pump
from time import sleep_ms

# สร้าง Pump object
pump = Pump()

# เริ่มปั๊มที่ 50% duty cycle
pump.start(duty_percent=50)
print("ปั๊มทำงานที่ 50%")
sleep_ms(2000)

# เปลี่ยนเป็น 100%
pump.set_duty(100)
print("เพิ่มเป็น 100%")
sleep_ms(2000)

# หยุดปั๊ม
result = pump.stop()
print(f"หยุดปั๊ม: เวลา {result['elapsed_time_s']:.2f}s, "
      f"ปริมาตร {result['volume_ml']:.3f} mL")

# สูบปริมาตรที่กำหนด (blocking)
result = pump.run_for_volume(volume_ml=2.0, duty_percent=100)
print(f"สูบ 2 mL เสร็จ: เวลา {result['elapsed_time_s']:.2f}s")

# ทำความสะอาด
pump.deinit()
```

---

## อ้างอิง (References)

### เอกสารทางเคมี
- Skoog, D.A., West, D.M., Holler, F.J., & Crouch, S.R. (2014). *Fundamentals of Analytical Chemistry* (9th ed.). Cengage Learning.
- Harris, D.C. (2015). *Quantitative Chemical Analysis* (9th ed.). W.H. Freeman.

### เอกสาร MicroPython
- [MicroPython Documentation](https://docs.micropython.org/)
- [MicroPython ESP32 Quick Reference](https://docs.micropython.org/en/latest/esp32/quickref.html)

### แหล่งข้อมูลเพิ่มเติม
- [TitraLab GitHub Repository](https://github.com/your-repo/titralab)
- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)

---

## ผู้พัฒนา (Developers)

- Hemmawan Saon
- Nuttakit Deemon
- Saowapak Vchirawongkwin
- Sumrit Wacharasindhu
- Viwat Vchirawongkwin

**รายวิชา:** 2302311 Analytical Chemistry Laboratory
**สถาบัน:** Chulalongkorn University

---

## เวอร์ชัน (Version)

**Version 2.0.0** - OOP Refactored Edition

การเปลี่ยนแปลงหลัก:
- ปรับโครงสร้างเป็น Object-Oriented
- เพิ่ม State Machine สำหรับระบบเมนู
- เพิ่มระบบ Mode ที่ขยายได้ง่าย
- ปรับปรุง Hardware abstraction layer
- เพิ่มการรองรับ Async operations

---

*สร้างเมื่อ: มกราคม 2026*
*อัปเดตล่าสุด: มกราคม 2026*

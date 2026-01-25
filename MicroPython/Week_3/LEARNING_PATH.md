# TitraLab Week 3 - User Manual / คู่มือการใช้งาน

**ระบบไทเทรชันอัตโนมัติ (Automatic Titration System)**

วิชา: Integrated Chemistry Laboratory I (2302311)
ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย

---

## สารบัญ (Table of Contents)

1. [ภาพรวมระบบ (System Overview)](#1-ภาพรวมระบบ-system-overview)
2. [การติดตั้งฮาร์ดแวร์ (Hardware Setup)](#2-การติดตั้งฮาร์ดแวร์-hardware-setup)
3. [การเริ่มต้นใช้งาน (Getting Started)](#3-การเริ่มต้นใช้งาน-getting-started)
4. [โหมดการทำงานทั้ง 6 โหมด (All 6 Modes)](#4-โหมดการทำงานทั้ง-6-โหมด-all-6-modes)
5. [ขั้นตอนการทดลองวันจริง (Lab Day Workflow)](#5-ขั้นตอนการทดลองวันจริง-lab-day-workflow)
6. [การดาวน์โหลดและวิเคราะห์ข้อมูล (Data Download and Analysis)](#6-การดาวน์โหลดและวิเคราะห์ข้อมูล-data-download-and-analysis)
7. [รูปแบบไฟล์ข้อมูล (Data File Formats)](#7-รูปแบบไฟล์ข้อมูล-data-file-formats)
8. [ตารางอ้างอิง GPIO (GPIO Reference)](#8-ตารางอ้างอิง-gpio-gpio-reference)
9. [การแก้ไขปัญหา (Troubleshooting)](#9-การแก้ไขปัญหา-troubleshooting)
10. [ข้อควรระวังและข้อปฏิบัติ (Safety and Best Practices)](#10-ข้อควรระวังและข้อปฏิบัติ-safety-and-best-practices)
11. [โครงสร้างโค้ด (Code Architecture)](#11-โครงสร้างโค้ด-code-architecture)

---

## 1. ภาพรวมระบบ (System Overview)

### ระบบ TitraLab Week 3 คืออะไร?

ระบบ TitraLab Week 3 เป็นโปรแกรม MicroPython สำหรับ ESP32 ที่ทำหน้าที่ควบคุมการไทเทรชัน
กรด-เบส (acid-base titration) แบบอัตโนมัติ ระบบนี้ออกแบบตามหลัก OOP (Object-Oriented
Programming) แบบ modular คือแบ่งโค้ดเป็นส่วนย่อยๆ เพื่อให้ง่ายต่อการเข้าใจและบำรุงรักษา

### ระบบทำงานอย่างไร?

```
ลำดับการทำงาน (Operation Sequence):

  สูบ 0.2 mL → หยุด → รอ 10 วินาที → อ่าน pH → บันทึก CSV → ทำซ้ำ
  (Pump 0.2 mL)  (Stop)  (Wait 10s)    (Read pH)  (Log CSV)    (Repeat)
```

**หลักการทางเคมี (Chemistry Principle):**
- จุดสมมูล (equivalence point) คือจุดที่กรดและเบสทำปฏิกิริยาพอดี
- ที่จุดสมมูล การเปลี่ยนแปลง pH ต่อปริมาตร (dpH/dV) จะมีค่าสูงสุด
- ระบบเติมสารไทแทรนต์ (titrant) ทีละ 0.2 mL คงที่ เหมือน "หยดทีละหยด" แบบสม่ำเสมอ

### อุปกรณ์ในระบบ (System Components)

| อุปกรณ์ | หน้าที่ | การเชื่อมต่อ |
|---------|--------|-------------|
| ESP32 (TitraLab Board) | หน่วยประมวลผลหลัก | - |
| หัววัด pH (pH Probe) | วัดค่า pH ของสารละลาย | ADC pin |
| DS18B20 | วัดอุณหภูมิ | Digital pin |
| ปั๊ม (Peristaltic Pump) | สูบสารไทแทรนต์ | PWM pin |
| จอ TFT ILI9341 | แสดงสถานะและค่า pH | SPI1 (fixed) |
| ปุ่มกด 3 ปุ่ม (Buttons) | เลือกเมนู/ปรับค่า | Input pins |
| Buzzer | แจ้งเตือนเสียง | PWM pin |
| LED (แดง/เขียว) | แสดงสถานะ | Output pins |

---

## 2. การติดตั้งฮาร์ดแวร์ (Hardware Setup)

### 2.1 ขาที่กำหนดตายตัว (Fixed Pins - PCB Hardwired)

ขาเหล่านี้ถูกกำหนดตายตัวบนแผงวงจร (PCB) ไม่สามารถเปลี่ยนได้:

```
จอ TFT Display (SPI Bus 1):
  SCK  = GPIO14    (SPI Clock)
  MOSI = GPIO13    (SPI Data)
  DC   = GPIO27    (Data/Command select)
  CS   = GPIO15    (Chip Select)
  RST  = GPIO0     (Reset)

SD Card (ไม่ใช้งาน - NOT USED):
  MISO = GPIO19
  MOSI = GPIO23
  SCK  = GPIO18
  CS   = GPIO5
```

> **หมายเหตุ**: ระบบนี้ไม่ใช้ SD Card เพราะบอร์ดเชื่อมต่อกับ laptop ตลอดเวลาผ่าน USB
> ไฟล์ CSV จะบันทึกใน ESP32 flash memory แทน แล้วดาวน์โหลดผ่าน Thonny IDE

### 2.2 ขาที่นิสิตเลือกเอง (Student-Assigned Pins via Jumper Wires)

บอร์ด TitraLab มี 2 header แยกกัน:
- **GPIO Header**: ขา GPIO จาก ESP32 โดยตรง
- **DEVICES Header**: สัญญาณของอุปกรณ์ต่อพ่วง (LED, ปุ่ม, เซ็นเซอร์, ปั๊ม, ฯลฯ)

นิสิตใช้ **สายจัมเปอร์ (jumper wires)** เชื่อมต่อระหว่าง GPIO กับ DEVICES ตามความเหมาะสม:

```
GPIO Header                    DEVICES Header
+----------------------------+ +-----------------------------+
| IO26 IO12 IO2  IO4  IO16  | | RED  GREEN  BUTTON_1  ...  |
| IO17 IO21 IO22 IO25 IO33  | | BUZZER  PH_PROBE  RELAY    |
| IO32 IO35* IO34* IO39*    | | CONTROL_1  CONTROL_2       |
| (* = Input Only)           | | DS18B20  POT_1  POT_2      |
+----------------------------+ +-----------------------------+
         |                              |
         +--- สายจัมเปอร์ (jumper wires) ---+
```

### 2.3 ตารางเลือกขา GPIO (Pin Selection Guide)

**สำคัญ**: นิสิตต้องพิจารณาคุณสมบัติของ GPIO ก่อนเลือกต่อสาย
(เปรียบเสมือนการเลือกเครื่องแก้วที่เหมาะสมกับปฏิกิริยาเคมี):

| อุปกรณ์ | ต้องการ | GPIO ที่แนะนำ | ห้ามใช้ |
|---------|--------|--------------|--------|
| LED แดง/เขียว | Digital Output | 2, 4, 12, 16, 17, 21, 22, 26 | 34, 35, 36, 39 (input-only) |
| ปุ่มกด (Button) | Digital Input | 34, 35, 39 (input-only เหมาะมาก) | - |
| หัววัด pH | ADC Input | 32, 33 (ADC1 แนะนำ) | 25, 26 ถ้าใช้ WiFi |
| ปั๊ม (Pump) | PWM Output | 2, 4, 12, 16, 17, 21, 22, 26 | 34, 35, 36, 39 (no PWM) |
| Buzzer | PWM Output | 2, 4, 12, 16, 17, 21, 22, 26 | 34, 35, 36, 39 (no PWM) |
| DS18B20 | Digital I/O | 2, 4, 12, 16, 17, 21, 22 | 34, 35, 36, 39 (input-only) |

### 2.4 ค่าเริ่มต้นใน config.py (Default Pin Assignments)

ไฟล์ `config.py` กำหนดค่าเริ่มต้นไว้ดังนี้ (นิสิตสามารถเปลี่ยนตามการต่อสายจัมเปอร์):

```python
# LED แสดงสถานะ (Status LEDs) - ต้องการ OUTPUT
LED_RED = 2       # GPIO2  - LED สีแดง
LED_GREEN = 4     # GPIO4  - LED สีเขียว

# ปุ่มกด (Buttons) - ต้องการ INPUT
BUTTON_1 = 34     # GPIO34 - ปุ่ม UP (input-only)
BUTTON_2 = 35     # GPIO35 - ปุ่ม SELECT (input-only)
BUTTON_3 = 39     # GPIO39 - ปุ่ม DOWN (input-only)

# เซ็นเซอร์ (Sensors)
PH_PIN = 25       # GPIO25 - หัววัด pH (ADC)
DS18B20_PIN = 16  # GPIO16 - เซ็นเซอร์อุณหภูมิ (OneWire)

# ปั๊มและเสียง (Pump & Buzzer) - ต้องการ PWM
# ปั๊มต่อที่ CONTROL_1 หรือ CONTROL_2 บน DEVICES header
# Pump connects to CONTROL_1 or CONTROL_2 on DEVICES header
CONTROL_1_PIN = 21  # GPIO21 - CONTROL_1 on DEVICES
CONTROL_2_PIN = 22  # GPIO22 - CONTROL_2 on DEVICES
PUMP_PIN = CONTROL_1_PIN  # เปลี่ยนเป็น CONTROL_2_PIN ถ้าต่อที่ CONTROL_2
BUZZER_PIN = 26   # GPIO26 - Buzzer
```

### 2.5 การต่ออุปกรณ์ (Wiring Diagram)

```
                    +------------------+
                    |   TitraLab Board |
                    |     (ESP32)      |
                    |                  |
  pH Probe --------| ADC pin (25)     |
  (BNC Connector)  |                  |
                    |                  |--------- ปั๊ม (Pump)
  DS18B20 ---------| GPIO16           |           PWM: CONTROL_1 (21)
                    |                  |           หรือ CONTROL_2 (22)
  (อุณหภูมิ)        |                  |
                    |                  |--------- Buzzer
  ปุ่ม 3 ปุ่ม ------| GPIO34,35,39     |           PWM pin (26)
  (Buttons)         |                  |
                    |       SPI1       |--------- จอ TFT ILI9341
  USB to Laptop ----| (CP2102)         |           (Fixed: 13,14,15,27,0)
  (Thonny IDE)      |                  |
                    +------------------+
```

---

## 3. การเริ่มต้นใช้งาน (Getting Started)

### 3.1 การเชื่อมต่อ (Connection)

1. เสียบสาย USB ระหว่าง TitraLab Board กับ Laptop
2. เปิดโปรแกรม **Thonny IDE**
3. เลือก Port ที่ถูกต้อง (เช่น COM3, COM4 บน Windows)
4. ตรวจสอบว่าเห็น `>>>` prompt ใน Shell panel

### 3.2 การอัปโหลดไฟล์ (Uploading Files)

คัดลอกไฟล์ทั้งหมดใน folder `Week_3/` ไปยัง ESP32:

```
ESP32 Flash Memory:
/
├── main.py              ← จุดเริ่มต้นโปรแกรม
├── config.py            ← ค่าคงที่และ GPIO
├── hardware/            ← Hardware drivers
│   ├── __init__.py
│   ├── pump.py
│   ├── ph_sensor.py
│   ├── temp_sensor.py
│   ├── display.py
│   ├── buttons.py
│   ├── buzzer.py
│   └── leds.py
├── core/                ← Business logic
│   ├── __init__.py
│   ├── calibrator.py
│   ├── titration.py
│   ├── data_manager.py
│   └── math_utils.py
├── modes/               ← โหมดการทำงาน (Operating modes)
│   ├── __init__.py
│   ├── base_mode.py
│   ├── mode_calibrate_ph.py
│   ├── mode_calibrate_flow.py
│   ├── mode_test_ph.py
│   ├── mode_test_flow.py
│   ├── mode_purge.py
│   └── mode_titration.py
├── ui/                  ← User interface
│   ├── __init__.py
│   └── menu.py
├── async_support/       ← Async functions (optional)
│   ├── __init__.py
│   ├── scheduler.py
│   ├── async_pump.py
│   └── async_titration.py
├── fonts/               ← ฟอนต์สำหรับจอ TFT (TFT fonts)
│   └── EspressoDolce18x24.c
├── ili9341.py           ← Driver สำหรับจอ TFT
└── xglcd_font.py        ← Library สำหรับโหลดฟอนต์
```

### 3.3 การเริ่มโปรแกรม (Starting the Program)

**วิธีที่ 1**: พิมพ์ใน Thonny Shell:
```python
import main
main.main()
```

**วิธีที่ 2**: กดปุ่ม Reset บน ESP32 (ถ้าไฟล์ชื่อ `main.py` อยู่ใน root)

**ผลลัพธ์ที่คาดหวัง (Expected Output):**
```
==================================================
กำลังเริ่มต้น Hardware (Initializing Hardware)
==================================================
[1/7] จอแสดงผล (Display)... OK
[2/7] ปุ่มกด (Buttons)... OK
[3/7] LED... OK
[4/7] Buzzer... OK
[5/7] เซ็นเซอร์ pH (pH Sensor)... OK
[6/7] เซ็นเซอร์อุณหภูมิ (Temperature Sensor)... OK
[7/7] ปั๊ม (Pump)... OK
==================================================
Hardware พร้อมใช้งาน (Hardware Ready)
==================================================
```

### 3.4 การควบคุมด้วยปุ่มกด (Button Controls)

| ปุ่ม | GPIO | หน้าที่ในเมนู | หน้าที่ในโหมดต่างๆ |
|-----|------|-------------|------------------|
| BTN1 | GPIO34 | SELECT / เลือก | ยืนยัน / ไปข้อถัดไป |
| BTN2 | GPIO35 | UP / เลื่อนขึ้น | เพิ่มค่า (+5 mL, +0.5 pH) |
| BTN3 | GPIO39 | DOWN / เลื่อนลง | ลดค่า (-5 mL, -0.5 pH) |

**การออกจากโปรแกรม**: กดปุ่ม BTN3 ค้าง 3 วินาที หรือกด Ctrl+C ใน Thonny

---

## 4. โหมดการทำงานทั้ง 6 โหมด (All 6 Modes)

### เลือกโหมดตามงาน (Select Mode by Task)

| งานที่ต้องทำ | โหมด | เมื่อไหร่ต้องใช้ |
|-------------|------|----------------|
| สอบเทียบ pH | Mode 1: Calibrate pH | ก่อนไทเทรชัน (ทุกครั้ง) |
| ตรวจสอบค่า pH | Mode 2: pH Test | หลังสอบเทียบ / ตรวจสอบ |
| สอบเทียบปั๊ม | Mode 3: Calibrate Flow | ก่อนไทเทรชัน (ทุกครั้ง) |
| ทดสอบปั๊ม | Mode 4: Flow Test | หลังสอบเทียบ / ตรวจสอบ |
| ล้างท่อ | Mode 5: Purge | ก่อน/หลังทดลอง |
| ไทเทรชันอัตโนมัติ | Mode 6: Titration | ขั้นตอนการทดลองหลัก |

---

### Mode 1: Calibrate pH / สอบเทียบเซ็นเซอร์ pH

**วัตถุประสงค์**: สร้างสมการเส้นตรงเพื่อแปลงแรงดันไฟฟ้า (mV) เป็นค่า pH

**หลักการทางเคมี (Nernst Equation):**
```
E = E0 - (2.303 RT / nF) x pH

ที่อุณหภูมิ 25 C:
E = E0 - 59.16 mV x pH

ดังนั้น: pH = slope_m x mV + intercept_b
  โดย slope_m มีหน่วย pH/mV (ค่าลบ เพราะ pH สูง = mV ต่ำ)
```

**ขั้นตอน (Step-by-Step):**

```
ขั้นตอนที่ 1: จุ่มหัววัดในบัฟเฟอร์ pH 4.00
         ↓
    รอ 10 วินาทีจนค่าเสถียร (stabilize)
         ↓
    ระบบบันทึกค่า mV อัตโนมัติ
         ↓
ขั้นตอนที่ 2: จุ่มหัววัดในบัฟเฟอร์ pH 7.00
         ↓
    รอ 10 วินาที → บันทึก mV
         ↓
ขั้นตอนที่ 3: จุ่มหัววัดในบัฟเฟอร์ pH 10.00
         ↓
    รอ 10 วินาที → บันทึก mV
         ↓
ระบบคำนวณ Linear Regression:
    pH = slope_m x mV + intercept_b
         ↓
ตรวจสอบ R-squared >= 0.99
    ถ้าผ่าน → บันทึกลง data_calibrate.txt
    ถ้าไม่ผ่าน → แจ้งเตือน ต้องสอบเทียบใหม่
```

**เกณฑ์ผ่าน (Acceptance Criteria):**
- R-squared (R2) >= 0.99 (ความสัมพันธ์เชิงเส้นต้องดีมาก)
- slope_m ควรใกล้เคียง **-0.0169 pH/mV** (ค่าทฤษฎีจาก Nernst: 1/(-59.16 mV/pH))

**ข้อมูลที่บันทึก:**
```
ไฟล์: data_calibrate.txt
รูปแบบ CSV:
  slope_m,intercept_b,r_squared,cal_temp
  -0.016911,34.9800,0.999500,25.20
```

**สิ่งที่ต้องเตรียม:**
- สารละลายบัฟเฟอร์ (buffer solution) pH 4.00, 7.00, 10.00
- บีกเกอร์ 3 ใบ + น้ำกลั่นสำหรับล้างหัววัดระหว่างเปลี่ยนบัฟเฟอร์
- กระดาษซับสำหรับซับหัววัด

---

### Mode 2: pH Test / ทดสอบค่า pH

**วัตถุประสงค์**: ตรวจสอบว่าการสอบเทียบถูกต้อง โดยวัด pH แบบ real-time

**ขั้นตอน:**
1. เลือก Mode 2 จากเมนู
2. จุ่มหัววัดในสารละลายที่ทราบค่า pH (เช่น บัฟเฟอร์)
3. จอแสดงค่า pH แบบ real-time (อัปเดตทุก 1 วินาที)
4. ตรวจสอบว่าค่าที่อ่านได้ตรงกับค่าที่คาดหวัง
5. กด BTN1 (SELECT) เพื่อออก

**วิธีตรวจสอบ:**
- จุ่มในบัฟเฟอร์ pH 4.00 ต้องอ่านได้ 4.00 +/- 0.05
- จุ่มในบัฟเฟอร์ pH 7.00 ต้องอ่านได้ 7.00 +/- 0.05
- ถ้าค่าผิดเพี้ยนมาก ให้กลับไปสอบเทียบใหม่ (Mode 1)

---

### Mode 3: Calibrate Flow / สอบเทียบอัตราการไหลของปั๊ม

**วัตถุประสงค์**: หาอัตราการไหล (mL/s) ของปั๊ม เพื่อให้ระบบคำนวณปริมาตรที่จ่ายได้แม่นยำ

**หลักการ:**
```
อัตราการไหล (flow rate) = ปริมาตรจริง (mL) / เวลา (s)

ตัวอย่าง: สูบได้ 5.00 mL ใน 18.05 วินาที
  flow_rate = 5.00 / 18.05 = 0.2770 mL/s
```

**ขั้นตอน (Step-by-Step):**

```
1. เตรียมภาชนะรองรับของเหลว (ใช้กระบอกตวงหรือบีกเกอร์)
         ↓
2. เลือก Mode 3 จากเมนู
         ↓
3. กด BTN1 (SELECT) เพื่อเริ่มสูบ
   → ปั๊มจะสูบจนได้ปริมาตรประมาณ 5 mL แล้วหยุด
         ↓
4. วัดปริมาตรจริงที่สูบได้ด้วยกระบอกตวง
         ↓
5. พิมพ์ปริมาตรจริง (mL) ผ่าน Thonny terminal
   (ระบบจะถาม input() ใน terminal)
         ↓
6. ระบบคำนวณ flow_rate = volume / time
         ↓
7. บันทึกลง data_flowrate.txt (ทศนิยม 4 ตำแหน่ง)
```

**ความสำคัญของทศนิยม 4 ตำแหน่ง:**
```
ตัวอย่างความคลาดเคลื่อนสะสม (Cumulative Error):
  - ใช้ 0.28 mL/s (2 ทศนิยม): ที่ 60 วินาที = 16.80 mL
  - ใช้ 0.2772 mL/s (4 ทศนิยม): ที่ 60 วินาที = 16.63 mL
  - ผลต่าง = 0.17 mL → อาจเลยจุดสมมูลไปแล้ว!
```

**ข้อมูลที่บันทึก:**
```
ไฟล์: data_flowrate.txt
บรรทัดที่ 1: 0.2772        (flow_rate, mL/s, 4 ทศนิยม)
บรรทัดที่ 2: Last saved: 2025-03-15
```

---

### Mode 4: Flow Test / ทดสอบอัตราการไหล

**วัตถุประสงค์**: ตรวจสอบว่าปั๊มจ่ายปริมาตรตรงตามที่สอบเทียบ

**ขั้นตอน:**
1. เลือก Mode 4 จากเมนู
2. ระบบจะสูบปริมาตรที่กำหนด (ตามค่า flow_rate ที่สอบเทียบไว้)
3. วัดปริมาตรจริงที่ได้ ตรวจสอบว่าตรงกับค่าเป้าหมาย
4. ถ้าผลต่างมาก (เช่น %RSD > 5%) ให้สอบเทียบใหม่ (Mode 3)

---

### Mode 5: Purge / ล้างท่อ

**วัตถุประสงค์**: ล้างท่อปั๊มด้วยน้ำกลั่น เพื่อกำจัดสารตกค้างหรือฟองอากาศ

**เมื่อไหร่ต้องใช้:**
- ก่อนเริ่มทดลอง (ไล่อากาศออกจากท่อ)
- หลังเสร็จสิ้นทดลอง (ล้างสารเคมีออก)
- เมื่อเปลี่ยนสารไทแทรนต์

**ขั้นตอน:**
1. จุ่มปลายท่อดูด (suction tube) ในน้ำกลั่น
2. วางปลายท่อจ่าย (discharge tube) ในภาชนะเก็บของเสีย
3. เลือก Mode 5 จากเมนู
4. กด BTN1 (SELECT) เพื่อเริ่มสูบ
5. ปั๊มจะทำงานต่อเนื่อง 2-3 นาที
6. กด BTN1 (SELECT) อีกครั้งเพื่อหยุด

**ข้อสำคัญ**: ตรวจสอบว่าไม่มีฟองอากาศ (air bubble) ในท่อก่อนเริ่มไทเทรชัน

---

### Mode 6: Full Auto Titration / ไทเทรชันอัตโนมัติ

**วัตถุประสงค์**: ดำเนินการไทเทรชันกรด-เบสแบบอัตโนมัติ บันทึกข้อมูล pH vs ปริมาตร

**ข้อกำหนดก่อนเริ่ม (Prerequisites):**
- ต้องสอบเทียบ pH แล้ว (Mode 1) - R2 >= 0.99
- ต้องสอบเทียบ flow rate แล้ว (Mode 3)
- ท่อปั๊มต้องไม่มีฟองอากาศ (ใช้ Mode 5 ล้างก่อน)

#### ขั้นตอนการตั้งค่า (Setup Steps):

```
ขั้นตอน 1: ตั้งปริมาตรสารตัวอย่าง (Sample Volume)
  ┌─────────────────────────────┐
  │  Sample Volume: 5.0 mL     │
  │  [UP: +5 mL] [DOWN: -5 mL] │
  │  [SELECT: ยืนยัน]           │
  └─────────────────────────────┘
  ช่วงค่า: 5 - 100 mL (เพิ่ม/ลดทีละ 5 mL)
  ค่าเริ่มต้น: 5.0 mL
         ↓
ขั้นตอน 2: ตั้งค่า pH เป้าหมาย (Target pH)
  ┌─────────────────────────────┐
  │  Target pH: 7.0             │
  │  [UP: +0.5] [DOWN: -0.5]   │
  │  [SELECT: ยืนยัน]           │
  └─────────────────────────────┘
  ปรับค่าทีละ 0.5
         ↓
ขั้นตอน 3: หน้าจอ Ready (Checklist)
  ┌─────────────────────────────┐
  │  CHECKLIST:                 │
  │  - หัววัดอยู่ในสารตัวอย่าง   │
  │  - สารไทแทรนต์พร้อม         │
  │  - ท่อไม่มีฟองอากาศ         │
  │  [SELECT: เริ่มไทเทรชัน]     │
  └─────────────────────────────┘
```

#### อัลกอริทึมการไทเทรชัน (Titration Algorithm):

```
เริ่มต้น: อ่านค่า pH เริ่มต้น (Volume = 0 mL)
    ↓
วนซ้ำ (Loop):
    1. สูบสารไทแทรนต์ 0.2 mL (pump 0.2 mL at 100% duty)
    2. หยุดปั๊ม (stop pump)
    3. รอ 10 วินาที ให้ pH เสถียร (wait for stabilization)
    4. อ่านค่า pH และอุณหภูมิ (read pH and temperature)
    5. คำนวณ dpH/dV (derivative)
    6. บันทึกข้อมูลลง CSV (log to file)
    7. แสดงผลบนจอ TFT และ terminal
    ↓
เงื่อนไขหยุด (Stop Conditions):
    - ปริมาตรรวม >= ปริมาตรสูงสุด (2 x sample volume)
    - ตรวจพบจุดสมมูล (|dpH/dV| ลดลงหลังจากสูงสุด)
    - นิสิตกด BTN1 (SELECT) เพื่อหยุดเอง
    - เวลาเกิน 600 วินาที (10 นาที)
```

#### ค่าคงที่สำคัญ (Key Constants):

| ค่า | ค่าเริ่มต้น | ความหมาย |
|-----|-----------|---------|
| DOSE_VOLUME | 0.2 mL | ปริมาตรต่อ step (คงที่ทุก step) |
| STABILIZE_TIME | 10.0 s | เวลารอ pH เสถียร |
| SAMPLE_VOLUME | 5.0 mL | ปริมาตรสารตัวอย่าง |
| MAX_VOLUME | 2 x sample | ปริมาตรไทเทรชันสูงสุด |
| Total Steps | max / 0.2 | จำนวน step ทั้งหมด (เช่น 50 step) |

#### ตัวอย่างการแสดงผลใน Terminal:

```
==================================================
เริ่มการไทเทรชันอัตโนมัติ (Starting Automatic Titration)
==================================================
ปริมาตรตัวอย่าง (Sample): 5.0 mL
ปริมาตรสูงสุด (Max): 10.0 mL (2x sample)
ปริมาตรต่อครั้ง (Dose): 0.2 mL
จำนวน step (Total steps): 50
--------------------------------------------------
Cycle   1: V=  0.20mL, pH= 1.22, dpH/dV= +0.150
Cycle   2: V=  0.40mL, pH= 1.25, dpH/dV= +0.175
...
Cycle  24: V=  4.80mL, pH= 3.50, dpH/dV= +2.500
Cycle  25: V=  5.00mL, pH= 7.10, dpH/dV=+18.000  ← จุดสมมูล!
Cycle  26: V=  5.20mL, pH=10.50, dpH/dV=+17.000
...
==================================================
พบจุดสมมูล! (Equivalence Point Found!)
  ปริมาตร (Volume): 5.000 mL
  pH: 7.100
  dpH/dV สูงสุด (Max dpH/dV): 18.000
==================================================
```

#### ระหว่างไทเทรชัน:

| การกระทำ | วิธีทำ |
|---------|-------|
| หยุดไทเทรชัน (Stop) | กด BTN1 (SELECT) |
| ดูค่าปัจจุบัน | ดูจอ TFT หรือ Thonny terminal |
| เสียงเตือนเสร็จ | Buzzer ส่งเสียง 2 ครั้ง (beep-beep) |

---

## 5. ขั้นตอนการทดลองวันจริง (Lab Day Workflow)

### ลำดับการใช้งานที่แนะนำ:

```
=== เตรียมการ (Preparation) ===

1. [Mode 5: Purge]        ล้างท่อด้วยน้ำกลั่น (2-3 นาที)
   │                      → ตรวจว่าไม่มีฟองอากาศ
   ▼
2. [Mode 1: Calibrate pH] สอบเทียบด้วย buffer pH 4, 7, 10
   │                      → R2 ต้อง >= 0.99
   ▼
3. [Mode 2: pH Test]      ตรวจสอบค่า pH (optional)
   │                      → ค่าที่อ่านต้องตรงกับ buffer
   ▼
4. [Mode 3: Calibrate Flow] สอบเทียบอัตราไหลปั๊ม
   │                        → วัดปริมาตรจริงด้วยกระบอกตวง
   ▼
5. [Mode 4: Flow Test]    ทดสอบปริมาตร (optional)

=== ไทเทรชัน (Titration) ===

   ▼
6. เตรียมสารตัวอย่าง (Prepare analyte)
   - ปิเปตสารตัวอย่าง 5 mL ลงบีกเกอร์
   - จุ่มหัววัด pH ในสารตัวอย่าง
   - จุ่มท่อดูดใน NaOH (สารไทแทรนต์)
   ▼
7. [Mode 6: Titration]    เริ่มไทเทรชันอัตโนมัติ
   │                      → รอจนเสร็จ (ใช้เวลา 5-15 นาที)
   ▼
8. บันทึกผล → ไฟล์ titration_data_R1.csv (อัตโนมัติ)

=== ทดลองซ้ำ (Replicate) ===

   ▼
9. ล้างหัววัด + เตรียมสารตัวอย่างใหม่
   ▼
10. [Mode 6: Titration]   ไทเทรชันรอบที่ 2
    │                     → ไฟล์ titration_data_R2.csv
    ▼
11. ทำซ้ำจนครบ (ปกติ 3 replicates)

=== เก็บของ (Cleanup) ===

    ▼
12. [Mode 5: Purge]       ล้างท่อหลังเสร็จสิ้น
    ▼
13. ดาวน์โหลดไฟล์ CSV ผ่าน Thonny
    ▼
14. วิเคราะห์ด้วย EquivPoint tool
```

---

## 6. การดาวน์โหลดและวิเคราะห์ข้อมูล (Data Download and Analysis)

### 6.1 ดาวน์โหลดไฟล์จาก ESP32 (Download from ESP32)

ข้อมูลถูกบันทึกใน ESP32 flash memory (ไม่ใช้ SD Card):

**ขั้นตอนดาวน์โหลดผ่าน Thonny IDE:**

```
1. เปิด Thonny IDE (ต้องเชื่อมต่อ ESP32 อยู่)
2. มองหา "Files" panel ด้านซ้าย
   - ถ้าไม่เห็น: View → Files
3. ในส่วน "MicroPython device" จะเห็นไฟล์:
   - titration_data_R1.csv
   - titration_data_R2.csv
   - data_calibrate.txt
   - data_flowrate.txt
4. คลิกขวาที่ไฟล์ CSV ที่ต้องการ
5. เลือก "Download to..."
6. เลือกตำแหน่งบันทึกบน laptop (เช่น folder EquivPoint/)
```

### 6.2 วิเคราะห์ด้วย EquivPoint Tool

EquivPoint เป็น Python tool สำหรับหาจุดสมมูลจากข้อมูลไทเทรชัน
โดยใช้ spline interpolation และ derivative analysis:

**ขั้นตอนการติดตั้ง (ครั้งแรก):**
```bash
# เปิด Command Prompt หรือ Terminal
# ไปยังโฟลเดอร์ EquivPoint ในโปรเจกต์ TitraLab
# (ปรับ path ตามตำแหน่งที่เก็บโปรเจกต์บนเครื่องของนิสิต)
cd <your-path>/TitraLab/EquivPoint

# สร้าง virtual environment (ครั้งแรก)
python -m venv venv

# เปิดใช้งาน virtual environment (Windows)
venv\Scripts\activate

# ติดตั้ง packages จาก requirements.txt
pip install -r requirements.txt
```

**ขั้นตอนการใช้งาน:**
```bash
# เปิดใช้งาน virtual environment
cd <your-path>/TitraLab/EquivPoint
venv\Scripts\activate

# วิเคราะห์ข้อมูล
python equiv_point.py titration_data_R1.csv

# บันทึกกราฟเป็นไฟล์ PNG
python equiv_point.py titration_data_R1.csv --save
```

### 6.3 ผลลัพธ์จาก EquivPoint (Analysis Output)

EquivPoint แสดงกราฟ 3 ช่อง (3-panel plot):

![EquivPoint Analysis - การวิเคราะห์จุดสมมูล](../../EquivPoint/data.png)

| Panel | ชื่อ | คำอธิบาย |
|:-----:|------|----------|
| 1 | Titration Curve | เส้นโค้ง S-shape (pH vs Volume) + Spline fit |
| 2 | First Derivative | dpH/dV - จุดสูงสุด (★) คือจุดสมมูล |
| 3 | Second Derivative | d²pH/dV² - จุดตัดศูนย์ (zero crossing) ยืนยันจุดสมมูล |

**ผลลัพธ์ใน Console:**
```
=== Equivalence Point Analysis Results ===
Method 1 (Max dpH/dV): Volume = 5.000 mL, pH = 7.10
Method 2 (d2pH/dV2 = 0): Volume = 4.980 mL
Method 3 (pH = 7 crossing): Volume = 4.990 mL
```

### 6.4 ตัวอย่างการวิเคราะห์ผลทั้งหมด (Complete Analysis Example)

```bash
# ดาวน์โหลดไฟล์จาก ESP32 ผ่าน Thonny → บันทึกที่ EquivPoint/

# วิเคราะห์ทั้ง 3 replicates
python equiv_point.py titration_data_R1.csv --save
python equiv_point.py titration_data_R2.csv --save
python equiv_point.py titration_data_R3.csv --save

# ผลลัพธ์: titration_data_R1.png, R2.png, R3.png
# รวมถึงค่า equivalence point volume สำหรับคำนวณความเข้มข้น
```

---

## 7. รูปแบบไฟล์ข้อมูล (Data File Formats)

### 7.1 ไฟล์ผลไทเทรชัน (Titration Data CSV)

**ชื่อไฟล์**: `titration_data_R1.csv`, `titration_data_R2.csv`, ...
(R = Replicate, หมายเลขเพิ่มอัตโนมัติ)

**รูปแบบ:**
```csv
Volume (mL),pH Value,Cycle,Time(s),Temperature(C)
0.000,1.188,0,0.00,25.10
0.200,1.215,1,12.50,25.12
0.400,1.248,2,25.00,25.11
0.600,1.290,3,37.50,25.13
...
5.000,7.100,25,312.50,25.15
...
10.000,12.500,50,625.00,25.18
```

**ความเข้ากันกับ EquivPoint:**
- EquivPoint ต้องการเฉพาะ 2 คอลัมน์แรก: `Volume (mL)` และ `pH Value`
- คอลัมน์ `Cycle`, `Time(s)`, `Temperature(C)` เป็นข้อมูลเสริม (EquivPoint จะข้ามไป)
- ไฟล์จาก ESP32 ใช้ได้โดยตรงกับ EquivPoint ไม่ต้องแก้ไข

### 7.2 ไฟล์สอบเทียบ pH (pH Calibration File)

**ชื่อไฟล์**: `data_calibrate.txt`

**รูปแบบ CSV:**
```
slope_m,intercept_b,r_squared,cal_temp
-0.016911,34.9800,0.999500,25.20
```

| ค่า | ความหมาย | หน่วย | ตัวอย่าง |
|-----|---------|------|---------|
| slope_m | ความชันของสมการ | pH/mV | -0.016911 |
| intercept_b | จุดตัดแกน y | pH | 34.9800 |
| r_squared | ค่า R-squared | ไม่มีหน่วย | 0.999500 |
| cal_temp | อุณหภูมิขณะสอบเทียบ | Celsius | 25.20 |

**วิธีใช้**: `pH = slope_m x mV + intercept_b`

### 7.3 ไฟล์สอบเทียบอัตราการไหล (Flow Rate File)

**ชื่อไฟล์**: `data_flowrate.txt`

**รูปแบบ:**
```
0.2772
Last saved: 2025-03-15
```

| บรรทัด | ความหมาย |
|--------|---------|
| บรรทัดที่ 1 | อัตราการไหล (mL/s, ทศนิยม 4 ตำแหน่ง) |
| บรรทัดที่ 2 | วันที่สอบเทียบล่าสุด |

---

## 8. ตารางอ้างอิง GPIO (GPIO Reference)

### 8.1 คุณสมบัติ GPIO ทั้งหมด (Complete GPIO Capabilities)

| GPIO | Output | Input | ADC | PWM | หมายเหตุ |
|------|--------|-------|-----|-----|---------|
| 2    | Yes | Yes | No  | Yes | มี LED บนบอร์ด (onboard LED) |
| 4    | Yes | Yes | No  | Yes | - |
| 12   | Yes | Yes | Yes | Yes | ADC2 |
| 16   | Yes | Yes | No  | Yes | เหมาะสำหรับ DS18B20 |
| 17   | Yes | Yes | No  | Yes | - |
| 21   | Yes | Yes | No  | Yes | เหมาะสำหรับปั๊ม (PWM) |
| 22   | Yes | Yes | No  | Yes | - |
| 25   | Yes | Yes | Yes | Yes | ADC2 (conflict กับ WiFi) |
| 26   | Yes | Yes | Yes | Yes | ADC2 |
| 32   | Yes | Yes | Yes | Yes | **ADC1 - แนะนำสำหรับ pH** |
| 33   | Yes | Yes | Yes | Yes | **ADC1 - แนะนำสำหรับ pH** |
| 34   | **No** | Yes | Yes | **No** | **Input-only** - เหมาะสำหรับปุ่ม |
| 35   | **No** | Yes | Yes | **No** | **Input-only** - เหมาะสำหรับปุ่ม |
| 36   | **No** | Yes | Yes | **No** | **Input-only** |
| 39   | **No** | Yes | Yes | **No** | **Input-only** - เหมาะสำหรับปุ่ม |

### 8.2 ขาที่ห้ามใช้ (Reserved Pins)

| GPIO | เหตุผล |
|------|-------|
| 0 | TFT Reset + Boot mode select |
| 5 | SD Card CS (PCB hardwired) |
| 13 | TFT MOSI (PCB hardwired) |
| 14 | TFT SCK (PCB hardwired) |
| 15 | TFT CS (PCB hardwired) |
| 18 | SD Card SCK (PCB hardwired) |
| 19 | SD Card MISO (PCB hardwired) |
| 23 | SD Card MOSI (PCB hardwired) |
| 27 | TFT DC (PCB hardwired) |

### 8.3 วิธีคิดเลือกขา GPIO (How to Choose GPIO)

**เปรียบเสมือนการเลือกเครื่องแก้วทางเคมี:**
- อยากวัด pH (ADC) → เลือก GPIO ที่มี ADC เหมือนเลือก buret ที่อ่านค่าได้ละเอียด
- อยากขับปั๊ม (PWM) → เลือก GPIO ที่รองรับ output เหมือนเลือกเครื่องแก้วที่ทนแรงดัน
- อยากอ่านปุ่ม (Input) → GPIO ใดก็ได้ เหมือนใช้ beaker ธรรมดารับของเหลว

**ตัวอย่างการตัดสินใจ:**
```
ถาม: "ฉันจะต่อ pH probe ที่ GPIO ไหน?"
ตอบ:
  1. pH probe ส่งสัญญาณแอนะล็อก → ต้องใช้ ADC
  2. ADC1 (GPIO 32, 33): ใช้ได้เสมอ แม้เปิด WiFi
  3. ADC2 (GPIO 25, 26): ใช้ไม่ได้ถ้าเปิด WiFi
  4. สรุป: เลือก GPIO32 หรือ GPIO33 (แนะนำ)
```

---

## 9. การแก้ไขปัญหา (Troubleshooting)

### 9.1 ปัญหาเกี่ยวกับการสอบเทียบ pH (pH Calibration Issues)

| ปัญหา | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|-------|-------------------|--------|
| R2 < 0.99 | หัววัดสกปรก | ล้างหัววัดด้วยน้ำกลั่น ซับให้แห้ง |
| R2 < 0.99 | บัฟเฟอร์เสื่อมสภาพ | ใช้บัฟเฟอร์ชุดใหม่ |
| R2 < 0.99 | ฟองอากาศที่หัววัด | ใช้ลูกยางดูดหัววัดไล่ฟอง |
| ค่า mV ไม่เปลี่ยน | สายขาด/หลวม | ตรวจสอบสายจัมเปอร์ GPIO→DEVICES |
| ค่า mV กระโดดไม่นิ่ง | สัญญาณรบกวน | ตรวจ ground, ห่างจากมอเตอร์ |
| Slope ผิดจากทฤษฎีมาก | หัววัดเสื่อม | เปลี่ยนหัววัดใหม่ |

### 9.2 ปัญหาเกี่ยวกับปั๊ม (Pump Issues)

| ปัญหา | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|-------|-------------------|--------|
| ปั๊มไม่ทำงาน | สายจัมเปอร์หลวม | ตรวจ GPIO→CONTROL_1 หรือ CONTROL_2 |
| ปั๊มไม่ทำงาน | PUMP_PIN ไม่ตรงกับสาย | ถ้าต่อ CONTROL_2 ต้องใช้ GPIO22 ใน config.py |
| ปั๊มไม่ทำงาน | ใช้ input-only pin | เปลี่ยนเป็น GPIO21 หรือ GPIO22 |
| ปริมาตรไม่ตรง | ท่ออุดตัน | เปลี่ยนท่อหรือล้างด้วย Mode 5 |
| ปริมาตรไม่ตรง | ฟองอากาศในท่อ | ใช้ Mode 5: Purge ไล่ฟอง |
| ปริมาตรไม่ตรง | Flow rate ผิด | สอบเทียบใหม่ด้วย Mode 3 |
| เสียงดังผิดปกติ | ท่อหัก/พับ | ตรวจสอบท่อไม่ให้พับงอ |

### 9.3 ปัญหาเกี่ยวกับจอ TFT (Display Issues)

| ปัญหา | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|-------|-------------------|--------|
| จอไม่แสดงผล | ขา SPI ผิด | ขา TFT เป็น fixed pin ไม่ต้องต่อสาย |
| จอขาวทั้งหมด | ไม่ได้ init | กดปุ่ม Reset บน ESP32 |
| ฟอนต์ไม่แสดง | ไม่มีไฟล์ฟอนต์ | คัดลอก fonts/EspressoDolce18x24.c ไป ESP32 |
| จอค้าง | โปรแกรม error | กด Ctrl+C แล้วรันใหม่ |

### 9.4 ปัญหาเกี่ยวกับไฟล์ข้อมูล (Data File Issues)

| ปัญหา | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|-------|-------------------|--------|
| ไม่พบ CSV | ไทเทรชันยังไม่เสร็จ | ตรวจสอบใน Files panel ของ Thonny |
| EquivPoint error | ไฟล์เสียหาย | เปิดไฟล์ด้วย text editor ตรวจสอบ format |
| EquivPoint error | ข้อมูลน้อยเกินไป | ต้องมีอย่างน้อย 10 data points |
| ไม่สามารถเขียนไฟล์ | Flash เต็ม | ลบไฟล์เก่าออก |

### 9.5 ปัญหาทั่วไป (General Issues)

| ปัญหา | วิธีแก้ |
|-------|--------|
| ESP32 ไม่ตอบสนอง | กดปุ่ม Reset หรือถอด/เสียบ USB ใหม่ |
| Thonny เชื่อมต่อไม่ได้ | ตรวจ COM port, ลองปิด/เปิด Thonny |
| ImportError | ตรวจว่าไฟล์ทั้งหมดอยู่ใน ESP32 ครบ |
| MemoryError | รีสตาร์ท ESP32 (กด Reset) |
| ค่า pH อ่านเป็น 0.0 | ตรวจว่าโหลด calibration data แล้ว |

---

## 10. ข้อควรระวังและข้อปฏิบัติ (Safety and Best Practices)

### 10.1 ความปลอดภัยทางเคมี (Chemical Safety)

- สวมแว่นตานิรภัยตลอดเวลาที่ทำการทดลอง
- สวมถุงมือเมื่อจับสารเคมี (โดยเฉพาะ NaOH และ HCl เข้มข้น)
- หากสารเคมีสัมผัสผิวหนัง ล้างด้วยน้ำสะอาดทันที
- ทิ้งของเสียในภาชนะที่กำหนดเท่านั้น

### 10.2 ความปลอดภัยทางไฟฟ้า (Electrical Safety)

- ห้ามถอด/เสียบสายจัมเปอร์ขณะที่เครื่องเปิดอยู่
- ระวังอย่าให้สารเคมีหยดลงบนแผงวงจร
- ใช้บอร์ดบนพื้นผิวแห้งเท่านั้น
- ถ้ามีสัญญาณผิดปกติ (เช่น กลิ่นไหม้ ร้อนผิดปกติ) ให้ถอด USB ทันที

### 10.3 ข้อปฏิบัติสำหรับหัววัด pH (pH Probe Care)

- เก็บหัววัดในสารละลาย KCl 3M เสมอ (ห้ามเก็บแห้ง)
- ล้างด้วยน้ำกลั่นก่อนจุ่มในบัฟเฟอร์แต่ละตัว
- ซับเบาๆ ด้วยกระดาษซับ (ห้ามถู)
- อย่าจับส่วน glass bulb ด้วยมือเปล่า
- สอบเทียบใหม่ทุกครั้งที่เริ่มทดลอง

### 10.4 ข้อปฏิบัติสำหรับการบันทึกข้อมูล (Data Management)

- ดาวน์โหลดข้อมูลทุกครั้งหลังทดลองเสร็จ (ก่อนปิดเครื่อง)
- ตั้งชื่อไฟล์ที่ดาวน์โหลดให้ชัดเจน (เช่น เพิ่มชื่อ-วันที่)
- สำรองข้อมูลไว้มากกว่า 1 ที่
- ตรวจสอบไฟล์ CSV หลังดาวน์โหลดว่ามีข้อมูลครบ

### 10.5 ข้อปฏิบัติสำหรับท่อปั๊ม (Tubing Care)

- ล้างท่อด้วย Mode 5 (Purge) ทุกครั้งก่อนและหลังใช้งาน
- ตรวจสอบว่าไม่มีฟองอากาศก่อนเริ่มไทเทรชัน
- อย่าให้ท่อพับงอ
- เปลี่ยนท่อเมื่อเห็นว่าเสื่อมสภาพ (เหลืองหรือแข็ง)

---

## 11. โครงสร้างโค้ด (Code Architecture)

### 11.1 แผนผังโครงสร้าง (Architecture Diagram)

```
                    +-------------+
                    |   main.py   |  ← จุดเริ่มต้น (Entry Point)
                    +------+------+
                           |
              +------------+------------+
              |                         |
     +--------v--------+     +---------v---------+
     |  HardwareHub    |     |    MenuSystem     |
     |  (ศูนย์รวม HW)   |     |  (ระบบเมนู)       |
     +--------+--------+     +-------------------+
              |
     +--------+--------+--------+--------+--------+
     |        |        |        |        |        |
  Display  Buttons   Pump   PHSensor  Temp    Buzzer
  (จอ)     (ปุ่ม)    (ปั๊ม)  (pH)      (อุณหภูมิ) (เสียง)

              +-------------------+
              |    Core Logic     |
              +--------+----------+
              |        |          |
         Calibrator  Titration  DataManager
         (สอบเทียบ)  (ไทเทรชัน)  (จัดการไฟล์)
```

### 11.2 หลักการ OOP ที่ใช้ (OOP Concepts Used)

| หลักการ OOP | ตัวอย่างในระบบ | อุปมาทางเคมี |
|------------|--------------|-------------|
| Class/คลาส | `Pump`, `PHSensor` | เหมือน "ชนิด" ของเครื่องมือ |
| Object/ออบเจกต์ | `pump = Pump()` | เหมือนเครื่องมือตัวจริงที่ใช้งาน |
| Encapsulation/การห่อหุ้ม | `self._flow_rate` (private) | เหมือนกลไกภายในเครื่องมือ |
| Composition/การประกอบ | HardwareHub มี Pump, PHSensor | เหมือนชุดอุปกรณ์ไทเทรชัน |
| Dependency Injection | `TitrationController(pump=pump)` | เหมือนการเลือกอุปกรณ์ก่อนทดลอง |

### 11.3 แผนผังการไหลของข้อมูล (Data Flow)

```
pH Probe → ADC (mV) → สมการ pH = slope*mV + intercept → ค่า pH
                                                            ↓
Pump → PWM → flow_rate x time = volume (mL)               ↓
                    ↓                                      ↓
               ปริมาตรรวม (total volume) ─────────────→ CSV File
                                                            ↓
                                              EquivPoint (Desktop)
                                                            ↓
                                              Equivalence Point
                                              (จุดสมมูล)
```

---

## คู่มืออ้างอิงฉบับย่อ (Quick Reference Card)

### คำสั่งเริ่มต้น (Startup Commands)

```python
# เริ่มโปรแกรม (Start program)
import main
main.main()

# หรือรัน config.py เพื่อตรวจสอบ GPIO
import config
config.validate_pins()
```

### สรุปลำดับงาน (Workflow Summary)

```
Purge → Calibrate pH → Calibrate Flow → Titrate → Download → Analyze
(ล้าง)   (สอบเทียบ pH)   (สอบเทียบปั๊ม)  (ไทเทรต)  (ดาวน์โหลด) (วิเคราะห์)
```

### คำสั่ง EquivPoint

```bash
# วิเคราะห์ไฟล์เดียว
python equiv_point.py titration_data_R1.csv

# วิเคราะห์และบันทึกกราฟ
python equiv_point.py titration_data_R1.csv --save
```

### ไฟล์สำคัญ

| ไฟล์ | ตำแหน่ง | เนื้อหา |
|------|---------|--------|
| `data_calibrate.txt` | ESP32 flash | slope, intercept, R2, temp |
| `data_flowrate.txt` | ESP32 flash | flow_rate (mL/s) |
| `titration_data_R*.csv` | ESP32 flash | Volume, pH, Time, Temp |

---

## หมายเหตุสำหรับอาจารย์ (Notes for Instructors)

ไฟล์นี้ออกแบบมาเป็นคู่มือการใช้งานสำหรับนิสิตในห้องปฏิบัติการ
หากต้องการเอกสารเชิงลึกเกี่ยวกับโครงสร้างโค้ด โปรดดูที่:

- `hardware/README.md` - รายละเอียด hardware classes
- `core/README.md` - algorithm สำหรับ calibration และ titration
- `modes/README.md` - โครงสร้างของแต่ละโหมด
- `docs/agent-spec/` - specifications สำหรับ AI agents

**ข้อเสนอแนะการใช้งาน:**
- ให้นิสิตอ่าน Section 1-5 ก่อนวันทดลอง (เป็น prelab)
- Section 6 สำหรับใช้หลังทดลอง (วิเคราะห์ข้อมูล)
- Section 8-9 เป็นเอกสารอ้างอิงเมื่อเกิดปัญหา

---

*TitraLab Week 3 - User Manual v2.0*
*ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย*
*Integrated Chemistry Laboratory I (2302311)*

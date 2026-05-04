# TitraLab Week 1: รู้จักบอร์ด TitraLab
# TitraLab Week 1: Introduction to TitraLab Board

---

> **รายวิชา:** 2302311 Integrated Chemistry Laboratory I
> **ภาควิชา:** เคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย
> **Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## ภาพรวม (Overview)

**ระยะเวลา (Duration):** 3 ชั่วโมง / 3 hours

**TitraLab** คือบอร์ดพัฒนาสำหรับการศึกษาที่ใช้ ESP32 สำหรับการไทเทรตกรด-เบสอัตโนมัติ บอร์ดนี้รวมเซ็นเซอร์ (pH probe, DS18B20), จอแสดงผล TFT 2.4", SD card, buzzer, LED และปั๊มเพอริสตาลติก (peristaltic pump) เข้าด้วยกัน

**TitraLab** is an ESP32-based educational development board for automated acid-base titration. It integrates sensors (pH probe, DS18B20 temperature), 2.4" TFT display, SD card, buzzer, LEDs, and a peristaltic pump.

### เป้าหมายหลักของ TitraLab (Main Goal of TitraLab)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ระบบไทเทรตอัตโนมัติ                              │
│                  Automated Titration System                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   [สารตัวอย่าง]  ←──  [ปั๊ม]  ←──  [สารไทแทรนต์]                    │
│   [Analyte]     ←──  [Pump]  ←──  [Titrant]                        │
│        │                                                            │
│        ▼                                                            │
│   [เซ็นเซอร์ pH]  ──►  [ESP32]  ──►  [จอ TFT + SD Card]            │
│   [pH Sensor]    ──►  [ESP32]  ──►  [TFT + SD Card]                │
│        │                  │                                         │
│        │                  ▼                                         │
│        │         [ตรวจจับจุดสมมูล]                                  │
│        │         [Detect Equivalence Point]                         │
│        │                  │                                         │
│        └──────────────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### เส้นทางการเรียนรู้ TitraLab (TitraLab Learning Path)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TitraLab Learning Path                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Week 1                   Week 2                   Week 3          │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐  │
│   │ พื้นฐาน     │  ──►   │ การสอบเทียบ  │  ──►   │ ระบบเต็ม    │  │
│   │ Hardware    │         │ Calibration │         │ Full System │  │
│   ├─────────────┤         ├─────────────┤         ├─────────────┤  │
│   │ LED/Button  │         │ pH Sensor   │         │ Titration   │  │
│   │ ADC/PWM     │         │ Pump Flow   │         │ Loop        │  │
│   │ Display     │         │ OOP ขั้นกลาง │         │ Data Log    │  │
│   │ OOP พื้นฐาน  │         │ Inheritance │         │ Menu System │  │
│   └─────────────┘         └─────────────┘         └─────────────┘  │
│                                                                     │
│   ความซับซ้อน: ง่าย ─────────────────────────────────────► ยาก    │
│   Complexity:  Simple ──────────────────────────────────► Complex │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

หลังจากเรียนจบบทเรียนนี้ นิสิตจะสามารถ:

### วัตถุประสงค์หลัก: รู้จักฮาร์ดแวร์ TitraLab (Primary: TitraLab Hardware)

1. **เข้าใจส่วนประกอบของบอร์ด TitraLab**
   - รู้จักอุปกรณ์ทุกชิ้นบนบอร์ด: LED, Button, เซ็นเซอร์ pH, เซ็นเซอร์อุณหภูมิ, ปั๊ม, จอ TFT
   - เข้าใจบทบาทของแต่ละอุปกรณ์ในการไทเทรตอัตโนมัติ

2. **เข้าใจพื้นฐานอิเล็กทรอนิกส์สำหรับการไทเทรต**
   - **ADC (Analog-to-Digital Converter)**: แปลงสัญญาณจากเซ็นเซอร์ pH เป็นค่าดิจิทัล
   - **PWM (Pulse Width Modulation)**: ควบคุมความเร็วปั๊มสำหรับหยดสารไทแทรนต์
   - สูตรการแปลงค่า: ADC → แรงดัน → pH

3. **ใช้งานอุปกรณ์พื้นฐานได้**
   - ควบคุม LED แสดงสถานะ (เขียว = กำลังทำงาน, แดง = ถึงจุดสมมูล)
   - อ่านปุ่มกดสำหรับควบคุมการไทเทรต
   - อ่านค่าอุณหภูมิสำหรับชดเชยสมการ Nernst
   - แสดงข้อมูลบนจอ TFT

### วัตถุประสงค์รอง: ทักษะโปรแกรมสนับสนุน (Secondary: Supporting Programming Skills)

4. **เข้าใจ Class และ Object**
   - Class = พิมพ์เขียว (เหมือนแบบแปลนบีกเกอร์)
   - Object = สิ่งที่สร้างจากพิมพ์เขียว (บีกเกอร์จริงแต่ละใบ)

5. **เขียน Class อย่างง่ายได้**
   - `__init__` = Constructor (ตัวสร้าง)
   - method = ฟังก์ชันในคลาส
   - `self` = ตัวอ้างอิงถึง object ปัจจุบัน

6. **[เสริม] เข้าใจ DAC**
   - Digital-to-Analog Converter (ตรงข้ามกับ ADC)

---

## ตารางเรียน 3 ชั่วโมง (3-Hour Teaching Schedule)

### หลักการจัดลำดับ (Pedagogical Principles)

```
ง่าย → ยาก (Simple → Complex)
Digital (0/1) → Analog (0-4095)
ผลลัพธ์ทันที (LED สว่าง) → ค่าที่ต้องคำนวณ (ADC)
```

| ช่วงเวลา | หัวข้อ | ไฟล์ | เวลา |
|:--------:|--------|------|:----:|
| **ชั่วโมงที่ 1** | **Digital I/O พื้นฐาน** | | **60 นาที** |
| 0:00-0:15 | แนะนำ TitraLab: ส่วนประกอบและเป้าหมาย | - | 15 นาที |
| 0:15-0:35 | **LED (Digital Output)**: เปิด/ปิด | `core/01_led_class.py` | 20 นาที |
| | *→ เคมี: แสดงสถานะ (เขียว = กำลังทำงาน, แดง = ถึงจุดสมมูล)* | | |
| 0:35-0:50 | **Button (Digital Input)**: กด/ไม่กด | `core/02_button_class.py` | 15 นาที |
| | *→ เคมี: ควบคุมการไทเทรต (เริ่ม/หยุด/ยืนยัน)* | | |
| 0:50-1:00 | **พัก (Break)** | - | 10 นาที |
| **ชั่วโมงที่ 2** | **Analog I/O สำหรับเซ็นเซอร์/ปั๊ม** | | **60 นาที** |
| 1:00-1:20 | **ADC (Analog Input)**: อ่านค่า 0-4095 | `core/03_adc_ph_basics.py` | 20 นาที |
| | *→ เคมี: เซ็นเซอร์ pH อ่านแรงดัน แปลงเป็น pH ด้วยสมการ Nernst* | | |
| 1:20-1:35 | **PWM (Analog-like Output)**: Duty cycle | `core/04_pwm_pump_basics.py` | 15 นาที |
| | *→ เคมี: ควบคุมความเร็วปั๊ม (เร็วตอนเริ่ม, ช้าใกล้จุดสมมูล)* | | |
| 1:35-1:50 | **ADC+PWM รวมกัน**: Pot -> LED Dimming | `core/05_pot_led_dimming.py` | 15 นาที |
| | *→ เตรียมพร้อม: pH Sensor (ADC) -> Pump Speed (PWM)* | | |
| 1:50-1:55 | **เซ็นเซอร์อุณหภูมิ**: ชดเชย Nernst | `core/06_temp_sensor_class.py` | 5 นาที |
| | *→ เคมี: ความชัน Nernst เปลี่ยนตามอุณหภูมิ (59.16 mV ที่ 25°C)* | | |
| 1:55-2:00 | **พัก (Break)** | - | 5 นาที |
| **ชั่วโมงที่ 3** | **จอแสดงผล, OOP และการรวมระบบ** | | **60 นาที** |
| 2:00-2:20 | **จอ TFT**: แสดง pH และกราฟ | `core/07_display_basics.py` | 20 นาที |
| 2:20-2:40 | **OOP พื้นฐาน**: Class และ Object | `core/08_intro_oop.py` | 20 นาที |
| | *→ เปรียบเทียบ: Class = พิมพ์เขียวบีกเกอร์, Object = บีกเกอร์จริงแต่ละใบ* | | |
| 2:40-2:55 | **ตัวอย่างรวม**: Lab Alert System | `core/09_combined_example.py` | 15 นาที |
| 2:55-3:00 | สรุปและเชื่อมโยงกับ Week 2 (การสอบเทียบ) | - | 5 นาที |

### ทำไมต้องเรียน LED/Button ก่อน ADC/PWM?

| ลำดับ | หัวข้อ | ความซับซ้อน | เหตุผล |
|:-----:|--------|:-----------:|--------|
| 1 | LED | **ง่ายมาก** | 1 bit (0/1), เห็นผลทันที (ไฟติด/ดับ) |
| 2 | Button | **ง่าย** | 1 bit (กด/ไม่กด), เข้าใจ input |
| 3 | ADC | **ซับซ้อน** | 12 bit (0-4095), ต้องแปลงค่า |
| 4 | PWM | **ซับซ้อน** | 10 bit (0-1023), ต้องเข้าใจ duty cycle |

> **หมายเหตุ**: สอน Digital ก่อน Analog เหมือนสอนนับเลขก่อนสอนแคลคูลัส

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

```
Week_1/
├── core/                               # [หลัก] ไฟล์สำหรับสอนในห้องเรียน (เรียงตามลำดับการสอน)
│   ├── 01_led_class.py                 # ชม.1: คลาส LED - แสดงสถานะการไทเทรต
│   ├── 02_button_class.py              # ชม.1: คลาส Button - ควบคุมการไทเทรต
│   ├── 03_adc_ph_basics.py             # ชม.2: พื้นฐาน ADC สำหรับเซ็นเซอร์ pH
│   ├── 04_pwm_pump_basics.py           # ชม.2: พื้นฐาน PWM สำหรับควบคุมปั๊ม
│   ├── 05_pot_led_dimming.py           # ชม.2: Pot (ADC) -> LED (PWM) รวมกัน
│   ├── 06_temp_sensor_class.py         # ชม.2: คลาส TemperatureSensor - สมการ Nernst
│   ├── 07_display_basics.py            # ชม.3: พื้นฐานจอ TFT Display
│   ├── 08_intro_oop.py                 # ชม.3: บทนำ OOP (ตัวอย่างคลาส Beaker)
│   ├── 09_combined_example.py          # ชม.3: ตัวอย่างรวม Lab Alert System
│   ├── ex_status_led.py                # แบบฝึกหัด: คลาส StatusLED
│   └── README.md                       # คู่มือโฟลเดอร์ core
│
├── extras/                             # [เสริม] สื่อเพิ่มเติม
│   ├── 01_procedural/                  # ตัวอย่างแบบ Procedural (ไม่ใช้ OOP)
│   │   ├── 01_basic.py                 # LED พื้นฐาน
│   │   ├── 02_toggle.py                # สลับ LED
│   │   ├── 02_basic_loop.py            # LED กระพริบใน loop
│   │   ├── 03_twoLed.py                # ควบคุม LED 2 ดวง
│   │   ├── 03_Potentiometer.py         # อ่านค่า ADC
│   │   ├── 04_twoLed_infiniteLoop.py   # LED 2 ดวงใน infinite loop
│   │   └── 04_PWM_OUT.py               # PWM ควบคุม LED
│   ├── 02_advanced_oop/                # OOP ขั้นสูง
│   ├── 03_exercises/                   # แบบฝึกหัดพร้อมเฉลย
│   ├── 04_hardware/                    # ตัวอย่างเฉพาะฮาร์ดแวร์
│   │   ├── Buzzer/                     # Buzzer - แจ้งเตือนจุดสมมูล
│   │   ├── DAC/                        # DAC (Digital-to-Analog)
│   │   ├── DS18B20/                    # เซ็นเซอร์อุณหภูมิ
│   │   ├── SDCard/                     # SD Card - บันทึกข้อมูล
│   │   └── TFT/                        # จอ TFT - แสดง pH และกราฟ
│   ├── 05_reference/                   # เอกสารอ้างอิง
│   └── archive/                        # [เก็บถาวร] ตัวอย่าง ADC/PWM แบบละเอียด
│       ├── 07_ADC/                     # ตัวอย่าง ADC หลายไฟล์
│       └── 07_PWM/                     # ตัวอย่าง PWM หลายไฟล์
│
├── lib/                                # ไลบรารีที่จำเป็น (อัปโหลดไปยัง ESP32)
│   ├── ili9341.py                      # ไดรเวอร์จอ TFT
│   ├── xglcd_font.py                   # ไลบรารีแสดงฟอนต์
│   ├── sdcard.py                       # ไลบรารี SD Card
│   └── titralab_simple.py              # คลาสพื้นฐาน TitraLab (LED, Button, etc.)
│
├── fonts/                              # ไฟล์ฟอนต์ (อัปโหลดไปยัง ESP32)
│   ├── ArcadePix9x11.c                 # ฟอนต์เล็ก
│   └── EspressoDolce18x24.c            # ฟอนต์ใหญ่
│
├── pins.py                             # การกำหนดขา GPIO มาตรฐาน
└── README.md                           # ไฟล์นี้
```

### แผนที่ไฟล์สำหรับการสอน (File Map for Teaching)

| ชั่วโมง | หัวข้อ | ไฟล์หลัก | ไฟล์เสริม |
|:------:|--------|----------|-----------|
| **1** | LED | `core/01_led_class.py` | `extras/01_procedural/01_basic.py` |
| **1** | Button | `core/02_button_class.py` | `extras/01_procedural/02_toggle.py` |
| **2** | ADC | `core/03_adc_ph_basics.py` | `extras/01_procedural/03_Potentiometer.py` |
| **2** | PWM | `core/04_pwm_pump_basics.py` | `extras/01_procedural/04_PWM_OUT.py` |
| **2** | ADC+PWM | `core/05_pot_led_dimming.py` | - |
| **2** | Temperature | `core/06_temp_sensor_class.py` | `extras/04_hardware/DS18B20/` |
| **3** | TFT Display | `core/07_display_basics.py` | `extras/04_hardware/TFT/` |
| **3** | OOP | `core/08_intro_oop.py` | - |
| **3** | Combined | `core/09_combined_example.py` | - |

---

## เริ่มต้นใช้งาน Thonny (Getting Started with Thonny)

Thonny เป็น IDE (Integrated Development Environment/สภาพแวดล้อมพัฒนาโปรแกรม) ที่เหมาะสำหรับนิสิตที่เริ่มต้นเรียนรู้การเขียนโปรแกรม รองรับ MicroPython บน ESP32 โดยมีหน้าต่างแสดงผลที่เข้าใจง่าย

### ขั้นตอนที่ 1: ดาวน์โหลดและติดตั้ง (Download and Install)

1. เปิดเว็บไซต์ **https://thonny.org**
2. คลิกปุ่มดาวน์โหลดตามระบบปฏิบัติการ:
   - **Windows**: คลิก "Windows" แล้วรันไฟล์ `.exe`
   - **macOS**: คลิก "Mac" แล้วลากไปใส่ Applications
   - **Linux**: ใช้คำสั่ง `pip install thonny` หรือดาวน์โหลดจากเว็บ
3. ติดตั้งตามขั้นตอนปกติ (Next > Next > Install)

### ขั้นตอนที่ 2: ตั้งค่าสำหรับ ESP32 (Configure for ESP32)

1. เปิด Thonny
2. ไปที่ **Tools > Options** (เครื่องมือ > ตัวเลือก)
3. เลือกแท็บ **Interpreter** (ตัวแปลภาษา)
4. เลือก **"MicroPython (ESP32)"** จากรายการแบบเลื่อนลง
5. เลือก Port (พอร์ต):
   - **Windows**: เลือก COM port เช่น `COM3`, `COM4` (ดูใน Device Manager)
   - **macOS/Linux**: เลือก `/dev/ttyUSB0` หรือ `/dev/cu.usbserial-xxxx`
6. คลิก **OK**

> **เคล็ดลับ (Tip)**: หากไม่เห็น COM port ให้ตรวจสอบว่าติดตั้ง **CP210x USB driver** แล้ว
> (TitraLab ใช้ CP210x bridge controller - ดาวน์โหลดได้ที่ https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

### ขั้นตอนที่ 3: ตรวจสอบการเชื่อมต่อ (Verify Connection)

1. ดูที่ **Shell** panel ด้านล่าง
2. ถ้าเชื่อมต่อสำเร็จจะเห็น:
   ```
   MicroPython v1.xx.x on xxxx-xx-xx; ESP32 module with ESP32
   Type "help()" for more information.
   >>>
   ```
3. พิมพ์ `print("Hello")` แล้วกด Enter เพื่อทดสอบ

---

## อัปโหลดไฟล์ไปยัง ESP32 (Uploading Files to ESP32)

ก่อนรันโค้ดที่ใช้ TFT Display หรือไลบรารีอื่น นิสิตต้องอัปโหลดไฟล์ที่จำเป็นไปยัง ESP32 ก่อน

### เปิด File Browser (Enable File Browser)

1. ไปที่ **View > Files** (มุมมอง > ไฟล์)
2. จะเห็นหน้าต่างแบ่งเป็น 2 ส่วน:
   - **ซ้ายบน**: ไฟล์ในคอมพิวเตอร์ (This computer)
   - **ซ้ายล่าง**: ไฟล์ใน ESP32 (MicroPython device)

### อัปโหลดไฟล์เดียว (Upload Single File)

1. ในส่วน "This computer" นำทางไปยังไฟล์ที่ต้องการ
2. **คลิกขวา** ที่ไฟล์ (เช่น `ili9341.py`)
3. เลือก **"Upload to /"** (อัปโหลดไปยัง /)
4. ไฟล์จะปรากฏในส่วน "MicroPython device"

### อัปโหลดโฟลเดอร์ทั้งหมด (Upload Entire Folder)

1. ในส่วน "This computer" นำทางไปยังโฟลเดอร์ที่ต้องการ
2. **คลิกขวา** ที่โฟลเดอร์ (เช่น `lib/` หรือ `fonts/`)
3. เลือก **"Upload to /"**
4. โฟลเดอร์และไฟล์ทั้งหมดจะถูกอัปโหลด

### ความแตกต่างระหว่าง "Upload to /" และ "Save as"

| วิธี | ใช้เมื่อ |
|------|---------|
| **Upload to /** | อัปโหลดไฟล์/โฟลเดอร์ที่มีอยู่แล้วในคอมพิวเตอร์ |
| **File > Save as** | บันทึกไฟล์ที่เปิดอยู่ใน Thonny ไปยัง ESP32 (เลือก "MicroPython device" ในกล่อง Save) |

---

## การรันโค้ด (Running Code)

### วิธีที่ 1: รันจากคอมพิวเตอร์ (Run from Computer)

1. เปิดไฟล์ `.py` จากคอมพิวเตอร์ (File > Open หรือดับเบิลคลิกใน File Browser)
2. คลิกปุ่ม **Run** (สีเขียว) หรือกด **F5**
3. โค้ดจะถูกส่งไปรันบน ESP32
4. ดูผลลัพธ์ใน **Shell** panel ด้านล่าง

### วิธีที่ 2: รันจาก ESP32 (Run from ESP32)

1. ในส่วน "MicroPython device" ดับเบิลคลิกไฟล์ `.py`
2. คลิกปุ่ม **Run** (F5)

### หยุดรันโค้ด (Stop Running Code)

- กดปุ่ม **Stop** (สีแดง) หรือกด **Ctrl+C**
- หากโค้ดค้าง ให้กดปุ่ม **Reset** บน ESP32 (ปุ่ม EN หรือ RST)

### ดูผลลัพธ์ (View Output)

- ผลลัพธ์แสดงใน **Shell** panel ด้านล่าง
- ข้อความ `print()` จะปรากฏที่นี่
- ข้อผิดพลาด (Error/ข้อผิดพลาด) จะแสดงเป็นสีแดง

---

## ปัญหาที่พบบ่อยใน Thonny (Common Thonny Issues)

### ปัญหา: "Could not connect" / เชื่อมต่อไม่ได้

**อาการ**: ไม่สามารถเชื่อมต่อ ESP32 ได้

**วิธีแก้**:
1. ตรวจสอบสาย USB - ลองใช้สายอื่น (บางสายชาร์จอย่างเดียว ไม่ส่งข้อมูล)
2. ตรวจสอบ COM port ใน **Tools > Options > Interpreter**
3. ลองถอดและเสียบสาย USB ใหม่
4. ตรวจสอบว่าติดตั้ง **CP210x USB driver** แล้ว (TitraLab ใช้ CP210x bridge controller)
5. ปิดโปรแกรมอื่นที่อาจใช้ COM port อยู่ (เช่น Arduino IDE, Serial Monitor)

### ปัญหา: "No module named xxx" / ไม่พบโมดูล

**อาการ**: `ImportError: no module named 'ili9341'`

**วิธีแก้**:
1. อัปโหลดไฟล์ไลบรารี (library/ไลบรารี) ที่จำเป็นไปยัง ESP32 ก่อน
2. สำหรับ Week 1 ต้องอัปโหลด:
   - โฟลเดอร์ `lib/` (มี `ili9341.py`, `xglcd_font.py`, `sdcard.py`)
   - โฟลเดอร์ `fonts/` (มีไฟล์ `.c`)
3. ตรวจสอบว่าไฟล์อยู่ใน root directory ของ ESP32 (`/lib/`, `/fonts/`)

### ปัญหา: "REPL not responding" / REPL ไม่ตอบสนอง

**อาการ**: พิมพ์คำสั่งใน Shell แล้วไม่มีอะไรเกิดขึ้น

**วิธีแก้**:
1. กด **Ctrl+C** เพื่อหยุดโปรแกรมที่กำลังทำงาน
2. คลิกปุ่ม **Stop/Restart** (สีแดง)
3. กดปุ่ม **Reset** บน ESP32 (ปุ่ม EN หรือ RST)
4. ถอดและเสียบสาย USB ใหม่
5. ใน Thonny: **Run > Interrupt execution** แล้ว **Device > Soft reboot**

### ปัญหา: ไม่พบไฟล์ฟอนต์ (Font file not found)

**อาการ**: `OSError: [Errno 2] ENOENT` เมื่อโหลดฟอนต์

**วิธีแก้**:
1. อัปโหลดโฟลเดอร์ `fonts/` ไปยัง ESP32
2. ตรวจสอบว่าโครงสร้างเป็น `/fonts/ArcadePix9x11.c` ไม่ใช่ `/ArcadePix9x11.c`
3. ตรวจสอบชื่อไฟล์ให้ตรงกับที่ใช้ในโค้ด (ตัวพิมพ์เล็ก-ใหญ่ต้องตรงกัน/case-sensitive)

### ปัญหา: หน่วยความจำไม่พอ (Memory allocation failed)

**อาการ**: `MemoryError` หรือ `memory allocation failed`

**วิธีแก้**:
1. กด Reset บน ESP32 เพื่อล้างหน่วยความจำ
2. หลีกเลี่ยงการรันโค้ดซ้ำหลายครั้งโดยไม่ Reset
3. ลบไฟล์ที่ไม่จำเป็นออกจาก ESP32

---

## รันโค้ด TitraLab แรกของคุณ (Running Your First TitraLab Code)

ทำตามขั้นตอนนี้เพื่อรันโค้ดแรกบนบอร์ด TitraLab สำเร็จ:

### ขั้นตอนที่ 1: เชื่อมต่อ ESP32 (Connect ESP32)

1. ใช้สาย USB เชื่อมต่อบอร์ด TitraLab (ESP32) กับคอมพิวเตอร์
2. รอให้ Windows/macOS รู้จักอุปกรณ์ (อาจมีเสียง)

### ขั้นตอนที่ 2: เปิด Thonny และตั้งค่า (Open Thonny and Configure)

1. เปิด Thonny IDE
2. ไปที่ **Tools > Options > Interpreter**
3. เลือก **"MicroPython (ESP32)"**
4. เลือก COM port ที่ถูกต้อง
5. คลิก **OK**
6. ตรวจสอบว่าเห็น `>>>` ใน Shell

### ขั้นตอนที่ 3: อัปโหลดโฟลเดอร์ lib/ (Upload lib/ folder)

1. ไปที่ **View > Files** เพื่อเปิด File Browser
2. นำทางไปยังโฟลเดอร์ `Week_1/lib/`
3. คลิกขวาที่โฟลเดอร์ `lib`
4. เลือก **"Upload to /"**
5. รอจนอัปโหลดเสร็จ (ดูสถานะใน Shell)

### ขั้นตอนที่ 4: อัปโหลดโฟลเดอร์ fonts/ (Upload fonts/ folder)

1. นำทางไปยังโฟลเดอร์ `Week_1/fonts/`
2. คลิกขวาที่โฟลเดอร์ `fonts`
3. เลือก **"Upload to /"**
4. รอจนอัปโหลดเสร็จ

### ขั้นตอนที่ 5: เปิดไฟล์โค้ด (Open the code file)

1. ไปที่ **File > Open** (Ctrl+O)
2. นำทางไปยัง `Week_1/core/01_led_class.py`
3. เปิดไฟล์

### ขั้นตอนที่ 6: รันโค้ด (Run the code)

1. คลิกปุ่ม **Run** (สีเขียว) หรือกด **F5**
2. ดูผลลัพธ์ใน Shell panel:
   ```
   ==================================================
   ทดสอบคลาส LED - จำลองสถานะระบบไทเทรชัน
   LED Class Test - Simulate Titration System Status
   ==================================================
   LED 'Red-Error' พร้อมใช้งานที่ GPIO2 (ready)
   LED 'Green-Status' พร้อมใช้งานที่ GPIO4 (ready)
   ...
   ```

### ขั้นตอนที่ 7: ลองแก้ไขโค้ด (Try modifying the code)

1. ลองเปลี่ยนจำนวนครั้งกระพริบ เช่น:
   ```python
   led_green.blink(5, 0.2)  # กระพริบ 5 ครั้ง
   ```
2. กด **F5** เพื่อรันใหม่
3. สังเกตผลลัพธ์ที่เปลี่ยนไป

---

## ขา GPIO ของบอร์ด TitraLab (Hardware GPIO Pinout)

ตารางต่อไปนี้แสดงการกำหนดขา GPIO มาตรฐานของบอร์ด TitraLab (ดูรายละเอียดเพิ่มเติมในไฟล์ `pins.py`)

| อุปกรณ์ (Component) | GPIO | หมายเหตุ (Notes) |
|---------------------|------|------------------|
| **LED แสดงสถานะ (Status LEDs)** | | |
| LED สีแดง (Red) | 2 | Output - แสดงสถานะ เช่น ถึงจุดสมมูล |
| LED สีเขียว (Green) | 4 | Output - แสดงสถานะ เช่น กำลังไทเทรต |
| **ปุ่มกด (Buttons)** | | |
| Button 1 | 34 | Input-only, ใช้ external pull-down |
| Button 2 | 35 | Input-only, ใช้ external pull-down |
| Button 3 | 39 | Input-only, ใช้ external pull-down |
| **เซ็นเซอร์ (Sensors)** | | |
| DS18B20 เซ็นเซอร์อุณหภูมิ | 16 | OneWire protocol |
| pH Sensor (ADC) | 25 | อ่านค่าแรงดันจากหัววัด pH |
| **Potentiometer (ตัวต้านทานปรับค่า)** | | |
| POT1 | 32 | ADC input |
| POT2 | 33 | ADC input |
| **Actuator (อุปกรณ์ขับเคลื่อน)** | | |
| Buzzer | 26 | PWM output |
| Pump (ปั๊ม) | 21 | PWM output - ควบคุมปั๊มไทเทรชัน |
| **TFT Display (SPI Bus 1)** | | |
| TFT SCK | 14 | SPI Clock |
| TFT MOSI | 13 | SPI Data |
| TFT DC | 27 | Data/Command |
| TFT CS | 15 | Chip Select |
| TFT RST | 0 | Reset |
| **SD Card (SoftSPI)** | | |
| SD MISO | 19 | SPI Data In |
| SD MOSI | 23 | SPI Data Out |
| SD SCK | 18 | SPI Clock |
| SD CS | 5 | Chip Select |

> **หมายเหตุสำคัญ**: GPIO 34, 35, 39 เป็นขา input-only ไม่สามารถใช้ internal pull-up/pull-down ได้ บอร์ด TitraLab ใช้ external pull-down resistor

---

## พื้นฐาน ADC, PWM และ DAC (ADC, PWM, and DAC Basics)

ส่วนนี้อธิบายแนวคิดพื้นฐานของ ADC, PWM และ DAC ที่จำเป็นสำหรับการทำงานกับเซ็นเซอร์และอุปกรณ์ควบคุมในระบบ TitraLab การเข้าใจแนวคิดเหล่านี้จะช่วยให้นิสิตเตรียมพร้อมสำหรับสัปดาห์ที่ 2 ที่จะใช้งานเซ็นเซอร์ pH และควบคุมปั๊ม

This section explains the fundamentals of ADC, PWM, and DAC essential for working with sensors and actuators in the TitraLab system. Understanding these concepts prepares students for Week 2 where pH sensor and pump control are implemented.

---

### ADC คืออะไร? (What is ADC?)

**ADC (Analog-to-Digital Converter / ตัวแปลงสัญญาณแอนะล็อกเป็นดิจิทัล)** คืออุปกรณ์ที่แปลงสัญญาณแอนะล็อก (แรงดันไฟฟ้าต่อเนื่อง) เป็นสัญญาณดิจิทัล (ตัวเลข) ที่ไมโครคอนโทรลเลอร์สามารถประมวลผลได้

ADC (Analog-to-Digital Converter) converts continuous analog voltage signals into digital numbers that a microcontroller can process.

#### คุณสมบัติ ADC ของ ESP32 (ESP32 ADC Specifications)

| คุณสมบัติ (Property) | ค่า (Value) | คำอธิบาย (Description) |
|----------------------|-------------|------------------------|
| ความละเอียด (Resolution) | 12-bit | ค่าที่อ่านได้อยู่ในช่วง 0-4095 |
| ช่วงแรงดัน (Voltage Range) | 0-3.3V | ที่ ATTN_11DB (attenuation 11dB) |
| ขา ADC1 | GPIO 32-39 | ใช้งานได้ตลอดเวลา |
| ขา ADC2 | GPIO 0,2,4,12-15,25-27 | ใช้ไม่ได้เมื่อ WiFi ทำงาน |

#### สูตรการแปลงค่า ADC เป็นแรงดันไฟฟ้า (ADC to Voltage Conversion Formula)

```
แรงดัน (V) = (ค่า ADC / 4095) x 3.3V
Voltage (V) = (ADC value / 4095) x 3.3V
```

**ตัวอย่าง**: ถ้าอ่านค่า ADC ได้ 2048 (ครึ่งหนึ่งของ 4095)
- แรงดัน = (2048 / 4095) x 3.3V = 1.65V (ครึ่งหนึ่งของ 3.3V)

#### เชื่อมโยงกับเคมี: เซ็นเซอร์ pH (Chemistry Connection: pH Sensor)

เซ็นเซอร์ pH ของ TitraLab เชื่อมต่อที่ GPIO25 และส่งออกแรงดันไฟฟ้าตามค่า pH ของสารละลาย โดยอิงตาม**สมการ Nernst**:

The TitraLab pH sensor connects to GPIO25 and outputs voltage proportional to the solution's pH, based on the **Nernst equation**:

```
E = E0 - (2.303RT/nF) x pH
```

ที่อุณหภูมิ 25C: **slope = -59.16 mV ต่อหน่วย pH**

At 25C: **slope = -59.16 mV per pH unit**

| ค่า pH | แรงดันโดยประมาณ (mV) | คำอธิบาย |
|--------|----------------------|----------|
| 4.00 | ~177 mV above neutral | กรด (Acidic) |
| 7.00 | ~0 mV (neutral point) | กลาง (Neutral) |
| 10.00 | ~-177 mV below neutral | เบส (Basic) |

#### ตัวอย่างโค้ด ADC (ADC Code Example)

```python
from machine import Pin, ADC

# สร้าง ADC object ที่ GPIO32 (Potentiometer)
# Create ADC object on GPIO32 (Potentiometer)
adc = ADC(Pin(32))

# ตั้งค่า attenuation เป็น 11dB สำหรับอ่าน 0-3.3V
# Set attenuation to 11dB for 0-3.3V range
adc.atten(ADC.ATTN_11DB)

# อ่านค่าดิบ (0-4095) (Read raw value)
raw_value = adc.read()

# แปลงเป็นแรงดันไฟฟ้า (Convert to voltage)
voltage = (raw_value / 4095) * 3.3

print(f"ค่า ADC (ADC Value): {raw_value}")
print(f"แรงดัน (Voltage): {voltage:.3f} V")
```

---

### PWM คืออะไร? (What is PWM?)

**PWM (Pulse Width Modulation / การมอดูเลตความกว้างพัลส์)** คือเทคนิคการสร้างสัญญาณดิจิทัลที่สลับระหว่าง HIGH และ LOW อย่างรวดเร็ว โดยควบคุม "ความกว้าง" ของพัลส์ HIGH เพื่อจำลองสัญญาณแอนะล็อก

PWM (Pulse Width Modulation) creates a digital signal that rapidly switches between HIGH and LOW, controlling the "width" of HIGH pulses to simulate analog output.

#### แนวคิด Duty Cycle (Duty Cycle Concept)

**Duty Cycle** คือสัดส่วนเวลาที่สัญญาณอยู่ที่ HIGH ต่อหนึ่งรอบ วัดเป็นเปอร์เซ็นต์:

Duty Cycle is the proportion of time the signal stays HIGH per cycle, measured as percentage:

```
สัญญาณ PWM (PWM Signal):
                     _____       _____       _____
25% Duty Cycle:  ___|     |_____|     |_____|     |_____
                     _________   _________   _________
50% Duty Cycle:  ___|         |_|         |_|         |_
                     _____________   ___________   _____
75% Duty Cycle:  ___|             |_|           |_|
                     _______________________________________________
100% Duty Cycle: ___|
```

#### คุณสมบัติ PWM ของ ESP32 (ESP32 PWM Specifications)

| คุณสมบัติ (Property) | ค่า (Value) | คำอธิบาย (Description) |
|----------------------|-------------|------------------------|
| ความละเอียด (Resolution) | 10-bit | ค่า duty อยู่ในช่วง 0-1023 |
| ช่วงความถี่ (Frequency Range) | 1 Hz - 40 MHz | ปรับได้ตามต้องการ |
| Duty 0% | duty = 0 | ปิดสนิท (OFF) |
| Duty 100% | duty = 1023 | เปิดเต็มที่ (Full ON) |

#### สูตรการแปลง Duty Cycle (Duty Cycle Conversion Formula)

```
ค่า duty (0-1023) = (เปอร์เซ็นต์ / 100) x 1023
duty value (0-1023) = (percentage / 100) x 1023
```

**ตัวอย่าง**: ต้องการ 50% duty cycle
- ค่า duty = (50 / 100) x 1023 = 511 (หรือ 512)

#### เชื่อมโยงกับเคมี: ควบคุมปั๊ม (Chemistry Connection: Pump Control)

ปั๊มไทเทรชันของ TitraLab เชื่อมต่อที่ GPIO21 และควบคุมด้วย PWM เพื่อปรับอัตราการไหลของสารไทแทรนต์ (titrant):

The TitraLab titration pump connects to GPIO21 and uses PWM to control the flow rate of titrant:

| Duty Cycle | ความเร็วปั๊ม (Pump Speed) | การใช้งาน (Application) |
|------------|---------------------------|------------------------|
| 0% | หยุด (Stopped) | ไม่หยดสาร |
| 25% | ช้า (Slow) | ใกล้จุดสมมูล (near equivalence point) |
| 50% | ปานกลาง (Medium) | ช่วงกลางการไทเทรต |
| 100% | เร็ว (Fast) | ช่วงเริ่มต้น (initial stage) |

**สำคัญ**: เมื่อใกล้ถึงจุดสมมูล (equivalence point) ต้องลด duty cycle เพื่อหยดสารช้าลง จะได้ค่า pH ที่แม่นยำ

#### ตัวอย่างโค้ด PWM (PWM Code Example)

```python
from machine import Pin, PWM
import time

# สร้าง PWM object ที่ GPIO2 (LED สีแดง)
# Create PWM object on GPIO2 (Red LED)
led = PWM(Pin(2), freq=500)

# ค่อยๆ เพิ่มความสว่าง (Fade in)
for duty in range(0, 1024, 10):
    led.duty(duty)
    time.sleep(0.01)

# ค่อยๆ ลดความสว่าง (Fade out)
for duty in range(1023, -1, -10):
    led.duty(duty)
    time.sleep(0.01)

# สำคัญ: คืนทรัพยากร PWM เมื่อเลิกใช้
# Important: Release PWM resources when done
led.duty(0)
led.deinit()
```

---

### DAC คืออะไร? (What is DAC?) [เนื้อหาเสริม/Optional]

**DAC (Digital-to-Analog Converter / ตัวแปลงสัญญาณดิจิทัลเป็นแอนะล็อก)** คืออุปกรณ์ที่ทำงานตรงข้ามกับ ADC โดยแปลงค่าตัวเลขดิจิทัลเป็นแรงดันไฟฟ้าแอนะล็อก

DAC (Digital-to-Analog Converter) works opposite to ADC, converting digital numbers to analog voltage output.

#### คุณสมบัติ DAC ของ ESP32 (ESP32 DAC Specifications)

| คุณสมบัติ (Property) | ค่า (Value) | คำอธิบาย (Description) |
|----------------------|-------------|------------------------|
| ความละเอียด (Resolution) | 8-bit | ค่าที่กำหนดได้อยู่ในช่วง 0-255 |
| ช่วงแรงดัน (Voltage Range) | 0-3.3V | แรงดันเอาต์พุต |
| ขา DAC | GPIO 25, GPIO 26 | ESP32 มี DAC 2 ช่อง |

#### เปรียบเทียบ ADC, PWM และ DAC (Comparing ADC, PWM, and DAC)

| แนวคิด (Concept) | ทิศทาง (Direction) | ความละเอียด (Resolution) | การใช้งาน (Use Case) |
|------------------|-------------------|--------------------------|---------------------|
| **ADC** | Analog -> Digital | 12-bit (0-4095) | อ่านค่าเซ็นเซอร์ pH, Potentiometer |
| **PWM** | Digital -> "Analog" | 10-bit (0-1023) | ควบคุมความสว่าง LED, ความเร็วปั๊ม |
| **DAC** | Digital -> Analog | 8-bit (0-255) | สร้างแรงดันอ้างอิง, สัญญาณเสียง |

> **หมายเหตุ**: PWM ไม่ใช่ analog จริง แต่สัญญาณที่สลับเร็วๆ ทำให้ "ดูเหมือน" analog เมื่อใช้กับอุปกรณ์บางชนิด (เช่น LED, มอเตอร์)

#### ตัวอย่างโค้ด DAC (DAC Code Example)

```python
from machine import Pin, DAC

# สร้าง DAC object ที่ GPIO26
# Create DAC object on GPIO26
dac = DAC(Pin(26))

# กำหนดค่าแรงดันเอาต์พุต
# Set output voltage
# 0 = 0V, 128 = 1.65V, 255 = 3.3V
dac.write(128)  # ประมาณ 1.65V

# สร้างสัญญาณคลื่นซายน์อย่างง่าย (Simple sine wave)
import math
import time

for i in range(360):
    value = int(127.5 + 127.5 * math.sin(math.radians(i)))
    dac.write(value)
    time.sleep_ms(5)
```

---

## เชื่อมต่อกับสัปดาห์ที่ 2: การประยุกต์ใช้ ADC และ PWM (Connection to Week 2: ADC and PWM Applications)

ในสัปดาห์ที่ 2 นิสิตจะนำความรู้พื้นฐาน ADC และ PWM ไปประยุกต์ใช้กับการควบคุมระบบ TitraLab จริง:

In Week 2, students will apply ADC and PWM fundamentals to control the actual TitraLab system:

### ADC -> เซ็นเซอร์ pH (ADC -> pH Sensor)

```
[สารละลาย]  ->  [เซ็นเซอร์ pH]  ->  [ADC GPIO25]  ->  [คำนวณ pH]
[Solution]  ->  [pH Sensor]     ->  [ADC GPIO25]  ->  [Calculate pH]

สมการแปลงค่า (Conversion Equation):
pH = slope x voltage + intercept

โดย slope และ intercept ได้จากการสอบเทียบ (calibration)
ด้วยสารละลายกันชนมาตรฐาน (standard buffer solutions)
```

**คลาส PHSensor ในสัปดาห์ที่ 2:**
- `read_voltage()` - อ่านแรงดันจาก ADC และกรองสัญญาณรบกวน
- `read_ph()` - แปลงแรงดันเป็นค่า pH ด้วยสมการสอบเทียบ
- `calibrate()` - สอบเทียบเซ็นเซอร์ด้วยสารละลายกันชน pH 4.00 และ 7.00

### PWM -> ปั๊มไทเทรชัน (PWM -> Titration Pump)

```
[คำสั่งควบคุม]  ->  [PWM GPIO21]  ->  [ปั๊ม]  ->  [สารไทแทรนต์]
[Control Command]  ->  [PWM GPIO21]  ->  [Pump]  ->  [Titrant]

การคำนวณปริมาตร (Volume Calculation):
volume (mL) = flow_rate (mL/s) x time (s) x (duty_cycle / 100)
```

**คลาส Pump ในสัปดาห์ที่ 2:**
- `start(duty_percent)` - เริ่มปั๊มที่ความเร็วที่กำหนด
- `stop()` - หยุดปั๊มและคืนค่าเวลา/ปริมาตรที่หยด
- `run_for_volume(mL)` - หยดสารตามปริมาตรที่กำหนด

### ตัวอย่างลูปการไทเทรตอัตโนมัติ (Automated Titration Loop Example)

```python
# ตัวอย่างแนวคิด (Conceptual example)
# โค้ดเต็มจะเรียนในสัปดาห์ที่ 2-3

while True:
    # อ่านค่า pH ด้วย ADC
    ph = ph_sensor.read_ph()

    # ตรวจสอบจุดสมมูล
    if detect_equivalence_point(ph):
        pump.stop()
        break

    # ปรับความเร็วปั๊มตามค่า pH
    if abs(ph - target_ph) < 0.5:
        pump.set_duty(25)   # ช้า - ใกล้จุดสมมูล
    else:
        pump.set_duty(100)  # เร็ว - ห่างจากจุดสมมูล
```

---

## อ้างอิง OOP สำหรับ TitraLab (OOP Reference for TitraLab)

### นิยาม Class (Class Definition)

```python
class ClassName:
    """Class = พิมพ์เขียว (Blueprint) สำหรับสร้าง Object"""

    def __init__(self, parameter):
        """
        Constructor (ตัวสร้าง) - ทำงานอัตโนมัติเมื่อสร้าง object
        ใช้กำหนดค่าเริ่มต้นให้กับ object
        """
        self.attribute = parameter  # Instance variable (ตัวแปรของ object)

    def method_name(self):
        """Method (เมธอด) = ฟังก์ชันที่อยู่ใน class"""
        return self.attribute
```

### ทำความเข้าใจ self (Understanding `self`)

**`self`** = ตัวอ้างอิงถึง object ปัจจุบัน (reference to current object)

- `self.pin_number` หมายถึง `pin_number` ของ object นี้โดยเฉพาะ
- เมื่อมี LED 2 ดวง แต่ละดวงมี `self.pin_number` ของตัวเอง (เหมือนบีกเกอร์ 2 ใบ แต่ละใบมีปริมาตรของตัวเอง)

### สร้างและใช้งาน Object (Creating & Using Objects)

```python
# Class = พิมพ์เขียว, Object = สิ่งที่สร้างจากพิมพ์เขียว (Instance)
led_red = LED(2, "Red")      # Object ที่ 1 - LED สีแดงที่ GPIO2
led_green = LED(4, "Green")  # Object ที่ 2 - LED สีเขียวที่ GPIO4

led_red.on()    # เรียก method ของ object led_red
led_green.off() # เรียก method ของ object led_green
```

### ตัวอย่างคลาส LED (LED Class Example)

โค้ดด้านล่างแสดงการสร้างคลาส LED สำหรับควบคุมไฟ LED ซึ่งใช้แสดงสถานะการไทเทรต เช่น สีเขียว = กำลังทำงาน, สีแดง = ถึงจุดสมมูล (equivalence point)

```python
from machine import Pin
import time

class LED:
    """คลาสควบคุม LED (LED Control Class)"""

    def __init__(self, pin_number, name="LED"):
        """สร้าง LED object (Create LED object)"""
        self.pin_number = pin_number
        self.name = name
        self.is_on = False
        # สร้าง Pin เป็น OUTPUT (Create Pin as OUTPUT)
        self._pin = Pin(pin_number, Pin.OUT)
        self._pin.value(0)  # เริ่มต้นปิด (Start off)

    def on(self):
        """เปิด LED (Turn LED on)"""
        self._pin.value(1)
        self.is_on = True

    def off(self):
        """ปิด LED (Turn LED off)"""
        self._pin.value(0)
        self.is_on = False

    def toggle(self):
        """สลับสถานะ (Toggle state)"""
        if self.is_on:
            self.off()
        else:
            self.on()

    def blink(self, times=1, delay_sec=0.3):
        """กระพริบ LED (Blink LED)"""
        for _ in range(times):
            self._pin.value(1)
            time.sleep(delay_sec)
            self._pin.value(0)
            time.sleep(delay_sec)
```

### ตัวอย่างคลาส Button (Button Class Example)

คลาส Button ใช้อ่านสถานะปุ่มกดพร้อม debounce (การกำจัดสัญญาณรบกวนจากการกดปุ่ม) ปุ่มกดบนบอร์ด TitraLab ใช้สำหรับ:
- Button 1 (GPIO34): เริ่ม/หยุดการไทเทรต
- Button 2 (GPIO35): ยืนยันการสอบเทียบ (calibration)
- Button 3 (GPIO39): ยกเลิก/ออก

```python
from machine import Pin
import time

class Button:
    """คลาสอ่านปุ่มกดพร้อม Debounce (Button class with debounce)"""

    def __init__(self, pin_number, name="Button", debounce_ms=200):
        """สร้าง Button (Create Button object)"""
        self.pin_number = pin_number
        self.name = name
        self.debounce_ms = debounce_ms
        self._pin = Pin(pin_number, Pin.IN)
        self._last_press_time = 0
        self._was_pressed = False

    def is_active(self):
        """ตรวจสอบว่ากดอยู่ (Check if currently pressed)"""
        return self._pin.value() == 1

    def is_pressed(self):
        """
        ตรวจจับการกดใหม่พร้อม debounce
        Returns True only ONCE per press (คืนค่า True แค่ครั้งเดียวต่อการกด)
        """
        current_time = time.ticks_ms()
        is_active_now = self.is_active()

        if is_active_now and not self._was_pressed:
            if time.ticks_diff(current_time, self._last_press_time) > self.debounce_ms:
                self._last_press_time = current_time
                self._was_pressed = True
                return True

        if not is_active_now:
            self._was_pressed = False
        return False
```

### ตัวอย่างคลาส TemperatureSensor - เชื่อมโยงกับเคมี (Chemistry Connection)

คลาส TemperatureSensor ไม่เพียงแค่อ่านค่าอุณหภูมิ แต่ยังสามารถแปลงหน่วยเป็น Kelvin และคำนวณค่าที่ใช้ในสมการ Nernst ได้ ซึ่งเป็นสมการสำคัญในการคำนวณค่า pH จากแรงดันไฟฟ้า:

**สมการ Nernst**: E = E0 - (2.303RT/nF) x pH

ที่อุณหภูมิ 25 C ค่า 2.303RT/nF = 59.16 mV ต่อหน่วย pH

```python
class TemperatureSensor:
    """เซ็นเซอร์อุณหภูมิพร้อมการคำนวณทางเคมี"""

    R_JOULES = 8.314   # ค่าคงที่ของก๊าซ (J/(mol*K))
    FARADAY = 96485    # ค่าคงที่ฟาราเดย์ (C/mol)

    def read_kelvin(self):
        """
        อ่านอุณหภูมิในหน่วย Kelvin
        ใช้ในสมการ Nernst: E = E0 - (RT/nF)ln(Q)
        """
        celsius = self.read_celsius()
        return celsius + 273.15

    def get_nernst_factor(self, n=1):
        """
        คำนวณ 2.303RT/nF ที่อุณหภูมิปัจจุบัน
        ค่านี้คือ mV ต่อหน่วย pH (ประมาณ 59.16 mV ที่ 25 C)
        """
        T = self.read_kelvin()
        return (2.303 * self.R_JOULES * T) / (n * self.FARADAY)
```

---

## เชื่อมโยงการเขียนโปรแกรมกับเคมี (Programming-Chemistry Connection)

การเรียนรู้ OOP ผ่านบอร์ด TitraLab ช่วยให้นิสิตเห็นความเชื่อมโยงระหว่างแนวคิดการเขียนโปรแกรมกับการประยุกต์ใช้ทางเคมี:

| แนวคิดการเขียนโปรแกรม (Programming Concept) | การประยุกต์ใช้ทางเคมี (Chemistry Application) |
|---------------------------------------------|----------------------------------------------|
| **Class และ Object** | เหมือนพิมพ์เขียว "บีกเกอร์" กับ บีกเกอร์จริงหลายใบ |
| **Class LED** | แสดงสถานะการไทเทรต (เขียว = กำลังหยดสาร, แดง = ถึงจุดสมมูล) |
| **Class Button** | ควบคุมการเริ่ม/หยุดการหยดสาร, ยืนยันการสอบเทียบ |
| **Class TemperatureSensor** | ชดเชยอุณหภูมิในสมการ Nernst: E = E0 - (2.303RT/nF) x pH |
| **Class pHSensor** (Week 2) | อ่านค่า mV และแปลงเป็น pH ด้วยเส้นสอบเทียบ |
| **Class Pump** (Week 2) | ควบคุมการหยดสารไทแทรนต์ด้วย PWM |
| **TFT Display** | แสดง pH, อุณหภูมิ, กราฟไทเทรชัน (titration curve) |
| **Loop/ลูป** | วัด pH ซ้ำๆ ทุกวินาทีจนถึงจุดสมมูล |
| **Conditional/เงื่อนไข** | ตรวจจับจุดสมมูล (equivalence point) จากการเปลี่ยนแปลง pH อย่างรวดเร็ว |

---

## สื่อศึกษาเพิ่มเติม (Self-Study Materials)

**ไฟล์หลักสำหรับการสอน (Core Teaching Files):**
| ไฟล์ | คำอธิบาย | บทบาทในการไทเทรต |
|------|----------|------------------|
| `core/01_led_class.py` | คลาส LED | แสดงสถานะ: เขียว = กำลังทำงาน, แดง = ถึงจุดสมมูล |
| `core/02_button_class.py` | คลาส Button พร้อม debounce | ควบคุมการเริ่ม/หยุด/ยืนยัน |
| `core/06_temp_sensor_class.py` | คลาส TemperatureSensor | ชดเชยอุณหภูมิในสมการ Nernst |
| `core/07_display_basics.py` | พื้นฐานจอ TFT | แสดง pH, กราฟ, เมนู |
| `core/08_intro_oop.py` | บทนำ OOP (คลาส Beaker) | เข้าใจ Class/Object |
| `core/09_combined_example.py` | ตัวอย่างรวม Lab Alert | รวมทุก concept |

**ไฟล์สำคัญ: ADC และ PWM (Important: ADC and PWM):**
| ไฟล์ | คำอธิบาย | เตรียมพร้อมสำหรับ |
|------|----------|------------------|
| `core/03_adc_ph_basics.py` | ADC 0-4095, สมการ Nernst | เซ็นเซอร์ pH ใน Week 2-3 |
| `core/04_pwm_pump_basics.py` | PWM Duty cycle, กลยุทธ์ไทเทรชัน | ควบคุมปั๊มใน Week 3 |
| `core/05_pot_led_dimming.py` | ADC+PWM รวมกัน, value mapping | pH → Pump control loop |

**ไฟล์เสริม (Supplementary Files):**
| โฟลเดอร์ | คำอธิบาย |
|----------|----------|
| `extras/01_procedural/` | ตัวอย่างแบบ Procedural (ไม่ใช้ OOP) - เปรียบเทียบกับ OOP |
| `extras/02_advanced_oop/` | ตัวอย่าง OOP ขั้นสูง - หลาย object, Buzzer class |
| `extras/03_exercises/` | แบบฝึกหัดพร้อมเฉลย (starter และ solution) |
| `extras/04_hardware/DS18B20/` | ตัวอย่างเซ็นเซอร์อุณหภูมิเพิ่มเติม |
| `extras/04_hardware/TFT/` | ตัวอย่างจอ TFT เพิ่มเติม |
| `extras/04_hardware/Buzzer/` | ตัวอย่าง Buzzer - แจ้งเตือนจุดสมมูล |
| `extras/04_hardware/SDCard/` | ตัวอย่าง SD Card - บันทึกข้อมูลการไทเทรต |
| `extras/04_hardware/DAC/` | [เสริม] พื้นฐาน DAC |
| `extras/05_reference/` | เอกสารอ้างอิง - อธิบาย self, common mistakes |
| `extras/archive/07_ADC/` | [เก็บถาวร] ตัวอย่าง ADC แบบละเอียด |
| `extras/archive/07_PWM/` | [เก็บถาวร] ตัวอย่าง PWM แบบละเอียด |

---

## สรุปการเชื่อมต่อ Week 1 ไป Week 2 และ Week 3 (Summary: Week 1 to Week 2-3 Connections)

ในสัปดาห์ที่ 2 นิสิตจะนำความรู้จาก Week 1 ไปใช้ในการ **สอบเทียบ (Calibration)**:

### Week 1 -> Week 2: การสอบเทียบ (Calibration)

| Week 1 (พื้นฐาน) | Week 2 (การประยุกต์ใช้) |
|------------------|------------------------|
| ADC: อ่านค่า 0-4095 จาก Potentiometer | **สอบเทียบ pH**: อ่านค่าจากเซ็นเซอร์ pH, สร้างสมการถดถอย |
| PWM: ควบคุม LED ด้วย duty cycle | **สอบเทียบปั๊ม**: หา flow rate จริง, ตรวจสอบ %RSD |
| เซ็นเซอร์อุณหภูมิ: อ่านค่า °C, K | ชดเชยอุณหภูมิในสมการ Nernst |
| OOP: Class และ Object พื้นฐาน | OOP ขั้นกลาง: Inheritance, Composition |

### การสอบเทียบ pH (pH Calibration)
```
Week 1: ADC basics (0-4095)
   ↓
Week 2: สอบเทียบด้วยสารละลายกันชน pH 4, 7, 10
   ↓
ผลลัพธ์: slope, intercept, R-squared ≥ 0.99
```

### การสอบเทียบปั๊ม (Pump Calibration)
```
Week 1: PWM basics (duty cycle)
   ↓
Week 2: วัด flow rate 3-5 ครั้ง, คำนวณ %RSD
   ↓
ผลลัพธ์: flow_rate (mL/s), %RSD < 5%
```

> **หมายเหตุ**: ดูรายละเอียดทางเทคนิคเพิ่มเติมที่หัวข้อ "เชื่อมต่อกับสัปดาห์ที่ 2: การประยุกต์ใช้ ADC และ PWM" ด้านบน (หลังหัวข้อ DAC)

### Week 1 -> Week 3: ระบบเต็มรูปแบบ (Full System)

ในสัปดาห์ที่ 3 นิสิตจะรวมทุกสิ่งที่เรียนมาเพื่อสร้าง **ระบบไทเทรตอัตโนมัติแบบสมบูรณ์**:

In Week 3, students integrate all knowledge to build a **complete automated titration system**:

### โครงสร้างระบบ Week 3 (Week 3 System Architecture)

```
Week_3/
├── main.py                 # จุดเริ่มต้นโปรแกรม
├── config.py               # ค่าคงที่ระบบ (GPIO pins, etc.)
├── hardware/               # Hardware abstraction layer
│   ├── ph_sensor.py        # คลาส PHSensor (ADC จาก Week 1)
│   ├── pump.py             # คลาส Pump (PWM จาก Week 1)
│   ├── temp_sensor.py      # คลาส TempSensor (DS18B20)
│   └── display.py          # คลาส Display (TFT)
├── core/                   # Business logic
│   ├── titration.py        # ลูปไทเทรตอัตโนมัติ
│   ├── calibrator.py       # สอบเทียบ pH และ flow rate
│   └── data_manager.py     # บันทึกข้อมูลลง SD Card
├── modes/                  # โหมดการทำงาน (State pattern)
│   ├── mode_titration.py   # โหมดไทเทรต
│   └── mode_calibrate_*.py # โหมดสอบเทียบ
└── ui/                     # User interface
    └── menu.py             # ระบบเมนู
```

### การนำความรู้ Week 1 ไปใช้ใน Week 3 (Week 1 Knowledge in Week 3)

| Week 1 (พื้นฐาน) | Week 3 (ระบบเต็มรูปแบบ) |
|------------------|------------------------|
| LED Class | `hardware/leds.py` - แสดงสถานะระบบ |
| Button Class | `hardware/buttons.py` - ควบคุมเมนู/การไทเทรต |
| ADC Basics | `hardware/ph_sensor.py` - อ่านและแปลงค่า pH |
| PWM Basics | `hardware/pump.py` - ควบคุมปั๊มอัตโนมัติ |
| TFT Display | `hardware/display.py` - แสดงผลและกราฟ |
| OOP (Class/Object) | ทุกโมดูลใช้ OOP - Hardware Abstraction |

---

## เริ่มต้นเร็ว (Quick Start)

โค้ดนี้สรุปขั้นตอนหลักของ OOP ใน 4 ขั้นตอน: Import > Define Class > Create Object > Use Object

```python
# 1. Import - นำเข้าโมดูลที่จำเป็น
from machine import Pin
import time

# 2. Define Class - กำหนดคลาส (พิมพ์เขียว)
class LED:
    def __init__(self, pin):
        """Constructor - ทำงานเมื่อสร้าง object"""
        self._pin = Pin(pin, Pin.OUT)

    def on(self):
        """เปิด LED"""
        self._pin.value(1)

    def off(self):
        """ปิด LED"""
        self._pin.value(0)

# 3. Create Object - สร้าง object จากคลาส
led = LED(2)  # LED สีแดงที่ GPIO2

# 4. Use Object - ใช้งาน object
try:
    led.on()
    time.sleep(1)
    led.off()
except KeyboardInterrupt:
    print("\nหยุดโปรแกรม (Program stopped)")
finally:
    led.off()  # ปิด LED เมื่อจบโปรแกรม
```

---

## คำศัพท์สำคัญ (Key Terminology)

### คำศัพท์ OOP (OOP Terms)

| ภาษาอังกฤษ (English) | ภาษาไทย (Thai) | คำอธิบาย |
|----------------------|----------------|----------|
| Class | คลาส | พิมพ์เขียวสำหรับสร้าง object |
| Object | ออบเจกต์ | สิ่งที่สร้างจากคลาส (instance) |
| Constructor | ตัวสร้าง | method `__init__` ที่ทำงานเมื่อสร้าง object |
| Method | เมธอด | ฟังก์ชันที่อยู่ใน class |
| Attribute | แอตทริบิวต์ | ตัวแปรที่อยู่ใน class |
| self | ตัวเอง | ตัวอ้างอิงถึง object ปัจจุบัน |

### คำศัพท์ฮาร์ดแวร์ (Hardware Terms)

| ภาษาอังกฤษ (English) | ภาษาไทย (Thai) | คำอธิบาย |
|----------------------|----------------|----------|
| GPIO | จีพีไอโอ | General Purpose Input/Output - ขาอเนกประสงค์ |
| ADC | เอดีซี | Analog-to-Digital Converter - ตัวแปลงสัญญาณแอนะล็อกเป็นดิจิทัล (12-bit, 0-4095) |
| PWM | พีดับเบิลยูเอ็ม | Pulse Width Modulation - การมอดูเลตความกว้างพัลส์ (10-bit, 0-1023) |
| DAC | ดีเอซี | Digital-to-Analog Converter - ตัวแปลงสัญญาณดิจิทัลเป็นแอนะล็อก (8-bit, 0-255) |
| Duty Cycle | ดิวตี้ไซเคิล | สัดส่วนเวลาที่สัญญาณอยู่ที่ HIGH (0-100%) |
| Attenuation | แอทเทนูเอชัน | การลดทอนสัญญาณ (ใช้ตั้งค่าช่วงแรงดัน ADC) |
| Debounce | ดีเบาซ์ | การกำจัดสัญญาณรบกวนจากปุ่มกด |

### คำศัพท์เคมี (Chemistry Terms)

| ภาษาอังกฤษ (English) | ภาษาไทย (Thai) | คำอธิบาย |
|----------------------|----------------|----------|
| pH | พีเอช | ค่าความเป็นกรด-เบส (-log[H+]) |
| Titration | ไทเทรชัน | การไทเทรต - การหาปริมาณสารด้วยการเติมสารไทแทรนต์ |
| Titrant | สารไทแทรนต์ | สารละลายที่ใช้หยดลงไป (เช่น NaOH) |
| Analyte | สารตัวอย่าง | สารละลายที่ต้องการวิเคราะห์ (เช่น HCl) |
| Equivalence Point | จุดสมมูล | จุดที่สารทำปฏิกิริยาพอดีกัน (pH เปลี่ยนเร็วมาก) |
| Endpoint | จุดยุติ | จุดที่ตรวจวัดได้จริง (อาจต่างจากจุดสมมูลเล็กน้อย) |
| Buffer Solution | สารละลายกันชน | สารละลายที่มี pH คงที่ ใช้สอบเทียบเซ็นเซอร์ |
| Calibration | การสอบเทียบ | การปรับค่าเซ็นเซอร์ให้อ่านค่าถูกต้อง |
| Nernst Equation | สมการเนิร์นสต์ | สมการความสัมพันธ์ระหว่างแรงดันไฟฟ้ากับ pH |
| Slope | ความชัน | ค่า mV/pH จากการสอบเทียบ (ประมาณ -59.16 mV/pH ที่ 25C) |
| Intercept | จุดตัดแกน | ค่าคงที่จากการสอบเทียบ |

---

*TitraLab - 2302311 Integrated Chemistry Laboratory I*
*ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย*
*Department of Chemistry, Faculty of Science, Chulalongkorn University*

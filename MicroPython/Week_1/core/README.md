# Week 1 Core: TitraLab Hardware & OOP Fundamentals

## ภาพรวม (Overview)

โฟลเดอร์ `core/` ประกอบด้วยไฟล์สอนหลักสำหรับสัปดาห์ที่ 1 ออกแบบเป็นคาบเรียน 3 ชั่วโมงที่เชื่อมโยงกับระบบไทเทรชันอัตโนมัติใน Week 3

This `core/` folder contains core teaching files for Week 1, designed as a 3-hour session that connects to the automated titration system in Week 3.

---

## ตารางสอน 3 ชั่วโมง (3-Hour Teaching Schedule)

| ชั่วโมง | ไฟล์ | หัวข้อหลัก | เชื่อมโยง Week 3 |
|--------|------|-----------|-----------------|
| **Hour 1** | 01-02 | GPIO Input/Output | LED status, Button control |
| **Hour 2** | 03-06 | ADC, PWM, Temperature | pH sensor, Pump, Nernst |
| **Hour 3** | 07-09 | Display, OOP, Integration | Full titration UI |

**ระยะเวลารวม (Total Duration):** ~3 ชั่วโมง (สามารถปรับตามความเหมาะสม)

---

## Hour 1: GPIO Basics (ชั่วโมงที่ 1: พื้นฐาน GPIO)

สอนการควบคุม LED และปุ่มกดซึ่งเป็นหัวใจของ user interface ในระบบไทเทรชัน

### `01_led_class.py` - LED Status Display (~30 min)

**แนวคิด OOP (OOP Concepts):**
- Class และ Object พื้นฐาน
- Encapsulation: ซ่อน `_pin` ภายในคลาส
- Methods: `on()`, `off()`, `toggle()`, `blink()`

**Pin Configuration:**
| LED | GPIO | การใช้งานใน Week 3 |
|-----|------|-------------------|
| Red | GPIO2 | ถึงจุดสมมูล/Error |
| Green | GPIO4 | ปั๊มกำลังทำงาน |

**เชื่อมโยงเคมี:** LED แสดงสถานะระบบไทเทรชัน - เขียวติด = หยดสาร, แดงติด = ถึง endpoint

---

### `02_button_class.py` - Button Control (~30 min)

**แนวคิด OOP (OOP Concepts):**
- State management: `_was_pressed`, `_last_press_time`
- Debounce algorithm: ป้องกันการอ่านซ้ำ
- Blocking vs non-blocking: `wait_for_press()` vs `is_pressed()`

**Pin Configuration:**
| Button | GPIO | การใช้งานใน Week 3 |
|--------|------|-------------------|
| Button 1 | GPIO34 | SELECT - เริ่ม/หยุด |
| Button 2 | GPIO35 | UP - เลื่อนเมนู |
| Button 3 | GPIO39 | DOWN - ลดค่า |

**หมายเหตุ:** GPIO34, 35, 39 เป็น input-only ไม่มี internal pull-up

**เชื่อมโยงเคมี:** ปุ่มควบคุมการเริ่ม/หยุดไทเทรชัน และยืนยัน calibration

---

## Hour 2: Sensors & Actuators (ชั่วโมงที่ 2: เซ็นเซอร์และแอคชูเอเตอร์)

สอน ADC สำหรับอ่านค่า pH และ PWM สำหรับควบคุมปั๊ม

### `03_adc_ph_basics.py` - ADC for pH Sensor (~30 min)

**แนวคิดที่สอน (Concepts):**
- ADC 12-bit: แปลง 0-3.3V เป็น 0-4095
- สมการ Nernst: E = E0 - 59.16 mV x pH (ที่ 25C)
- Attenuation: ATTN_11DB สำหรับ 0-3.3V

**Pin Configuration:**
| Component | GPIO | Description |
|-----------|------|-------------|
| Potentiometer | GPIO32 | จำลองสัญญาณ pH (ฝึก) |
| pH Sensor | GPIO32 | ใช้จริงใน Week 3 (ADC1 — ใช้ขาเดียวกับ Potentiometer ทีละอย่าง, ห้ามใช้ GPIO25) |

**เชื่อมโยงเคมี:** pH sensor ส่งแรงดัน analog ตามสมการ Nernst - ต้องใช้ ADC อ่านค่า

---

### `04_pwm_pump_basics.py` - PWM for Pump Control (~30 min)

**แนวคิดที่สอน (Concepts):**
- PWM Duty Cycle: 0-1023 (10-bit)
- ความเร็วปั๊มตาม Phase การไทเทรชัน
- รูปแบบ titration: เร็ว -> กลาง -> ช้า -> หยุด

**รูปแบบความเร็วปั๊ม (Titration Pattern):**
```
Phase 1: ห่างจุดสมมูล  -> 80% (เร็ว)
Phase 2: เข้าใกล้       -> 50% (กลาง)
Phase 3: ใกล้มาก       -> 25% (ช้า-แม่นยำ)
Phase 4: ถึงจุดสมมูล!   -> 0% (หยุด)
```

**Pin:** GPIO21 -> EL357N optocoupler -> MOSFET -> Pump 12V

**เชื่อมโยงเคมี:** ใกล้จุดสมมูล ต้องหยดช้าเพื่อความแม่นยำ

---

### `05_pot_led_dimming.py` - Combined ADC+PWM (~20 min)

**แนวคิดที่สอน (Concepts):**
- รวม ADC (input) + PWM (output)
- Mapping: 0-4095 -> 0-1023
- หลักการเดียวกับ pH -> pump speed

**หลักการ (Principle):**
```
ตัวอย่างนี้:  Potentiometer (ADC) -> LED brightness (PWM)
Week 3:       pH Sensor (ADC)     -> Pump speed (PWM)
```

**เชื่อมโยงเคมี:** อ่านค่า -> ประมวลผล -> ควบคุม output (pattern เดียวกับไทเทรชันอัตโนมัติ)

---

### `06_temp_sensor_class.py` - Temperature for Nernst (~20 min)

**แนวคิดที่สอน (Concepts):**
- OneWire protocol: DS18B20
- สมการ Nernst slope เปลี่ยนตามอุณหภูมิ
- Multiple return formats: Celsius, Kelvin, Fahrenheit

**สมการ Nernst (Nernst Equation):**
```
E = E0 - (2.303 * R * T) / (n * F) * pH

ที่ 25C (298 K): slope = 59.16 mV/pH
ที่ 30C (303 K): slope = 60.15 mV/pH
```

**Pin:** GPIO16 (OneWire, มี pull-up 4.7k บนบอร์ด)

**เชื่อมโยงเคมี:** การวัด pH ที่แม่นยำต้องชดเชยอุณหภูมิตามสมการ Nernst

---

## Hour 3: Display, OOP & Integration (ชั่วโมงที่ 3: จอแสดงผล, OOP และบูรณาการ)

สอนการแสดงผลและรวมทุกส่วนเข้าด้วยกัน

### `07_display_basics.py` - TFT Display (~30 min)

**แนวคิดที่สอน (Concepts):**
- SPI communication: ILI9341 driver
- Color565 format: RGB 16-bit
- Helper functions: `draw_text()`, `draw_value_box()`

**Pin Configuration (SPI1):**
| Function | GPIO |
|----------|------|
| SCK | GPIO14 |
| MOSI | GPIO13 |
| DC | GPIO27 |
| CS | GPIO15 |
| RST | GPIO0 |

**เชื่อมโยงเคมี:** แสดง pH, อุณหภูมิ, ปริมาตร และกราฟไทเทรชันแบบ real-time

---

### `08_intro_oop.py` - OOP with Beaker Class (~30 min)

**แนวคิด OOP (OOP Concepts):**
- Class = Blueprint (พิมพ์เขียว)
- Object = Instance (ตัวอย่างที่สร้างจากคลาส)
- `__init__()` = Constructor
- `self` = Reference ถึง object ปัจจุบัน
- Method = ฟังก์ชันภายในคลาส

**ตัวอย่าง (Example):**
```python
beaker = Beaker(250)           # สร้างบีกเกอร์ 250 mL
beaker.add_liquid(100, "HCl")  # เติม HCl 100 mL
beaker.get_info()              # แสดงข้อมูล
```

**เชื่อมโยงเคมี:** คลาส Beaker จำลองอุปกรณ์ห้องปฏิบัติการ - มี attribute (ความจุ, ปริมาตร) และ method (เติม, เท)

---

### `09_combined_example.py` - Integrated Lab Alert System (~40 min)

**แนวคิด OOP (OOP Concepts):**
- **Composition**: รวมหลาย object (LED + Button + TempSensor + Display)
- State machine: `running` state toggle
- Main loop pattern: event checking + periodic updates
- Graceful cleanup: `cleanup()` method

**ระบบประกอบด้วย (Components):**
```
TitrationMonitor
├── LED (GPIO 2, 4)      - แสดงสถานะ
├── Button (GPIO 34)     - สั่งเริ่ม/หยุด
├── TempSensor (GPIO 16) - วัดอุณหภูมิ
└── Display (SPI1)       - แสดงผล
```

**เชื่อมโยงเคมี:** จำลองระบบติดตามการไทเทรชัน - กดปุ่มเริ่ม/หยุด, แสดงอุณหภูมิ, LED แสดงสถานะ

---

## แบบฝึกหัด (Exercise)

### `ex_status_led.py` - StatusLED Class Exercise (~15 min)

**วัตถุประสงค์:** ให้นิสิตเขียนคลาส `StatusLED` ด้วยตนเอง โดยเติมโค้ดในส่วน `TODO`

**ส่วนที่ต้องเติม:**
1. `__init__()` - สร้าง Pin object
2. `on()` - เปิด LED
3. `off()` - ปิด LED
4. `blink()` - กระพริบ LED
5. `is_on` property - ตรวจสอบสถานะ

---

## เส้นทางการเรียนรู้ (Learning Progression)

```
Hour 1: GPIO Basics
========================
01_led_class.py (30 min)
    |   สร้าง Class, ควบคุม Output
    v
02_button_class.py (30 min)
    |   อ่าน Input, Debounce
    v

Hour 2: Sensors & Actuators
========================
03_adc_ph_basics.py (30 min)
    |   ADC 12-bit, สมการ Nernst
    v
04_pwm_pump_basics.py (30 min)
    |   PWM Duty Cycle, ความเร็วปั๊ม
    v
05_pot_led_dimming.py (20 min)
    |   รวม ADC + PWM (pattern สำหรับ Week 3)
    v
06_temp_sensor_class.py (20 min)
    |   OneWire, ชดเชยอุณหภูมิ
    v

Hour 3: Display, OOP & Integration
========================
07_display_basics.py (30 min)
    |   TFT SPI, แสดง pH
    v
08_intro_oop.py (30 min)
    |   Class/Object ด้วย Beaker
    v
09_combined_example.py (40 min)
    |   Composition, ระบบรวม
    v
ex_status_led.py (15 min)
    |   ฝึกเขียน Class ด้วยตนเอง
    v
[พร้อมสำหรับ Week 3: Titration System]
```

---

## การเชื่อมโยงไปยัง Week 3 (Connection to Week 3)

| Week 1 Concept | Week 3 Application |
|----------------|-------------------|
| LED Class | แสดงสถานะไทเทรชัน (running/endpoint) |
| Button Class | ควบคุมเมนู, เริ่ม/หยุด, calibration |
| ADC (Pot) | อ่านค่าจาก pH Sensor |
| PWM (LED) | ควบคุมความเร็วปั๊ม |
| TempSensor | ชดเชย Nernst slope |
| Display | แสดง pH, volume, กราฟไทเทรชัน |
| Composition | รวมทุกส่วนเป็น TitrationSystem |

---

## สิ่งที่ต้องเตรียม (Prerequisites)

### ไฟล์ Library บน ESP32 (Library Files)
```
ESP32 Root/
├── lib/
│   ├── ili9341.py       # TFT Display driver
│   ├── xglcd_font.py    # Font rendering
│   └── sdcard.py        # SD card driver
├── fonts/
│   ├── EspressoDolce18x24.c  # Large font
│   └── ArcadePix9x11.c       # Small font
└── (your .py files)
```

### ความรู้พื้นฐาน (Background Knowledge)
- **เคมี:** หลักการไทเทรชัน, การวัด pH, สมการ Nernst
- **โปรแกรม:** ไม่จำเป็นต้องมีพื้นฐาน - เริ่มจากศูนย์

---

## Pin Reference (อ้างอิง GPIO)

```
TitraLab Board - Week 1 Core
=============================
LED Red:      GPIO 2   (Output/PWM - 01, 04)
LED Green:    GPIO 4   (Output/PWM - 01, 04)
Button 1-3:   GPIO 34, 35, 39 (Input-only - 02)
DS18B20:      GPIO 16  (OneWire - 06)
Potentiometer: GPIO 32 (ADC - 03, 05)
pH Sensor:    GPIO 32  (ADC1 - Week 3, ใช้ขาเดียวกับ Potentiometer ทีละอย่าง)
Pump:         GPIO 21  (PWM - 04)
TFT:          SPI1 (GPIO 14,13,27,15,0 - 07)
```

---

## การแก้ปัญหาเบื้องต้น (Troubleshooting)

| ปัญหา | สาเหตุ | แก้ไข |
|-------|--------|-------|
| `ImportError: ili9341` | ไม่มี library | อัพโหลด `ili9341.py` ไปที่ `lib/` |
| `RuntimeError: DS18B20 not found` | เซ็นเซอร์ไม่ได้เชื่อมต่อ | ตรวจสอบการต่อที่ GPIO16 |
| จอ TFT ไม่แสดงผล | ไม่มีไฟล์ font | อัพโหลดไฟล์ `.c` ไปที่ `fonts/` |
| ปุ่มกดไม่ตอบสนอง | input-only pins | ตรวจสอบสายไฟ (บอร์ดมี pull-down) |

---

## ผู้จัดทำ (Author)

เอกสารนี้จัดทำสำหรับรายวิชา 2302311 Integrated Chemistry Laboratory I
ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย

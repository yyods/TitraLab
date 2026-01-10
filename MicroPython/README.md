# TitraLab MicroPython Curriculum
# หลักสูตร MicroPython สำหรับ TitraLab

---

> **รายวิชา:** 2302311 Integrated Chemistry Laboratory I
> **ภาควิชา:** เคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย
> **Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## ภาพรวม (Overview)

โฟลเดอร์นี้ประกอบด้วยหลักสูตร MicroPython สำหรับบอร์ด **TitraLab ESP32** ออกแบบมาเพื่อสอนนิสิตเคมีที่ไม่มีพื้นฐานการเขียนโปรแกรม ให้สามารถสร้างระบบไทเทรตกรด-เบสอัตโนมัติได้

This folder contains the MicroPython curriculum for the **TitraLab ESP32** board, designed to teach chemistry students with no programming background to build an automated acid-base titration system.

### กลุ่มเป้าหมาย (Target Audience)

- นิสิตเคมีชั้นปีที่ 2-3 (2nd-3rd year Chemistry undergraduates)
- มีพื้นฐานเคมีวิเคราะห์ ไทเทรชัน สมการ Nernst
- **ไม่ต้องมีพื้นฐานการเขียนโปรแกรมมาก่อน**

---

## เส้นทางการเรียนรู้ 3 สัปดาห์ (3-Week Learning Progression)

```
+===========================================================================+
|                   TitraLab Learning Progression                           |
|                   เส้นทางการเรียนรู้ TitraLab                              |
+===========================================================================+

   Week 1                      Week 2                      Week 3
   สัปดาห์ที่ 1                   สัปดาห์ที่ 2                   สัปดาห์ที่ 3
===========================================================================

 +-------------------+       +-------------------+       +-------------------+
 |    พื้นฐาน         |       |   การสอบเทียบ      |       |   ระบบเต็มรูปแบบ   |
 |   Fundamentals    |       |    Calibration    |       |    Full System    |
 +-------------------+       +-------------------+       +-------------------+
 | - LED, Button     |       | - pH Sensor Cal.  |       | - 6 Operating     |
 | - ADC, PWM        | ----> | - Flow Rate Cal.  | ----> |   Modes           |
 | - DS18B20, TFT    |       | - Inheritance     |       | - Modular OOP     |
 | - OOP พื้นฐาน      |       | - Composition     |       | - Menu System     |
 +-------------------+       +-------------------+       +-------------------+
        |                           |                           |
        v                           v                           v
   3 ชั่วโมง                     3 ชั่วโมง                     3 ชั่วโมง
   3 hours                      3 hours                      3 hours

===========================================================================
ความซับซ้อน:  ง่าย -----------------------------------------> ซับซ้อน
Complexity:   Simple ---------------------------------------> Complex
===========================================================================
```

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

```
MicroPython/
+-- Week_1/              # พื้นฐานฮาร์ดแวร์และ OOP เบื้องต้น
|   +-- core/            # ไฟล์หลักสำหรับการสอน (9 ไฟล์)
|   +-- extras/          # สื่อเสริม, แบบฝึกหัด, ตัวอย่างเพิ่มเติม
|   +-- lib/             # ไลบรารีที่จำเป็น (ili9341, xglcd_font, etc.)
|   +-- fonts/           # ไฟล์ฟอนต์สำหรับจอ TFT
|   +-- pins.py          # การกำหนดขา GPIO มาตรฐาน
|   +-- README.md        # คู่มือ Week 1
|
+-- Week_2/              # การสอบเทียบเซ็นเซอร์และ OOP ขั้นกลาง
|   +-- 01_pH_Sensor/    # การวัดและสอบเทียบ pH
|   +-- 02_Pump_Control/ # การสอบเทียบอัตราการไหล
|   +-- 03_OOP_Advanced/ # Inheritance, Composition, @property
|   +-- lib/             # คลาส OOP สำหรับอ้างอิง
|   +-- exercises/       # แบบฝึกหัดพร้อมเฉลย
|   +-- README.md        # คู่มือ Week 2
|
+-- Week_3/              # ระบบไทเทรตอัตโนมัติแบบเต็มรูปแบบ
|   +-- main.py          # จุดเริ่มต้นโปรแกรม
|   +-- config.py        # ค่าคงที่และการตั้งค่า GPIO
|   +-- hardware/        # Hardware Abstraction Layer
|   +-- core/            # Business Logic Layer
|   +-- modes/           # Application Mode Layer (6 โหมด)
|   +-- ui/              # User Interface Layer
|   +-- README.md        # คู่มือ Week 3
|
+-- SeniorProject/       # ตัวอย่างโปรเจกต์นิสิตรุ่นพี่
|   +-- Hemmawan_Saon/
|   +-- Nuttakit_Deemon/
|
+-- README.md            # ไฟล์นี้ - ภาพรวมหลักสูตร
```

---

## ตารางสรุปรายสัปดาห์ (Weekly Summary Table)

| สัปดาห์ | หัวข้อหลัก | แนวคิด OOP | ผลลัพธ์ |
|:------:|----------|-----------|--------|
| **Week 1** | LED, Button, ADC, PWM, DS18B20, TFT, Buzzer | Class, Object, Constructor, Method | เข้าใจฮาร์ดแวร์ TitraLab |
| **Week 2** | pH Sensor Calibration, Pump Flow Rate | Inheritance, Composition, @property | ได้ค่าสอบเทียบ (R-squared >= 0.99) |
| **Week 3** | Full Auto Titration, 6 Operating Modes | Modular Architecture, State Machine | ไทเทรตสำเร็จ + ไฟล์ CSV |

---

## สิ่งที่ต้องเตรียม (Prerequisites)

### ซอฟต์แวร์ (Software)

| รายการ | คำอธิบาย | ดาวน์โหลด |
|--------|----------|-----------|
| **Thonny IDE** | IDE สำหรับเขียนและอัปโหลดโค้ด MicroPython | [thonny.org](https://thonny.org) |
| **CP210x USB Driver** | ไดรเวอร์สำหรับเชื่อมต่อ ESP32 ผ่าน USB | [Silicon Labs](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) |
| **Python 3.x** | (สำหรับ EquivPoint) วิเคราะห์จุดสมมูล | [python.org](https://python.org) |

### ฮาร์ดแวร์ (Hardware)

| รายการ | คำอธิบาย |
|--------|----------|
| **บอร์ด TitraLab** | ESP32-WROOM-32 พร้อมอุปกรณ์ต่อพ่วง |
| **เซ็นเซอร์ pH** | พร้อมวงจรขยายสัญญาณ LMC6482 |
| **ปั๊มเพอริสตาลติก** | 12V DC ควบคุมด้วย PWM |
| **สารละลายบัฟเฟอร์** | pH 4.00, 7.00, 10.00 สำหรับสอบเทียบ |
| **สารไทแทรนต์** | เช่น NaOH 0.1M |

---

## เริ่มต้นอย่างรวดเร็ว (Quick Start)

### ขั้นตอนที่ 1: ติดตั้ง Thonny และ Driver

1. ดาวน์โหลดและติดตั้ง [Thonny IDE](https://thonny.org)
2. ติดตั้ง CP210x USB driver (ถ้ายังไม่มี)
3. เชื่อมต่อบอร์ด TitraLab ผ่านสาย USB

### ขั้นตอนที่ 2: ตั้งค่า Thonny สำหรับ ESP32

1. เปิด Thonny
2. ไปที่ **Tools > Options > Interpreter**
3. เลือก **"MicroPython (ESP32)"**
4. เลือก COM port ที่ถูกต้อง
5. คลิก **OK**

### ขั้นตอนที่ 3: อัปโหลดไลบรารี

1. ไปที่ **View > Files** เพื่อเปิด File Browser
2. อัปโหลดโฟลเดอร์ `Week_1/lib/` ไปยัง ESP32
3. อัปโหลดโฟลเดอร์ `Week_1/fonts/` ไปยัง ESP32

### ขั้นตอนที่ 4: เริ่มเรียนรู้

1. เปิดไฟล์ `Week_1/core/01_led_class.py`
2. กด **F5** หรือคลิกปุ่ม Run
3. ดูผลลัพธ์ใน Shell panel

### เส้นทางการเรียน (Learning Path)

```
เริ่มต้นที่นี่!
      |
      v
Week_1/README.md  -->  Week_2/README.md  -->  Week_3/README.md
      |                       |                       |
      v                       v                       v
   พื้นฐาน               การสอบเทียบ            ระบบเต็มรูปแบบ
```

---

## ไลบรารีที่จำเป็น (Required Libraries)

ไลบรารีทั้งหมดอยู่ในโฟลเดอร์ `Week_1/lib/` ให้อัปโหลดไปยัง ESP32 ก่อนใช้งาน

| ไฟล์ | คำอธิบาย | จำเป็น |
|------|----------|:------:|
| `ili9341.py` | ไดรเวอร์จอ TFT ILI9341 | ใช่ |
| `xglcd_font.py` | ไลบรารีแสดงฟอนต์ | ใช่ |
| `sdcard.py` | ไดรเวอร์ SD Card | ไม่* |
| `titralab_simple.py` | คลาสพื้นฐาน TitraLab | ใช่ |

> *หมายเหตุ: Week 3 ใช้ ESP32 flash storage แทน SD Card

### ไฟล์ฟอนต์ (Font Files)

อยู่ในโฟลเดอร์ `Week_1/fonts/`:

| ไฟล์ | ขนาด | การใช้งาน |
|------|:----:|----------|
| `ArcadePix9x11.c` | 9x11 px | ข้อความเล็ก, ค่าตัวเลข |
| `EspressoDolce18x24.c` | 18x24 px | หัวข้อ, ค่า pH หลัก |

---

## ตารางอ้างอิงขา GPIO (GPIO Pin Reference)

ตารางนี้แสดงขา GPIO หลักที่ใช้ในบอร์ด TitraLab (ดูรายละเอียดเพิ่มเติมที่ `Week_1/pins.py`)

### ขาหลักที่ใช้บ่อย (Commonly Used Pins)

| อุปกรณ์ | GPIO | ค่าคงที่ | ประเภท | หมายเหตุ |
|---------|:----:|---------|--------|----------|
| **LED สีแดง** | 2 | `LED_RED` | Output | แสดงข้อผิดพลาด |
| **LED สีเขียว** | 4 | `LED_GREEN` | Output | แสดงสถานะปกติ |
| **Button 1** | 34 | `BUTTON1` | Input-only | SELECT/ยืนยัน |
| **Button 2** | 35 | `BUTTON2` | Input-only | UP/เลื่อนขึ้น |
| **Button 3** | 39 | `BUTTON3` | Input-only | DOWN/เลื่อนลง |
| **pH Sensor** | 25 | `PH_PIN` | ADC | อ่านแรงดัน 0-3.3V |
| **Temperature** | 16 | `DS18B20_PIN` | OneWire | เซ็นเซอร์อุณหภูมิ |
| **Pump** | 21 | `PUMP_PIN` | PWM | ควบคุมปั๊มไทแทรนต์ |
| **Buzzer** | 26 | `BUZZER_PIN` | PWM | เสียงแจ้งเตือน |

### ข้อควรระวัง (Important Notes)

- **GPIO34, 35, 39** เป็นขา input-only ไม่มี internal pull-up/pull-down
- **GPIO0, 2, 5, 12, 15** มีข้อจำกัดในการใช้งาน (boot mode pins)
- ดูรายละเอียดทั้งหมดที่ [`Week_1/pins.py`](Week_1/pins.py)

---

## การไหลของข้อมูลใน Week 3 (Data Flow in Week 3)

```
+==========================================================================+
|                      TitraLab Data Flow (Week 3)                          |
|                    การไหลของข้อมูลในระบบ TitraLab                          |
+==========================================================================+

  +-------------+     +-------------+     +-------------+
  |   Sensors   |     |    ESP32    |     | TFT Display |
  |  เซ็นเซอร์   | --> |   ประมวลผล   | --> |   แสดงผล    |
  +-------------+     +-------------+     +-------------+
  | - pH Probe  |     |             |
  | - DS18B20   |     +------+------+
  +-------------+            |
                             v
                    +----------------+
                    | Flash Storage  |
                    | (ไฟล์ CSV)      |
                    +----------------+
                             |
                             v
                    +----------------+
                    |  Thonny IDE    |
                    |  (ดาวน์โหลด)    |
                    +----------------+
                             |
                             v
                    +----------------+
                    |  EquivPoint    |
                    | (วิเคราะห์ข้อมูล) |
                    +----------------+
                             |
                             v
                    +----------------+
                    | จุดสมมูล (Ve)   |
                    | Equivalence Pt |
                    +----------------+

==========================================================================
```

### ขั้นตอนหลังการไทเทรต (Post-Titration Steps)

1. **บันทึกข้อมูล** - ระบบบันทึก pH, ปริมาตร, อุณหภูมิ ลง ESP32 flash
2. **ดาวน์โหลดไฟล์** - ใช้ Thonny IDE ดาวน์โหลดไฟล์ CSV จาก ESP32
3. **วิเคราะห์ข้อมูล** - ใช้ EquivPoint (Python tool) หาจุดสมมูลที่แม่นยำ
4. **คำนวณความเข้มข้น** - ใช้สูตร C1V1 = C2V2

---

## ลิงก์ไปยัง README รายสัปดาห์ (Links to Weekly READMEs)

| สัปดาห์ | ลิงก์ | คำอธิบาย |
|:------:|------|----------|
| **Week 1** | [Week_1/README.md](Week_1/README.md) | พื้นฐานฮาร์ดแวร์, GPIO, ADC, PWM, OOP เบื้องต้น |
| **Week 2** | [Week_2/README.md](Week_2/README.md) | การสอบเทียบ pH และ Flow Rate, OOP ขั้นกลาง |
| **Week 3** | [Week_3/README.md](Week_3/README.md) | ระบบไทเทรตอัตโนมัติ 6 โหมด, OOP ขั้นสูง |

---

## การเชื่อมโยงโปรแกรมกับเคมี (Programming-Chemistry Connection)

การเรียนรู้การเขียนโปรแกรมผ่านบอร์ด TitraLab ช่วยให้นิสิตเห็นความเชื่อมโยงที่ชัดเจน:

| แนวคิดโปรแกรม | แนวคิดเคมี | ตัวอย่างใน TitraLab |
|--------------|-----------|-------------------|
| **Variable/ตัวแปร** | ค่าที่วัดได้ | pH, temperature, volume |
| **Loop/ลูป** | การวัดซ้ำ | วัด pH ทุกวินาทีระหว่างไทเทรต |
| **Conditional/เงื่อนไข** | การตรวจสอบ | ถ้า pH > 7 แสดงว่าเป็นเบส |
| **ADC** | สมการ Nernst | แปลง mV -> pH |
| **PWM** | ควบคุมอัตราการไหล | ปรับความเร็วปั๊มตาม pH |
| **Class/Object** | พิมพ์เขียว/ของจริง | Class LED -> led_red, led_green |
| **Inheritance** | ประเภทเซ็นเซอร์ | BaseSensor -> pHSensor, TempSensor |

---

## คำศัพท์สำคัญ (Key Terminology)

### คำศัพท์ OOP (OOP Terms)

| English | ภาษาไทย | คำอธิบาย |
|---------|---------|----------|
| Class | คลาส | พิมพ์เขียวสำหรับสร้าง Object |
| Object | ออบเจกต์ | สิ่งที่สร้างจาก Class (Instance) |
| Constructor | ตัวสร้าง | Method `__init__` ที่ทำงานตอนสร้าง Object |
| Method | เมธอด | ฟังก์ชันที่อยู่ใน Class |
| Attribute | แอตทริบิวต์ | ตัวแปรที่อยู่ใน Class |
| Inheritance | การสืบทอด | Class ลูกรับคุณสมบัติจาก Class แม่ |
| Composition | การประกอบ | Object มี Object อื่นเป็นส่วนประกอบ |

### คำศัพท์ฮาร์ดแวร์ (Hardware Terms)

| English | ภาษาไทย | คำอธิบาย |
|---------|---------|----------|
| GPIO | จีพีไอโอ | General Purpose Input/Output - ขาอเนกประสงค์ |
| ADC | เอดีซี | Analog-to-Digital Converter - ตัวแปลงสัญญาณ (12-bit, 0-4095) |
| PWM | พีดับเบิลยูเอ็ม | Pulse Width Modulation (10-bit, 0-1023) |
| Duty Cycle | ดิวตี้ไซเคิล | สัดส่วนเวลาที่สัญญาณอยู่ที่ HIGH |

### คำศัพท์เคมี (Chemistry Terms)

| English | ภาษาไทย | คำอธิบาย |
|---------|---------|----------|
| Titration | ไทเทรชัน | การหาปริมาณสารด้วยการเติมสารไทแทรนต์ |
| Equivalence Point | จุดสมมูล | จุดที่สารทำปฏิกิริยาพอดีกัน |
| Calibration | การสอบเทียบ | การปรับค่าเซ็นเซอร์ให้อ่านค่าถูกต้อง |
| Nernst Equation | สมการเนิร์นสต์ | E = E0 - (2.303RT/nF) x pH |
| Buffer Solution | สารละลายบัฟเฟอร์ | สารละลายที่มี pH คงที่ |

---

## เกณฑ์ความสำเร็จ (Success Criteria)

### เกณฑ์รายสัปดาห์ (Weekly Criteria)

| สัปดาห์ | เกณฑ์ | สถานะ |
|:------:|-------|:-----:|
| **Week 1** | เข้าใจ LED, Button, ADC, PWM และสร้าง Class ง่ายๆ ได้ | [ ] |
| **Week 2** | สอบเทียบ pH (R-squared >= 0.99) และ Flow Rate (%RSD < 5%) | [ ] |
| **Week 3** | ไทเทรตสำเร็จ พบจุดสมมูล และวิเคราะห์ด้วย EquivPoint ได้ | [ ] |

### ผลลัพธ์สุดท้าย (Final Deliverables)

- [ ] ไฟล์สอบเทียบ `data_calibrate.txt` (slope, intercept, R-squared)
- [ ] ไฟล์ Flow Rate `data_flowrate.txt` (mL/s)
- [ ] ไฟล์ข้อมูลไทเทรต `titration_data_R*.csv`
- [ ] รายงานการวิเคราะห์จุดสมมูลจาก EquivPoint

---

## โปรเจกต์นิสิตรุ่นพี่ (Senior Project Examples)

โฟลเดอร์ `SeniorProject/` ประกอบด้วยตัวอย่างโปรเจกต์จากนิสิตรุ่นก่อน:

| โฟลเดอร์ | นิสิต | คำอธิบาย |
|---------|-------|----------|
| `Hemmawan_Saon/` | เหมวรรณ สาออน | โค้ดไทเทรตเวอร์ชัน 2023 |
| `Nuttakit_Deemon/` | ณัฐกิตติ์ ดีมอญ | โค้ดไทเทรตเวอร์ชัน 2024 |

นิสิตสามารถศึกษาโค้ดเหล่านี้เป็นแนวทางในการพัฒนาโปรเจกต์ของตนเอง

---

## การแก้ไขปัญหาเบื้องต้น (Troubleshooting)

### ปัญหาที่พบบ่อย (Common Issues)

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|-------|--------|
| เชื่อมต่อ ESP32 ไม่ได้ | Driver หรือสาย USB | ติดตั้ง CP210x driver, ลองสายอื่น |
| `No module named 'ili9341'` | ไม่ได้อัปโหลดไลบรารี | อัปโหลด `Week_1/lib/` ไปยัง ESP32 |
| ค่า pH ไม่เสถียร | หัววัดสกปรก | ล้างด้วยน้ำ DI |
| R-squared < 0.99 | สารละลายบัฟเฟอร์หมดอายุ | ใช้บัฟเฟอร์ใหม่, ล้างหัววัด |
| ปั๊มไม่ทำงาน | สายไฟหลุด | ตรวจสอบการเชื่อมต่อ |

### ขอความช่วยเหลือ (Getting Help)

1. ดู README ของแต่ละสัปดาห์
2. ตรวจสอบ error message ใน Thonny Shell
3. สอบถามอาจารย์ผู้สอนหรือ TA

---

## ผู้พัฒนา (Developers)

### ผู้ออกแบบบอร์ด (Board Designers)
- รศ.ดร.วิวัฒน์ วชิรวงศ์กวิน (Assoc. Prof. Dr. Viwat Vchirawongkwin)
- ศ.ดร.สัมฤทธิ์ วัชรสินธุ์ (Prof. Dr. Sumrit Wacharasindhu)

### ผู้พัฒนาโค้ด (Code Contributors)
- เหมวรรณ สาออน (Hemmawan Saon)
- ณัฐกิตติ์ ดีมอญ (Nuttakit Deemorn)

**รายวิชา:** 2302311 Integrated Chemistry Laboratory I
**สถาบัน:** ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย

---

*Version 1.0.0 - MicroPython Curriculum Overview*
*สร้างเมื่อ: มกราคม 2026*

# TitraLab

## ภาพรวม (Overview)

**TitraLab** คือบอร์ดพัฒนาสำหรับการศึกษาที่ออกแบบโดย รศ.ดร.วิวัฒน์ วชิรวงศ์กวิน และ ศ.ดร.สัมฤทธิ์ วัชรสินธุ์ เพื่อยกระดับประสบการณ์การเรียนรู้ในสาขาเคมี บอร์ดนี้ใช้ไมโครคอนโทรลเลอร์ ESP32 เป็นแกนหลัก และมีบทบาทสำคัญในรายวิชา 2302311 Integrated Chemistry Laboratory I ในหัวข้อ "Advanced Acid-Base Titrations with Automated Flow System"

TitraLab is an educational development board ingeniously designed by Associate Professor Dr. Viwat Vchirawongkwin and Professor Dr. Sumrit Wacharasindhu to enhance the learning experience in the field of chemistry. At its core, TitraLab utilizes the ESP32 microcontroller, renowned for its versatility and robust performance. This project plays a pivotal role in the Integrated Chemistry Laboratory I (2302311) course, particularly in the module titled "Advanced Acid-Base Titrations with Automated Flow System."

---

## วัตถุประสงค์ (Purpose)

วัตถุประสงค์หลักของ TitraLab คือการแนะนำนิสิตให้รู้จักการประยุกต์ใช้การเขียนโปรแกรมในการวิเคราะห์ทางเคมีและระบบอัตโนมัติในห้องปฏิบัติการ บอร์ดนี้เป็นเครื่องมือการศึกษาสำหรับการทำความเข้าใจและการนำระบบไทเทรตอัตโนมัติไปใช้งาน ซึ่งเป็นกระบวนการพื้นฐานในเคมีวิเคราะห์ ผ่านประสบการณ์จริงกับ TitraLab นิสิตจะได้รับข้อมูลเชิงลึกที่มีคุณค่าเกี่ยวกับการบูรณาการฮาร์ดแวร์และซอฟต์แวร์ในการวิจัยทางวิทยาศาสตร์

The primary objective of TitraLab is to introduce students to the practical applications of programming in chemical analysis and laboratory automation. It serves as an educational tool in understanding and implementing automated titrations, a fundamental process in analytical chemistry. Through hands-on experience with TitraLab, students gain valuable insights into the integration of hardware and software in scientific research.

---

## คุณสมบัติหลัก (Key Features)

- **ไมโครคอนโทรลเลอร์ (Microcontroller):** ESP32
- **ความเข้ากันได้ในการเขียนโปรแกรม (Programming Compatibility):** Arduino IDE และ MicroPython
- **IDE สำหรับ MicroPython:** Thonny
- **จอแสดงผล (Display):** จอ TFT ขนาด 2.4 นิ้ว พร้อมไดรเวอร์ ili9341
- **เซ็นเซอร์และตัวบ่งชี้ (Sensors & Indicators):**
  - LED สีแดงและสีเขียวสำหรับแสดงสถานะ
  - เซ็นเซอร์อุณหภูมิ DS18B20
  - ขั้วต่อ BNC สำหรับหัววัด pH
  - วงจรรวมสำหรับอ่านค่ามิลลิโวลต์จากหัววัด pH
- **การจัดเก็บข้อมูล (Storage):** ข้อมูลถูกบันทึกลงใน ESP32 flash storage และดาวน์โหลดผ่าน Thonny IDE
- **เสียง (Sound):** Buzzer บนบอร์ด
- **ปั๊ม (Pump):** ปั๊มเพอริสตาลติกสำหรับการเติมสารไทแทรนต์อัตโนมัติ

---

## โครงสร้างโฟลเดอร์ (Directory Structure)

```
TitraLab/
├── MicroPython/                 # โค้ด MicroPython สำหรับ ESP32
│   ├── Week_1/                  # สัปดาห์ที่ 1: GPIO, เซ็นเซอร์, อุปกรณ์ต่อพ่วงพื้นฐาน
│   │   ├── pins.py              # ค่าคงที่การกำหนดขา GPIO มาตรฐาน
│   │   ├── core/                # ไฟล์หลักสำหรับการสอน (LED, Button, ADC, PWM, OOP)
│   │   ├── lib/                 # ไลบรารีที่จำเป็น (ili9341, xglcd_font, sdcard)
│   │   ├── fonts/               # ไฟล์ฟอนต์สำหรับจอ TFT
│   │   └── extras/              # ตัวอย่างเพิ่มเติม (Buzzer, DS18B20, TFT, DAC)
│   ├── Week_2/                  # สัปดาห์ที่ 2: การวัด pH, การสอบเทียบ, การควบคุมปั๊ม
│   │   ├── 01_pH_Sensor/        # การสอบเทียบและอ่านค่า pH
│   │   ├── 02_Pump_Control/     # การสอบเทียบอัตราการไหล
│   │   └── 03_OOP_Advanced/     # OOP ขั้นกลาง (Inheritance, Composition)
│   ├── Week_3/                  # สัปดาห์ที่ 3: ระบบไทเทรตอัตโนมัติเต็มรูปแบบ
│   │   ├── main.py              # จุดเริ่มต้นโปรแกรม
│   │   ├── config.py            # การตั้งค่า GPIO และค่าคงที่
│   │   ├── hardware/            # Hardware Abstraction Layer
│   │   ├── core/                # Business Logic (Calibrator, TitrationController)
│   │   ├── modes/               # 6 โหมดการทำงาน (Calibrate, Test, Titration)
│   │   └── ui/                  # User Interface (Menu System)
│   └── SeniorProject/           # โปรเจกต์นิสิตปริญญาตรี
│
├── EquivPoint/                  # เครื่องมือวิเคราะห์ข้อมูลบน Desktop (Python)
│   ├── equiv_point.py           # โปรแกรมหาจุดสมมูลด้วย Spline และ Derivative
│   └── README.md                # คู่มือการใช้งาน EquivPoint
│
├── ArduinoIDE/                  # Arduino IDE sketches (ทางเลือก)
│
├── Documents/                   # เอกสารประกอบรายวิชา
│   ├── Prelab_Week1.pdf         # Prelab สัปดาห์ที่ 1
│   ├── Prelab_Week2.pdf         # Prelab สัปดาห์ที่ 2
│   ├── Prelab_Week3.pdf         # Prelab สัปดาห์ที่ 3
│   ├── Report_Week2.docx        # แบบฟอร์มรายงานสัปดาห์ที่ 2
│   └── Report_Week3.docx        # แบบฟอร์มรายงานสัปดาห์ที่ 3
│
└── docs/
    └── agent-spec/              # AI Agent specifications
```

---

## โครงสร้างรายวิชา (Course Structure)

### สัปดาห์ที่ 1: รู้จักบอร์ด TitraLab (Introduction to TitraLab Programming)

- **Blink:** เข้าใจ GPIO ของ ESP32 ในโหมด OUTPUT โดยใช้ LED บนบอร์ด
- **Button:** เรียนรู้ GPIO ของ ESP32 ในโหมด INPUT
- **DS18B20:** อ่านค่าอุณหภูมิด้วยโปรโตคอล 1-wire
- **TFT Display:** ใช้งานไดรเวอร์ ili9341 สำหรับแสดงข้อมูล
- **Buzzer:** ใช้งาน buzzer บนบอร์ด
- **OOP พื้นฐาน:** Class, Object, Constructor, Method

### สัปดาห์ที่ 2: ทบทวนทฤษฎีและการประยุกต์ใช้ (Calibration and Advanced OOP)

- **การวัด pH:** เข้าใจสมการ Nernst และการใช้หัววัด pH ที่เชื่อมต่อผ่าน BNC
- **Linear Regression:** ทบทวนวิธีการและสมการ
- **เป้าหมายเชิงปฏิบัติ:**
  - สอบเทียบหัววัด pH และเข้าใจการอ่านค่ามิลลิโวลต์
  - สอบเทียบอัตราการไหลของปั๊มเพอริสตาลติกสำหรับการไทเทรต
- **OOP ขั้นกลาง:** Inheritance, Composition

### สัปดาห์ที่ 3: ระบบไทเทรตอัตโนมัติเต็มรูปแบบ (Full Automated Titration System)

- **โครงสร้างโค้ดแบบ OOP Modular:**
  - `hardware/` - Hardware Abstraction Layer (PHSensor, Pump, Display, Buttons)
  - `core/` - Business Logic (Calibrator, TitrationController, DataManager)
  - `modes/` - 6 โหมดการทำงาน (Calibrate pH, Test pH, Calibrate Flow, Test Flow, Purge, Full Auto Titration)
  - `ui/` - User Interface (Menu System)
- **การประยุกต์ใช้:** ใช้โค้ดไทเทรตที่พัฒนาโดยนางสาวเหมวรรณ สาออน และนายณัฐกิตติ์ ดีมอญ สำหรับการไทเทรตกรด-เบส
- **วัตถุประสงค์:** ทำการไทเทรตระหว่าง HCl และ NaOH โดยใช้ TitraLab
- **การวิเคราะห์:** สร้างกราฟไทเทรชันเพื่อหาจุดสมมูล เปรียบเทียบกับการเปลี่ยนสีของ phenolphthalein indicator
- **การจัดเก็บข้อมูล:** ข้อมูลถูกบันทึกลงใน ESP32 flash storage และดาวน์โหลดผ่าน Thonny IDE

---

## EquivPoint - เครื่องมือหาจุดสมมูล (Equivalence Point Analysis Tool)

**EquivPoint** เป็นเครื่องมือวิเคราะห์ข้อมูลบน Desktop ที่พัฒนาด้วย Python สำหรับหาจุดสมมูล (equivalence point) จากข้อมูลที่บันทึกโดยบอร์ด TitraLab

### คุณสมบัติหลัก

- **Spline Interpolation:** ใช้ Cubic Spline ในการปรับเส้นโค้งให้เรียบ
- **First Derivative Analysis:** หาจุดที่ dpH/dV มีค่าสูงสุด (maximum rate of pH change)
- **Second Derivative Analysis:** หาจุดที่ d2pH/dV2 = 0 (inflection point)
- **pH = 7 Crossing:** สำหรับการไทเทรตกรดแก่-เบสแก่ หาจุดที่ pH ตัดผ่าน 7.0

### การใช้งาน

```bash
cd EquivPoint
python -m venv venv
venv\Scripts\activate          # Windows
pip install numpy matplotlib scipy pandas
python equiv_point.py titration_data_R1.csv
```

### ขั้นตอนการทำงาน (Workflow)

```
1. ทำการไทเทรตบนบอร์ด TitraLab (Mode 6: Full Auto Titration)
   │
   ▼
2. ข้อมูล CSV ถูกบันทึกลงใน ESP32 flash storage
   │
   ▼
3. ดาวน์โหลดไฟล์ CSV ผ่าน Thonny IDE (Files panel > Right-click > Download to...)
   │
   ▼
4. รัน EquivPoint เพื่อวิเคราะห์จุดสมมูลอย่างแม่นยำ
```

---

## เริ่มต้นอย่างรวดเร็ว (Quick Start)

### สำหรับนิสิต

| สัปดาห์ | เริ่มต้นที่ | คำอธิบาย |
|:-------:|-------------|----------|
| **1** | [MicroPython/Week_1/README.md](MicroPython/Week_1/README.md) | รู้จักบอร์ด, GPIO, ADC, PWM, OOP พื้นฐาน |
| **2** | [MicroPython/Week_2/README.md](MicroPython/Week_2/README.md) | สอบเทียบ pH และ Flow Rate, OOP ขั้นกลาง |
| **3** | [MicroPython/Week_3/README.md](MicroPython/Week_3/README.md) | ระบบไทเทรตอัตโนมัติเต็มรูปแบบ |
| **วิเคราะห์** | [EquivPoint/README.md](EquivPoint/README.md) | หาจุดสมมูลด้วย Spline และ Derivative |

### ไฟล์สำคัญใน Week 3

```python
# ใน Thonny REPL หลังจากอัปโหลดไฟล์ Week_3 ไปยัง ESP32:
>>> import main
>>> main.main()
```

เมนู 6 โหมดจะปรากฏบนหน้าจอ TFT พร้อมใช้งานทันที:

| โหมด | ชื่อ | คำอธิบาย |
|:----:|------|----------|
| 1 | Calibrate pH Sensor | สอบเทียบ pH ด้วยบัฟเฟอร์ 4, 7, 10 |
| 2 | pH Sensor Test | ทดสอบการอ่านค่า pH แบบ real-time |
| 3 | Calibrate Flow Rate | สอบเทียบอัตราการไหลของปั๊ม |
| 4 | Flow Rate Test | ทดสอบปั๊มปริมาตรที่กำหนด |
| 5 | Purge | ล้างท่อ/ไล่ฟองอากาศ |
| 6 | Full Auto Titration | ไทเทรชันอัตโนมัติ |

---

## การกำหนดขา GPIO (GPIO Pin Configuration)

ดูรายละเอียดเพิ่มเติมได้ที่ [`MicroPython/Week_1/pins.py`](MicroPython/Week_1/pins.py)

| อุปกรณ์ | GPIO | ประเภท |
|---------|:----:|--------|
| LED สีแดง | 2 | Output |
| LED สีเขียว | 4 | Output |
| Button 1-3 | 34, 35, 39 | Input-only |
| DS18B20 | 16 | OneWire |
| pH Sensor | 25 | ADC |
| Pump | 21 | PWM |
| Buzzer | 26 | PWM |
| TFT (SPI) | 14, 13, 27, 15, 0 | SPI1 |

---

## เอกสารประกอบรายวิชา (Course Documents)

- **Prelab:** เอกสารเตรียมความพร้อมก่อนเข้าปฏิบัติการ (`Documents/Prelab_Week*.pdf`)
- **Report Templates:** แบบฟอร์มรายงาน (`Documents/Report_Week*.docx`)

---

## ผู้พัฒนา (Developers)

### ผู้ออกแบบและพัฒนาบอร์ด (Board Designers)

- **รศ.ดร.วิวัฒน์ วชิรวงศ์กวิน (Associate Professor Dr. Viwat Vchirawongkwin)**
- **ศ.ดร.สัมฤทธิ์ วัชรสินธุ์ (Professor Dr. Sumrit Wacharasindhu)**

### ผู้พัฒนาโค้ดไทเทรต (Titration Code Contributors)

- **นางสาวเหมวรรณ สาออน (Miss Hemmawan Saon)**
- **นายณัฐกิตติ์ ดีมอญ (Mr. Nuttakit Deemorn)**

---

## สถาบัน (Institution)

**ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย**

**Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

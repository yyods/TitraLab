# TitraLab Week 3: Automated Acid-Base Titration System
# TitraLab สัปดาห์ที่ 3: ระบบไทเทรตกรด-เบสอัตโนมัติแบบเต็มรูปแบบ

---

> **รายวิชา:** 2302311 Integrated Chemistry Laboratory I
> **ภาควิชา:** เคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย
> **Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## สารบัญ (Table of Contents)

| หมวด | เนื้อหา |
|:----:|---------|
| 📚 | [เอกสารประกอบ](#เอกสารประกอบ-documentation) |
| 1 | [Quick Start - เริ่มต้นที่นี่](#quick-start---เริ่มต้นที่นี่-2-นาที) |
| 2 | [เส้นทางการเรียนรู้](#เส้นทางการเรียนรู้-titralab-learning-path) |
| 3 | [ความรู้พื้นฐานที่ต้องการ](#ความรู้พื้นฐานที่ต้องการ-prerequisites) |
| 4 | [6 โหมดการทำงาน](#6-โหมดการทำงาน-6-operating-modes) |
| 5 | [โครงสร้างโฟลเดอร์](#โครงสร้างโฟลเดอร์-folder-structure) |
| 6 | [GPIO Pin Reference](#gpio-pin-reference-ตารางอ้างอิงขา-gpio) |
| 7 | [หลักการทางเคมี](#หลักการทางเคมี-chemistry-principles) |
| 8 | [OOP Design Patterns](#oop-design-patterns-รูปแบบการออกแบบ-oop) |
| 9 | [ตารางเวลาการสอน](#ตารางเวลาการสอน-3-ชั่วโมง-teaching-schedule) |
| 10 | [ขั้นตอนการทดลอง](#ขั้นตอนการทดลอง-lab-procedure) |
| 11 | [การใช้งานปุ่มกด](#การใช้งานปุ่มกด-button-controls) |
| 12 | [ผลลัพธ์ที่คาดหวัง](#ผลลัพธ์ที่คาดหวัง-expected-results) |
| 13 | [การแก้ไขปัญหา](#การแก้ไขปัญหา-troubleshooting) |
| 14 | [เกณฑ์ความสำเร็จ](#เกณฑ์ความสำเร็จ-success-criteria) |
| 15 | [การวิเคราะห์ข้อมูลด้วย EquivPoint](#การวิเคราะห์ข้อมูลด้วย-equivpoint-data-analysis-with-equivpoint) |

> **หมายเหตุสำคัญ:** ระบบ TitraLab ใช้ **ESP32 flash storage** สำหรับบันทึกไฟล์ CSV
> (ไม่ใช้ SD Card) นิสิตดาวน์โหลดไฟล์ผ่าน Thonny IDE เพื่อวิเคราะห์ด้วย EquivPoint

---

## เอกสารประกอบ (Documentation)

| เอกสาร | คำอธิบาย | สำหรับ |
|--------|----------|--------|
| 📘 **README.md** | เอกสารเทคนิคฉบับเต็ม (Technical Documentation) | ผู้สอน, ศึกษาเพิ่มเติม |
| 📗 **[USER_MANUAL.md](USER_MANUAL.md)** | คู่มือการใช้งานฉบับย่อ (Quick Reference) | **นิสิต - วันทดลอง** |
| 📙 **[LAB_DIRECTION.md](LAB_DIRECTION.md)** | คู่มือปฏิบัติการ (Experiment Guide with Theory) | **นิสิต - ก่อนทดลอง** |

```
┌─────────────────────────────────────────────────────────────────┐
│  📙 LAB_DIRECTION.md    →  อ่านก่อนทดลอง (ทฤษฎี + ขั้นตอน)     │
│  📗 USER_MANUAL.md      →  ใช้วันทดลอง (Quick Reference)        │
│  📘 README.md           →  ศึกษาเพิ่มเติม (Technical Details)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start - เริ่มต้นที่นี่ (2 นาที)

> **สำหรับนิสิต:** เริ่มที่นี่! ไม่จำเป็นต้องเข้าใจโค้ดทั้งหมด ใช้งานผ่านเมนูได้ทันที
> **For Students:** Start here! You don't need to understand all the code - just use the menu!

### 3 ไฟล์หลักที่ต้องรู้จัก (3 Core Files to Know)

| ลำดับ | ไฟล์ | คำอธิบาย | สำหรับ |
|:-----:|------|----------|:------:|
| **1** | `main.py` | จุดเริ่มต้นโปรแกรม - รันไฟล์นี้! | ทุกคน |
| **2** | `config.py` | การตั้งค่า GPIO และค่าคงที่ | แก้ไขเมื่อต้องการ |
| **3** | `hardware/*.py` | ไดรเวอร์อุปกรณ์ (ไม่ต้องแก้ไข) | ศึกษาเพิ่มเติม |

### Step 1: Upload Files (อัปโหลดไฟล์)

ใช้ Thonny IDE อัปโหลดโฟลเดอร์ `Week_3` ทั้งหมดไปยัง ESP32:

```
Week_3/  -->  อัปโหลดทั้งโฟลเดอร์ไปยัง ESP32
```

### Step 2: Run Program (รันโปรแกรม)

```python
# ใน Thonny REPL พิมพ์:
>>> import main
>>> main.main()
```

### Step 3: Use Menu (ใช้งานเมนู)

เมนูจะปรากฏบนหน้าจอ TFT พร้อมใช้งานทันที:

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
```

---

## เส้นทางการเรียนรู้ (TitraLab Learning Path)

Week 3 เป็นจุดสุดยอดของการเรียนรู้ TitraLab โดยรวมความรู้จาก Week 1 และ Week 2:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        TitraLab Learning Path                                  ║
║                      เส้นทางการเรียนรู้ TitraLab                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

   Week 1                      Week 2                      Week 3
   สัปดาห์ที่ 1                  สัปดาห์ที่ 2                  สัปดาห์ที่ 3
══════════════════════════════════════════════════════════════════════════════════

 ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
 │    พื้นฐาน         │      │   การสอบเทียบ     │      │   ระบบเต็มรูปแบบ   │
 │   Hardware Basics │      │    Calibration    │      │    Full System    │
 ├───────────────────┤      ├───────────────────┤      ├───────────────────┤
 │ - LED / Button    │      │ - pH Calibration  │      │ - 6 Operating     │
 │ - ADC / PWM       │ ───► │ - Flow Rate Cal.  │ ───► │   Modes           │
 │ - DS18B20 / TFT   │      │ - Inheritance     │      │ - Modular OOP     │
 │ - OOP พื้นฐาน      │      │ - Composition     │      │ - Menu System     │
 └───────────────────┘      └───────────────────┘      └───────────────────┘

       3 ชม.                      3 ชม.                      3 ชม.

 ความซับซ้อน: ง่าย ───────────────────────────────────────────────► ซับซ้อน
 Complexity:  Simple ─────────────────────────────────────────────► Complex

══════════════════════════════════════════════════════════════════════════════════

   สิ่งที่เรียนรู้:              สิ่งที่เรียนรู้:              สิ่งที่เรียนรู้:
   - Digital I/O             - Linear Regression        - Hardware Abstraction
   - Analog I/O              - Nernst Equation          - Dependency Injection
   - Class & Object          - %RSD Calculation         - State Management
   - Constructor             - @property                - Data Persistence
```

### การเชื่อมโยงความรู้ (Knowledge Integration)

| Week 1 (พื้นฐาน) | Week 2 (การประยุกต์) | Week 3 (ระบบเต็มรูปแบบ) |
|------------------|---------------------|------------------------|
| ADC 0-4095 จาก Pot | สอบเทียบ pH 3 จุด | `hardware/ph_sensor.py` - อ่าน pH จริง |
| PWM duty cycle | สอบเทียบ flow rate | `hardware/pump.py` - ควบคุมปั๊มอัตโนมัติ |
| Class LED, Button | Inheritance, Composition | `modes/*.py` - 6 โหมดการทำงาน |
| TFT Display พื้นฐาน | แสดงผลการสอบเทียบ | `ui/menu.py` - ระบบเมนูสมบูรณ์ |

---

## ความรู้พื้นฐานที่ต้องการ (Prerequisites)

### จาก Week 1 (From Week 1)

| หัวข้อ | ไฟล์อ้างอิง | ใช้งานใน Week 3 |
|--------|------------|----------------|
| ADC (อ่านค่า 0-4095) | `Week_1/core/03_adc_ph_basics.py` | อ่านค่าจาก pH Sensor |
| PWM (duty cycle) | `Week_1/core/04_pwm_pump_basics.py` | ควบคุมความเร็วปั๊ม |
| Class และ Object | `Week_1/core/08_intro_oop.py` | โครงสร้าง hardware/, modes/ |
| TFT Display | `Week_1/core/07_display_basics.py` | แสดงผลเมนูและกราฟ |

### จาก Week 2 (From Week 2)

| หัวข้อ | ไฟล์อ้างอิง | ใช้งานใน Week 3 |
|--------|------------|----------------|
| การสอบเทียบ pH 3 จุด | `Week_2/01_pH_Sensor/02_calibration_3point.py` | Mode 1: Calibrate pH |
| การสอบเทียบ flow rate | `Week_2/02_Pump_Control/01_flow_rate_calibration.py` | Mode 3: Calibrate Flow |
| Inheritance | `Week_2/03_OOP_Advanced/01_inheritance_sensors.py` | `modes/base_mode.py` |
| Composition | `Week_2/03_OOP_Advanced/02_composition_pump.py` | `main.py` HardwareHub |

### ไฟล์สอบเทียบที่ต้องมี (Required Calibration Files)

ก่อนใช้งาน Week 3 ต้องมีไฟล์สอบเทียบจาก Week 2:

| ไฟล์ | เนื้อหา | สร้างจาก |
|------|--------|---------|
| `data_calibrate.txt` | slope_m, intercept_b, r_squared, cal_temp (CSV format) | Week 2 pH Calibration |
| `data_flowrate.txt` | flow rate (mL/s, ทศนิยม 4 ตำแหน่ง) | Week 2 Pump Calibration |

**รูปแบบไฟล์ `data_calibrate.txt` (Calibration File Format):**
```
slope_m,intercept_b,r_squared,cal_temp
-0.016911,34.9800,0.999500,25.20
```

โดย:
- **slope_m** = ค่า slope ในหน่วย pH/mV (ประมาณ -0.0169 ที่ 25 C)
- **intercept_b** = ค่า intercept ในหน่วย pH (ประมาณ 34-36)
- **r_squared** = ค่าความแม่นยำ (ต้อง >= 0.99)
- **cal_temp** = อุณหภูมิขณะสอบเทียบ (C)

**รูปแบบไฟล์ `data_flowrate.txt` (Flow Rate File Format - รองรับหลายค่า):**
```
0.2772
0.0008
0.29
[0.2775,0.2768,0.2773]
Last saved: 2026-01-26
```

- บรรทัดแรก: ค่าเฉลี่ย flow rate (mL/s) - **ระบบอ่านเฉพาะบรรทัดนี้**
- บรรทัดถัดไป: SD, %RSD, ค่าทุกครั้งที่วัด (เก็บไว้เพื่อ audit trail)

> **ทำไมต้อง 4 ทศนิยม?** เพราะค่า flow rate ใช้คำนวณปริมาตรที่ถ่ายโอน (volume = flow_rate * time)
> ถ้าตัดทอนเหลือ 3 ตำแหน่ง อาจเกิดความคลาดเคลื่อนประมาณ 1.2% ซึ่งส่งผลต่อความแม่นยำของการไทเทรต

> **ทำไมต้องวัดหลายครั้ง?** เพราะการวัดครั้งเดียวอาจมีความคลาดเคลื่อน การวัด 3-5 ครั้ง
> และตรวจสอบ %RSD <= 3% ช่วยให้มั่นใจว่าค่าที่ได้แม่นยำ

---

## 6 โหมดการทำงาน (6 Operating Modes)

### ภาพรวมโหมด (Mode Overview)

| โหมด | ชื่อ | คำอธิบาย | ไฟล์ | เวลา |
|:----:|------|----------|------|:----:|
| **1** | Calibrate pH Sensor | สอบเทียบ pH ด้วยบัฟเฟอร์ 4, 7, 10 | `modes/mode_calibrate_ph.py` | 10 นาที |
| **2** | pH Sensor Test | ทดสอบการอ่านค่า pH แบบ real-time | `modes/mode_test_ph.py` | 2 นาที |
| **3** | Calibrate Flow Rate | สอบเทียบอัตราการไหลของปั๊ม | `modes/mode_calibrate_flow.py` | 5 นาที |
| **4** | Flow Rate Test | ทดสอบปั๊มปริมาตรที่กำหนด | `modes/mode_test_flow.py` | 2 นาที |
| **5** | Purge | ล้างท่อ/ไล่ฟองอากาศ | `modes/mode_purge.py` | 30 วินาที |
| **6** | Full Auto Titration | **ไทเทรชันอัตโนมัติ** | `modes/mode_titration.py` | 5-15 นาที |

---

### Mode 1: Calibrate pH Sensor (สอบเทียบเซ็นเซอร์ pH)

**ทำไมต้องสอบเทียบ?**

หัววัด pH ต้องการสอบเทียบเพื่อแปลงค่าแรงดันไฟฟ้า (mV) เป็นค่า pH ที่ถูกต้อง ตามหลักสมการ Nernst:

```
E = E0 - (2.303RT/nF) x pH    (ที่ 25 C: slope ทฤษฎี = -59.16 mV/pH)
```

สมการสอบเทียบใช้รูปแบบ **direct-use** (ใช้งานตรง ไม่ต้องกลับสมการ):

```
pH = slope_m * mV + intercept_b
```

โดย:
- **slope_m** มีหน่วย pH/mV (ประมาณ -0.0169 pH/mV ที่ 25 C)
- **intercept_b** มีหน่วย pH (ประมาณ 34-36)
- ข้อดี: ใช้งานทันทีจากค่า mV ที่อ่านได้ ไม่ต้อง invert สมการ

**วิธีใช้:**
1. เลือก Mode 1 จากเมนู
2. แช่หัววัดในบัฟเฟอร์ pH 4.00 -> กดปุ่มบันทึก
3. แช่หัววัดในบัฟเฟอร์ pH 7.00 -> กดปุ่มบันทึก
4. แช่หัววัดในบัฟเฟอร์ pH 10.00 -> กดปุ่มบันทึก
5. ระบบคำนวณสมการ `pH = slope_m * mV + intercept_b` และแสดง R-squared
6. บันทึกเป็นไฟล์ `data_calibrate.txt` (CSV format: slope_m,intercept_b,r_squared,cal_temp)

**เกณฑ์ผ่าน:** R-squared >= 0.99

---

### Mode 2: Test pH Sensor (ทดสอบเซ็นเซอร์ pH)

**ทำไมต้องทดสอบ?**

ตรวจสอบว่าหัววัด pH ทำงานถูกต้องหลังจากสอบเทียบแล้ว

**วิธีใช้:**
1. เลือก Mode 2 จากเมนู
2. แช่หัววัดในสารละลายใดๆ
3. หน้าจอแสดงค่า pH และ mV แบบ real-time
4. กดปุ่มเพื่อออก

**สิ่งที่ต้องสังเกต:** ค่า pH ควรเสถียร (ไม่กระโดดมาก)

---

### Mode 3: Calibrate Flow Rate (สอบเทียบอัตราการไหล)

**ทำไมต้องสอบเทียบ?**

ปั๊มแต่ละตัวมีอัตราการไหลต่างกัน ต้องวัดค่าจริงเพื่อความแม่นยำในการเติมสารไทแทรนต์

**วิธีใช้ (รองรับการวัดหลายครั้ง - แนะนำ 3-5 ครั้ง):**
1. เลือก Mode 3 จากเมนู
2. วางภาชนะรองรับของเหลว (กระบอกตวง)
3. **กด BTN1** เพื่อเริ่มสูบ (ปั๊มจะสูบ ~5 mL แล้วหยุด)
4. วัดปริมาตรจริงที่ได้ด้วยกระบอกตวง
5. **กด BTN2** เพื่อบันทึกค่าปริมาตร
6. ทำซ้ำขั้นตอน 3-5 (แนะนำ 3-5 ครั้ง)
7. **กด BTN3** เมื่อวัดครบ - ระบบคำนวณสถิติและบันทึก

**ปุ่มควบคุม:**
- BTN1: เริ่ม/หยุดปั๊ม
- BTN2: บันทึกค่าปริมาตร
- BTN3: บันทึกและออก (คำนวณ average, SD, %RSD)

**การวิเคราะห์คุณภาพ:**
- **RSD <= 3%**: Excellent! (ดีเยี่ยม)
- **RSD 3-5%**: Good (ดี)
- **RSD > 5%**: Warning - ควรสอบเทียบใหม่

---

### Mode 4: Test Flow Rate (ทดสอบอัตราการไหล)

**ทำไมต้องทดสอบ?**

ยืนยันว่าการสอบเทียบอัตราการไหลถูกต้อง

**วิธีใช้:**
1. เลือก Mode 4 จากเมนู
2. ระบบแสดงข้อมูลทดสอบบนหน้าจอ:
   - ปริมาตรเป้าหมาย: **5.00 mL**
   - อัตราการไหล: ค่าที่สอบเทียบไว้ (mL/s)
   - **เวลาที่คำนวณ**: time = 5.0 / flow_rate (วินาที)
3. **กด BTN1 เพื่อเริ่ม** หรือ BTN3 ยกเลิก
4. ระบบสูบปริมาตร 5 mL ตามเวลาที่คำนวณ
5. วัดปริมาตรจริงด้วยกระบอกตวง
6. เปรียบเทียบ: ความคลาดเคลื่อนควร < 5%

**หมายเหตุ:** BTN3 สามารถยกเลิกได้ทั้งก่อนเริ่มและระหว่างการสูบ

---

### Mode 5: Purge (ล้างท่อ)

**ทำไมต้อง Purge?**

ก่อนไทเทรต ต้องไล่ฟองอากาศออกจากท่อเพื่อให้ได้ปริมาตรที่แม่นยำ

**วิธีใช้ (Manual Start/Stop):**
1. จุ่มปลายท่อดูดในน้ำกลั่นหรือสารไทแทรนต์
2. วางปลายท่อจ่ายในภาชนะเก็บของเสีย
3. เลือก Mode 5 จากเมนู
4. **กด BTN1 เพื่อเริ่มปั๊ม** หรือ BTN3 ยกเลิก
5. ปั๊มทำงานต่อเนื่องจนกว่าจะ **กด BTN1 อีกครั้งเพื่อหยุด**
6. ระบบแสดงเวลาที่ใช้ล้างท่อเมื่อเสร็จสิ้น

**หมายเหตุ:** นิสิตควบคุมเวลาล้างเอง (แนะนำ 1-3 นาที) จนแน่ใจว่าไม่มีฟองอากาศ

**คำแนะนำ:** ทำ Purge ทุกครั้งก่อนเริ่มไทเทรต และหลังเปลี่ยนสารไทแทรนต์

---

### Mode 6: Full Auto Titration (ไทเทรชันอัตโนมัติ) - โหมดหลัก

**นี่คือโหมดสำหรับการทดลองจริง**

**หลักการทำงาน (Constant Dose Volume Approach):**

ระบบใช้วิธี **ปริมาตรคงที่ต่อครั้ง (constant dose volume)** ครั้งละ **0.2 mL** ตลอดทั้งการไทเทรต:

```
กด BTN1 เริ่ม → สูบ 0.2 mL → หยุด → รอ pH เสถียร → อ่านค่า pH → ทำซ้ำ (50 step)
Press BTN1 → Pump 0.2 mL → Stop → Wait stabilize → Read pH → Repeat (50 steps)
```

**เหตุผลทางการเรียนรู้ (Pedagogical Rationale):**

วิธี constant dose volume ถูกเลือกเพราะ:
1. **เข้าใจง่าย**: ทุกจุดบนกราฟห่างกัน 0.2 mL เท่ากันหมด
2. **ตรวจสอบได้**: นิสิตคำนวณเองได้ว่า `total_volume = dose_count x 0.2 mL`
3. **หาจุดสมมูลชัดเจน**: จุดสมมูลอยู่ระหว่างสอง step ที่ pH เปลี่ยนมากที่สุด
4. **เหมือนการไทเทรตมือ**: เปรียบเสมือนการ "หยดสารไทแทรนต์ทีละหยด" แบบสม่ำเสมอ
5. **ปั๊มทำงานที่ 100% เสมอ**: ไม่มีการปรับ duty cycle ลดความซับซ้อนของโค้ด

**ขั้นตอนการใช้งาน:**
1. เลือก Mode 6 จากเมนู
2. ระบบแสดงหน้าจอ Ready พร้อมพารามิเตอร์ (Sample vol, Max vol, Dose, Steps)
3. **กด BTN1 เพื่อเริ่ม** หรือ BTN3 ยกเลิก
4. ระบบทำงานอัตโนมัติครบทุก step (เช่น 50 step = 10 mL)
5. **BTN3 สามารถยกเลิกได้ตลอดเวลา** ระหว่างไทเทรชัน

**ขั้นตอนการไทเทรต (แต่ละ step):**

| ขั้นตอน | การทำงาน | รายละเอียด |
|:-------:|----------|------------|
| 1 | สูบ (Pump) | เปิดปั๊ม 100% เติม 0.2 mL แล้วหยุด |
| 2 | รอ (Wait) | รอ stabilize_time วินาทีให้ pH เสถียร (default=10s) |
| 3 | วัด (Read) | อ่านค่า pH และอุณหภูมิ |
| 4 | บันทึก (Log) | บันทึกข้อมูลลง CSV |
| 5 | แสดงผล (Display) | อัปเดตจอ TFT (step, volume, pH, temp, progress) |
| 6 | ทำซ้ำ (Repeat) | กลับขั้นตอน 1 จนครบทุก step |

**เสียงเตือนใกล้จุดสมมูล (Near-Equivalence Alert):**
- ที่ปริมาตร **4.80 mL**: Buzzer ส่งเสียงสูง **3 ครั้ง** (2000 Hz)
- จุดประสงค์: แจ้งนิสิตให้เตรียมสังเกตจุดสมมูลที่กำลังจะเกิด
- สำหรับการทดลอง HCl 0.1M 5mL + NaOH 0.1M: จุดสมมูลประมาณ 5.0 mL

**การแสดงผลบนจอ TFT:**
- Step ปัจจุบัน / Step ทั้งหมด (เช่น Step 25/50)
- ปริมาตรรวม / ปริมาตรสูงสุด (เช่น 5.00 mL / 10.00 mL)
- ค่า pH ปัจจุบัน
- อุณหภูมิปัจจุบัน
- Progress bar แสดงความคืบหน้า
- สถานะ (Titrating... BTN3:Cancel)

**หมายเหตุสำคัญ:**
- ระบบเก็บข้อมูล **ครบทุก 50 จุด** (ไม่หยุดอัตโนมัติเมื่อพบจุดสมมูล)
- เหตุผล: ต้องการข้อมูลครบถ้วนสำหรับวิเคราะห์ด้วย EquivPoint tool
- จุดสมมูลจะถูกหาในตอนท้ายโดยฟังก์ชัน `detect_equivalence_point()`

**การปรับ stabilize_time:**

ใน `main.py` บรรทัด 191-193 สามารถปรับค่าได้:
```python
titration.configure(
    stabilize_time=10.0  # วินาที - เปลี่ยนเป็น 2.0 สำหรับทดสอบ
)
```
- `stabilize_time=10.0` สำหรับการทดลองจริง (รอให้ pH เสถียร)
- `stabilize_time=2.0` สำหรับทดสอบโปรแกรม (เร็วขึ้น)

**ขีดจำกัดความปลอดภัย:**
- ปริมาตรสูงสุด: 2 x sample volume (default: 10 mL)
- จำนวน step: max_volume / 0.2 (default: 50 step)

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

Week 3 มี 31 ไฟล์ Python จัดเป็น 5 โมดูลหลัก:

```
Week_3/
├── main.py                     # [ENTRY] จุดเริ่มต้น - HardwareHub + Menu Loop
├── config.py                   # [CONFIG] GPIO pins และค่าคงที่ทั้งหมด
│
├── README.md                   # เอกสารนี้ (Technical Documentation)
├── USER_MANUAL.md              # คู่มือการใช้งาน (Quick Reference for Lab Day)
├── LAB_DIRECTION.md            # คู่มือปฏิบัติการ (Experiment Guide with Theory)
│
├── hardware/                   # [LAYER 1] Hardware Abstraction Layer
│   ├── __init__.py             # Package initialization
│   ├── buttons.py              # ButtonManager - จัดการปุ่มกด 3 ปุ่ม
│   ├── buzzer.py               # Buzzer - เสียงแจ้งเตือน
│   ├── display.py              # DisplayManager - จอ TFT ILI9341
│   ├── leds.py                 # LEDManager - LED แดง/เขียว
│   ├── ph_sensor.py            # PHSensor - อ่านและแปลงค่า pH
│   ├── pump.py                 # Pump - ควบคุมปั๊ม PWM
│   ├── sd_card.py              # [DEPRECATED] ไม่ใช้งาน - เก็บไว้อ้างอิง
│   ├── temp_sensor.py          # TemperatureSensor - DS18B20
│   └── README.md               # คำอธิบาย Hardware Layer
│
├── core/                       # [LAYER 2] Business Logic Layer
│   ├── __init__.py             # Package initialization
│   ├── calibrator.py           # Calibrator - สอบเทียบ pH และ flow rate
│   ├── data_manager.py         # DataManager - จัดการข้อมูลสอบเทียบ
│   ├── math_utils.py           # MathUtils - Linear regression, statistics
│   ├── titration.py            # TitrationController - ลูปไทเทรต
│   └── README.md               # คำอธิบาย Core Layer
│
├── modes/                      # [LAYER 3] Application Mode Layer
│   ├── __init__.py             # Package initialization
│   ├── base_mode.py            # BaseMode - Abstract base class
│   ├── mode_calibrate_ph.py    # Mode 1: สอบเทียบ pH
│   ├── mode_test_ph.py         # Mode 2: ทดสอบ pH
│   ├── mode_calibrate_flow.py  # Mode 3: สอบเทียบ flow rate
│   ├── mode_test_flow.py       # Mode 4: ทดสอบ flow rate
│   ├── mode_purge.py           # Mode 5: ล้างท่อ
│   ├── mode_titration.py       # Mode 6: ไทเทรชันอัตโนมัติ
│   └── README.md               # คำอธิบาย Modes Layer
│
├── ui/                         # [LAYER 4] User Interface Layer
│   ├── __init__.py             # Package initialization
│   ├── menu.py                 # MenuSystem - ระบบเมนูหลัก
│   ├── screens.py              # Screen templates - หน้าจอต่างๆ
│   └── README.md               # คำอธิบาย UI Layer
│
├── async_support/              # [OPTIONAL] Asynchronous Support (Advanced)
│   ├── __init__.py             # Package initialization
│   ├── scheduler.py            # Task scheduler
│   ├── async_pump.py           # Async pump control
│   ├── async_titration.py      # Async titration
│   └── README.md               # คำอธิบาย Async Support
│
├── fonts/                      # [LIBRARY] ฟอนต์สำหรับจอ TFT
│   └── EspressoDolce18x24.c    # ฟอนต์หลัก 18x24 pixels
│
├── ili9341.py                  # [LIBRARY] TFT Display Driver
└── xglcd_font.py               # [LIBRARY] Font Loading Library
```

### สถาปัตยกรรมแบบชั้น (Layered Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                 │
│                    (Entry Point + HardwareHub)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           ui/                                   │
│                    (User Interface Layer)                       │
│                  menu.py, screens.py                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          modes/                                 │
│                  (Application Mode Layer)                       │
│   mode_calibrate_ph.py, mode_titration.py, base_mode.py, etc.  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           core/                                 │
│                   (Business Logic Layer)                        │
│       calibrator.py, titration.py, data_manager.py             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         hardware/                               │
│                 (Hardware Abstraction Layer)                    │
│    ph_sensor.py, pump.py, display.py, buttons.py, etc.         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         config.py                               │
│                (GPIO Pins + Constants)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## GPIO Pin Reference (ตารางอ้างอิงขา GPIO)

ตารางนี้ตรงกับ `config.py` (อัปเดตล่าสุด):

### ขา GPIO หลัก (Primary GPIO Pins)

| อุปกรณ์ | GPIO | ค่าคงที่ใน config.py | ประเภท | หมายเหตุ |
|---------|:----:|---------------------|--------|----------|
| **LED แสดงสถานะ** |
| LED สีแดง (Error) | 2 | `LED_RED` | Output | แสดงข้อผิดพลาด |
| LED สีเขียว (Status) | 4 | `LED_GREEN` | Output | แสดงสถานะปกติ |
| **ปุ่มกด (Buttons)** |
| Button 1 (Select) | 34 | `BUTTON_1` | Input-only | ต้องใช้ external pull-down 10K |
| Button 2 (Up) | 35 | `BUTTON_2` | Input-only | ต้องใช้ external pull-down 10K |
| Button 3 (Down/Exit) | 39 | `BUTTON_3` | Input-only | ต้องใช้ external pull-down 10K |
| **เซ็นเซอร์ (Sensors)** |
| pH Sensor | 25 | `PH_PIN` | ADC | อ่านแรงดัน 0-3.3V |
| DS18B20 Temperature | 16 | `DS18B20_PIN` | OneWire | ต้องใช้ pull-up 4.7K |
| **ตัวกระตุ้น (Actuators)** |
| Pump (ปั๊ม) | 21 หรือ 22 | `PUMP_PIN` | PWM | ต่อ CONTROL_1 (21) หรือ CONTROL_2 (22) |
| Buzzer | 26 | `BUZZER_PIN` | PWM | เสียงแจ้งเตือน |
| **Potentiometers** |
| POT1 | 32 | `POT1_PIN` | ADC | ปรับค่า |
| POT2 | 33 | `POT2_PIN` | ADC | ปรับค่า |

### ขา GPIO สำหรับปั๊ม (Pump GPIO Options)

นิสิตเลือกต่อปั๊มที่ CONTROL_1 หรือ CONTROL_2 บน DEVICES header แล้วตั้ง PUMP_PIN ให้ตรง:

| อุปกรณ์ | GPIO | ค่าคงที่ใน config.py | หมายเหตุ |
|---------|:----:|---------------------|----------|
| CONTROL_1 | 21 | `CONTROL_1_PIN` | ต่อปั๊มที่นี่ → PUMP_PIN = CONTROL_1_PIN |
| CONTROL_2 | 22 | `CONTROL_2_PIN` | ต่อปั๊มที่นี่ → PUMP_PIN = CONTROL_2_PIN |
| Relay | 17 | `RELAY_PIN` | รีเลย์ควบคุม |

### ขา TFT Display (SPI Bus 1)

| สัญญาณ | GPIO | ค่าคงที่ |
|--------|:----:|---------|
| SCK | 14 | `TFT_SCK` |
| MOSI | 13 | `TFT_MOSI` |
| DC | 27 | `TFT_DC` |
| CS | 15 | `TFT_CS` |
| RST | 0 | `TFT_RST` |

### การเก็บข้อมูล (Data Storage)

> **หมายเหตุสำคัญ:** ระบบ TitraLab ไม่ใช้ SD Card
>
> เนื่องจากบอร์ด TitraLab เชื่อมต่อกับ laptop ของนิสิตผ่าน USB ตลอดเวลาระหว่างการทดลอง
> ไฟล์ CSV จะถูกบันทึกลงใน **ESP32 flash storage** โดยตรง และนิสิตสามารถ
> ดาวน์โหลดไฟล์ผ่าน **Thonny IDE** ได้ทันที

| รายการ | รายละเอียด |
|--------|------------|
| ที่เก็บข้อมูล | ESP32 Flash Storage |
| รูปแบบไฟล์ | CSV |
| ตัวอย่างชื่อไฟล์ | `titration_data_R1.csv` |
| วิธีดาวน์โหลด | ใช้ Thonny IDE (ดูขั้นตอนด้านล่าง) |

---

## หลักการทางเคมี (Chemistry Principles)

### สมการ Nernst (Nernst Equation)

หัววัด pH ให้สัญญาณแรงดันไฟฟ้าตามสมการ Nernst:

```
E = E0 - (2.303RT/nF) x pH
```

ที่อุณหภูมิ 25 C: slope ทฤษฎี = -59.16 mV/pH

### สมการสอบเทียบ pH รูปแบบ Direct-Use

ในระบบ TitraLab ใช้สมการในรูปแบบ **direct-use** (ใช้งานตรง):

```
pH = slope_m * mV + intercept_b
```

โดย:
- **slope_m** = ความชัน (pH/mV)
  - ค่าทฤษฎีที่ 25 C: 1/(-59.16) = **-0.0169 pH/mV**
- **intercept_b** = ค่า pH เมื่อ mV = 0 (ประมาณ **34-36 pH**)

**ทำไมใช้รูปแบบนี้?**
- ใช้งานทันทีจากค่า mV ที่ ADC อ่านได้ ไม่ต้องกลับสมการ (no inversion needed)
- ลดโอกาสผิดพลาดจากการคำนวณ
- โค้ดเข้าใจง่าย: `ph_value = slope_m * voltage_mv + intercept_b`

### ความสัมพันธ์ ADC - mV - pH

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  pH Probe   │ ───► │  ADC Value  │ ───► │     mV      │ ───► │   pH Value  │
│  (แรงดัน)   │      │   (0-4095)  │      │   (0-3300)  │      │   (0-14)    │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
                            │                    │                    │
                            ▼                    ▼                    ▼
                     mV = ADC/4095 x 3300   pH = slope_m * mV + intercept_b
```

### การกรองสัญญาณ ADC แบบ Robust (Robust ADC Filtering)

ระบบใช้ **IQR-based Outlier Rejection** (Tukey's Fences) เพื่อกำจัดค่าผิดปกติจาก ADC glitches:

```
การอ่านค่าแบบ Robust (Robust Reading Process):

25 ADC samples ─► Sort ─► Calculate Q1, Q3, IQR ─► Define bounds ─► Reject outliers ─► Average
   (20ms apart)           (percentiles)            [Q1-1.5*IQR,      (outside bounds)
                                                    Q3+1.5*IQR]
```

**ข้อดี:**
- กำจัด extreme outliers ได้ (เช่น pH=26.9 แทนที่จะเป็น ~11.7)
- ไม่ต้องรู้ค่าที่คาดหวังล่วงหน้า (adaptive threshold)
- เป็นวิธีมาตรฐานทางสถิติ (ใช้ใน box plots)

**ค่าคงที่ใน config.py:**
| ค่าคงที่ | ค่า | ความหมาย |
|---------|-----|---------|
| `ADC_ROBUST_SAMPLES` | 25 | จำนวนตัวอย่าง |
| `ADC_SAMPLE_DELAY_MS` | 20 | หน่วงเวลาระหว่างตัวอย่าง (ms) |
| `ADC_IQR_FACTOR` | 1.5 | ตัวคูณ Tukey มาตรฐาน |

**เวลาที่ใช้:** ~500ms ต่อการอ่าน (เพิ่มจาก ~100ms แต่ robust กว่ามาก)

### การตรวจจับจุดสมมูล (Equivalence Point Detection)

ระบบใช้วิธี derivative เพื่อหาจุดสมมูล โดยแต่ละจุดห่างกัน 0.2 mL:

![Titration Curve Analysis - การวิเคราะห์เส้นโค้งไทเทรชัน](../../EquivPoint/data.png)

**กราฟแสดง 3 ส่วน (3-Panel Plot):**
1. **Titration Curve** - เส้นโค้งไทเทรชัน (pH vs Volume) พร้อม spline fit
2. **First Derivative** - อนุพันธ์อันดับหนึ่ง (dpH/dV) จุดสูงสุดคือจุดสมมูล
3. **Second Derivative** - อนุพันธ์อันดับสอง จุดตัดศูนย์ (zero crossing) คือจุดสมมูล

**เนื่องจากใช้ constant dose volume (0.2 mL):**
- `dpH/dV = (pH[i] - pH[i-1]) / 0.2` (ตัวหารคงที่ทุก step)
- จุดสมมูลคือ step ที่ `|pH[i] - pH[i-1]|` มากที่สุด (เพราะ dV คงที่)
- นิสิตเข้าใจได้ง่าย: "หา step ที่ pH กระโดดมากที่สุด"

---

## OOP Design Patterns (รูปแบบการออกแบบ OOP)

Week 3 แสดงตัวอย่างการใช้ OOP Design Patterns หลายรูปแบบ:

### 1. Hardware Hub Pattern (Facade Pattern)

`main.py` ใช้ HardwareHub เป็นศูนย์รวมการจัดการ Hardware ทั้งหมด:

```python
# จาก main.py (บรรทัด 45-61)
class HardwareHub:
    """
    ศูนย์รวมการจัดการ Hardware ทั้งหมด
    Central hub for all hardware management
    """

    def __init__(self):
        # สร้าง hardware objects ทั้งหมดในที่เดียว
        self.display = DisplayManager()
        self.buttons = ButtonManager()
        self.pump = Pump()
        self.ph_sensor = PHSensor()
        self.temp_sensor = TemperatureSensor()
        self.buzzer = Buzzer()
        self.leds = LEDManager()
        # หมายเหตุ: ไม่ใช้ SD Card - CSV บันทึกใน ESP32 flash โดย TitrationController
```

**ข้อดี:**
- รวมการเริ่มต้น hardware ไว้ที่เดียว
- ง่ายต่อการจัดการ lifecycle (init/deinit)
- ลดความซับซ้อนของ main()

### 2. Dependency Injection Pattern

`main.py` ส่ง hardware objects ไปยังคลาสอื่นผ่าน constructor:

```python
# จาก main.py (บรรทัด 173-191)
# สร้าง Calibrator - ส่ง dependencies ผ่าน constructor
calibrator = Calibrator(
    ph_sensor=hardware.ph_sensor,
    pump=hardware.pump,
    display=hardware.display,
    buttons=hardware.buttons,
    buzzer=hardware.buzzer,
    data_manager=data_manager
)

# สร้าง Titration Controller
titration = TitrationController(
    pump=hardware.pump,
    ph_sensor=hardware.ph_sensor,
    temp_sensor=hardware.temp_sensor,
    display=hardware.display,
    buzzer=hardware.buzzer,
    led_indicator=hardware.leds.green
)
# หมายเหตุ: CSV บันทึกใน ESP32 flash โดยตรง (ดาวน์โหลดผ่าน Thonny IDE)

# โหลดค่าสอบเทียบที่บันทึกไว้ (Load saved calibration at startup)
slope_m, intercept_b, r_squared, cal_temp = data_manager.load_ph_calibration()
if slope_m is not None and intercept_b is not None:
    hardware.ph_sensor.set_calibration(slope_m, intercept_b)

flow_rate, _ = data_manager.load_flow_rate()
if flow_rate is not None:
    hardware.pump.flow_rate = flow_rate
```

> **หมายเหตุสำคัญ:** เมื่อเริ่มโปรแกรม `main.py` จะโหลดค่าสอบเทียบ pH (`data_calibrate.txt`) และ flow rate (`data_flowrate.txt`) อัตโนมัติ
> ทำให้ไม่ต้องสอบเทียบใหม่ทุกครั้งที่รีสตาร์ท หากยังไม่เคยสอบเทียบ ระบบจะใช้ค่า default
>
> **Important:** On startup, `main.py` automatically loads saved pH calibration and flow rate from files.
> Students don't need to recalibrate after every restart. If no calibration files exist, default values are used.

**ข้อดี:**
- ทดสอบง่าย (สามารถส่ง mock objects ได้)
- ความยืดหยุ่นสูง
- เห็น dependencies ชัดเจน

### 3. State Pattern (ในระบบเมนู)

แต่ละโหมดเป็น state ที่แยกจากกัน:

```python
# จาก main.py (บรรทัด 201-208)
menu_actions = {
    1: lambda: calibrator.calibrate_ph(),        # Mode 1
    2: lambda: calibrator.test_ph_sensor(),      # Mode 2
    3: lambda: calibrator.calibrate_flow_rate(), # Mode 3
    4: lambda: calibrator.test_flow_rate(),      # Mode 4
    5: lambda: hardware.pump.purge(),            # Mode 5
    6: lambda: titration.run_titration()         # Mode 6
}
```

### 4. Template Method Pattern (ใน modes/)

`base_mode.py` กำหนดโครงสร้างการทำงาน และ mode ย่อยแต่ละตัว override เฉพาะส่วนที่ต้องการ:

```python
# แนวคิด Template Method
class BaseMode:
    def run(self):
        self.setup()      # ขั้นตอน 1: เตรียมการ
        self.execute()    # ขั้นตอน 2: ทำงานหลัก
        self.cleanup()    # ขั้นตอน 3: ทำความสะอาด

class CalibratePHMode(BaseMode):
    def execute(self):
        # Override เฉพาะส่วนการสอบเทียบ pH
        pass
```

### ตารางสรุป Design Patterns

| Pattern | ใช้ที่ไหน | วัตถุประสงค์ |
|---------|----------|-------------|
| **Facade** | `main.py` HardwareHub | ซ่อนความซับซ้อนของ hardware |
| **Dependency Injection** | constructor ทุกคลาส | ลด coupling, ทดสอบง่าย |
| **State** | `modes/*.py` | แยกพฤติกรรมแต่ละโหมด |
| **Template Method** | `base_mode.py` | กำหนดโครงสร้างการทำงาน |
| **Singleton** | config constants | ค่าคงที่ใช้ร่วมกัน |

### Memory Optimization (การปรับแต่งหน่วยความจำ)

ESP32 มี RAM จำกัด (~520KB ทั้งหมด, ~300KB ใช้งานได้จริง) ดังนั้นต้องออกแบบโค้ดอย่างระมัดระวัง:

**เทคนิคที่ใช้:**

| เทคนิค | คำอธิบาย | ประโยชน์ |
|--------|----------|----------|
| **ลบ test code** | ลบ `if __name__ == "__main__":` ออกจากทุกโมดูล | ประหยัด ~750 บรรทัด |
| **Lazy imports** | `core/__init__.py` ไม่ auto-import ทุกคลาส | โหลดเมื่อใช้งานจริง |
| **Strategic gc.collect()** | เรียก garbage collector ก่อนสร้าง objects ใหญ่ | คืนหน่วยความจำ |
| **Ordered creation** | สร้าง display (ใช้ RAM มาก) สุดท้าย | ลดโอกาส MemoryError |

**ลำดับการสร้าง Hardware Objects:**
```
1. buttons (น้อย)  →  2. leds (น้อย)  →  3. buzzer (น้อย)
                               ↓
4. ph_sensor (กลาง)  →  5. temp_sensor (กลาง)  →  6. pump (กลาง)
                               ↓
                    7. display (มาก) ← สร้างสุดท้าย
```

**เปรียบเทียบกับหลักการทางเคมี:**
เหมือนกับการเตรียมสารละลายในห้องปฏิบัติการ - เตรียมสารปริมาณน้อยก่อน
แล้วค่อยเตรียมสารปริมาณมากภายหลัง เพื่อให้ใช้ภาชนะได้อย่างมีประสิทธิภาพ

---

## ตารางเวลาการสอน 3 ชั่วโมง (Teaching Schedule)

| ช่วงเวลา | หัวข้อ | กิจกรรม | เวลา |
|:--------:|--------|---------|:----:|
| **ชั่วโมงที่ 1** | **ภาพรวมและการเตรียมตัว** | | **60 นาที** |
| 0:00-0:15 | แนะนำระบบ Week 3 | อธิบายโครงสร้าง, 6 โหมด | 15 นาที |
| 0:15-0:30 | ตรวจสอบการสอบเทียบ | ใช้ Mode 2 (Test pH) | 15 นาที |
| 0:30-0:45 | ตรวจสอบ flow rate | ใช้ Mode 4 (Test Flow) | 15 นาที |
| 0:45-1:00 | Purge และเตรียมสารละลาย | ใช้ Mode 5 (Purge) | 15 นาที |
| **ชั่วโมงที่ 2** | **ปฏิบัติการไทเทรต** | | **60 นาที** |
| 1:00-1:15 | เตรียมสารตัวอย่าง | HCl ความเข้มข้นไม่ทราบค่า | 15 นาที |
| 1:15-1:45 | ไทเทรตครั้งที่ 1 | ใช้ Mode 6 (Full Auto) | 30 นาที |
| 1:45-2:00 | บันทึกผลและวิเคราะห์ | ดูผลบน TFT และดาวน์โหลดไฟล์ CSV | 15 นาที |
| **ชั่วโมงที่ 3** | **ไทเทรตซ้ำและสรุป** | | **60 นาที** |
| 2:00-2:30 | ไทเทรตครั้งที่ 2-3 | ซ้ำเพื่อหาค่าเฉลี่ย | 30 นาที |
| 2:30-2:45 | คำนวณความเข้มข้น | C1V1 = C2V2 | 15 นาที |
| 2:45-3:00 | สรุปและ Q&A | อภิปราย, แก้ไขปัญหา | 15 นาที |

---

## ขั้นตอนการทดลอง (Lab Procedure)

### ก่อนเริ่มปฏิบัติการ (Before Lab)

1. **ตรวจสอบการสอบเทียบ pH** - ควรทำใน Week 2 หรือใช้ Mode 1
2. **ตรวจสอบอัตราการไหล** - ควรทำใน Week 2 หรือใช้ Mode 3
3. **เตรียมสารละลาย** - สารตัวอย่าง (analyte) และสารไทแทรนต์ (titrant)

### เริ่มปฏิบัติการ (Lab Procedure)

```
Step 1: Purge (ล้างท่อ)
        │
        ▼
Step 2: ใส่สารตัวอย่างในบีกเกอร์ + แช่หัววัด pH
        │
        ▼
Step 3: จุ่มท่อปั๊มในสารไทแทรนต์
        │
        ▼
Step 4: เลือก Mode 6 (Full Auto Titration)
        │
        ▼
Step 5: รอจนการไทเทรตเสร็จสิ้น
        │
        ▼
Step 6: บันทึกผลจากหน้าจอและดาวน์โหลดไฟล์ CSV
```

### หลังปฏิบัติการ (After Lab)

1. **ดูผลบนหน้าจอ** - ปริมาตรที่จุดสมมูล, pH ที่จุดสมมูล
2. **ดาวน์โหลดไฟล์ CSV จาก ESP32** - ใช้ Thonny IDE (ดูขั้นตอนด้านล่าง)
3. **วิเคราะห์ข้อมูลด้วย EquivPoint** - หาจุดสมมูลที่แม่นยำ
4. **ล้างอุปกรณ์** - ล้างหัววัด pH และท่อปั๊มด้วยน้ำ DI

---

## การใช้งานปุ่มกด (Button Controls)

```
+------------------+------------------+------------------+
|    Button 1      |    Button 2      |    Button 3      |
|    GPIO34        |    GPIO35        |    GPIO39        |
+------------------+------------------+------------------+
|    SELECT        |      UP          |    DOWN/CANCEL   |
| เริ่ม/ยืนยัน/หยุด  |     เลื่อนขึ้น     |  เลื่อนลง/ยกเลิก  |
+------------------+------------------+------------------+
                                      |  กดค้าง 3 วินาที  |
                                      |   = ออกโปรแกรม   |
                                      +------------------+
```

### การใช้ปุ่มในแต่ละสถานการณ์

| สถานการณ์ | Button 1 | Button 2 | Button 3 |
|-----------|----------|----------|----------|
| หน้าเมนูหลัก | เลือกโหมด | เลื่อนขึ้น | เลื่อนลง |
| ก่อนเริ่มทำงาน (Ready screen) | **เริ่ม (Start)** | - | **ยกเลิก (Cancel)** |
| สอบเทียบ pH | **ยืนยันค่า** | - | **ยกเลิก** |
| Mode 5 Purge (ขณะปั๊มทำงาน) | **หยุดปั๊ม** | - | - |
| ระหว่างไทเทรชัน | - | - | **ยกเลิก** |
| กดค้าง 3 วินาที | - | - | ออกโปรแกรม |

### Button 1 ทำงานแตกต่างกันตามบริบท (Context-Dependent)

| บริบท | การกด BTN1 ทำอะไร |
|--------|------------------|
| หน้าเมนูหลัก | เลือกโหมดที่ highlight |
| ก่อนเริ่มทำงาน (Ready) | เริ่มทำงาน (Start) |
| สอบเทียบ pH แต่ละจุด | ยืนยันค่าและไปจุดถัดไป |
| Mode 5 Purge (ปั๊มทำงาน) | หยุดปั๊ม (Stop) |

### Button 3 สำหรับยกเลิกทุกโหมด

BTN3 สามารถยกเลิกการทำงานได้ในทุกโหมด:
- ก่อนเริ่มทำงาน: กลับไปหน้าเมนูหลัก
- ระหว่างไทเทรชัน: หยุดไทเทรชันทันที (ข้อมูลที่เก็บแล้วยังอยู่)

---

## ผลลัพธ์ที่คาดหวัง (Expected Results)

### บนหน้าจอ TFT

- กราฟ Titration Curve (pH vs Volume)
- ค่า pH และปริมาตรที่จุดสมมูล (Equivalence Point)
- สถานะการทำงาน (กำลังเติม, ใกล้จุดสมมูล, เสร็จสิ้น)

### ไฟล์ CSV บน ESP32 Flash Storage

ไฟล์ CSV ที่บันทึกลง ESP32 มีรูปแบบที่ใช้ได้กับ **EquivPoint** โดยตรง:
```
Volume (mL),pH Value,Time(s),Temperature(C)
0.200,2.50,2.50,25.1
0.400,2.55,5.00,25.1
0.600,2.61,7.50,25.1
...
```

> **สังเกต**:
> - ปริมาตรเพิ่มขึ้นคงที่ทีละ 0.200 mL ทุก step
> - รูปแบบไฟล์ใช้ได้กับ EquivPoint โดยไม่ต้องแปลงคอลัมน์
> - Header ใช้ `Volume (mL)` และ `pH Value` ตามที่ EquivPoint ต้องการ

> **วิธีดาวน์โหลดไฟล์ CSV จาก ESP32 ผ่าน Thonny IDE:**
>
> 1. เปิด Thonny IDE และเชื่อมต่อ ESP32 ผ่าน USB
> 2. ในหน้าต่าง "Files" ด้านซ้าย จะเห็นไฟล์บน ESP32 (MicroPython device)
> 3. คลิกขวาที่ไฟล์ `titration_data_R1.csv`
> 4. เลือก "Download to..." และบันทึกไปยังโฟลเดอร์ EquivPoint
> 5. หรือลากไฟล์จาก ESP32 ไปยังโฟลเดอร์บนคอมพิวเตอร์

### ตัวอย่างผลลัพธ์การไทเทรตกรดแก่-เบสแก่

```
Equivalence Point Found!
========================
Volume: 25.32 mL
pH: 7.02
Temperature: 25.1 C

Calculated Concentration:
C_analyte = (C_titrant * V_titrant) / V_analyte
```

---

## การแก้ไขปัญหา (Troubleshooting)

### ปัญหา: ค่า pH ไม่เสถียร (pH readings unstable)

**สาเหตุ:**
- หัววัดไม่สะอาด
- สารละลายไม่คนให้เข้ากัน
- หัววัดเสื่อมสภาพ

**วิธีแก้:**
- ล้างหัววัดด้วยน้ำ DI
- คนสารละลายเบาๆ ขณะวัด
- ตรวจสอบสภาพหัววัด (ควรเปลี่ยนทุก 1-2 ปี)

---

### ปัญหา: ค่า pH ผิดปกติรุนแรง (Extreme pH reading errors)

**ตัวอย่าง:** pH อ่านได้ 26.9 หรือ 0.8 แทนที่จะเป็น ~11.7

**สาเหตุ:**
- ADC glitch จากสัญญาณรบกวนไฟฟ้า
- สัญญาณรบกวนจากมอเตอร์ปั๊ม

**วิธีแก้:**
- ระบบใช้ **IQR-based outlier rejection** (Tukey's Fences) อัตโนมัติ
- เก็บตัวอย่าง 25 ค่า คำนวณ Q1, Q3, IQR แล้วตัดค่านอกขอบเขตออก
- ถ้ายังมีปัญหา: ตรวจสอบการต่อสายกราวด์และห่างจากมอเตอร์

**หมายเหตุ:** การกรองแบบ robust ทำงานอัตโนมัติ ไม่ต้องตั้งค่าเพิ่มเติม

---

### ปัญหา: ปั๊มไม่ทำงาน (Pump not working)

**วิธีตรวจสอบ:**
```python
# ทดสอบปั๊มโดยตรง
from machine import Pin, PWM
pwm = PWM(Pin(21), freq=1000)
pwm.duty(1023)  # ปั๊มควรทำงาน
# รอ 2 วินาที
pwm.duty(0)     # หยุดปั๊ม
pwm.deinit()
```

**สาเหตุที่เป็นไปได้:**
- สายไฟหลุด
- แหล่งจ่ายไฟไม่เพียงพอ
- ต่อปั๊มที่ CONTROL_2 แต่ config.py ยังใช้ CONTROL_1_PIN

---

### ปัญหา: Temperature Sensor ล้มเหลว (Temperature sensor failure)

**อาการ:**
- แสดงข้อความ "Temp sensor failed, using default 25C"
- อุณหภูมิแสดง 25.0C ตลอด

**สาเหตุและวิธีแก้:**
| สาเหตุ | วิธีแก้ |
|--------|--------|
| สายจัมเปอร์หลุด | ตรวจสอบสาย GPIO16 -> DS18B20 |
| ไม่มี pull-up resistor | ต้องมี 4.7K pull-up ระหว่าง VCC กับ DATA |
| DS18B20 เสีย | เปลี่ยน sensor ใหม่ |

**หมายเหตุ:** ระบบยังคงทำงานได้แม้ไม่มี temperature sensor แต่จะใช้ค่า 25C เป็นค่าเริ่มต้น

---

### ปัญหา: R-squared ต่ำกว่า 0.99 (Poor calibration)

**สาเหตุ:**
- บัฟเฟอร์หมดอายุหรือปนเปื้อน
- ไม่ได้ล้างหัววัดระหว่างเปลี่ยนบัฟเฟอร์
- อ่านค่าก่อนที่หัววัดจะเสถียร

**วิธีแก้:**
- ใช้บัฟเฟอร์ใหม่
- ล้างหัววัดด้วยน้ำ DI ก่อนเปลี่ยนบัฟเฟอร์
- รอ 30-60 วินาทีให้ค่าเสถียรก่อนบันทึก

---

### ปัญหา: ไม่พบจุดสมมูล (Equivalence point not detected)

**สาเหตุ:**
- ความเข้มข้นสารไม่เหมาะสม
- สารไทแทรนต์ไม่ถูกต้อง
- ปริมาตรเกินขีดจำกัด (50 mL)

**วิธีแก้:**
- ตรวจสอบความเข้มข้นของสารละลาย
- ตรวจสอบว่าใช้กรด-เบสคู่ที่ถูกต้อง
- เพิ่มความเข้มข้นสารไทแทรนต์

---

### ปัญหา: ไม่พบไฟล์ CSV บน ESP32 (CSV file not found on ESP32)

**วิธีตรวจสอบ:**
```python
# ใน Thonny REPL พิมพ์:
import os
files = os.listdir('/')
print(f"Files on ESP32: {files}")
```

**สาเหตุที่เป็นไปได้:**
- การไทเทรตถูกยกเลิกก่อนบันทึกไฟล์
- ESP32 flash storage เต็ม
- ชื่อไฟล์อาจต่างจากที่คาดไว้

**วิธีแก้:**
- ตรวจสอบรายชื่อไฟล์ใน Thonny IDE (หน้าต่าง Files ด้านซ้าย)
- ลบไฟล์เก่าที่ไม่ใช้แล้วเพื่อเพิ่มพื้นที่
- รันการไทเทรตใหม่และรอจนจบ

---

### ปัญหา: File creation error บนจอ TFT (File creation error on TFT)

**อาการ:**
- แสดงข้อความ "File creation error" บนจอ TFT
- ไม่สามารถเริ่มไทเทรชันได้

**สาเหตุและวิธีแก้:**
| สาเหตุ | วิธีแก้ |
|--------|--------|
| Flash storage เต็ม | ลบไฟล์เก่าออก |
| ไฟล์ระบบเสียหาย | รีสตาร์ท ESP32 |
| สิทธิ์เขียนผิดพลาด | อัปโหลดไฟล์ทั้งหมดใหม่ |

---

### ปัญหา: ข้อมูลสูญหายหลังไฟดับ (Data loss after power failure)

**วิธีป้องกัน (ระบบทำอัตโนมัติแล้ว):**
- ระบบใช้ `f.flush()` หลังเขียนทุกบรรทัดใน CSV
- ข้อมูลจะถูก sync ลง flash ทันที

**ถ้าข้อมูลยังสูญหาย:**
- ตรวจสอบว่าใช้เวอร์ชันล่าสุด (v3.6.0)
- ข้อมูลที่เขียนก่อนไฟดับควรยังอยู่
- ข้อมูล 1-2 บรรทัดสุดท้ายอาจหายได้ในกรณีที่ไฟดับทันที

---

## เกณฑ์ความสำเร็จ (Success Criteria)

### เกณฑ์ผ่านขั้นต่ำ (Minimum Requirements)

| รายการ | เกณฑ์ | สถานะ |
|--------|-------|:-----:|
| สอบเทียบ pH สำเร็จ | R-squared >= 0.99 | [ ] |
| สอบเทียบ flow rate สำเร็จ | %RSD <= 5% (วัด >= 3 ครั้ง) | [ ] |
| ไทเทรตสำเร็จอย่างน้อย 1 ครั้ง | พบจุดสมมูล | [ ] |
| บันทึกและดาวน์โหลดข้อมูล | ไฟล์ CSV จาก ESP32 สมบูรณ์ | [ ] |
| วิเคราะห์ข้อมูลด้วย EquivPoint | หาจุดสมมูลจากกราฟ | [ ] |

### เกณฑ์ผ่านระดับดี (Good Performance)

| รายการ | เกณฑ์ | สถานะ |
|--------|-------|:-----:|
| สอบเทียบ flow rate ดีเยี่ยม | %RSD <= 3% (Excellent!) | [ ] |
| ไทเทรตซ้ำ 3 ครั้ง | ค่า Ve ใกล้เคียงกัน (%RSD < 3%) | [ ] |
| คำนวณความเข้มข้นถูกต้อง | ตรงกับค่าทฤษฎี +/- 5% | [ ] |

### การประเมินทักษะ OOP (OOP Skills Assessment)

| ทักษะ | ตัวอย่างในโค้ด | เข้าใจ |
|-------|---------------|:------:|
| Hardware Abstraction | `hardware/*.py` | [ ] |
| Dependency Injection | `main.py` HardwareHub | [ ] |
| State Pattern | `modes/*.py` | [ ] |
| Try/Finally Cleanup | `main.py` main() | [ ] |

---

## การวิเคราะห์ข้อมูลด้วย EquivPoint (Data Analysis with EquivPoint)

หลังจากทำการไทเทรตและได้ข้อมูล CSV จาก ESP32 แล้ว นิสิตสามารถใช้เครื่องมือ **EquivPoint**
ซึ่งเป็นโปรแกรม Python สำหรับวิเคราะห์หาจุดสมมูล (equivalence point) ได้อย่างแม่นยำยิ่งขึ้น

### ภาพรวมขั้นตอนการทำงาน (Workflow Overview)

```
                    การไหลของข้อมูล (Data Flow)
══════════════════════════════════════════════════════════════════════════════════

   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
   │    TitraLab     │      │    Thonny IDE   │      │   EquivPoint    │
   │    (ESP32)      │      │   (Download)    │      │   (Analysis)    │
   │                 │      │                 │      │                 │
   │  Mode 6: Full   │      │  ดาวน์โหลดไฟล์   │      │  วิเคราะห์ข้อมูล  │
   │  Auto Titration │─────►│  จาก ESP32      │─────►│  Python Tool    │
   │                 │      │  ผ่าน USB       │      │                 │
   │  บันทึก CSV     │      │                 │      │  Spline + Deriv │
   │  ลง Flash       │      │                 │      │                 │
   └─────────────────┘      └─────────────────┘      └─────────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
    1. ทำการทดลอง          2. ดาวน์โหลด CSV         3. รัน EquivPoint
       บนบอร์ด                จาก ESP32                หาจุดสมมูล

══════════════════════════════════════════════════════════════════════════════════
```

### ขั้นตอนการถ่ายโอนข้อมูล (Data Transfer Steps)

#### Step 1: ดาวน์โหลดไฟล์ CSV จาก ESP32 (Download CSV from ESP32)

1. **เปิด Thonny IDE** และเชื่อมต่อ ESP32 ผ่าน USB
2. ในเมนู **View > Files** เพื่อเปิดหน้าต่าง Files (ถ้ายังไม่เปิด)
3. ด้านซ้ายล่าง จะเห็น **MicroPython device** แสดงไฟล์บน ESP32
4. หาไฟล์ `titration_data_R1.csv` (หรือชื่อที่คล้ายกัน)
5. **คลิกขวา** ที่ไฟล์ แล้วเลือก **"Download to..."**
6. บันทึกไปยังโฟลเดอร์ `EquivPoint/` ในโปรเจกต์ TitraLab:
   ```
   TitraLab/EquivPoint/
   ```

#### Step 2: ใช้ไฟล์ CSV ได้ทันที (CSV Ready to Use)

ไฟล์ CSV จาก TitraLab Week 3 **ใช้ได้กับ EquivPoint โดยตรง** ไม่ต้องแปลงรูปแบบ:

**รูปแบบจาก TitraLab (ปริมาตรเพิ่มทีละ 0.2 mL):**
```csv
Volume (mL),pH Value,Time(s),Temperature(C)
0.200,2.50,2.50,25.1
0.400,2.55,5.00,25.1
0.600,2.61,7.50,25.1
```

> **หมายเหตุ:** EquivPoint อ่านคอลัมน์ `Volume (mL)` และ `pH Value` โดยอัตโนมัติ
> คอลัมน์เพิ่มเติม (Time, Temperature) จะถูกข้ามไป

### EquivPoint คืออะไร? (What is EquivPoint?)

EquivPoint เป็นเครื่องมือวิเคราะห์ข้อมูลบนคอมพิวเตอร์ (Desktop Python Tool) ที่ใช้:
- **Spline Interpolation** - การประมาณค่าด้วยเส้นโค้งเรียบ (smooth curve fitting)
- **First Derivative** - อนุพันธ์อันดับหนึ่ง (dpH/dV) หาจุดที่เปลี่ยนแปลงเร็วที่สุด
- **Second Derivative** - อนุพันธ์อันดับสอง (d2pH/dV2) หาจุดเปลี่ยนแปลงความโค้ง (inflection point)

### ทำไมต้องใช้ EquivPoint? (Why Use EquivPoint?)

| วิธีการ | ข้อดี | ข้อจำกัด |
|---------|-------|----------|
| TitraLab (บนบอร์ด) | เห็นผลทันที | ความแม่นยำจำกัด, ไม่มีกราฟละเอียด |
| EquivPoint (บนคอมพิวเตอร์) | แม่นยำสูง, กราฟสวยงาม, บันทึกรูปภาพได้ | ต้องดาวน์โหลดไฟล์จาก ESP32 ก่อน |

**แนะนำ:** ใช้ทั้งสองวิธีร่วมกัน - TitraLab สำหรับดูผลเบื้องต้น และ EquivPoint สำหรับวิเคราะห์อย่างละเอียด

### ขั้นตอนการใช้งาน EquivPoint (EquivPoint Usage Steps)

#### Step 3: ติดตั้งโปรแกรม (Installation) - ทำครั้งแรกครั้งเดียว

```bash
# เปิด Command Prompt หรือ Terminal
# ไปยังโฟลเดอร์ EquivPoint ในโปรเจกต์ TitraLab
# (ปรับ path ตามตำแหน่งที่เก็บโปรเจกต์บนเครื่องของนิสิต)
cd <your-path>/TitraLab/EquivPoint

# สร้าง Virtual Environment (ทำครั้งแรกครั้งเดียว)
python -m venv venv

# เปิดใช้งาน Virtual Environment (Windows)
venv\Scripts\activate

# ติดตั้ง dependencies จาก requirements.txt
pip install -r requirements.txt
```

#### Step 4: รันโปรแกรม EquivPoint (Run EquivPoint)

```bash
# เปิดใช้งาน venv (ถ้ายังไม่เปิด)
cd <your-path>/TitraLab/EquivPoint
venv\Scripts\activate

# รันโปรแกรมวิเคราะห์
python equiv_point.py titration_data_R1.csv
```

#### Step 5: อ่านผลลัพธ์ (Interpret Results)

โปรแกรมจะแสดง 3 กราฟ:

![EquivPoint Analysis Output - ผลลัพธ์การวิเคราะห์](../../EquivPoint/data.png)

**คำอธิบายกราฟ (Graph Description):**

| กราฟ | ชื่อ | คำอธิบาย |
|:----:|------|----------|
| 1 | Titration Curve | ข้อมูลจริง (จุดสีน้ำเงิน) + Spline fit (เส้นสีส้ม) |
| 2 | First Derivative | dpH/dV - จุดสูงสุด (★) คือจุดสมมูล |
| 3 | Second Derivative | d²pH/dV² - เส้นประสีแดงคือ zero crossing (จุดสมมูล) |

**ตัวอย่างผลลัพธ์ใน Console:**
```
Approximate volume at zero crossing: 5.58 mL
```

ค่า 5.58 mL คือปริมาตรที่จุดสมมูล (Equivalence Point Volume)

### เปรียบเทียบผลลัพธ์ (Compare Results)

| แหล่งข้อมูล | ปริมาตรจุดสมมูล | หมายเหตุ |
|-------------|-----------------|----------|
| TitraLab (หน้าจอ TFT) | ~5.5 mL | ค่าประมาณจาก simple derivative |
| EquivPoint | 5.58 mL | ค่าแม่นยำจาก spline interpolation |

### โครงสร้างโฟลเดอร์ EquivPoint (EquivPoint Folder Structure)

```
TitraLab/                    <-- โฟลเดอร์หลักของโปรเจกต์
├── MicroPython/
│   └── Week_3/              <-- คุณอยู่ที่นี่
│       └── README.md
└── EquivPoint/              <-- เครื่องมือวิเคราะห์ข้อมูล
    ├── README.md            # คู่มือการใช้งาน EquivPoint
    ├── requirements.txt     # Python dependencies
    ├── equiv_point.py       # โปรแกรมหลัก
    ├── data.csv             # ไฟล์ตัวอย่าง
    ├── data.png             # กราฟตัวอย่าง
    ├── venv/                # Virtual environment (สร้างขึ้นหลังติดตั้ง)
    └── titration_data_R1.csv  # <-- คัดลอกไฟล์จาก ESP32 มาที่นี่
```

### การเชื่อมโยงกับหลักการทางเคมี (Connection to Chemistry Principles)

วิธีการหาจุดสมมูลด้วย derivative มีพื้นฐานมาจากหลักการทางเคมี:

1. **จุดสมมูล (Equivalence Point)** - จุดที่กรดและเบสทำปฏิกิริยาพอดี (stoichiometric point)

2. **First Derivative Maximum** - ที่จุดสมมูล การเปลี่ยนแปลง pH ต่อปริมาตร (dpH/dV) จะมีค่าสูงสุด

3. **Second Derivative Zero Crossing** - จุดที่ d2pH/dV2 = 0 คือจุดเปลี่ยนแปลงความโค้ง (inflection point) ซึ่งตรงกับจุดสมมูล

```
หลักการทางคณิตศาสตร์ (Mathematical Principle):

ที่จุดสมมูล:
- dpH/dV = สูงสุด (maximum)
- d2pH/dV2 = 0 (zero crossing)
```

### คำถามท้ายบท (Discussion Questions)

1. ทำไมการใช้ spline interpolation ให้ผลแม่นยำกว่าการหา derivative จากข้อมูลดิบโดยตรง?
2. ถ้าข้อมูลมี noise มาก (ค่า pH กระโดด) ควรปรับ smoothing factor อย่างไร?
3. ทำไมจุด zero crossing ของ second derivative ถึงบอกจุดสมมูลได้?

---

## Quick Reference Card (บัตรอ้างอิงด่วน)

```
+--------------------------------------------------+
|              TitraLab Quick Reference             |
+--------------------------------------------------+
| เริ่มต้น:  import main; main.main()              |
+--------------------------------------------------+
| ก่อนไทเทรต:                                       |
|   1. Purge (Mode 5) - ไล่ฟองอากาศ               |
|   2. ตรวจสอบ pH sensor (Mode 2)                  |
+--------------------------------------------------+
| ไทเทรต:                                          |
|   - เลือก Mode 6 (Full Auto Titration)           |
|   - รอจนจบ ดูผลบนหน้าจอ                          |
+--------------------------------------------------+
| หลังไทเทรต:                                       |
|   1. ดาวน์โหลดไฟล์ CSV จาก ESP32 (Thonny IDE)    |
|   2. รัน EquivPoint วิเคราะห์จุดสมมูล             |
+--------------------------------------------------+
| ปุ่ม:                                            |
|   Button 1 = เริ่ม/ยืนยัน/หยุด (ตามบริบท)         |
|   Button 2 = ขึ้น                                |
|   Button 3 = ลง/ยกเลิก (กดค้าง 3 วินาที = ออก)    |
+--------------------------------------------------+
| ปัญหาเบื้องต้น:                                   |
|   - pH ไม่เสถียร -> ล้างหัววัด                   |
|   - ปั๊มไม่ทำงาน -> ตรวจสอบสายไฟ                 |
|   - R2 < 0.99 -> สอบเทียบใหม่                    |
+--------------------------------------------------+
```

---

## คำศัพท์สำคัญ (Key Terminology)

### คำศัพท์ทางเคมี (Chemistry Terms)

| ภาษาอังกฤษ | ภาษาไทย | คำอธิบาย |
|------------|---------|----------|
| Titration | ไทเทรชัน | การหาปริมาณสารด้วยการเติมสารไทแทรนต์ |
| Equivalence Point | จุดสมมูล | จุดที่สารทำปฏิกิริยาพอดีกัน |
| Endpoint | จุดยุติ | จุดที่ตรวจวัดได้จริง |
| Titrant | สารไทแทรนต์ | สารละลายที่ใช้หยดลงไป |
| Analyte | สารตัวอย่าง | สารละลายที่ต้องการวิเคราะห์ |
| Buffer Solution | สารละลายบัฟเฟอร์ | สารละลายที่มี pH คงที่ |
| Nernst Equation | สมการเนิร์นสต์ | ความสัมพันธ์ระหว่าง mV กับ pH |

### คำศัพท์ทางโปรแกรม (Programming Terms)

| ภาษาอังกฤษ | ภาษาไทย | คำอธิบาย |
|------------|---------|----------|
| Hardware Abstraction | การห่อหุ้มฮาร์ดแวร์ | ซ่อนความซับซ้อนของอุปกรณ์ |
| Dependency Injection | การฉีด dependencies | ส่ง objects ผ่าน constructor |
| State Pattern | รูปแบบสถานะ | แยกพฤติกรรมตามสถานะ |
| Facade Pattern | รูปแบบหน้าฉาก | รวมระบบย่อยเป็นหน้าตาเดียว |

---

## ผู้พัฒนา (Developers)

- Hemmawan Saon
- Nuttakit Deemon
- Saowapak Vchirawongkwin
- Sumrit Wacharasindhu
- Viwat Vchirawongkwin

**รายวิชา:** 2302311 Integrated Chemistry Laboratory I
**สถาบัน:** ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย

---

*Version 3.6.0 - Memory Optimization and Multi-Measurement Flow Calibration*
*สร้างเมื่อ: มกราคม 2026*
*อัปเดตล่าสุด: มกราคม 2026*

**การเปลี่ยนแปลงใน v3.6.0:**
- **Memory Optimization (การปรับแต่งหน่วยความจำ):**
  - ลบ test code (`if __name__ == "__main__":`) ออกจากทุกโมดูล (~750 บรรทัด) เพื่อประหยัด RAM
  - เพิ่ม strategic `gc.collect()` calls ใน main.py ก่อนสร้าง hardware objects
  - เปลี่ยน `core/__init__.py` ให้ใช้ lazy imports แทน auto-import ทั้งหมด
  - เรียงลำดับการสร้าง hardware: objects ที่ใช้หน่วยความจำน้อยก่อน, display สุดท้าย

- **Multi-Measurement Flow Rate Calibration (Mode 3):**
  - รองรับการวัดหลายครั้ง (แนะนำ 3-5 ครั้ง)
  - คำนวณสถิติ: ค่าเฉลี่ย, ส่วนเบี่ยงเบนมาตรฐาน (SD), %RSD
  - แสดงคำแนะนำคุณภาพ: RSD <= 3% "Excellent!", 3-5% "Good", >5% "Warning"
  - บันทึกทุกค่าที่วัดและสถิติลง data_flowrate.txt
  - ปุ่มควบคุม: BTN1=เริ่ม/หยุดปั๊ม, BTN2=บันทึกค่า, BTN3=บันทึกและออก

- **Bug Fixes (แก้ไขข้อบกพร่อง):**
  - แก้ floating-point volume drift: ใช้ `cycle_count * dose_volume` แทนการบวกสะสม
  - แก้เมธอด temperature sensor: `read_temperature()` -> `read()`
  - เพิ่มการตรวจสอบขอบเขต pH (-2.0 ถึง 16.0, NaN check)
  - เพิ่ม division threshold จาก 0.0001 เป็น 0.01 mL
  - เพิ่ม `f.flush()` หลังเขียน CSV เพื่อป้องกันข้อมูลสูญหาย
  - เพิ่มคำเตือนเมื่อ temperature sensor ล้มเหลว (ใช้ค่าเริ่มต้น 25 C)
  - แก้ไข pH slope เป็นค่าลบอัตโนมัติพร้อมคำเตือน
  - แสดง error บนจอ TFT เมื่อสร้างไฟล์ CSV ไม่สำเร็จ

- **Configuration:**
  - `stabilize_time=10.0` วินาที (เปลี่ยนเป็น 2.0 สำหรับทดสอบ)
  - `alert_volume=4.80` mL สามารถปรับได้ใน main.py

**การเปลี่ยนแปลงใน v3.5.0:**
- **Robust pH Reading**: เพิ่มการกรองสัญญาณ ADC แบบ IQR-based Outlier Rejection (Tukey's Fences)
  - แก้ปัญหาค่า pH ผิดปกติรุนแรง (เช่น 26.9, 20.1, 0.8 แทนที่จะเป็น ~11.7)
  - เก็บตัวอย่าง 25 ค่า คำนวณ Q1, Q3, IQR แล้วตัดค่านอกขอบเขต [Q1-1.5*IQR, Q3+1.5*IQR]
  - ใช้อัตโนมัติใน `ph_sensor.read()` และ `ph_sensor.read_voltage()`
  - เพิ่มเมธอด `read_voltage_simple()` สำหรับวิธีเดิม (trimmed mean) ถ้าต้องการเร็วกว่า
- **New config.py constants**: `ADC_ROBUST_SAMPLES=25`, `ADC_SAMPLE_DELAY_MS=20`, `ADC_IQR_FACTOR=1.5`
- **Time impact**: การอ่าน pH เพิ่มจาก ~100ms เป็น ~500ms ต่อครั้ง (เวลาไทเทรชันรวมเพิ่ม ~4%)

**การเปลี่ยนแปลงใน v3.4.0:**
- **Mode 4 (Test Flow Rate)**: แสดงเวลาที่คำนวณจาก flow rate, รอกด BTN1 ก่อนเริ่ม
- **Mode 5 (Purge)**: เปลี่ยนเป็น manual start/stop (กด BTN1 เริ่ม, กด BTN1 อีกครั้งหยุด)
- **Mode 6 (Titration)**: ปรับปรุงหลายจุด:
  - รอกด BTN1 ก่อนเริ่มไทเทรชัน (แสดงหน้าจอ Ready พร้อมพารามิเตอร์)
  - เพิ่มเสียงเตือนใกล้จุดสมมูล (3 beeps @ 2000 Hz ที่ 4.80 mL)
  - แสดงความคืบหน้าบนจอ TFT (step, volume, pH, temp, progress bar)
  - เก็บข้อมูลครบทุก 50 จุด (ไม่หยุดอัตโนมัติเมื่อพบจุดสมมูล)
  - BTN3 ยกเลิกได้ตลอดเวลา
  - ปรับค่า stabilize_time ได้ใน main.py (10s สำหรับทดลองจริง, 2s สำหรับทดสอบ)
- **Button Controls**: BTN1 ทำงานตามบริบท (Start/Confirm/Stop), BTN3 เป็น Cancel ในทุกโหมด

**การเปลี่ยนแปลงใน v3.3.0:**
- เปลี่ยนอัลกอริทึมไทเทรตเป็น **constant dose volume** (ปริมาตรคงที่ 0.2 mL ต่อ step)
  - ยกเลิกระบบ multi-phase (Fast Dosing / Slow Dosing) ที่ใช้ duty cycle ต่างกัน
  - ปั๊มทำงานที่ 100% duty เสมอ เติมทีละ 0.2 mL แล้วหยุดรอ pH เสถียร
  - เหตุผล: เข้าใจง่ายกว่า เหมือนการหยดสารทีละหยดในการไทเทรตมือ
  - นิสิตตรวจสอบได้: total_volume = dose_count x 0.2 mL

**การเปลี่ยนแปลงใน v3.2.0:**
- สมการสอบเทียบ pH เปลี่ยนเป็นรูปแบบ direct-use: `pH = slope_m * mV + intercept_b`
  - slope_m มีหน่วย pH/mV (ประมาณ -0.0169 ที่ 25 C)
  - intercept_b มีหน่วย pH (ประมาณ 34-36)
- รูปแบบไฟล์ `data_calibrate.txt` เปลี่ยนเป็น CSV: `slope_m,intercept_b,r_squared,cal_temp`
- ค่า flow rate ใช้ทศนิยม 4 ตำแหน่ง (ลดความคลาดเคลื่อน ~1.2%)
- ปริมาตรป้อนผ่าน `input()` ใน Thonny terminal (ไม่ hardcode)

**การเปลี่ยนแปลงใน v3.1.0:**
- ลบการใช้งาน SD Card - ใช้ ESP32 flash storage แทน
- เพิ่มขั้นตอนการดาวน์โหลดไฟล์ CSV ผ่าน Thonny IDE
- เพิ่มการบูรณาการกับ EquivPoint tool สำหรับวิเคราะห์จุดสมมูล

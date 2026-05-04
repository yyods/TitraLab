# TitraLab Week 3 - User Manual / คู่มือการใช้งาน

**ระบบไทเทรชันอัตโนมัติ | Automatic Titration System**

วิชา: Integrated Chemistry Laboratory I (2302311)

---

## 🔌 Wiring / การต่อสายจัมเปอร์

### Default Wiring (config.py)

```
GPIO Header          DEVICES Header
+-----------+        +-------------+
|   IO2   ●------>---● RED         |  LED แดง
|   IO4   ●------>---● GREEN       |  LED เขียว
|  IO26   ●------>---● BUZZER      |  Buzzer
|  IO34*  ●------>---● BUTTON_1    |  ปุ่ม 1 (SELECT)
|  IO35*  ●------>---● BUTTON_2    |  ปุ่ม 2 (UP)
|  IO39*  ●------>---● BUTTON_3    |  ปุ่ม 3 (DOWN)
|  IO25   ●------>---● PH_PROBE    |  หัววัด pH
|  IO16   ●------>---● DS18B20     |  เซ็นเซอร์อุณหภูมิ
|  IO21   ●------>---● CONTROL_1   |  ปั๊ม (Pump)
+-----------+        +-------------+
  (* = Input Only)
```

### GPIO Selection Guide / ตารางเลือก GPIO

| อุปกรณ์ | ต้องการ | GPIO ที่ใช้ได้ | ห้ามใช้ |
|---------|--------|---------------|--------|
| LED | Output | 2, 4, 12, 16, 17, 21, 22, 26 | 34, 35, 39 |
| Button | Input | 34, 35, 39 (แนะนำ) | - |
| pH Probe | ADC | 25, 32, 33 | 34-39 ถ้าต้องการ ADC1 |
| Pump | PWM | 2, 4, 12, 21, 22, 26 | 34, 35, 39 |
| DS18B20 | Digital | 2, 4, 12, 16, 17 | 34, 35, 39 |

### Fixed Pins (PCB Hardwired) - ห้ามเปลี่ยน

```
TFT Display: SCK=14, MOSI=13, DC=27, CS=15, RST=0
SD Card: MISO=19, MOSI=23, SCK=18, CS=5 (ไม่ใช้งาน)
```

---

## 🎮 Button Controls / การควบคุมปุ่ม

| ปุ่ม | หน้าที่หลัก | ในเมนู |
|------|------------|--------|
| **BTN1** | SELECT / เลือก | เริ่มทำงาน, ยืนยัน |
| **BTN2** | UP / ขึ้น | เลื่อนเมนูขึ้น |
| **BTN3** | DOWN / ลง | เลื่อนเมนูลง, **กดค้าง 3 วินาที = ออก** |

---

## 📋 6 Modes / 6 โหมดการทำงาน

| Mode | ชื่อ | คำอธิบาย | เมื่อใช้ |
|------|-----|---------|---------|
| 1 | Calibrate pH | สอบเทียบ pH 3 จุด (4, 7, 10) | ก่อนทดลอง |
| 2 | pH Test | ทดสอบค่า pH แบบ real-time | ตรวจสอบหลังสอบเทียบ |
| 3 | Calibrate Flow | สอบเทียบอัตราการไหลปั๊ม | ก่อนทดลอง |
| 4 | Flow Test | ทดสอบจ่าย 5 mL | ตรวจสอบหลังสอบเทียบ |
| 5 | Purge | ล้างท่อปั๊ม | ก่อน/หลังทดลอง |
| 6 | **Auto Titration** | ไทเทรชันอัตโนมัติ | **ทำการทดลอง** |

---

## 🧪 Lab Day Workflow / ขั้นตอนวันทดลอง

### ขั้นตอนที่ 1: เตรียมระบบ (Setup) - 15 นาที

```
1. เสียบ USB → เปิด Thonny → Run main.py
2. Mode 5: Purge → ล้างท่อด้วยสาร titrant
3. Mode 1: Calibrate pH → ใช้ buffer 4, 7, 10 (ต้องได้ R² ≥ 0.99)
4. Mode 2: pH Test → ตรวจสอบค่าถูกต้อง
5. Mode 3: Calibrate Flow → วัด 3-5 ครั้ง (ต้องได้ RSD ≤ 5%)
```

### ขั้นตอนที่ 2: ไทเทรชัน (Titration) - 10-15 นาที/ซ้ำ

```
1. เตรียมสารละลาย analyte ในบีกเกอร์
2. จุ่มหัววัด pH และท่อ titrant
3. Mode 6: Auto Titration → กด BTN1 เริ่ม
4. รอจนเสร็จ (Buzzer ดัง 3 ครั้งเมื่อใกล้จุดสมมูล)
5. ข้อมูลบันทึกใน titration_data_R1.csv อัตโนมัติ
```

### ขั้นตอนที่ 3: ดาวน์โหลดข้อมูล (Download)

```
Thonny → Files panel → คลิกขวาที่ไฟล์ → Download to...
  - titration_data_R1.csv (ข้อมูลไทเทรชัน)
  - data_calibrate.txt (ข้อมูลสอบเทียบ pH)
  - data_flowrate.txt (ข้อมูลสอบเทียบ flow)
```

---

## 🔧 Mode Details / รายละเอียดแต่ละโหมด

### Mode 1: Calibrate pH

```
จุ่ม buffer → กด BTN1 ยืนยัน → ทำซ้ำ 3 บัฟเฟอร์
✓ ผ่าน: R² ≥ 0.99, slope ≈ -0.017 pH/mV
✗ ไม่ผ่าน: ล้างหัววัด → สอบเทียบใหม่
```

### Mode 3: Calibrate Flow (Multi-Measurement)

```
BTN1: เริ่ม/หยุดปั๊ม
BTN2: บันทึกปริมาตร (พิมพ์ใน terminal)
BTN3: บันทึกและออก

✓ RSD ≤ 3%: Excellent
✓ RSD 3-5%: Good
⚠ RSD > 5%: Warning → สอบเทียบใหม่
```

### Mode 6: Auto Titration

```
เสียง Buzzer:
  - 3 เสียง = ใกล้ถึง alert_volume
  - เสียงยาว = เสร็จสิ้น
```

---

## ⚙️ Configuration / การตั้งค่า (main.py)

แก้ไขไฟล์ `main.py` บรรทัด ~195-198:

```python
titration.configure(
    stabilize_time=10.0,  # วินาที - เวลารอ pH เสถียร
    alert_volume=4.80     # mL - เตือนเมื่อใกล้จุดสมมูล
)
```

### Parameters / พารามิเตอร์

| พารามิเตอร์ | ค่าเริ่มต้น | คำอธิบาย | ปรับเมื่อไหร่ |
|-------------|-----------|---------|--------------|
| `stabilize_time` | 10.0 s | เวลารอให้ pH คงที่หลังเติม titrant | ใช้ 2.0 สำหรับทดสอบ |
| `alert_volume` | 4.80 mL | ปริมาตรที่ดัง 3 เสียงเตือน | ปรับตามจุดสมมูลที่คาดการณ์ |

### How to Calculate alert_volume / วิธีคำนวณ

```
สำหรับ HCl 0.1M 5mL + NaOH 0.1M:
  จุดสมมูล ≈ 5.0 mL
  alert_volume = 5.0 - 0.2 = 4.80 mL (เตือนก่อน 1 dose)

สูตรทั่วไป:
  alert_volume = (จุดสมมูลที่คาด) - (1-2 × dose_volume)
```

### Quick Test Mode / โหมดทดสอบเร็ว

เปลี่ยน `stabilize_time=2.0` เพื่อทดสอบระบบ (ไม่ต้องรอนาน):

```python
titration.configure(
    stabilize_time=2.0,   # ⚡ โหมดทดสอบ (ใช้ 10.0 สำหรับทดลองจริง)
    alert_volume=4.80
)
```

---

## 📊 Data Files / ไฟล์ข้อมูล

| ไฟล์ | เนื้อหา |
|------|--------|
| `data_calibrate.txt` | slope, intercept, R², temp |
| `data_flowrate.txt` | flow_rate (mL/s), statistics |
| `titration_data_R1.csv` | Volume, pH, Cycle, Time, Temp |

**CSV Format:**
```csv
Volume (mL),pH Value,Cycle,Time(s),Temperature(C)
0.000,2.85,0,0.00,25.00
0.200,2.92,1,11.37,25.00
...
```

---

## ⚠️ Quick Troubleshooting / แก้ปัญหาเบื้องต้น

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|-------|--------|
| pH อ่านค่าแปลกๆ | หัววัดสกปรก/ไม่ได้สอบเทียบ | ล้างหัววัด → Mode 1 |
| R² < 0.99 | บัฟเฟอร์หมดอายุ/หัววัดเสีย | เปลี่ยนบัฟเฟอร์/ตรวจหัววัด |
| ปั๊มไม่ทำงาน | สายหลุด/ท่ออุดตัน | ตรวจสาย → Mode 5 ล้างท่อ |
| Flow RSD > 5% | ท่อมีฟองอากาศ | Mode 5 ล้างท่อซ้ำ |
| MemoryError | หน่วยความจำเต็ม | กด Ctrl+D รีสตาร์ท ESP32 |
| จอไม่แสดง | SPI ผิดพลาด | ตรวจสายต่อ → รีสตาร์ท |

---

## 📌 Important Notes / หมายเหตุสำคัญ

1. **ล้างหัววัด pH** ด้วยน้ำกลั่นทุกครั้งที่เปลี่ยนสารละลาย
2. **ซับให้แห้ง** ก่อนจุ่มในสารละลายถัดไป
3. **Purge ท่อ** ก่อนเริ่มทดลองจริงเพื่อไล่ฟองอากาศ
4. **บันทึกหมายเลข Run** (R1, R2, R3) สำหรับทดลองซ้ำ
5. **กดค้าง BTN3** 3 วินาทีเพื่อออกจากโปรแกรม

---

## 🔬 Analysis with EquivPoint Tool

```bash
# วิเคราะห์หาจุดสมมูล
cd EquivPoint
python equiv_point.py titration_data_R1.csv --save
```

**Output:**
- First derivative: dpH/dV maximum
- Second derivative: d²pH/dV² = 0
- pH = 7 crossing (for strong acid-base)

---

*Version 2.5 | TitraLab - Chemistry Automation*
*User Manual for Week 3 Program*

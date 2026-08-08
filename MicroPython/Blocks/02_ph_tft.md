# Blocks ตัวอย่างที่ 4: วัดค่า pH แสดงบนจอ TFT
# Blocks Example 4: pH Meter on the TFT Display

ตัวอย่างนี้อยู่ในแอป SciLabPro MicroPad: หน้า **Blocks → Examples → "pH Meter"**
(แอป 1.3.1 (42) ขึ้นไป) — กดโหลดแล้วบล็อกทั้ง 5 ชิ้นปรากฏบนพื้นที่ทำงาน
โครงสร้างเหมือนตัวอย่างที่ 1 เป๊ะ — เปลี่ยนแค่เซ็นเซอร์กับจำนวนทศนิยม

Ships inside the app: **Blocks → Examples → "pH Meter"** (app 1.3.1 (42)+).
Identical structure to Example 1 — only the sensor and the precision change.

## ⚠️ ต้องสอบเทียบก่อน! (Calibrate first!)

บล็อก **อ่าน pH** ใช้ค่าสอบเทียบ "ของบอร์ดตัวนี้" ที่เก็บไว้ในบอร์ด
(บันทึกจากหน้า **Lab → pH** ของแอป) — ถ้ายังไม่เคยสอบเทียบ โปรแกรมจะหยุดพร้อมข้อความ:

```
RuntimeError: ph calibration missing for pin 32
```

**นี่ไม่ใช่ข้อผิดพลาด — นี่คือบทเรียน!** เครื่องมือวัดต้องสอบเทียบก่อนใช้เสมอ
และโปรแกรมนี้ปฏิเสธที่จะ "เดา" ค่า pH โดยไม่มีการสอบเทียบของจริง
ไปที่ **Lab → pH** สอบเทียบด้วยบัฟเฟอร์ pH 4 / 7 (และ 10) แล้วกลับมารันใหม่

The **Read pH** block consumes THIS board's stored calibration (written by
the app's **Lab → pH** wizard). Uncalibrated boards stop with the message
above — **that is the lesson, not a bug**: instruments are calibrated before
use, and this program refuses to fabricate a pH. Calibrate with pH 4/7
buffers in Lab → pH, then run again.

## เตรียมฮาร์ดแวร์ (Hardware setup)

| รายการ | ค่า |
| --- | --- |
| หัววัด pH | ต่อผ่านวงจรขยาย ที่ **GPIO32** (ADC1 ตามผังบอร์ด) |
| สอบเทียบ | **Lab → pH** ในแอป (บัฟเฟอร์ pH 4 / 7 / 10) — ต้องทำก่อน |
| จอ TFT | ติดตั้งบนบอร์ดอยู่แล้ว |
| แอป / เฟิร์มแวร์ | MicroPad 1.3.1 (42)+ / เฟิร์มแวร์ 0.4.17+ |

## บล็อกทั้ง 5 ชิ้น (The 5 blocks)

1. **แสดงข้อความบนจอ** "pH Meter" แถวที่ **1**
2. **ทำซ้ำตลอดไป** (Forever):
3. ตั้งตัวแปร `ph` = **อ่าน pH** ขา **32**
4. **พิมพ์ค่า** `ph`
5. **แสดงค่าบนจอ** `ph` แถวที่ **3** **ทศนิยม 2 ตำแหน่ง** แล้ว **หน่วง 1 วินาที**

สังเกต: ทศนิยม **2 ตำแหน่ง** ตามธรรมเนียมการรายงานค่า pH ในเคมี
(ตัวอย่างแรกที่ใช้ตัวเลือกทศนิยมกับเซ็นเซอร์จริง!)

## ผลที่เป็นไปได้ 2 แบบ (Two valid outcomes)

| บอร์ด | ผล |
| --- | --- |
| สอบเทียบแล้ว | จอแสดง `pH Meter` และค่า pH สด เช่น `7.02` อัปเดตทุกวินาที |
| ยังไม่สอบเทียบ | จอแสดง `pH Meter` แล้วโปรแกรมหยุดพร้อม `ph calibration missing for pin 32` → ไปสอบเทียบก่อน |

(ตรวจสอบบนบอร์ดจริง 2026-07-10: บอร์ดที่ยังไม่สอบเทียบผ่านหน้า Lab
หยุดพร้อมข้อความดังกล่าวอย่างถูกต้อง — โปรแกรมไม่สร้างค่าปลอมขึ้นเอง)

## โค้ดที่บล็อกสร้างให้ (The generated Python)

ดู [`02_ph_tft_reference.py`](02_ph_tft_reference.py) — เหมือนตัวอย่างที่ 1
ทุกบรรทัดยกเว้น: `slp.ph_probe(32).read()` แทน DS18B20 และ `_tft_show(3, ph, 2)`
(อาร์กิวเมนต์ตัวที่สาม = ทศนิยม 2 ตำแหน่ง)

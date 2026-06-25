# TitraLab Week 3: Acid-Base Titration Lesson (Lean / MicroPad)
# TitraLab สัปดาห์ที่ 3: บทเรียนไทเทรตกรด-เบส (รุ่นลีน / MicroPad)

---

> **รายวิชา (Course):** 2302311 Integrated Chemistry Laboratory I
> **ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย**
> **Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## วัตถุประสงค์ (Objectives)

เมื่อจบบทเรียนนี้ นิสิตจะสามารถ (By the end of this lesson, students will be able to):

1. **โฟกัสที่เคมี ไม่ใช่ไดรเวอร์** — เขียนโค้ดไทเทรตโดยเรียก high-level helper จากเฟิร์มแวร์ (`scilabpro.*`) แทนการเขียนไดรเวอร์ฮาร์ดแวร์เอง (focus on the **chemistry**, not driver internals)
2. **นำผลสอบเทียบของตัวเองมาใช้ (apply your own calibration)** — อ่านไฟล์สอบเทียบที่นิสิต "ทำเองใน Week_2" แล้วนำมาใช้จริงในการทดลอง (pH = slope·mV + intercept; เวลาปั๊ม = ปริมาตร/flow_rate)
3. **หาจุดสมมูล (equivalence point)** ด้วยวิธีอนุพันธ์ |dpH/dV| สูงสุด
4. **คำนวณความเข้มข้นที่ไม่ทราบค่า** ด้วยกฎ C1V1 = C2V2 พร้อมอัตราส่วนสโตอิชิโอเมตรี
5. **ใช้งานบทเรียนผ่านแอป MicroPad** — แท็บเล็ตเป็นจอแสดงผล, ดูค่า pH/temp/volume สด ๆ และอ่านผลลัพธ์

---

## โมเดลใหม่: ฮาร์ดแวร์อยู่ในเฟิร์มแวร์ (The New Model)

> **สิ่งที่เปลี่ยนไป (What changed):** เดิม Week 3 ขนไดรเวอร์ทั้งหมด (pH, ปั๊ม, จอ TFT, ปุ่ม, ฯลฯ)
> มาไว้ใน `/workspace` เอง ตอนนี้ **ไดรเวอร์ (raw ADC / OneWire / PWM) อยู่ในเฟิร์มแวร์ MicroPad แล้ว**
> ส่วน **การสอบเทียบ (calibration) ยังเป็นงานของนิสิต** — นิสิตสอบเทียบเองใน Week_2 แล้ว Week_3
> "อ่านไฟล์ผลสอบเทียบ" มาใช้จริง บทเรียนจึงเหลือแค่ไฟล์เคมีสั้น ๆ ที่ **เรียก helper** `scilabpro.*` (`slp`)

```
┌─────────────────────────────────────────────────────────────────┐
│  เฟิร์มแวร์ MicroPad (FIRMWARE) = ไดรเวอร์ดิบ (RAW DRIVER) เท่านั้น │
│                                                                   │
│   raw ADC · OneWire(อุณหภูมิ) · PWM/relay(ปั๊ม) · LED · buzzer    │
│   ไม่ "ตีความ" pH ให้ — แค่คืน "ค่า ADC ดิบ" (does NOT interpret) │
│                                                                   │
│   เปิดให้บทเรียนใช้ผ่าน helper:  import scilabpro as slp           │
└───────────────────────────────┬───────────────────────────────────┘
   slp.read_analog('PH') (raw ADC) / slp.ds18b20() / slp.set_actuator() / slp.data()
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  บทเรียน /workspace (LESSON — เคมี + การนำผลสอบเทียบมาใช้)        │
│                                                                   │
│   main.py        ← โหลดไฟล์สอบเทียบ → หยด → อ่าน → วิเคราะห์      │
│   titration.py   ← เคมี + APPLY fit:  pH = slope·mV + intercept   │
│   experiment.py  ← ค่าคงที่ + เส้นทางไฟล์สอบเทียบ (PH/FLOW_CAL)   │
└───────────────────────────────┬───────────────────────────────────┘
        ▲ อ่าน (reads)          │ BLE
        │                       ▼
┌───────┴─────────────────────────────────────────────────────────┐
│  /workspace/data/  ← ผลสอบเทียบ "ของนิสิต" จาก Week_2 (per board) │
│    ph_calibration.txt   (slope_m, intercept_b, ...)              │
│    flow_calibration.txt (flow_rate=<mL/s>)                       │
└─────────────────────────────────────────────────────────────────┘
```

**ทำไมต้องสอบเทียบเอง (Why student calibration is load-bearing)?** อุปกรณ์ TitraLab ราคาประหยัด
และ **แต่ละบอร์ดต่างกัน** หัววัด pH และปั๊มของบอร์ดคุณไม่เหมือนของเพื่อน นิสิตจึง **ต้อง** สอบเทียบเอง
และการได้ลงมือ/เห็นการสอบเทียบนั้นคือหัวใจของการเรียน บทเรียนนี้ **ใช้ค่าสอบเทียบของบอร์ดตัวเอง**
(ไม่ใช่ค่าคงที่ตายตัว และไม่ใช่ "กล่องดำ" ของเฟิร์มแวร์) — ไดรเวอร์คืน *ค่า ADC ดิบ* ส่วนการแปลงเป็น pH
และการจับเวลาปั๊มเป็น **Python ที่นิสิตมองเห็น** เปรียบได้กับการใช้ pH meter ในแล็บที่ "ต้องสอบเทียบ
ด้วยบัฟเฟอร์มาตรฐานก่อนวัดทุกครั้ง" (The driver returns RAW ADC; converting it to pH and timing the
pump are visible student Python that USES each board's own Week_2 calibration — never a hard-coded
constant and never a firmware black box.)

---

## ความรู้พื้นฐาน (Prerequisites)

| ด้าน | สิ่งที่ควรรู้ |
|------|--------------|
| เคมี (Chemistry) | ไทเทรชันกรด-เบส, จุดสมมูล (equivalence point), C1V1 = C2V2, สมการ Nernst เบื้องต้น |
| โปรแกรม (Programming) | ฟังก์ชัน (function), ลูป (loop), เงื่อนไข (conditional), การ import โมดูล, list/dict พื้นฐาน |
| ระบบ (System) | แอป MicroPad จับคู่บอร์ดผ่าน BLE และเป็นจอแสดงผล (ไม่มีเมนู TFT บนบอร์ด) |
| **สอบเทียบ (Calibration)** | **ต้องทำ Week_2 ก่อน** — สอบเทียบ pH 3 จุด + อัตราการไหลปั๊ม (ดูบล็อก ⚠ ด้านล่าง) |

> ### ⚠ ต้องสอบเทียบใน Week_2 ก่อนรันบทเรียนนี้ (Calibrate in Week_2 FIRST — required)
>
> Week_3 **ไม่มีโหมดสอบเทียบ** แต่ **ต้องใช้ผลสอบเทียบที่นิสิตทำเองใน Week_2** ก่อนรัน ให้รันสองสคริปต์นี้
> ซึ่งจะบันทึกค่าสอบเทียบ "ของบอร์ดตัวเอง" ลงไฟล์ถาวรใน `/workspace/data/`:
>
> | รันใน Week_2 (run first) | ได้ไฟล์ (produces) | Week_3 ใช้ทำอะไร |
> |--------------------------|--------------------|------------------|
> | `Week_2/01_pH_Sensor/02_calibration_3point.py` | `/workspace/data/ph_calibration.txt` | แปลง mV → pH (slope·mV + intercept) |
> | `Week_2/02_Pump_Control/01_flow_rate_calibration.py` | `/workspace/data/flow_calibration.txt` | คำนวณเวลาเปิดปั๊มต่อ step (ปริมาตร/flow_rate) |
>
> **ถ้าไฟล์ใดหาย Week_3 จะหยุดทันที** (abort) พร้อม event `ph_calibration_missing` /
> `flow_calibration_missing` และจะ **ไม่เดินปั๊มเลย** — ให้กลับไปรันการสอบเทียบ Week_2 ที่หายก่อน
> (If a calibration file is missing, Week_3 aborts before any dosing and tells you to run the Week_2
> calibration first.)

---

## แนวคิดหลัก (Key Concepts)

### helper ของเฟิร์มแวร์ที่บทเรียนเรียก (scilabpro helpers used)

| Helper | หน้าที่ | เชื่อมโยงเคมี/โปรแกรม |
|--------|---------|----------------------|
| `slp.claim_controller()` | ขอสิทธิ์ควบคุมบอร์ด (เผื่อรันผ่าน USB ขณะแท็บเล็ตเชื่อมอยู่) | ต้อง "ถือ lease" ก่อนสั่งงาน actuator |
| `slp.read_analog('PH')` | อ่าน **ค่า ADC ดิบ** (0–4095) ของหัววัด pH | ADC (ตัวแปลงสัญญาณแอนะล็อกเป็นดิจิทัล) — ยังไม่ใช่ pH |
| `slp.ds18b20(16).read_c()` | อ่านอุณหภูมิ (°C) | ใช้บันทึกควบคู่ pH (pH ขึ้นกับอุณหภูมิ) |
| `slp.set_actuator('CONTROL_1', on, max_on_ms=...)` | สั่งปั๊มเปิด/ปิด พร้อมเพดานเวลาปลอดภัย | PWM/relay; `max_on_ms` = guard ฮาร์ดแวร์ |
| `slp.pin(4)` | ขา output (LED สถานะ) | Digital output (variable แสดงสถานะ) |
| `slp.pin(34, input=True)` | ขา input-only (BUTTON_1) | Digital input; ปุ่มเริ่ม local |
| `slp.buzzer(26).tone(hz)` / `.off()` | เสียงแจ้งเตือน | Conditional → แจ้งเตือนเมื่อใกล้จุดสมมูล |
| `slp.data(name, value, unit=...)` | สตรีมค่าไปยังแอป (สด) | ติดตามการวัดต่อเนื่อง (live monitoring) |
| `slp.event(name, dict)` | ส่ง event/ผลลัพธ์ไปยังแอป | รายงานผลสุดท้าย (titration_complete) |
| `slp.stop_requested()` | ถามว่าผู้ใช้สั่งหยุดจากแอปหรือยัง | ลูปต้อง poll ทุกครั้ง (cooperative stop) |

> **ไม่ใช้ `slp.ph_probe()` (we do NOT use `slp.ph_probe()`):** `slp.ph_probe()` จะใช้ `calibration.json`
> ของแอป/เฟิร์มแวร์ ซึ่ง **ไม่ใช่** การสอบเทียบของนิสิต บทเรียนนี้จึงอ่าน **ADC ดิบ** ด้วย
> `slp.read_analog('PH')` แล้วนำ **สมการสอบเทียบของนิสิตเอง (จาก Week_2)** มาแปลงเป็น pH ใน Python ที่เห็นได้

### ฟังก์ชันในบทเรียนที่ "นำผลสอบเทียบมาใช้" (lesson helpers that APPLY the calibration)

อยู่ใน `titration.py` — โหลดไฟล์สอบเทียบของนิสิตจาก Week_2 แล้วนำมาใช้จริง (in `titration.py`):

| ฟังก์ชัน | อ่านไฟล์ | คืนค่า / ทำอะไร |
|----------|----------|-----------------|
| `load_ph_calibration()` | `ph_calibration.txt` | คืน `(slope_m, intercept_b)`; ถ้าไฟล์หาย → `RuntimeError` |
| `load_flow_rate()` | `flow_calibration.txt` | คืน `flow_rate` (mL/s); ถ้าไฟล์หาย → `RuntimeError` |
| `read_ph_median(slope_m, intercept_b, n, gap)` | — | อ่าน ADC ดิบ → `mV = raw × RAW_TO_MV` → **`pH = slope_m·mV + intercept_b`** → มัธยฐาน |
| `pump_time_ms_for_volume(vol, flow, max_ms)` | — | `round(vol / flow × 1000)` แล้ว clamp ที่ `max_ms` (เวลาเปิดปั๊มต่อ step) |

### หลักการทางเคมี (Chemistry recap)

- **จุดสมมูล (equivalence point):** จุดที่กรดและเบสทำปฏิกิริยาพอดี ที่จุดนี้ **|dpH/dV| สูงสุด**
- **คำนวณความเข้มข้นที่ไม่ทราบค่า:** `C_analyte = ratio × C_titrant × V_eq / V_sample`
  (สำหรับ HCl + NaOH อัตราส่วน 1:1 → `ratio = 1.0`)
- **นำสมการสอบเทียบมาใช้ (apply the fit):** `pH = slope_m × mV + intercept_b` โดย `slope_m`, `intercept_b`
  มาจากการถดถอยเชิงเส้น 3 จุดที่นิสิตทำใน Week_2 ส่วน `mV = raw_ADC × 3300/4095` (ตัวประกอบเดียวกับ Week_2)
- **อ่าน pH แบบมัธยฐาน (median):** อ่านหลายครั้งแล้วใช้ค่ามัธยฐานเพื่อทนต่อค่าผิดปกติ (outlier) จาก ADC
- **จับเวลาปั๊มจาก flow rate (closed-loop on volume):** `เวลาเปิดปั๊ม = DOSE_VOLUME_ML / flow_rate` ทำให้
  ปริมาตรที่รายงานเท่ากับปริมาตรที่ "ส่งจริง" (ไม่ใช่ค่าฮาร์ดโค้ด)

---

## ไฟล์ในบทเรียน (Files) — มีแค่ 3 ไฟล์ Python

```
Week_3/
├── main.py          # [ENTRY] โหลดสอบเทียบ → ไทเทรต — runner เรียก /workspace/main.py
├── titration.py     # [CHEMISTRY] โหลด/นำผลสอบเทียบมาใช้ + หาจุดสมมูล + คำนวณความเข้มข้น
├── experiment.py    # [CONFIG] ค่าคงที่การทดลอง + เส้นทางไฟล์สอบเทียบ + ชื่อ endpoint
│
├── README.md        # เอกสารนี้ (ภาพรวมเทคนิค)
├── USER_MANUAL.md   # คู่มือใช้งานวันทดลอง (Quick Reference + แอป MicroPad)
└── LAB_DIRECTION.md # คู่มือปฏิบัติการ (ทฤษฎี + ขั้นตอน + อินดิเคเตอร์ + คำถาม)

(อ่านจากภายนอก / read from outside this folder)
/workspace/data/ph_calibration.txt    ← นิสิตสร้างใน Week_2 (slope_m, intercept_b)
/workspace/data/flow_calibration.txt  ← นิสิตสร้างใน Week_2 (flow_rate=<mL/s>)
```

| ไฟล์ | บทบาท | นิสิตแก้ไขไหม |
|------|-------|:------------:|
| `main.py` | โหลดสอบเทียบ → เริ่ม → หยดทีละ step → อ่าน pH/temp → สตรีม → วิเคราะห์ → ส่งผล | บางส่วน (ลำดับ/เงื่อนไข) |
| `titration.py` | โหลด+นำผลสอบเทียบมาใช้ (apply fit) + เคมีล้วน ทดสอบบนคอมพิวเตอร์ได้ | **ใช่ (โฟกัสที่นี่)** |
| `experiment.py` | ค่าคงที่: dose, ปริมาตร, ความเข้มข้น, อัตราส่วน, เวลาหน่วง, **เส้นทางไฟล์สอบเทียบ + RAW_TO_MV** | **ใช่ (ปรับการทดลอง)** |

> **เลขขา GPIO ส่วนใหญ่เป็นหน้าที่ของ routing profile ในเฟิร์มแวร์** บทเรียนอ้างอุปกรณ์ด้วย
> **ชื่อ endpoint** (เช่น `'CONTROL_1'` สำหรับปั๊ม, `'PH'` สำหรับหัววัด pH) ส่วนเลขขาที่ปรากฏใน
> `experiment.py` (`PH_PROBE_PIN = 32` เป็น fallback, `TEMP_PROBE_PIN = 16`) มีไว้เพราะ helper
> `slp.ds18b20(num)` / `slp.pin(num)` รับ "หมายเลขขา" โดยตรง — ไม่ใช่การ hard-code wiring ของทั้งระบบ

---

## โค้ดตัวอย่าง (Example Code) — รูปแบบการใช้ helper

`main.py` สั้นและตรงไปตรงมา หัวใจคือ "**โหลดผลสอบเทียบของนิสิต → หยด → รอเสถียร → อ่าน(แปลงด้วย fit)
→ สตรีม → ทำซ้ำ**" โดยตรวจ `slp.stop_requested()` ทุกลูป และปั๊มถูก guard ด้วย `max_on_ms` เสมอ:

```python
import time
import scilabpro as slp        # firmware RAW drivers only (raw ADC / OneWire / PWM)

import experiment as exp
from titration import (TitrationAnalysis, read_ph_median,
                       load_ph_calibration, load_flow_rate, pump_time_ms_for_volume)

slp.claim_controller()                     # ขอสิทธิ์ควบคุมบอร์ด

# 1) โหลดผลสอบเทียบที่นิสิต "ทำเองใน Week_2" — ถ้าหาย ให้หยุดก่อนแตะปั๊มใด ๆ
#    Load the student's own Week_2 calibration; abort BEFORE any dosing if missing.
try:
    ph_slope_m, ph_intercept_b = load_ph_calibration()   # อ่าน ph_calibration.txt
except RuntimeError as e:
    slp.event('ph_calibration_missing', {'path': exp.PH_CAL_PATH, 'error': str(e),
               'hint': 'Run Week_2 01_pH_Sensor/02_calibration_3point.py first'})
    raise SystemExit  # หยุด: ให้นิสิตไปสอบเทียบ pH ใน Week_2 ก่อน

try:
    flow_rate_ml_s = load_flow_rate()                    # อ่าน flow_calibration.txt (mL/s)
except RuntimeError as e:
    slp.event('flow_calibration_missing', {'path': exp.FLOW_CAL_PATH, 'error': str(e),
               'hint': 'Run Week_2 02_Pump_Control/01_flow_rate_calibration.py first'})
    raise SystemExit  # หยุด: ให้นิสิตไปสอบเทียบอัตราการไหลใน Week_2 ก่อน

# เวลาเปิดปั๊มต่อ step = ปริมาตร/flow_rate (closed-loop) แล้ว clamp เพดานปลอดภัย
pump_time_ms = pump_time_ms_for_volume(exp.DOSE_VOLUME_ML, flow_rate_ml_s, exp.DOSE_MAX_ON_MS)

led = slp.pin(4)                           # LED สถานะ (output)
analysis = TitrationAnalysis()             # เคมีล้วน (จาก titration.py)

volume = 0.0
while volume < exp.MAX_VOLUME_ML:
    if slp.stop_requested():               # ผู้ใช้กดหยุดในแอป → ออกอย่างปลอดภัย
        break

    # หยดไทแทรนต์ 1 step — เวลาปั๊มมาจาก flow rate ที่สอบเทียบ; guard ด้วย max_on_ms
    slp.set_actuator(exp.PUMP_ENDPOINT, True, max_on_ms=exp.DOSE_MAX_ON_MS)
    time.sleep_ms(pump_time_ms)            # = DOSE_VOLUME_ML / flow_rate (ไม่ใช่ค่าฮาร์ดโค้ด)
    slp.set_actuator(exp.PUMP_ENDPOINT, False)   # ปิดปั๊มอย่างชัดเจนเสมอ
    volume += exp.DOSE_VOLUME_ML

    # อ่าน ADC ดิบ → mV → pH = slope_m·mV + intercept_b (สมการสอบเทียบของนิสิตเอง) → มัธยฐาน
    ph = read_ph_median(ph_slope_m, ph_intercept_b, exp.PH_SAMPLES_PER_POINT)
    analysis.add_point(volume, ph)
    slp.data('volume_ml', volume, unit='mL')   # สตรีมไปยังแอป (live)
    slp.data('pH', ph, unit='pH')

eq = analysis.detect_equivalence_point()       # (V_eq, pH) จาก |dpH/dV| สูงสุด
conc = analysis.calculate_unknown_concentration(
    titrant_conc_m=exp.TITRANT_CONCENTRATION_M,
    sample_volume_ml=exp.SAMPLE_VOLUME_ML,
    ratio=exp.STOICHIOMETRIC_RATIO,            # C_analyte = ratio·C·V_eq/V_sample
)
slp.event('titration_complete', {             # ส่งผลลัพธ์ไปยังแอป
    'equivalence_volume_ml': eq[0] if eq else None,
    'unknown_concentration_m': conc,
})
```

> หมายเหตุ: `main.py` ตัวจริงมีรายละเอียดเพิ่ม (event `calibration_loaded` แจ้งค่าที่ใช้, เริ่ม local
> ด้วย BUTTON_1, ไฟ LED, อุณหภูมิ, เสียงเตือนใกล้จุดสมมูล, `try/finally` ปิดปั๊มทุกเส้นทาง) แต่โครงสร้าง
> หลัก — **โหลดสอบเทียบ → หยุดถ้าหาย → นำ fit มาใช้ → จับเวลาปั๊มจาก flow rate** — เป็นไปตามด้านบน

### ความปลอดภัยของปั๊ม (Pump safety — สำคัญ)

ทุกครั้งที่เปิดปั๊มจะส่ง `max_on_ms` เป็น **เพดานเวลา** ฮาร์ดแวร์ไทเมอร์ของเฟิร์มแวร์จะ **ตัดปั๊มเอง**
แม้สคริปต์จะค้าง และโค้ดยัง "ปิดปั๊มอย่างชัดเจน" (explicit OFF) ใน `finally` ทุกเส้นทางออก —
สอดคล้องกับหลักความปลอดภัยในแล็บ: ไม่ปล่อยให้สารไทแทรนต์ไหลค้างโดยไม่ตั้งใจ

---

## ใช้งานกับแอป MicroPad (Using the MicroPad App)

### 1) นำไฟล์เข้าสู่บอร์ด (Import the lesson into `/workspace`)

ใช้ตัวเรียกดู GitHub ในแอป (GitHub repo browser) เพื่อดึง **3 ไฟล์แบน** เข้าโฟลเดอร์ `/workspace`:

```
GitHub repo browser ในแอป MicroPad
   └─ TitraLab/MicroPython/Week_3/
        ├─ main.py        ──┐
        ├─ titration.py    ─┼─►  import เข้า  /workspace/  บนบอร์ด
        └─ experiment.py  ──┘
```

> ไฟล์เป็น **`.py` แบบแบน** (ไม่มีโฟลเดอร์ย่อย ไม่มี `.mpy`) วางทั้งสามไฟล์ไว้ระดับเดียวกันใน `/workspace`

### 2) จับคู่และรัน (Pair over BLE and run)

```
1. เปิดแอป MicroPad บนแท็บเล็ต → สแกนและจับคู่บอร์ดผ่าน BLE
2. เปิด /workspace/main.py → กด Run
3. (ถ้า WAIT_FOR_LOCAL_START=True) กด BUTTON_1 บนบอร์ดเพื่อเริ่ม หรือรอ timeout
```

### 3) ดูค่าสด ๆ และผลลัพธ์ (Watch live data + read the result)

แท็บเล็ตเป็นจอแสดงผล ทุกค่าที่บทเรียนเรียก `slp.data(...)` จะ **สตรีมขึ้นแอปแบบสด**:

| ค่าที่สตรีม (`slp.data`) | หน่วย | ความหมาย |
|--------------------------|:----:|----------|
| `volume_ml` | mL | ปริมาตรไทแทรนต์สะสม |
| `pH` | pH | ค่า pH ที่จุดนั้น (median) |
| `temp_c` | °C | อุณหภูมิ |

และ event ที่บทเรียนส่ง (`slp.event(...)`) จะปรากฏในแอป:

| Event | เมื่อใด | ข้อมูลเด่น |
|-------|--------|-----------|
| **`ph_calibration_missing`** | **ไม่พบ `ph_calibration.txt` (ไป Week_2 ก่อน)** | **path, error, hint** |
| **`flow_calibration_missing`** | **ไม่พบ `flow_calibration.txt` (ไป Week_2 ก่อน)** | **path, error, hint** |
| `calibration_loaded` | โหลดสอบเทียบของบอร์ดสำเร็จ (เห็นค่าที่ใช้) | ph_slope_m, ph_intercept_b, flow_rate_ml_s, pump_time_ms |
| `titration_started` | เริ่มการทดลอง | sample_volume_ml, titrant_conc_m, total_steps |
| `waiting_for_start` | รอกด BUTTON_1 | button: 'BUTTON_1' |
| `approaching_equivalence` | ถึง `ALERT_VOLUME_ML` (มีเสียง buzzer) | volume_ml |
| `temp_sensor_warning` | อ่านอุณหภูมิไม่ได้ (ใช้ค่า 25 °C) | error, default_c |
| `titration_aborted` | ผู้ใช้กดหยุด | reason, points_collected |
| **`titration_complete`** | **เสร็จสิ้น** | **equivalence_volume_ml, equivalence_ph_estimate, unknown_concentration_m** |

> ผลลัพธ์ที่ตรวจสอบบนคอมพิวเตอร์แล้ว (verified on host) สำหรับเคส HCl 0.1 M 5 mL + NaOH 0.1 M:
> **V_eq ≈ 5.0 mL, pH ≈ 7.0, C(HCl) ≈ 0.1 mol/L**

---

## ปรับแต่งการทดลอง (Tuning the experiment) — `experiment.py`

ค่าคงที่ทั้งหมดอยู่ที่เดียวใน `experiment.py` ปรับได้โดยไม่ต้องแตะโค้ดควบคุม:

| ค่าคงที่ | ค่าเริ่มต้น | ความหมาย |
|----------|:-----------:|----------|
| `DOSE_VOLUME_ML` | 0.2 mL | ปริมาตรไทแทรนต์ต่อ step (ทุกจุดบนกราฟห่างเท่ากัน) |
| `SAMPLE_VOLUME_ML` | 5.0 mL | ปริมาตรสารตัวอย่าง (analyte) |
| `MAX_VOLUME_ML` | 10.0 mL | ปริมาตรไทเทรตสูงสุด (2× ตัวอย่าง → กราฟรูป S สมบูรณ์) |
| `TITRANT_CONCENTRATION_M` | 0.1 mol/L | ความเข้มข้นไทแทรนต์ที่ทราบ |
| `STOICHIOMETRIC_RATIO` | 1.0 | อัตราส่วนโมล analyte:titrant (เปลี่ยนเป็น 0.5 สำหรับ H2SO4 ฯลฯ) |
| `SETTLE_MS` | 10000 ms | รอให้ pH คงที่หลังหยดแต่ละครั้ง |
| `DOSE_MAX_ON_MS` | 1500 ms | เพดานเวลาเปิดปั๊มต่อ step (guard ฮาร์ดแวร์ + clamp เวลาที่คำนวณ) |
| `PH_SAMPLES_PER_POINT` | 5 | จำนวนอ่าน pH ต่อจุด (ใช้ค่ามัธยฐาน) |
| `ALERT_VOLUME_ML` | 4.80 mL | ปริมาตรที่ buzzer เตือนใกล้จุดสมมูล |
| `PUMP_ENDPOINT` / `PH_ENDPOINT` | `'CONTROL_1'` / `'PH'` | ชื่อ endpoint ของปั๊ม / หัววัด pH (เฟิร์มแวร์แปลงเป็นเลขขาให้) |
| `PH_CAL_PATH` | `/workspace/data/ph_calibration.txt` | ไฟล์สอบเทียบ pH **ที่นิสิตสร้างใน Week_2** |
| `FLOW_CAL_PATH` | `/workspace/data/flow_calibration.txt` | ไฟล์อัตราการไหล **ที่นิสิตสร้างใน Week_2** |
| `RAW_TO_MV` | 3300/4095 | ตัวประกอบ ADC ดิบ → mV (**ต้องตรงกับ Week_2** จึงจะแปลง pH ถูก) |

> **ไม่มี `DOSE_ON_MS` แบบฮาร์ดโค้ดแล้ว (no hard-coded `DOSE_ON_MS`):** เวลาเปิดปั๊มต่อ step คำนวณสด
> จาก `DOSE_VOLUME_ML / flow_rate` (จากไฟล์ `flow_calibration.txt`) ดังนั้นปริมาตรที่รายงานคือปริมาตรที่ส่งจริง
>
> **`RAW_TO_MV` ต้องตรงกับ Week_2:** Week_2 fit สมการด้วย `mV = adc × 3300/4095` ถ้า Week_3 ใช้ค่าต่าง
> การนำ `slope_m`/`intercept_b` มาใช้จะได้ pH ผิด — ทั้งสองสัปดาห์จึงใช้ค่าเดียวกันเป๊ะ
>
> **ทดสอบเร็ว (quick test):** ลด `SETTLE_MS` เป็น `2000` เพื่อรันให้จบเร็วขณะตรวจโปรแกรม
> แล้วค่อยตั้งกลับเป็น `10000` สำหรับการทดลองจริง (pH probe ต้องการ 10–20 วินาทีจึงเสถียร)

---

## แก้ไขปัญหาเบื้องต้น (Troubleshooting)

| ปัญหา | สาเหตุที่พบบ่อย | วิธีแก้ |
|-------|----------------|--------|
| event `ph_calibration_missing` (หยุดทันที) | ยังไม่ได้สอบเทียบ pH ใน Week_2 / ไฟล์หาย | รัน `Week_2/01_pH_Sensor/02_calibration_3point.py` ให้ได้ `ph_calibration.txt` ก่อน แล้วรันใหม่ |
| event `flow_calibration_missing` (หยุดทันที) | ยังไม่ได้สอบเทียบอัตราการไหลใน Week_2 / ไฟล์หาย | รัน `Week_2/02_Pump_Control/01_flow_rate_calibration.py` ให้ได้ `flow_calibration.txt` ก่อน แล้วรันใหม่ |
| pH อ่านได้แต่ผิดเพี้ยน | ไฟล์ `ph_calibration.txt` มาจากบอร์ดอื่น / R² ต่ำใน Week_2 | สอบเทียบ pH ใหม่ "บนบอร์ดตัวนี้" ให้ R² ≥ 0.99 |
| ปริมาตร/ความเข้มข้นเพี้ยน | flow rate สอบเทียบไม่แม่น (RSD สูงใน Week_2) | สอบเทียบอัตราการไหลใหม่ให้ RSD ต่ำ แล้วรันใหม่ |
| ไม่เห็นค่าในแอป | บอร์ดยังไม่จับคู่ BLE / ไม่ได้ Run | จับคู่ใหม่, เปิด `/workspace/main.py` แล้วกด Run |
| ค้างที่ "waiting_for_start" | `WAIT_FOR_LOCAL_START=True` รอกดปุ่ม | กด BUTTON_1 บนบอร์ด หรือรอ timeout (30 วิ) |
| `temp_sensor_warning` | สาย DS18B20 หลุด/ไม่มี pull-up | ตรวจสายที่ขา 16; ระบบจะใช้ 25 °C ต่อได้ |
| ไม่พบจุดสมมูล (eq เป็น None) | ข้อมูลน้อยกว่า 3 จุด / ปริมาตรไม่ถึงจุดสมมูล | เพิ่ม `MAX_VOLUME_ML` หรือตรวจความเข้มข้นสาร |
| ปั๊มไม่ทำงาน | ต่อปั๊มผิด endpoint | ต่อปั๊มที่ `CONTROL_1` ให้ตรงกับ `PUMP_ENDPOINT` |

---

## เชื่อมโยงโปรแกรม ↔ เคมี (Programming ↔ Chemistry)

| แนวคิดโปรแกรม | ใช้ตรงไหนในบทเรียน | เชื่อมโยงเคมี |
|----------------|--------------------|---------------|
| Variable / ตัวแปร | `volume`, `ph`, `temp`, `ph_slope_m`, `flow_rate_ml_s` | ค่าปริมาตร/pH/อุณหภูมิ + ค่าสอบเทียบของบอร์ด |
| Loop / ลูป | ลูปไทเทรตหลัก | หยดและวัดซ้ำจนเลยจุดสมมูล |
| Conditional / เงื่อนไข | `if step >= alert_step` | ตรวจว่าใกล้จุดสมมูลหรือยัง |
| Function / ฟังก์ชัน | `load_ph_calibration`, `read_ph_median`, `dose_one_step` | ขั้นตอนที่ทำซ้ำได้ (เหมือนหัตถการในแล็บ) |
| File I/O / อ่านไฟล์ | `load_ph_calibration()`, `load_flow_rate()` | อ่านผลสอบเทียบของนิสิตจาก Week_2 |
| Array/List / อาร์เรย์ | `self.points` ใน `TitrationAnalysis` | เก็บจุดข้อมูลกราฟไทเทรชัน |
| ADC reading + calibration | `slp.read_analog('PH')` → `pH = slope·mV + b` | raw ADC → mV → **pH ด้วยสมการของนิสิต** (สมการ Nernst) |
| PWM / guard + calibration | `slp.set_actuator(..., max_on_ms=)`, เวลา = `vol/flow` | จ่ายสารไทแทรนต์ตามปริมาตรจริง (จาก flow rate ที่สอบเทียบ) อย่างปลอดภัย |

---

## คำศัพท์สำคัญ (Key Terminology)

| English | ไทย |
|---------|-----|
| Titration | การไทเทรต / ไทเทรชัน |
| Equivalence point | จุดสมมูล |
| Endpoint | จุดยุติ |
| Titrant | สารไทแทรนต์ |
| Analyte | สารตัวอย่าง |
| Calibration | การสอบเทียบ |
| pH probe | หัววัด pH |
| ADC (Analog-to-Digital Converter) | ตัวแปลงสัญญาณแอนะล็อกเป็นดิจิทัล |
| Derivative (dpH/dV) | อนุพันธ์ |

---

## ผู้พัฒนา (Developers)

- Hemmawan Saon
- Nuttakit Deemon
- Saowapak Vchirawongkwin
- Sumrit Wacharasindhu
- Viwat Vchirawongkwin

**รายวิชา:** 2302311 Integrated Chemistry Laboratory I
**ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย**

---

*Lean rewrite for MicroPad — firmware-provided drivers, tablet display, chemistry-first.*
*บทเรียนรุ่นลีนสำหรับ MicroPad — ไดรเวอร์มาจากเฟิร์มแวร์, แท็บเล็ตเป็นจอ, เน้นเคมีเป็นหลัก.*

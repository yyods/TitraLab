# TitraLab Week 3 - User Manual / คู่มือการใช้งาน

**บทเรียนไทเทรตกรด-เบส (รุ่นลีน / MicroPad) | Acid-Base Titration Lesson (Lean / MicroPad)**

วิชา: Integrated Chemistry Laboratory I (2302311)

> คู่มือนี้สำหรับ **วันทดลอง** ดูทฤษฎีและขั้นตอนเต็มได้ที่ `LAB_DIRECTION.md`
> และดูภาพรวมเทคนิคได้ที่ `README.md`

---

## ภาพรวม 30 วินาที (30-Second Overview)

```
ไดรเวอร์ดิบ (raw ADC/OneWire/PWM) อยู่ใน เฟิร์มแวร์ MicroPad
การสอบเทียบ (calibration) เป็นงานของนิสิต: ทำใน Week_2 แล้ว Week_3 อ่านมาใช้
บทเรียน /workspace มีแค่ 3 ไฟล์ และเรียก helper:  import scilabpro as slp
แท็บเล็ต (แอป MicroPad) จับคู่ผ่าน BLE และเป็น "จอแสดงผล"
```

> ### ⚠ ก่อนรัน Week_3 ต้องสอบเทียบใน Week_2 ก่อน (Calibrate in Week_2 FIRST)
> นิสิตสอบเทียบ "ของบอร์ดตัวเอง" ใน Week_2 ผลจะถูกบันทึกลงไฟล์ถาวรที่ Week_3 อ่านไปใช้:
> | รันใน Week_2 (run first) | ได้ไฟล์ (produces) |
> |--------------------------|--------------------|
> | `Week_2/01_pH_Sensor/02_calibration_3point.py` | `/workspace/data/ph_calibration.txt` |
> | `Week_2/02_Pump_Control/01_flow_rate_calibration.py` | `/workspace/data/flow_calibration.txt` |
>
> ถ้าไฟล์ใดหาย Week_3 จะ **หยุดทันทีและไม่เดินปั๊ม** พร้อมแจ้ง `ph_calibration_missing` /
> `flow_calibration_missing` ให้กลับไปสอบเทียบ Week_2 ที่หายก่อน

| ไฟล์ | บทบาท |
|------|-------|
| `01_titration_auto.py` | จุดเริ่ม — โหลดผลสอบเทียบ → ลำดับการไทเทรต (runner เรียก `/workspace/01_titration_auto.py`) |
| `titration.py` | เคมี + นำผลสอบเทียบมาใช้ (pH = slope·mV+b) — หาจุดสมมูล + คำนวณความเข้มข้น |
| `experiment.py` | ค่าคงที่การทดลอง + เส้นทางไฟล์สอบเทียบ (ปรับ dose, ความเข้มข้น, เวลาหน่วง) |

---

## ขั้นตอนวันทดลอง (Lab Day Workflow)

### ขั้นตอนที่ 0: สอบเทียบใน Week_2 ก่อน (Calibrate in Week_2 FIRST) — ต้องทำก่อนเสมอ

```
รัน Week_2 สองสคริปต์นี้บนบอร์ดตัวเอง (run on THIS board) เพื่อสร้างไฟล์สอบเทียบ:
   1) Week_2/01_pH_Sensor/02_calibration_3point.py
        → สอบเทียบ pH 3 จุด (pH 4/7/10) → /workspace/data/ph_calibration.txt
   2) Week_2/02_Pump_Control/01_flow_rate_calibration.py
        → สอบเทียบอัตราการไหลปั๊ม → /workspace/data/flow_calibration.txt
```

> ค่าสอบเทียบเป็น "ของบอร์ดตัวเอง" (per-board) ถ้ายังไม่มีไฟล์ Week_3 จะหยุดและบอกให้ทำขั้นตอนนี้ก่อน

### ขั้นตอนที่ 1: นำไฟล์เข้าบอร์ดผ่านแอป (Import) — ทำครั้งเดียว

```
แอป MicroPad → GitHub repo browser
   → TitraLab/MicroPython/Week_3/
   → import:  01_titration_auto.py , titration.py , experiment.py  (ไฟล์ .py แบน)
   → ปลายทาง:  /workspace/  บนบอร์ด
```

### ขั้นตอนที่ 2: จับคู่และรัน (Pair & Run)

```
1. เปิดแอป MicroPad บนแท็บเล็ต → สแกน BLE → จับคู่บอร์ด
2. เปิด /workspace/01_titration_auto.py → กด Run
3. (ถ้า WAIT_FOR_LOCAL_START=True) กด BUTTON_1 บนบอร์ดเพื่อเริ่ม หรือรอ timeout
```

### ขั้นตอนที่ 3: ดูค่าสด ๆ บนแท็บเล็ต (Watch live data)

```
เริ่มต้น: โหลดผลสอบเทียบของบอร์ด → แอปแจ้ง event calibration_loaded
   (slope/intercept ของ pH + flow_rate + เวลาเปิดปั๊มต่อ step ที่คำนวณได้)
ระบบทำซ้ำอัตโนมัติ:  หยด 0.2 mL → รอ pH เสถียร → อ่าน pH/temp → สตรีมขึ้นแอป
   • เวลาเปิดปั๊มต่อ step = 0.2 mL / flow_rate(ที่สอบเทียบ) → ปริมาตรที่จ่ายตรงจริง
   • pH คำนวณจาก ADC ดิบด้วยสมการของนิสิต:  pH = slope·mV + intercept
   • volume_ml (mL) , pH , temp_c (°C) เลื่อนขึ้นแบบสด
   • buzzer ดังเตือนเมื่อใกล้จุดสมมูล (ที่ ALERT_VOLUME_ML)
   • กด Stop ในแอปเพื่อหยุดได้ตลอดเวลา (ปั๊มปิดทันที)
```

### ขั้นตอนที่ 4: อ่านผลลัพธ์ (Read the result event)

```
เมื่อเสร็จ แอปจะแสดง event:  titration_complete
   • equivalence_volume_ml     (ปริมาตรที่จุดสมมูล)
   • equivalence_ph_estimate   (pH ที่จุดสมมูล — ค่าประมาณ)
   • unknown_concentration_m   (ความเข้มข้นที่คำนวณได้ mol/L)
```

> ตัวอย่างผลที่ตรวจสอบแล้ว (HCl 0.1 M 5 mL + NaOH 0.1 M):
> **V_eq ≈ 5.0 mL · pH ≈ 7.0 · C(HCl) ≈ 0.1 mol/L**

---

## ปุ่มและอุปกรณ์บนบอร์ด (On-Board Controls)

| สิ่ง | ขา/Endpoint | หน้าที่ในบทเรียน |
|------|:-----------:|------------------|
| **BUTTON_1** | GPIO34 (input-only) | กดเพื่อเริ่ม local (เมื่อ `WAIT_FOR_LOCAL_START=True`) |
| **GREEN LED** | GPIO4 (output) | ติด = กำลังทำงาน |
| **BUZZER** | GPIO26 | เสียงเตือนใกล้จุดสมมูล + เสียงเสร็จสิ้น |
| **pH probe** | GPIO32 (ADC1) | อ่าน **ADC ดิบ** (`slp.read_analog('PH')`) → แปลงเป็น pH ด้วยสอบเทียบของนิสิต |
| **DS18B20 temp** | GPIO16 (OneWire) | อ่านอุณหภูมิ |
| **Pump** | `CONTROL_1` | ปั๊มจ่ายไทแทรนต์ (เวลาเปิด = ปริมาตร/flow_rate · guarded ด้วย `max_on_ms`) |

> **การควบคุมหลักอยู่ที่แอป (Stop/Run) ไม่ใช่ปุ่มบนบอร์ด** BUTTON_1 มีไว้เพื่อ "เริ่ม local" เท่านั้น
> เลขขาส่วนใหญ่เป็นของ routing profile ในเฟิร์มแวร์ บทเรียนใช้ **ชื่อ endpoint** (`CONTROL_1`, `PH`)
> ส่วนเลขขาใน `experiment.py` (32 เป็น fallback ของ pH, 16) มีเพราะ helper `slp.ds18b20(num)` / `slp.pin(num)` รับเลขขาตรง ๆ

---

## ตารางการต่อสาย / แผนที่ขา (Board Wiring / Pin Map) — ตารางอ้างอิงหลัก

> **นี่คือตารางเต็มที่ `LAB_DIRECTION.md` อ้างถึง (This is the full table `LAB_DIRECTION.md` points to).**
>
> **Routing profile เริ่มต้น:** `titralab_v1_default` (ณ วันที่ 2026-06-25)
> **แหล่งข้อมูลจริง (SOURCE OF TRUTH):** `firmware/routing_profiles/titralab_v1_default.toml`
> ตารางนี้เป็น **สำเนาสะท้อน (mirror)** ของ profile นั้น — ถ้า profile เปลี่ยน ต้อง **ซิงก์ตารางนี้ใหม่**
> (บอร์ดเป็นการออกแบบตายตัวของผู้ใช้ จึงแทบไม่เปลี่ยน / The board is the user's fixed design, so it rarely changes.)

TitraLab Ver. 1.0 เป็นบอร์ด ESP32 แบบ **patch-panel/จัมเปอร์** มี header สองชุด: **GPIO header** กับ **DEVICES header** นิสิตใช้สายจัมเปอร์ต่อระหว่างสอง header ให้ตรงกับ profile (TitraLab Ver. 1.0 is a jumper-configurable ESP32 board; students patch the GPIO header to the DEVICES header to match the profile.)

### ตารางที่ 1 — Endpoints แบบจัมเปอร์ (Jumper-Configurable Endpoints)

ต่อด้วยสายจัมเปอร์ระหว่าง GPIO header ↔ DEVICES header ให้ตรงตามนี้ (Patch these with jumper wires):

| Endpoint | GPIO | Device / อุปกรณ์ | Notes / หมายเหตุ |
|----------|:----:|------------------|------------------|
| `RED` | 2 | RED LED | output |
| `GREEN` | 4 | GREEN LED | output · **ใช้ในบทเรียน** = แสดงสถานะ "กำลังทำงาน" |
| `BUTTON_1` | 34 | ปุ่มกด 1 / Button 1 | **input-only** · **ใช้ในบทเรียน** = เริ่ม local + safe-mode/pairing |
| `BUTTON_2` | 35 | ปุ่มกด 2 / Button 2 | **input-only** |
| `BUTTON_3` | 39 | ปุ่มกด 3 / Button 3 | **input-only** · safe-mode/cancel |
| `DS18B20` | 16 | เซ็นเซอร์อุณหภูมิ / temperature | **1-Wire** · ต้องมี pull-up **4.7 kΩ** · **ใช้ในบทเรียน** = อ่าน temp |
| `RELAY` | 17 | รีเลย์ / relay | actuator · guard max-on **5000 ms** |
| `CONTROL_1` | 21 | ปั๊ม / pump | actuator · guard max-on **5000 ms** · **ใช้ในบทเรียน** = ปั๊มจ่ายไทแทรนต์ |
| `CONTROL_2` | *(verify)* | — | **UNMAPPED — ห้ามใช้ในบทเรียน (do NOT use)** |
| `BUZZER` | 26 | บัซเซอร์ / buzzer | actuator · guard max-on **1500 ms** · **ใช้ในบทเรียน** = เสียงเตือน/เสร็จสิ้น |
| `PH_PROBE` | 32 | หัววัด pH / pH probe | **ADC1, wireless-safe** (ไม่ใช่ GPIO25/ADC2) · **ใช้ในบทเรียน** = อ่าน pH |
| `POT_1` | 32 | โพเทนชิออมิเตอร์ 1 / pot 1 | **ใช้สาย ADC1 ร่วมกับ `PH_PROBE`** — ใช้ไม่ได้เมื่อ pH อยู่ที่ GPIO32 |
| `POT_2` | 33 | โพเทนชิออมิเตอร์ 2 / pot 2 | ADC1 |

> บทเรียนรุ่นลีนนี้ (`01_titration_auto.py` / `titration.py` / `experiment.py`) ใช้เพียง **6 endpoint**: `PH_PROBE`, `DS18B20`, `CONTROL_1`, `GREEN`, `BUTTON_1`, `BUZZER` (This lean lesson uses only these 6 endpoints.)
>
> **เพดานความปลอดภัยของ actuator (hardware-guard max-on):** เฟิร์มแวร์ตัดเอาต์พุตเมื่อถึงเวลานี้ ไม่ว่าสคริปต์จะสั่งอะไร — `RELAY` = 5000 ms, `CONTROL_1` = 5000 ms, `BUZZER` = 1500 ms (Firmware cuts the output at this time regardless of the script.)

### ตารางที่ 2 — บัสบน PCB แบบตายตัว (Fixed PCB Buses)

**ห้ามต่อสายจัมเปอร์ใหม่ / ห้ามกำหนดขาใหม่** — เป็นวงจรตายตัวบน PCB และเฟิร์มแวร์เป็นเจ้าของ (Never re-patch or reassign — these are hardwired on the PCB and firmware-owned.)

| Bus | ขา (Pins) | หมายเหตุ / Notes |
|-----|-----------|------------------|
| **ILI9341 TFT** (firmware-owned) | SCK=14, MOSI=13, DC=27, CS=15 | MISO = unused/verify (GPIO0) · เฟิร์มแวร์วาดหน้า splash เอง |
| **MicroSD (SPI)** | SCK=18, MOSI=23, MISO=19, CS=5 | mount ที่ `/sd` |

### หมายเหตุความปลอดภัย / ขาสงวน (Safety / Reserved Pin Notes)

- **ขา input-only (เป็น output ไม่ได้ / cannot drive outputs):** GPIO **34, 35, 36, 39** — เหมาะกับปุ่มกด (buttons) เท่านั้น
- **ห้ามใช้เป็น student IO (forbidden / do-not-use):** GPIO **0, 5, 12, 15** (strapping / TFT / SD)
- **ADC2 (GPIO 25/26/27) ชนกับ Wi-Fi** — `PH_PROBE` จึงอยู่บน **ADC1 (GPIO32)** เสมอ (ห้ามย้าย pH ไป GPIO25)
- **Safe-mode bootstrap:** กดค้าง `BUTTON_1` + `BUTTON_3` (GPIO34 + GPIO39) ~**1.5 วินาที** ตอนบูต
- **Pairing (จับคู่):** กดค้าง `BUTTON_1` ~**3 วินาที**
- **Cancel (ยกเลิก):** กดค้าง `BUTTON_3` ~**3 วินาที**

### ขั้นตอนต่อสายจัมเปอร์ก่อนรันบทเรียน (Jumper Setup Workflow)

ก่อนรันบทเรียน ให้ patch บอร์ดให้ตรงกับ `titralab_v1_default` (Before running the lesson, patch the board to match `titralab_v1_default`):

1. **ดูตารางที่ 1** แล้วต่อสายจัมเปอร์จากขา GPIO ฝั่ง **GPIO header** ไปยังอุปกรณ์ฝั่ง **DEVICES header** ทีละ endpoint (เช่น GPIO32 → `PH_PROBE`, GPIO16 → `DS18B20`, GPIO21 → `CONTROL_1`, GPIO4 → `GREEN`, GPIO34 → `BUTTON_1`, GPIO26 → `BUZZER`).
2. สำหรับ `DS18B20` (GPIO16) ต้องมีตัวต้านทาน **pull-up 4.7 kΩ** บนสายข้อมูล 1-Wire (ปกติบอร์ดเตรียมไว้แล้ว — ตรวจให้แน่ใจ).
3. **อย่าแตะ** ตารางที่ 2 (TFT / MicroSD) — เป็นวงจรตายตัว.
4. บทเรียน **อ้างถึงอุปกรณ์ด้วยชื่อ endpoint** (เช่น `slp.set_actuator('CONTROL_1', ...)`) แล้ว **เฟิร์มแวร์แปลงชื่อ → หมายเลขขา GPIO** ให้เอง ดังนั้นถ้าวันใดมีการเปลี่ยนการต่อสาย เพียงอัปเดต routing profile ในเฟิร์มแวร์ก็พอ ไม่ต้องแก้โค้ดบทเรียน (The lesson refers to devices by endpoint NAME; the firmware maps name → GPIO. Re-wiring means updating the profile, not the lesson code.)
5. ส่วนเลขขาที่โผล่ใน `experiment.py` / `01_titration_auto.py` (32, 16, 4, 34, 26) มีไว้เพราะ helper บางตัว (`slp.ds18b20(num)`, `slp.pin(num)`, `slp.buzzer(num)`) รับ **เลขขาตรง ๆ** — เลขเหล่านี้ตรงกับ `titralab_v1_default` ส่วน pH อ่านด้วยชื่อ endpoint `slp.read_analog('PH')` (มี `slp.pin(32, input=True)` เป็น fallback) (These pin numbers in the lesson match `titralab_v1_default`.)

---

## ปรับค่าการทดลอง (Tune) — `experiment.py`

| ค่าคงที่ | ค่าเริ่มต้น | ปรับเมื่อไหร่ |
|----------|:-----------:|--------------|
| `DOSE_VOLUME_ML` | 0.2 mL | ต้องการกราฟละเอียดขึ้น → ลดค่า |
| `SAMPLE_VOLUME_ML` | 5.0 mL | ตามปริมาตร analyte จริง |
| `MAX_VOLUME_ML` | 10.0 mL | ถ้าจุดสมมูลเกินช่วง → เพิ่มค่า |
| `TITRANT_CONCENTRATION_M` | 0.1 mol/L | ตามความเข้มข้น titrant จริง |
| `STOICHIOMETRIC_RATIO` | 1.0 | กรด/เบสไม่ใช่ 1:1 (เช่น H2SO4 → 0.5) |
| `SETTLE_MS` | 10000 ms | **ทดสอบเร็วใช้ 2000; จริงใช้ 10000** |
| `ALERT_VOLUME_ML` | 4.80 mL | ปรับตามจุดสมมูลที่คาด |

> **ค่าสอบเทียบไม่ได้ปรับที่นี่ (calibration is NOT tuned here):** `PH_CAL_PATH`, `FLOW_CAL_PATH`,
> `RAW_TO_MV` ใน `experiment.py` ชี้/แปลงผลสอบเทียบที่นิสิตทำใน Week_2 ปกติไม่ต้องแก้ ถ้าต้องการ
> เปลี่ยน slope/intercept หรือ flow rate ให้ **สอบเทียบใหม่ใน Week_2** แล้ว Week_3 จะอ่านค่าใหม่อัตโนมัติ

**วิธีตั้ง alert_volume:** `ALERT_VOLUME_ML = (จุดสมมูลที่คาด) − (1–2 × DOSE_VOLUME_ML)`
ตัวอย่าง HCl 0.1 M 5 mL + NaOH 0.1 M → จุดสมมูล ≈ 5.0 → `5.0 − 0.2 = 4.80 mL`

---

## เสียง buzzer (Buzzer cues)

| เสียง | ความหมาย |
|-------|----------|
| บี๊บสั้นเสียงสูง (2000 Hz) | ใกล้จุดสมมูล (ถึง `ALERT_VOLUME_ML`) — เตรียมสังเกต |
| สองโน้ต (1000 → 1500 Hz) | ไทเทรชันเสร็จสิ้น |

---

## แก้ปัญหาเบื้องต้น (Quick Troubleshooting)

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|-------|--------|
| `ph_calibration_missing` (หยุดทันที) | ยังไม่ได้สอบเทียบ pH ใน Week_2 / ไฟล์หาย | รัน `Week_2/01_pH_Sensor/02_calibration_3point.py` → รัน Week_3 ใหม่ |
| `flow_calibration_missing` (หยุดทันที) | ยังไม่ได้สอบเทียบอัตราการไหลใน Week_2 / ไฟล์หาย | รัน `Week_2/02_Pump_Control/01_flow_rate_calibration.py` → รัน Week_3 ใหม่ |
| pH เพี้ยน / ปริมาตรเพี้ยน | ใช้ไฟล์สอบเทียบของบอร์ดอื่น / สอบเทียบ Week_2 คุณภาพต่ำ | สอบเทียบใหม่ "บนบอร์ดตัวนี้" (R² ≥ 0.99, RSD ต่ำ) |
| ไม่เห็นค่าในแอป | ยังไม่จับคู่ BLE / ไม่ได้ Run | จับคู่ใหม่ → เปิด `01_titration_auto.py` → Run |
| ค้างที่ `waiting_for_start` | รอกดปุ่มเริ่ม | กด BUTTON_1 บนบอร์ด หรือรอ timeout |
| ขึ้น `temp_sensor_warning` | สาย DS18B20 หลุด/ไม่มี pull-up 4.7K | ตรวจสายขา 16; ระบบใช้ 25 °C ต่อได้ |
| ไม่พบจุดสมมูล | ข้อมูล < 3 จุด / ปริมาตรไม่ถึง | เพิ่ม `MAX_VOLUME_ML` / ตรวจความเข้มข้น |
| ปั๊มไม่ทำงาน | ต่อปั๊มผิด endpoint | ต่อปั๊มที่ `CONTROL_1` ให้ตรง `PUMP_ENDPOINT` |
| ปั๊มเปิดค้าง | — | ฮาร์ดแวร์ไทเมอร์ตัดเองที่ `DOSE_MAX_ON_MS`; กด Stop ในแอปได้ |

---

## หมายเหตุสำคัญ (Important Notes)

1. **ล้างหัววัด pH** ด้วยน้ำกลั่นทุกครั้งที่เปลี่ยนสารละลาย แล้วซับให้แห้ง (ห้ามถู)
2. **หัววัดต้องจม** ถึง glass bulb ตลอดการวัด (เติมน้ำกลั่นได้โดยไม่เปลี่ยนจำนวนโมล)
3. **การสอบเทียบเป็นงานของนิสิต** — ทำใน Week_2 (pH 3 จุด + อัตราการไหลปั๊ม) บน "บอร์ดตัวเอง" ก่อนเสมอ
   Week_3 อ่านไฟล์ผลสอบเทียบมาใช้จริง (ไม่ใช้ค่าคงที่ตายตัว และไม่ใช่ "กล่องดำ" ของเฟิร์มแวร์)
4. **บทเรียนนี้ไม่มีโหมดสอบเทียบ** — ถ้าไฟล์สอบเทียบหาย Week_3 จะหยุดและบอกให้ไปสอบเทียบ Week_2 ก่อน
5. **กด Stop ในแอป** เพื่อหยุดได้ทุกเมื่อ ปั๊มจะปิดทันทีและถูก guard ด้วยฮาร์ดแวร์ไทเมอร์
6. **อ่านผลที่ event** `titration_complete` ในแอป (ไม่ต้องดาวน์โหลดไฟล์)

---

*Lean User Manual for Week 3 — app is the display, raw drivers live in firmware, calibration is the student's own Week_2 work that Week_3 reads and applies.*
*คู่มือใช้งานรุ่นลีน — แอปเป็นจอแสดงผล, ไดรเวอร์ดิบอยู่ในเฟิร์มแวร์, การสอบเทียบเป็นงานของนิสิตจาก Week_2 ที่ Week_3 อ่านมาใช้.*

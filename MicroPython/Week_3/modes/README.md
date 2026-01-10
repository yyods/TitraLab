# Modes Layer (Layer 3)
# ชั้น Operating Modes

---

## ภาพรวม (Overview)

โฟลเดอร์ `modes/` คือชั้นที่ 3 ของสถาปัตยกรรม TitraLab ทำหน้าที่กำหนด **พฤติกรรมของแต่ละโหมดการทำงาน** โดยใช้รูปแบบ **Inheritance (การสืบทอด)** จาก BaseMode

The `modes/` folder is Layer 3 of the TitraLab architecture. It defines the **behavior of each operating mode** using **Inheritance** from BaseMode.

### หลักการสำคัญ (Key Principles)

1. **Abstract Base Class**: BaseMode กำหนด lifecycle methods ที่ทุกโหมดต้อง implement
2. **Polymorphism/พหุสัณฐาน**: ทุกโหมดมี interface เดียวกัน แต่พฤติกรรมต่างกัน
3. **Lifecycle Pattern**: on_enter() → update() → on_exit()

---

## โครงสร้างไฟล์ (File Structure)

```
modes/
├── __init__.py              # Package initialization
├── base_mode.py             # Abstract Base Class
├── mode_calibrate_ph.py     # Mode 1: สอบเทียบ pH
├── mode_test_ph.py          # Mode 2: ทดสอบ pH
├── mode_calibrate_flow.py   # Mode 3: สอบเทียบอัตราการไหล
├── mode_test_flow.py        # Mode 4: ทดสอบอัตราการไหล
├── mode_purge.py            # Mode 5: ล้างท่อ
└── mode_titration.py        # Mode 6: ไทเทรชันอัตโนมัติ
```

---

## BaseMode - คลาสพื้นฐาน (Abstract Base Class)

`BaseMode` คือ Abstract Base Class ที่กำหนด **lifecycle** และ **interface** ที่ทุกโหมดต้องปฏิบัติตาม

### Lifecycle ของโหมด (Mode Lifecycle)

```
┌─────────────────────────────────────────────────────────────────┐
│                       MODE LIFECYCLE                             │
│                                                                  │
│   ┌─────────────┐                                               │
│   │  on_enter() │  ← เรียกเมื่อเข้าโหมด (Enter mode)            │
│   │  - Setup    │    - Initialize variables                     │
│   │  - Display  │    - Show initial screen                      │
│   └──────┬──────┘                                               │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │   update()  │  ← เรียกทุก loop iteration                    │
│   │  - Process  │    - Check inputs                             │
│   │  - Display  │    - Update state                             │
│   │  ─────────  │    - Update display                           │
│   │ is_complete │    - Set _complete when done                  │
│   │    ?        │                                               │
│   └──────┬──────┘                                               │
│          │ (เมื่อ is_complete() = True)                         │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │  on_exit()  │  ← เรียกเมื่อออกจากโหมด (Exit mode)           │
│   │  - Cleanup  │    - Stop hardware                            │
│   │  - Save     │    - Save results                             │
│   └─────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### การสร้างโหมดใหม่ (Creating a New Mode)

```python
from modes.base_mode import BaseMode

class MyMode(BaseMode):
    """ตัวอย่างการสร้างโหมดใหม่"""

    def __init__(self, display, colors, my_hardware):
        super().__init__(display, colors, "My Mode Name")
        self.my_hardware = my_hardware
        self.my_data = []

    def on_enter(self):
        """เรียกเมื่อเข้าโหมด"""
        super().on_enter()          # เรียก parent's on_enter
        self.my_data = []           # Reset data
        self.display.clear()
        self.display.draw_header(self.name)

    def update(self):
        """เรียกทุก loop - ต้อง implement"""
        # อ่านค่า
        value = self.my_hardware.read()
        self.my_data.append(value)

        # อัปเดตหน้าจอ
        self.display.draw_text(10, 50, f"Value: {value}")

        # ตรวจสอบปุ่ม
        if self.check_button('select'):
            self.set_complete()     # ทำเสร็จแล้ว

        if self.check_button('down'):
            self.set_complete()     # ยกเลิก

    def on_exit(self):
        """เรียกเมื่อออกจากโหมด"""
        super().on_exit()
        # บันทึกผลลัพธ์
        self.set_results(data=self.my_data)
```

### Helper Methods ที่ BaseMode จัดให้ (BaseMode Helper Methods)

| Method | คำอธิบาย |
|--------|----------|
| `check_button(name)` | ตรวจสอบปุ่มพร้อม debounce ('select', 'up', 'down') |
| `wait_button_press(name, timeout_ms)` | รอจนกว่าปุ่มจะถูกกด |
| `get_elapsed_time()` | รับเวลาที่ผ่านไปตั้งแต่เริ่มโหมด (วินาที) |
| `set_complete()` | กำหนดให้โหมดเสร็จสิ้น |
| `is_complete()` | ตรวจสอบว่าโหมดเสร็จสิ้นหรือยัง |
| `set_results(**kwargs)` | บันทึกผลลัพธ์ |
| `get_results()` | รับผลลัพธ์ |
| `show_countdown(seconds, message)` | แสดงการนับถอยหลัง |
| `show_instruction(title, message)` | แสดงคำแนะนำและรอปุ่ม |

---

## 6 โหมดการทำงาน (The 6 Operating Modes)

### Mode 1: CalibratePHMode - สอบเทียบ pH

**ไฟล์**: `mode_calibrate_ph.py`

**วัตถุประสงค์**: สร้างสมการ `pH = slope * voltage + intercept` จากบัฟเฟอร์มาตรฐาน

**ขั้นตอนการทำงาน**:
```
1. แสดงคำแนะนำ "แช่หัววัดในบัฟเฟอร์ pH 4.00"
2. รอผู้ใช้กด SELECT เพื่อบันทึกค่า
3. แสดงคำแนะนำ "แช่หัววัดในบัฟเฟอร์ pH 7.00"
4. รอผู้ใช้กด SELECT เพื่อบันทึกค่า
5. แสดงคำแนะนำ "แช่หัววัดในบัฟเฟอร์ pH 10.00"
6. รอผู้ใช้กด SELECT เพื่อบันทึกค่า
7. คำนวณ Linear Regression
8. แสดงผล slope, intercept, R²
9. บันทึกค่าถ้า R² >= 0.99
```

**ผลลัพธ์**:
```python
{
    'slope': -5.7901,
    'intercept': 16.769,
    'r_squared': 0.9998,
    'is_valid': True
}
```

---

### Mode 2: TestPHMode - ทดสอบ pH

**ไฟล์**: `mode_test_ph.py`

**วัตถุประสงค์**: แสดงค่า pH และแรงดันแบบ real-time

**การทำงาน**:
- อ่านค่าทุก 1 วินาที
- แสดงค่า Voltage และ pH บนหน้าจอ
- กด DOWN เพื่อออก

**หน้าจอ**:
```
+----------------------------------+
|         pH Sensor Test           |
+----------------------------------+
|                                  |
|   Voltage: 2.0123 V              |
|   pH:      7.02                  |
|   Temp:    25.1 C                |
|                                  |
+----------------------------------+
|  Press DOWN to exit              |
+----------------------------------+
```

---

### Mode 3: CalibrateFlowMode - สอบเทียบอัตราการไหล

**ไฟล์**: `mode_calibrate_flow.py`

**วัตถุประสงค์**: วัดอัตราการไหลจริงของปั๊ม (mL/s)

**ขั้นตอนการทำงาน**:
```
1. แสดงคำแนะนำ "เตรียมภาชนะรับของเหลว"
2. รอผู้ใช้กด SELECT
3. เริ่มปั๊มที่ 100% duty cycle
4. รอผู้ใช้กด SELECT เมื่อได้ปริมาตรเป้าหมาย (5 mL)
5. หยุดปั๊มและบันทึกเวลา
6. คำนวณ flow_rate = volume / time
7. บันทึกค่า
```

**ผลลัพธ์**:
```python
{
    'flow_rate': 0.2772,  # mL/s
    'volume': 5.0,        # mL
    'time': 18.05         # seconds
}
```

---

### Mode 4: TestFlowMode - ทดสอบอัตราการไหล

**ไฟล์**: `mode_test_flow.py`

**วัตถุประสงค์**: ยืนยันความแม่นยำของ flow rate ที่สอบเทียบไว้

**การทำงาน**:
- สูบปริมาตรที่กำหนด (เช่น 2 mL)
- ให้ผู้ใช้วัดปริมาตรจริง
- คำนวณ % ความคลาดเคลื่อน

---

### Mode 5: PurgeMode - ล้างท่อ

**ไฟล์**: `mode_purge.py`

**วัตถุประสงค์**: ไล่อากาศและทำความสะอาดท่อปั๊ม

**การทำงาน**:
- เปิดปั๊ม 100% เป็นเวลา 3 วินาที (default)
- แสดง countdown บนหน้าจอ
- หยุดปั๊มอัตโนมัติเมื่อครบเวลา

```python
# การใช้งาน
purge_mode.set_duration(5000)  # ตั้งเวลา 5 วินาที
```

---

### Mode 6: TitrationMode - ไทเทรชันอัตโนมัติ

**ไฟล์**: `mode_titration.py`

**วัตถุประสงค์**: ดำเนินการไทเทรตอัตโนมัติพร้อมตรวจจับจุดสมมูล

**ขั้นตอนการทำงาน**:
```
1. แสดงคำแนะนำและตรวจสอบการสอบเทียบ
2. เริ่ม Fast Dosing (100% duty)
3. เมื่อใกล้จุดสมมูล → Slow Dosing (50% duty)
4. ตรวจจับจุดสมมูล (|dpH/dV| สูงสุด)
5. หยุดปั๊มและแสดงผลลัพธ์
6. บันทึกข้อมูลลง ESP32 flash (ดาวน์โหลดผ่าน Thonny IDE)
```

**State Machine ภายใน TitrationMode**:
```
┌──────────────┐   pH ห่างจาก target   ┌──────────────┐
│  FAST_DOSE   │ ──────────────────► │  SLOW_DOSE   │
│   (100%)     │   < 1.5 units       │    (50%)     │
└──────────────┘                      └──────┬───────┘
                                             │
                                             │ |dpH/dV| สูงสุด
                                             ▼
                                      ┌──────────────┐
                                      │   ENDPOINT   │
                                      │    (STOP)    │
                                      └──────────────┘
```

**ผลลัพธ์**:
```python
{
    'equivalence_volume': 25.3,   # mL
    'equivalence_ph': 7.02,
    'total_volume': 25.5,         # mL
    'total_time': 312,            # seconds
    'data_file': 'titration_data_R1.csv'  # บน ESP32 flash
}
```

---

## ตารางสรุปโหมด (Mode Summary Table)

| โหมด | ไฟล์ | วัตถุประสงค์ | Output |
|:----:|------|-------------|--------|
| 1 | `mode_calibrate_ph.py` | สอบเทียบ pH 3 จุด | slope, intercept, R² |
| 2 | `mode_test_ph.py` | ทดสอบ pH real-time | pH, Voltage (display) |
| 3 | `mode_calibrate_flow.py` | สอบเทียบ flow rate | flow_rate (mL/s) |
| 4 | `mode_test_flow.py` | ทดสอบ flow rate | % error |
| 5 | `mode_purge.py` | ล้างท่อ | - |
| 6 | `mode_titration.py` | ไทเทรชันอัตโนมัติ | eq. point, CSV file |

---

## Inheritance Diagram (แผนภาพการสืบทอด)

```
                    ┌────────────────────────────────────────┐
                    │              BaseMode                   │
                    │  (Abstract Base Class)                  │
                    │                                         │
                    │  + on_enter()                           │
                    │  + update()        ← Must override      │
                    │  + on_exit()                            │
                    │  + is_complete()                        │
                    │  + check_button()                       │
                    └────────────────────┬───────────────────┘
                                         │
            ┌────────────────┬───────────┼───────────┬────────────────┐
            │                │           │           │                │
            ▼                ▼           ▼           ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ CalibratePH  │ │   TestPH     │ │CalibrateFlow │ │  Titration   │
    │    Mode      │ │    Mode      │ │    Mode      │ │    Mode      │
    └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
           │                │                │                │
           │                │                │                │
    Override update()  Override update()  Override update()  Override update()
    to implement       to implement       to implement       to implement
    3-point calib.     real-time pH       flow calibration   auto titration
```

---

## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

หลังจากศึกษาโฟลเดอร์นี้ นักศึกษาจะสามารถ:

1. **เข้าใจ Abstract Base Class**: การกำหนด interface ที่บังคับให้ subclass implement
2. **ใช้ Inheritance/การสืบทอด**: สร้าง class ใหม่โดยสืบทอดจาก BaseMode
3. **เข้าใจ Polymorphism/พหุสัณฐาน**: ทุกโหมดมี interface เดียวกัน ใช้แทนกันได้
4. **ออกแบบ Lifecycle Pattern**: on_enter(), update(), on_exit()

---

## ลำดับการศึกษาแนะนำ (Recommended Study Order)

1. `base_mode.py` - เข้าใจ lifecycle และ interface ก่อน
2. `mode_purge.py` - โหมดง่ายที่สุด (ไม่มี logic ซับซ้อน)
3. `mode_test_ph.py` - โหมดอ่านค่าอย่างง่าย
4. `mode_calibrate_ph.py` - โหมดที่มี state หลายขั้นตอน
5. `mode_calibrate_flow.py` - คล้ายกับ calibrate_ph
6. `mode_test_flow.py` - ใช้ค่าจาก calibration
7. `mode_titration.py` - โหมดซับซ้อนที่สุด (state machine ภายใน)

---

*TitraLab Week 3 - Operating Modes Layer*

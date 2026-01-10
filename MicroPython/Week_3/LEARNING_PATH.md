# LEARNING_PATH.md
# เส้นทางการเรียนรู้ Week 3

---

## ภาพรวม (Overview)

เอกสารนี้แนะนำลำดับการศึกษาไฟล์ใน Week 3 สำหรับนักศึกษาเคมีที่ต้องการเข้าใจระบบไทเทรชันอัตโนมัติของ TitraLab อย่างลึกซึ้ง

This document guides the file study order in Week 3 for chemistry students who want to deeply understand the TitraLab automated titration system.

---

## ความรู้พื้นฐานที่ต้องมี (Prerequisites)

### จาก Week 1: พื้นฐาน Hardware

| หัวข้อ | ไฟล์ที่เกี่ยวข้อง | สิ่งที่ต้องรู้ |
|--------|-----------------|---------------|
| LED Control | `core/02_led_class.py` | `Pin.OUT`, `.value()` |
| Button Input | `core/03_button_class.py` | `Pin.IN`, debounce |
| ADC | `core/07_ADC/` | 12-bit (0-4095), attenuation |
| PWM | `core/07_PWM/` | duty cycle (0-1023), frequency |
| Temperature | `core/04_temp_sensor_class.py` | DS18B20, OneWire |
| TFT Display | `core/05_display_basics.py` | SPI, ili9341 |
| OOP Basics | `core/01_intro_oop.py` | Class, Object, self |

### จาก Week 2: การสอบเทียบและการวัด

| หัวข้อ | สิ่งที่ต้องรู้ |
|--------|---------------|
| pH Sensor | อ่านค่า ADC → แปลงเป็น voltage → แปลงเป็น pH |
| pH Calibration | 3-point calibration, Linear Regression |
| Nernst Equation | E = E0 - 59.16 mV * pH (ที่ 25 C) |
| Pump Control | PWM duty cycle → flow rate (mL/s) |
| Flow Calibration | วัดปริมาตรจริง → คำนวณ flow rate |

### ตรวจสอบความพร้อม (Self-Check)

ก่อนเริ่ม Week 3 ลองตอบคำถามเหล่านี้:

1. `adc.read()` คืนค่าในช่วงใด? (คำตอบ: 0-4095)
2. `pwm.duty(512)` หมายความว่าอย่างไร? (คำตอบ: 50% duty cycle)
3. สมการ `pH = slope * voltage + intercept` ได้มาอย่างไร? (คำตอบ: Linear Regression)
4. R-squared ที่ดีสำหรับการสอบเทียบ pH ควรมีค่าเท่าไร? (คำตอบ: >= 0.99)

---

## เส้นทางการเรียนรู้ (Learning Paths)

### เส้นทาง A: ภาพรวมระบบ (System Overview)

**เหมาะสำหรับ**: นักศึกษาที่ต้องการเข้าใจภาพรวมก่อนลงรายละเอียด

```
เวลาโดยประมาณ: 2-3 ชั่วโมง
Estimated time: 2-3 hours
```

| ขั้นตอน | ไฟล์ | เป้าหมาย | เวลา |
|:-------:|------|----------|:----:|
| 1 | `README.md` | เข้าใจสถาปัตยกรรม 4 ชั้น | 30 นาที |
| 2 | `main.py` | ดูการประกอบระบบ | 30 นาที |
| 3 | `config.py` | เข้าใจ GPIO configuration | 20 นาที |
| 4 | `hardware/__init__.py` | ดู HardwareHub pattern | 30 นาที |
| 5 | `modes/base_mode.py` | เข้าใจ lifecycle pattern | 30 นาที |
| 6 | `ui/menu.py` | เข้าใจ State Machine | 30 นาที |

### เส้นทาง B: Hardware Layer (ชั้น 1)

**เหมาะสำหรับ**: นักศึกษาที่ต้องการเข้าใจการเข้าถึง hardware

```
เวลาโดยประมาณ: 3-4 ชั่วโมง
Estimated time: 3-4 hours
```

| ขั้นตอน | ไฟล์ | เป้าหมาย | ความยาก |
|:-------:|------|----------|:-------:|
| 1 | `hardware/leds.py` | Digital Output พื้นฐาน | ง่าย |
| 2 | `hardware/buttons.py` | Digital Input + debounce | ง่าย |
| 3 | `hardware/buzzer.py` | PWM Output อย่างง่าย | ง่าย |
| 4 | `hardware/pump.py` | PWM Output + volume tracking | ปานกลาง |
| 5 | `hardware/ph_sensor.py` | ADC Input + calibration | ปานกลาง |
| 6 | `hardware/temp_sensor.py` | OneWire protocol | ปานกลาง |
| 7 | `hardware/display.py` | SPI + graphics | ซับซ้อน |
| 8 | `hardware/sd_card.py` | File I/O | ปานกลาง |
| 9 | `hardware/__init__.py` | HardwareHub aggregation | ซับซ้อน |

### เส้นทาง C: Core Logic (ชั้น 2)

**เหมาะสำหรับ**: นักศึกษาที่ต้องการเข้าใจ logic ทางคณิตศาสตร์

```
เวลาโดยประมาณ: 2-3 ชั่วโมง
Estimated time: 2-3 hours
```

| ขั้นตอน | ไฟล์ | เป้าหมาย | ความเชื่อมโยงกับเคมี |
|:-------:|------|----------|---------------------|
| 1 | `core/math_utils.py` | Linear Regression, Statistics | สมการสอบเทียบ pH |
| 2 | `core/calibrator.py` | pH & Flow calibration | กระบวนการสอบเทียบ |
| 3 | `core/data_manager.py` | Data persistence | บันทึกผลการทดลอง |
| 4 | `core/titration.py` | Auto titration algorithm | หาจุดสมมูล |

### เส้นทาง D: Operating Modes (ชั้น 3)

**เหมาะสำหรับ**: นักศึกษาที่ต้องการเข้าใจการทำงานของแต่ละโหมด

```
เวลาโดยประมาณ: 3-4 ชั่วโมง
Estimated time: 3-4 hours
```

| ขั้นตอน | ไฟล์ | เป้าหมาย | ความยาก |
|:-------:|------|----------|:-------:|
| 1 | `modes/base_mode.py` | Abstract Base Class | ปานกลาง |
| 2 | `modes/mode_purge.py` | โหมดง่ายที่สุด | ง่าย |
| 3 | `modes/mode_test_ph.py` | โหมดอ่านค่าอย่างง่าย | ง่าย |
| 4 | `modes/mode_calibrate_ph.py` | โหมดหลายขั้นตอน | ปานกลาง |
| 5 | `modes/mode_calibrate_flow.py` | คล้าย calibrate_ph | ปานกลาง |
| 6 | `modes/mode_test_flow.py` | ใช้ค่า calibration | ปานกลาง |
| 7 | `modes/mode_titration.py` | โหมดซับซ้อนที่สุด | ซับซ้อน |

### เส้นทาง E: User Interface (ชั้น 4)

**เหมาะสำหรับ**: นักศึกษาที่ต้องการเข้าใจ State Machine

```
เวลาโดยประมาณ: 2 ชั่วโมง
Estimated time: 2 hours
```

| ขั้นตอน | ไฟล์ | เป้าหมาย |
|:-------:|------|----------|
| 1 | `ui/menu.py` (MenuState) | เข้าใจ State constants |
| 2 | `ui/menu.py` (ButtonHandler) | เข้าใจ event handling |
| 3 | `ui/menu.py` (MenuSystem) | เข้าใจ state transitions |
| 4 | `ui/screens.py` | ดูโครงสร้าง Screen classes |

---

## เส้นทางตามวัตถุประสงค์ (Goal-Based Paths)

### "ฉันต้องการรันระบบได้"

```
1. README.md (Quick Start section)
2. main.py
3. ลองรันด้วย: import main; main.main()
```

### "ฉันต้องการเข้าใจการสอบเทียบ pH"

```
1. Week 2: pH calibration basics
2. core/math_utils.py (LinearRegression)
3. core/calibrator.py (calibrate_ph)
4. modes/mode_calibrate_ph.py
```

### "ฉันต้องการเข้าใจการตรวจจับจุดสมมูล"

```
1. ทฤษฎี: วิธี Derivative (dpH/dV)
2. core/titration.py
3. modes/mode_titration.py
```

### "ฉันต้องการสร้างโหมดใหม่"

```
1. modes/base_mode.py (เข้าใจ lifecycle)
2. modes/mode_purge.py (ตัวอย่างง่ายๆ)
3. ลองสร้างโหมดใหม่
```

### "ฉันต้องการเพิ่ม hardware ใหม่"

```
1. hardware/__init__.py (ดูโครงสร้าง)
2. hardware/buzzer.py (ตัวอย่างง่ายๆ)
3. ลองสร้าง class สำหรับ hardware ใหม่
4. เพิ่มใน HardwareHub
```

---

## แผนที่ไฟล์และความสัมพันธ์ (File Map and Dependencies)

```
main.py
   │
   ├──► config.py (GPIO constants)
   │
   ├──► hardware/
   │       ├── __init__.py (HardwareHub)
   │       ├── pump.py ──────────────────┐
   │       ├── ph_sensor.py ─────────────┤
   │       ├── temp_sensor.py ───────────┤
   │       ├── display.py ───────────────┤
   │       ├── buttons.py ───────────────┤
   │       ├── buzzer.py ────────────────┤
   │       ├── leds.py ──────────────────┤
   │       └── sd_card.py ───────────────┘
   │                                      │
   │                                      ▼
   ├──► core/                        (ใช้โดย modes)
   │       ├── math_utils.py ◄───────────┤
   │       ├── calibrator.py ◄───────────┤
   │       ├── data_manager.py ◄─────────┤
   │       └── titration.py ◄────────────┘
   │
   ├──► modes/
   │       ├── base_mode.py (Abstract)
   │       │       ▲
   │       │       │ (inherit)
   │       ├── mode_calibrate_ph.py ─────┤
   │       ├── mode_test_ph.py ──────────┤
   │       ├── mode_calibrate_flow.py ───┤
   │       ├── mode_test_flow.py ────────┤
   │       ├── mode_purge.py ────────────┤
   │       └── mode_titration.py ────────┘
   │
   └──► ui/
           ├── menu.py (MenuSystem, State Machine)
           └── screens.py (Display screens)
```

---

## แบบฝึกหัด (Exercises)

### แบบฝึกหัดระดับ 1: พื้นฐาน

1. **อ่านและทำความเข้าใจ** `hardware/leds.py` แล้วอธิบายว่า LED class ทำงานอย่างไร
2. **ดัดแปลง** `modes/mode_purge.py` ให้แสดง countdown เป็นภาษาไทย
3. **ทดสอบ** `core/math_utils.py` โดยสร้างข้อมูลสมมติและคำนวณ Linear Regression

### แบบฝึกหัดระดับ 2: ปานกลาง

4. **สร้างโหมดใหม่** "Temperature Test" ที่แสดงอุณหภูมิแบบ real-time
5. **เพิ่ม feature** ในจอ TFT แสดงกราฟ pH vs time อย่างง่าย
6. **วิเคราะห์** flow ของ State Machine ใน `ui/menu.py`

### แบบฝึกหัดระดับ 3: ขั้นสูง

7. **เพิ่ม hardware** เซ็นเซอร์ใหม่ (เช่น Conductivity sensor)
8. **ปรับปรุง algorithm** ตรวจจับจุดสมมูลใน `core/titration.py`
9. **ออกแบบ** โหมดใหม่สำหรับ multi-point titration

---

## คำถามทบทวน (Review Questions)

### ระดับความเข้าใจ (Comprehension)

1. สถาปัตยกรรม 4 ชั้นของ TitraLab มีอะไรบ้าง?
2. Lifecycle ของ BaseMode ประกอบด้วย methods อะไรบ้าง?
3. State Machine ใน MenuSystem มีกี่สถานะ?

### ระดับการประยุกต์ใช้ (Application)

4. ถ้าต้องการเพิ่มเซ็นเซอร์ conductivity ต้องแก้ไขไฟล์ใดบ้าง?
5. ถ้าต้องการเปลี่ยน threshold ของ R-squared ต้องแก้ที่ไหน?
6. ถ้าต้องการเพิ่มโหมดที่ 7 ต้องทำอย่างไร?

### ระดับการวิเคราะห์ (Analysis)

7. เหตุใดจึงแยก hardware layer ออกจาก core layer?
8. ข้อดีของการใช้ Abstract Base Class สำหรับ modes คืออะไร?
9. ทำไมต้องใช้ State Machine ในการจัดการ UI?

---

## ทรัพยากรเพิ่มเติม (Additional Resources)

### เอกสารใน Repository

- `docs/agent-spec/` - AI agent specifications
- `Documents/` - Prelab PDFs

### แหล่งข้อมูลภายนอก

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)
- Harris, D.C. *Quantitative Chemical Analysis* (สำหรับทฤษฎีเคมี)

---

## สรุป (Summary)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     WEEK 3 LEARNING PROGRESSION                          │
│                                                                          │
│   Week 1 & 2 Prerequisites                                               │
│        │                                                                 │
│        ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  PHASE 1: Overview                                               │   │
│   │  main.py → config.py → README.md                                │   │
│   └──────────────────────────────┬──────────────────────────────────┘   │
│                                  │                                       │
│                                  ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  PHASE 2: Hardware Layer (Bottom-Up)                            │   │
│   │  leds → buttons → buzzer → pump → ph_sensor → ...               │   │
│   └──────────────────────────────┬──────────────────────────────────┘   │
│                                  │                                       │
│                                  ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  PHASE 3: Core Logic                                             │   │
│   │  math_utils → calibrator → data_manager → titration             │   │
│   └──────────────────────────────┬──────────────────────────────────┘   │
│                                  │                                       │
│                                  ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  PHASE 4: Modes & UI                                             │   │
│   │  base_mode → modes → menu → screens                              │   │
│   └──────────────────────────────┬──────────────────────────────────┘   │
│                                  │                                       │
│                                  ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  OPTIONAL: Async Support                                         │   │
│   │  (For advanced learners only)                                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*TitraLab Week 3 - Learning Path Guide*
*ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย*

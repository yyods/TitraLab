# 03_OOP_Advanced - แนวคิด OOP ขั้นสูง
# Advanced OOP Concepts

---

> **ส่วนนี้เป็นส่วนของ:** Week 2 - TitraLab MicroPython
> **เวลาที่ใช้:** 60 นาที (1 ชั่วโมง)

---

## สารบัญ (Table of Contents)

| หมวด | เนื้อหา |
|:----:|---------|
| 1 | [วัตถุประสงค์](#วัตถุประสงค์-objectives) |
| 2 | [ความรู้พื้นฐาน](#ความรู้พื้นฐาน-prerequisites) |
| 3 | [แนวคิดหลัก](#แนวคิดหลัก-key-concepts) |
| 4 | [ไฟล์ในโฟลเดอร์](#ไฟล์ในโฟลเดอร์-files-in-this-folder) |
| 5 | [รายละเอียดไฟล์](#รายละเอียดไฟล์-file-details) |
| 6 | [ตารางสรุป OOP](#ตารางสรุปแนวคิด-oop) |
| 7 | [แบบฝึกหัด](#แบบฝึกหัดเสริม-additional-exercises) |
| 8 | [การเชื่อมต่อ Week 3](#การเชื่อมต่อกับ-week-3-connection-to-week-3) |

---

## วัตถุประสงค์ (Objectives)

เมื่อจบบทเรียนนี้ นิสิตจะสามารถ:

1. **เข้าใจ Inheritance (การสืบทอด)** และใช้ `super().__init__()`
2. **เข้าใจ Composition (การประกอบ)** - Object มี Object อื่นเป็นส่วนประกอบ
3. **ใช้ @property decorator** สำหรับ Getter/Setter
4. **เห็นประโยชน์ของ OOP** ในการจัดระเบียบโค้ดระบบไทเทรต

---

## ความรู้พื้นฐาน (Prerequisites)

### จาก Week 1 - OOP พื้นฐาน

| แนวคิด | ไฟล์อ้างอิงใน Week 1 | Week 2 ต่อยอด |
|--------|---------------------|---------------|
| Class และ Object | `01_intro_oop.py` | Inheritance |
| `__init__` และ methods | `02_led_class.py` | Composition |
| Attributes | - | @property |

### ทางเคมี:
- ความเข้าใจเกี่ยวกับเซ็นเซอร์ pH และอุณหภูมิ
- หลักการควบคุมปั๊ม
- ค่าสอบเทียบจาก 01_pH_Sensor และ 02_Pump_Control

---

## แนวคิดหลัก (Key Concepts)

### 1. Inheritance (การสืบทอด/การสืบทอดคลาส)

**การเชื่อมโยงกับเคมี:**
- หัววัด pH และหัววัดอุณหภูมิ เป็น "เซ็นเซอร์" ทั้งคู่
- เหมือนกับที่ "กรดแก่" และ "กรดอ่อน" เป็นประเภทของ "กรด"

```
         ┌───────────────────┐
         │    BaseSensor     │     <- คลาสแม่ (Parent Class)
         │  (เซ็นเซอร์ทั่วไป)  │
         └─────────┬─────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         v                   v
┌─────────────────┐  ┌─────────────────┐
│    PHSensor     │  │   TempSensor    │
│ (เซ็นเซอร์ pH)   │  │ (เซ็นเซอร์อุณหภูมิ) │
│                 │  │                 │
│ สืบทอดจาก        │  │ สืบทอดจาก        │
│ BaseSensor      │  │ BaseSensor      │
└─────────────────┘  └─────────────────┘
     คลาสลูก (Child Class)
```

**Syntax:**
```python
class BaseSensor:          # คลาสแม่ - เซ็นเซอร์ทั่วไป
    pass

class PHSensor(BaseSensor):    # คลาสลูก - สืบทอดจาก BaseSensor
    pass

class TempSensor(BaseSensor):  # คลาสลูก - สืบทอดจาก BaseSensor
    pass
```

---

### 2. Composition (การประกอบ)

**การเชื่อมโยงกับเคมี:**
- ปั๊ม "ประกอบด้วย" มอเตอร์และตัวควบคุม PWM
- ระบบไทเทรต "ประกอบด้วย" หัววัด pH, ปั๊ม, และจอแสดงผล

```
┌─────────────────────────────────────────────┐
│                   Pump                      │
│           (คลาสปั๊ม)                         │
│  ┌───────────────────────────────────────┐  │
│  │                                       │  │
│  │    ┌─────────────────────────┐        │  │
│  │    │    PWMController        │        │  │
│  │    │  (ตัวควบคุม PWM)         │        │  │
│  │    │                         │        │  │
│  │    │  - set_duty()           │        │  │
│  │    │  - get_duty()           │        │  │
│  │    └─────────────────────────┘        │  │
│  │                                       │  │
│  │    Pump "has-a" PWMController         │  │
│  │    ปั๊ม "มี" ตัวควบคุม PWM              │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Syntax:**
```python
class Pump:
    def __init__(self):
        self._pwm_controller = PWMController()  # Composition: Pump มี PWMController
```

---

### 3. @property Decorator

**การเชื่อมโยงกับเคมี:**
- ค่า slope ของการสอบเทียบ - อ่านได้ แต่ควรเปลี่ยนผ่านกระบวนการสอบเทียบเท่านั้น
- ค่า R-squared - อ่านได้อย่างเดียว เกิดจากการคำนวณ

```
┌───────────────────────────────────────────────────────────┐
│                      pHSensor                             │
├───────────────────────────────────────────────────────────┤
│  Private Attributes (ตัวแปรภายใน):                         │
│  - _slope = -5.79  (pH/V, จาก calibration)               │
│  - _intercept = 16.77                                     │
├───────────────────────────────────────────────────────────┤
│  @property (อ่านค่าได้):                                   │
│  + slope --> return self._slope                           │
│                                                           │
│  @slope.setter (กำหนดค่าได้พร้อม validation):              │
│  + slope = value --> validate แล้วค่อย set               │
│                      ถ้าไม่ valid จะ raise error          │
└───────────────────────────────────────────────────────────┘
```

**Syntax:**
```python
@property
def slope(self):
    return self._slope

@slope.setter
def slope(self, value):
    if -100 < value < 0:
        self._slope = value
    else:
        raise ValueError("Slope must be between -100 and 0")
```

---

## ไฟล์ในโฟลเดอร์ (Files in This Folder)

| ไฟล์ | คำอธิบาย | OOP Concept | เวลา |
|------|----------|-------------|:----:|
| `01_inheritance_sensors.py` | Inheritance: BaseSensor -> PHSensor, TempSensor | Inheritance | 30 นาที |
| `02_composition_pump.py` | Composition: Pump มี PWMController | Composition | 20 นาที |
| `03_property_decorator.py` | @property และ Encapsulation | Property | 10 นาที |
| `04_combined_demo.py` | รวม concepts ทั้งหมด | Combined | 15 นาที |
| `05_class_static_methods.py` | @classmethod และ @staticmethod | Advanced | เสริม |

---

## รายละเอียดไฟล์ (File Details)

### 01_inheritance_sensors.py

**วัตถุประสงค์:** เรียนรู้พื้นฐาน Inheritance สำหรับระบบเซ็นเซอร์

**สิ่งที่เรียนรู้:**
- การสร้าง Parent Class (BaseSensor)
- การสร้าง Child Class (PHSensor, TempSensor)
- การใช้ `super().__init__()` เรียก parent constructor
- Method Overriding

**การเปรียบเทียบกับเคมี:**

| OOP Concept | Chemistry Analogy |
|-------------|-------------------|
| BaseSensor | Sensor ทั่วไป (เหมือนกรด) |
| PHSensor | เซ็นเซอร์ pH (เหมือนกรดแก่) |
| TempSensor | เซ็นเซอร์อุณหภูมิ (เหมือนกรดอ่อน) |
| Inheritance | "is-a" relationship |

**Syntax สำคัญ:**

```python
class PHSensor(BaseSensor):        # สืบทอดจาก BaseSensor
    def __init__(self, pin=25):
        super().__init__(pin, "pH Sensor")  # เรียก constructor ของคลาสแม่
        self._slope = -5.7901               # เพิ่ม attribute เฉพาะ
```

---

### 02_composition_pump.py

**วัตถุประสงค์:** เรียนรู้ Composition สำหรับระบบปั๊ม

**สิ่งที่เรียนรู้:**
- ความแตกต่างระหว่าง Inheritance และ Composition
- การใช้ "has-a" relationship
- การห่อหุ้ม (wrap) object อื่นภายใน class

**เมื่อใช้ Inheritance vs Composition:**

| ใช้ Inheritance เมื่อ | ใช้ Composition เมื่อ |
|---------------------|---------------------|
| "is-a" relationship | "has-a" relationship |
| PHSensor **เป็น** Sensor | Pump **มี** PWMController |
| ต้องการ override methods | ต้องการ delegate งาน |

**Syntax สำคัญ:**

```python
class Pump:
    def __init__(self, pin=21):
        self._pwm = PWMController(pin)  # Composition: Pump มี PWMController

    def start(self):
        self._pwm.set_duty(1023)  # ใช้งานผ่าน PWMController
```

---

### 03_property_decorator.py

**วัตถุประสงค์:** เรียนรู้ @property สำหรับ Encapsulation

**สิ่งที่เรียนรู้:**
- การใช้ @property สร้าง getter
- การใช้ @property.setter สร้าง setter พร้อม validation
- การป้องกันการแก้ไขค่าโดยตรง (Encapsulation)

**ประโยชน์:**
- ป้องกันค่าที่ไม่ถูกต้อง (validation)
- เปลี่ยน implementation ภายในได้โดยไม่กระทบ user code
- สร้าง read-only attributes ได้

**Syntax สำคัญ:**

```python
class PHSensor:
    def __init__(self):
        self._slope = -5.79  # pH/V จาก calibration (private attribute)

    @property
    def slope(self):
        """Getter - อ่านค่า slope"""
        return self._slope

    @slope.setter
    def slope(self, value):
        """Setter - กำหนดค่าพร้อม validation"""
        if -25 < value < 0:  # ช่วงที่เป็นไปได้สำหรับ pH/V
            self._slope = value
        else:
            raise ValueError("Slope must be between -25 and 0 (pH/V)")
```

---

### 04_combined_demo.py

**วัตถุประสงค์:** รวม concepts ทั้งหมดในตัวอย่างจริง

**สิ่งที่เรียนรู้:**
- การใช้ Inheritance, Composition, และ @property ร่วมกัน
- การออกแบบระบบที่ซับซ้อน
- ตัวอย่างที่เกี่ยวข้องกับ TitraLab จริง

---

### 05_class_static_methods.py

**วัตถุประสงค์:** เรียนรู้ @classmethod และ @staticmethod (เนื้อหาเสริม)

**สิ่งที่เรียนรู้:**
- @staticmethod - method ที่ไม่ต้องการ instance
- @classmethod - method ที่ทำงานกับ class เอง
- Factory pattern

**หมายเหตุ:** เนื้อหาเสริมสำหรับนิสิตที่สนใจ

---

## ตารางสรุปแนวคิด OOP

| แนวคิด | Syntax | เปรียบเทียบเคมี | ตัวอย่าง |
|--------|--------|-----------------|----------|
| **Inheritance** | `class Child(Parent):` | pH electrode เป็นประเภทของ electrode | PHSensor(BaseSensor) |
| **super()** | `super().__init__()` | เรียกขั้นตอนมาตรฐานก่อน | เรียก constructor คลาสแม่ |
| **Override** | กำหนด method ชื่อเดียวกัน | ปรับขั้นตอนให้เฉพาะเจาะจง | read_raw() |
| **Composition** | Object มี object อื่น | ปั๊มมีมอเตอร์และ controller | Pump มี PWMController |
| **@property** | Getter/Setter | อ่านค่า slope แต่ป้องกันการแก้ไขโดยตรง | slope property |
| **Encapsulation** | `_private_attribute` | ข้อมูล calibration ภายใน | _slope, _intercept |

---

## แบบฝึกหัดเสริม (Additional Exercises)

ดูที่โฟลเดอร์ `../exercises/`:

| ไฟล์ | คำอธิบาย | Concept |
|------|----------|---------|
| `exercise_01_inheritance_starter.py` | แบบฝึกหัด Inheritance (โจทย์) | Inheritance |
| `exercise_01_inheritance_solution.py` | แบบฝึกหัด Inheritance (เฉลย) | Inheritance |
| `exercise_02_property_starter.py` | แบบฝึกหัด @property (โจทย์) | Property |
| `exercise_02_property_solution.py` | แบบฝึกหัด @property (เฉลย) | Property |
| `exercise_03_composition_starter.py` | แบบฝึกหัด Composition (โจทย์) | Composition |
| `exercise_03_composition_solution.py` | แบบฝึกหัด Composition (เฉลย) | Composition |

### ลำดับการทำแบบฝึกหัด

```
exercise_01_inheritance  -->  exercise_02_property  -->  exercise_03_composition
      (30 นาที)                   (20 นาที)                   (20 นาที)
```

---

## การเชื่อมต่อกับ Week 3 (Connection to Week 3)

OOP concepts จาก Week 2 จะถูกนำไปใช้ใน Week 3:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Week 2 --> Week 3                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Week 2 Concepts              Week 3 Applications                       │
│  ───────────────              ────────────────────                       │
│                                                                         │
│  BaseSensor inheritance  -->  BaseMode สำหรับ mode ต่างๆ                │
│                               (CalibrationMode, TitrationMode)          │
│                                                                         │
│  Pump composition       -->  TitrationSystem ที่รวมทุกอุปกรณ์            │
│                               (pHSensor + Pump + Display)               │
│                                                                         │
│  @property              -->  Calibration data และ system state          │
│                               (read-only ค่าสอบเทียบ)                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

| Week 2 Concept | Week 3 Application |
|----------------|-------------------|
| BaseSensor inheritance | ขยายเป็น BaseMode สำหรับ mode ต่างๆ |
| Pump composition | ขยายเป็น TitrationSystem ที่รวมทุกอุปกรณ์ |
| @property | ใช้กับ calibration data และ system state |

---

## สรุป (Summary)

หลังจบ Week 2:

| สิ่งที่ได้ | ไฟล์/ความรู้ |
|----------|-------------|
| ค่าสอบเทียบ pH | `data_calibrate.txt` (slope, intercept, R-squared) |
| ค่า Flow Rate | `data_flowrate.txt` (mL/s) |
| OOP: Inheritance | สร้าง child class ได้ |
| OOP: Composition | ใช้ "has-a" relationship |
| OOP: @property | สร้าง getter/setter พร้อม validation |

**พร้อมสำหรับ Week 3:** นำค่าสอบเทียบและ OOP concepts ไปสร้างระบบไทเทรตอัตโนมัติ

---

*สร้างเมื่อ: มกราคม 2026*

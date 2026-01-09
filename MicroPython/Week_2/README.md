# TitraLab Week 2: pH and Pump Calibration
# TitraLab สัปดาห์ที่ 2: การสอบเทียบเซ็นเซอร์ pH และปั๊ม

---

> **รายวิชา:** 2302311 Integrated Chemistry Laboratory I
> **ภาควิชา:** เคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย
> **Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## วัตถุประสงค์หลัก (Primary Objectives)

หลังจากเรียนจบบทเรียนนี้ นิสิตจะสามารถ:

### วัตถุประสงค์ด้านเคมีวิเคราะห์ (Analytical Chemistry Objectives)

1. **เข้าใจสมการ Nernst และการสอบเทียบ pH**
   - อธิบายสมการ Nernst: E = E0 - (2.303RT/nF) x pH
   - เข้าใจว่าความชันทฤษฎีที่ 25C คือ -59.16 mV/pH
   - ทำการสอบเทียบ 3 จุดด้วยสารละลายกันชนมาตรฐาน (pH 4, 7, 10)

2. **คำนวณและประเมินคุณภาพการสอบเทียบ**
   - คำนวณสมการถดถอยเชิงเส้น (Linear Regression): E = m x pH + b
   - ประเมินค่า R-squared (ค่าที่ดีต้อง >= 0.99)
   - คำนวณ Nernst Slope Efficiency (ค่าที่ดีต้องอยู่ในช่วง 95-105%)

3. **สอบเทียบอัตราการไหลของปั๊ม**
   - คำนวณ flow rate จากปริมาตรและเวลา: flow_rate = volume / time
   - ประเมินความสม่ำเสมอด้วย %RSD (ค่าที่ดีต้อง < 5%)
   - เข้าใจผลกระทบของ flow rate ที่ไม่แม่นยำต่อการไทเทรต

### วัตถุประสงค์ด้านทักษะโปรแกรม (Supporting Programming Objectives)

4. **ใช้ OOP จัดระเบียบโค้ดสำหรับการสอบเทียบ**
   - ใช้ Inheritance สำหรับเซ็นเซอร์ (BaseSensor -> pHSensor, TempSensor)
   - ใช้ Composition สำหรับตัวกระตุ้น (Pump มี PWMController)
   - ใช้ @property สำหรับการห่อหุ้มข้อมูลสอบเทียบ

---

## หลักการทางเคมี (Chemistry Principles)

### สมการ Nernst (Nernst Equation)

หัววัด pH ให้สัญญาณแรงดันไฟฟ้าตามสมการ Nernst:

```
E = E0 - (2.303RT/nF) x pH
```

จัดรูปใหม่เป็นสมการเส้นตรง:

```
E (mV) = m x pH + b
```

โดย:
- **m (slope)** = ความชัน (mV/pH)
  - ค่าทฤษฎีที่ 20C = -58.17 mV/pH
  - ค่าทฤษฎีที่ 25C = -59.16 mV/pH (ค่ามาตรฐาน)
  - ค่าทฤษฎีที่ 30C = -60.15 mV/pH
- **b (intercept)** = ศักย์ไฟฟ้าที่ pH = 0 (mV)

### ทำไมต้องสอบเทียบ 3 จุด?

| สารละลายกันชน | ค่า pH | ความสำคัญ |
|:-------------:|:------:|-----------|
| Potassium hydrogen phthalate | 4.00 | ตัวแทนช่วงกรด |
| Phosphate buffer | 7.00 | จุด isopotential (ไม่ขึ้นกับอุณหภูมิ) |
| Carbonate-bicarbonate buffer | 10.00 | ตัวแทนช่วงเบส |

### เกณฑ์คุณภาพการสอบเทียบ

| ตัวชี้วัด | ดีเยี่ยม | พอใช้ได้ | ต้องสอบเทียบใหม่ |
|----------|:--------:|:--------:|:---------------:|
| R-squared | >= 0.999 | >= 0.99 | < 0.99 |
| Slope Efficiency | 95-105% | 90-110% | < 90% หรือ > 110% |
| %RSD (flow rate) | < 2% | < 5% | >= 5% |

---

## ตารางเวลาการสอน 3 ชั่วโมง (3-Hour Teaching Schedule)

| ช่วงเวลา | หัวข้อ | ไฟล์ | เวลา |
|:--------:|--------|------|:----:|
| **ชั่วโมงที่ 1** | **การสอบเทียบเซ็นเซอร์ pH** | | **60 นาที** |
| 0:00-0:15 | ทฤษฎี: สมการ Nernst และหลักการสอบเทียบ | - | 15 นาที |
| 0:15-0:55 | ปฏิบัติ: สอบเทียบ 3 จุดด้วย pH 4, 7, 10 | `pH/02_calibration.py` | 40 นาที |
| 0:55-1:00 | อภิปราย: วิเคราะห์ R-squared และ Slope Efficiency | - | 5 นาที |
| **ชั่วโมงที่ 2** | **การสอบเทียบปั๊ม** | | **45 นาที** |
| 1:00-1:15 | ทฤษฎี: PWM และผลต่ออัตราการไหล | - | 15 นาที |
| 1:15-1:35 | ปฏิบัติ: วัด flow rate 3-5 ครั้ง | `Pump/01_flowRate.py` | 20 นาที |
| 1:35-1:45 | ปฏิบัติ: ตรวจสอบความแม่นยำ | `Pump/pumpValidate_1.py` | 10 นาที |
| **ชั่วโมงที่ 3** | **OOP สำหรับระบบไทเทรต** | | **60 นาที** |
| 1:45-2:15 | Inheritance: BaseSensor -> pHSensor | `core/01_inheritance_basics.py` | 30 นาที |
| 2:15-2:35 | Composition: Pump มี PWMController | `core/02_composition_basics.py` | 20 นาที |
| 2:35-2:45 | @property สำหรับข้อมูลสอบเทียบ | `core/03_property_decorator.py` | 10 นาที |
| **แบบฝึกหัด** | **รวมความรู้** | | **15 นาที** |
| 2:45-3:00 | รวม concepts และสรุป | `core/04_combined_demo.py` | 15 นาที |

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

```
Week_2/
├── pH/                         # [สำคัญ] การวัดและสอบเทียบ pH
│   ├── 01_pH.py                # การวัดค่า pH แบบต่อเนื่อง
│   └── 02_calibration.py       # *** การสอบเทียบ pH 3 จุด ***
│
├── Pump/                       # [สำคัญ] การควบคุมและสอบเทียบปั๊ม
│   ├── 01_flowRate.py          # *** การสอบเทียบ flow rate ***
│   ├── pumpValidate_1.py       # การตรวจสอบ: ปั๊มต่อเนื่อง
│   └── pumpValidate_2.py       # การตรวจสอบ: ปั๊มเป็นช่วง
│
├── core/                       # [บทเรียน OOP] ไฟล์สำหรับสอนในห้องเรียน
│   ├── 01_inheritance_basics.py    # Inheritance พื้นฐาน
│   ├── 02_composition_basics.py    # Composition พื้นฐาน
│   ├── 03_property_decorator.py    # @property และ Encapsulation
│   └── 04_combined_demo.py         # รวม concepts
│
├── lib/                        # [ห้องสมุดคลาส] OOP classes สำหรับอ้างอิง
│   ├── base_sensor.py          # Abstract Base Class สำหรับเซ็นเซอร์
│   ├── ph_sensor.py            # คลาส pHSensor สืบทอดจาก BaseSensor
│   ├── temp_sensor.py          # คลาส TempSensor สืบทอดจาก BaseSensor
│   ├── pump.py                 # คลาส Pump ใช้ Composition
│   └── buzzer.py               # คลาส Buzzer ใช้ PWM
│
├── exercises/                  # [แบบฝึกหัด] สำหรับนิสิตทำเอง
│   ├── exercise_01_inheritance_starter.py
│   ├── exercise_01_inheritance_solution.py
│   ├── exercise_02_property_starter.py
│   ├── exercise_02_property_solution.py
│   ├── exercise_03_composition_starter.py
│   └── exercise_03_composition_solution.py
│
├── 01_sensor_inheritance.py    # [สาธิต] Inheritance demo
├── 02_composition_demo.py      # [สาธิต] Composition demo
├── 03_properties_demo.py       # [สาธิต] @property demo
│
└── Old/                        # [อ้างอิง] Legacy code
    ├── cal_flowrate.py
    └── cal_pH.py
```

---

## เคล็ดลับการปฏิบัติ (Practical Tips)

### การสอบเทียบ pH

1. **การเตรียมสารละลายกันชน**
   - ใช้สารละลายกันชนมาตรฐานที่ยังไม่หมดอายุ
   - เก็บรักษาในภาชนะที่ปิดสนิท ห่างจากความร้อนและแสง
   - ตรวจสอบอุณหภูมิของสารละลายกันชน (ค่า pH เปลี่ยนตามอุณหภูมิ)

2. **การล้างหัววัด**
   - ล้างด้วยน้ำกลั่น (deionized water) ระหว่างเปลี่ยนสารละลายกันชน
   - ซับน้ำเบาๆ ด้วยกระดาษทิชชู่ ห้ามถูแรง
   - ไม่ควรปล่อยให้หัววัดแห้ง

3. **เวลารอให้ค่าเสถียร (Stabilization Time)**
   - รอ 30-60 วินาทีหลังจากแช่หัววัดในสารละลายกันชน
   - สังเกตค่าแรงดันไฟฟ้า (mV) ที่แสดงบนจอ
   - ค่าควรหยุดเปลี่ยนแปลงหรือเปลี่ยนช้ามาก (< 1 mV/นาที) ก่อนกดบันทึก

4. **การแก้ไขเมื่อ R-squared < 0.99**
   - ตรวจสอบสารละลายกันชน (อาจเสื่อมสภาพ)
   - ทำความสะอาดหัววัด pH
   - ตรวจสอบการเชื่อมต่อสายสัญญาณ
   - รอให้ค่าเสถียรนานขึ้น

### การสอบเทียบปั๊ม

1. **การเตรียมอุปกรณ์**
   - ใช้กระบอกตวงที่มีความละเอียด 0.1 mL หรือดีกว่า
   - ตรวจสอบว่าท่อปั๊มไม่มีฟองอากาศ (purge ก่อนสอบเทียบ)
   - วางกระบอกตวงให้ตั้งตรง

2. **การวัด Flow Rate**
   - ทำซ้ำ 3-5 ครั้งเพื่อหาค่าเฉลี่ย
   - ปั๊มครั้งละ 10-20 วินาทีเพื่อให้ได้ปริมาตรที่วัดง่าย
   - อ่านกระบอกตวงที่ระดับสายตา (meniscus)

3. **เกณฑ์ยอมรับ %RSD**
   - %RSD < 5% = ใช้งานได้
   - %RSD >= 5% = ตรวจสอบปั๊มและท่อ

4. **การตรวจสอบความแม่นยำ (Validation)**
   - หลังสอบเทียบ ให้รัน `pumpValidate_1.py` เพื่อปั๊มปริมาตรที่กำหนด
   - เปรียบเทียบปริมาตรที่วัดได้กับค่าที่คำนวณ
   - % error < 5% ถือว่าผ่าน

---

## ไฟล์สอบเทียบหลัก (Key Calibration Files)

### 1. การสอบเทียบ pH: `pH/02_calibration.py`

**วัตถุประสงค์:** สอบเทียบหัววัด pH ด้วยสารละลายกันชนมาตรฐาน 3 จุด

**ขั้นตอนการทำงาน:**
1. แช่หัววัดในสารละลายกันชน pH 4.00 -> รอค่าเสถียร -> กดปุ่มบันทึก
2. แช่หัววัดในสารละลายกันชน pH 7.00 -> รอค่าเสถียร -> กดปุ่มบันทึก
3. แช่หัววัดในสารละลายกันชน pH 10.00 -> รอค่าเสถียร -> กดปุ่มบันทึก
4. โปรแกรมคำนวณ Linear Regression และแสดงผล

**ผลลัพธ์:**
- ไฟล์ `data_calibrate.txt`: slope, intercept, R-squared, อุณหภูมิ
- ไฟล์ `calibration_log.txt`: รายละเอียดการสอบเทียบ

**โค้ดสำคัญ - การคำนวณ Linear Regression:**

```python
def linear_regression(x_values, y_values):
    """
    คำนวณการถดถอยเชิงเส้น y = mx + b พร้อมค่า R-squared
    สำหรับเซ็นเซอร์ pH: E(mV) = m * pH + b
    """
    n = len(x_values)

    # คำนวณค่าที่ต้องใช้ (Calculate required sums)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x ** 2 for x in x_values)

    # คำนวณความชัน (Calculate slope)
    denominator = n * sum_x2 - sum_x ** 2
    slope = (n * sum_xy - sum_x * sum_y) / denominator

    # คำนวณจุดตัดแกน y (Calculate intercept)
    intercept = (sum_y - slope * sum_x) / n

    # คำนวณ R-squared
    y_mean = sum_y / n
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)
    ss_res = sum((y - (slope * x + intercept)) ** 2
                 for x, y in zip(x_values, y_values))
    r_squared = 1 - (ss_res / ss_tot)

    return slope, intercept, r_squared
```

---

### 2. การสอบเทียบ Flow Rate: `Pump/01_flowRate.py`

**วัตถุประสงค์:** หาอัตราการไหลที่แท้จริงของปั๊ม

**ขั้นตอนการทำงาน:**
1. กดปุ่ม 1 เริ่มปั๊ม (จับเวลาอัตโนมัติ)
2. ปั๊มน้ำลงกระบอกตวงประมาณ 10-20 วินาที
3. กดปุ่ม 1 หยุดปั๊ม
4. อ่านปริมาตรจากกระบอกตวง -> แก้ไข `MEASURED_VOLUME` ในโค้ด
5. กดปุ่ม 2 บันทึกผลการวัด (ทำซ้ำ 3-5 ครั้ง)
6. กดปุ่ม 3 บันทึกค่า flow rate ลงไฟล์

**ผลลัพธ์:**
- ไฟล์ `data_flowrate.txt`: ค่า flow rate เฉลี่ย (mL/s)

**โค้ดสำคัญ - การคำนวณ Flow Rate:**

```python
def record_measurement():
    """
    บันทึกผลการวัดและคำนวณ flow rate
    สูตร: flow_rate = volume / time (mL/s)
    """
    global calibration_data, current_volume

    # ใช้ค่าจากตัวแปร MEASURED_VOLUME
    current_volume = MEASURED_VOLUME

    # คำนวณ flow rate
    flow_rate = current_volume / elapsed_time

    # บันทึกข้อมูล
    calibration_data.append((elapsed_time, current_volume, flow_rate))

    # แสดงค่าเฉลี่ยและ RSD
    if len(calibration_data) >= 2:
        avg_flow_rate = sum(d[2] for d in calibration_data) / len(calibration_data)
        variance = sum((d[2] - avg_flow_rate) ** 2 for d in calibration_data) / len(calibration_data)
        std_dev = variance ** 0.5
        rsd = (std_dev / avg_flow_rate) * 100  # %RSD

        if rsd > 5:
            print("*** คำเตือน: RSD > 5% - ค่าไม่สม่ำเสมอ ***")
```

---

### 3. การตรวจสอบความแม่นยำ: `Pump/pumpValidate_1.py` และ `pumpValidate_2.py`

**pumpValidate_1.py** - ปั๊มต่อเนื่อง:
- ปั๊มน้ำจนถึงปริมาตรเป้าหมาย (เช่น 5 mL) แบบต่อเนื่อง
- ใช้ในช่วงเริ่มต้นการไทเทรต (pH ยังห่างจากจุดสมมูล)

**pumpValidate_2.py** - ปั๊มเป็นช่วง:
- ปั๊ม -> หยุด -> (อ่าน pH) -> ปั๊ม -> ...
- ใช้ในช่วงใกล้จุดสมมูล (equivalence point)
- รอให้ pH stabilize ก่อนปั๊มครั้งถัดไป

---

## GPIO Pin Reference / ตารางอ้างอิงขา GPIO

ตารางนี้ตรงกับ `MicroPython/Week_1/pins.py`:

### ขา GPIO ที่ใช้ใน Week 2

| อุปกรณ์ | GPIO | ค่าคงที่ใน pins.py | ประเภท | หมายเหตุ |
|---------|:----:|-------------------|--------|----------|
| **Sensors (เซ็นเซอร์)** |
| pH Sensor | 25 | `PH_PIN` | ADC Input | อ่านแรงดัน 0-3.3V จากหัววัด pH |
| Temperature (DS18B20) | 16 | `DS18B20_PIN` | OneWire | ต้องใช้ pull-up resistor 4.7K |
| **Actuators (ตัวกระตุ้น)** |
| Pump | 21 | `PUMP_PIN` | PWM Output | ความถี่ 1000 Hz, 10-bit duty (0-1023) |
| Buzzer | 26 | `BUZZER_PIN` | PWM Output | สำหรับ feedback เสียง |
| **LEDs** |
| Red LED | 2 | `LED_RED` | Output | แสดงสถานะ error / ปั๊มทำงาน |
| Green LED | 4 | `LED_GREEN` | Output | แสดงสถานะ OK / เสร็จสิ้น |
| **Buttons (ปุ่มกด)** |
| Button 1 | 34 | `BUTTON1` | Input-only | ต้องใช้ external pull-down 10K |
| Button 2 | 35 | `BUTTON2` | Input-only | ต้องใช้ external pull-down 10K |
| Button 3 | 39 | `BUTTON3` | Input-only | ต้องใช้ external pull-down 10K |

### ข้อควรระวัง GPIO34/35/39

```python
# GPIO34, 35, 39 เป็น Input-Only Pins
# ไม่รองรับ internal pull-up/pull-down resistor
# ต้องใช้ external pull-down resistor (10K ohm)

button_1 = Pin(34, Pin.IN)  # ถูกต้อง
button_1 = Pin(34, Pin.IN, Pin.PULL_DOWN)  # ผิด! ไม่รองรับ
```

---

## ทักษะ OOP สนับสนุน (Supporting OOP Skills)

### 1. Inheritance/การสืบทอด

**แนวคิดทางเคมี:**
- หัววัด pH (pH electrode) เป็น **ประเภทหนึ่งของ** electrode ทั่วไป
- หัววัดอุณหภูมิ (Temperature sensor) เป็น **ประเภทหนึ่งของ** sensor ทั่วไป

**Syntax:**
```python
class pHSensor(BaseSensor):
    def __init__(self, pin=25, slope=-5.7901, intercept=16.769):
        # เรียก constructor ของคลาสแม่
        super().__init__(pin, "pH Sensor")

        # เพิ่ม attributes เฉพาะของ pHSensor
        self._slope = slope
        self._intercept = intercept
```

---

### 2. Composition/การประกอบ

**แนวคิดทางเคมี:**
- ปั๊มไทแทรนต์ **ประกอบด้วย** มอเตอร์และตัวควบคุม PWM
- ระบบไทเทรต **ประกอบด้วย** หัววัด pH, ปั๊ม, และจอแสดงผล

**Syntax:**
```python
class Pump:
    def __init__(self, pin=21, flow_rate=0.2772):
        # Composition: Pump มี PWMController
        self._pwm_controller = PWMController(pin)
        self._flow_rate = flow_rate
```

---

### 3. @property Decorator

**แนวคิดทางเคมี:**
- ค่า slope ของการสอบเทียบ - อ่านได้ แต่ควรเปลี่ยนผ่านกระบวนการสอบเทียบเท่านั้น
- ค่า R-squared - อ่านได้อย่างเดียว เกิดจากการคำนวณ

**Syntax:**
```python
class pHSensor:
    @property
    def slope(self):
        """Getter - อ่านค่า slope"""
        return self._slope

    @slope.setter
    def slope(self, value):
        """Setter - กำหนดค่า slope พร้อม validation"""
        if -100 < value < 0:
            self._slope = value
        else:
            raise ValueError("Slope must be between -100 and 0")
```

---

## ผลลัพธ์การเรียนรู้ (Learning Outcomes)

ใช้ checkbox ด้านล่างเพื่อติดตามความก้าวหน้า:

### การสอบเทียบ pH (pH Calibration) - 60 นาที
- [ ] เข้าใจสมการ Nernst และความสัมพันธ์ระหว่าง mV กับ pH
- [ ] ทำการสอบเทียบ 3 จุดด้วยสารละลายกันชน pH 4, 7, 10 สำเร็จ
- [ ] ได้ค่า R-squared >= 0.99
- [ ] เข้าใจความหมายของ Nernst Slope Efficiency
- [ ] บันทึกค่าสอบเทียบลงไฟล์ได้

### การสอบเทียบปั๊ม (Pump Calibration) - 45 นาที
- [ ] เข้าใจความสำคัญของ flow rate ที่แม่นยำต่อการไทเทรต
- [ ] คำนวณ flow rate จากปริมาตรและเวลาได้
- [ ] ได้ค่า %RSD < 5%
- [ ] ตรวจสอบความแม่นยำด้วย pumpValidate สำเร็จ

### ทักษะ OOP (OOP Skills) - 60 นาที
- [ ] สร้าง child class ที่สืบทอดจาก parent class ได้
- [ ] ใช้ `super().__init__()` ได้ถูกต้อง
- [ ] สร้างคลาสที่ใช้ Composition ได้
- [ ] ใช้ @property สำหรับ getter และ setter ได้

---

## ความรู้พื้นฐาน (Prerequisites)

### ความรู้ทางเคมี (Chemistry Knowledge)
- หลักการไทเทรตกรด-เบส (Acid-base titration)
- สมการ Nernst: E = E0 - (2.303RT/nF) x pH
- การใช้สารละลายกันชนมาตรฐาน (Standard buffer solutions)
- ความหมายของจุดสมมูล (Equivalence point) และจุดยุติ (Endpoint)

### ความรู้จาก Week 1 (Week 1 Knowledge)
- Python พื้นฐาน: Variables/ตัวแปร, Functions/ฟังก์ชัน, Loops/ลูป
- การสร้าง Class และ Object เบื้องต้น
- การทำงานกับ GPIO, ADC, PWM บน ESP32
- การอ่าน/เขียนไฟล์

---

## การเชื่อมต่อกับ Week 3 (Connection to Week 3)

Week 3 นำค่าสอบเทียบจาก Week 2 มาใช้ในระบบไทเทรตอัตโนมัติ:

| Week 2 | Week 3 |
|--------|--------|
| ค่า slope, intercept จาก `data_calibrate.txt` | ใช้ใน pHSensor class เพื่อแปลง mV เป็น pH |
| ค่า flow_rate จาก `data_flowrate.txt` | ใช้ใน Pump class เพื่อคำนวณปริมาตร |
| Inheritance concept | ขยายเป็น BaseMode สำหรับ mode ต่างๆ |
| Composition concept | ขยายเป็น TitrationSystem ที่รวมทุกอุปกรณ์ |

---

## ตารางสรุปแนวคิด OOP

| แนวคิด | Syntax | เปรียบเทียบเคมี | ตัวอย่างใน Week 2 |
|--------|--------|-----------------|-------------------|
| **Inheritance** | `class Child(Parent):` | pH electrode เป็นประเภทของ electrode | pHSensor(BaseSensor) |
| **super()** | `super().__init__()` | เรียกขั้นตอนมาตรฐานก่อน | เรียก constructor คลาสแม่ |
| **Override** | กำหนด method ชื่อเดียวกัน | ปรับขั้นตอนให้เฉพาะเจาะจง | read_raw() |
| **Composition** | Object มี object อื่น | ปั๊มมีมอเตอร์และ controller | Pump มี PWMController |
| **@property** | Getter/Setter | อ่านค่า slope แต่ป้องกันการแก้ไขโดยตรง | slope property |
| **Encapsulation** | `_private_attribute` | ข้อมูล calibration ภายใน | _slope, _intercept |

---

## อ้างอิง (References)

### เอกสารทางเคมี
- สมการ Nernst และการวัด pH
- วิธีการสอบเทียบ 3 จุด (3-point calibration methodology)
- หลักการไทเทรตและการหาจุดสมมูล

### เอกสาร MicroPython
- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 ADC Reference](https://docs.micropython.org/en/latest/esp32/quickref.html#adc-analog-to-digital-conversion)
- [ESP32 PWM Reference](https://docs.micropython.org/en/latest/esp32/quickref.html#pwm-pulse-width-modulation)

---

## ผู้พัฒนา (Developers)

- Hemmawan Saon
- Nuttakit Deemon
- Saowapak Vchirawongkwin
- Sumrit Wacharasindhu
- Viwat Vchirawongkwin

**รายวิชา:** 2302311 Integrated Chemistry Laboratory I
**สถาบัน:** ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย / Department of Chemistry, Faculty of Science, Chulalongkorn University

---

## เวอร์ชัน (Version)

**Version 2.0.0** - Week 2: pH and Pump Calibration

การเรียนรู้หลัก:
- การสอบเทียบเซ็นเซอร์ pH ด้วยสมการ Nernst และ Linear Regression
- การสอบเทียบอัตราการไหลของปั๊มและการตรวจสอบความแม่นยำ
- ทักษะ OOP (Inheritance, Composition, @property) เป็นเครื่องมือสนับสนุน

**เวลาที่ใช้ทั้งหมด:** ประมาณ 3 ชั่วโมง

---

*สร้างเมื่อ: มกราคม 2026*
*อัปเดตล่าสุด: มกราคม 2026*

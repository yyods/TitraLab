# Core Layer (Layer 2)
# ชั้น Core Logic

---

## ภาพรวม (Overview)

โฟลเดอร์ `core/` คือชั้นที่ 2 ของสถาปัตยกรรม TitraLab ทำหน้าที่จัดการ **logic ทางคณิตศาสตร์** และ **การประมวลผลข้อมูล** โดยไม่ขึ้นกับ hardware โดยตรง

The `core/` folder is Layer 2 of the TitraLab architecture. It handles **mathematical logic** and **data processing** without depending directly on hardware.

### หลักการสำคัญ (Key Principles)

1. **Hardware Independence/ไม่ขึ้นกับ Hardware**: Logic ใช้งานได้แม้ไม่มี hardware จริง
2. **Pure Functions/ฟังก์ชันบริสุทธิ์**: ผลลัพธ์ขึ้นกับ input เท่านั้น
3. **Reusability/ใช้ซ้ำได้**: นำไปใช้ในโปรเจกต์อื่นได้

---

## โครงสร้างไฟล์ (File Structure)

```
core/
├── __init__.py       # Package initialization
├── math_utils.py     # คณิตศาสตร์และสถิติ (Math & Statistics)
├── calibrator.py     # การสอบเทียบ pH และ flow rate
├── data_manager.py   # จัดการการบันทึก/โหลดข้อมูล
└── titration.py      # ควบคุมการไทเทรชันอัตโนมัติ
```

---

## คำอธิบายแต่ละไฟล์ (File Descriptions)

### math_utils.py - คลาสคณิตศาสตร์ (Math Utilities)

**หน้าที่**: ฟังก์ชันทางคณิตศาสตร์และสถิติสำหรับการสอบเทียบและวิเคราะห์ข้อมูล

**ความเชื่อมโยงกับเคมี**:
- Linear Regression ใช้สร้างสมการสอบเทียบ pH: `pH = slope_m * mV + intercept_b`
  - slope_m มีหน่วย pH/mV (ประมาณ -0.0169 ที่ 25 C)
  - intercept_b มีหน่วย pH (ประมาณ 34-36)
- R-squared ใช้ประเมินคุณภาพการสอบเทียบ (>= 0.99 ผ่านเกณฑ์)

#### คลาส LinearRegression

```python
# ตัวอย่างการใช้งาน (Usage Example)
from core.math_utils import LinearRegression

lr = LinearRegression()

# เพิ่มจุดข้อมูล (voltage, pH) จากการสอบเทียบ
lr.add_point(1.500, 4.00)   # Buffer pH 4.00
lr.add_point(2.000, 7.00)   # Buffer pH 7.00
lr.add_point(2.500, 10.00)  # Buffer pH 10.00

# คำนวณสมการ
lr.calculate()

print(f"สมการ: pH = {lr.slope:.6f} * mV + {lr.intercept:.4f}")
print(f"R-squared: {lr.r_squared:.6f}")

# ทำนายค่า
ph = lr.predict(2010.0)  # ทำนาย pH จากแรงดัน 2010 mV
```

#### ฟังก์ชัน Helper

```python
from core.math_utils import calculate_mean, calculate_std

# คำนวณค่าเฉลี่ย
mean_ph = calculate_mean([7.01, 7.02, 6.99, 7.00])  # = 7.005

# คำนวณส่วนเบี่ยงเบนมาตรฐาน
std_ph = calculate_std([7.01, 7.02, 6.99, 7.00])    # = 0.013
```

**Methods สำคัญ**:
| Method/Function | คำอธิบาย |
|-----------------|----------|
| `LinearRegression.add_point(x, y)` | เพิ่มจุดข้อมูล |
| `LinearRegression.calculate()` | คำนวณ slope, intercept, r_squared |
| `LinearRegression.predict(x)` | ทำนาย y จาก x |
| `calculate_mean(data)` | คำนวณค่าเฉลี่ย |
| `calculate_std(data)` | คำนวณส่วนเบี่ยงเบนมาตรฐาน |

---

### calibrator.py - คลาสการสอบเทียบ (Calibrator Class)

**หน้าที่**: จัดการการสอบเทียบเซ็นเซอร์ pH และอัตราการไหลของปั๊ม

**ความเชื่อมโยงกับเคมี**:
- **pH Calibration**: สร้างสมการ `pH = slope_m * mV + intercept_b` จากบัฟเฟอร์มาตรฐาน
  (direct-use form: slope_m in pH/mV, intercept_b in pH)
- **Flow Rate Calibration**: วัดอัตราการไหลจริงของปั๊ม (mL/s, ทศนิยม 4 ตำแหน่ง)

```python
# ตัวอย่างการใช้งาน (Usage Example)
from core.calibrator import Calibrator

# สร้าง Calibrator พร้อม dependencies
calibrator = Calibrator(
    ph_sensor=ph_sensor,
    pump=pump,
    display=display,
    buttons=buttons,
    buzzer=buzzer,
    data_manager=data_manager
)

# สอบเทียบ pH (3-point calibration)
result = calibrator.calibrate_ph()
# result = {'slope_m': -0.016911, 'intercept_b': 34.98, 'r_squared': 0.9995, 'is_valid': True}
# สมการ: pH = slope_m * mV + intercept_b (direct-use form)

# สอบเทียบอัตราการไหล
flow_result = calibrator.calibrate_flow_rate()
# flow_result = {'flow_rate': 0.2772, 'volume': 5.0, 'time': 18.05}
# หมายเหตุ: flow_rate ใช้ 4 ทศนิยม เพื่อความแม่นยำในการคำนวณปริมาตร

# ทดสอบ pH
calibrator.test_ph_sensor()

# ทดสอบ Flow Rate
calibrator.test_flow_rate()
```

**เกณฑ์การสอบเทียบ pH (pH Calibration Criteria)**:
| เกณฑ์ | ค่า | ความหมาย |
|-------|-----|----------|
| R-squared >= 0.99 | Excellent | ผ่านเกณฑ์สำหรับการสอบเทียบ pH |
| R-squared >= 0.95 | Acceptable | ยอมรับได้แต่ควรสอบเทียบใหม่ |
| R-squared < 0.95 | Fail | ต้องสอบเทียบใหม่ |

**ขั้นตอนการสอบเทียบ pH 3 จุด (3-Point pH Calibration)**:
```
1. แช่หัววัดในบัฟเฟอร์ pH 4.00  → วัดแรงดัน V1
2. แช่หัววัดในบัฟเฟอร์ pH 7.00  → วัดแรงดัน V2
3. แช่หัววัดในบัฟเฟอร์ pH 10.00 → วัดแรงดัน V3
4. คำนวณ Linear Regression → slope, intercept, R²
5. ตรวจสอบ R² >= 0.99
6. บันทึกค่าสอบเทียบ
```

---

### data_manager.py - คลาสจัดการข้อมูล (Data Manager Class)

**หน้าที่**: บันทึกและโหลดข้อมูลการสอบเทียบและการไทเทรต

**ไฟล์ที่จัดการ**:
- `data_calibrate.txt` - ค่าสอบเทียบ pH (CSV: slope_m,intercept_b,r_squared,cal_temp)
- `data_flowrate.txt` - อัตราการไหลของปั๊ม (ทศนิยม 4 ตำแหน่ง)
- `titration_data_R*.csv` - ข้อมูลการไทเทรต (บันทึกใน ESP32 flash)

**รูปแบบไฟล์ `data_calibrate.txt`:**
```
slope_m,intercept_b,r_squared,cal_temp
-0.016911,34.9800,0.999500,25.20
```

```python
# ตัวอย่างการใช้งาน (Usage Example)
from core.data_manager import DataManager

dm = DataManager()  # ใช้ ESP32 flash storage

# หมายเหตุ: main.py จะเรียก load_ph_calibration() และ load_flow_rate()
# อัตโนมัติตอนเริ่มโปรแกรม เพื่อนำค่าที่บันทึกไว้มาใช้งานทันที
# (main.py automatically loads saved calibration at startup)

# บันทึก/โหลด ค่าสอบเทียบ pH (direct-use form: pH = slope_m * mV + intercept_b)
dm.save_ph_calibration(slope_m=-0.016911, intercept_b=34.98, r_squared=0.9995, cal_temp=25.2)
slope_m, intercept_b, r_squared, cal_temp = dm.load_ph_calibration()

# บันทึก/โหลด อัตราการไหล (4 ทศนิยม)
dm.save_flow_rate(0.2772)
flow_rate = dm.load_flow_rate()

# บันทึกข้อมูลไทเทรต
dm.start_titration_log("titration_001.csv")
dm.log_titration_point(volume=1.0, ph=7.02, temp=25.1)
dm.end_titration_log()
```

---

### titration.py - คลาสควบคุมการไทเทรต (Titration Controller Class)

**หน้าที่**: ควบคุมการไทเทรตอัตโนมัติและตรวจจับจุดสมมูล

**อัลกอริทึม - Constant Dose Volume:**

ใช้ปริมาตรคงที่ **0.2 mL** ต่อ step ตลอดทั้งการไทเทรต (ปั๊มที่ 100% เสมอ):

```
สูบ 0.2 mL → หยุด → รอ 2 วินาที → อ่าน pH → ทำซ้ำ
```

**เหตุผลทางการเรียนรู้ (Pedagogical Rationale):**
- ทุกจุดบนกราฟห่างกัน 0.2 mL เท่ากัน ง่ายต่อการเข้าใจ
- นิสิตตรวจสอบได้: `total_volume = dose_count x 0.2 mL`
- เนื่องจาก dV คงที่ (0.2 mL) การหาจุดสมมูลเหลือเพียง "หา step ที่ |dpH| มากที่สุด"
- เหมือนการไทเทรตมือ: หยดสารไทแทรนต์ทีละหยดแบบสม่ำเสมอ

**ความเชื่อมโยงกับเคมี**:
- ตรวจจับจุดสมมูล (equivalence point) ด้วยวิธี derivative
- จุดสมมูลคือจุดที่ |dpH/dV| มีค่าสูงสุด
- เนื่องจาก dV = 0.2 mL คงที่ จึงเทียบเท่ากับหา |dpH| สูงสุด

```python
# ตัวอย่างการใช้งาน (Usage Example)
from core.titration import TitrationController

titration = TitrationController(
    pump=pump,
    ph_sensor=ph_sensor,
    temp_sensor=temp_sensor,
    display=display,
    buzzer=buzzer
)
# ข้อมูล CSV บันทึกใน ESP32 flash storage (ดาวน์โหลดผ่าน Thonny IDE)

# ตั้งค่าปริมาตรคงที่ 0.2 mL ต่อ step (Configure constant dose volume)
titration.configure(
    dose_volume=0.2,      # 0.2 mL ต่อ step (fixed)
    stabilize_time=2.0,   # รอ 2 วินาทีให้ pH เสถียร
    max_volume=50.0       # สูงสุด 50 mL = 250 doses
)

# เริ่มไทเทรตอัตโนมัติ (Start auto titration)
result = titration.run_titration()
# result = {
#     'equivalence_volume': 25.2,   # mL (= 126 doses x 0.2 mL)
#     'equivalence_ph': 7.02,
#     'total_volume': 25.4,
#     'data_points': [(0.0, 2.1), (0.2, 2.15), (0.4, 2.2), ...]
# }
```

**อัลกอริทึมหาจุดสมมูล (Equivalence Point Detection)**:
```python
# วิธี First Derivative (dpH/dV)
# เนื่องจาก dose volume คงที่ (0.2 mL) ทุก step:
#   dpH/dV = (pH[i] - pH[i-1]) / 0.2
#   ดังนั้น หาจุดที่ |pH[i] - pH[i-1]| มากที่สุดก็พอ
for i in range(1, len(data_points)):
    delta_v = 0.2  # คงที่ทุก step (constant dose volume)
    delta_ph = pH[i] - pH[i-1]
    derivative = delta_ph / delta_v

    if abs(derivative) > max_derivative:
        max_derivative = abs(derivative)
        equivalence_point = (volume[i], pH[i])
```

**ขั้นตอนการทำงาน (Operation Steps)**:

| ขั้นตอน | การทำงาน | รายละเอียด |
|:-------:|----------|------------|
| 1 | สูบ (Pump) | เปิดปั๊ม 100% เติม 0.2 mL แล้วหยุด |
| 2 | รอ (Wait) | รอ 2 วินาทีให้ pH เสถียร |
| 3 | วัด (Read) | อ่านค่า pH และอุณหภูมิ |
| 4 | บันทึก (Log) | บันทึกข้อมูลลง CSV |
| 5 | ตรวจสอบ (Check) | ตรวจจับจุดสมมูล (dpH/dV สูงสุด) |
| 6 | ทำซ้ำ (Repeat) | กลับขั้นตอน 1 จนจบ |

**Safety Limits**:
- ปริมาตรสูงสุด: 50 mL (= 250 doses x 0.2 mL)
- เวลาสูงสุด: 10 นาที

---

## ความสัมพันธ์ระหว่างคลาส (Class Relationships)

```
┌─────────────────────────────────────────────────────────────────┐
│                          Calibrator                              │
│  - จัดการการสอบเทียบ pH และ flow rate                           │
│  - ใช้ LinearRegression สำหรับคำนวณสมการ                        │
│  - ใช้ DataManager สำหรับบันทึก/โหลดค่า                         │
└─────────────────────────────────────────────────────────────────┘
                │                              │
                ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────────────┐
│    LinearRegression     │    │         DataManager              │
│  - slope, intercept     │    │  - save/load calibration        │
│  - r_squared            │    │  - log titration data           │
│  - predict()            │    │  - file I/O                     │
└─────────────────────────┘    └─────────────────────────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────────┐
                               │     TitrationController         │
                               │  - run_titration()              │
                               │  - detect_equivalence_point()   │
                               │  - ใช้ DataManager สำหรับ log   │
                               └─────────────────────────────────┘
```

---

## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

หลังจากศึกษาโฟลเดอร์นี้ นักศึกษาจะสามารถ:

1. **เข้าใจ Linear Regression**: คำนวณ slope, intercept, R-squared
2. **ประยุกต์ใช้สถิติกับเคมี**: ประเมินคุณภาพการสอบเทียบด้วย R-squared
3. **ออกแบบ Algorithm**: ตรวจจับจุดสมมูลด้วยวิธี derivative
4. **จัดการ Data Persistence**: บันทึก/โหลดข้อมูลจากไฟล์

---

## ลำดับการศึกษาแนะนำ (Recommended Study Order)

1. `math_utils.py` - ทำความเข้าใจ Linear Regression และสถิติ
2. `calibrator.py` - ดูการประยุกต์ใช้ Linear Regression กับการสอบเทียบ
3. `data_manager.py` - เรียนรู้การจัดการ file I/O
4. `titration.py` - ศึกษาอัลกอริทึมตรวจจับจุดสมมูล

---

## สมการสำคัญ (Key Equations)

### Linear Regression

```
slope (m) = Σ(xi - x̄)(yi - ȳ) / Σ(xi - x̄)²
intercept (b) = ȳ - m * x̄
R² = 1 - (SS_residual / SS_total)
```

### Nernst Equation (ที่ 25 C)

```
E = E0 - 59.16 mV * pH    (slope ทฤษฎี = -59.16 mV/pH)

สมการ direct-use (ใช้ใน TitraLab):
pH = slope_m * mV + intercept_b
   โดย slope_m ≈ -0.0169 pH/mV (= 1/(-59.16))
       intercept_b ≈ 34-36 pH
```

### Derivative สำหรับหาจุดสมมูล (Constant Dose Volume)

```
dpH/dV = (pH[i] - pH[i-1]) / (V[i] - V[i-1])

เนื่องจาก TitraLab ใช้ constant dose volume (0.2 mL):
  V[i] - V[i-1] = 0.2 mL (คงที่ทุก step)

ดังนั้น:
  dpH/dV = (pH[i] - pH[i-1]) / 0.2
  จุดสมมูล = step ที่ |pH[i] - pH[i-1]| มากที่สุด
```

---

*TitraLab Week 3 - Core Logic Layer*

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
- Linear Regression ใช้สร้างสมการสอบเทียบ pH (pH = slope * mV + intercept)
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

print(f"สมการ: pH = {lr.slope:.4f} * V + {lr.intercept:.4f}")
print(f"R-squared: {lr.r_squared:.4f}")

# ทำนายค่า
ph = lr.predict(2.100)  # ทำนาย pH จากแรงดัน 2.1V
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
- **pH Calibration**: สร้างสมการ pH = slope * mV + intercept จากบัฟเฟอร์มาตรฐาน
- **Flow Rate Calibration**: วัดอัตราการไหลจริงของปั๊ม (mL/s)

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
# result = {'slope': -5.79, 'intercept': 16.77, 'r_squared': 0.999, 'is_valid': True}

# สอบเทียบอัตราการไหล
flow_result = calibrator.calibrate_flow_rate()
# flow_result = {'flow_rate': 0.277, 'volume': 5.0, 'time': 18.05}

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
- `data_calibrate.txt` - ค่าสอบเทียบ pH (slope, intercept)
- `data_flowrate.txt` - อัตราการไหลของปั๊ม
- `/sd/titration_*.csv` - ข้อมูลการไทเทรต

```python
# ตัวอย่างการใช้งาน (Usage Example)
from core.data_manager import DataManager

dm = DataManager(sd_card=sd_card)

# บันทึก/โหลด ค่าสอบเทียบ pH
dm.save_ph_calibration(slope=-5.79, intercept=16.77)
slope, intercept = dm.load_ph_calibration()

# บันทึก/โหลด อัตราการไหล
dm.save_flow_rate(0.277)
flow_rate = dm.load_flow_rate()

# บันทึกข้อมูลไทเทรต
dm.start_titration_log("titration_001.csv")
dm.log_titration_point(volume=1.0, ph=7.02, temp=25.1)
dm.end_titration_log()
```

---

### titration.py - คลาสควบคุมการไทเทรต (Titration Controller Class)

**หน้าที่**: ควบคุมการไทเทรตอัตโนมัติและตรวจจับจุดสมมูล

**ความเชื่อมโยงกับเคมี**:
- ตรวจจับจุดสมมูล (equivalence point) ด้วยวิธี derivative
- จุดสมมูลคือจุดที่ |dpH/dV| มีค่าสูงสุด

```python
# ตัวอย่างการใช้งาน (Usage Example)
from core.titration import TitrationController

titration = TitrationController(
    pump=pump,
    ph_sensor=ph_sensor,
    temp_sensor=temp_sensor,
    sd_card=sd_card,
    display=display,
    buzzer=buzzer
)

# เริ่มไทเทรตอัตโนมัติ
result = titration.run_titration()
# result = {
#     'equivalence_volume': 25.3,
#     'equivalence_ph': 7.02,
#     'total_volume': 25.5,
#     'data_points': [(0.0, 2.1), (1.0, 2.5), ...]
# }
```

**อัลกอริทึมหาจุดสมมูล (Equivalence Point Detection)**:
```python
# วิธี First Derivative (dpH/dV)
for i in range(1, len(data_points)):
    delta_v = volume[i] - volume[i-1]
    delta_ph = pH[i] - pH[i-1]
    derivative = delta_ph / delta_v

    if abs(derivative) > max_derivative:
        max_derivative = abs(derivative)
        equivalence_point = (volume[i], pH[i])
```

**เฟสการทำงาน (Operating Phases)**:
| เฟส | Duty Cycle | เงื่อนไข |
|-----|------------|----------|
| Fast Dosing | 100% | ห่างจาก target pH > 1.5 unit |
| Slow Dosing | 50% | ห่างจาก target pH < 1.5 unit |
| Endpoint | หยุด | ห่างจาก target pH < 0.3 unit |

**Safety Limits**:
- ปริมาตรสูงสุด: 50 mL
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
E = E0 - 59.16 mV * pH
หรือ
pH = slope * E + intercept
```

### Derivative สำหรับหาจุดสมมูล

```
dpH/dV = (pH[i] - pH[i-1]) / (V[i] - V[i-1])
จุดสมมูล = จุดที่ |dpH/dV| สูงสุด
```

---

*TitraLab Week 3 - Core Logic Layer*

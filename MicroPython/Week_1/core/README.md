# Week 1 Core: TitraLab Hardware & OOP Fundamentals

## ภาพรวม (Overview)

โฟลเดอร์ `core/` นี้ประกอบด้วยไฟล์สอนหลักสำหรับการเรียนรู้บอร์ด TitraLab และ Object-Oriented Programming (OOP) โดยออกแบบมาเพื่อให้นิสิตที่ไม่มีพื้นฐานการเขียนโปรแกรมสามารถเข้าใจการทำงานของฮาร์ดแวร์และหลักการ OOP

This `core/` folder contains teaching files for learning the TitraLab board and Object-Oriented Programming (OOP). The curriculum is designed for students with no programming background, teaching hardware operation and OOP concepts through hands-on exercises.

### เนื้อหาหลัก (Main Content):
| หมวด | จำนวนไฟล์ | หัวข้อ |
|------|----------|--------|
| OOP Fundamentals | 7 ไฟล์ | Class, Object, Encapsulation, Composition |
| 07_ADC/ | 3 ไฟล์ | ADC 12-bit, Averaging, Attenuation (สำหรับ pH sensor) |
| 07_PWM/ | 4 ไฟล์ | Duty Cycle, Frequency, Pump Control (สำหรับปั๊ม) |

**ระยะเวลารวม (Total Duration):** ~4 ชั่วโมง 40 นาที (สามารถเลือกสอนบางส่วนได้)

---

## สิ่งที่ต้องเตรียม (Prerequisites)

### ไฟล์ Library (Library Files)
ต้องคัดลอกไฟล์ต่อไปนี้ไปไว้ในโฟลเดอร์ `lib/` บน ESP32:

| File | Description |
|------|-------------|
| `ili9341.py` | TFT Display driver (ไดรเวอร์จอ TFT) |
| `xglcd_font.py` | Font rendering library (ไลบรารีแสดงฟอนต์) |
| `sdcard.py` | SD card driver (ไดรเวอร์ SD card) |

### ไฟล์ Font (Font Files)
ต้องคัดลอกไฟล์ฟอนต์ไปไว้ในโฟลเดอร์ `fonts/` บน ESP32:

| File | Description |
|------|-------------|
| `EspressoDolce18x24.c` | Large font 18x24 pixels (ฟอนต์ขนาดใหญ่) |
| `ArcadePix9x11.c` | Small font 9x11 pixels (ฟอนต์ขนาดเล็ก) |

### โครงสร้างไฟล์บน ESP32 (File Structure on ESP32)
```
ESP32 Root/
├── lib/
│   ├── ili9341.py
│   ├── xglcd_font.py
│   └── sdcard.py
├── fonts/
│   ├── EspressoDolce18x24.c
│   └── ArcadePix9x11.c
└── (your .py files)
```

### ความรู้พื้นฐาน (Background Knowledge)
- **ด้านเคมี (Chemistry):** หลักการไทเทรชัน (titration), การวัด pH, สมการ Nernst
- **ด้านโปรแกรม (Programming):** ไม่จำเป็นต้องมีพื้นฐาน - เริ่มต้นจากศูนย์

---

## รายละเอียดไฟล์ (File Descriptions)

### 1. `01_intro_oop.py` - บทนำ OOP (OOP Introduction)
**ระยะเวลา (Duration):** ~30 นาที

**แนวคิด OOP ที่สอน (OOP Concepts):**
- Class (คลาส) = พิมพ์เขียว/แม่แบบ (Blueprint)
- Object (ออบเจกต์) = ตัวอย่างที่สร้างจากคลาส (Instance)
- `__init__()` = Constructor - ฟังก์ชันที่ทำงานตอนสร้าง object
- `self` = ตัวอ้างอิงถึง object ปัจจุบัน (Reference to current object)
- Method (เมธอด) = ฟังก์ชันภายในคลาส

**ตัวอย่าง (Example):** คลาส `Beaker` - จำลองบีกเกอร์ในห้องปฏิบัติการ
```python
beaker_1 = Beaker(250)           # สร้างบีกเกอร์ 250 mL
beaker_1.add_liquid(100, "HCl")  # เติม HCl 100 mL
beaker_1.get_info()              # แสดงข้อมูล
```

**เชื่อมโยงเคมี (Chemistry Connection):**
บีกเกอร์มี attribute (capacity, volume, contents) และ method (add, pour, get_info) เหมือนกับอุปกรณ์จริงในห้องปฏิบัติการ

---

### 2. `02_led_class.py` - คลาส LED (LED Class)
**ระยะเวลา (Duration):** ~20 นาที

**แนวคิด OOP ที่สอน (OOP Concepts):**
- Encapsulation (การห่อหุ้ม) - ซ่อน `_pin` ไว้ภายในคลาส
- Method chaining - `on()`, `off()`, `toggle()`, `blink()`
- Default parameter - `name="LED"`, `delay_sec=0.3`
- Resource cleanup - `deinit()` method

**Pin Configuration:**
| LED | GPIO Pin | Usage in Titration |
|-----|----------|-------------------|
| Red | GPIO 2 | Endpoint reached (ถึงจุดสมมูล) |
| Green | GPIO 4 | System running (กำลังทำงาน) |

**ตัวอย่าง (Example):**
```python
led_red = LED(2, "Red")
led_red.on()         # เปิด LED
led_red.blink(3)     # กระพริบ 3 ครั้ง
led_red.deinit()     # คืนทรัพยากร
```

**เชื่อมโยงเคมี (Chemistry Connection):**
- LED เขียว: แสดงสถานะกำลังหยดสารละลาย (titrant delivery)
- LED แดง: แจ้งเตือนเมื่อถึงจุดสมมูล (equivalence point alert)

---

### 3. `03_button_class.py` - คลาสปุ่มกด (Button Class)
**ระยะเวลา (Duration):** ~25 นาที

**แนวคิด OOP ที่สอน (OOP Concepts):**
- State management - `_was_pressed`, `_last_press_time`
- Private attributes - underscore prefix `_xxx`
- Debounce algorithm - ป้องกันการอ่านซ้ำ
- Blocking vs non-blocking - `wait_for_press()` vs `is_pressed()`

**Pin Configuration:**
| Button | GPIO Pin | Usage in Titration |
|--------|----------|-------------------|
| Button 1 | GPIO 34 | Start/Stop (เริ่ม/หยุด) |
| Button 2 | GPIO 35 | Confirm calibration (ยืนยันการสอบเทียบ) |
| Button 3 | GPIO 39 | Cancel/Exit (ยกเลิก/ออก) |

**หมายเหตุ (Note):** GPIO34, 35, 39 เป็น input-only ไม่มี internal pull-up บอร์ด TitraLab ใช้ external pull-down resistor

**ตัวอย่าง (Example):**
```python
btn = Button(34, "Start", debounce_ms=200)
if btn.is_pressed():    # Return True เพียงครั้งเดียวต่อการกด
    print("Pressed!")
```

**เชื่อมโยงเคมี (Chemistry Connection):**
- ปุ่ม Start: เริ่มการไทเทรชัน
- ปุ่ม Confirm: ยืนยันค่า pH buffer ระหว่าง calibration
- ปุ่ม Exit: ยกเลิกและบันทึกข้อมูล

---

### 4. `04_temp_sensor_class.py` - คลาสเซ็นเซอร์อุณหภูมิ (Temperature Sensor Class)
**ระยะเวลา (Duration):** ~25 นาที

**แนวคิด OOP ที่สอน (OOP Concepts):**
- Class constants - `R = 8.314`, `F = 96485`
- Multiple return formats - `read_celsius()`, `read_kelvin()`, `read_fahrenheit()`
- Error handling - `RuntimeError` when sensor not found
- Chemistry calculation method - `get_nernst_slope()`

**Pin Configuration:**
| Sensor | GPIO Pin | Protocol |
|--------|----------|----------|
| DS18B20 | GPIO 16 | OneWire |

**ตัวอย่าง (Example):**
```python
sensor = TemperatureSensor(16)
temp_c = sensor.read_celsius()    # อ่านอุณหภูมิเป็นองศาเซลเซียส
temp_k = sensor.read_kelvin()     # อ่านอุณหภูมิเป็นเคลวิน (สำหรับ Nernst)
slope = sensor.get_nernst_slope() # คำนวณ slope จากอุณหภูมิจริง
```

**เชื่อมโยงเคมี (Chemistry Connection) - สมการ Nernst:**
```
E = E0 - (2.303 * R * T) / (n * F) * pH

ที่ 25C (298 K): slope = 59.16 mV/pH
ที่ 30C (303 K): slope = 60.15 mV/pH
```

การวัด pH ที่แม่นยำต้องชดเชยอุณหภูมิ (temperature compensation) เพราะ slope เปลี่ยนตามอุณหภูมิ

---

### 5. `05_display_basics.py` - พื้นฐานจอแสดงผล (TFT Display Basics)
**ระยะเวลา (Duration):** ~30 นาที

**แนวคิด OOP ที่สอน (OOP Concepts):**
- Hardware initialization - `init_display()`
- Color constants - `color565(R, G, B)`
- Helper functions - `draw_text()`, `draw_value_box()`, `draw_status_bar()`
- Modular design - แยกฟังก์ชันออกเป็นส่วนย่อย

**Pin Configuration (SPI1):**
| Function | GPIO Pin |
|----------|----------|
| SCK (Clock) | GPIO 14 |
| MOSI (Data) | GPIO 13 |
| DC (Data/Command) | GPIO 27 |
| CS (Chip Select) | GPIO 15 |
| RST (Reset) | GPIO 0 |

**ตัวอย่าง (Example):**
```python
display = init_display()
font = load_font()
draw_status_bar(display, font, "TitraLab v1.0")
draw_value_box(display, font, 50, 100, "pH", "7.00", "", GREEN)
```

**เชื่อมโยงเคมี (Chemistry Connection):**
จอ TFT แสดงข้อมูลแบบ real-time ระหว่างการไทเทรชัน:
- ค่า pH ปัจจุบัน
- อุณหภูมิสารละลาย
- ปริมาตร titrant ที่หยดไป
- สถานะระบบ (Running/Stopped/Endpoint)

---

### 6. `06_combined_example.py` - ระบบรวม (Combined Lab Alert System)
**ระยะเวลา (Duration):** ~40 นาที

**แนวคิด OOP ที่สอน (OOP Concepts):**
- **Composition** (การประกอบ) - รวมหลาย object เข้าด้วยกัน
- Simplified inline classes - คลาสแบบย่อสำหรับอ้างอิง
- State machine - `running` state toggle
- Main loop pattern - event checking + periodic updates
- Graceful cleanup - `cleanup()` method

**ระบบประกอบด้วย (Components):**
```
TitrationMonitor
├── LED (GPIO 2, 4)      - แสดงสถานะ
├── Button (GPIO 34)     - สั่งเริ่ม/หยุด
├── TempSensor (GPIO 16) - วัดอุณหภูมิ
└── Display (SPI1)       - แสดงผล
```

**ตัวอย่าง (Example):**
```python
monitor = TitrationMonitor()
try:
    monitor.run()       # Main loop
finally:
    monitor.cleanup()   # คืนทรัพยากรทั้งหมด
```

**เชื่อมโยงเคมี (Chemistry Connection):**
ระบบจำลองการติดตามการไทเทรชัน:
- กดปุ่มเพื่อเริ่ม/หยุดการวัด
- แสดงอุณหภูมิทั้งองศาเซลเซียสและเคลวิน
- LED เขียวติด = กำลังวัด, LED แดงติด = หยุดวัด

---

### 7. `ex_status_led.py` - แบบฝึกหัด: คลาส StatusLED (Exercise: StatusLED Class)
**ระยะเวลา (Duration):** ~15 นาที

**วัตถุประสงค์ (Objective):**
ให้นิสิตเขียนคลาส `StatusLED` ด้วยตนเอง โดยเติมโค้ดในส่วน `TODO`

**ส่วนที่ต้องเติม (TODO Sections):**
1. `__init__()` - สร้าง Pin object และกำหนดค่าเริ่มต้น
2. `on()` - เปิด LED
3. `off()` - ปิด LED
4. `blink()` - กระพริบ LED
5. `is_on` property - ตรวจสอบสถานะ

**Test Cases ที่ให้มา:**
```python
led_red = StatusLED(2)
led_red.on()
print(led_red.is_on)   # Should be True
led_red.blink(times=5, delay_ms=200)
```

---

## โฟลเดอร์ 07_ADC/ - พื้นฐาน ADC (ADC Fundamentals)

โฟลเดอร์นี้สอนพื้นฐาน ADC (Analog-to-Digital Converter) ซึ่งเป็นหัวใจสำคัญของการอ่านค่าจากเซ็นเซอร์ pH

This folder teaches ADC (Analog-to-Digital Converter) fundamentals, which is essential for reading pH sensor values.

### 8. `07_ADC/01_adc_basics.py` - พื้นฐาน ADC (ADC Basics)
**ระยะเวลา (Duration):** ~15 นาที

**แนวคิดที่สอน (Concepts):**
- ADC แปลง analog (0-3.3V) เป็น digital (0-4095)
- ADC converts analog (0-3.3V) to digital (0-4095)
- ESP32 ADC 12-bit resolution (2^12 = 4096 ระดับ)
- สูตรแปลงค่า: voltage = (raw / 4095) * 3.3

**Pin Configuration:**
| Component | GPIO Pin | Description |
|-----------|----------|-------------|
| Potentiometer 1 | GPIO 32 | ใช้ทดสอบการอ่าน ADC |
| Potentiometer 2 | GPIO 33 | สำรอง (optional) |

**ตัวอย่าง (Example):**
```python
from machine import Pin, ADC
adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)  # ตั้งช่วง 0-3.3V
raw_value = adc.read()     # อ่านค่า 0-4095
voltage = (raw_value / 4095) * 3.3
```

**เชื่อมโยงเคมี (Chemistry Connection):**
เซ็นเซอร์ pH ส่งสัญญาณ analog ออกมา เราต้องใช้ ADC อ่านค่าก่อนแปลงเป็น pH

---

### 9. `07_ADC/02_adc_averaging.py` - การเฉลี่ยค่า ADC (ADC Averaging)
**ระยะเวลา (Duration):** ~10 นาที

**แนวคิดที่สอน (Concepts):**
- สัญญาณ analog มี noise (สัญญาณรบกวน)
- Analog signals have noise
- การเฉลี่ยหลายค่าช่วยลด noise (Moving average)
- Averaging multiple readings reduces noise

**ตัวอย่าง (Example):**
```python
def read_averaged(adc, num_samples=10):
    total = 0
    for _ in range(num_samples):
        total += adc.read()
        time.sleep_ms(5)
    return total // num_samples
```

**เชื่อมโยงเคมี (Chemistry Connection):**
ค่า pH ที่เสถียรต้องเฉลี่ยหลายค่า เหมือนการวัดซ้ำหลายครั้งในห้องปฏิบัติการ

---

### 10. `07_ADC/03_adc_attenuation.py` - การตั้งค่า Attenuation (ADC Attenuation)
**ระยะเวลา (Duration):** ~15 นาที

**แนวคิดที่สอน (Concepts):**
- Attenuation กำหนดช่วงแรงดันที่ ADC อ่านได้
- Attenuation determines readable voltage range
- ตาราง Attenuation:

| Setting | ช่วงแรงดัน | การใช้งาน |
|---------|-----------|----------|
| ATTN_0DB | 0-1.1V | เซ็นเซอร์แรงดันต่ำ |
| ATTN_2_5DB | 0-1.5V | Low voltage sensor |
| ATTN_6DB | 0-2.2V | Medium voltage |
| **ATTN_11DB** | **0-3.3V** | **pH sensor (แนะนำ)** |

**ตัวอย่าง (Example):**
```python
adc = ADC(Pin(25))  # pH sensor pin
adc.atten(ADC.ATTN_11DB)  # ครอบคลุม 0-3.3V
# สำหรับ pH sensor ที่ส่งออก 0-3V
```

**เชื่อมโยงเคมี (Chemistry Connection):**
pH sensor บน TitraLab ส่งแรงดัน 0-3V ดังนั้น ATTN_11DB เหมาะสมที่สุดเพราะครอบคลุมทุกค่า pH

---

## โฟลเดอร์ 07_PWM/ - พื้นฐาน PWM (PWM Fundamentals)

โฟลเดอร์นี้สอนพื้นฐาน PWM (Pulse Width Modulation) ซึ่งใช้ควบคุมความเร็วปั๊มในการไทเทรชัน

This folder teaches PWM (Pulse Width Modulation) fundamentals, used for pump speed control during titration.

### 11. `07_PWM/01_pwm_led_brightness.py` - พื้นฐาน PWM: ควบคุมความสว่าง LED
**ระยะเวลา (Duration):** ~15 นาที

**แนวคิดที่สอน (Concepts):**
- PWM จำลองสัญญาณ analog จาก digital
- PWM simulates analog output from digital signals
- Duty Cycle = สัดส่วนเวลาที่สัญญาณเป็น HIGH
- ESP32 ใช้ค่า 0-1023 (10-bit)

**แผนภาพ Duty Cycle:**
```
0% (duty=0)       50% (duty=512)     100% (duty=1023)
_________________  _____     _____   ___________________
                  |     |___|     |
LED: ปิด (Off)    LED: หรี่ (Dim)   LED: สว่างสุด (Bright)
```

**ตัวอย่าง (Example):**
```python
from machine import Pin, PWM
led_pwm = PWM(Pin(2))
led_pwm.freq(1000)     # 1000 Hz
led_pwm.duty(512)      # 50% brightness
```

**เชื่อมโยงเคมี (Chemistry Connection):**
หลักการเดียวกับที่ใช้ควบคุมความเร็วปั๊ม: duty ต่ำ = ปั๊มช้า, duty สูง = ปั๊มเร็ว

---

### 12. `07_PWM/02_pwm_led_fade.py` - PWM: LED Fade Smoothly
**ระยะเวลา (Duration):** ~10 นาที

**แนวคิดที่สอน (Concepts):**
- การเปลี่ยน duty cycle แบบค่อยเป็นค่อยไป
- Gradual duty cycle transitions
- สร้าง effect การ fade in/out อย่างนุ่มนวล
- Creating smooth fade in/out effects

**ตัวอย่าง (Example):**
```python
# Fade in: 0% -> 100%
for duty in range(0, 1024, 32):
    led_pwm.duty(duty)
    time.sleep_ms(50)

# Fade out: 100% -> 0%
for duty in range(1023, -1, -32):
    led_pwm.duty(duty)
    time.sleep_ms(50)
```

**เชื่อมโยงเคมี (Chemistry Connection):**
การค่อยๆ เปลี่ยนความเร็วปั๊มช่วยให้การควบคุมปริมาตรแม่นยำขึ้น

---

### 13. `07_PWM/03_pwm_frequency.py` - PWM: Frequency vs Duty Cycle
**ระยะเวลา (Duration):** ~10 นาที

**แนวคิดที่สอน (Concepts):**
- Frequency = จำนวนรอบต่อวินาที (Hz)
- Frequency = cycles per second (Hz)
- Duty Cycle = สัดส่วนเวลา ON ในแต่ละรอบ
- Duty Cycle = proportion of ON time per cycle

**ความแตกต่าง:**
| Parameter | ผลต่อ LED | ผลต่อปั๊ม |
|-----------|----------|----------|
| Frequency | ความเรียบของแสง | เสียง/ความนุ่มนวล |
| Duty Cycle | ความสว่าง | ความเร็ว |

**ตัวอย่าง (Example):**
```python
led_pwm.freq(500)   # 500 Hz - อาจเห็นกระพริบ
led_pwm.freq(1000)  # 1000 Hz - นุ่มนวล
led_pwm.freq(5000)  # 5000 Hz - นุ่มนวลมาก
```

---

### 14. `07_PWM/04_pwm_pump_preview.py` - PWM: ตัวอย่างควบคุมปั๊ม
**ระยะเวลา (Duration):** ~20 นาที

**แนวคิดที่สอน (Concepts):**
- ควบคุมความเร็วปั๊มด้วย PWM
- Controlling pump speed with PWM
- ฟังก์ชัน: `pump_on()`, `pump_off()`, `pump_set_speed()`
- จำลองรูปแบบการไทเทรชัน (titration pattern)

**Pin Configuration:**
| Component | GPIO Pin | Description |
|-----------|----------|-------------|
| Pump | GPIO 21 | PWM control |
| LED Green | GPIO 4 | ปั๊มทำงาน (pump running) |
| LED Red | GPIO 2 | ปั๊มหยุด (pump stopped) |

**รูปแบบการไทเทรชัน (Titration Pattern):**
```
Phase 1: ห่างจากจุดสมมูล -> 80% speed (เร็ว)
Phase 2: เข้าใกล้          -> 50% speed (ปานกลาง)
Phase 3: ใกล้มาก          -> 25% speed (ช้า - แม่นยำ)
Phase 4: ถึงจุดสมมูล!      -> 0% (หยุด)
```

**ตัวอย่าง (Example):**
```python
pump_pwm = PWM(Pin(21))
pump_pwm.freq(1000)

def pump_set_speed(pwm, percentage):
    duty = int((percentage / 100) * 1023)
    pwm.duty(duty)

pump_set_speed(pump_pwm, 80)  # 80% speed
time.sleep(3)
pump_set_speed(pump_pwm, 25)  # ลดลงใกล้จุดสมมูล
```

**เชื่อมโยงเคมี (Chemistry Connection):**
ในการไทเทรชัน:
- เริ่มต้น: เร็ว (pH เปลี่ยนช้า)
- ใกล้จุดสมมูล: ช้า (ควบคุมแม่นยำ)
- Week 2 จะเรียนการสอบเทียบ mL/min และควบคุมอัตโนมัติ

---

## ลำดับการเรียนรู้ (Learning Progression)

### เส้นทางที่ 1: OOP Fundamentals (ไฟล์ 01-06)
```
01_intro_oop.py (30 min)
    |
    v  เข้าใจ Class, Object, self
02_led_class.py (20 min)
    |
    v  ควบคุม GPIO Output
03_button_class.py (25 min)
    |
    v  อ่าน GPIO Input + Debounce
04_temp_sensor_class.py (25 min)
    |
    v  อ่านเซ็นเซอร์ OneWire + Nernst
05_display_basics.py (30 min)
    |
    v  แสดงผลบนจอ TFT
06_combined_example.py (40 min)
    |
    v  รวมทุกอย่าง + Composition
ex_status_led.py (15 min)
    |
    v  ฝึกเขียนคลาสด้วยตนเอง
```

### เส้นทางที่ 2: ADC Fundamentals (โฟลเดอร์ 07_ADC/)
```
07_ADC/01_adc_basics.py (15 min)
    |
    v  เข้าใจ ADC 12-bit, แปลง analog -> digital
07_ADC/02_adc_averaging.py (10 min)
    |
    v  การเฉลี่ยค่าเพื่อลด noise
07_ADC/03_adc_attenuation.py (15 min)
    |
    v  ตั้งค่า attenuation สำหรับ pH sensor
```

### เส้นทางที่ 3: PWM Fundamentals (โฟลเดอร์ 07_PWM/)
```
07_PWM/01_pwm_led_brightness.py (15 min)
    |
    v  เข้าใจ Duty Cycle, ควบคุมความสว่าง LED
07_PWM/02_pwm_led_fade.py (10 min)
    |
    v  Fade in/out อย่างนุ่มนวล
07_PWM/03_pwm_frequency.py (10 min)
    |
    v  ความแตกต่าง Frequency vs Duty Cycle
07_PWM/04_pwm_pump_preview.py (20 min)
    |
    v  ตัวอย่างควบคุมปั๊ม -> เตรียมพร้อม Week 2
```

### สรุปเวลา (Time Summary)
| หมวด | เวลา |
|------|------|
| OOP Fundamentals (01-06 + ex) | ~3 ชั่วโมง 5 นาที |
| ADC Fundamentals (07_ADC/) | ~40 นาที |
| PWM Fundamentals (07_PWM/) | ~55 นาที |
| **รวมทั้งหมด** | **~4 ชั่วโมง 40 นาที** |

**หมายเหตุ:** สามารถเลือกสอนบางส่วนตามเวลาที่มี เส้นทาง ADC และ PWM สามารถสอนแยกหรือรวมกับ OOP ได้

---

## วิธีรันไฟล์ใน Thonny (Quick Start - Running Files in Thonny)

### ขั้นตอนที่ 1: เชื่อมต่อบอร์ด (Connect Board)
1. เสียบสาย USB เชื่อมต่อบอร์ด TitraLab กับคอมพิวเตอร์
2. เปิด Thonny IDE
3. เลือก **Run > Configure interpreter...**
4. เลือก **MicroPython (ESP32)** และ port ที่ถูกต้อง (เช่น COM3)

### ขั้นตอนที่ 2: อัพโหลดไฟล์ Library (Upload Libraries)
1. คลิกขวาที่ไฟล์ใน `lib/` > **Upload to /**
2. สร้างโฟลเดอร์ `lib/` และ `fonts/` บน ESP32 ถ้ายังไม่มี
3. อัพโหลดไฟล์ library และ font ตามที่ระบุใน Prerequisites

### ขั้นตอนที่ 3: รันไฟล์ (Run File)
1. เปิดไฟล์ `.py` ที่ต้องการ
2. กดปุ่ม **Run (F5)** หรือคลิกปุ่มสีเขียว
3. ดูผลลัพธ์ใน Shell ด้านล่าง
4. กด **Ctrl+C** เพื่อหยุดโปรแกรม

### คำสั่งใน Shell (Shell Commands)
```python
# รันไฟล์โดยตรง
exec(open('01_intro_oop.py').read())

# หยุดโปรแกรม
# กด Ctrl+C

# Reset บอร์ด
# กด Ctrl+D หรือกดปุ่ม RESET บนบอร์ด
```

---

## เชื่อมโยงแนวคิด OOP กับเคมี (OOP-Chemistry Connections Summary)

| OOP Concept | Chemistry Analogy |
|-------------|-------------------|
| Class | สูตรเคมี/วิธีการทดลอง (Recipe/Procedure) |
| Object | สารละลายที่เตรียมจากสูตร (Prepared solution) |
| Attribute | คุณสมบัติสาร: ความเข้มข้น, ปริมาตร, pH |
| Method | การกระทำ: เติม, ผสม, วัด, หยด |
| Encapsulation | การควบคุมปฏิกิริยาในภาชนะปิด |
| Composition | การประกอบระบบไทเทรชันจากหลายส่วน |

---

## การแก้ปัญหาเบื้องต้น (Troubleshooting)

### ปัญหา: `ImportError: no module named 'ili9341'`
**สาเหตุ:** ไม่ได้อัพโหลดไฟล์ library
**แก้ไข:** อัพโหลดไฟล์ `ili9341.py` และ `xglcd_font.py` ไปที่โฟลเดอร์ `lib/` บน ESP32

### ปัญหา: `RuntimeError: DS18B20 not found`
**สาเหตุ:** เซ็นเซอร์ไม่ได้เชื่อมต่อ หรือสายหลุด
**แก้ไข:** ตรวจสอบการเชื่อมต่อที่ GPIO16

### ปัญหา: จอ TFT ไม่แสดงผล
**สาเหตุ:** ไม่ได้อัพโหลดไฟล์ฟอนต์ หรือ path ไม่ถูกต้อง
**แก้ไข:**
1. ตรวจสอบว่ามีโฟลเดอร์ `fonts/` บน ESP32
2. อัพโหลดไฟล์ `EspressoDolce18x24.c`
3. ตรวจสอบ path ในโค้ด: `fonts/EspressoDolce18x24.c`

### ปัญหา: ปุ่มกดไม่ตอบสนอง
**สาเหตุ:** GPIO34, 35, 39 เป็น input-only ไม่มี pull-up
**แก้ไข:** บอร์ด TitraLab มี external resistor อยู่แล้ว - ตรวจสอบการเชื่อมต่อสายไฟ

---

## Pin Reference (อ้างอิงขา GPIO)

```
TitraLab Board Pin Assignment
=============================
LED Red:      GPIO 2      (Output / PWM)
LED Green:    GPIO 4      (Output / PWM)
Button 1:     GPIO 34     (Input-only)
Button 2:     GPIO 35     (Input-only)
Button 3:     GPIO 39     (Input-only)
DS18B20:      GPIO 16     (OneWire)

ADC (Analog Input):
-------------------
Potentiometer 1: GPIO 32  (ADC, ใช้ในบทเรียน ADC)
Potentiometer 2: GPIO 33  (ADC, สำรอง)
pH Sensor:       GPIO 25  (ADC, ใช้ใน Week 2)

PWM (Analog Output):
--------------------
Pump:         GPIO 21     (PWM, ใช้ในบทเรียน PWM)
Buzzer:       GPIO 26     (PWM)

TFT Display (SPI1):
-------------------
TFT SCK:      GPIO 14     (SPI1)
TFT MOSI:     GPIO 13     (SPI1)
TFT DC:       GPIO 27     (SPI1)
TFT CS:       GPIO 15     (SPI1)
TFT RST:      GPIO 0      (SPI1)
```

---

## ผู้จัดทำ (Author)

เอกสารนี้จัดทำสำหรับรายวิชา 2302311 Integrated Chemistry Laboratory I
ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย

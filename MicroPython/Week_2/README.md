# TitraLab Week 2: Intermediate OOP
# TitraLab สัปดาห์ที่ 2: OOP ระดับกลาง

---

## วัตถุประสงค์ (Objectives)

หลังจากเรียนจบบทเรียนนี้ นักศึกษาจะสามารถ:

1. **เข้าใจ Inheritance/การสืบทอด**
   - สร้างคลาสลูก (Child Class) จากคลาสแม่ (Parent Class)
   - ใช้ `super().__init__()` เพื่อเรียก constructor ของคลาสแม่
   - Override เมธอดจากคลาสแม่เพื่อปรับแต่งพฤติกรรม

2. **เข้าใจ Composition/การประกอบ**
   - สร้างออบเจ็กต์ที่ประกอบด้วยออบเจ็กต์อื่น
   - เข้าใจความแตกต่างระหว่าง Inheritance และ Composition

3. **ใช้ @property decorator**
   - สร้าง getter และ setter สำหรับ attributes
   - ควบคุมการเข้าถึงข้อมูลภายในออบเจ็กต์

4. **เข้าใจ Encapsulation/การห่อหุ้ม**
   - ใช้ private attributes (`_variable`) เพื่อซ่อนข้อมูลภายใน
   - ป้องกันการเข้าถึงข้อมูลที่ไม่ต้องการให้แก้ไขโดยตรง

5. **ประยุกต์ใช้ OOP กับการควบคุม Hardware**
   - อ่านค่า pH และอุณหภูมิแบบ OOP
   - ควบคุมปั๊มด้วย PWM อย่างเป็นระบบ
   - สอบเทียบเซ็นเซอร์ด้วยโครงสร้างที่ดี

---

## ความรู้พื้นฐาน (Prerequisites)

### ความรู้ทางเคมี (Chemistry Knowledge)
- หลักการไทเทรตกรด-เบส (Acid-base titration)
- สมการ Nernst: E = E0 - (2.303RT/nF) x pH
- การสอบเทียบหัววัด pH ด้วยสารละลายบัฟเฟอร์มาตรฐาน (Standard buffer solutions)
- ความหมายของจุดสมมูล (Equivalence point) และจุดยุติ (Endpoint)

### ความรู้จาก Week 1 (Week 1 Knowledge)
- Python พื้นฐาน: Variables/ตัวแปร, Functions/ฟังก์ชัน, Loops/ลูป
- การสร้าง Class และ Object เบื้องต้น
- การทำงานกับ GPIO, ADC, PWM บน ESP32
- การใช้ Timer และ Interrupt

---

## การเชื่อมต่อกับ Week 1 (Connection to Week 1)

### Week 1 สิ่งที่เรียนไปแล้ว (Week 1 Review)

| หัวข้อ | สิ่งที่เรียน |
|--------|-------------|
| **Blink LED** | การควบคุม GPIO output, การใช้ loop |
| **Button** | การอ่าน GPIO input, interrupt, debounce |
| **DS18B20** | โปรโตคอล OneWire, การอ่านอุณหภูมิ |
| **SD Card** | การอ่าน/เขียนไฟล์ |
| **TFT Display** | การแสดงผลบนจอ ILI9341 |
| **Buzzer** | การใช้ PWM สร้างเสียง |

### Week 2 ต่อยอด (Week 2 Building On)

Week 2 นำความรู้จาก Week 1 มาจัดระเบียบด้วย OOP:

```
Week 1: ฟังก์ชันแยกกันทำงาน
  read_ph() --> แปลง ADC --> แสดงผล

Week 2: รวมเป็น Class ที่มีโครงสร้าง
  class pHSensor:
      def __init__(self):
          self._adc = ADC(Pin(25))
          self._slope = -5.7901
          self._intercept = 16.769

      @property
      def slope(self):
          return self._slope

      def read(self):
          voltage = self._read_voltage()
          ph = self._slope * voltage + self._intercept
          return voltage, ph
```

---

## แนวคิดหลัก (Key Concepts)

### 1. Inheritance/การสืบทอด

**แนวคิดทางเคมี (Chemistry Analogy):**
- หัววัด pH (pH electrode) เป็น **ประเภทหนึ่งของ** electrode ทั่วไป
- หัววัดอุณหภูมิ (Temperature sensor) เป็น **ประเภทหนึ่งของ** sensor ทั่วไป
- เหมือนกับที่ "กรดแก่" และ "กรดอ่อน" เป็นประเภทของ "กรด"

**แนวคิดการเขียนโปรแกรม (Programming Concept):**

```python
# คลาสแม่ (Parent Class/Base Class)
class Sensor:
    """คลาสพื้นฐานสำหรับเซ็นเซอร์ทั่วไป"""

    def __init__(self, pin_number):
        self._pin = pin_number
        self._is_calibrated = False

    def read_raw(self):
        """อ่านค่าดิบจากเซ็นเซอร์"""
        raise NotImplementedError("Subclass must implement")

    def calibrate(self):
        """สอบเทียบเซ็นเซอร์"""
        raise NotImplementedError("Subclass must implement")


# คลาสลูก (Child Class/Subclass)
class pHSensor(Sensor):
    """คลาสเซ็นเซอร์ pH สืบทอดจาก Sensor"""

    def __init__(self, pin_number=25, slope=-5.7901, intercept=16.769):
        # เรียก constructor ของคลาสแม่
        super().__init__(pin_number)

        # เพิ่ม attributes เฉพาะของ pHSensor
        self._slope = slope
        self._intercept = intercept
        self._adc = ADC(Pin(pin_number))
        self._adc.atten(ADC.ATTN_11DB)

    def read_raw(self):
        """Override: อ่านค่า ADC ดิบ"""
        return self._adc.read()

    def read_ph(self):
        """Method เฉพาะของ pHSensor"""
        voltage = self.read_voltage()
        return self._slope * voltage + self._intercept

    def calibrate(self):
        """Override: สอบเทียบเซ็นเซอร์ pH"""
        # ... calibration logic ...
        self._is_calibrated = True
```

**Syntax สำคัญ:**

| Syntax | ความหมาย |
|--------|----------|
| `class Child(Parent):` | สร้างคลาสลูกที่สืบทอดจากคลาสแม่ |
| `super().__init__()` | เรียก constructor ของคลาสแม่ |
| Method override | กำหนด method ชื่อเดียวกับคลาสแม่เพื่อเปลี่ยนพฤติกรรม |

---

### 2. Composition/การประกอบ

**แนวคิดทางเคมี (Chemistry Analogy):**
- ปั๊มไทแทรนต์ **ประกอบด้วย** มอเตอร์และตัวควบคุม PWM
- ระบบไทเทรต **ประกอบด้วย** หัววัด pH, ปั๊ม, และจอแสดงผล
- เหมือนกับที่ "เครื่อง pH Meter" ประกอบด้วย electrode, display, และ microprocessor

**แนวคิดการเขียนโปรแกรม (Programming Concept):**

```python
class PWMController:
    """คลาสควบคุม PWM"""

    def __init__(self, pin_number, freq=1000):
        self._pin = Pin(pin_number, Pin.OUT)
        self._pwm = PWM(self._pin, freq=freq)
        self._pwm.duty(0)

    def set_duty(self, percent):
        """กำหนด duty cycle (0-100%)"""
        duty_value = int((percent / 100) * 1023)
        self._pwm.duty(duty_value)

    def stop(self):
        """หยุด PWM"""
        self._pwm.duty(0)


class Pump:
    """คลาสปั๊ม - ประกอบด้วย PWMController"""

    def __init__(self, pin_number=21, flow_rate=0.2772):
        # Composition: Pump มี PWMController
        self._pwm_controller = PWMController(pin_number)
        self._flow_rate = flow_rate
        self._is_running = False
        self._start_time = 0

    def start(self, duty_percent=100):
        """เริ่มปั๊ม"""
        self._pwm_controller.set_duty(duty_percent)
        self._start_time = ticks_us()
        self._is_running = True

    def stop(self):
        """หยุดปั๊ม"""
        self._pwm_controller.stop()
        elapsed = ticks_diff(ticks_us(), self._start_time) / 1_000_000
        volume = self._flow_rate * elapsed
        self._is_running = False
        return {'time': elapsed, 'volume': volume}
```

**Inheritance vs Composition:**

| ความสัมพันธ์ | ตัวอย่าง | เมื่อใช้ |
|-------------|----------|---------|
| **Inheritance** (is-a) | pHSensor **is a** Sensor | เมื่อคลาสลูก "เป็นประเภทหนึ่งของ" คลาสแม่ |
| **Composition** (has-a) | Pump **has a** PWMController | เมื่อคลาสหนึ่ง "มี" คลาสอื่นเป็นส่วนประกอบ |

---

### 3. @property Decorator

**แนวคิดทางเคมี (Chemistry Analogy):**
- ค่า slope ของการสอบเทียบ - อ่านได้ แต่ควรเปลี่ยนผ่านกระบวนการสอบเทียบเท่านั้น
- ค่า R-squared - อ่านได้อย่างเดียว เกิดจากการคำนวณ

**แนวคิดการเขียนโปรแกรม (Programming Concept):**

```python
class pHSensor:
    def __init__(self):
        self._slope = -5.7901      # Private attribute
        self._intercept = 16.769   # Private attribute

    @property
    def slope(self):
        """Getter - อ่านค่า slope"""
        return self._slope

    @slope.setter
    def slope(self, value):
        """Setter - กำหนดค่า slope พร้อม validation"""
        if -100 < value < 0:
            self._slope = value
            print(f"Slope updated: {value}")
        else:
            raise ValueError("Slope must be between -100 and 0")

    @property
    def intercept(self):
        """Getter - อ่านค่า intercept"""
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """Setter - กำหนดค่า intercept"""
        self._intercept = value


# การใช้งาน
sensor = pHSensor()
print(sensor.slope)      # อ่านค่า: -5.7901
sensor.slope = -6.0      # กำหนดค่าใหม่
sensor.slope = 10        # Error! ค่าไม่ถูกต้อง
```

---

### 4. Encapsulation/การห่อหุ้ม

**แนวคิดทางเคมี (Chemistry Analogy):**
- ข้อมูลการสอบเทียบภายในเครื่อง pH Meter - ผู้ใช้ไม่ควรแก้ไขโดยตรง
- Reference electrode voltage - ค่าภายในที่ไม่ควรเปลี่ยน

**แนวคิดการเขียนโปรแกรม (Programming Concept):**

```python
class pHSensor:
    def __init__(self):
        # Private attributes (ขึ้นต้นด้วย _)
        self._adc = ADC(Pin(25))           # ซ่อนการเข้าถึง ADC โดยตรง
        self._calibration_points = []       # ข้อมูลสอบเทียบภายใน
        self._slope = -5.7901
        self._intercept = 16.769

    # Public method - ผู้ใช้เรียกได้
    def read(self):
        """อ่านค่า pH (public)"""
        voltage = self._read_voltage()      # เรียก private method
        ph = self._calculate_ph(voltage)    # เรียก private method
        return voltage, ph

    # Private method - ใช้ภายในเท่านั้น
    def _read_voltage(self):
        """อ่านแรงดัน (private)"""
        raw = self._adc.read()
        return (raw / 4095) * 3.3

    def _calculate_ph(self, voltage):
        """คำนวณ pH (private)"""
        return self._slope * voltage + self._intercept
```

**Convention สำหรับ Private:**

| รูปแบบ | ความหมาย |
|--------|----------|
| `variable` | Public - เข้าถึงได้จากภายนอก |
| `_variable` | Protected - ควรใช้ภายในเท่านั้น (convention) |
| `__variable` | Private - Python จะ name mangle (ไม่ค่อยใช้) |

---

## การกำหนดขา GPIO (Hardware Configuration)

### GPIO สำหรับ Week 2

```
                    +------------------+
                    |    ESP32 Board   |
                    |                  |
    Red LED    <----|  GPIO2           |
    Green LED  <----|  GPIO4           |
                    |                  |
    TFT SCK    <----|  GPIO14          |
    TFT MOSI   <----|  GPIO13          |
    TFT CS     <----|  GPIO15          |
    TFT DC     <----|  GPIO27          |
    TFT RST    <----|  GPIO0           |
                    |                  |
    DS18B20    <----|  GPIO16          |  <- Temperature Sensor
                    |                  |
    Pump PWM   <----|  GPIO21          |  <- Pump Control
                    |                  |
    pH Sensor  ---->|  GPIO25 (ADC)    |  <- pH Measurement
                    |                  |
    Button 1   ---->|  GPIO34 (Input)  |  <- Start/Confirm
    Button 2   ---->|  GPIO35 (Input)  |  <- Select/Navigate
    Button 3   ---->|  GPIO39 (Input)  |  <- Back/Cancel
                    |                  |
    Buzzer     <----|  GPIO26 (PWM)    |
                    +------------------+
```

### ตารางสรุป GPIO

| อุปกรณ์ | GPIO | ประเภท | หมายเหตุ |
|---------|------|--------|----------|
| **Sensors** |
| pH Sensor | GPIO25 | ADC Input | อ่านแรงดัน 0-3.3V จากหัววัด pH |
| Temperature (DS18B20) | GPIO16 | OneWire | ต้องใช้ pull-up resistor 4.7K |
| **Actuators** |
| Pump | GPIO21 | PWM Output | ความถี่ 1000 Hz, 10-bit duty (0-1023) |
| **Buttons** |
| Button 1 (Start) | GPIO34 | Input-only | ต้องใช้ external pull-down 10K |
| Button 2 (Select) | GPIO35 | Input-only | ต้องใช้ external pull-down 10K |
| Button 3 (Back) | GPIO39 | Input-only | ต้องใช้ external pull-down 10K |

### ข้อควรระวัง GPIO34/35/39

```python
# GPIO34, 35, 39 เป็น Input-Only Pins
# ไม่รองรับ internal pull-up/pull-down resistor
# ต้องใช้ external pull-down resistor (10K ohm)

button_1 = Pin(34, Pin.IN)  # ถูกต้อง
button_1 = Pin(34, Pin.IN, Pin.PULL_DOWN)  # ผิด! ไม่รองรับ

# การต่อวงจร:
#   Button -> GPIO34
#   GPIO34 -> 10K resistor -> GND
#   Button อีกขา -> 3.3V
```

---

## คำอธิบายไฟล์ (File Descriptions)

### โฟลเดอร์ pH/

| ไฟล์ | คำอธิบาย | แนวคิด OOP ที่เรียน |
|------|----------|-------------------|
| `01_pH.py` | การวัดค่า pH และอุณหภูมิ พร้อมบันทึกข้อมูล | Functions, Timer interrupt, State variables |
| `02_calibration.py` | การสอบเทียบ pH 3 จุด | Procedural calibration |

### โฟลเดอร์ Pump/

| ไฟล์ | คำอธิบาย | แนวคิด OOP ที่เรียน |
|------|----------|-------------------|
| `01_flowRate.py` | การควบคุมปั๊มด้วย PWM | PWM control, Duty cycle |
| `pumpValidate_1.py` | การปั๊มต่อเนื่องจนถึงปริมาตรเป้าหมาย | Volume calculation, Precise timing |
| `pumpValidate_2.py` | การปั๊มแบบเป็นช่วงๆ (intermittent) | Interval pumping, pH stabilization |

### โฟลเดอร์ Old/

| ไฟล์ | คำอธิบาย | หมายเหตุ |
|------|----------|----------|
| `cal_pH.py` | โค้ดเก่าสำหรับ calibrate pH | อ้างอิงสำหรับการเรียนรู้ |
| `cal_flowrate.py` | โค้ดเก่าสำหรับ calibrate flow rate | อ้างอิงสำหรับการเรียนรู้ |

---

## โค้ดตัวอย่าง (Example Code)

### ตัวอย่าง 1: Inheritance - สร้างคลาส pHSensor

```python
"""
ตัวอย่าง Inheritance: pHSensor สืบทอดจาก BaseSensor
Example Inheritance: pHSensor inherits from BaseSensor
"""
from machine import Pin, ADC
from time import sleep_ms


class BaseSensor:
    """
    คลาสพื้นฐานสำหรับเซ็นเซอร์ทั้งหมด
    Base class for all sensors
    """

    def __init__(self, pin_number, name="Sensor"):
        self._pin_number = pin_number
        self._name = name
        self._is_calibrated = False
        print(f"{name} initialized on GPIO{pin_number}")

    @property
    def name(self):
        """ชื่อเซ็นเซอร์ (Sensor name)"""
        return self._name

    @property
    def is_calibrated(self):
        """สถานะการสอบเทียบ (Calibration status)"""
        return self._is_calibrated

    def read_raw(self):
        """อ่านค่าดิบ - ต้อง override ในคลาสลูก"""
        raise NotImplementedError("Subclass must implement read_raw()")


class pHSensor(BaseSensor):
    """
    คลาสเซ็นเซอร์ pH - สืบทอดจาก BaseSensor
    pH Sensor class - inherits from BaseSensor

    ตัวอย่างการใช้งาน (Usage):
        >>> sensor = pHSensor()
        >>> voltage, ph = sensor.read()
        >>> print(f"pH = {ph:.2f}")
    """

    # ค่าคงที่ (Constants)
    ADC_MAX = 4095
    ADC_VOLTAGE = 3.3

    def __init__(self, pin=25, slope=-5.7901, intercept=16.769):
        # เรียก constructor ของ BaseSensor
        super().__init__(pin, "pH Sensor")

        # Private attributes เฉพาะ pHSensor
        self._slope = slope
        self._intercept = intercept
        self._adc = ADC(Pin(pin))
        self._adc.atten(ADC.ATTN_11DB)
        self._samples = 10

    @property
    def slope(self):
        """ค่า slope ของสมการสอบเทียบ"""
        return self._slope

    @slope.setter
    def slope(self, value):
        """กำหนดค่า slope"""
        self._slope = value

    @property
    def intercept(self):
        """ค่า intercept ของสมการสอบเทียบ"""
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """กำหนดค่า intercept"""
        self._intercept = value

    def read_raw(self):
        """Override: อ่านค่า ADC ดิบ (0-4095)"""
        return self._adc.read()

    def read_voltage(self):
        """อ่านแรงดันพร้อมกรองค่า (Read filtered voltage)"""
        samples = []
        for _ in range(self._samples):
            samples.append(self._adc.read())
            sleep_ms(10)

        # เรียงลำดับและตัดค่าสูง-ต่ำสุดออก
        samples.sort()
        trimmed = samples[2:8]
        avg_adc = sum(trimmed) / len(trimmed)

        return (avg_adc / self.ADC_MAX) * self.ADC_VOLTAGE

    def read(self):
        """อ่านค่า pH พร้อมแรงดัน"""
        voltage = self.read_voltage()
        ph = self._slope * voltage + self._intercept
        return voltage, ph

    def read_ph(self):
        """อ่านเฉพาะค่า pH"""
        _, ph = self.read()
        return ph

    def set_calibration(self, slope, intercept):
        """กำหนดค่าสอบเทียบใหม่"""
        self._slope = slope
        self._intercept = intercept
        self._is_calibrated = True
        print(f"Calibration updated: pH = {slope:.4f} * V + {intercept:.4f}")


# ทดสอบการใช้งาน
if __name__ == "__main__":
    sensor = pHSensor()
    print(f"Sensor: {sensor.name}")
    print(f"Slope: {sensor.slope}")

    for i in range(5):
        voltage, ph = sensor.read()
        print(f"Reading {i+1}: V={voltage:.4f}V, pH={ph:.2f}")
        sleep_ms(1000)
```

---

### ตัวอย่าง 2: Composition - สร้างคลาส Pump

```python
"""
ตัวอย่าง Composition: Pump ประกอบด้วย PWMController
Example Composition: Pump contains PWMController
"""
from machine import Pin, PWM
from time import ticks_us, ticks_diff, sleep_ms


class PWMController:
    """
    คลาสควบคุม PWM
    PWM Controller class
    """

    MAX_DUTY = 1023  # 10-bit PWM

    def __init__(self, pin_number, freq=1000):
        self._pin = Pin(pin_number, Pin.OUT)
        self._pwm = PWM(self._pin, freq=freq)
        self._pwm.duty(0)
        self._current_duty = 0

    @property
    def current_duty(self):
        """Duty cycle ปัจจุบัน (%)"""
        return (self._current_duty / self.MAX_DUTY) * 100

    def set_duty_percent(self, percent):
        """กำหนด duty cycle (0-100%)"""
        percent = max(0, min(100, percent))
        duty_value = int((percent / 100) * self.MAX_DUTY)
        self._pwm.duty(duty_value)
        self._current_duty = duty_value

    def stop(self):
        """หยุด PWM"""
        self._pwm.duty(0)
        self._current_duty = 0

    def deinit(self):
        """ปิดการใช้งาน PWM"""
        self._pwm.duty(0)
        self._pwm.deinit()


class Pump:
    """
    คลาสควบคุมปั๊ม - ใช้ Composition กับ PWMController
    Pump control class - uses Composition with PWMController

    Composition: Pump "has-a" PWMController
    เปรียบเทียบ: ปั๊ม "มี" ตัวควบคุม PWM เป็นส่วนประกอบ

    ตัวอย่างการใช้งาน (Usage):
        >>> pump = Pump()
        >>> pump.start(duty_percent=100)
        >>> sleep_ms(2000)
        >>> result = pump.stop()
        >>> print(f"Volume: {result['volume_ml']:.2f} mL")
    """

    def __init__(self, pin=21, flow_rate=0.2772):
        # Composition: Pump มี PWMController
        self._pwm_controller = PWMController(pin)
        self._flow_rate = flow_rate  # mL/s at 100% duty
        self._is_running = False
        self._start_time = 0
        self._current_duty_percent = 0

        print(f"Pump initialized on GPIO{pin}")
        print(f"Flow rate: {flow_rate} mL/s at 100% duty")

    @property
    def is_running(self):
        """สถานะปั๊ม (Pump status)"""
        return self._is_running

    @property
    def flow_rate(self):
        """อัตราการไหล (Flow rate)"""
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, value):
        """กำหนดอัตราการไหล"""
        if value > 0:
            self._flow_rate = value
        else:
            raise ValueError("Flow rate must be positive")

    def start(self, duty_percent=100):
        """เริ่มปั๊ม (Start pump)"""
        if self._is_running:
            print("Warning: Pump already running")
            return False

        self._pwm_controller.set_duty_percent(duty_percent)
        self._start_time = ticks_us()
        self._current_duty_percent = duty_percent
        self._is_running = True

        print(f"Pump started at {duty_percent}%")
        return True

    def stop(self):
        """หยุดปั๊มและคำนวณปริมาตร (Stop pump and calculate volume)"""
        if not self._is_running:
            return {'elapsed_s': 0, 'volume_ml': 0}

        self._pwm_controller.stop()

        elapsed_us = ticks_diff(ticks_us(), self._start_time)
        elapsed_s = elapsed_us / 1_000_000

        # คำนวณปริมาตร
        effective_flow = self._flow_rate * (self._current_duty_percent / 100)
        volume_ml = effective_flow * elapsed_s

        self._is_running = False

        result = {
            'elapsed_s': elapsed_s,
            'volume_ml': volume_ml,
            'duty_percent': self._current_duty_percent
        }

        print(f"Pump stopped: {elapsed_s:.2f}s, {volume_ml:.3f} mL")
        return result

    def run_for_volume(self, volume_ml, duty_percent=100):
        """ปั๊มจนได้ปริมาตรที่ต้องการ (Pump until target volume)"""
        effective_flow = self._flow_rate * (duty_percent / 100)
        required_time_ms = int((volume_ml / effective_flow) * 1000)

        print(f"Pumping {volume_ml} mL (estimated {required_time_ms/1000:.2f}s)")

        self.start(duty_percent)
        sleep_ms(required_time_ms)
        return self.stop()

    def purge(self, duration_ms=3000):
        """ล้างท่อ (Purge lines)"""
        print(f"Purging for {duration_ms}ms...")
        self.start(100)
        sleep_ms(duration_ms)
        return self.stop()

    def deinit(self):
        """ปิดการใช้งาน"""
        if self._is_running:
            self.stop()
        self._pwm_controller.deinit()


# ทดสอบการใช้งาน
if __name__ == "__main__":
    pump = Pump()

    # ทดสอบ start/stop
    pump.start(50)
    sleep_ms(2000)
    result = pump.stop()
    print(f"Result: {result}")

    # ทดสอบ run_for_volume
    result = pump.run_for_volume(1.0, duty_percent=100)
    print(f"Volume pumped: {result['volume_ml']:.3f} mL")

    pump.deinit()
```

---

### ตัวอย่าง 3: การรวม pHSensor และ Pump สำหรับไทเทรต

```python
"""
ตัวอย่างการรวม pHSensor และ Pump
Example combining pHSensor and Pump for simple titration
"""

class SimpleTitrator:
    """
    ระบบไทเทรตอย่างง่าย - ใช้ Composition
    Simple titration system - uses Composition

    Composition:
        - Titrator "has-a" pHSensor
        - Titrator "has-a" Pump
    """

    def __init__(self, target_ph=7.0):
        # Composition: Titrator มี pHSensor และ Pump
        self._ph_sensor = pHSensor()
        self._pump = Pump()
        self._target_ph = target_ph
        self._data = []

    @property
    def target_ph(self):
        return self._target_ph

    @target_ph.setter
    def target_ph(self, value):
        if 0 <= value <= 14:
            self._target_ph = value
        else:
            raise ValueError("pH must be between 0 and 14")

    def read_ph(self):
        """อ่านค่า pH ปัจจุบัน"""
        voltage, ph = self._ph_sensor.read()
        return ph

    def add_titrant(self, volume_ml):
        """เติมสารไทแทรนต์"""
        result = self._pump.run_for_volume(volume_ml)
        return result['volume_ml']

    def run_simple_titration(self, increment_ml=0.5, max_volume=50):
        """
        รันไทเทรตอย่างง่าย
        Run simple titration
        """
        total_volume = 0
        self._data = []

        print("Starting simple titration...")
        print(f"Target pH: {self._target_ph}")

        while total_volume < max_volume:
            # อ่านค่า pH
            ph = self.read_ph()
            self._data.append({'volume': total_volume, 'ph': ph})

            print(f"Volume: {total_volume:.2f} mL, pH: {ph:.2f}")

            # ตรวจสอบว่าถึง target หรือยัง
            if abs(ph - self._target_ph) < 0.3:
                print(f"Target reached at {total_volume:.2f} mL!")
                break

            # เติมสารไทแทรนต์
            self.add_titrant(increment_ml)
            total_volume += increment_ml

            sleep_ms(2000)  # รอให้ pH เสถียร

        return self._data

    def deinit(self):
        """ปิดการใช้งาน"""
        self._pump.deinit()


# ทดสอบ
if __name__ == "__main__":
    titrator = SimpleTitrator(target_ph=7.0)
    data = titrator.run_simple_titration(increment_ml=0.5, max_volume=10)
    titrator.deinit()
```

---

## แบบฝึกหัด (Exercises)

### แบบฝึกหัดที่ 1: สร้างคลาส TemperatureSensor

สร้างคลาส `TemperatureSensor` ที่สืบทอดจาก `BaseSensor`:

```python
class TemperatureSensor(BaseSensor):
    """
    เซ็นเซอร์อุณหภูมิ DS18B20
    ต้อง implement:
    - __init__() พร้อมเรียก super().__init__()
    - read_raw() - override
    - read_celsius() - อ่านอุณหภูมิเป็นเซลเซียส
    - read_fahrenheit() - อ่านอุณหภูมิเป็นฟาเรนไฮต์
    """
    pass
```

### แบบฝึกหัดที่ 2: เพิ่ม Calibration ให้ pHSensor

เพิ่ม methods สำหรับการสอบเทียบ 3 จุดให้คลาส pHSensor:

```python
def add_calibration_point(self, buffer_ph, voltage):
    """เพิ่มจุดสอบเทียบ"""
    pass

def calculate_calibration(self):
    """คำนวณ slope, intercept, r_squared"""
    pass

def validate_calibration(self):
    """ตรวจสอบว่า R-squared >= 0.99"""
    pass
```

### แบบฝึกหัดที่ 3: สร้าง DataLogger

สร้างคลาส `DataLogger` ที่ใช้ Composition:

```python
class DataLogger:
    """
    บันทึกข้อมูลการทดลอง
    Composition: มี list สำหรับเก็บข้อมูล

    Methods:
    - add_data(volume, ph, temperature)
    - save_to_csv(filename)
    - get_statistics() - คืน mean, std, min, max
    """
    pass
```

---

## การเชื่อมต่อกับ Week 3 (Connection to Week 3)

### Week 3 Preview: Full OOP Modular System

Week 3 จะนำแนวคิดจาก Week 2 มาสร้างระบบที่สมบูรณ์:

```
Week_3/
|
|-- main.py                 # Entry point
|-- config.py               # GPIO และค่าคงที่
|
|-- hardware/               # Hardware Layer (Composition)
|   |-- pump.py             # คลาส Pump (จาก Week 2)
|   |-- ph_sensor.py        # คลาส pHSensor (จาก Week 2)
|   |-- temp_sensor.py      # คลาส TemperatureSensor
|   |-- display.py          # คลาส Display
|   |-- buttons.py          # คลาส Buttons
|
|-- core/                   # Business Logic Layer
|   |-- calibrator.py       # การสอบเทียบ
|   |-- titration.py        # การไทเทรต
|
|-- modes/                  # Mode Layer (Inheritance)
|   |-- base_mode.py        # คลาสแม่ BaseMode
|   |-- mode_calibrate_ph.py    # สืบทอดจาก BaseMode
|   |-- mode_test_ph.py         # สืบทอดจาก BaseMode
|   |-- mode_titration.py       # สืบทอดจาก BaseMode
|
|-- ui/                     # UI Layer
    |-- menu.py             # State Machine
```

### หลักการที่จะเรียนเพิ่มใน Week 3

| หัวข้อ | รายละเอียด |
|--------|-------------|
| **Abstract Base Class** | BaseMode บังคับให้คลาสลูก implement methods |
| **State Machine** | MenuSystem จัดการสถานะของโปรแกรม |
| **Dependency Injection** | ส่ง hardware objects ผ่าน constructor |
| **Modular Design** | แยกโค้ดเป็นโมดูลย่อยๆ ที่จัดการได้ง่าย |

---

## ตารางสรุป OOP Concepts

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
- หลักการ Nernst equation และ pH measurement
- 3-point calibration methodology
- Titration theory and equivalence point detection

### เอกสาร MicroPython
- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 ADC Reference](https://docs.micropython.org/en/latest/esp32/quickref.html#adc-analog-to-digital-conversion)
- [ESP32 PWM Reference](https://docs.micropython.org/en/latest/esp32/quickref.html#pwm-pulse-width-modulation)

### เอกสาร Python OOP
- [Python Classes Tutorial](https://docs.python.org/3/tutorial/classes.html)
- [Property Decorator](https://docs.python.org/3/library/functions.html#property)

---

## ผู้พัฒนา (Developers)

- Hemmawan Saon
- Nuttakit Deemon
- Saowapak Vchirawongkwin
- Sumrit Wacharasindhu
- Viwat Vchirawongkwin

**รายวิชา:** 2302311 Analytical Chemistry Laboratory
**สถาบัน:** Chulalongkorn University

---

## เวอร์ชัน (Version)

**Version 1.0.0** - Week 2: Intermediate OOP

การเรียนรู้หลัก:
- Inheritance และ super()
- Method overriding
- Composition (has-a relationship)
- @property decorator
- Encapsulation กับ private attributes

---

*สร้างเมื่อ: มกราคม 2026*
*อัปเดตล่าสุด: มกราคม 2026*

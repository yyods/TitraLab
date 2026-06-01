# ==============================================================================
# 04_combined_demo.py - สาธิตการรวม OOP Concepts สำหรับระบบไทเทรต
# (Combined Demo: OOP Concepts for Titration System)
# ==============================================================================
# เวลาในการสอน: ~30 นาที (Teaching time: ~30 minutes)
#
# โปรแกรมนี้รวมแนวคิด OOP ทั้งหมดที่เรียนมา
# เพื่อสร้างระบบไทเทรตอย่างง่าย เตรียมพร้อมสำหรับ Week 3
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เห็นการใช้ Inheritance, Composition, และ @property ร่วมกัน
#   2. เข้าใจโครงสร้างระบบที่ใหญ่ขึ้น
#   3. เตรียมพร้อมสำหรับ Week 3 modular system
#
# การเชื่อมโยงกับเคมี (Chemistry Connection):
#   - ระบบไทเทรตประกอบด้วย: หัววัด pH, ปั๊ม, และ display
#   - การวัด pH ใช้สมการ Nernst และ calibration
#   - ปั๊มควบคุมปริมาตรสารไทแทรนต์
#   - รวมกันเพื่อหาจุดสมมูล (Equivalence Point)
#
# ==============================================================================
# ⚠ ความปลอดภัยของแอคชูเอเตอร์ — โปรดอ่าน (ACTUATOR SAFETY — READ FIRST)
# ==============================================================================
# โปรแกรมนี้ขับปั๊ม (GPIO21) ด้วย machine.PWM โดยตรง (raw PWM) ผ่านคลาส Pump.
# This program drives the pump (GPIO21) with raw machine.PWM via the Pump class.
#
# *** RAW PWM ไม่ผ่านตัวจับเวลานิรภัยของเฟิร์มแวร์ (F-40 actuator guard) ***
# Raw PWM BYPASSES the firmware F-40 actuator-guard GPTimer: NO hardware
# max-on-time force-cut. On firmware 0.3.x the run-scoped watchdog is also
# DISABLED (decision 0026/F-156). Supervised / physical-access use ONLY.
# The titration loop polls stop_requested() (app STOP), the run is wrapped in
# try/finally: titrator.cleanup() -> pump.deinit(), and KeyboardInterrupt
# routes to the same OFF path. Last-line stops: BUTTON_3 hold, Ctrl+C, reset.
# (safety-hw ruling R, decision 0027)
# ==============================================================================

from machine import Pin, ADC, PWM
from time import sleep_ms, ticks_us, ticks_diff

# ให้แอป Student/Instructor สั่งหยุดสคริปต์ได้แบบ cooperative (F-149 STOP ladder)
# Let the Student/Instructor app stop this script cooperatively (F-149 STOP).
try:
    from scilabpro import stop_requested
except ImportError:
    stop_requested = None


# ==============================================================================
# ส่วนที่ 1: ทบทวน OOP Concepts (10 นาที)
# Part 1: Review OOP Concepts (10 minutes)
# ==============================================================================

print("=" * 60)
print("สาธิตการรวม OOP Concepts สำหรับระบบไทเทรต")
print("(Combined OOP Demo for Titration System)")
print("=" * 60)

print("""
===== ทบทวน OOP Concepts ที่เรียนมา =====

1. Inheritance (การสืบทอด):
   - class PHSensor(BaseSensor)
   - สืบทอด attributes และ methods
   - Override methods ที่ต้องการ

2. Composition (การประกอบ):
   - Pump "has-a" PWM
   - Titrator "has-a" PHSensor และ Pump
   - ซ่อนความซับซ้อนภายใน

3. @property (Encapsulation):
   - ควบคุมการเข้าถึง attributes
   - เพิ่ม validation
   - Computed properties

===== โครงสร้างระบบไทเทรต =====

    SimpleTitrator
         |
         |--- pH Sensor (Inheritance from BaseSensor)
         |       |--- slope, intercept (@property)
         |       |--- read_ph() method
         |
         |--- Pump (Composition with PWM)
         |       |--- flow_rate (@property)
         |       |--- start(), stop() methods
         |
         |--- Data storage (list)
                 |--- volume, pH pairs
""")


# ==============================================================================
# Base Classes และ Helper Classes
# ==============================================================================

class BaseSensor:
    """คลาสพื้นฐานสำหรับเซ็นเซอร์ (Base Sensor Class)"""

    def __init__(self, name, pin):
        self._name = name
        self._pin_number = pin
        self._is_initialized = False
        self._read_count = 0
        print(f"[{name}] สร้างที่ GPIO{pin}")

    @property
    def name(self):
        return self._name

    @property
    def pin_number(self):
        return self._pin_number

    @property
    def is_initialized(self):
        return self._is_initialized

    @property
    def read_count(self):
        return self._read_count

    def read(self):
        raise NotImplementedError("คลาสลูกต้อง implement read()")

    def log(self, message):
        print(f"[{self._name}] {message}")


class PHSensor(BaseSensor):
    """
    เซ็นเซอร์ pH (สาธิต Inheritance และ @property)

    Inheritance: สืบทอดจาก BaseSensor
    @property: slope, intercept, calibration_equation
    """

    ADC_MAX = 4095
    ADC_VREF = 3.3

    def __init__(self, pin=25, slope=-5.79, intercept=16.77):
        # เรียก parent constructor
        super().__init__("pH Sensor", pin)

        # Attributes เฉพาะ (Private)
        self._slope = slope
        self._intercept = intercept
        self._adc = None
        self._last_voltage = None
        self._last_ph = None

        self.log(f"สมการ: {self.calibration_equation}")

    # ===== Properties =====

    @property
    def slope(self):
        return self._slope

    @slope.setter
    def slope(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("slope ต้องเป็นตัวเลข")
        if value > 0:
            self.log("คำเตือน: slope ควรเป็นค่าลบ")
        self._slope = value

    @property
    def intercept(self):
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("intercept ต้องเป็นตัวเลข")
        self._intercept = value

    @property
    def calibration_equation(self):
        """Computed property"""
        return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"

    @property
    def last_ph(self):
        return self._last_ph

    # ===== Methods =====

    def init(self):
        """เริ่มต้น ADC"""
        try:
            self._adc = ADC(Pin(self._pin_number))
            self._adc.atten(ADC.ATTN_11DB)
            self._is_initialized = True
            self.log("เริ่มต้น ADC สำเร็จ")
            return True
        except Exception as e:
            self.log(f"เริ่มต้นล้มเหลว: {e}")
            return False

    def read(self):
        """Override read() จาก BaseSensor"""
        if not self._is_initialized:
            return None

        # อ่านและกรองค่า
        samples = []
        for _ in range(10):
            samples.append(self._adc.read())
            sleep_ms(5)

        samples.sort()
        avg = sum(samples[2:8]) / 6

        voltage = (avg / self.ADC_MAX) * self.ADC_VREF
        ph = self._slope * voltage + self._intercept

        self._last_voltage = voltage
        self._last_ph = ph
        self._read_count += 1

        return ph

    def read_with_voltage(self):
        """อ่านทั้ง voltage และ pH"""
        ph = self.read()
        return self._last_voltage, ph


class Pump:
    """
    คลาสควบคุมปั๊ม (สาธิต Composition และ @property)

    Composition: มี PWM object ภายใน
    @property: flow_rate, is_running
    """

    PWM_MAX_DUTY = 1023

    def __init__(self, pin=21, flow_rate=0.2772):
        self._pin_number = pin
        self._flow_rate = flow_rate

        # Composition: Pump "has-a" PWM
        self._pin = Pin(pin, Pin.OUT)
        self._pwm = PWM(self._pin, freq=1000)
        self._pwm.duty(0)

        self._is_running = False
        self._start_time = 0
        self._current_duty = 0

        print(f"[Pump] สร้างที่ GPIO{pin}")

    @property
    def flow_rate(self):
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, value):
        if value <= 0:
            raise ValueError("flow_rate ต้อง > 0")
        self._flow_rate = value

    @property
    def is_running(self):
        return self._is_running

    def start(self, duty_percent=100):
        """เริ่มปั๊ม"""
        if self._is_running:
            return False
        duty = int((duty_percent / 100) * self.PWM_MAX_DUTY)
        self._pwm.duty(duty)
        self._current_duty = duty_percent
        self._start_time = ticks_us()
        self._is_running = True
        return True

    def stop(self):
        """หยุดปั๊ม"""
        self._pwm.duty(0)
        elapsed_us = ticks_diff(ticks_us(), self._start_time)
        elapsed_s = elapsed_us / 1_000_000
        volume = self._flow_rate * (self._current_duty / 100) * elapsed_s
        self._is_running = False
        return {'time_s': elapsed_s, 'volume_ml': volume}

    def run_for_volume(self, volume_ml, duty_percent=100):
        """ปั๊มจนได้ปริมาตรที่ต้องการ"""
        time_s = volume_ml / (self._flow_rate * duty_percent / 100)
        time_ms = int(time_s * 1000)
        self.start(duty_percent)
        sleep_ms(time_ms)
        return self.stop()

    def deinit(self):
        """ปิดการใช้งาน"""
        if self._is_running:
            self.stop()
        self._pwm.duty(0)
        self._pwm.deinit()


# ==============================================================================
# ส่วนที่ 2: SimpleTitrator - รวม Concepts ทั้งหมด
# Part 2: SimpleTitrator - Combining All Concepts
# ==============================================================================

class SimpleTitrator:
    """
    ระบบไทเทรตอย่างง่าย - รวม Inheritance, Composition, และ @property

    ===== โครงสร้าง (Structure) =====

    SimpleTitrator
         |
         |--- Composition: มี PHSensor
         |--- Composition: มี Pump
         |--- @property: target_ph, total_volume
         |--- Methods: run_titration()

    ===== ตัวอย่างการใช้งาน =====

        titrator = SimpleTitrator(target_ph=7.0)
        titrator.init()

        # รันไทเทรต
        data = titrator.run_titration(increment_ml=0.5, max_volume=10)

        # แสดงผลลัพธ์
        print(f"ปริมาตรรวม: {titrator.total_volume} mL")

        titrator.cleanup()
    """

    def __init__(self, target_ph=7.0, ph_tolerance=0.5):
        """
        สร้าง SimpleTitrator

        Args:
            target_ph (float): ค่า pH เป้าหมาย
            ph_tolerance (float): ค่าความคลาดเคลื่อนที่ยอมรับได้
        """
        # ===== Composition =====
        # SimpleTitrator "has-a" PHSensor
        self._ph_sensor = PHSensor()

        # SimpleTitrator "has-a" Pump
        self._pump = Pump()

        # Private attributes
        self._target_ph = target_ph
        self._ph_tolerance = ph_tolerance
        self._total_volume = 0.0
        self._data = []
        self._is_initialized = False

        print("\n[Titrator] สร้างระบบไทเทรต")
        print(f"[Titrator] pH เป้าหมาย: {target_ph}")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def target_ph(self):
        """ค่า pH เป้าหมาย"""
        return self._target_ph

    @target_ph.setter
    def target_ph(self, value):
        """กำหนดค่า pH เป้าหมายพร้อม validation"""
        if not 0 <= value <= 14:
            raise ValueError("pH ต้องอยู่ในช่วง 0-14")
        self._target_ph = value
        print(f"[Titrator] pH เป้าหมายใหม่: {value}")

    @property
    def total_volume(self):
        """ปริมาตรรวมที่ใช้ไป (Read-only)"""
        return self._total_volume

    @property
    def data(self):
        """ข้อมูลการทดลอง (Read-only)"""
        return self._data.copy()

    @property
    def is_initialized(self):
        """สถานะการเริ่มต้น"""
        return self._is_initialized

    @property
    def current_ph(self):
        """ค่า pH ปัจจุบัน (Computed property)"""
        return self._ph_sensor.last_ph

    # =========================================================================
    # Methods
    # =========================================================================

    def init(self):
        """เริ่มต้นระบบ"""
        print("\n[Titrator] กำลังเริ่มต้นระบบ...")

        if not self._ph_sensor.init():
            print("[Titrator] เริ่มต้น pH sensor ล้มเหลว")
            return False

        self._is_initialized = True
        print("[Titrator] เริ่มต้นระบบสำเร็จ")
        return True

    def read_ph(self):
        """อ่านค่า pH ปัจจุบัน"""
        if not self._is_initialized:
            print("[Titrator] ยังไม่ได้เริ่มต้นระบบ")
            return None
        return self._ph_sensor.read()

    def add_titrant(self, volume_ml):
        """เติมสารไทแทรนต์"""
        result = self._pump.run_for_volume(volume_ml)
        actual_volume = result['volume_ml']
        self._total_volume += actual_volume
        return actual_volume

    def run_titration(self, increment_ml=0.5, max_volume=20.0, stabilize_ms=1000):
        """
        รันไทเทรตอัตโนมัติ

        Args:
            increment_ml (float): ปริมาตรที่เติมในแต่ละครั้ง
            max_volume (float): ปริมาตรสูงสุด
            stabilize_ms (int): เวลารอให้ pH เสถียร (ms)

        Returns:
            list: ข้อมูล [(volume, pH), ...]
        """
        if not self._is_initialized:
            print("[Titrator] กรุณาเรียก init() ก่อน")
            return []

        print("\n" + "=" * 50)
        print(f"เริ่มไทเทรต - pH เป้าหมาย: {self._target_ph}")
        print(f"เติมครั้งละ: {increment_ml} mL")
        print("=" * 50)

        self._data = []
        self._total_volume = 0.0

        while self._total_volume < max_volume:
            # นิรภัย: ถ้าแอปสั่ง STOP ระหว่างไทเทรต ให้หยุดก่อนเติมสารรอบถัดไป
            # Safety: if the app requests STOP, halt before the next titrant burst.
            # cleanup() ใน finally จะปิดปั๊ม (pump.deinit) เสมอ
            if stop_requested is not None and stop_requested():
                self._pump.deinit()
                print("\nได้รับคำสั่งหยุดจากแอป — หยุดไทเทรตและปิดปั๊ม (Stop requested)")
                break

            # อ่านค่า pH
            ph = self.read_ph()
            if ph is None:
                break

            # บันทึกข้อมูล
            self._data.append({
                'volume': round(self._total_volume, 2),
                'ph': round(ph, 2)
            })

            print(f"V = {self._total_volume:6.2f} mL | pH = {ph:5.2f}")

            # ตรวจสอบว่าถึง target หรือยัง
            if abs(ph - self._target_ph) < self._ph_tolerance:
                print(f"\n*** ถึง pH เป้าหมายที่ {self._total_volume:.2f} mL! ***")
                break

            # เติมสารไทแทรนต์
            self.add_titrant(increment_ml)

            # รอให้ pH เสถียร
            sleep_ms(stabilize_ms)

        print("\n" + "=" * 50)
        print("ไทเทรตเสร็จสิ้น")
        print(f"ปริมาตรรวม: {self._total_volume:.2f} mL")
        print(f"pH สุดท้าย: {self.current_ph:.2f}")
        print("=" * 50)

        return self._data

    def get_statistics(self):
        """รับสถิติของการทดลอง"""
        if not self._data:
            return None

        ph_values = [d['ph'] for d in self._data]
        return {
            'total_volume': self._total_volume,
            'readings': len(self._data),
            'ph_min': min(ph_values),
            'ph_max': max(ph_values),
            'ph_final': ph_values[-1] if ph_values else None
        }

    def cleanup(self):
        """ทำความสะอาดทรัพยากร"""
        print("\n[Titrator] กำลังปิดระบบ...")
        self._pump.deinit()
        print("[Titrator] ปิดระบบเรียบร้อย")


# ==============================================================================
# ส่วนที่ 3: ทดสอบระบบ
# Part 3: Test the System
# ==============================================================================

print("\n" + "=" * 60)
print("ส่วนที่ 2: ทดสอบ SimpleTitrator")
print("Part 2: Test SimpleTitrator")
print("=" * 60)

# สร้างระบบไทเทรต
titrator = SimpleTitrator(target_ph=7.0)

try:
    # เริ่มต้นระบบ
    if titrator.init():
        # ทดสอบ properties
        print(f"\n--- Properties ---")
        print(f"target_ph: {titrator.target_ph}")
        print(f"total_volume: {titrator.total_volume}")
        print(f"is_initialized: {titrator.is_initialized}")

        # รันไทเทรต (จำกัดปริมาตรสำหรับการทดสอบ)
        print("\n--- รันไทเทรต ---")
        data = titrator.run_titration(
            increment_ml=0.3,
            max_volume=2.0,
            stabilize_ms=500
        )

        # แสดงผลลัพธ์
        print("\n--- ข้อมูลที่บันทึก ---")
        for point in data:
            print(f"  V={point['volume']:5.2f} mL, pH={point['ph']:5.2f}")

        # สถิติ
        stats = titrator.get_statistics()
        if stats:
            print("\n--- สถิติ ---")
            print(f"  ปริมาตรรวม: {stats['total_volume']:.2f} mL")
            print(f"  จำนวนการอ่าน: {stats['readings']}")
            print(f"  pH ต่ำสุด: {stats['ph_min']:.2f}")
            print(f"  pH สูงสุด: {stats['ph_max']:.2f}")
            print(f"  pH สุดท้าย: {stats['ph_final']:.2f}")

except KeyboardInterrupt:
    print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

except Exception as e:
    print(f"\nข้อผิดพลาด (Error): {e}")

finally:
    titrator.cleanup()


# ==============================================================================
# ส่วนที่ 4: สรุปและเชื่อมโยงกับ Week 3
# Part 4: Summary and Week 3 Preview
# ==============================================================================

print("\n" + "=" * 60)
print("สรุปและเตรียมพร้อมสำหรับ Week 3")
print("(Summary and Week 3 Preview)")
print("=" * 60)

print("""
===== สิ่งที่เรียนรู้ใน Week 2 =====

1. Inheritance (การสืบทอด):
   - PHSensor สืบทอดจาก BaseSensor
   - ใช้ super().__init__() เรียก parent constructor
   - Override methods ที่ต้องการ

2. Composition (การประกอบ):
   - Pump มี PWM object ภายใน
   - SimpleTitrator มี PHSensor และ Pump
   - ซ่อนความซับซ้อนจากผู้ใช้

3. @property และ Encapsulation:
   - ควบคุมการเข้าถึง attributes
   - Validation ใน setter
   - Computed properties

===== Week 3 Preview =====

Week 3 จะนำแนวคิดเหล่านี้มาสร้างระบบที่สมบูรณ์:

Week_3/
|-- main.py                 # Entry point
|-- config.py               # GPIO และค่าคงที่
|
|-- hardware/               # Hardware Layer
|   |-- pump.py             # คลาส Pump (Composition)
|   |-- ph_sensor.py        # คลาส PHSensor (Inheritance)
|   |-- temp_sensor.py      # คลาส TempSensor (Inheritance)
|   |-- display.py          # คลาส Display
|
|-- core/                   # Business Logic
|   |-- calibrator.py       # การสอบเทียบ
|   |-- titration.py        # การไทเทรต
|
|-- modes/                  # Mode Layer (Inheritance)
|   |-- base_mode.py        # คลาสแม่ BaseMode
|   |-- mode_calibrate.py   # สืบทอดจาก BaseMode
|   |-- mode_titration.py   # สืบทอดจาก BaseMode
|
|-- ui/                     # UI Layer
    |-- menu.py             # State Machine

หลักการเพิ่มเติมใน Week 3:
- Abstract Base Class
- State Machine
- Dependency Injection
- Modular Design
""")

print("=" * 60)
print("จบ Week 2: Intermediate OOP")
print("พร้อมสำหรับ Week 3: Full Modular System!")
print("=" * 60)

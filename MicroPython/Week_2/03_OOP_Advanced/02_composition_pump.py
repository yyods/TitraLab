# ==============================================================================
# 02_composition_pump.py - พื้นฐาน Composition (Composition Basics)
# ==============================================================================
# เวลาในการสอน: ~30-35 นาที (Teaching time: ~30-35 minutes)
#
# โปรแกรมนี้สอน Composition สำหรับนิสิตเคมี
# This program teaches Composition for chemistry students
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Composition: "has-a" relationship
#   2. เปรียบเทียบ Composition vs Inheritance
#   3. ดูประโยชน์ของ Encapsulation ผ่าน Composition
#   4. นำไปประยุกต์ใช้กับการควบคุมปั๊มไทแทรนต์
#
# การเชื่อมโยงกับเคมี (Chemistry Connection):
#   - ปั๊มไทแทรนต์ "ประกอบด้วย" มอเตอร์และตัวควบคุม PWM
#   - ระบบไทเทรต "ประกอบด้วย" หัววัด pH, ปั๊ม, และจอแสดงผล
#   - เหมือน "pH Meter" ที่ประกอบด้วย electrode, display, และ processor
#
# หมายเหตุ: Class Methods และ Static Methods อยู่ในไฟล์เสริม
#           extras/class_static_methods.py
# Note: Class Methods and Static Methods are in supplementary file
#       extras/class_static_methods.py
#
# ==============================================================================

from machine import Pin, PWM
from time import sleep_ms, ticks_us, ticks_diff


# ==============================================================================
# ส่วนที่ 1: แนวคิด Composition (10 นาที)
# Part 1: Composition Concept (10 minutes)
# ==============================================================================

print("=" * 60)
print("ส่วนที่ 1: แนวคิด Composition")
print("Part 1: Composition Concept")
print("=" * 60)

print("""
===== Composition คืออะไร? (What is Composition?) =====

Composition คือการออกแบบที่ class หนึ่ง "มี" (has-a) object
ของ class อื่นเป็น attribute ภายใน

ตัวอย่าง:
  - Pump "has-a" PWM object
  - Buzzer "has-a" PWM object
  - Titrator "has-a" Pump และ "has-a" pHSensor

===== เปรียบเทียบ Inheritance vs Composition =====

Inheritance ("is-a"):
  - PHSensor IS-A Sensor (เป็นเซ็นเซอร์ชนิดหนึ่ง)
  - สืบทอดคุณสมบัติจากคลาสแม่
  - สายสัมพันธ์แน่น (tight coupling)

Composition ("has-a"):
  - Pump HAS-A PWM (มี PWM เป็นส่วนประกอบ)
  - มี object เป็น component
  - สายสัมพันธ์หลวม (loose coupling)

===== เมื่อไหร่ใช้อะไร? =====

ใช้ Inheritance เมื่อ:
  - A "เป็นชนิดหนึ่งของ" B (PHSensor is-a Sensor)

ใช้ Composition เมื่อ:
  - A "มี" B เป็นส่วนประกอบ (Pump has-a PWM)
  - ต้องการ flexibility มากกว่า

Rule of Thumb:
  "Favor composition over inheritance"
  (เลือก composition ก่อน ถ้าไม่แน่ใจ)
""")


# ==============================================================================
# ส่วนที่ 2: ตัวอย่าง Composition กับ Pump (15-20 นาที)
# Part 2: Composition Example with Pump (15-20 minutes)
# ==============================================================================

print("\n" + "=" * 60)
print("ส่วนที่ 2: ตัวอย่าง Composition กับ Pump")
print("Part 2: Composition Example with Pump")
print("=" * 60)


class Pump:
    """
    คลาสควบคุมปั๊มด้วย PWM (Pump control class using PWM)

    ===== Composition Design =====

    Pump "has-a" PWM object และ "has-a" Pin object

    โครงสร้างภายใน:
        Pump
         |--- _pin (Pin object)     <-- Composition
         |--- _pwm (PWM object)     <-- Composition
         |--- _flow_rate (float)
         |--- methods...

    ===== ข้อดีของ Composition =====

    1. Encapsulation: ซ่อน PWM complexity
       แทนที่: pwm.duty(int((percent/100)*1023))
       ใช้แค่:  pump.start(50)

    2. Flexibility: เปลี่ยน implementation ได้
       เช่น เปลี่ยนจาก PWM เป็น DAC โดยไม่ต้องแก้โค้ดภายนอก

    3. Single Responsibility:
       Pump รับผิดชอบเฉพาะการควบคุมปั๊ม
       ไม่ต้องรู้รายละเอียดของ PWM

    ===== ตัวอย่างการใช้งาน =====

        pump = Pump()
        pump.start(100)  # เริ่มที่ 100%
        sleep_ms(2000)
        result = pump.stop()
        print(f"ปริมาตร: {result['volume_ml']:.2f} mL")
    """

    # Class constants - ค่าคงที่ระดับ class
    PUMP_PIN = 21               # GPIO21 สำหรับปั๊ม (Pump GPIO)
    PWM_FREQUENCY = 1000        # ความถี่ PWM (PWM frequency)
    PWM_MAX_DUTY = 1023         # 10-bit max duty
    DEFAULT_FLOW_RATE = 0.2772  # mL/s ที่ 100% duty

    def __init__(self, pin=None, flow_rate=None):
        """
        Constructor - สร้าง Pump object พร้อม PWM ภายใน

        ===== Composition ใน Constructor =====

        ที่นี่เราสร้าง objects ที่ Pump "มี" (has-a):
        1. สร้าง Pin object
        2. สร้าง PWM object โดยใช้ Pin object

        นี่คือ "composing" objects เข้าด้วยกัน

        Args:
            pin (int): GPIO pin สำหรับปั๊ม (ค่าเริ่มต้น: 21)
            flow_rate (float): อัตราการไหลที่ 100% (mL/s)
        """
        # กำหนดค่า pin และ flow_rate
        self._pin_number = pin if pin is not None else self.PUMP_PIN
        self._flow_rate = flow_rate if flow_rate is not None else self.DEFAULT_FLOW_RATE

        # ===== Composition: สร้าง Pin และ PWM objects =====
        # Pump "has-a" Pin object
        self._pin = Pin(self._pin_number, Pin.OUT)

        # Pump "has-a" PWM object (สร้างจาก Pin)
        self._pwm = PWM(self._pin, freq=self.PWM_FREQUENCY)
        self._pwm.duty(0)  # เริ่มต้นปิดปั๊ม (Start with pump off)

        # State variables - ตัวแปรสถานะ
        self._is_running = False
        self._current_duty = 0
        self._start_time = 0

        print(f"[Pump] สร้างปั๊มที่ GPIO{self._pin_number}")
        print(f"[Pump] อัตราการไหล: {self._flow_rate:.4f} mL/s")

    # =========================================================================
    # Properties - Encapsulation ด้วย @property
    # =========================================================================

    @property
    def is_running(self):
        """สถานะการทำงานของปั๊ม (Pump running status) - Read-only"""
        return self._is_running

    @property
    def flow_rate(self):
        """อัตราการไหล (Flow rate) - Read-write"""
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, value):
        """กำหนดอัตราการไหลใหม่พร้อม validation"""
        if value <= 0:
            raise ValueError("อัตราการไหลต้อง > 0 (Flow rate must be > 0)")
        self._flow_rate = value
        print(f"[Pump] อัตราการไหลใหม่: {value:.4f} mL/s")

    @property
    def pin_number(self):
        """หมายเลข GPIO pin - Read-only"""
        return self._pin_number

    # =========================================================================
    # Public Methods - การควบคุมปั๊ม
    # =========================================================================

    def start(self, duty_percent=100):
        """
        เริ่มทำงานปั๊ม (Start the pump)

        ===== Encapsulation ของ PWM =====

        ผู้ใช้ไม่จำเป็นต้องรู้ว่าภายในใช้ PWM
        แค่เรียก start(50) สำหรับ 50% duty cycle
        Pump class จัดการ PWM ให้เอง

        Args:
            duty_percent (float): Duty cycle 0-100%

        Returns:
            bool: True ถ้าเริ่มสำเร็จ
        """
        if self._is_running:
            print("[Pump] คำเตือน: ปั๊มกำลังทำงานอยู่แล้ว")
            return False

        # แปลงเปอร์เซ็นต์เป็น duty value
        duty_percent = max(0, min(100, duty_percent))
        duty_value = int((duty_percent / 100) * self.PWM_MAX_DUTY)

        # กำหนดให้ PWM (ซ่อนความซับซ้อนนี้จากผู้ใช้)
        self._pwm.duty(duty_value)

        # อัปเดต state
        self._current_duty = duty_percent
        self._start_time = ticks_us()
        self._is_running = True

        print(f"[Pump] เริ่มปั๊มที่ {duty_percent}%")
        return True

    def stop(self):
        """
        หยุดปั๊มและคำนวณเวลา/ปริมาตร (Stop pump and calculate time/volume)

        Returns:
            dict: ข้อมูลการทำงาน
        """
        if not self._is_running:
            print("[Pump] คำเตือน: ปั๊มไม่ได้ทำงาน")
            return {'elapsed_s': 0, 'volume_ml': 0, 'duty_percent': 0}

        # หยุด PWM
        self._pwm.duty(0)

        # คำนวณเวลา
        elapsed_us = ticks_diff(ticks_us(), self._start_time)
        elapsed_s = elapsed_us / 1_000_000

        # คำนวณปริมาตร (สมมติ flow rate เป็นสัดส่วนกับ duty)
        effective_flow = self._flow_rate * (self._current_duty / 100)
        volume_ml = effective_flow * elapsed_s

        # อัปเดต state
        self._is_running = False

        result = {
            'elapsed_s': elapsed_s,
            'volume_ml': volume_ml,
            'duty_percent': self._current_duty
        }

        print(f"[Pump] หยุดปั๊ม: {elapsed_s:.2f}s, {volume_ml:.3f} mL")
        self._current_duty = 0

        return result

    def run_for_time(self, time_ms, duty_percent=100):
        """
        ปั๊มตามเวลาที่กำหนด (Pump for specified time)

        Args:
            time_ms (int): เวลาในมิลลิวินาที
            duty_percent (float): Duty cycle 0-100%

        Returns:
            dict: ข้อมูลการทำงาน
        """
        print(f"[Pump] ปั๊ม {time_ms} ms ที่ {duty_percent}%")
        self.start(duty_percent)
        sleep_ms(time_ms)
        return self.stop()

    def deinit(self):
        """
        ปิดการใช้งาน PWM และคืนทรัพยากร (Deinitialize PWM)

        ===== Resource Management =====

        เมื่อไม่ใช้ Pump แล้ว ต้อง deinit เพื่อคืนทรัพยากร
        โดยเฉพาะ PWM ที่ต้อง deinit ก่อน reuse

        ควรเรียกใน finally block:
            pump = Pump()
            try:
                pump.start(100)
                sleep_ms(1000)
                pump.stop()
            finally:
                pump.deinit()
        """
        try:
            if self._is_running:
                self.stop()
            self._pwm.duty(0)
            self._pwm.deinit()
            print(f"[Pump] ปิดการใช้งาน GPIO{self._pin_number}")
        except Exception as e:
            print(f"[Pump] Error deinit: {e}")

    def __repr__(self):
        """แสดงข้อมูล object สำหรับ debugging"""
        return f"Pump(pin={self._pin_number}, running={self._is_running})"


# ==============================================================================
# ส่วนที่ 3: ทดสอบการใช้งาน Pump (5-10 นาที)
# Part 3: Testing Pump Usage (5-10 minutes)
# ==============================================================================

print("\n" + "=" * 60)
print("ส่วนที่ 3: ทดสอบการใช้งาน Pump")
print("Part 3: Testing Pump Usage")
print("=" * 60)

print("\n--- ทดสอบ Pump ---")

pump = Pump()
print(f"\nrepr: {repr(pump)}")
print(f"pin_number: {pump.pin_number}")
print(f"flow_rate: {pump.flow_rate}")
print(f"is_running: {pump.is_running}")

try:
    # ทดสอบ start/stop
    print("\n--- ทดสอบ start/stop ---")
    pump.start(50)
    print(f"is_running: {pump.is_running}")
    sleep_ms(1000)
    result = pump.stop()
    print(f"ผลลัพธ์: {result}")

    # ทดสอบ run_for_time
    print("\n--- ทดสอบ run_for_time ---")
    result = pump.run_for_time(500, 100)
    print(f"ผลลัพธ์: {result}")

finally:
    pump.deinit()


# ==============================================================================
# ส่วนที่ 4: สรุป
# Part 4: Summary
# ==============================================================================

print("\n" + "=" * 60)
print("สรุป (Summary)")
print("=" * 60)

print("""
สิ่งที่เรียนรู้ในบทนี้:

1. Composition ("has-a" relationship):
   - Class หนึ่งมี object ของ class อื่นเป็น attribute
   - Pump "has-a" PWM object
   - ซ่อนความซับซ้อนภายใน (Encapsulation)

2. เปรียบเทียบ Inheritance vs Composition:
   - Inheritance: PHSensor "is-a" Sensor
   - Composition: Pump "has-a" PWM
   - "Favor composition over inheritance"

3. ข้อดีของ Composition:
   - Encapsulation: ซ่อนรายละเอียดภายใน
   - Flexibility: เปลี่ยน implementation ได้ง่าย
   - Loose coupling: ลดการพึ่งพาระหว่าง class

4. Resource Management:
   - ใช้ deinit() เพื่อคืนทรัพยากร
   - ใส่ใน finally block เสมอ

การเชื่อมโยงกับเคมี:
   - Pump = ปั๊มไทแทรนต์
   - PWM = การควบคุมความเร็วมอเตอร์
   - flow_rate = อัตราการไหลจาก calibration
   - ใช้ควบคุมการเติมสารไทแทรนต์อย่างแม่นยำ
""")

print("=" * 60)
print("จบบทเรียน Composition Basics")
print("(End of Composition Basics)")
print("=" * 60)

# ==============================================================================
# เนื้อหาเพิ่มเติม (Additional Content)
# ==============================================================================
print("""
===== เนื้อหาเสริม (Supplementary Material) =====

Class Methods และ Static Methods อยู่ในไฟล์เสริม:
    extras/class_static_methods.py

เนื้อหาที่ครอบคลุม:
    - @classmethod: Factory methods และ convenience methods
    - @staticmethod: Utility functions
    - ตัวอย่าง Buzzer class พร้อมทั้ง 3 ประเภทของ method

เวลาเพิ่มเติม: ~20-30 นาที
""")

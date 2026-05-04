# ==============================================================================
# pump.py - คลาสควบคุมปั๊มด้วย Composition
# (Pump Control Class using Composition)
# ==============================================================================
# โมดูลนี้สาธิต Composition: Pump class มี PWM object อยู่ภายใน
# This module demonstrates Composition: Pump class contains a PWM object
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Composition: "has-a" relationship
#   2. เปรียบเทียบ Composition vs Inheritance
#   3. Encapsulation: ซ่อน PWM object ภายใน Pump class
#   4. ใช้ @property สำหรับ is_running, flow_rate, duty_percent
#   5. Resource management: __del__, deinit()
#
# ===== Composition vs Inheritance =====
#
# Inheritance ("is-a"):
#   - PHSensor "is-a" BaseSensor
#   - TempSensor "is-a" BaseSensor
#   - Child class สืบทอดคุณสมบัติจาก Parent
#
# Composition ("has-a"):
#   - Pump "has-a" PWM object
#   - Pump "has-a" Pin object
#   - Class หนึ่งมีอีก class เป็น attribute
#
# ข้อดีของ Composition:
#   1. Loose coupling - เปลี่ยน implementation ง่าย
#   2. ยืดหยุ่นกว่า - สามารถเปลี่ยน component ได้ runtime
#   3. ง่ายต่อการทดสอบ - mock objects ได้ง่าย
#
# ความสำคัญในการไทเทรต (Importance in Titration):
#   - ควบคุมปริมาณสารไทแทรนต์อย่างแม่นยำ
#   - ปรับความเร็วตามระยะห่างจากจุดสมมูล
#   - คำนวณปริมาตรจากเวลาและอัตราการไหล
#
# Hardware Configuration:
#   - GPIO 21: Pump (PWM output)
#
# ==============================================================================

from machine import Pin, PWM
from time import ticks_us, ticks_diff, sleep_ms


# ==============================================================================
# ค่าคงที่สำหรับ Pump (Pump Constants)
# ==============================================================================
PUMP_PIN = 21                      # GPIO21 สำหรับปั๊ม
PWM_FREQUENCY = 1000               # ความถี่ PWM 1000 Hz
PWM_MAX_DUTY = 1023                # 10-bit PWM max value
PWM_MIN_DUTY = 0                   # PWM min value
DEFAULT_FLOW_RATE = 0.2772         # อัตราการไหลเริ่มต้น (mL/s) ที่ 100% duty


class Pump:
    """
    คลาสควบคุมปั๊มด้วย PWM โดยใช้ Composition
    (Pump control class using PWM with Composition design pattern)

    ===== Composition (การประกอบ) =====

    Composition คือการออกแบบที่ class หนึ่ง "มี" (has-a) object ของ class อื่น
    เป็น attribute ภายใน

    ในที่นี้:
    - Pump "has-a" PWM object  (self._pwm)
    - Pump "has-a" Pin object  (self._pin)

    โครงสร้าง:
        Pump
         |--- _pin (Pin object)
         |--- _pwm (PWM object)
         |--- _flow_rate (float)
         |--- methods...

    ข้อดีของ Composition:
    1. Encapsulation: ซ่อน PWM complexity จากผู้ใช้
       แทนที่จะต้อง: pwm.duty(int((percent/100)*1023))
       ใช้แค่: pump.start(50)  # 50%

    2. Flexibility: เปลี่ยน implementation ได้โดยไม่กระทบภายนอก
       เช่น เปลี่ยนจาก PWM เป็น DAC โดยไม่ต้องแก้โค้ดที่ใช้งาน

    3. Single Responsibility: Pump รับผิดชอบเฉพาะการควบคุมปั๊ม
       ไม่ต้องรู้รายละเอียดของ PWM

    ===== ตัวอย่างการใช้งาน (Usage Example) =====

        # สร้าง pump object
        pump = Pump()

        # เริ่มปั๊มที่ 100% duty cycle
        pump.start(duty_percent=100)

        # รอ 2 วินาที
        sleep(2)

        # หยุดปั๊มและรับข้อมูลการทำงาน
        result = pump.stop()
        print(f"เวลา: {result['elapsed_time_s']:.2f} s")
        print(f"ปริมาตร: {result['volume_ml']:.3f} mL")

        # ปั๊มปริมาตรที่กำหนด
        pump.run_for_volume(5.0)  # ปั๊ม 5 mL

        # ทำความสะอาดท่อ
        pump.purge(duration_ms=3000)

        # ปิดการใช้งาน
        pump.deinit()

    Attributes:
        _pin (Pin): Pin object สำหรับ GPIO (private - Composition)
        _pwm (PWM): PWM object สำหรับควบคุมความเร็ว (private - Composition)
        _flow_rate (float): อัตราการไหลที่ 100% duty (mL/s) (private)
        _is_running (bool): สถานะการทำงาน (private)
        _current_duty_percent (float): Duty cycle ปัจจุบัน (private)
        _start_time_us (int): เวลาเริ่มต้น (microseconds) (private)
    """

    def __init__(self, pin=None, freq=None, flow_rate=None):
        """
        Constructor - สร้าง Pump object พร้อม PWM ภายใน

        ===== Composition ใน Constructor =====

        ใน constructor เราสร้าง objects ที่ Pump "มี" (has-a):
        1. สร้าง Pin object
        2. สร้าง PWM object โดยใช้ Pin object

        นี่คือ "composing" objects เข้าด้วยกัน

        Args:
            pin (int): GPIO pin สำหรับปั๊ม (ค่าเริ่มต้น: GPIO21)
            freq (int): ความถี่ PWM (Hz) (ค่าเริ่มต้น: 1000)
            flow_rate (float): อัตราการไหลที่ 100% (mL/s)
        """
        # กำหนดค่าเริ่มต้น (Set default values)
        self._pin_number = pin if pin is not None else PUMP_PIN
        self._freq = freq if freq is not None else PWM_FREQUENCY
        self._flow_rate = flow_rate if flow_rate is not None else DEFAULT_FLOW_RATE

        # ===== Composition: สร้าง Pin และ PWM objects =====
        # Pump "has-a" Pin object
        self._pin = Pin(self._pin_number, Pin.OUT)

        # Pump "has-a" PWM object (สร้างจาก Pin)
        self._pwm = PWM(self._pin, freq=self._freq)
        self._pwm.duty(PWM_MIN_DUTY)  # เริ่มต้นปิดปั๊ม

        # State variables
        self._is_running = False
        self._current_duty_percent = 0
        self._start_time_us = 0
        self._last_stop_time_us = 0
        self._total_run_time_us = 0

        print(f"[Pump] สร้างปั๊มที่ GPIO{self._pin_number}, freq={self._freq}Hz")
        print(f"[Pump] Created pump on GPIO{self._pin_number}, freq={self._freq}Hz")

    # =========================================================================
    # Properties - Encapsulation ด้วย @property
    # =========================================================================

    @property
    def is_running(self):
        """
        สถานะการทำงานของปั๊ม (Pump running status)

        ===== Encapsulation =====

        _is_running เป็น private attribute (ขึ้นต้นด้วย _)
        เข้าถึงได้ผ่าน property นี้เท่านั้น (read-only)

        Returns:
            bool: True ถ้าปั๊มกำลังทำงาน
        """
        return self._is_running

    @property
    def flow_rate(self):
        """
        อัตราการไหลที่ 100% duty cycle (Flow rate at 100% duty)

        Returns:
            float: อัตราการไหล mL/s
        """
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, value):
        """
        กำหนดอัตราการไหลใหม่ (Set new flow rate)

        ===== Setter with Validation =====

        Setter สามารถตรวจสอบค่าก่อนกำหนดได้

        Args:
            value (float): อัตราการไหลใหม่ (mL/s)

        Raises:
            ValueError: ถ้าค่าไม่ถูกต้อง
        """
        if value <= 0:
            raise ValueError("อัตราการไหลต้องมากกว่า 0 (Flow rate must be > 0)")
        self._flow_rate = value
        print(f"[Pump] อัตราการไหลใหม่: {value:.4f} mL/s")

    @property
    def current_duty_percent(self):
        """
        Duty cycle ปัจจุบัน (Current duty cycle as percentage)

        Returns:
            float: Duty cycle 0-100%
        """
        return self._current_duty_percent

    @property
    def pin_number(self):
        """
        หมายเลข GPIO pin (GPIO pin number)

        Returns:
            int: หมายเลข GPIO
        """
        return self._pin_number

    @property
    def frequency(self):
        """
        ความถี่ PWM (PWM frequency)

        Returns:
            int: ความถี่ใน Hz
        """
        return self._freq

    # =========================================================================
    # Private Methods - Internal helpers
    # =========================================================================

    def _percent_to_duty(self, percent):
        """
        แปลงเปอร์เซ็นต์เป็นค่า duty (Convert percentage to duty value)

        ===== Private Method =====

        Method นี้ขึ้นต้นด้วย _ แสดงว่าเป็น internal
        ไม่ควรเรียกจากภายนอกคลาส

        การคำนวณ: duty = (percent / 100) * 1023

        Args:
            percent (float): 0-100%

        Returns:
            int: duty value 0-1023
        """
        # จำกัดค่าให้อยู่ในช่วง 0-100
        percent = max(0, min(100, percent))
        return int((percent / 100) * PWM_MAX_DUTY)

    def _log(self, message):
        """
        แสดงข้อความ log (Display log message)

        Args:
            message (str): ข้อความ
        """
        print(f"[Pump] {message}")

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
            self._log("คำเตือน: ปั๊มกำลังทำงานอยู่แล้ว (Warning: Already running)")
            return False

        # แปลงเปอร์เซ็นต์เป็นค่า duty และกำหนดให้ PWM
        duty_value = self._percent_to_duty(duty_percent)
        self._pwm.duty(duty_value)

        # อัปเดต state
        self._current_duty_percent = duty_percent
        self._start_time_us = ticks_us()
        self._is_running = True

        self._log(f"เริ่มปั๊ม Duty={duty_percent}% (Started at {duty_percent}%)")
        return True

    def stop(self):
        """
        หยุดปั๊มและคำนวณเวลา/ปริมาตร (Stop pump and calculate time/volume)

        Returns:
            dict: ข้อมูลการทำงาน
                - elapsed_time_s (float): เวลาที่ทำงาน (s)
                - volume_ml (float): ปริมาตรโดยประมาณ (mL)
                - duty_percent (float): Duty cycle ที่ใช้
        """
        if not self._is_running:
            self._log("คำเตือน: ปั๊มไม่ได้ทำงาน (Warning: Not running)")
            return {
                'elapsed_time_s': 0,
                'volume_ml': 0,
                'duty_percent': 0
            }

        # หยุด PWM
        self._pwm.duty(PWM_MIN_DUTY)

        # คำนวณเวลา
        self._last_stop_time_us = ticks_us()
        elapsed_us = ticks_diff(self._last_stop_time_us, self._start_time_us)
        elapsed_s = elapsed_us / 1_000_000

        # คำนวณปริมาตร
        # สมมติว่า flow rate เป็นสัดส่วนเชิงเส้นกับ duty cycle
        effective_flow_rate = self._flow_rate * (self._current_duty_percent / 100)
        volume_ml = effective_flow_rate * elapsed_s

        # อัปเดต state
        self._total_run_time_us += elapsed_us
        self._is_running = False

        result = {
            'elapsed_time_s': elapsed_s,
            'volume_ml': volume_ml,
            'duty_percent': self._current_duty_percent
        }

        self._log(f"หยุดปั๊ม เวลา={elapsed_s:.2f}s ปริมาตร={volume_ml:.3f}mL")
        self._current_duty_percent = 0

        return result

    def set_duty(self, duty_percent):
        """
        เปลี่ยน Duty Cycle ขณะปั๊มทำงาน (Change duty while running)

        Args:
            duty_percent (float): Duty cycle ใหม่ 0-100%

        Returns:
            bool: True ถ้าเปลี่ยนสำเร็จ
        """
        if not self._is_running:
            self._log("คำเตือน: ปั๊มไม่ได้ทำงาน (Warning: Not running)")
            return False

        duty_value = self._percent_to_duty(duty_percent)
        self._pwm.duty(duty_value)
        self._current_duty_percent = duty_percent

        self._log(f"เปลี่ยน Duty เป็น {duty_percent}%")
        return True

    def run_for_volume(self, volume_ml, duty_percent=100):
        """
        ปั๊มจนได้ปริมาตรที่ต้องการ (Pump until target volume reached)

        ===== Blocking Method =====

        Method นี้จะ block จนกว่าจะปั๊มครบปริมาตร
        ใช้สำหรับการทำงานแบบง่ายๆ

        Args:
            volume_ml (float): ปริมาตรเป้าหมาย (mL)
            duty_percent (float): Duty cycle 0-100%

        Returns:
            dict: ข้อมูลการทำงาน

        Raises:
            ValueError: ถ้าปริมาตรไม่ถูกต้อง
        """
        if volume_ml <= 0:
            raise ValueError("ปริมาตรต้องมากกว่า 0 (Volume must be > 0)")

        # คำนวณเวลาที่ต้องการ
        effective_flow_rate = self._flow_rate * (duty_percent / 100)
        required_time_s = volume_ml / effective_flow_rate
        required_time_ms = int(required_time_s * 1000)

        self._log(f"กำลังปั๊ม {volume_ml:.2f} mL ({required_time_s:.2f} s)")

        # เริ่มปั๊ม
        self.start(duty_percent)

        # รอตามเวลาที่คำนวณ
        sleep_ms(required_time_ms)

        # หยุดปั๊ม
        return self.stop()

    def run_for_time(self, time_ms, duty_percent=100):
        """
        ปั๊มตามเวลาที่กำหนด (Pump for specified time)

        Args:
            time_ms (int): เวลาในมิลลิวินาที
            duty_percent (float): Duty cycle 0-100%

        Returns:
            dict: ข้อมูลการทำงาน
        """
        if time_ms <= 0:
            raise ValueError("เวลาต้องมากกว่า 0 (Time must be > 0)")

        self._log(f"กำลังปั๊ม {time_ms} ms ที่ {duty_percent}%")

        self.start(duty_percent)
        sleep_ms(time_ms)
        return self.stop()

    def purge(self, duration_ms=3000, duty_percent=100):
        """
        ล้างท่อปั๊ม (Purge pump lines)

        ใช้สำหรับไล่อากาศหรือทำความสะอาดท่อ

        Args:
            duration_ms (int): เวลาในการ purge (ms)
            duty_percent (float): Duty cycle 0-100%

        Returns:
            dict: ข้อมูลการทำงาน
        """
        self._log(f"กำลังล้างท่อ {duration_ms} ms (Purging)")
        return self.run_for_time(duration_ms, duty_percent)

    def get_elapsed_time(self):
        """
        รับเวลาที่ปั๊มทำงาน (Get pump run time)

        Returns:
            float: เวลาเป็นวินาที
        """
        if self._is_running:
            current_us = ticks_us()
            elapsed_us = ticks_diff(current_us, self._start_time_us)
            return elapsed_us / 1_000_000
        else:
            if self._last_stop_time_us > 0 and self._start_time_us > 0:
                elapsed_us = ticks_diff(self._last_stop_time_us, self._start_time_us)
                return elapsed_us / 1_000_000
            return 0

    def get_total_run_time(self):
        """
        รับเวลารวมที่ปั๊มทำงาน (Get total pump run time)

        Returns:
            float: เวลารวมเป็นวินาที
        """
        total_s = self._total_run_time_us / 1_000_000
        if self._is_running:
            current_elapsed = ticks_diff(ticks_us(), self._start_time_us) / 1_000_000
            total_s += current_elapsed
        return total_s

    # =========================================================================
    # Resource Management
    # =========================================================================

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
                sleep(1)
                pump.stop()
            finally:
                pump.deinit()
        """
        try:
            # หยุดปั๊มถ้ากำลังทำงาน
            if self._is_running:
                self.stop()

            # ปิด PWM
            self._pwm.duty(PWM_MIN_DUTY)
            self._pwm.deinit()

            self._log(f"ปิดปั๊ม GPIO{self._pin_number} แล้ว (Deinitialized)")
        except Exception as e:
            self._log(f"ข้อผิดพลาด deinit: {e}")

    def __del__(self):
        """
        Destructor - เรียกเมื่อ object ถูก garbage collect

        ===== __del__ Method =====

        Python จะเรียก __del__ เมื่อไม่มี reference ถึง object แล้ว
        ใช้สำหรับ cleanup resources อัตโนมัติ

        หมายเหตุ: ไม่ควรพึ่งพา __del__ เพียงอย่างเดียว
        ควรเรียก deinit() explicitly เสมอ
        """
        self.deinit()

    # =========================================================================
    # Magic Methods
    # =========================================================================

    def __repr__(self):
        """แสดงข้อมูล object สำหรับ debugging"""
        return (f"Pump(pin={self._pin_number}, freq={self._freq}Hz, "
                f"flow_rate={self._flow_rate:.4f}mL/s, running={self._is_running})")

    def __str__(self):
        """แสดงข้อมูล object สำหรับผู้ใช้"""
        status = "ทำงาน (Running)" if self._is_running else "หยุด (Stopped)"
        return f"Pump at GPIO{self._pin_number} - {status}"


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Pump - ควบคุมปั๊มด้วย Composition")
    print("(Pump Control using Composition Design Pattern)")
    print("=" * 60)

    # สร้าง pump object
    pump = Pump()
    print(f"\nrepr: {repr(pump)}")
    print(f"str: {str(pump)}")

    # แสดง properties
    print(f"\n--- Properties ---")
    print(f"pin_number: {pump.pin_number}")
    print(f"frequency: {pump.frequency} Hz")
    print(f"flow_rate: {pump.flow_rate:.4f} mL/s")
    print(f"is_running: {pump.is_running}")
    print(f"current_duty_percent: {pump.current_duty_percent}%")

    # ทดสอบ setter
    print(f"\n--- ทดสอบ Setter ---")
    pump.flow_rate = 0.3  # ตั้งค่าใหม่
    print(f"flow_rate หลังเปลี่ยน: {pump.flow_rate:.4f} mL/s")

    try:
        print(f"\n--- ทดสอบการทำงาน ---")

        # ทดสอบ start/stop
        print("\n1. ทดสอบ Start/Stop:")
        pump.start(50)  # 50% duty
        print(f"   is_running: {pump.is_running}")
        print(f"   duty: {pump.current_duty_percent}%")
        sleep_ms(2000)
        result = pump.stop()
        print(f"   ผลลัพธ์: {result}")

        # ทดสอบ run_for_time
        print("\n2. ทดสอบ run_for_time:")
        result = pump.run_for_time(1000, 100)  # 1 วินาที
        print(f"   ผลลัพธ์: {result}")

        # ทดสอบ purge
        print("\n3. ทดสอบ purge:")
        result = pump.purge(500)  # 0.5 วินาที
        print(f"   ผลลัพธ์: {result}")

        # แสดงเวลารวม
        print(f"\n--- สรุป ---")
        print(f"เวลารวมที่ปั๊มทำงาน: {pump.get_total_run_time():.2f} s")

    except KeyboardInterrupt:
        print("\nหยุดโดยผู้ใช้ (Stopped by user)")

    finally:
        # ทำความสะอาด (Cleanup)
        pump.deinit()

    print("\n" + "=" * 60)
    print("เสร็จสิ้น (Done)")
    print("=" * 60)

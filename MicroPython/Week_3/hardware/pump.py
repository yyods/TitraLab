# ==============================================================================
# pump.py - คลาสควบคุมปั๊มสำหรับการไทเทรต (Pump Control Class for Titration)
# ==============================================================================
# โมดูลนี้จัดการการควบคุมปั๊มไทแทรนต์ด้วย PWM
# This module handles titrant pump control using PWM
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจหลักการ PWM (Pulse Width Modulation)
#   2. เรียนรู้การควบคุมความเร็วมอเตอร์ด้วย Duty Cycle
#   3. ประยุกต์ใช้การจับเวลาด้วย ticks_us() สำหรับความแม่นยำสูง
#
# ความสำคัญในการไทเทรต (Importance in Titration):
#   - ควบคุมปริมาณสารไทแทรนต์อย่างแม่นยำ
#   - ปรับความเร็วการหยดตามระยะห่างจากจุดสมมูล
#   - คำนวณปริมาตรจากเวลาและอัตราการไหล
#
# ==============================================================================

from machine import Pin, PWM
from time import ticks_us, ticks_diff, sleep_ms

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import (
        PUMP_PIN, PUMP_PWM_FREQ, PUMP_PWM_MAX_DUTY,
        PUMP_PWM_MIN_DUTY, DEFAULT_FLOW_RATE_ML_PER_SEC,
        CONTROL_1_PIN, CONTROL_2_PIN
    )
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    # ปั๊มต่อที่ CONTROL_1 หรือ CONTROL_2 บน DEVICES header
    # Pump connects to CONTROL_1 or CONTROL_2 on DEVICES header
    CONTROL_1_PIN = 21  # GPIO21 - CONTROL_1
    CONTROL_2_PIN = 22  # GPIO22 - CONTROL_2
    PUMP_PIN = CONTROL_1_PIN  # ค่าเริ่มต้นใช้ CONTROL_1 (Default: CONTROL_1)
    PUMP_PWM_FREQ = 1000
    PUMP_PWM_MAX_DUTY = 1023
    PUMP_PWM_MIN_DUTY = 0
    # ใช้ 4 ทศนิยมเพื่อลดความคลาดเคลื่อนของปริมาตรสะสม
    # Use 4 decimal places to minimize cumulative volume error
    # (3 ทศนิยมอาจให้ error ~1.2% ของปริมาตร)
    DEFAULT_FLOW_RATE_ML_PER_SEC = 0.2772


class Pump:
    """
    คลาสควบคุมปั๊มด้วย PWM (Pump control class using PWM)

    คุณสมบัติหลัก (Main Features):
        - ควบคุมความเร็วด้วย Duty Cycle (0-100%)
        - จับเวลาการทำงานด้วยความแม่นยำระดับไมโครวินาที
        - คำนวณปริมาตรที่สูบได้จากเวลาและอัตราการไหล

    หลักการ PWM (PWM Principle):
        - PWM ควบคุมความเร็วโดยการเปิด-ปิดสัญญาณอย่างรวดเร็ว
        - Duty Cycle = เปอร์เซ็นต์เวลาที่สัญญาณ HIGH
        - ESP32 ใช้ 10-bit PWM: 0-1023
        - 100% duty = 1023, 50% duty = 511, 0% = ปิด

    ตัวอย่างการใช้งาน (Usage Example):
        >>> pump = Pump()
        >>> pump.start(duty_percent=100)  # เริ่มปั๊มที่ 100%
        >>> sleep(5)
        >>> volume = pump.stop()  # หยุดและรับปริมาตร
        >>> print(f"Volume: {volume:.2f} mL")
    """

    def __init__(self, pin=None, freq=None, flow_rate=None):
        """
        กำหนดค่าเริ่มต้นสำหรับปั๊ม (Initialize pump settings)

        Args:
            pin (int): หมายเลขขา GPIO สำหรับปั๊ม (GPIO pin number)
                       ต่อปั๊มที่ CONTROL_1 → ใช้ GPIO21 (CONTROL_1_PIN)
                       ต่อปั๊มที่ CONTROL_2 → ใช้ GPIO22 (CONTROL_2_PIN)
                       Connect pump to CONTROL_1 → use GPIO21
                       Connect pump to CONTROL_2 → use GPIO22
                       ค่าเริ่มต้น: PUMP_PIN จาก config.py (default: GPIO21)
            freq (int): ความถี่ PWM (PWM frequency in Hz)
                        ค่าเริ่มต้น: 1000 Hz
            flow_rate (float): อัตราการไหลที่ 100% duty (mL/s at 100% duty)
                               ค่าเริ่มต้น: 0.2772 mL/s (4 ทศนิยม)
        """
        # กำหนดขา GPIO (Set GPIO pin)
        self._pin_number = pin if pin is not None else PUMP_PIN
        self._freq = freq if freq is not None else PUMP_PWM_FREQ
        self._flow_rate = flow_rate if flow_rate is not None else DEFAULT_FLOW_RATE_ML_PER_SEC

        # สร้าง PWM object (Create PWM object)
        self._pin = Pin(self._pin_number, Pin.OUT)
        self._pwm = PWM(self._pin, freq=self._freq)
        self._pwm.duty(PUMP_PWM_MIN_DUTY)  # เริ่มต้นปิดปั๊ม (Start with pump off)

        # ตัวแปรสถานะ (State variables)
        self._is_running = False
        self._start_time_us = 0
        self._current_duty_percent = 0
        self._total_run_time_us = 0
        self._last_stop_time_us = 0

        print(f"ปั๊มพร้อมใช้งานที่ GPIO{self._pin_number} (Pump ready on GPIO{self._pin_number})")

    @property
    def is_running(self):
        """
        ตรวจสอบสถานะปั๊ม (Check pump status)

        Returns:
            bool: True ถ้าปั๊มกำลังทำงาน (if pump is running)
        """
        return self._is_running

    @property
    def flow_rate(self):
        """
        อัตราการไหลปัจจุบัน (Current flow rate)

        Returns:
            float: อัตราการไหล mL/s ที่ 100% duty (flow rate at 100% duty)
        """
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, value):
        """
        กำหนดอัตราการไหลใหม่ (Set new flow rate)

        ใช้ 4 ทศนิยม (.4f) เพื่อรักษาความแม่นยำในการคำนวณปริมาตร
        Uses 4 decimal places (.4f) to maintain precision in volume calculation

        Args:
            value (float): อัตราการไหล mL/s ที่ 100% duty (flow rate at 100% duty)
        """
        if value <= 0:
            raise ValueError("อัตราการไหลต้องมากกว่า 0 (Flow rate must be > 0)")
        self._flow_rate = value
        print(f"อัตราการไหลใหม่: {value:.4f} mL/s (New flow rate: {value:.4f} mL/s)")

    @property
    def current_duty_percent(self):
        """
        Duty cycle ปัจจุบัน (Current duty cycle)

        Returns:
            float: Duty cycle เป็นเปอร์เซ็นต์ (duty cycle as percentage)
        """
        return self._current_duty_percent

    def _percent_to_duty(self, percent):
        """
        แปลงเปอร์เซ็นต์เป็นค่า duty (Convert percentage to duty value)

        การคำนวณ (Calculation):
            duty_value = (percent / 100) * 1023

        Args:
            percent (float): เปอร์เซ็นต์ 0-100 (percentage 0-100)

        Returns:
            int: ค่า duty 0-1023 (duty value 0-1023)
        """
        # จำกัดค่าให้อยู่ในช่วง 0-100 (Clamp to 0-100 range)
        percent = max(0, min(100, percent))
        return int((percent / 100) * PUMP_PWM_MAX_DUTY)

    def start(self, duty_percent=100):
        """
        เริ่มทำงานปั๊ม (Start the pump)

        Args:
            duty_percent (float): Duty cycle เป็นเปอร์เซ็นต์ (0-100)
                                  ค่าเริ่มต้น: 100 (เต็มกำลัง)

        Returns:
            bool: True ถ้าเริ่มสำเร็จ (if started successfully)

        หมายเหตุ (Note):
            ใช้ ticks_us() แทน ticks_ms() สำหรับความแม่นยำสูงกว่า
            Uses ticks_us() instead of ticks_ms() for higher precision
        """
        if self._is_running:
            print("คำเตือน: ปั๊มกำลังทำงานอยู่แล้ว (Warning: Pump is already running)")
            return False

        # คำนวณและกำหนด duty cycle (Calculate and set duty cycle)
        duty_value = self._percent_to_duty(duty_percent)
        self._pwm.duty(duty_value)
        self._current_duty_percent = duty_percent

        # บันทึกเวลาเริ่มต้น (Record start time)
        self._start_time_us = ticks_us()
        self._is_running = True

        print(f"เริ่มปั๊ม Duty={duty_percent}% (Pump started at {duty_percent}%)")
        return True

    def stop(self):
        """
        หยุดปั๊มและคำนวณเวลาที่ทำงาน (Stop pump and calculate run time)

        Returns:
            dict: ข้อมูลการทำงาน (operation data) containing:
                - elapsed_time_s (float): เวลาที่ทำงาน (run time in seconds)
                - volume_ml (float): ปริมาตรโดยประมาณ (estimated volume in mL)
                - duty_percent (float): Duty cycle ที่ใช้ (duty cycle used)
        """
        if not self._is_running:
            print("คำเตือน: ปั๊มไม่ได้ทำงาน (Warning: Pump is not running)")
            return {
                'elapsed_time_s': 0,
                'volume_ml': 0,
                'duty_percent': 0
            }

        # หยุด PWM (Stop PWM)
        self._pwm.duty(PUMP_PWM_MIN_DUTY)

        # คำนวณเวลาที่ทำงาน (Calculate elapsed time)
        self._last_stop_time_us = ticks_us()
        elapsed_us = ticks_diff(self._last_stop_time_us, self._start_time_us)
        elapsed_s = elapsed_us / 1_000_000

        # คำนวณปริมาตร (Calculate volume)
        # Volume = flow_rate * time * (duty_percent / 100)
        # สมมติว่า flow_rate เป็นสัดส่วนเชิงเส้นกับ duty cycle
        # Assuming flow_rate is linearly proportional to duty cycle
        effective_flow_rate = self._flow_rate * (self._current_duty_percent / 100)
        volume_ml = effective_flow_rate * elapsed_s

        # อัพเดตสถานะ (Update state)
        self._total_run_time_us += elapsed_us
        self._is_running = False

        result = {
            'elapsed_time_s': elapsed_s,
            'volume_ml': volume_ml,
            'duty_percent': self._current_duty_percent
        }

        print(f"หยุดปั๊ม เวลา={elapsed_s:.2f}s ปริมาตร={volume_ml:.3f}mL "
              f"(Pump stopped: time={elapsed_s:.2f}s volume={volume_ml:.3f}mL)")

        self._current_duty_percent = 0
        return result

    def get_elapsed_time(self):
        """
        อ่านเวลาที่ปั๊มทำงาน (Get pump run time)

        Returns:
            float: เวลาเป็นวินาที (time in seconds)
                   ถ้าปั๊มกำลังทำงาน จะคืนเวลาปัจจุบัน
                   ถ้าปั๊มหยุด จะคืนเวลาครั้งสุดท้าย
        """
        if self._is_running:
            current_us = ticks_us()
            elapsed_us = ticks_diff(current_us, self._start_time_us)
            return elapsed_us / 1_000_000
        else:
            # คืนเวลาจากการทำงานครั้งล่าสุด
            # Return time from last run
            if self._last_stop_time_us > 0 and self._start_time_us > 0:
                elapsed_us = ticks_diff(self._last_stop_time_us, self._start_time_us)
                return elapsed_us / 1_000_000
            return 0

    def set_duty(self, duty_percent):
        """
        เปลี่ยน Duty Cycle ขณะปั๊มทำงาน (Change duty cycle while running)

        Args:
            duty_percent (float): Duty cycle ใหม่ (0-100) (new duty cycle)

        Returns:
            bool: True ถ้าเปลี่ยนสำเร็จ (if changed successfully)
        """
        if not self._is_running:
            print("คำเตือน: ปั๊มไม่ได้ทำงาน (Warning: Pump is not running)")
            return False

        duty_value = self._percent_to_duty(duty_percent)
        self._pwm.duty(duty_value)
        self._current_duty_percent = duty_percent

        print(f"เปลี่ยน Duty เป็น {duty_percent}% (Duty changed to {duty_percent}%)")
        return True

    def run_for_volume(self, volume_ml, duty_percent=100):
        """
        เดินปั๊มจนได้ปริมาตรที่ต้องการ (Run pump until target volume reached)

        Args:
            volume_ml (float): ปริมาตรเป้าหมาย (target volume in mL)
            duty_percent (float): Duty cycle (0-100), ค่าเริ่มต้น 100%

        Returns:
            dict: ข้อมูลการทำงาน (operation data)

        หมายเหตุ (Note):
            ฟังก์ชันนี้เป็น blocking - จะรอจนกว่าจะครบปริมาตร
            This function is blocking - waits until volume reached
        """
        if volume_ml <= 0:
            raise ValueError("ปริมาตรต้องมากกว่า 0 (Volume must be > 0)")

        # คำนวณเวลาที่ต้องการ (Calculate required time)
        effective_flow_rate = self._flow_rate * (duty_percent / 100)
        required_time_s = volume_ml / effective_flow_rate
        required_time_ms = int(required_time_s * 1000)

        print(f"กำลังสูบ {volume_ml:.2f} mL (เวลา {required_time_s:.2f} s)"
              f" (Pumping {volume_ml:.2f} mL in {required_time_s:.2f} s)")

        # เริ่มปั๊ม (Start pump)
        self.start(duty_percent)

        # รอตามเวลาที่คำนวณ (Wait for calculated time)
        sleep_ms(required_time_ms)

        # หยุดปั๊ม (Stop pump)
        return self.stop()

    def pump_volume(self, volume_ml, duty_percent=100):
        """
        ชื่อเรียกอีกชื่อสำหรับ run_for_volume (Alias for run_for_volume)

        Args:
            volume_ml (float): ปริมาตรเป้าหมาย (target volume in mL)
            duty_percent (float): Duty cycle (0-100)

        Returns:
            dict: ข้อมูลการทำงาน (operation data)
        """
        return self.run_for_volume(volume_ml, duty_percent)

    def init(self):
        """
        เมธอดเริ่มต้น (สำหรับความเข้ากันได้กับ HardwareHub)
        Initialization method (for HardwareHub compatibility)

        ปั๊มถูกเริ่มต้นใน __init__ แล้ว เมธอดนี้มีไว้สำหรับความเข้ากันได้
        Pump is already initialized in __init__, this method is for compatibility
        """
        print(f"ปั๊มพร้อมใช้งาน GPIO{self._pin_number} (Pump ready GPIO{self._pin_number})")
        return True

    def purge(self, duration_ms=3000, duty_percent=100):
        """
        ล้างท่อปั๊ม (Purge pump lines)

        ใช้สำหรับไล่อากาศหรือทำความสะอาดท่อ
        Used to remove air or clean the tubing

        Args:
            duration_ms (int): เวลาในการ purge (purge duration in ms)
            duty_percent (float): Duty cycle (0-100)

        Returns:
            dict: ข้อมูลการทำงาน (operation data)
        """
        print(f"กำลังล้างท่อ {duration_ms}ms (Purging for {duration_ms}ms)")

        self.start(duty_percent)
        sleep_ms(duration_ms)
        return self.stop()

    def deinit(self):
        """
        ปิดการใช้งาน PWM และคืนทรัพยากร (Deinitialize PWM and release resources)

        ควรเรียกเมื่อไม่ใช้งานปั๊มแล้ว
        Should be called when pump is no longer needed
        """
        try:
            # หยุดปั๊มถ้ากำลังทำงาน (Stop if running)
            if self._is_running:
                self.stop()

            # ปิด PWM (Deinitialize PWM)
            self._pwm.duty(PUMP_PWM_MIN_DUTY)
            self._pwm.deinit()

            print(f"ปิดปั๊ม GPIO{self._pin_number} แล้ว "
                  f"(Pump GPIO{self._pin_number} deinitialized)")
        except Exception as e:
            print(f"ข้อผิดพลาดขณะปิดปั๊ม (Error during pump deinit): {e}")

    def __del__(self):
        """
        Destructor - ทำความสะอาดเมื่อ object ถูกลบ
        Destructor - cleanup when object is deleted
        """
        self.deinit()

    def __repr__(self):
        """แสดงข้อมูลปั๊ม (Display pump information)"""
        return (f"Pump(pin={self._pin_number}, freq={self._freq}Hz, "
                f"flow_rate={self._flow_rate:.4f}mL/s, running={self._is_running})")

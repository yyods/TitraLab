# ==============================================================================
# buzzer.py - คลาสควบคุม Buzzer สำหรับ TitraLab
# (Buzzer Control Class for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการการสร้างเสียงด้วย PWM สำหรับ feedback ต่างๆ
# This module handles sound generation using PWM for various feedbacks
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจหลักการสร้างเสียงด้วย PWM
#   2. เรียนรู้ความสัมพันธ์ระหว่างความถี่และระดับเสียง
#   3. ประยุกต์ใช้ pattern สำหรับ audio feedback
#
# หลักการสร้างเสียง (Sound Generation Principle):
#   - ใช้ PWM สร้างคลื่นสี่เหลี่ยมที่ความถี่ต่างๆ
#   - ความถี่กำหนดระดับเสียง (pitch)
#   - Duty cycle กำหนดความดัง (volume)
#
# ==============================================================================

from machine import Pin, PWM
from time import sleep_ms

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import (
        BUZZER_PIN, BUZZER_FREQ_LOW, BUZZER_FREQ_MED,
        BUZZER_FREQ_HIGH, BUZZER_DUTY_ON, BUZZER_DUTY_OFF
    )
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    BUZZER_PIN = 26
    BUZZER_FREQ_LOW = 1000
    BUZZER_FREQ_MED = 2000
    BUZZER_FREQ_HIGH = 4000
    BUZZER_DUTY_ON = 512
    BUZZER_DUTY_OFF = 0


class Buzzer:
    """
    คลาสควบคุม Buzzer ด้วย PWM (Buzzer control class using PWM)

    คุณสมบัติหลัก (Main Features):
        - สร้างเสียง beep สั้น/ยาว
        - รูปแบบเสียงสำเร็จรูปสำหรับ feedback ต่างๆ
        - ควบคุมความถี่และความดัง

    หลักการ PWM สำหรับเสียง (PWM for Sound):
        - ความถี่ (freq): กำหนดระดับเสียง
          - ต่ำ (1000 Hz) = เสียงทุ้ม
          - สูง (4000 Hz) = เสียงแหลม
        - Duty cycle: กำหนดความดัง
          - 512 = 50% = ดังปกติ
          - 0 = ปิดเสียง

    ตัวอย่างการใช้งาน (Usage Example):
        >>> buzzer = Buzzer()
        >>> buzzer.beep()                    # เสียง beep สั้น
        >>> buzzer.success_sound()           # เสียงสำเร็จ
        >>> buzzer.error_sound()             # เสียงผิดพลาด
        >>> buzzer.play_tone(2000, 500)      # เสียง 2000Hz 500ms
    """

    def __init__(self, pin=None, default_freq=None, default_duty=None):
        """
        สร้าง Buzzer object (Create Buzzer object)

        Args:
            pin (int): หมายเลขขา GPIO (GPIO pin number)
                       ค่าเริ่มต้น: GPIO26
            default_freq (int): ความถี่เริ่มต้น (default frequency in Hz)
                                ค่าเริ่มต้น: 2000 Hz
            default_duty (int): Duty cycle เริ่มต้น (default duty cycle)
                                ค่าเริ่มต้น: 512 (50%)
        """
        # กำหนดค่า (Set values)
        self._pin_number = pin if pin is not None else BUZZER_PIN
        self._default_freq = default_freq if default_freq else BUZZER_FREQ_MED
        self._default_duty = default_duty if default_duty else BUZZER_DUTY_ON

        # สร้าง PWM object (Create PWM object)
        self._pin = Pin(self._pin_number, Pin.OUT)
        self._pwm = PWM(self._pin, freq=self._default_freq, duty=BUZZER_DUTY_OFF)

        # สถานะ (State)
        self._is_playing = False

        print(f"Buzzer พร้อมใช้งานที่ GPIO{self._pin_number} "
              f"(Buzzer ready on GPIO{self._pin_number})")

    def init(self):
        """
        เริ่มต้น Buzzer (Initialize Buzzer)

        เมธอดนี้ถูกเรียกโดย HardwareHub - PWM พร้อมใช้งานตั้งแต่สร้าง object
        This method is called by HardwareHub - PWM ready from object creation.
        """
        pass  # PWM พร้อมใช้งานตั้งแต่ __init__ (PWM ready from __init__)

    @property
    def is_playing(self):
        """ตรวจสอบว่ากำลังเล่นเสียงหรือไม่ (Check if sound is playing)"""
        return self._is_playing

    def _play(self, freq, duty):
        """
        เริ่มเล่นเสียง (Start playing sound)

        Args:
            freq (int): ความถี่ Hz (frequency in Hz)
            duty (int): Duty cycle 0-1023
        """
        self._pwm.freq(freq)
        self._pwm.duty(duty)
        self._is_playing = True

    def _stop(self):
        """หยุดเล่นเสียง (Stop playing sound)"""
        self._pwm.duty(BUZZER_DUTY_OFF)
        self._is_playing = False

    def play_tone(self, freq, duration_ms, duty=None):
        """
        เล่นเสียงที่ความถี่และระยะเวลาที่กำหนด
        Play tone at specified frequency and duration

        Args:
            freq (int): ความถี่ Hz (frequency in Hz)
            duration_ms (int): ระยะเวลา มิลลิวินาที (duration in ms)
            duty (int): Duty cycle (optional, default 512)
        """
        if duty is None:
            duty = self._default_duty

        self._play(freq, duty)
        sleep_ms(duration_ms)
        self._stop()

    def beep(self, duration_ms=50):
        """
        เสียง beep สั้น (Short beep sound)

        ใช้สำหรับ feedback เมื่อกดปุ่ม
        Used for button press feedback

        Args:
            duration_ms (int): ระยะเวลา (duration in ms), ค่าเริ่มต้น 50ms
        """
        self.play_tone(BUZZER_FREQ_MED, duration_ms)

    def beep_beep(self, beep_duration=100, gap_duration=100):
        """
        เสียง beep สองครั้ง (Double beep sound)

        ใช้สำหรับ feedback การยืนยัน
        Used for confirmation feedback

        Args:
            beep_duration (int): ระยะเวลาแต่ละ beep (each beep duration in ms)
            gap_duration (int): ระยะห่างระหว่าง beep (gap between beeps in ms)
        """
        self.play_tone(BUZZER_FREQ_MED, beep_duration)
        sleep_ms(gap_duration)
        self.play_tone(BUZZER_FREQ_MED, beep_duration)

    def long_beep(self, duration_ms=1000):
        """
        เสียง beep ยาว (Long beep sound)

        ใช้สำหรับ feedback การดำเนินการเสร็จสิ้น
        Used for operation complete feedback

        Args:
            duration_ms (int): ระยะเวลา (duration in ms), ค่าเริ่มต้น 1000ms
        """
        self.play_tone(BUZZER_FREQ_MED, duration_ms)

    def success_sound(self):
        """
        เสียงสำเร็จ - ไล่จากต่ำไปสูง (Success sound - ascending tones)

        รูปแบบ: 1000 Hz -> 2000 Hz -> 3000 Hz
        Pattern: 1000 Hz -> 2000 Hz -> 3000 Hz
        """
        self.play_tone(1000, 100)
        self.play_tone(2000, 100)
        self.play_tone(3000, 100)

    def error_sound(self):
        """
        เสียงผิดพลาด - ไล่จากสูงไปต่ำ (Error sound - descending tones)

        รูปแบบ: 4000 Hz -> 1000 Hz -> 500 Hz
        Pattern: 4000 Hz -> 1000 Hz -> 500 Hz
        """
        self.play_tone(4000, 100)
        self.play_tone(1000, 100)
        self.play_tone(500, 100)

    def calibration_sound(self):
        """
        เสียงการสอบเทียบ (Calibration sound)

        รูปแบบ: เสียงยาวตามด้วยเสียงสั้น
        Pattern: Long tone followed by short tone
        """
        self.play_tone(BUZZER_FREQ_HIGH, 300)
        self.play_tone(BUZZER_FREQ_LOW, 100)

    def warning_sound(self):
        """
        เสียงเตือน (Warning sound)

        รูปแบบ: สลับเสียงสูง-ต่ำ
        Pattern: Alternating high-low tones
        """
        for _ in range(3):
            self.play_tone(BUZZER_FREQ_HIGH, 100)
            self.play_tone(BUZZER_FREQ_LOW, 100)

    def countdown_tick(self):
        """
        เสียง tick สำหรับนับถอยหลัง (Countdown tick sound)

        ใช้สำหรับนับถอยหลังก่อนเริ่มการทดสอบ
        Used for countdown before starting tests
        """
        self.play_tone(1500, 50)

    def start_sound(self):
        """
        เสียงเริ่มต้น (Start sound)

        ใช้เมื่อเริ่มการทำงาน
        Used when starting an operation
        """
        self.success_sound()

    def stop_sound(self):
        """
        เสียงหยุด (Stop sound)

        ใช้เมื่อหยุดการทำงาน
        Used when stopping an operation
        """
        self.error_sound()

    def menu_select_sound(self):
        """
        เสียงเลือกเมนู (Menu select sound)

        ใช้เมื่อเลือกรายการในเมนู
        Used when selecting menu item
        """
        self.beep(30)

    def menu_navigate_sound(self):
        """
        เสียงเลื่อนเมนู (Menu navigate sound)

        ใช้เมื่อเลื่อนในเมนู
        Used when navigating menu
        """
        self.play_tone(1800, 20)

    def titration_complete_sound(self):
        """
        เสียงเมื่อไทเทรตเสร็จ (Titration complete sound)

        เสียงพิเศษสำหรับแจ้งเตือนว่าถึงจุดสมมูล
        Special sound to indicate equivalence point reached
        """
        # ทำนองชัยชนะ (Victory melody)
        notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
        for note in notes:
            self.play_tone(note, 150)
            sleep_ms(50)

    def play_melody(self, notes, durations):
        """
        เล่นทำนองเพลง (Play melody)

        Args:
            notes (list): รายการความถี่ (list of frequencies in Hz)
            durations (list): รายการระยะเวลา (list of durations in ms)

        ตัวอย่าง (Example):
            >>> buzzer.play_melody([262, 294, 330], [200, 200, 400])
        """
        if len(notes) != len(durations):
            raise ValueError(
                "จำนวน notes และ durations ต้องเท่ากัน "
                "(notes and durations must have same length)"
            )

        for freq, duration in zip(notes, durations):
            if freq > 0:
                self.play_tone(freq, duration)
            else:
                sleep_ms(duration)  # Rest (pause)

    def mute(self):
        """
        ปิดเสียง (Mute buzzer)
        """
        self._stop()

    def deinit(self):
        """
        ปิดการใช้งาน PWM และคืนทรัพยากร
        Deinitialize PWM and release resources

        ควรเรียกเมื่อไม่ใช้งาน Buzzer แล้ว
        Should be called when Buzzer is no longer needed
        """
        try:
            self._stop()
            self._pwm.deinit()
            print(f"ปิด Buzzer GPIO{self._pin_number} แล้ว "
                  f"(Buzzer GPIO{self._pin_number} deinitialized)")
        except Exception as e:
            print(f"ข้อผิดพลาดขณะปิด Buzzer (Error during buzzer deinit): {e}")

    def __del__(self):
        """
        Destructor - ทำความสะอาดเมื่อ object ถูกลบ
        Destructor - cleanup when object is deleted
        """
        self.deinit()

    def __repr__(self):
        """แสดงข้อมูล Buzzer"""
        return f"Buzzer(pin={self._pin_number}, freq={self._default_freq}Hz)"

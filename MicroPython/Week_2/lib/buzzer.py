# ==============================================================================
# buzzer.py - คลาสควบคุม Buzzer ด้วย Composition และ Class Methods
# (Buzzer Control Class using Composition and Class Methods)
# ==============================================================================
# โมดูลนี้สาธิต Composition และ Class Methods
# This module demonstrates Composition and Class Methods
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. Composition: Buzzer "has-a" PWM object
#   2. @classmethod: ใช้ factory methods สร้าง predefined sounds
#   3. @staticmethod: utility functions ไม่ต้องการ instance
#   4. Context Manager: __enter__ และ __exit__ สำหรับ with statement
#
# ===== Class Methods vs Static Methods =====
#
# @classmethod:
#   - รับ cls (class) เป็น argument แรก
#   - สามารถเข้าถึง class attributes/methods
#   - ใช้สำหรับ factory methods, alternative constructors
#   - เรียกได้: Buzzer.create_alarm() หรือ buzzer.create_alarm()
#
# @staticmethod:
#   - ไม่รับ self หรือ cls
#   - เป็น utility function ที่เกี่ยวข้องกับ class
#   - ไม่สามารถเข้าถึง instance หรือ class data
#   - เรียกได้: Buzzer.frequency_to_note(440)
#
# Hardware Configuration:
#   - GPIO 26: Buzzer (PWM output)
#
# ==============================================================================

from machine import Pin, PWM
from time import sleep_ms


# ==============================================================================
# ค่าคงที่สำหรับ Buzzer (Buzzer Constants)
# ==============================================================================
BUZZER_PIN = 26                    # GPIO26 สำหรับ Buzzer
PWM_DEFAULT_FREQ = 2000            # ความถี่เริ่มต้น 2000 Hz
PWM_MAX_DUTY = 1023                # 10-bit PWM max
PWM_DUTY_50_PERCENT = 512          # 50% duty for buzzer

# ความถี่โน้ตดนตรี (Musical Note Frequencies)
NOTES = {
    'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349,
    'G4': 392, 'A4': 440, 'B4': 494,
    'C5': 523, 'D5': 587, 'E5': 659, 'F5': 698,
    'G5': 784, 'A5': 880, 'B5': 988
}


class Buzzer:
    """
    คลาสควบคุม Buzzer ด้วย PWM
    (Buzzer control class using PWM)

    ===== Composition =====

    Buzzer "has-a" PWM object เหมือนกับ Pump
    แต่ Buzzer เน้นการสร้างเสียงมากกว่าการควบคุมมอเตอร์

    ===== Class Methods =====

    Buzzer มี class methods สำหรับสร้างเสียงสำเร็จรูป:
    - Buzzer.beep() - เสียง beep สั้น
    - Buzzer.success() - เสียงสำเร็จ
    - Buzzer.error() - เสียง error
    - Buzzer.alarm() - เสียงเตือน

    ===== Context Manager =====

    ใช้กับ with statement ได้:
        with Buzzer() as buzzer:
            buzzer.tone(1000, 500)
        # PWM ถูก deinit อัตโนมัติ

    ===== ตัวอย่างการใช้งาน (Usage Examples) =====

    1. สร้าง instance และใช้งาน:
        buzzer = Buzzer()
        buzzer.tone(1000, 500)  # 1000 Hz, 500 ms
        buzzer.deinit()

    2. ใช้ class method (ไม่ต้องสร้าง instance):
        Buzzer.beep()     # เสียง beep สั้น
        Buzzer.success()  # เสียงสำเร็จ
        Buzzer.error()    # เสียง error

    3. ใช้กับ with statement:
        with Buzzer() as buzzer:
            buzzer.melody(['C4', 'E4', 'G4'], 200)

    Attributes:
        _pin (Pin): Pin object (private - Composition)
        _pwm (PWM): PWM object (private - Composition)
        _is_playing (bool): สถานะกำลังเล่นเสียง (private)
    """

    # ===== Class Attributes =====
    # ค่าเหล่านี้ใช้ร่วมกันโดยทุก instances และ class methods
    DEFAULT_PIN = BUZZER_PIN
    DEFAULT_DURATION_MS = 100
    DEFAULT_FREQUENCY = PWM_DEFAULT_FREQ

    def __init__(self, pin=None):
        """
        Constructor - สร้าง Buzzer object

        Args:
            pin (int): GPIO pin สำหรับ buzzer (ค่าเริ่มต้น: GPIO26)
        """
        # กำหนดค่า pin
        self._pin_number = pin if pin is not None else self.DEFAULT_PIN

        # ===== Composition: สร้าง Pin และ PWM objects =====
        self._pin = Pin(self._pin_number, Pin.OUT)
        self._pwm = PWM(self._pin, freq=self.DEFAULT_FREQUENCY)
        self._pwm.duty(0)  # เริ่มต้นปิดเสียง

        # State
        self._is_playing = False

        print(f"[Buzzer] สร้าง Buzzer ที่ GPIO{self._pin_number}")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_playing(self):
        """สถานะกำลังเล่นเสียง (Is currently playing sound)"""
        return self._is_playing

    @property
    def pin_number(self):
        """หมายเลข GPIO pin"""
        return self._pin_number

    # =========================================================================
    # Instance Methods - การสร้างเสียง
    # =========================================================================

    def tone(self, frequency, duration_ms=None):
        """
        เล่นเสียงที่ความถี่และระยะเวลาที่กำหนด
        (Play tone at specified frequency and duration)

        Args:
            frequency (int): ความถี่ (Hz)
            duration_ms (int): ระยะเวลา (ms)
        """
        duration = duration_ms if duration_ms else self.DEFAULT_DURATION_MS

        self._pwm.freq(frequency)
        self._pwm.duty(PWM_DUTY_50_PERCENT)
        self._is_playing = True

        sleep_ms(duration)

        self._pwm.duty(0)
        self._is_playing = False

    def note(self, note_name, duration_ms=None):
        """
        เล่นโน้ตดนตรี (Play musical note)

        Args:
            note_name (str): ชื่อโน้ต เช่น 'C4', 'A4', 'G5'
            duration_ms (int): ระยะเวลา (ms)
        """
        if note_name not in NOTES:
            print(f"[Buzzer] ไม่รู้จักโน้ต: {note_name}")
            return

        frequency = NOTES[note_name]
        self.tone(frequency, duration_ms)

    def melody(self, notes_list, note_duration_ms=200, gap_ms=50):
        """
        เล่นทำนอง (Play melody)

        Args:
            notes_list (list): รายการโน้ต ['C4', 'D4', 'E4']
            note_duration_ms (int): ระยะเวลาแต่ละโน้ต (ms)
            gap_ms (int): ช่องว่างระหว่างโน้ต (ms)
        """
        for note_name in notes_list:
            if note_name == 'REST':
                sleep_ms(note_duration_ms)
            else:
                self.note(note_name, note_duration_ms)
            sleep_ms(gap_ms)

    def beep_pattern(self, pattern):
        """
        เล่นรูปแบบเสียง (Play beep pattern)

        Args:
            pattern (list): รายการ (frequency, duration) tuples
                           เช่น [(1000, 100), (2000, 100), (1000, 200)]
        """
        for freq, duration in pattern:
            self.tone(freq, duration)
            sleep_ms(50)  # ช่องว่างระหว่างเสียง

    def off(self):
        """ปิดเสียง (Turn off sound)"""
        self._pwm.duty(0)
        self._is_playing = False

    # =========================================================================
    # Class Methods - Factory methods สำหรับเสียงสำเร็จรูป
    # =========================================================================

    @classmethod
    def beep(cls, pin=None):
        """
        เล่นเสียง beep สั้น (Play short beep)

        ===== @classmethod =====

        Class method รับ cls (class) เป็น argument แรก
        ใช้สำหรับสร้าง object และใช้งานในครั้งเดียว

        วิธีใช้:
            Buzzer.beep()  # ไม่ต้องสร้าง instance ก่อน

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            buzzer.tone(2000, 50)
        finally:
            buzzer.deinit()

    @classmethod
    def double_beep(cls, pin=None):
        """
        เล่นเสียง beep สองครั้ง (Play double beep)

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            buzzer.tone(2000, 100)
            sleep_ms(100)
            buzzer.tone(2000, 100)
        finally:
            buzzer.deinit()

    @classmethod
    def long_beep(cls, pin=None, duration_ms=500):
        """
        เล่นเสียง beep ยาว (Play long beep)

        Args:
            pin (int): GPIO pin (optional)
            duration_ms (int): ระยะเวลา (ms)
        """
        buzzer = cls(pin)
        try:
            buzzer.tone(2000, duration_ms)
        finally:
            buzzer.deinit()

    @classmethod
    def success(cls, pin=None):
        """
        เล่นเสียงสำเร็จ (Play success sound)

        รูปแบบ: เสียงสูงขึ้น (ascending tones)

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            pattern = [(1000, 100), (1500, 100), (2000, 100)]
            buzzer.beep_pattern(pattern)
        finally:
            buzzer.deinit()

    @classmethod
    def error(cls, pin=None):
        """
        เล่นเสียง error (Play error sound)

        รูปแบบ: เสียงต่ำลง (descending tones)

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            pattern = [(2000, 100), (1500, 100), (1000, 200)]
            buzzer.beep_pattern(pattern)
        finally:
            buzzer.deinit()

    @classmethod
    def alarm(cls, pin=None, repeats=3):
        """
        เล่นเสียงเตือน (Play alarm sound)

        รูปแบบ: เสียงสลับสูง-ต่ำ

        Args:
            pin (int): GPIO pin (optional)
            repeats (int): จำนวนรอบ
        """
        buzzer = cls(pin)
        try:
            for _ in range(repeats):
                buzzer.tone(2500, 100)
                buzzer.tone(1500, 100)
        finally:
            buzzer.deinit()

    @classmethod
    def calibration_saved(cls, pin=None):
        """
        เล่นเสียงบันทึก calibration (Play calibration saved sound)

        ใช้ในโปรแกรม calibration

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            pattern = [(4000, 300), (1000, 100)]
            buzzer.beep_pattern(pattern)
        finally:
            buzzer.deinit()

    @classmethod
    def startup(cls, pin=None):
        """
        เล่นเสียงเริ่มต้น (Play startup sound)

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            # เสียงไล่ขึ้น (ascending)
            pattern = [(1000, 100), (2000, 100), (3000, 100)]
            buzzer.beep_pattern(pattern)
        finally:
            buzzer.deinit()

    @classmethod
    def shutdown(cls, pin=None):
        """
        เล่นเสียงปิดเครื่อง (Play shutdown sound)

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)
        try:
            # เสียงไล่ลง (descending)
            pattern = [(3000, 100), (2000, 100), (1000, 100)]
            buzzer.beep_pattern(pattern)
        finally:
            buzzer.deinit()

    # =========================================================================
    # Static Methods - Utility functions
    # =========================================================================

    @staticmethod
    def frequency_to_note(frequency):
        """
        แปลงความถี่เป็นชื่อโน้ตที่ใกล้เคียง
        (Convert frequency to nearest note name)

        ===== @staticmethod =====

        Static method ไม่รับ self หรือ cls
        เป็น utility function ที่ไม่ต้องการ instance หรือ class data

        วิธีใช้:
            note = Buzzer.frequency_to_note(440)  # Returns 'A4'

        Args:
            frequency (int): ความถี่ (Hz)

        Returns:
            str: ชื่อโน้ตที่ใกล้เคียง หรือ None
        """
        if frequency <= 0:
            return None

        closest_note = None
        min_diff = float('inf')

        for note_name, note_freq in NOTES.items():
            diff = abs(frequency - note_freq)
            if diff < min_diff:
                min_diff = diff
                closest_note = note_name

        return closest_note

    @staticmethod
    def note_to_frequency(note_name):
        """
        แปลงชื่อโน้ตเป็นความถี่ (Convert note name to frequency)

        Args:
            note_name (str): ชื่อโน้ต เช่น 'A4'

        Returns:
            int: ความถี่ (Hz) หรือ None
        """
        return NOTES.get(note_name)

    @staticmethod
    def get_available_notes():
        """
        รับรายการโน้ตที่รองรับ (Get list of supported notes)

        Returns:
            list: รายการชื่อโน้ต
        """
        return list(NOTES.keys())

    @staticmethod
    def calculate_octave_frequency(base_freq, octaves):
        """
        คำนวณความถี่ที่ต่างจาก base โดย octaves
        (Calculate frequency at different octaves)

        Args:
            base_freq (int): ความถี่ฐาน (Hz)
            octaves (int): จำนวน octaves (+ หรือ -)

        Returns:
            int: ความถี่ใหม่
        """
        return int(base_freq * (2 ** octaves))

    # =========================================================================
    # Context Manager - สำหรับ with statement
    # =========================================================================

    def __enter__(self):
        """
        เมื่อเข้า with block (Called when entering with block)

        ===== Context Manager =====

        ใช้กับ with statement:
            with Buzzer() as buzzer:
                buzzer.tone(1000, 500)
            # __exit__ ถูกเรียกอัตโนมัติ -> deinit()

        Returns:
            self: Buzzer object
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        เมื่อออกจาก with block (Called when exiting with block)

        ทำความสะอาดทรัพยากรอัตโนมัติ

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            False: ไม่ suppress exception
        """
        self.deinit()
        return False  # ไม่ suppress exceptions

    # =========================================================================
    # Resource Management
    # =========================================================================

    def deinit(self):
        """ปิดการใช้งาน PWM (Deinitialize PWM)"""
        try:
            self._pwm.duty(0)
            self._pwm.deinit()
            print(f"[Buzzer] ปิด GPIO{self._pin_number} แล้ว")
        except Exception as e:
            print(f"[Buzzer] Error deinit: {e}")

    def __del__(self):
        """Destructor"""
        self.deinit()

    # =========================================================================
    # Magic Methods
    # =========================================================================

    def __repr__(self):
        """แสดงข้อมูล object สำหรับ debugging"""
        return f"Buzzer(pin={self._pin_number}, playing={self._is_playing})"

    def __str__(self):
        """แสดงข้อมูล object สำหรับผู้ใช้"""
        status = "กำลังเล่น (Playing)" if self._is_playing else "หยุด (Silent)"
        return f"Buzzer at GPIO{self._pin_number} - {status}"


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Buzzer - Composition และ Class Methods")
    print("(Buzzer - Composition and Class Methods)")
    print("=" * 60)

    # ===== 1. ทดสอบ Static Methods =====
    print("\n--- Static Methods ---")
    print(f"Available notes: {Buzzer.get_available_notes()}")
    print(f"A4 frequency: {Buzzer.note_to_frequency('A4')} Hz")
    print(f"440 Hz = {Buzzer.frequency_to_note(440)}")
    print(f"A4 up 1 octave: {Buzzer.calculate_octave_frequency(440, 1)} Hz")

    # ===== 2. ทดสอบ Class Methods (ไม่ต้องสร้าง instance) =====
    print("\n--- Class Methods (No instance needed) ---")

    print("Buzzer.beep()...")
    Buzzer.beep()
    sleep_ms(500)

    print("Buzzer.double_beep()...")
    Buzzer.double_beep()
    sleep_ms(500)

    print("Buzzer.success()...")
    Buzzer.success()
    sleep_ms(500)

    print("Buzzer.error()...")
    Buzzer.error()
    sleep_ms(500)

    # ===== 3. ทดสอบ Instance Methods =====
    print("\n--- Instance Methods ---")
    buzzer = Buzzer()
    print(f"repr: {repr(buzzer)}")
    print(f"str: {str(buzzer)}")

    try:
        print("Playing tone 1000 Hz, 200 ms...")
        buzzer.tone(1000, 200)
        sleep_ms(300)

        print("Playing note A4...")
        buzzer.note('A4', 300)
        sleep_ms(300)

        print("Playing melody C-E-G...")
        buzzer.melody(['C4', 'E4', 'G4'], 200, 50)

    finally:
        buzzer.deinit()

    # ===== 4. ทดสอบ Context Manager =====
    print("\n--- Context Manager (with statement) ---")
    print("Using with statement...")

    with Buzzer() as bz:
        bz.tone(1500, 100)
        bz.tone(2000, 100)
        bz.tone(2500, 100)
    # deinit() ถูกเรียกอัตโนมัติเมื่อออกจาก with block

    print("Exited with block - PWM auto-released")

    print("\n" + "=" * 60)
    print("เสร็จสิ้น (Done)")
    print("=" * 60)

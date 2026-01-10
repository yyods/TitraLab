# ==============================================================================
# 05_class_static_methods.py - Class Methods และ Static Methods
#                           (Class Methods and Static Methods)
# ==============================================================================
# (เนื้อหาเสริม / Supplementary Material)
# เวลาในการสอน: ~20-30 นาที (Teaching time: ~20-30 minutes)
#
# โปรแกรมนี้สอน Class Methods และ Static Methods สำหรับนิสิตเคมี
# This program teaches Class Methods and Static Methods for chemistry students
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจความแตกต่างระหว่าง Instance, Class และ Static Methods
#   2. รู้ว่าเมื่อไหร่ควรใช้ @classmethod
#   3. รู้ว่าเมื่อไหร่ควรใช้ @staticmethod
#   4. นำไปประยุกต์ใช้กับการควบคุม Buzzer
#
# เนื้อหาเสริมจาก: core/02_composition_basics.py
# Supplementary to: core/02_composition_basics.py
#
# ==============================================================================

from machine import Pin, PWM
from time import sleep_ms


# ==============================================================================
# ส่วนที่ 1: แนวคิด Class Methods และ Static Methods (10 นาที)
# Part 1: Class Methods and Static Methods Concept (10 minutes)
# ==============================================================================

print("=" * 60)
print("เนื้อหาเสริม: Class Methods และ Static Methods")
print("Supplementary: Class Methods and Static Methods")
print("=" * 60)

print("""
===== ประเภทของ Methods ใน Python =====

Python มี method 3 ประเภท:

1. Instance Methods (ปกติ):
   - รับ self เป็น argument แรก
   - ทำงานกับ instance เฉพาะ
   - ต้องสร้าง object ก่อนเรียก
   - ตัวอย่าง:
        buzzer = Buzzer()
        buzzer.tone(1000, 200)  # ต้องมี object ก่อน

2. Class Methods (@classmethod):
   - รับ cls (class) เป็น argument แรก
   - ทำงานกับ class โดยรวม
   - เรียกได้โดยไม่ต้องสร้าง instance
   - ตัวอย่าง:
        Buzzer.beep()  # ไม่ต้องสร้าง object

3. Static Methods (@staticmethod):
   - ไม่รับ self หรือ cls
   - เป็น utility function ที่เกี่ยวข้องกับ class
   - ไม่สามารถเข้าถึง instance หรือ class data โดยตรง
   - ตัวอย่าง:
        freq = Buzzer.note_to_frequency('A4')

===== เมื่อไหร่ใช้อะไร? =====

Instance Method:
    - เมื่อต้องการเข้าถึง/แก้ไขข้อมูลของ instance
    - เช่น buzzer.tone() ต้องใช้ self._pwm ของ instance นั้น

Class Method:
    - เมื่อต้องการสร้าง instance แบบพิเศษ (Factory method)
    - เมื่อต้องการทำงานที่เกี่ยวกับ class แต่ไม่ต้องการ instance ถาวร
    - เช่น Buzzer.beep() สร้าง instance ชั่วคราว เล่นเสียง แล้วทำลาย

Static Method:
    - เมื่อเป็น utility function ที่ไม่ต้องใช้ instance หรือ class data
    - เช่น แปลงโน้ตเป็นความถี่ (ไม่จำเป็นต้องมี buzzer object)
""")


# ==============================================================================
# ส่วนที่ 2: ตัวอย่าง Buzzer Class (15 นาที)
# Part 2: Buzzer Class Example (15 minutes)
# ==============================================================================

print("\n" + "=" * 60)
print("ส่วนที่ 2: ตัวอย่าง Buzzer Class")
print("Part 2: Buzzer Class Example")
print("=" * 60)


class Buzzer:
    """
    คลาสควบคุม Buzzer พร้อม Class Methods และ Static Methods
    (Buzzer control class with Class Methods and Static Methods)

    ===== ตัวอย่างการใช้งาน =====

    Instance method (ต้องสร้าง object):
        buzzer = Buzzer()
        buzzer.tone(1000, 200)
        buzzer.deinit()

    Class method (ไม่ต้องสร้าง instance):
        Buzzer.beep()
        Buzzer.success()
        Buzzer.error()

    Static method (utility function):
        freq = Buzzer.note_to_frequency('A4')  # 440 Hz
    """

    # Class constants - ค่าคงที่ระดับ class
    BUZZER_PIN = 26
    DEFAULT_FREQ = 2000
    DUTY_50_PERCENT = 512

    # Musical notes - ความถี่โน้ตดนตรี (Frequency of musical notes)
    NOTES = {
        'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349,
        'G4': 392, 'A4': 440, 'B4': 494,
        'C5': 523, 'D5': 587, 'E5': 659
    }

    def __init__(self, pin=None):
        """
        Constructor - สร้าง Buzzer object

        Args:
            pin (int): GPIO pin สำหรับ buzzer (ค่าเริ่มต้น: 26)
        """
        self._pin_number = pin if pin is not None else self.BUZZER_PIN
        self._pin = Pin(self._pin_number, Pin.OUT)
        self._pwm = PWM(self._pin, freq=self.DEFAULT_FREQ)
        self._pwm.duty(0)  # เริ่มต้นปิดเสียง (Start with sound off)
        print(f"[Buzzer] สร้าง Buzzer ที่ GPIO{self._pin_number}")

    # =========================================================================
    # Instance Methods - ทำงานกับ instance เฉพาะ
    # Instance Methods - Work with specific instance
    # =========================================================================

    def tone(self, frequency, duration_ms=100):
        """
        เล่นเสียงที่ความถี่และระยะเวลาที่กำหนด (Instance method)
        Play sound at specified frequency and duration

        ===== Instance Method =====
        ต้องสร้าง object ก่อน:
            buzzer = Buzzer()
            buzzer.tone(1000, 200)

        Args:
            frequency (int): ความถี่ (Hz)
            duration_ms (int): ระยะเวลา (ms)
        """
        self._pwm.freq(frequency)
        self._pwm.duty(self.DUTY_50_PERCENT)
        sleep_ms(duration_ms)
        self._pwm.duty(0)

    def note(self, note_name, duration_ms=200):
        """
        เล่นโน้ตดนตรี (Instance method)
        Play musical note

        Args:
            note_name (str): ชื่อโน้ต เช่น 'A4', 'C5'
            duration_ms (int): ระยะเวลา (ms)
        """
        if note_name in self.NOTES:
            self.tone(self.NOTES[note_name], duration_ms)
        else:
            print(f"[Buzzer] ไม่รู้จักโน้ต: {note_name} (Unknown note)")

    def play_melody(self, melody, tempo=120):
        """
        เล่นเมโลดี้ (Instance method)
        Play melody

        Args:
            melody (list): รายการ tuple (note, duration_beats)
            tempo (int): จังหวะต่อนาที (beats per minute)
        """
        beat_duration = 60000 // tempo  # ms per beat
        for note_name, beats in melody:
            if note_name == 'R':  # Rest
                sleep_ms(int(beat_duration * beats))
            else:
                self.note(note_name, int(beat_duration * beats * 0.9))
                sleep_ms(int(beat_duration * beats * 0.1))  # Gap between notes

    def deinit(self):
        """
        ปิดการใช้งาน PWM และคืนทรัพยากร (Deinitialize PWM)
        """
        self._pwm.duty(0)
        self._pwm.deinit()
        print(f"[Buzzer] ปิดการใช้งาน GPIO{self._pin_number}")

    # =========================================================================
    # Class Methods - เรียกได้โดยไม่ต้องสร้าง instance
    # Class Methods - Can be called without creating an instance
    # =========================================================================

    @classmethod
    def beep(cls, pin=None):
        """
        เล่นเสียง beep สั้น (Class method)
        Play short beep sound

        ===== @classmethod =====
        - รับ cls (class) เป็น argument แรก
        - สามารถสร้าง instance ภายในได้
        - เรียกได้โดยไม่ต้องสร้าง object:
            Buzzer.beep()

        Args:
            pin (int): GPIO pin (optional)
        """
        buzzer = cls(pin)  # สร้าง instance ชั่วคราว (Create temporary instance)
        try:
            buzzer.tone(2000, 50)
        finally:
            buzzer.deinit()  # คืนทรัพยากร (Release resources)

    @classmethod
    def double_beep(cls, pin=None):
        """
        เล่นเสียง beep สองครั้ง (Class method)
        Play double beep sound
        """
        buzzer = cls(pin)
        try:
            buzzer.tone(2000, 100)
            sleep_ms(100)
            buzzer.tone(2000, 100)
        finally:
            buzzer.deinit()

    @classmethod
    def success(cls, pin=None):
        """
        เล่นเสียงสำเร็จ - เสียงสูงขึ้น (Class method)
        Play success sound - ascending tones
        """
        buzzer = cls(pin)
        try:
            buzzer.tone(1000, 100)
            buzzer.tone(1500, 100)
            buzzer.tone(2000, 100)
        finally:
            buzzer.deinit()

    @classmethod
    def error(cls, pin=None):
        """
        เล่นเสียง error - เสียงต่ำลง (Class method)
        Play error sound - descending tones
        """
        buzzer = cls(pin)
        try:
            buzzer.tone(2000, 100)
            buzzer.tone(1500, 100)
            buzzer.tone(1000, 200)
        finally:
            buzzer.deinit()

    @classmethod
    def warning(cls, pin=None):
        """
        เล่นเสียงเตือน - เสียงซ้ำ (Class method)
        Play warning sound - repeated tones
        """
        buzzer = cls(pin)
        try:
            for _ in range(3):
                buzzer.tone(1500, 100)
                sleep_ms(100)
        finally:
            buzzer.deinit()

    # =========================================================================
    # Static Methods - Utility functions
    # Static Methods - ฟังก์ชันช่วยที่ไม่ต้องใช้ instance
    # =========================================================================

    @staticmethod
    def note_to_frequency(note_name):
        """
        แปลงชื่อโน้ตเป็นความถี่ (Static method)
        Convert note name to frequency

        ===== @staticmethod =====
        - ไม่รับ self หรือ cls
        - เป็น utility function ที่เกี่ยวข้องกับ class
        - เรียกได้โดยไม่ต้องสร้าง object:
            freq = Buzzer.note_to_frequency('A4')

        Args:
            note_name (str): ชื่อโน้ต เช่น 'A4'

        Returns:
            int: ความถี่ (Hz) หรือ None ถ้าไม่พบ
        """
        return Buzzer.NOTES.get(note_name)

    @staticmethod
    def frequency_to_note(frequency):
        """
        แปลงความถี่เป็นโน้ตที่ใกล้เคียงที่สุด (Static method)
        Convert frequency to closest note

        Args:
            frequency (int): ความถี่ (Hz)

        Returns:
            str: ชื่อโน้ตที่ใกล้เคียงที่สุด
        """
        closest_note = None
        min_diff = float('inf')
        for name, freq in Buzzer.NOTES.items():
            diff = abs(frequency - freq)
            if diff < min_diff:
                min_diff = diff
                closest_note = name
        return closest_note

    @staticmethod
    def get_available_notes():
        """
        รับรายการโน้ตที่รองรับ (Static method)
        Get list of supported notes

        Returns:
            list: รายการชื่อโน้ต
        """
        return list(Buzzer.NOTES.keys())

    @staticmethod
    def calculate_frequency(note, octave):
        """
        คำนวณความถี่จากโน้ตและ octave (Static method)
        Calculate frequency from note and octave

        ใช้สูตร: f = 440 * 2^((n-49)/12)
        โดย n คือลำดับของคีย์บนเปียโน (A4 = 49)

        Args:
            note (str): ชื่อโน้ต (C, D, E, F, G, A, B)
            octave (int): หมายเลข octave (4 = กลาง)

        Returns:
            int: ความถี่ (Hz)
        """
        # ลำดับของโน้ตใน octave (Semitones from C)
        semitones = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

        if note not in semitones:
            return None

        # คำนวณลำดับคีย์ (A4 = 49)
        # Calculate key number (A4 = 49)
        key_number = (octave - 4) * 12 + semitones[note] - semitones['A'] + 49

        # คำนวณความถี่ (Calculate frequency)
        frequency = 440 * (2 ** ((key_number - 49) / 12))
        return int(frequency)


# ==============================================================================
# ส่วนที่ 3: ทดสอบการใช้งาน (5-10 นาที)
# Part 3: Testing Usage (5-10 minutes)
# ==============================================================================

print("\n" + "=" * 60)
print("ส่วนที่ 3: ทดสอบการใช้งาน")
print("Part 3: Testing Usage")
print("=" * 60)

# --- ทดสอบ Static Methods ---
print("\n--- Static Methods (ไม่ต้องสร้าง instance) ---")
print(f"โน้ตที่รองรับ: {Buzzer.get_available_notes()}")
print(f"A4 = {Buzzer.note_to_frequency('A4')} Hz")
print(f"C5 = {Buzzer.note_to_frequency('C5')} Hz")
print(f"440 Hz = {Buzzer.frequency_to_note(440)}")
print(f"คำนวณ A4 = {Buzzer.calculate_frequency('A', 4)} Hz")
print(f"คำนวณ C5 = {Buzzer.calculate_frequency('C', 5)} Hz")

# --- ทดสอบ Class Methods ---
print("\n--- Class Methods (ไม่ต้องสร้าง instance) ---")
print("Buzzer.beep():")
Buzzer.beep()
sleep_ms(300)

print("Buzzer.success():")
Buzzer.success()
sleep_ms(300)

print("Buzzer.error():")
Buzzer.error()
sleep_ms(300)

print("Buzzer.warning():")
Buzzer.warning()

# --- ทดสอบ Instance Methods ---
print("\n--- Instance Methods (ต้องสร้าง instance) ---")
buzzer = Buzzer()
try:
    print("buzzer.note('A4'):")
    buzzer.note('A4', 300)
    sleep_ms(200)

    print("buzzer.tone(1000, 200):")
    buzzer.tone(1000, 200)
finally:
    buzzer.deinit()


# ==============================================================================
# ส่วนที่ 4: สรุป
# Part 4: Summary
# ==============================================================================

print("\n" + "=" * 60)
print("สรุป (Summary)")
print("=" * 60)

print("""
สิ่งที่เรียนรู้ในเนื้อหาเสริมนี้:

1. Instance Methods:
   - รับ self เป็น argument แรก
   - ทำงานกับ instance เฉพาะ
   - ตัวอย่าง: buzzer.tone(), buzzer.note()

2. Class Methods (@classmethod):
   - รับ cls (class) เป็น argument แรก
   - เรียกได้โดยไม่ต้องสร้าง instance
   - ใช้สำหรับ factory methods หรือ convenience methods
   - ตัวอย่าง: Buzzer.beep(), Buzzer.success()

3. Static Methods (@staticmethod):
   - ไม่รับ self หรือ cls
   - เป็น utility functions ที่เกี่ยวข้องกับ class
   - ตัวอย่าง: Buzzer.note_to_frequency()

การเชื่อมโยงกับ TitraLab:
   - Buzzer.success() = เสียงเมื่อไทเทรชันสำเร็จ
   - Buzzer.error() = เสียงเมื่อเกิดข้อผิดพลาด
   - Buzzer.warning() = เสียงเตือนใกล้จุดสมมูล
   - note_to_frequency() = แปลงโน้ตสำหรับสร้างเมโลดี้

เนื้อหาหลัก Composition อยู่ที่: core/02_composition_basics.py
""")

print("=" * 60)
print("จบเนื้อหาเสริม Class Methods และ Static Methods")
print("(End of Class Methods and Static Methods)")
print("=" * 60)

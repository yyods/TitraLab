# ==============================================================================
# 02_buzzer_class.py - คลาส Buzzer พื้นฐาน (Basic Buzzer Class)
# ==============================================================================
# สัปดาห์ที่ 1: เรียนรู้ OOP โดยสร้างคลาสควบคุม Buzzer
# Week 1: Learn OOP by creating a Buzzer control class
#
# *** บริบทการไทเทรชัน (Titration Context) ***
# Buzzer แจ้งเตือนเหตุการณ์สำคัญในการไทเทรชัน:
#   - เสียง beep สั้น: ยืนยันการกดปุ่ม (button press confirmed)
#   - เสียงไล่ขึ้น: การสอบเทียบสำเร็จ (calibration complete)
#   - เสียงไล่ลง: ข้อผิดพลาด (error occurred)
#   - เสียงซ้ำ 3 ครั้ง: ตรวจพบจุดสมมูล! (endpoint detected!)
#
# Buzzer signals important titration events:
#   - Short beep: Button press confirmation
#   - Ascending tones: Calibration successful
#   - Descending tones: Error occurred
#   - Triple beep: Endpoint detected - titration complete!
#
# ในการไทเทรชันจริง:
#   - endpoint_sound() = แจ้งว่าถึงจุดสมมูล หยุดหยดสารทันที
#   - error_sound() = แจ้งปัญหา เช่น เซ็นเซอร์ไม่ตอบสนอง
#   - success_sound() = สอบเทียบ pH สำเร็จ พร้อมใช้งาน
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. สร้างคลาสที่ใช้ PWM (Pulse Width Modulation)
#   2. เข้าใจความสัมพันธ์ระหว่างความถี่และเสียง
#   3. เรียนรู้การ cleanup ทรัพยากร PWM ด้วย deinit()
#   4. สร้าง method สำหรับเสียงต่างๆ: beep(), melody()
#
# หลักการสร้างเสียงด้วย PWM:
#   - PWM สร้างคลื่นสี่เหลี่ยมที่ความถี่ต่างๆ
#   - ความถี่ (Hz) กำหนดระดับเสียง (pitch):
#     - 262 Hz = โน้ต C (โด)
#     - 294 Hz = โน้ต D (เร)
#     - 330 Hz = โน้ต E (มี)
#   - Duty cycle กำหนดความดัง (volume):
#     - 512 = 50% = ดังปกติ
#     - 0 = ปิดเสียง
#
# ==============================================================================

from machine import Pin, PWM
import time


class Buzzer:
    """
    คลาสควบคุม Buzzer ด้วย PWM (Buzzer control class using PWM)

    คลาสนี้ช่วยให้การสร้างเสียงง่ายขึ้น และจัดการ PWM อัตโนมัติ

    This class makes sound generation easier and manages PWM automatically.

    ตัวอย่างการใช้งาน (Usage Example):
        >>> buzzer = Buzzer(26)
        >>> buzzer.beep()                # เสียง beep สั้น
        >>> buzzer.play_tone(440, 500)   # เล่นโน้ต A4 นาน 500ms
        >>> buzzer.success_sound()       # เสียงสำเร็จ
        >>> buzzer.deinit()              # ปิด PWM
    """

    # === Class Constants (ค่าคงที่ของคลาส) ===
    # โน้ตดนตรีมาตรฐาน (Standard musical notes)
    NOTES = {
        'C4': 262,  # โด (Do)
        'D4': 294,  # เร (Re)
        'E4': 330,  # มี (Mi)
        'F4': 349,  # ฟา (Fa)
        'G4': 392,  # ซอล (Sol)
        'A4': 440,  # ลา (La)
        'B4': 494,  # ที (Ti)
        'C5': 523,  # โด สูง (High Do)
    }

    def __init__(self, pin_number=26, default_freq=2000, default_duty=512):
        """
        สร้าง Buzzer object (Create Buzzer object)

        Args:
            pin_number (int): หมายเลขขา GPIO
                             TitraLab ใช้ GPIO26
            default_freq (int): ความถี่เริ่มต้น Hz (default frequency)
            default_duty (int): Duty cycle เริ่มต้น 0-1023 (default duty)
                               512 = 50% = ความดังปานกลาง

        ตัวอย่าง (Example):
            buzzer = Buzzer(26)
            buzzer = Buzzer(26, default_freq=1000)  # ความถี่ต่ำกว่า
        """
        # === Instance Variables ===
        self.pin_number = pin_number
        self.default_freq = default_freq
        self.default_duty = default_duty

        # สร้าง PWM object (Create PWM object)
        # PWM = Pulse Width Modulation
        self._pin = Pin(pin_number, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(default_freq)
        self._pwm.duty(0)  # เริ่มต้นปิดเสียง (start with sound off)

        # สถานะ (State)
        self._is_initialized = True

        print(f"สร้าง Buzzer ที่ GPIO{pin_number} สำเร็จ")
        print(f"(Created Buzzer on GPIO{pin_number})")

    def play_tone(self, frequency, duration_ms, duty=None):
        """
        เล่นเสียงที่ความถี่และระยะเวลาที่กำหนด
        Play tone at specified frequency and duration

        Args:
            frequency (int): ความถี่ Hz เช่น 440 = โน้ต A4
                            (frequency in Hz, e.g., 440 = note A4)
            duration_ms (int): ระยะเวลา มิลลิวินาที (duration in ms)
            duty (int): Duty cycle 0-1023 (optional)
                       None = ใช้ค่าเริ่มต้น (use default)

        ตัวอย่าง (Example):
            buzzer.play_tone(440, 500)       # A4 for 500ms
            buzzer.play_tone(262, 1000, 256) # C4 for 1s, quieter
        """
        if duty is None:
            duty = self.default_duty

        # ตั้งความถี่และเปิดเสียง (Set frequency and turn on)
        self._pwm.freq(frequency)
        self._pwm.duty(duty)

        # รอตามระยะเวลา (Wait for duration)
        time.sleep_ms(duration_ms)

        # ปิดเสียง (Turn off sound)
        self._pwm.duty(0)

    def play_note(self, note_name, duration_ms):
        """
        เล่นโน้ตตามชื่อ (Play note by name)

        Args:
            note_name (str): ชื่อโน้ต เช่น 'C4', 'A4', 'G4'
                            (note name e.g., 'C4', 'A4', 'G4')
            duration_ms (int): ระยะเวลา มิลลิวินาที (duration in ms)

        ตัวอย่าง (Example):
            buzzer.play_note('C4', 500)  # โน้ต C นาน 500ms
            buzzer.play_note('A4', 250)  # โน้ต A นาน 250ms
        """
        if note_name in self.NOTES:
            frequency = self.NOTES[note_name]
            self.play_tone(frequency, duration_ms)
        else:
            print(f"ไม่พบโน้ต {note_name} (Note {note_name} not found)")

    def beep(self, duration_ms=100):
        """
        เสียง beep สั้น (Short beep sound)

        Args:
            duration_ms (int): ระยะเวลา (duration in ms)
                              ค่าเริ่มต้น: 100ms

        ตัวอย่าง (Example):
            buzzer.beep()       # beep 100ms
            buzzer.beep(50)     # beep 50ms
        """
        self.play_tone(self.default_freq, duration_ms)

    def beep_beep(self, count=2, duration_ms=100, gap_ms=100):
        """
        เสียง beep หลายครั้ง (Multiple beeps)

        Args:
            count (int): จำนวนครั้ง (number of beeps)
            duration_ms (int): ระยะเวลาแต่ละ beep (each beep duration)
            gap_ms (int): ระยะห่างระหว่าง beep (gap between beeps)

        ตัวอย่าง (Example):
            buzzer.beep_beep(3, 50, 50)  # beep 3 ครั้ง
        """
        for i in range(count):
            self.beep(duration_ms)
            if i < count - 1:  # ไม่ต้องรอหลัง beep สุดท้าย
                time.sleep_ms(gap_ms)

    def success_sound(self):
        """
        เสียงสำเร็จ - ไล่จากต่ำไปสูง (Success sound - ascending tones)

        ใช้บ่งบอกว่าการดำเนินการสำเร็จ
        Used to indicate operation success
        """
        print("เล่นเสียงสำเร็จ (Playing success sound)")
        self.play_note('C4', 100)
        self.play_note('E4', 100)
        self.play_note('G4', 100)
        self.play_note('C5', 200)

    def error_sound(self):
        """
        เสียงผิดพลาด - ไล่จากสูงไปต่ำ (Error sound - descending tones)

        ใช้บ่งบอกว่าเกิดข้อผิดพลาด
        Used to indicate an error occurred
        """
        print("เล่นเสียงผิดพลาด (Playing error sound)")
        self.play_tone(800, 100)
        self.play_tone(400, 100)
        self.play_tone(200, 200)

    def warning_sound(self):
        """
        เสียงเตือน - สลับสูง-ต่ำ (Warning sound - alternating high-low)

        ใช้เตือนผู้ใช้
        Used to warn the user
        """
        print("เล่นเสียงเตือน (Playing warning sound)")
        for _ in range(3):
            self.play_tone(1000, 100)
            self.play_tone(500, 100)

    def play_melody(self, notes, durations):
        """
        เล่นทำนองเพลง (Play melody)

        Args:
            notes (list): รายการโน้ต เช่น ['C4', 'D4', 'E4']
                         (list of notes)
            durations (list): รายการระยะเวลาแต่ละโน้ต (list of durations)

        ตัวอย่าง (Example):
            # เล่น Do-Re-Mi
            buzzer.play_melody(['C4', 'D4', 'E4'], [300, 300, 500])
        """
        if len(notes) != len(durations):
            print("ข้อผิดพลาด: จำนวน notes และ durations ต้องเท่ากัน")
            print("(Error: notes and durations must have same length)")
            return

        for note, duration in zip(notes, durations):
            self.play_note(note, duration)
            time.sleep_ms(50)  # ช่องว่างเล็กๆ ระหว่างโน้ต

    def mute(self):
        """
        ปิดเสียง (Mute/silence)
        """
        self._pwm.duty(0)

    def deinit(self):
        """
        ปิดการใช้งาน PWM และคืนทรัพยากร (Deinitialize PWM and release resources)

        สำคัญ: ต้องเรียกเมื่อใช้งานเสร็จ!
        Important: Must call when done!

        PWM ใช้ทรัพยากร hardware ถ้าไม่ deinit อาจทำให้:
        - ใช้ PWM ที่ pin อื่นไม่ได้
        - เกิด error เมื่อรันโปรแกรมใหม่
        """
        if self._is_initialized:
            self.mute()
            self._pwm.deinit()
            self._is_initialized = False
            print(f"ปิด Buzzer GPIO{self.pin_number} แล้ว")
            print(f"(Buzzer GPIO{self.pin_number} deinitialized)")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบคลาส Buzzer (Testing Buzzer Class)")
    print("=" * 60)

    # === สร้าง Buzzer object ===
    buzzer = Buzzer(26)

    try:
        # === ทดสอบ beep ===
        print("\n--- ทดสอบ beep (Testing beep) ---\n")

        print("1. beep สั้น (short beep)")
        buzzer.beep()
        time.sleep(0.5)

        print("2. beep ยาว (long beep)")
        buzzer.beep(500)
        time.sleep(0.5)

        print("3. beep 3 ครั้ง (beep 3 times)")
        buzzer.beep_beep(3, 100, 100)
        time.sleep(0.5)

        # === ทดสอบ play_tone ===
        print("\n--- ทดสอบ play_tone (Testing play_tone) ---\n")

        print("เล่นความถี่ต่างๆ (Playing different frequencies)")
        for freq in [200, 400, 800, 1600, 3200]:
            print(f"  {freq} Hz")
            buzzer.play_tone(freq, 200)
            time.sleep(0.2)

        # === ทดสอบ play_note ===
        print("\n--- ทดสอบ play_note (Testing play_note) ---\n")

        print("เล่นโน้ต Do-Re-Mi-Fa-Sol-La-Ti-Do")
        for note in ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']:
            print(f"  {note}")
            buzzer.play_note(note, 200)

        time.sleep(0.5)

        # === ทดสอบเสียงสำเร็จ/ผิดพลาด ===
        print("\n--- ทดสอบเสียงพิเศษ (Testing special sounds) ---\n")

        buzzer.success_sound()
        time.sleep(0.5)

        buzzer.error_sound()
        time.sleep(0.5)

        buzzer.warning_sound()
        time.sleep(0.5)

        # === ทดสอบ melody ===
        print("\n--- ทดสอบ melody (Testing melody) ---\n")

        print("เล่นเพลง Twinkle Twinkle (ช่วงแรก)")
        # Twinkle Twinkle Little Star
        notes = ['C4', 'C4', 'G4', 'G4', 'A4', 'A4', 'G4']
        durations = [300, 300, 300, 300, 300, 300, 600]
        buzzer.play_melody(notes, durations)

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        # === ทำความสะอาด (Cleanup) ===
        print("\n--- ทำความสะอาด (Cleanup) ---\n")
        buzzer.deinit()

        print("\n" + "=" * 60)
        print("สรุปสิ่งที่เรียนรู้ (What we learned):")
        print("=" * 60)
        print("""
1. สร้าง class Buzzer ที่ใช้ PWM สร้างเสียง
   (Created Buzzer class using PWM for sound)

2. เข้าใจ PWM (Pulse Width Modulation):
   - freq: ความถี่ = ระดับเสียง (pitch)
   - duty: Duty cycle = ความดัง (volume)

3. สร้าง method ที่มีประโยชน์:
   - play_tone(): เล่นเสียงที่ความถี่กำหนด
   - play_note(): เล่นโน้ตตามชื่อ
   - beep(), beep_beep(): เสียงสั้นๆ
   - success_sound(), error_sound(): เสียง feedback

4. เรียนรู้การ cleanup ทรัพยากร:
   - PWM ใช้ hardware resources
   - ต้องเรียก deinit() เมื่อใช้งานเสร็จ
   - ใช้ try-finally เพื่อให้แน่ใจว่า cleanup ทุกครั้ง

5. ใช้ Class Constants (NOTES dictionary):
   - เก็บค่าคงที่ที่ใช้ร่วมกันทุก object
   - ง่ายต่อการอ้างอิงโน้ตดนตรี
""")
        print("เสร็จสิ้น (Done)")

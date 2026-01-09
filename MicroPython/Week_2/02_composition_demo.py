# ==============================================================================
# 02_composition_demo.py - สาธิต Composition กับ Pump และ Buzzer
# (Composition Demo with Pump and Buzzer)
# ==============================================================================
# โปรแกรมนี้สาธิต Composition: การออกแบบที่ class หนึ่ง "มี" object ของ class อื่น
# This program demonstrates Composition: design where one class "has" another
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Composition: "has-a" relationship
#   2. เปรียบเทียบ Composition vs Inheritance
#   3. ดูประโยชน์ของ Encapsulation
#   4. ใช้ Context Manager (with statement)
#   5. เรียนรู้ Class Methods vs Static Methods
#
# ===== Composition vs Inheritance =====
#
# Inheritance ("is-a"):
#   - PHSensor "is-a" BaseSensor
#   - Child class สืบทอดคุณสมบัติและ methods
#
# Composition ("has-a"):
#   - Pump "has-a" PWM object
#   - Buzzer "has-a" PWM object
#   - Class หนึ่งมีอีก class เป็น attribute
#
# ข้อดีของ Composition:
#   1. Loose coupling - เปลี่ยน implementation ได้ง่าย
#   2. Flexibility - สามารถเปลี่ยน component ได้ runtime
#   3. Encapsulation - ซ่อนความซับซ้อนภายใน
#
# Hardware Configuration:
#   - GPIO 21: Pump (PWM output)
#   - GPIO 26: Buzzer (PWM output)
#
# ==============================================================================

from time import sleep_ms
import sys

# เพิ่ม lib path (Add lib to path)
sys.path.append('lib')

# นำเข้าคลาส Pump และ Buzzer
from lib.pump import Pump
from lib.buzzer import Buzzer


# ==============================================================================
# ส่วนที่ 1: อธิบาย Composition
# Part 1: Explain Composition
# ==============================================================================
def explain_composition():
    """
    อธิบายหลักการ Composition (Explain Composition concept)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 1: Composition คืออะไร?")
    print("Part 1: What is Composition?")
    print("=" * 60)

    print("""
    ===== Composition ("has-a" relationship) =====

    Composition คือการออกแบบที่ class หนึ่ง "มี" (has-a) object
    ของ class อื่นเป็น attribute ภายใน

    ตัวอย่าง:
    - Pump "has-a" PWM object
    - Pump "has-a" Pin object
    - Buzzer "has-a" PWM object

    โครงสร้าง Pump:
        Pump
         |--- _pin (Pin object)     <-- Composition
         |--- _pwm (PWM object)     <-- Composition
         |--- _flow_rate (float)
         |--- methods...

    ===== Composition vs Inheritance =====

    Inheritance ("is-a"):
    - PHSensor IS-A BaseSensor
    - สืบทอดคุณสมบัติ
    - สายสัมพันธ์แน่น (tight coupling)

    Composition ("has-a"):
    - Pump HAS-A PWM
    - มี object เป็น component
    - สายสัมพันธ์หลวม (loose coupling)

    ===== ข้อดีของ Composition =====

    1. Encapsulation: ซ่อน PWM complexity
       แทนที่: pwm.duty(int((percent/100)*1023))
       ใช้แค่:  pump.start(50)

    2. Flexibility: เปลี่ยน implementation ได้
       เช่น เปลี่ยนจาก PWM เป็น DAC

    3. Single Responsibility:
       Pump รับผิดชอบเฉพาะการควบคุมปั๊ม
    """)


# ==============================================================================
# ส่วนที่ 2: สาธิต Pump Composition
# Part 2: Demonstrate Pump Composition
# ==============================================================================
def demonstrate_pump_composition():
    """
    สาธิต Pump ที่ใช้ Composition กับ PWM
    (Demonstrate Pump using Composition with PWM)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 2: Pump Composition")
    print("Part 2: Pump Composition")
    print("=" * 60)

    print("\n--- โครงสร้าง Pump ---")
    print("Pump")
    print(" |--- _pin = Pin(21, Pin.OUT)    # Composition")
    print(" |--- _pwm = PWM(_pin, freq=1000) # Composition")
    print(" |--- _flow_rate = 0.2772")
    print(" |--- _is_running = False")

    print("\n--- สร้าง Pump object ---")
    pump = Pump()
    print(f"repr: {repr(pump)}")
    print(f"str: {str(pump)}")

    print("\n--- Properties ---")
    print(f"  pin_number: {pump.pin_number}")
    print(f"  frequency: {pump.frequency} Hz")
    print(f"  flow_rate: {pump.flow_rate:.4f} mL/s")
    print(f"  is_running: {pump.is_running}")

    print("\n--- Encapsulation: ซ่อน PWM complexity ---")
    print("ไม่ต้องเขียน: pwm.duty(int((50/100)*1023))")
    print("แค่เขียน: pump.start(50)")

    print("\n--- ทดสอบ start/stop ---")
    pump.start(50)  # 50% duty
    print(f"  is_running: {pump.is_running}")
    print(f"  current_duty: {pump.current_duty_percent}%")
    sleep_ms(1000)

    result = pump.stop()
    print(f"  ผลลัพธ์: {result}")

    print("\n--- ทดสอบ run_for_time ---")
    result = pump.run_for_time(500, 100)  # 500ms, 100%
    print(f"  ผลลัพธ์: {result}")

    # ทำความสะอาด
    pump.deinit()

    return True


# ==============================================================================
# ส่วนที่ 3: สาธิต Buzzer Composition และ Class Methods
# Part 3: Demonstrate Buzzer Composition and Class Methods
# ==============================================================================
def demonstrate_buzzer_composition():
    """
    สาธิต Buzzer ที่ใช้ Composition และ Class Methods
    (Demonstrate Buzzer with Composition and Class Methods)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 3: Buzzer Composition และ Class Methods")
    print("Part 3: Buzzer Composition and Class Methods")
    print("=" * 60)

    print("\n--- โครงสร้าง Buzzer ---")
    print("Buzzer")
    print(" |--- _pin = Pin(26, Pin.OUT)    # Composition")
    print(" |--- _pwm = PWM(_pin, freq=2000) # Composition")
    print(" |--- _is_playing = False")

    # ===== สาธิต Class Methods =====
    print("\n" + "-" * 50)
    print("Class Methods - เรียกได้โดยไม่ต้องสร้าง instance")
    print("-" * 50)

    print("\n--- Buzzer.beep() ---")
    print("เรียก: Buzzer.beep()  # ไม่ต้อง buzzer = Buzzer() ก่อน")
    Buzzer.beep()
    sleep_ms(300)

    print("\n--- Buzzer.double_beep() ---")
    Buzzer.double_beep()
    sleep_ms(300)

    print("\n--- Buzzer.success() ---")
    print("รูปแบบ: เสียงสูงขึ้น (ascending)")
    Buzzer.success()
    sleep_ms(300)

    print("\n--- Buzzer.error() ---")
    print("รูปแบบ: เสียงต่ำลง (descending)")
    Buzzer.error()
    sleep_ms(300)

    print("\n--- Buzzer.alarm(repeats=2) ---")
    print("รูปแบบ: เสียงสลับสูง-ต่ำ")
    Buzzer.alarm(repeats=2)
    sleep_ms(300)

    # ===== สาธิต Static Methods =====
    print("\n" + "-" * 50)
    print("Static Methods - Utility functions")
    print("-" * 50)

    print("\n--- Buzzer.get_available_notes() ---")
    notes = Buzzer.get_available_notes()
    print(f"  โน้ตที่รองรับ: {notes}")

    print("\n--- Buzzer.note_to_frequency('A4') ---")
    freq = Buzzer.note_to_frequency('A4')
    print(f"  A4 = {freq} Hz")

    print("\n--- Buzzer.frequency_to_note(440) ---")
    note = Buzzer.frequency_to_note(440)
    print(f"  440 Hz = {note}")

    print("\n--- Buzzer.calculate_octave_frequency(440, 1) ---")
    new_freq = Buzzer.calculate_octave_frequency(440, 1)
    print(f"  A4 (440 Hz) + 1 octave = {new_freq} Hz (A5)")

    return True


# ==============================================================================
# ส่วนที่ 4: สาธิต Instance Methods
# Part 4: Demonstrate Instance Methods
# ==============================================================================
def demonstrate_instance_methods():
    """
    สาธิต Instance Methods ของ Buzzer
    (Demonstrate Buzzer instance methods)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 4: Instance Methods")
    print("Part 4: Instance Methods")
    print("=" * 60)

    print("\n--- สร้าง Buzzer instance ---")
    buzzer = Buzzer()
    print(f"repr: {repr(buzzer)}")

    try:
        print("\n--- buzzer.tone(1000, 200) ---")
        print("เล่นเสียง 1000 Hz, 200 ms")
        buzzer.tone(1000, 200)
        sleep_ms(200)

        print("\n--- buzzer.note('A4', 300) ---")
        print("เล่นโน้ต A4, 300 ms")
        buzzer.note('A4', 300)
        sleep_ms(200)

        print("\n--- buzzer.melody(['C4', 'E4', 'G4'], 200) ---")
        print("เล่นทำนอง C-E-G")
        buzzer.melody(['C4', 'E4', 'G4'], 200, 50)
        sleep_ms(200)

        print("\n--- buzzer.beep_pattern() ---")
        print("เล่นรูปแบบเสียง")
        pattern = [(1000, 100), (1500, 100), (2000, 100), (1500, 100), (1000, 200)]
        buzzer.beep_pattern(pattern)

    finally:
        buzzer.deinit()

    return True


# ==============================================================================
# ส่วนที่ 5: สาธิต Context Manager
# Part 5: Demonstrate Context Manager
# ==============================================================================
def demonstrate_context_manager():
    """
    สาธิต Context Manager (with statement)
    (Demonstrate Context Manager)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 5: Context Manager (with statement)")
    print("Part 5: Context Manager (with statement)")
    print("=" * 60)

    print("""
    ===== Context Manager คืออะไร? =====

    Context Manager ช่วยจัดการ resources อัตโนมัติ:
    - __enter__(): เรียกเมื่อเข้า with block
    - __exit__(): เรียกเมื่อออกจาก with block

    ตัวอย่าง:
        with Buzzer() as buzzer:
            buzzer.tone(1000, 500)
        # __exit__() ถูกเรียก -> deinit() อัตโนมัติ

    ===== ข้อดี =====
    1. ไม่ต้องเรียก deinit() เอง
    2. deinit() ถูกเรียกแม้เกิด exception
    3. Code สะอาดและปลอดภัยกว่า
    """)

    print("\n--- ใช้ with statement ---")
    print("Code:")
    print("  with Buzzer() as buzzer:")
    print("      buzzer.tone(1500, 100)")
    print("      buzzer.tone(2000, 100)")
    print("  # deinit() ถูกเรียกอัตโนมัติ")

    print("\nรัน...")
    with Buzzer() as buzzer:
        buzzer.tone(1500, 100)
        buzzer.tone(2000, 100)
        buzzer.tone(2500, 100)

    print("ออกจาก with block - PWM ถูก deinit อัตโนมัติ")

    print("\n--- เปรียบเทียบกับการใช้ try/finally ---")
    print("Code:")
    print("  buzzer = Buzzer()")
    print("  try:")
    print("      buzzer.tone(1500, 100)")
    print("  finally:")
    print("      buzzer.deinit()  # ต้องเรียกเอง")

    return True


# ==============================================================================
# ส่วนที่ 6: เปรียบเทียบ Composition vs Inheritance
# Part 6: Compare Composition vs Inheritance
# ==============================================================================
def compare_composition_inheritance():
    """
    เปรียบเทียบ Composition กับ Inheritance
    (Compare Composition with Inheritance)
    """
    print("\n" + "=" * 60)
    print("ส่วนที่ 6: เปรียบเทียบ Composition vs Inheritance")
    print("Part 6: Compare Composition vs Inheritance")
    print("=" * 60)

    print("""
    ===== Inheritance ("is-a") =====

    โครงสร้าง:
                BaseSensor
               /          \\
          PHSensor      TempSensor

    คุณสมบัติ:
    - PHSensor "is-a" BaseSensor
    - สืบทอด attributes และ methods
    - ใช้ super().__init__()
    - Override methods ได้

    เหมาะใช้เมื่อ:
    - มีความสัมพันธ์ "is-a"
    - ต้องการ share behavior
    - ต้องการ polymorphism

    ===== Composition ("has-a") =====

    โครงสร้าง:
        Pump
         |--- _pin (Pin object)
         |--- _pwm (PWM object)

        Buzzer
         |--- _pin (Pin object)
         |--- _pwm (PWM object)

    คุณสมบัติ:
    - Pump "has-a" PWM
    - มี object เป็น attribute
    - Encapsulate complexity
    - Loose coupling

    เหมาะใช้เมื่อ:
    - มีความสัมพันธ์ "has-a"
    - ต้องการ flexibility
    - ต้องการ encapsulation

    ===== ตัวอย่างเปรียบเทียบ =====

    สมมติต้องการสร้าง StirringMotor:

    Inheritance approach:
        class StirringMotor(PWM):
            pass
        # StirringMotor IS-A PWM? ไม่ถูกต้อง!

    Composition approach:
        class StirringMotor:
            def __init__(self):
                self._pwm = PWM(...)  # HAS-A PWM
        # StirringMotor HAS-A PWM ถูกต้อง!

    ===== Rule of Thumb =====

    "Favor composition over inheritance"
    - ถ้าไม่แน่ใจ ให้ใช้ Composition ก่อน
    - ใช้ Inheritance เมื่อมี "is-a" relationship ชัดเจน
    """)


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
def main():
    """โปรแกรมหลัก (Main program)"""
    print("=" * 60)
    print("สาธิต Composition กับ Pump และ Buzzer")
    print("(Composition Demo with Pump and Buzzer)")
    print("=" * 60)

    try:
        # ส่วนที่ 1: อธิบาย Composition
        explain_composition()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 2: Pump Composition
        demonstrate_pump_composition()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 3: Buzzer Composition และ Class Methods
        demonstrate_buzzer_composition()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 4: Instance Methods
        demonstrate_instance_methods()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 5: Context Manager
        demonstrate_context_manager()
        input("\nกด Enter เพื่อไปส่วนถัดไป...")

        # ส่วนที่ 6: เปรียบเทียบ
        compare_composition_inheritance()

    except KeyboardInterrupt:
        print("\n\nหยุดโดยผู้ใช้ (Stopped by user)")

    except Exception as e:
        print(f"\nข้อผิดพลาด (Error): {e}")

    finally:
        print("\n" + "=" * 60)
        print("สรุป (Summary):")
        print("- Composition: class มี object อื่นเป็น attribute")
        print("- Class Methods: เรียกได้โดยไม่ต้องสร้าง instance")
        print("- Static Methods: utility functions ของ class")
        print("- Context Manager: จัดการ resources อัตโนมัติ")
        print("- 'Favor composition over inheritance'")
        print("=" * 60)


# รันโปรแกรม
if __name__ == "__main__":
    main()

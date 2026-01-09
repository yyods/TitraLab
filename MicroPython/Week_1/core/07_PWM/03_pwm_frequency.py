# ==============================================================================
# 03_pwm_frequency.py - PWM Frequency Concept
# ==============================================================================
# แนวคิด PWM Frequency และความแตกต่างจาก Duty Cycle
# PWM Frequency concept and difference from Duty Cycle
#
# ความแตกต่างระหว่าง Frequency กับ Duty Cycle:
# Difference between Frequency and Duty Cycle:
#
#   FREQUENCY (ความถี่):
#   - จำนวนรอบการเปิด-ปิดต่อวินาที (cycles per second)
#   - หน่วย: Hz (Hertz)
#   - ตัวอย่าง: 1000 Hz = เปิด-ปิด 1000 รอบ/วินาที
#
#   DUTY CYCLE (ดิวตี้ไซเคิล):
#   - สัดส่วนเวลาที่เปิด ในแต่ละรอบ (proportion of ON time per cycle)
#   - หน่วย: % หรือ 0-1023 ใน ESP32
#
#   แผนภาพ (Diagram):
#
#   Freq = 100 Hz, Duty = 50%        Freq = 200 Hz, Duty = 50%
#   |  Period = 10ms |               | Period = 5ms |
#   _____       _____                __    __    __    __
#   |   |_____||   |_____            | |__|| |__|| |__|| |__
#   <5ms><5ms> <5ms><5ms>            <2.5><2.5>
#
#   ทั้งสองให้ค่าเฉลี่ยแรงดัน 50% เหมือนกัน แต่ความถี่ต่างกัน!
#   Both give 50% average voltage, but different frequencies!
#
# ความถี่มีผลกับอะไร? (What does Frequency affect?)
#
#   1. LED:
#      - ความถี่ต่ำ (<100 Hz): ตาเห็นการกระพริบ (visible flickering)
#      - ความถี่สูง (>100 Hz): ดูเหมือนสว่างสม่ำเสมอ (appears steady)
#
#   2. Buzzer:
#      - ความถี่ต่างกัน = เสียงความถี่ต่างกัน (different tones)
#      - 262 Hz = โน้ต C, 440 Hz = โน้ต A, etc.
#
#   3. Motor/Pump:
#      - ต้องใช้ความถี่ที่เหมาะสมกับมอเตอร์
#      - ความถี่ 1000 Hz เหมาะกับปั๊มของ TitraLab
#
# Chemistry Connection (เชื่อมโยงเคมี):
#   - ปั๊ม TitraLab ใช้ความถี่ 1000 Hz เป็นมาตรฐาน
#   - The TitraLab pump uses 1000 Hz as standard
#   - ความถี่ต่ำเกินไป: มอเตอร์กระตุก (motor jerks)
#   - ความถี่สูงเกินไป: มอเตอร์อาจไม่ตอบสนอง (motor may not respond)
#
# ==============================================================================

from machine import Pin, PWM
import time

# GPIO Pins จาก pins.py (GPIO Pins from pins.py)
LED_RED = 2       # LED สำหรับแสดงผล frequency ต่ำ (LED for low frequency demo)
BUZZER_PIN = 26   # Buzzer สำหรับแสดงผล frequency เสียง (Buzzer for tone demo)

# ==============================================================================
# ส่วนที่ 1: ตั้งค่า PWM (PWM Setup)
# ==============================================================================

print("=" * 50)
print("PWM Frequency Concept Demo")
print("สาธิตแนวคิดความถี่ PWM")
print("=" * 50)
print()

# สร้าง PWM objects (Create PWM objects)
led_pwm = PWM(Pin(LED_RED))
buzzer_pwm = PWM(Pin(BUZZER_PIN))

# ==============================================================================
# ส่วนที่ 2: ผลของ Frequency ต่อ LED (Effect of Frequency on LED)
# ==============================================================================

print("--- ส่วนที่ 1: ผลของ Frequency ต่อ LED ---")
print("--- Part 1: Effect of Frequency on LED ---")
print()

try:
    # ทดสอบความถี่ต่างๆ กับ LED (Test different frequencies with LED)
    # ตั้ง duty = 50% คงที่ (Keep duty at 50%)
    led_pwm.duty(512)

    frequencies_led = [
        (1,    "1 Hz    - เห็นกระพริบชัดเจน (clearly visible blinking)"),
        (5,    "5 Hz    - กระพริบช้า (slow blinking)"),
        (10,   "10 Hz   - กระพริบเร็วขึ้น (faster blinking)"),
        (50,   "50 Hz   - เริ่มเห็นไม่ชัด (starts to blur)"),
        (100,  "100 Hz  - แทบไม่เห็นกระพริบ (barely visible flickering)"),
        (1000, "1000 Hz - ดูสว่างสม่ำเสมอ (appears steady)")
    ]

    print("สังเกต: Duty Cycle = 50% คงที่")
    print("Observe: Duty Cycle = 50% (constant)")
    print("-" * 50)

    for freq, description in frequencies_led:
        led_pwm.freq(freq)
        print(f"Frequency: {description}")
        time.sleep(3)  # รอสังเกต 3 วินาที (observe for 3 seconds)

    # ปิด LED (Turn off LED)
    led_pwm.duty(0)
    print()
    print("สรุป: ความถี่สูงกว่า 100 Hz ทำให้ตาไม่เห็นการกระพริบ")
    print("Summary: Frequencies above 100 Hz appear flicker-free to human eyes")
    print()

    # ==============================================================================
    # ส่วนที่ 3: ผลของ Frequency ต่อ Buzzer (Effect of Frequency on Buzzer)
    # ==============================================================================

    print("-" * 50)
    print("--- ส่วนที่ 2: ผลของ Frequency ต่อ Buzzer ---")
    print("--- Part 2: Effect of Frequency on Buzzer ---")
    print()

    # ตั้ง duty = 50% สำหรับเสียง (Set duty = 50% for sound)
    buzzer_pwm.duty(512)

    # โน้ตดนตรีและความถี่ (Musical notes and frequencies)
    notes = [
        (262, "C4 - โด (Do)"),
        (294, "D4 - เร (Re)"),
        (330, "E4 - มี (Mi)"),
        (349, "F4 - ฟา (Fa)"),
        (392, "G4 - ซอล (Sol)"),
        (440, "A4 - ลา (La) - ความถี่มาตรฐาน"),
        (494, "B4 - ที (Ti)"),
        (523, "C5 - โด สูง (High Do)")
    ]

    print("เล่นโน้ตดนตรี - ความถี่ต่างกัน = เสียงต่างกัน")
    print("Playing musical notes - different frequencies = different tones")
    print("-" * 50)

    for freq, note_name in notes:
        buzzer_pwm.freq(freq)
        print(f"{freq:4d} Hz - {note_name}")
        time.sleep(0.5)  # เล่นแต่ละโน้ต 0.5 วินาที (play each note for 0.5s)

    # ปิดเสียง (Silence)
    buzzer_pwm.duty(0)
    print()

    # ==============================================================================
    # ส่วนที่ 4: สเกลเสียง ขึ้น-ลง (Sound Scale Up and Down)
    # ==============================================================================

    print("-" * 50)
    print("--- ส่วนที่ 3: สเกลความถี่เสียง (Frequency Sweep) ---")
    print()

    print("ความถี่เพิ่มจาก 200 Hz -> 2000 Hz (Sweeping 200 Hz -> 2000 Hz)")
    buzzer_pwm.duty(512)

    for freq in range(200, 2001, 100):
        buzzer_pwm.freq(freq)
        print(f"Frequency: {freq:4d} Hz", end="\r")
        time.sleep(0.1)

    buzzer_pwm.duty(0)
    print()
    print("ความถี่ลดจาก 2000 Hz -> 200 Hz (Sweeping 2000 Hz -> 200 Hz)")
    buzzer_pwm.duty(512)

    for freq in range(2000, 199, -100):
        buzzer_pwm.freq(freq)
        print(f"Frequency: {freq:4d} Hz", end="\r")
        time.sleep(0.1)

    buzzer_pwm.duty(0)
    print()

    # ==============================================================================
    # ส่วนที่ 5: ความถี่สำหรับ Pump (Frequency for Pump)
    # ==============================================================================

    print()
    print("-" * 50)
    print("--- ส่วนที่ 4: ความถี่สำหรับ Pump (ทฤษฎี) ---")
    print("--- Part 4: Frequency for Pump (Theory) ---")
    print("-" * 50)
    print()
    print("ความถี่ที่เหมาะสมสำหรับปั๊ม TitraLab:")
    print("Recommended frequency for TitraLab pump:")
    print()
    print("  PUMP_PIN = 21")
    print("  pump_pwm = PWM(Pin(21))")
    print("  pump_pwm.freq(1000)  # <-- 1000 Hz มาตรฐาน (standard)")
    print()
    print("  ทำไมต้อง 1000 Hz? (Why 1000 Hz?)")
    print("  - ความถี่ต่ำเกินไป: มอเตอร์กระตุก ไม่สม่ำเสมอ")
    print("  - ความถี่สูงเกินไป: มอเตอร์อาจไม่ตอบสนอง")
    print("  - 1000 Hz: เหมาะสมกับ DC motor ขนาดเล็ก")
    print()

    print("=" * 50)
    print("สรุปทั้งหมด (Complete Summary):")
    print("-" * 50)
    print("  Frequency vs Duty Cycle:")
    print("    - Frequency: จำนวนรอบ/วินาที (how fast)")
    print("    - Duty Cycle: สัดส่วนเปิด-ปิดในแต่ละรอบ (how much)")
    print()
    print("  การเลือก Frequency:")
    print("    - LED: >= 100 Hz (ไม่เห็นกระพริบ)")
    print("    - Buzzer: 262-2000 Hz (เสียงต่างๆ)")
    print("    - Pump: 1000 Hz (มาตรฐาน TitraLab)")
    print("=" * 50)

except KeyboardInterrupt:
    print("\n\nหยุดโปรแกรม (Program stopped by user)")

finally:
    # ทำความสะอาด PWM ทั้งหมด (Cleanup all PWM)
    # สำคัญมาก! ต้องทำเสมอ (Very important! Always do this)
    led_pwm.duty(0)
    led_pwm.deinit()
    buzzer_pwm.duty(0)
    buzzer_pwm.deinit()
    print("PWM cleanup completed / ทำความสะอาด PWM เรียบร้อย")

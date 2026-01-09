# ==============================================================================
# 01_song.py - การเล่นเพลงด้วย Buzzer (Playing Music with Buzzer)
# ==============================================================================
# โปรแกรมนี้สาธิตการใช้ PWM เพื่อสร้างเสียงดนตรีจาก Buzzer
# This program demonstrates using PWM to generate music from Buzzer
# ==============================================================================

import time
from machine import Pin, PWM

# กำหนดขา GPIO26 สำหรับ Buzzer (PWM output)
# Set GPIO26 for Buzzer (PWM output)
buzzer_pin = Pin(26, Pin.OUT)

# สร้าง PWM object สำหรับ Buzzer
# Create PWM object for Buzzer
buzzer_pwm = PWM(buzzer_pin)

# กำหนดระยะเวลาของแต่ละโน้ต (มิลลิวินาที)
# Define note duration (milliseconds)
note_duration = 250

# ==============================================================================
# กำหนดโน้ตเพลงและความถี่ (Define melody notes and frequencies)
# ความถี่ตามมาตรฐานดนตรี (Standard musical frequencies)
# ==============================================================================
melody = [
    ('G4', 392),   # โน้ต G (Note G)
    ('A4', 440),   # โน้ต A (Note A)
    ('B4', 494),   # โน้ต B (Note B)
    ('C5', 523),   # โน้ต C (Note C)
    ('G4', 392),
    ('A4', 440),
    ('B4', 494),
    ('C5', 523),
    ('F5', 698),   # โน้ต F (Note F)
    ('E5', 659),   # โน้ต E (Note E)
    ('A4', 440),
    ('C5', 523),
    ('E5', 659),
    ('D5', 587),   # โน้ต D (Note D)
    ('D5', 587),
    ('C5', 523),
    ('A4', 440),
    ('G4', 392),
    ('A4', 440),
    ('B4', 494),
    ('C5', 523),
    ('G4', 392),
    ('A4', 440),
    ('B4', 494),
    ('C5', 523),
    ('F5', 698),
    ('E5', 659),
    ('C5', 523),
    ('E5', 659),
    ('A5', 880),   # โน้ต A สูง (High A note)
    ('G5', 784),   # โน้ต G สูง (High G note)
    ('G4', 392),
    ('A4', 440),
    ('B4', 494),
    ('C5', 523),
    ('G4', 392),
    ('A4', 440),
    ('B4', 494),
    ('C5', 523),
    ('F5', 698),
    ('E5', 659),
    ('C5', 523),
    ('E5', 659),
    ('A5', 880),
    ('D5', 587),
    ('D5', 587),
    ('C5', 523),
    ('A4', 440),
]

print("เริ่มเล่นเพลง (Starting music playback)")
print("=" * 40)

try:
    # เล่นแต่ละโน้ตในเพลง (Play each note in melody)
    for note_name, frequency in melody:
        # ตั้งค่าความถี่ของโน้ต (Set note frequency)
        buzzer_pwm.freq(frequency)

        # ตั้งค่า duty cycle (ความดัง) - 512 = 50%
        # Set duty cycle (volume) - 512 = 50%
        buzzer_pwm.duty(512)

        # แสดงโน้ตที่กำลังเล่น (Show current note)
        print(f"เล่นโน้ต (Playing): {note_name} ({frequency} Hz)")

        # หน่วงเวลาตามระยะเวลาของโน้ต (Delay for note duration)
        time.sleep_ms(note_duration)

        # ปิดเสียงระหว่างโน้ต (Silence between notes)
        buzzer_pwm.duty(0)
        time.sleep_ms(50)

    print("=" * 40)
    print("เล่นเพลงเสร็จสิ้น (Music playback completed)")

except KeyboardInterrupt:
    print("\nหยุดเล่นเพลง (Music stopped)")

finally:
    # ปิด Buzzer และคืนทรัพยากร PWM
    # Turn off Buzzer and release PWM resources
    buzzer_pwm.duty(0)
    buzzer_pwm.deinit()
    print("ปิด Buzzer แล้ว (Buzzer turned off)")

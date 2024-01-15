import time
from machine import Pin, PWM

# Define the buzzer pin
buzzer_pin = Pin(26, Pin.OUT)

# Create a PWM object
buzzer_pwm = PWM(buzzer_pin)

# Define the note duration in milliseconds
note_duration = 250

# Define the melody notes and their frequencies
melody = [
    ('g1', 392),
    ('g1', 392),
    ('g1', 392),
    ('d2', 293),
    ('a1', 440),
    ('g1', 392),
    ('d2', 293),
    ('a1', 440),
    ('g1', 392),
    ('e2', 329),
    ('e2', 329),
    ('d2', 293),
    ('a1', 440),
    ('g1', 392),
    ('d2', 293),
    ('a1', 440),
    ('g1', 392),
    ('g2', 392 * 2),
    ('f2', 349),
    ('e2', 329),
    ('d2', 293),
    ('e2', 329),
    ('g1', 392),
    ('e2', 329),
    ('g2', 392 * 2),
    ('f2', 349),
    ('e2', 329),
    ('d2', 293),
    ('a1', 440),
    ('c2', 523),
    ('a1', 440),
    ('c2', 523),
    ('d2', 293),
    ('g1', 392),
    ('e2', 329),
    ('g2', 392 * 2),
    ('f2', 349),
    ('e2', 329),
    ('d2', 293),
    ('e2', 329),
    ('g1', 392),
    ('e2', 329),
    ('g2', 392 * 2),
    ('f2', 349),
    ('e2', 329),
    ('d2', 293),
    ('a1', 440),
]

# Play the melody
for note, frequency in melody:
    buzzer_pwm.freq(frequency)
    buzzer_pwm.duty(50)  # Set the duty cycle (volume)
    time.sleep_ms(note_duration)
    buzzer_pwm.duty(0)   # Turn off the buzzer
    time.sleep_ms(50)    # Pause between notes

# Turn off the buzzer
buzzer_pwm.duty(0)

# Cleanup PWM
buzzer_pwm.deinit()

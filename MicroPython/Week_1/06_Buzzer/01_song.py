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
    ('a1', 440),
    ('b1', 494),
    ('c2', 523),
    ('g1', 392),
    ('a1', 440),
    ('b1', 494),
    ('c2', 523),
    ('f2', 698),
    ('e2', 659),
    ('a1', 440),
    ('c2', 523),
    ('e2', 659),
    ('d2', 587),
    ('d2', 587),
    ('c2', 523),
    ('a1', 440),
    ('g1', 392),
    ('a1', 440),
    ('b1', 494),
    ('c2', 523),
    ('g1', 392),
    ('a1', 440),
    ('b1', 494),
    ('c2', 523),
    ('f2', 698),
    ('e2', 659),
    ('c2', 523),
    ('e2', 659),
    ('a2', 880),
    ('g2', 784),
    ('g1', 392),
    ('a1', 440),
    ('b1', 494),
    ('c2', 523),
    ('g1', 392),
    ('a1', 440),
    ('b1', 494),
    ('c2', 523),
    ('f2', 698),
    ('e2', 659),
    ('c2', 523),
    ('e2', 659),
    ('a2', 880),
    ('d2', 587),
    ('d2', 587),
    ('c2', 523),
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

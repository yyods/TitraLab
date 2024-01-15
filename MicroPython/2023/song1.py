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
    ('E5', 659),
    ('D5', 587),
    ('C5', 523),
    ('D5', 587),
    ('E5', 659),
    ('E5', 659),
    ('E5', 659),
    ('D5', 587),
    ('D5', 587),
    ('D5', 587),
    ('E5', 659),
    ('G5', 784),
    ('G5', 784),
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

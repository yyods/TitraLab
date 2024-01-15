import time
from machine import Pin, PWM

# Define the buzzer pin
buzzer_pin = Pin(26, Pin.OUT)

# Create a PWM object
buzzer_pwm = PWM(buzzer_pin)

# Define the melody notes and their frequencies
melody = [
    ('D5', 587.33),
    ('B4', 493.88),
    ('A4', 440.00),
    ('G4', 392.00),
    ('E4', 329.63),
    ('D4', 293.66),
    ('E4', 329.63),
    ('G4', 392.00),
    ('A4', 440.00),
    ('D4', 293.66),
    ('D4', 293.66),
    ('D5', 587.33),
    ('B4', 493.88),
    ('A4', 440.00),
    ('G4', 392.00),
    ('E4', 329.63),
    ('D4', 293.66),
    ('E4', 329.63),
    ('G4', 392.00),
    ('A4', 440.00),
    ('D4', 293.66),
    ('D4', 293.66),
]

# Define the note duration in milliseconds
note_duration = 250

# Play the melody
for note, frequency in melody:
    buzzer_pwm.freq(int(frequency))
    buzzer_pwm.duty(50)  # Set the duty cycle (volume)
    time.sleep_ms(note_duration)
    buzzer_pwm.duty(0)   # Turn off the buzzer
    time.sleep_ms(50)    # Pause between notes

# Turn off the buzzer
buzzer_pwm.deinit()
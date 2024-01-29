import machine
import time

# Define the GPIO pin for the LED (change as per your connection)
led_pin = 5

# Initialize PWM object on the LED pin with a frequency of 500 Hz
led = machine.PWM(machine.Pin(led_pin), freq=500)

# Function to gradually increase brightness
def fade_in(led, max_duty=4095, step=10, delay=0.01):
    for duty in range(0, max_duty+1, step):
        led.duty(duty)
        time.sleep(delay)

# Function to gradually decrease brightness
def fade_out(led, max_duty=4095, step=10, delay=0.01):
    for duty in range(max_duty, -1, -step):
        led.duty(duty)
        time.sleep(delay)

# Main loop to fade LED in and out
while True:
    fade_in(led)
    fade_out(led)

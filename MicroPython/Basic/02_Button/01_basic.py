import machine

button = machine.Pin(35, machine.Pin.IN)
print(button.value())
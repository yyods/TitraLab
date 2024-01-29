import machine

button = machine.Pin(35, machine.Pin.IN)

button_pressed = False

while True:
    if button.value() == 1 and not button_pressed:
        print('ON')
        button_pressed = True
        
    elif button.value() == 0 and button_pressed:
        print('OFF')
        button_pressed = False
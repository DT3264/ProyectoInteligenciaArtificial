from gpiozero import LED, Button

led = LED(25)
switch = Button(24)

lastState = False
actualState = False

while True:
    actualState = switch.is_pressed
    if lastState != actualState:
        if actualState:
            led.on()
        else:
            led.off()
    lastState = actualState

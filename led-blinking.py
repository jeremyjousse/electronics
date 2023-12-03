from machine import Pin, Timer
import time

led = Pin(15, Pin.OUT)
led2 = Pin(13, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

while True:
    if button.value():
        if led.value():
            led.value(0)
            led2.toggle()
            time.sleep(0.25)
        else:
            led.value(1)
            time.sleep(0.25)

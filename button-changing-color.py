from machine import Pin, PWM
from time import sleep
import random

button = Pin(12, Pin.IN, Pin.PULL_DOWN)

blue = PWM(Pin(15, Pin.OUT))
blue.freq(100)

green = PWM(Pin(14, Pin.OUT))
green.freq(100)

red = PWM(Pin(13, Pin.OUT))
red.freq(100)

leds = [blue, green, red]

def level_up(led):
    for duty in range(65025):
        led.duty_u16(duty)
        sleep(0.0001) 

def level_down(led):
    if led.duty_u16() == 65024:
        for duty in range(65025, 0, -1):
            led.duty_u16(duty)
            sleep(0.0001) 

while True:
    if button.value() == 1:
        led = leds[random.randint(0, 2)]
        level_up(led)
        level_down(led)








    # level_up(green)
    # level_down(blue)
    # level_up(red)
    # level_down(green)
    # level_up(blue)
    # level_down(red)
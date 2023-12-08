from machine import Pin, PWM
from time import sleep

blue = PWM(Pin(15))
blue.freq(100)

green = PWM(Pin(14))
green.freq(100)

red = PWM(Pin(13))
red.freq(100)


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
    level_up(green)
    level_down(blue)
    level_up(red)
    level_down(green)
    level_up(blue)
    level_down(red)
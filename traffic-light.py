from machine import Pin
import time

green_led = Pin(15, Pin.OUT)
red_led = Pin(13, Pin.OUT)

while True:
    green_led.on()
    red_led.off()
    time.sleep(5)
    red_led.on()
    time.sleep(1)
    green_led.off()
    time.sleep(5)

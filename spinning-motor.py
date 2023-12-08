from machine import Pin
import time

buzzer = Pin(15, Pin.OUT)
led = Pin(14, Pin.OUT)

while True:
    buzzer.on()
    led.on()
    time.sleep(5)
    buzzer.off()
    led.off()
    time.sleep(1)

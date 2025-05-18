import time
from neopixel import Neopixel
from machine import Pin

pin = Pin("LED", Pin.OUT)

num_pixels = 290
num_pixels_on = 5
pixels = Neopixel(num_pixels, 0, 28, "GRB")

i_color = 0

yellow = (255, 100, 0)
orange = (255, 50, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
purple = (200, 0, 100)
indigo = (100, 0, 90)

colors = [yellow, orange, green, blue, red, purple, indigo]
off_color = (0, 0, 0)

pixels.brightness(255)


pixels.fill(off_color)
pixels.show()

while True:
    i_color = i_color + 1
    if i_color >= len(colors):
        i_color = 0

    chase_color = colors[i_color]
    for i in range(num_pixels):
        pixel_to_turn_off_index = (i - num_pixels_on + num_pixels) % num_pixels

        pixels.set_pixel(i, chase_color)
        pixels.set_pixel(pixel_to_turn_off_index, off_color)

        pixels.show()
        time.sleep(0.001)

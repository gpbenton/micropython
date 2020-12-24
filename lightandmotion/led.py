# LED defintion for wemos d1 mini
from machine import Pin

class Led:
    def __init__(self, pin):
        self.led = Pin(pin, Pin.OUT)

    def on(self):
        self.led.off()

    def off(self):
        self.led.on()

led = Led(2)

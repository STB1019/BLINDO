from machine import Pin
from usrio.gpio_usr_buttons import GPIOUsrButtons

class UsrIOConfig:
    def __init__(self):
        self.PWR_PIN_ID = 0
        self.PWR_PIN = Pin(self.PWR_PIN_ID, Pin.IN, Pin.PULL_DOWN)
        
        self.VOL_UP_PIN = Pin(1, Pin.IN)
        self.VOL_DOWN_PIN = Pin(2, Pin.IN)
        self.USR_BTNS = GPIOUsrButtons(3, 4)

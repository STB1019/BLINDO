from machine import Pin, deepsleep
from lowpower import dormant_until_pin

class UsrIO:
    def __init__(self, config):
        self.config = config
        self.ready = False
        
        self.on_power_on = None
        self.on_power_off = None
        self.on_volume = None
        self.on_volume_up = None
        self.on_volume_dw = None
        
        self.configure()
        #self.sleep()
    
    def configure(self):
        self.config_vol_pins()
        self.config_pwr_pin()
        
    def config_pwr_pin(self):
        self.config.PWR_PIN.irq(
            handler=self.__pwr_irq, 
            trigger=Pin.IRQ_RISING
        )
    
    def config_vol_pins(self):
        self.config.VOL_UP_PIN.irq(
            handler=self.__vol_irq, 
            trigger=Pin.IRQ_FALLING
        )
        self.config.VOL_DOWN_PIN.irq(
            handler=self.__vol_irq, 
            trigger=Pin.IRQ_FALLING
        )
        
    def sleep(self):
        self.config.VOL_DOWN_PIN.irq(handler=None)
        self.config.VOL_UP_PIN.irq(handler=None)
        dormant_until_pin(self.config.PWR_PIN_ID)
        
    def __callback(self, function, *args, **kwargs):
        if function is not None:
            function(*args, **kwargs)

    def __pwr_irq(self, pin):
        self.ready = not self.ready
        if self.ready:
            print("Power ON")
            self.configure()
            self.__callback(self.on_power_on)
        else:
            print("Powering Off")
            self.__callback(self.on_power_off)
            self.sleep()
    
    def __vol_irq(self, pin):
        self.__callback(self.on_volume, inc=1 if pin is self.config.VOL_UP_PIN else -1)
        if pin is self.config.VOL_UP_PIN:
            self.__callback(self.on_volume_up)
        else:
            self.__callback(self.on_volume_dw)
            
            
            
#from usrio.usrio import UsrIO
#from usrio.usrio_conf import UsrIOConfig
#io = UsrIO(UsrIOConfig())
#io.on_volume = lambda inc=0: print(inc)
#p = machine.Pin('LED', machine.Pin.OUT)
#io.on_power_on=lambda: p.off()
#io.on_power_off=lambda: p.on()

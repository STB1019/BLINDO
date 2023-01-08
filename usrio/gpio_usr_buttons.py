from machine import Pin

class GPIOUsrButtons:
    def __init__(self, *gpios):
        self.gpios = list(map(lambda x: Pin(x, Pin.IN), gpios))
        self.irq = None
        for b in self.gpios:
            b.irq(handler=self.__btn_irq, trigger=Pin.IRQ_FALLING)
    
    def __btn_irq(self, pin):
        if self.irq is not None:
            self.irq(self, self.get_first())
    
    def __len__(self):
        return len(self.gpios)
    
    def iget(self):
        for btn in self.gpios:
            yield btn.value() == 0
    
    def get(self, n=None):
        if n is None:
            return list(self.iget())
            
        if n >= len(self.gpios):
            raise Exception("Inexistent User Button")
            
        return self.gpios[n].value() == 0
        
    def get_first(self):
        n = 0
        it = self.iget()
        try:
            while not next(it):
                n += 1
            return n
        except StopIteration:
            return None

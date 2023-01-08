from ui.ui import UI
from ssd1306 import SSD1306_I2C

class SSD1306UI(UI):
    def __init__(self, i2c):
        super(SSD1306UI, self).__init__(None, [0, 0, 128, 64])
        self.i2c = i2c
        assert 60 in self.i2c.scan()
        self.display = SSD1306_I2C(128, 64, self.i2c)
        self.display.fill(0)
        self.display.show()
        
        
#from machine import Pin, I2C
#from ui.ssd1306_ui import SSD1306UI
#from ui.primitives.line import Line
#from ui.primitives.rect import Rect
#from ui.primitives.text import Text
#from ui.primitives.poly import Poly
#ui = SSD1306UI(I2C(1, sda=Pin(14), scl=Pin(15), freq=400000))
#p = Poly(0, 0, [(0, 0), (128, 32), (0, 64)], edge_color=1, fill=False)

#l1 = Line(0, 12, 128, 12)
#l2 = Line(64, 0, 66, 32)
#l3 = Line(32, 4, 96, 20)
#r1 = Rect(40, 6, 28, 12, edge_color=1, fill=True, fill_color=0)
#r2 = Rect(32, 4, 64, 16, edge_color=1, fill=False)
#t = Text(24, 30, "Pippo Pera!", color=0, boxed=True)
#r3 = Rect(32, 25, 28, 20, edge_color=1, fill_color=0, fill=True)

#ui.add(l1, 0)
#ui.add(r2, 0)
#ui.add(r1, 1)
#ui.add(l2, -1)
#ui.redraw()

#ui.add(t, 3)
#ui.redraw()
#ui.add(r3, 2)
#ui.redraw()


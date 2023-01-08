from ui.views.view import View
from ui.primitives.rect import Rect
from ui.primitives.poly import Poly
from ui.primitives.text import Text

class FatalView(View):
    def __init__(self, ui, text):
        super(FatalView, self).__init__(ui)
        
        self.add(Rect(4, 4, 120, 56))
        self.add(Poly(52, 6, [(0, 4), (4, 0), (12, 8), (20, 0), (24, 4), (16, 12), (24, 20), (20, 24), (12, 16), (4, 24), (0,20), (8, 12)], fill_color=1, fill=True))
        
        lines = text.split("\n")
        y = 32
        for l in lines:
            l = l[:14]
            length = len(l)*8
            x = 8 + 56 - length/2
            self.add(Text(int(x), y, l))
            y += 10
            

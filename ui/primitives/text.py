from ui._element import Element

class Text(Element):
    def __init__(self, x, y, value, color=1, boxed=False, box_border_size=1):
        super(Text, self).__init__([x, y, len(value)*8, 8], not boxed)
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.boxed = boxed
        self.box_border_size = box_border_size

    def _write(self, display):
        if self.boxed:
            display.rect(self.x-self.box_border_size, self.y-self.box_border_size, len(self.value)*8+2*self.box_border_size, 8+2*self.box_border_size, 1-self.color, True)
        display.text(self.value, self.x, self.y, self.color)
        
    def set_text(self, value):
        self.value = value
        self._update([self.x, self.y, len(value)*8, 8])


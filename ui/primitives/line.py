from ui._element import Element

class Line(Element):
    def __init__(self, xa, ya, xb, yb, color=1):
        super(Line, self).__init__(Line.__bbox(xa, ya, xb, yb), True)
        self.args = [xa, ya, xb, yb]
        self.color = color

    def _write(self, display):
        display.line(*self.args, self.color)
        
    @staticmethod
    def __bbox(xa, ya, xb, yb):
        return [min(xa, xb), min(ya, yb), max(xa, xb)-min(xa, xb), max(ya, yb)-min(ya, yb)]


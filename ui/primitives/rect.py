from ui._element import Element

class Rect(Element):
    def __init__(self, x, y, w, h, edge_color=1, fill_color=0, fill=False):
        super(Rect, self).__init__([x, y, w, h], not fill)
        self.args = [x, y, w, h]
        self.edge_color = edge_color
        self.fill_color = fill_color
        self.fill = fill

    def _write(self, display):
        display.rect(*self.args, self.edge_color)
        if self.fill:
            display.rect(self.args[0]+1, self.args[1]+1, self.args[2]-2, self.args[3]-2, self.fill_color, True)

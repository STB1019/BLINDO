from ui._element import Element

class Ellipse(Element):
    def __init__(self, x, y, xr, yr, edge_color=1, fill_color=0, fill=False):
        super(Ellipse, self).__init__([x-xr, y-yr, 2*xr, 2*yr], not fill)
        self.args = [x, y, xr, yr]
        self.edge_color = edge_color
        self.fill_color = fill_color
        self.fill = fill

    def _write(self, display):
        display.ellipse(*self.args, self.edge_color, False)
        if self.fill:
            display.ellipse(self.args[0], self.args[1], self.args[2]-1, self.args[3]-1, self.fill_color, True)

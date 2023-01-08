from ui._element import Element
import array
class Poly(Element):
    def __init__(self, x, y, points, edge_color=1, fill_color=0, fill=False):
        coords = array.array('h', [0]*len(points)*2)
        min_x = 65535
        max_x = 0
        min_y = 65535
        max_y = 0
        for i, p in enumerate(points):
            coords[i*2] = p[0]
            coords[i*2+1] = p[1]
            min_x = min(min_x, p[0])
            max_x = max(max_x, p[0])
            min_y = min(min_y, p[1])
            max_y = max(max_y, p[1])
        
        super(Poly, self).__init__([min_x + x, min_y + y, max_x - min_x, max_y - min_y], not fill)
        
        self.args = [x, y, coords]
        self.edge_color = edge_color
        self.fill_color = fill_color
        self.fill = fill

    def _write(self, display):
        if self.fill:
            display.poly(*self.args, self.fill_color, True)
        display.poly(*self.args, self.edge_color)
        

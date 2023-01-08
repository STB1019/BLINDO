from ui.ui import UI

class View(UI):
    def __init__(self, ui):
        super(View, self).__init__(None, None)
        self.ui = ui

    def redraw(self, bbox):
        self.ui.redraw(bbox=None)
        
    def delete(self, element):
        self.ui.delete(element)
    
    def show(self):
        self.ui.elements = self.elements
        self.ui.redraw()


class UI:
    def __init__(self, display, screen_bbox):
        self.display = display
        self.screen_bbox = screen_bbox
        self.elements = []
        
    def add(self, element, zindex=0):
        element.view = self
        element.zidx = zindex
        if element not in self.elements:
            self.elements += [element]       
        self.elements.sort()
        
    def delete(self, element):
        self.elements.remove(element)
        self.redraw(element.bbox)
    
    def redraw(self, bbox=None):      
        if bbox is None or True: #todo ottimizzazione
            bbox = self.screen_bbox
        
        self.display.rect(*bbox, 0, True)
        for elm in self.elements:
            elm._write(self.display)
        self.display.show()
        
    @staticmethod
    def bbox_intersect(a, b): #X, Y, W, H
        return (abs((a[0] + a[2]/2) - (b[0] + b[2]/2)) * 2 <= (a[2] + b[2])) and (abs((a[1] + a[3]/2) - (b[1] + b[3]/2)) * 2 <= (a[3] + b[3]))
    
    @staticmethod
    def bbox_included(a, b): #X, Y, W, H
        return a[0] <= b[0] <= a[0]+a[2] and a[1] <= b[1] <= a[1]+a[3] and b[2] <= a[2]-(b[0]-a[0]) and b[3] <= a[3]-(b[1]-a[1])

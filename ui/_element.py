class Element:
    def __init__(self, bbox, transparent=False):
        self.bbox = bbox
        self.view = None
        self.transparent = transparent
        self.zidx = 0
        self.under = []
    
    def __lt__(self, oth):
        return self.zidx < oth.zidx
    
    def __gt__(self, oth):
        return self.zidx > oth.zidx

    def _write(self, display):
        raise Exception()
        
    def _update(self, new_bbox):
        refresh_bbox = [min(self.bbox[0], new_bbox[0]), min(self.bbox[1], new_bbox[1]), max(self.bbox[2], new_bbox[2]), max(self.bbox[2], new_bbox[2])]
        self.bbox = new_bbox
        self.view.redraw(refresh_bbox)

    def delete(self):
        self.view.delete(self)

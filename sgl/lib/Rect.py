

class Rect():
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def x2(self):
        return self.x + self.width

    @property
    def y2(self):
        return self.y + self.height

    def to_tuple(self, coords=False):
        if coords:
            return (self.x, self.y, self.x2, self.y2)
        else:
            return (self.x, self.y, self.width, self.height)

    def make_positive(self):
        if self.width < 0:
            self.width = -self.width
            self.x -= self.width

        if self.height < 0:
            self.height = -self.height
            self.y -= self.height

    def is_in(self, *args):
        if isinstance(args[0], Rect):
            other = args[0]
            return ((other.x2 > self.x) and
                    (other.x < self.x2) and
                    (other.y2 > self.y) and
                    (other.y < self.y2))

        else:
            x, y = args
            return ((x > self.x) and
                    (x < self.x2) and
                    (y > self.y) and
                    (y < self.y2))
            

    def intersect(self, other):
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)

        if x2 >= x and y2 >= y:
            return Rect(x, y, x2-x, y2-y)
        else:
            return None

if __name__ == "__main__":
    # r = Rect(0,0,32,32)
    # r2 = Rect(32, 0, 64, 64)
    # print r.is_in(r2)           # false
    # r.x = 1
    # print r.is_in(r2)           # true
    # r.x = 64
    # print r.is_in(r2)           # true
    # 
    # not expected behavior?

    import sgl
    sgl.init(640, 480)

    r = Rect(0,0,32,32)
    r2 = Rect(200, 200, 400, 200)

    sgl.no_fill()
    sgl.set_stroke(1.0)

    while sgl.is_running():
        sgl.clear(0)

        x = sgl.get_mouse_x()
        y = sgl.get_mouse_y()
        r.x = x - r.width/2
        r.y = y - r.height/2
        sgl.draw_rect(*r.to_tuple())

        with sgl.with_state():
            ir = r2.intersect(r)
            if ir:
                sgl.set_fill(0.5,0,0)
                sgl.set_stroke(1.0,0.5,0.5)
                sgl.draw_rect(*ir.to_tuple())

        with sgl.with_state():
            if r2.is_in(r):
                sgl.set_stroke(1.0,0,0)
            if r2.is_in(x,y):
                sgl.set_stroke_weight(2)
            sgl.draw_rect(*r2.to_tuple())

        sgl.frame()

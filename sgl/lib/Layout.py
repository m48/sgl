import sgl
from sgl.lib.Rect import Rect
from sgl.lib.Sprite import Sprite, EllipseSprite, RectSprite, Scene
import sgl.lib.Time as time

class HorizontalFlow(Sprite):
    def __init__(self):
        super(HorizontalFlow, self).__init__()

        self.spacing = 0
        self.size = 0,0

        self.has_stretchy = False
        self.draw_debug = True

    def add(self, sprite, proportion=0.0):
        super(HorizontalFlow, self).add(sprite)
        sprite.flow_proportion = proportion
        if proportion: self.has_stretchy = True
        self.reflow()

    def reflow(self):
        if self.has_stretchy:
            total_width = 0
            stretchy_total = 0
            stretchy_amount = 0
            last_stretchy = None

            for sprite in self.subsprites:
                if sprite.flow_proportion:
                    stretchy_total += sprite.flow_proportion
                    stretchy_amount += 1
                    last_stretchy = sprite
                else:
                    total_width += sprite.width + self.spacing

            leftover = (self.width - total_width)
            if leftover < 0: leftover = 0
               
        x = 0
        for sprite in self.subsprites:
            sprite.x = int(x)
            width = sprite.width

            if sprite.flow_proportion:
                width = (
                    (leftover / stretchy_total) 
                    * sprite.flow_proportion
                ) 
                if self.spacing:
                    width -= (self.spacing - 
                              (self.spacing/stretchy_amount))
                if width < 0: width = 0
                sprite.width = int(width)
                
            x += width + self.spacing
            
    def draw(self):
        super(HorizontalFlow, self).draw()

        with sgl.with_state():
            sgl.no_fill()
            sgl.set_stroke(0, 1.0, 0)
            sgl.draw_rect(*self.screen_rect.to_tuple())

if __name__ == "__main__":
    sgl.init(640, 480, 1)

    def make_circle(color):
        circle = EllipseSprite()

        circle.no_stroke = True
        circle.fill_color = color

        circle.size = 32, 32

        return circle

    def make_rect(color):
        circle = RectSprite()

        circle.no_stroke = True
        circle.fill_color = color

        circle.size = 32, 32

        return circle

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            blackness = RectSprite()

            blackness.no_stroke = True
            blackness.fill_color = 0

            blackness.size = sgl.get_width(), sgl.get_height()

            self.add(blackness)

            # self.text_rect = RectSprite()

            # self.text_rect.fill_color = 0.25

            # self.add(self.text_rect)

            self.flow = HorizontalFlow()

            self.flow.position = 32,32
            self.flow.size = sgl.get_width()-32-32, 32

            self.flow.spacing = 5

            self.flow.add(make_circle(1.0))
            self.flow.add(make_rect((0, 0.5, 0)), 2.0)
            self.flow.add(make_circle(0.5))
            self.flow.add(make_rect((0, 0.5, 0)), 1.0)
            self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            self.flow.add(make_circle(0.25))

            self.add(self.flow)

        def update(self):
            super(TestScene, self).update()

            x = sgl.get_mouse_x()
            y = sgl.get_mouse_y()

            w = x - self.flow.x
            h = y - self.flow.y

            if w > 0 and h > 0:
                self.flow.size = w, h
            else:
                self.flow.size = 0, 0

            if sgl.is_key_pressed(sgl.key.right):
                self.flow.spacing += 10 * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.left):
                if self.flow.spacing > 0:
                    self.flow.spacing -= 10 * sgl.get_dt()
                    if self.flow.spacing < 0: self.flow.spacing = 0

            self.flow.reflow()

            sgl.set_title("FPS: " + str(sgl.get_fps()))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)



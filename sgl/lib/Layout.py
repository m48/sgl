import sgl
from sgl.lib.Rect import Rect
from sgl.lib.Sprite import Sprite, EllipseSprite, RectSprite, Scene
import sgl.lib.Time as time

class FlowLayout(Sprite):
    def __init__(self, horizontal=False):
        super(FlowLayout, self).__init__()

        self.spacing = 0
        self.size = 0,0

        self._horizontal = horizontal

        self.margin = 0

        self.has_stretchy = False
        self.draw_debug = False

    @property
    def horizontal(self):
        return self._horizontal

    @horizontal.setter
    def horizontal(self, value):
        self._horizontal = value

        for sprite in self.subsprites:
            sprite.width = sprite.original_width
            sprite.height = sprite.original_height

    def add(self, sprite, proportion=0.0, 
            proportion_other_way=False, align=0.0):
        super(FlowLayout, self).add(sprite)
        sprite.flow_proportion = proportion
        sprite.flow_other_proportion = proportion_other_way
        sprite.flow_align = align
        
        sprite.original_width = sprite.width
        sprite.original_height = sprite.height

        if proportion: self.has_stretchy = True
        self.reflow()

    def clear(self):
        self.subsprites = []
        self.has_stretchy = False

    def reflow(self):
        self_size = (self.width if self.horizontal else self.height) - self.margin*2
        self_other_size = (self.height if self.horizontal else self.width) - self.margin*2

        if self.has_stretchy:
            total_size = 0
            stretchy_total = 0
            stretchy_amount = 0
            last_stretchy = None

            for sprite in self.subsprites:
                if sprite.flow_proportion:
                    stretchy_total += sprite.flow_proportion
                    stretchy_amount += 1
                    last_stretchy = sprite
                else:
                    total_size += (sprite.width if self.horizontal else sprite.height) + self.spacing

            leftover = (self_size - total_size)
            if leftover < 0: leftover = 0
               
        offset = self.margin
        for sprite in self.subsprites:
            if self.horizontal:
                sprite.x = int(offset)
            else:
                sprite.y = int(offset)

            size = sprite.width if self.horizontal else sprite.height
            other_size = sprite.height if self.horizontal else sprite.width
    
            if sprite.flow_proportion:
                size = (
                    (leftover / stretchy_total) 
                    * sprite.flow_proportion
                ) 
                if self.spacing:
                    size -= (self.spacing - 
                             (self.spacing/stretchy_amount))
                if size < 0: size = 0

                if self.horizontal:
                    sprite.width = int(size)+1
                else:
                    sprite.height = int(size)+1

            if sprite.flow_other_proportion:
                new_size = self_other_size * sprite.flow_other_proportion

                if self.horizontal:
                    sprite.height = int(new_size)
                else:
                    sprite.width = int(new_size)

                if (hasattr(sprite, "reflow") 
                    and hasattr(sprite.reflow, "__call__")):
                    sprite.reflow()

            if sprite.flow_align:
                other_offset = (
                    self_other_size * sprite.flow_align
                    - other_size * sprite.flow_align
                ) + self.margin

                if self.horizontal:
                    sprite.y = int(other_offset)
                    if sprite.y < self.margin: 
                        sprite.y = int(self.margin)
                else:
                    sprite.x = int(other_offset)
                    if sprite.x < self.margin: 
                        sprite.x = int(self.margin)
            else:
                if self.horizontal:
                    sprite.y = int(self.margin)
                else:
                    sprite.x = int(self.margin)
    
            offset += size + self.spacing
            
    def draw(self):
        super(FlowLayout, self).draw()
        
        if self.draw_debug:
            with sgl.with_state():
                sgl.no_fill()

                sgl.set_stroke(0, 0.5, 0)
                sgl.draw_rect(self.screen_x + self.margin,
                              self.screen_y + self.margin,
                              self.width - self.margin*2,
                              self.height - self.margin*2)

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

            self.flow_rect = RectSprite()

            self.flow_rect.size = 0,0

            self.flow_rect.no_stroke = True
            self.flow_rect.fill_color = 0.25

            self.add(self.flow_rect)

            self.flow = FlowLayout(False)

            self.flow.position = 32,32
            self.flow.size = sgl.get_width()-32-32, 32

            self.flow.spacing = 5

            self.flow.add(make_circle(1.0), 0, 0, 0)
            self.flow.add(make_circle(1.0), 0, 0, 0.75)
            self.flow.add(make_circle(1.0), 0, 0, 1.00)
            self.flow.add(make_rect(0.50), 0.25, 0.75, 0.5)

            self.flow2 = FlowLayout(True)
            self.flow2.size = 50, 200

            self.flow2.add(make_rect(0.75), 1.0, 1.0, 0)            
            self.flow2.add(make_circle(1.0), 0, 0, 0.5)
            self.flow2.add(make_circle(1.0), 0, 0, 0.5)
            self.flow2.add(make_rect(0.75), 1.0, 1.0, 0)

            self.flow.add(self.flow2, 1.0, 1.0, 0)

            # self.flow.add(make_rect(0.75), 1.0, 1.0, 0)

            self.flow.add(make_rect(0.50), 0.25, 0.75, 0.5)
            self.flow.add(make_circle(1.0), 0, 0, 1.00)
            self.flow.add(make_circle(1.0), 0, 0, 0.75)
            self.flow.add(make_circle(1.0), 0, 0, 0)

            # self.flow.add(make_rect((0, 0.5, 0)), 2.0, 1.0)
            # self.flow.add(make_circle(0.5), 0, 0, 1.0)
            # self.flow.add(make_rect((0, 0.5, 0)), 1.0, 0.5, 0.5)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0, 0, 0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_circle(0.25))

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

            self.flow_rect.position = self.flow.position
            # for some reason self.flow.size returns (32,32) constantly.
            # look into this :(
            # self.flow_rect.size = self.flow.size
            self.flow_rect.size = self.flow.width, self.flow.height

            if sgl.is_key_pressed(sgl.key.right 
                                  if self.flow.horizontal 
                                  else sgl.key.down):
                self.flow.spacing += 10 * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.left 
                                  if self.flow.horizontal 
                                  else sgl.key.up):
                if self.flow.spacing > 0:
                    self.flow.spacing -= 10 * sgl.get_dt()
                    if self.flow.spacing < 0: self.flow.spacing = 0

            if sgl.is_key_pressed(sgl.key.down 
                                  if self.flow.horizontal 
                                  else sgl.key.right):
                self.flow.margin += 10 * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.up
                                  if self.flow.horizontal 
                                  else sgl.key.left):
                if self.flow.margin > 0:
                    self.flow.margin -= 10 * sgl.get_dt()
                    if self.flow.margin < 0: self.flow.margin = 0

            if sgl.on_mouse_up():
                self.flow.horizontal = not self.flow.horizontal
                self.flow.reflow()

            self.flow.reflow()

            sgl.set_title("FPS: " + str(sgl.get_fps()))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)



import sgl
from sgl.lib.Sprite import Sprite, RectSprite, Scene, Viewport
from sgl.lib.Layout import FlowLayout
import sgl.lib.Tween as tween

class MenuItem(Sprite):
    def __init__(self, text, action=None, selectable=True):
        super(MenuItem, self).__init__()
        
        self.text = text
        self.action = action

        self.size = 0,20

        self.selected = False
        self.selectable = selectable

        self.draw_debug = False # True

    def reflow(self):
        pass

    def update(self):
        super(MenuItem, self).update()

    def draw(self):
        super(MenuItem, self).draw()    

        with sgl.with_state():
            sgl.draw_text(self.text, self.screen_x, self.screen_y)
            if self.draw_debug and self.selected:
                sgl.no_fill()
                sgl.set_stroke(0, 1.0, 0)
                sgl.draw_rect(*self.screen_rect.to_tuple())

class Menu(Sprite):
    def __init__(self):
        super(Menu, self).__init__()

        self.on_before_init()
        
        self.viewport = Viewport()
        
        self.layout = FlowLayout()
        self.layout.height = 2000
        self.viewport.add(self.layout)

        self.interior_margin = 0
        self.spacing = 0
        self.exterior_margin = 0

        self.animating = False

        self.loop_selection = False

        self.selected_index = 0

    def on_before_init(self):
        pass

    def add_item(self, item):
        self.layout.add(item, 0, 1.0)
        self.layout.reflow()

        if self.viewport not in self.subsprites:
            self.add(self.viewport)

        if len(self.items)-1 == self.selected_index:
            if item.selectable:
                # in case camera is moved up
                self.preupdate()
                self.update()

                self.set_selection(self.selected_index, system=True)
            else:
                self.selected_index += 1

    @property
    def first_visible_index(self):
        for index, item in enumerate(self.items):
            if self.items[index].screen_y < 0:
                pass
            else:
                return index

    @property
    def first_visible_item(self):
        return self.items[self.first_visible_index]

    @property
    def last_visible_index(self):
        last_index = 0
        for index, item in enumerate(self.items):
            if self.items[index].screen_y + self.items[index].height > self.viewport.height:
                break
            else:
                last_index = index

        return last_index

    @property
    def last_visible_item(self):
        return self.items[self.last_visible_index]

    @property
    def scroll_destination(self):

        if self.selection.screen_y + self.selection.height > self.viewport.screen_y + self.viewport.height: 
            return (self.selection.y+self.selection.height) - self.viewport.height
        elif self.selection.screen_y < self.viewport.screen_y:
            return self.selection.y
        else:
            return self.scroll

    @property
    def scroll(self):
        return -self.viewport.camera.y

    @scroll.setter
    def scroll(self, value):
        self.viewport.camera.y = -value
        if self.selection:
            self.layout.preupdate()
            self.selection.preupdate()

    def set_selection(self, new_value, system=False):
        self.selection.selected = False
        self.selected_index = new_value
        self.selection.selected = True
        self.scroll = self.scroll_destination
        self.on_selection(system)

    def on_selection(self):
        pass

    def next_item(self):
        index = self.selected_index + 1

        while True:
            if index > len(self.items)-1:
                if self.loop_selection: index = 0
                else:
                    self.on_invalid_selection() 
                    return

            if index == self.selected_index:
                self.on_invalid_selection()
                return
            elif self.items[index].selectable:
                break
            else:
                index += 1
        
        self.set_selection(index)

    def prev_item(self):
        index = self.selected_index - 1

        while True:
            if index < 0:
                if self.loop_selection: index = len(self.items)-1
                else: 
                    self.on_invalid_selection()
                    return

            if index == self.selected_index:
                self.on_invalid_selection()
                return
            elif self.items[index].selectable:
                break
            else:
                index -= 1

        self.set_selection(index)

    def on_invalid_selection(self):
        pass

    @property
    def selection(self):
        if len(self.items) != 0:
            return self.items[self.selected_index]
        else:
            return None

    @property
    def items(self):
        return self.layout.subsprites

    def reflow(self):
        self.viewport.x = self.exterior_margin
        self.viewport.y = self.exterior_margin
        self.viewport.width = self.width - self.exterior_margin*2
        self.viewport.height = self.height - self.exterior_margin*2

        self.layout.width = self.viewport.width
        # self.layout.height = self.layout.min_height
        self.layout.spacing = self.spacing
        self.layout.margin = self.interior_margin
        self.layout.reflow()

    def update(self):
        super(Menu, self).update()

        if not self.animating:
            if sgl.on_key_up(sgl.key.up):
                self.prev_item()
            if sgl.on_key_up(sgl.key.down):
                self.next_item()

if __name__ == "__main__":
    sgl.init(640, 480, 1)
    sgl.set_font(sgl.load_system_font("Arial", 20))

    class TestMenu1(Menu):
        def __init__(self):
            super(TestMenu1, self).__init__()

            self.position = 32,32
            self.size = 200, 200
            self.exterior_margin = 5
            self.reflow()

            self.loop_selection = True

            box = RectSprite()
            box.fill_color = 0.50
            box.size = self.width, self.height
            self.add(box)

            self.selection_box = RectSprite()
            self.selection_box.fill_color = (1.0, 0.25)
            self.selection_box.size = 0, 0
            self.selection_box.fixed = True
            self.add(self.selection_box)

            self.add_item(MenuItem("--- stuff ----", selectable=False))
            self.add_item(MenuItem("hi there"))
            self.add_item(MenuItem("cool"))
            self.add_item(MenuItem("", selectable=False))

            self.add_item(MenuItem("--- stuff ----", selectable=False))
            self.add_item(MenuItem("more stuff"))
            self.add_item(MenuItem("more cool"))
            self.add_item(MenuItem("", selectable=False))

            self.add_item(MenuItem("--- scrolling test ----", selectable=False))
            for number in range(10):
                self.add_item(MenuItem("item #" + str(number)))

            # self.on_selection(False)

        def unanimate(self):
            self.animating = False

        def on_selection(self, system):
            # self.animating = True

            if system:
                self.selection_box.x = self.selection.screen_x
                self.selection_box.y = self.selection.screen_y
                self.selection_box.size = self.selection.size
            else:
                tween.to(
                    self.selection_box, 
                    {'x': self.selection.screen_x,
                     'y': self.selection.screen_y,
                     'width': self.selection.width,
                     'height': self.selection.height},
                    0.10,
                    tween.Easing.ease_out,
                    done_callback=self.unanimate
                )

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            blackness = RectSprite()

            blackness.no_stroke = True
            blackness.fill_color = 0.25

            blackness.size = sgl.get_width(), sgl.get_height()

            self.add(blackness)

            self.add(TestMenu1())

        def update(self):
            super(TestScene, self).update()
            
            tween.update(sgl.get_dt())
            # self.menu.spacing += 10 * sgl.get_dt()
            # self.menu.viewport.camera.y += 100 * sgl.get_dt()
            # self.menu.reflow()

            sgl.set_title("FPS: " + str(sgl.get_fps()))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)


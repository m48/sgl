import sgl
from sgl.lib.Sprite import Sprite, RectSprite, Scene, Viewport, App
from sgl.lib.Layout import FlowLayout
import sgl.lib.Tween as tween
import sgl.lib.Time as time

class Menu(Sprite):
    def __init__(self):
        super(Menu, self).__init__()

        self.viewport = Viewport()
        
        self.layout = FlowLayout()
        self.viewport.add(self.layout)

        self.interior_margin = 0
        self.spacing = 0
        self.exterior_margin = 0

        self.repeat_delay = 0.25
        self.repeat_interval = 0.10

        self.center_vertical = False

        self.animating = False
        self.focused = True

        self.loop_selection = False

        self.selected_index = 0

        self.parent_menu = None

        self.repeat_object = None

        self.visible = False

    def on_add(self):
        self.update_selection()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

        if self.parent and hasattr(self.parent, "focused"):
            self.parent.focused = True
        elif self.parent_menu:
            self.parent_menu.focused = True

        self.kill()

    def add_item(self, item):
        if item.width == 0:
            self.layout.add(item, 0, 1.0)
        else:
            self.layout.add(item, 0, 0, 0.5)

        if self.viewport not in self.subsprites:
            self.add(self.viewport)

        if len(self.items)-1 == self.selected_index:
            if item.selectable:
                self.update_selection()
            else:
                self.selected_index += 1

    def update_selection(self):
        # in case camera is moved up
        self.update_screen_positions()
                
        self.set_selection(self.selected_index, system=True)

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
        if self.selected_index == 0:
            return 1
        elif self.selection.screen_y + self.selection.height > self.viewport.screen_y + self.viewport.height: 
            return (self.selection.y+self.selection.height) - self.viewport.height
        elif self.selection.screen_y < self.viewport.screen_y:
            return self.selection.y
        else:
            return None

    @property
    def scroll(self):
        return self.viewport.camera.y

    @scroll.setter
    def scroll(self, value):
        self.viewport.camera.y = value
        if self.selection:
            self.layout.preupdate()
            self.selection.preupdate()

    def set_selection(self, new_value, system=False):
        self.selection.selected = False
        self.selected_index = new_value
        self.selection.selected = True
        self.on_selection(system)

    def on_selection(self, system=False):
        pass

    def on_command(self):
        if self.selection.action:
            self.selection.action()

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
                if self.loop_selection: 
                    index = len(self.items)-1
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
        self.layout.spacing = self.spacing
        self.layout.margin = self.interior_margin

        self.layout.reflow()

        self.layout.height = self.layout.min_height

        if self.layout.height and self.center_vertical and self.layout.height < self.viewport.height:
            self.layout.y = (self.viewport.height-self.layout.height)/2
        else:
            self.layout.y = 0

        self.update_selection()

    def start_repeat(self):
        if self.repeat_object:
            self.repeat_object.stop()
            self.repeat_object = None
            return

        if sgl.is_key_pressed(sgl.key.up):
            self.repeat_object = time.set_interval(self.repeat_interval, self.prev_item)
        elif sgl.is_key_pressed(sgl.key.down):
            self.repeat_object = time.set_interval(self.repeat_interval, self.next_item)

    def update(self):
        super(Menu, self).update()

        if self.focused and not self.animating:
            if sgl.on_key_down(sgl.key.up):
                self.prev_item()
                time.set_timeout(self.repeat_delay, self.start_repeat)
            elif sgl.on_key_down(sgl.key.down):
                self.next_item()
                time.set_timeout(self.repeat_delay, self.start_repeat)
            elif not (sgl.is_key_pressed(sgl.key.up) 
                    or sgl.is_key_pressed(sgl.key.down)):
                if self.repeat_object:
                    self.repeat_object.stop()
                    self.repeat_object = None
            
            if sgl.on_key_down(sgl.key.enter):
                self.on_command()

class MenuItem(Sprite):
    def __init__(self, text, action=None, selectable=True):
        super(MenuItem, self).__init__()
        
        self.text = text
        self.action = action

        self.size = 0,sgl.get_text_height("")+5

        self.selected = False
        self.selectable = selectable

        self.draw_debug = False

    def reflow(self):
        pass

    def update(self):
        super(MenuItem, self).update()

    def draw_self(self):
        with sgl.with_state():
            # sgl.set_fill(0)
            # sgl.draw_text(self.text, self.screen_x+1, self.screen_y+1)
            sgl.set_fill(1.0)
            sgl.draw_text(self.text, self.screen_x, self.screen_y)
            if self.draw_debug and self.selected:
                sgl.no_fill()
                sgl.set_stroke(0, 1.0, 0)
                sgl.draw_rect(*self.screen_rect.to_tuple())

class BoxMenu(Menu):
    def __init__(self):
        super(BoxMenu, self).__init__()

        self.exterior_margin = 5

        self.loop_selection = True

        self.box = RectSprite()
        self.box.fill_color = 0.50
        self.box.size = 0,0
        self.add(self.box)

        self.side = "bottom"

        self.selection_box = RectSprite()
        self.selection_box.fill_color = (1.0, 0.25)
        self.selection_box.size = 0, 0
        self.selection_box.cancel_parent_transform = True
        self.add(self.selection_box)

    def reflow(self):
        super(BoxMenu, self).reflow()

        self.box.size = self.width, self.height            

    def show(self):
        self.visible = True
        self.animating = True
        self.selection_box.visible = False

        x, y = self.side_to_coords()
        tween.from_orig(self,
                        {'x': x, 'y': y},
                        0.25,
                        tween.Easing.ease_out,
                        done_callback=self.unanimate)

    def hide(self):
        self.animating = True
        self.selection_box.visible = False

        x, y = self.side_to_coords()
        tween.to(self,
                 {'x': x, 'y': y},
                 0.25,
                 tween.Easing.ease_out,
                 done_callback=self.hide_finish)

    def hide_finish(self):
        super(BoxMenu, self).hide()

    def side_to_coords(self):
        x = self.x
        y = self.y
        if self.side == "left":
            x = -self.width
        elif self.side == "right":
            x = sgl.get_width()
        elif self.side == "top":
            y = -self.height
        elif self.side == "bottom":
            y = sgl.get_height()
        return x,y

    def unanimate(self):
        self.animating = False
        self.selection_box.visible = True

    def on_selection(self, system):
        if system:
            if self.scroll_destination:
                self.scroll = self.scroll_destination

            self.selection_box.x = self.selection.screen_x
            self.selection_box.y = self.selection.screen_y
            self.selection_box.size = self.selection.size

            # print self.selection_box.position
        else:
            old_scroll = None
            scroll_destination = self.scroll_destination
            if scroll_destination:
                old_scroll = self.scroll
                self.scroll = scroll_destination

            tween.to(
                self.selection_box, 
                {'x': self.selection.screen_x,
                 'y': self.selection.screen_y,
                 'width': self.selection.width,
                 'height': self.selection.height},
                0.10,
                tween.Easing.ease_out
            )

            if old_scroll != None:
                self.scroll = old_scroll
                self.animating = True
                # self.selection_box.visible = False

                tween.to(
                    self,
                    {'scroll': scroll_destination},
                    0.10,
                    tween.Easing.ease_out,
                    done_callback=self.unanimate
                )

class ButtonMenuItem(Sprite):
    def __init__(self, text, action=None, selectable=True):
        super(ButtonMenuItem, self).__init__()
        
        self.text = text
        self.action = action

        self.size = sgl.get_width()/2, sgl.get_text_height("")+5

        self.selected = False
        self.selectable = selectable

    def show(self, index):
        tween.from_orig(
            self,
            {'x': self.parent.width + self.width},
            0.25,
            tween.Easing.ease_in,
            delay=index*0.1
        )

    def hide(self, index):
        if self.selected:
            tween.to(
                self,
                {'y': -sgl.get_height()},
                0.25,
                tween.Easing.ease_in
            )
        else:
            tween.to(
                self,
                {'x': -self.width},
                0.25,
                tween.Easing.ease_out
            )

    def reflow(self):
        pass

    def update(self):
        super(ButtonMenuItem, self).update()

    def draw_self(self):
        with sgl.with_state():
            if self.selected:
                sgl.set_fill(0.25)
            else:
                sgl.set_fill(0)

            sgl.draw_rect(*self.screen_rect.to_tuple())

            sgl.set_fill(1.0)
            x = (self.width-sgl.get_text_width(self.text))/2
            sgl.draw_text(self.text, self.screen_x+x, self.screen_y)

class ButtonMenu(Menu):
    def __init__(self):
        super(ButtonMenu, self).__init__()

        self.position = 0, 0
        self.size = sgl.get_width(), sgl.get_height()

        self.spacing = 10
        self.center_vertical = True
        self.animation_time = 0.25
        self.item_delay = 0.10
    
    def show(self):
        self.visible = True
        self.animating = True

        for index, item in enumerate(self.items):
            item.show(index)

        wait_time = self.animation_time + self.item_delay*(len(self.items)-1)
        time.set_timeout(wait_time, self.unanimate)

    def hide(self):
        self.animating = True

        for index, item in enumerate(self.items):
            item.hide(index)

        wait_time = self.animation_time + self.item_delay*(len(self.items)-1)
        time.set_timeout(wait_time, self.hide_finish)

    def hide_finish(self):
        super(ButtonMenu, self).hide()

    def unanimate(self):
        self.animating = False

if __name__ == "__main__":
    sgl.init(640, 480, 1)
    # sgl.set_fps_limit(15)
    sgl.set_font(sgl.load_system_font("Arial", 20))

    class TestMenu1(BoxMenu):
        def __init__(self):
            super(TestMenu1, self).__init__()

            self.center_vertical = True
            self.position = 32,32
            self.size = 200, 200

            self.add_item(MenuItem("Show Other Menu", action=self.show_other_menu))
            self.add_item(MenuItem("Show Scrolling Test", action=self.show_scroll))
            self.add_item(MenuItem("Show Button Menu", action=self.show_buttons))
            self.add_item(MenuItem("", selectable=False))

            self.add_item(MenuItem("- Unselectable", selectable=False))
            self.add_item(MenuItem("Random"))

            self.reflow()

        def show_other_menu(self):
            menu = self.add(TestMenu2())
            menu.show()
            self.focused = False

        def show_scroll(self):
            menu = self.add(TestMenu3())
            menu.show()
            self.focused = False

        def show_buttons(self):
            menu = self.scene.add(TestMenu4())
            menu.show()
            menu.parent_menu = self
            self.focused = False

    class TestMenu2(BoxMenu):
        def __init__(self):
            super(TestMenu2, self).__init__()

            self.position = 210,0
            self.size = 200, 200

            self.add_item(MenuItem("Hi there"))
            self.add_item(MenuItem("Cool"))
            self.add_item(MenuItem("< Close", action=self.hide))

            self.reflow()

    class TestMenu3(BoxMenu):
        def __init__(self):
            super(TestMenu3, self).__init__()

            self.side = "right"
            self.position = 210,0
            self.size = 200, 200

            for number in range(1,21):
                self.add_item(MenuItem("Item #" + str(number)))
            self.add_item(MenuItem("< Close", action=self.hide))

            self.reflow()

    class TestMenu4(ButtonMenu):
        def __init__(self):
            super(TestMenu4, self).__init__()

            self.add_item(ButtonMenuItem("Hi there"))
            self.add_item(ButtonMenuItem("Cool"))
            self.add_item(ButtonMenuItem("< Close", action=self.hide))

            self.reflow()

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            self.background_color = 0.25

            menu = TestMenu1()
            self.add(menu)
            menu.show()

        def update(self):
            super(TestScene, self).update()
            
            tween.update(sgl.get_dt())
            time.update(sgl.get_dt())

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    app = App(TestScene())

    sgl.run(app.update, app.draw)


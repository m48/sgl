import sgl
from sgl.lib.Rect import Rect
from sgl.lib.Sprite import Sprite, Scene

def is_string(thing):
    """ Returns whether `thing` is a string or not. """

    if 'basestring' not in globals():
        return isinstance(thing, str)
    else:
        return isinstance(thing, basestring)

class Block(object):
    def __init__(self, font, color, text):
        self.font = font
        self.color = color
        self.text = text

    @property
    def style(self):
        return (self.font, self.color)

    @property
    def width(self):
        with sgl.with_state():
            sgl.set_font(self.font)
            return sgl.get_text_width(self.text)

    @property
    def height(self):
        with sgl.with_state():
            sgl.set_font(self.font)
            return sgl.get_text_height("")

    def draw(self, x, y, debug=False):
        if debug:
            with sgl.with_state():
                sgl.no_fill()
                sgl.set_stroke(0, 0.50, 0)
                sgl.draw_rect(x, y, self.width, self.height)

        with sgl.with_state():
            sgl.set_font(self.font)
            sgl.set_fill(self.color)
            sgl.draw_text(self.text, x, y)

class Line(object):
    def __init__(self):
        self.items = []
        self.ends_in_newline = False

    def draw(self, x, y, debug=False):
        if debug:
            with sgl.with_state():
                sgl.no_fill()
                sgl.set_stroke(0, 0.75, 0)
                sgl.draw_rect(x, y, self.width, self.height)

        line_height = self.height
        x_offset = 0
        for item in self.items:
            item_height = item.height
            item.draw(
                x + x_offset, 
                y + (line_height-item_height), 
                debug
            )
            x_offset += item.width

    def add(self, block):
        self.items.append(block)

    @property
    def empty(self):
        return (len(self.items) == 0)

    @property
    def last_item(self):
        if self.empty:
            return None
        else:
            return self.items[-1]
    
    @property
    def width(self):
        result = 0
        for item in self.items:
            result += item.width
        return result

    @property
    def height(self):
        result = 0
        for item in self.items:
            height = item.height
            if height > result: result = height
        return result

class TextSprite(Sprite):
    def __init__(self):
        super(TextSprite, self).__init__()
        self._text = ""

        self.line_spacing = 10

        self.data = [Line()]

        self.font = None
        self.color = (1.0,)

        self.draw_debug = True

    @property
    def last_line(self):
        return self.data[-1]

    def new_line(self):
        self.data.append(Line())

    def add_block(self, block):
        if not self.can_handle_block(block):
            self.new_line()

        last_item = self.last_line.last_item
        if last_item and last_item.style == block.style:
            last_item.text += block.text
        else:
            self.last_line.add(block)
        
    def can_handle_block(self, block):
        total_width = self.last_line.width + block.width
        return total_width < self.width

    def reflow(self):
        data = self.data[:]
        self.clear()

        for line in data:
            for block in line.items:
                # print block.text
                self.font, self.color = block.style
                self.add_text(block.text)

            if line.ends_in_newline:
                self.add_text("\n")

    def clear(self):
        self.data = [Line()]

    def add_text(self, text):
        if text == "": 
            self.add_block(Block(self.font, self.color, ""))            
            return

        result = ""
        wrap_chars = (' ', '-')
        special_chars = ('\n',)
        watch_chars = wrap_chars + special_chars

        # Helps us avoid dealing with trailing words
        if text[-1] not in wrap_chars:
            text += wrap_chars[0]
            last_char_fake = True
        else:
            last_char_fake = False

        for index, char in enumerate(text):
            if (char not in special_chars and
                not (last_char_fake and index == len(text)-1)):
                result += char

            if char in watch_chars:
                self.add_block(Block(self.font, self.color, result))
                result = ""

                if char == "\n": 
                    self.last_line.ends_in_newline = True
                    self.new_line()

    def set_font(self, font):
        self.font = font

    def set_color(self, color):
        self.font = font

    def draw(self):
        y = 0
        for line in self.data:
            line.draw(self.screen_x, self.screen_y + y, self.draw_debug)
            y += line.height + self.line_spacing

        if self.draw_debug:
            with sgl.with_state():
                sgl.no_fill()
                sgl.set_stroke(0, 1.0, 0)
                sgl.draw_rect(*self.screen_rect.to_tuple())

if __name__ == "__main__":
    # sgl.init(320, 240, 2)
    sgl.init(640, 480, 1)
    # sgl.init(1280, 720, 1)

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            surface = sgl.make_surface(sgl.get_width(), 
                                       sgl.get_height(), 
                                       0)
            bg = Sprite(surface)

            self.add(bg)

            f = sgl.load_system_font("Arial", 20)
            f2 = sgl.load_system_font("Arial Black", 20)

            self.text = TextSprite()
            self.text.position = 32, 32
            self.text.size = 200, 200
            self.text.line_spacing = 0

            self.text.font = f
            self.text.color = 1.0
            self.text.add_text("Hello there. This is really cool and stuff, I like cheese and stuff.\n\nYeah ")

            self.text.font = f2
            self.text.color = (0.5,)
            self.text.add_text("no really and stuff.")            

            self.add(self.text)

        def update(self):
            super(TestScene, self).update()

            x = sgl.get_mouse_x()
            y = sgl.get_mouse_y()

            w = x - self.text.x
            h = y - self.text.y

            if w > 0 and h > 0:
                self.text.size = w, h
            else:
                self.text.size = 0, 0

            self.text.reflow()

    scene = TestScene()

    sgl.run(scene.update, scene.draw)


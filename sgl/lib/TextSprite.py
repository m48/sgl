import sgl
from sgl.lib.Rect import Rect
from sgl.lib.Sprite import Sprite, RectSprite, Scene
import sgl.lib.Time as time

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
        self.line_height = 0

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
        if self.line_height:
            return self.line_height

        result = 0
        for item in self.items:
            height = item.height
            if height > result: result = height
        return result

class TextSprite(Sprite):
    def __init__(self):
        super(TextSprite, self).__init__()
        self._text = ""

        self.line_spacing = 0

        self.data = [Line()]

        self.font = None
        self.color = (1.0,)
        self.line_height = 0
        self.auto_height = False
        self.text_align = 0

        self.draw_debug = False

        self.actual_word_box = None

        self.wrap_chars = (' ', '-')

    @property
    def actual_current_word(self):
        if self.actual_word_box:
            return self.actual_word_box.text
        else:
            return ""

    @actual_current_word.setter
    def actual_current_word(self, value):
        self.actual_word_box = Block(self.font, self.color, value)

    @property
    def last_line(self):
        return self.data[-1]

    @property
    def last_line_index(self):
        return len(self.data)-1

    def new_line(self):
        self.data.append(Line())
        self.last_line.line_height = self.line_height

    def add_block(self, block):
        last_item = self.last_line.last_item

        if not self.can_handle_block(block):
            if (last_item and 
                last_item.text and 
                last_item.text[-1] in self.wrap_chars):
                self.new_line()
                last_item = self.last_line.last_item
            elif not last_item:
                pass
            elif not self.actual_current_word:
                split_point = last_item.text.rfind(self.wrap_chars[0])+1
                before = last_item.text[:split_point]
                after = last_item.text[split_point:]

                last_item.text = before
                new_block = Block(*last_item.style, text=after)

                self.new_line()
                self.last_line.add(new_block)

                last_item = self.last_line.last_item

        if last_item and last_item.style == block.style:
            last_item.text += block.text
        else:
            self.last_line.add(block)
        
    def can_handle_block(self, block):
        if self.actual_current_word:
            return self.last_line.width + self.actual_word_box.width < self.width
        else:
            total_width = self.last_line.width + block.width
            return total_width < self.width

    def reflow(self, start_line=0):
        if self.width == 0: return

        if start_line == 0:
            data = self.data[:]
            self.clear()
        else:
            data = self.data[start_line:]
            del self.data[start_line:]

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
        special_chars = ('\n',)
        watch_chars = self.wrap_chars + special_chars

        # Helps us avoid dealing with trailing words
        if text[-1] not in self.wrap_chars:
            text += self.wrap_chars[0]
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

    def get_line_y(self, line_index):
        y = 0
        for index, line in enumerate(self.data):
            if line_index == index: break
            y += line.height + self.line_spacing
        return y

    def get_line_x(self, line_index):
        if self.text_align:
            line = self.data[line_index]
            return (self.width * self.text_align
                    - line.width * self.text_align)
        else:
            return 0

    def draw_self(self):
        x = 0
        y = 0
        for line in self.data:
            if self.text_align:
                x = (self.width * self.text_align
                     - line.width * self.text_align)

            line.draw(self.screen_x + x, self.screen_y + y, self.draw_debug)

            y += line.height + self.line_spacing

        # I would like to do this in one of the add_text functions or
        # whatever, but right now this seems a lot easier
        if self.auto_height:
            self.height = y

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

            self.f = sgl.load_system_font("Arial", 20)
            self.f2 = sgl.load_system_font("Impact", 20)

            self.text_rect = RectSprite()

            self.text_rect.fill_color = 0.25

            self.add(self.text_rect)

            self.text = TextSprite()

            self.text.position = 32, 32
            self.text.size = 200, 200

            self.text.font = self.f
            self.text.color = 1.0
            self.text.add_text("Hello there. This is really cool and stuff, I like cheese and stuff.\n\nYeah ")

            self.text.font = self.f2
            self.text.color = 0.5
            self.text.add_text("no really and stuff.")

            self.add(self.text)

            self.text2 = TextSprite()

            self.text2.position = 400, 32
            self.text2.size = 200, 200
            self.text2.font = self.f
            self.text2.auto_height = True
            self.text2.line_height = 25
 
            self.add(self.text2)

            self.text3 = TextSprite()

            self.text3.position = 400, 32+200
            self.text3.size = 200, 40
            self.text3.font = self.f
            self.text3.text_align = 0.5

            self.add(self.text3)

            self.message = "In this world, there are a lot of things we don't understand. In particular, the best way to pull off a stupid algorithm like this one."
            self.index = 0
            self.use_current_word = False

            time.at_fps(30, self.update_typing)

        def update_typing(self):
            if self.index < len(self.message):
                if self.index < self.message.find(". ")+1:
                    self.text2.color = 1.0
                    self.text2.font = self.f
                else:
                    self.text2.color = 0.75
                    self.text2.font = self.f2    

                if self.use_current_word:
                    start = self.message.rfind(" ", 0, self.index)+1

                    end = self.message.find(" ", self.index)+1
                    if end == 0: end = len(self.message)-1

                    current_word = self.message[start:end]

                    self.text2.actual_current_word = current_word
                    self.text2.add_text(self.message[self.index])

                    self.text3.clear()
                    self.text3.color = 1.0
                    self.text3.add_text(self.text2.actual_current_word)
                    self.text3.color = 0.5
                    self.text3.add_text(" ({}, {})".format(start, end))

                else:
                    self.text2.actual_current_word = ""
                    self.text2.add_text(self.message[self.index])

                    self.text3.clear()
                    self.text3.color = 0.5
                    self.text3.add_text("Not using current word feature")
                
                self.index += 1

        def update(self):
            super(TestScene, self).update()
            time.update(sgl.get_dt())

            x = sgl.get_mouse_x()
            y = sgl.get_mouse_y()

            w = x - self.text.x
            h = y - self.text.y

            if w > 0 and h > 0:
                self.text.size = w, h
            else:
                self.text.size = 0, 0

            self.text.reflow()

            padding = 5

            self.text_rect.x = self.text.x - padding
            self.text_rect.y = self.text.y - padding
            self.text_rect.width = self.text.width + padding*2
            self.text_rect.height = self.text.height + padding*2

            if sgl.on_mouse_up():
                self.use_current_word = not self.use_current_word
                self.text2.clear()
                self.index = 0

            if sgl.on_key_up(sgl.key.space):
                self.text.draw_debug = not self.text.draw_debug
                self.text2.draw_debug = not self.text2.draw_debug
                self.text3.draw_debug = not self.text3.draw_debug

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)


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
    def __init__(self, font, text):
        self.font = font
        self.text = text

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

    def draw(self, x, y):
        with sgl.with_state():
            sgl.set_font(self.font)
            sgl.draw_text(self.text, x, y)

class Line(object):
    def __init__(self):
        self.items = []

    def draw(self, x, y):
        h = self.height
        xo = 0
        for item in self.items:
            ih = item.height
            item.draw(x + xo, y + (h-ih))
            xo += item.width

    def add(self, block):
        self.items.append(block)

    @property
    def empty(self):
        return len(self.items) == 0
    
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
        self.color = (0,)

    @property
    def last_line(self):
        return self.data[-1]

    def new_line(self):
        self.data.append(Line())

    def add_block(self, block):
        if not self.can_handle_block(block):
            self.new_line()

        self.last_line.add(block)
        
    def can_handle_block(self, block):
        total_width = self.last_line.width + block.width
        return total_width < self.width

    def add_text(self, text):
        pass

        # last_line = self.data[-1]
        # width = last_line.width
        

        # if len(last_line) > 0:
        #     last_item = last_line[-1]
        # elif len(self.data) > 1:
        #     last_item = self.data[-2][-1]
        # else:
        #     last_item = None

        

   
    def set_font(self, font):
        self.font = font

    def draw(self):
        y = 0
        for line in self.data:
            line.draw(self.x, self.y + y)
            y += line.height + self.line_spacing

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

            text = TextSprite()
            text.position = 32, 32
            text.size = 200, 200
            text.add_block(Block(f, "hi there "))
            text.add_block(Block(f2, "we "))
            text.add_block(Block(f, "are cool "))
            text.add_block(Block(f, "are cool "))
            text.add_block(Block(f, "are cool "))
            text.add_block(Block(f, "are cool "))
            text.add_block(Block(f, "are cool "))
            self.add(text)
            

        def update(self):
            super(TestScene, self).update()

    scene = TestScene()

    sgl.run(scene.update, scene.draw)


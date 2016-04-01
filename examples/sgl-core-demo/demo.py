import sgl

sgl.init(320, 240, 2)

font = sgl.load_font("ChicagoFLF.ttf", 12)
sgl.set_font(font)
sgl.set_font_smooth(False)

class TestDemo():
    name = "Title Screen"
    description = "Welcome to SGL's demo! Use the arrow keys to navigate between demos and stuff. Have fun!"

    x = 0
    vel = 150
    score = 0

    def update(self):
        self.x += self.vel * sgl.get_dt()
        if self.x > sgl.get_width(): self.vel = -self.vel
        if self.x < 0: self.vel = -self.vel

        x = sgl.get_mouse_x()
        y = sgl.get_mouse_y()-73
        circle_y = sgl.get_height()/2
        if sgl.on_mouse_up():
            if (x > self.x-20 and x < self.x+20 and
                y > circle_y-20 and y < circle_y+20):
                self.score += 1

    def draw(self):
        sgl.clear(0)
        sgl.no_stroke()
        sgl.draw_circle(self.x, sgl.get_height()/2, 20)
        with sgl.with_state():
            sgl.no_fill()
            sgl.set_stroke(1.0,0,0)
            sgl.set_stroke_weight(1)
            sgl.draw_circle(sgl.get_mouse_x(), sgl.get_mouse_y()-73, 10)

        sgl.draw_text("Circle clicks: {}".format(self.score), 8, 8)

class DrawDemo():
    name = "Drawing Functions"
    description = "SGL provides basic drawing commands. Use the arrow keys to change the stroke thickness!"

    def __init__(self):
        self.stroke = 1

    def update(self):
        if (sgl.on_key_up(sgl.key.up)
            and self.stroke < 20):
            self.stroke += 1

        if (sgl.on_key_up(sgl.key.down)
            and self.stroke > 0):
            self.stroke -= 1

    def draw(self):
        sgl.clear(1.0)

        sgl.set_fill(0)
        sgl.draw_text("Circle", 1*8, 1*8)
        sgl.draw_text("Ellipse", 1*8, 10*8)

        sgl.draw_text("Rectangle", 20*8, 1*8)
        sgl.draw_text("Line", 20*8, 10*8)

        stroke = int(self.stroke)

        sgl.draw_text("Stroke Weight: {}".format(stroke), 8, sgl.get_height() - 3*8) 

        sgl.set_stroke(0)
        sgl.set_stroke_weight(stroke)
        sgl.set_fill(0.7)

        sgl.draw_circle(1*8, 3.5*8, 5*8, False)
        sgl.draw_circle(10*8, 6*8, 5*8, True)
        sgl.draw_ellipse(1*8, 12.5*8, 10*8, 5*8, False)
        sgl.draw_rect(20*8, 3.5*8, 10*8, 5*8)
        sgl.draw_line(20*8, 12.5*8, 30*8, 16*8)
        
class AlphaDemo():
    name = "Alpha"
    description = "SGL can handle alpha channel graphics! Wow I am really grasping here. "

    def __init__(self):
        self.x = 0
        self.vel = 50

        self.clouds = sgl.load_image("hd-clouds.png")
        self.smiley = sgl.load_alpha_image("hd-smiley.png")
        self.alpha = 255

    def update(self):
        self.x += self.vel * sgl.get_dt()
        if self.x > sgl.get_width()-128: self.vel = -self.vel
        if self.x < 0: self.vel = -self.vel
    
        if (sgl.is_key_pressed(sgl.key.up)
            and self.alpha < 255):
            self.alpha += 200 * sgl.get_dt()

        if (sgl.is_key_pressed(sgl.key.down)
            and self.alpha > 0):
            self.alpha -= 200 * sgl.get_dt()

    def draw(self):
        sgl.blit(self.clouds, 0, 0)

        alpha = int(self.alpha)
        sgl.blit(self.smiley, self.x, 8, alpha=self.alpha)

        text = "Alpha: {}".format(alpha)
        sgl.set_fill(0)
        sgl.draw_text(text, 8+1, (sgl.get_height() - 3*8) +1) 

        sgl.set_fill(1.0)
        sgl.draw_text(text, 8, sgl.get_height() - 3*8) 

class FlipDemo():
    name = "Flip"
    description = "It's very easy to flip graphics in SGL! "

    def __init__(self):
        self.x = 0
        self.vel = 50

        self.clouds = sgl.load_image("hd-clouds.png")
        self.smiley = sgl.load_alpha_image("hd-smiley.png")
        self.flip_horizontal = False
        self.flip_vertical = True

    def update(self):
        self.x += self.vel * sgl.get_dt()
        if self.x > sgl.get_width()-128: self.vel = -self.vel
        if self.x < 0: self.vel = -self.vel
    
        if (sgl.on_key_up(sgl.key.up)):
            self.flip_horizontal = not self.flip_horizontal

        if (sgl.on_key_up(sgl.key.down)):
            self.flip_vertical = not self.flip_vertical

    def draw(self):
        sgl.blit(self.clouds, 0, 0)

        sgl.blit(self.smiley, self.x, 8, flip_h=self.flip_horizontal, flip_v=self.flip_vertical)

        text = "flip_h: {} (up key) flip_v: {} (down key)".format(self.flip_horizontal, self.flip_vertical)
        sgl.set_fill(0)
        sgl.draw_text(text, 8+1, (sgl.get_height() - 3*8) +1) 

        sgl.set_fill(1.0)
        sgl.draw_text(text, 8, sgl.get_height() - 3*8) 

class ScaleDemo():
    name = "Scaling test"
    description = "You can resize graphics as well! Move the mouse to resize the smiley face."

    def __init__(self):
        self.clouds = sgl.load_image("hd-clouds.png")
        self.smiley = sgl.load_alpha_image("hd-smiley.png")
        self.pretty = False
        self.rectangle = False

    def update(self):
        if (sgl.on_key_up(sgl.key.up)):
            self.pretty = not self.pretty

        if (sgl.on_key_up(sgl.key.down)):
            self.rectangle = not self.rectangle

    def draw(self):
        sgl.blit(self.clouds, 0, 0)

        x,y = 8,8
        w,h = sgl.get_mouse_x()-x, sgl.get_mouse_y()-y-73

        sgl.blit(self.smiley, x, y, width=w, height=h, pretty=self.pretty)

        if self.rectangle:
            sgl.no_fill()
            sgl.set_stroke(0)
            sgl.draw_rect(x-1, y-1, w+2, h+2)
            sgl.draw_rect(x+1, y+1, w-2, h-2)
            sgl.set_stroke(1.0)
            sgl.draw_rect(x, y, w, h)

            text = "({}x{})".format(w,h)
            sgl.set_fill(0)
            sgl.draw_text(text, x+w+1, y+h+1) 

            sgl.set_fill(1.0)
            sgl.draw_text(text, x+w, y+h) 

        text = "pretty: {} (up) stats: {} (down)".format(self.pretty, self.rectangle)
        sgl.set_fill(0)
        sgl.draw_text(text, 8+1, (sgl.get_height() - 3*8) +1) 

        sgl.set_fill(1.0)
        sgl.draw_text(text, 8, sgl.get_height() - 3*8) 

class RotateDemo():
    name = "Rotate test"
    description = "SGL lets you easily rotate graphics, including from points that are not the center!"

    def __init__(self):
        self.clouds = sgl.load_image("hd-clouds.png")
        self.smiley = sgl.load_alpha_image("hd-smiley.png")
        self.pendulum = sgl.load_image("pendulum.png")

        self.pretty = False
        self.angle = 0

    def update(self):
        if (sgl.on_key_up(sgl.key.up)):
            self.pretty = not self.pretty

        self.angle += 50 * sgl.get_dt()
        if self.angle > 360: self.angle = 0

    def draw(self):
        sgl.blit(self.clouds, 0, 0)

        angle = int(self.angle)

        sgl.blit(
            self.smiley,
            sgl.get_width()/2-80,
            sgl.get_height()/2,
            angle=angle,
            a_x=0.5, a_y=0.5,
            pretty=self.pretty
        )

        # sgl.blit(
        #     self.smiley, 
        #     sgl.get_width()/2, 
        #     sgl.get_height()/2, 
        #     angle=angle, 
        #     a_x=128/2, a_y=128/2, 
        #     scale=1.0+angle/360.0, 
        #     pretty=self.pretty
        # )

        sgl.blit(
            self.pendulum,
            sgl.get_width()/2+80,
            sgl.get_height()/2,
            angle=angle,
            a_x=0.5, a_y=0,
            pretty=self.pretty
        )

        text = "pretty: {} (up)".format(self.pretty)

        sgl.set_fill(0)
        sgl.draw_text(text, 8+1, (sgl.get_height() - 3*8) +1) 
        sgl.set_fill(1.0)
        sgl.draw_text(text, 8, sgl.get_height() - 3*8) 

class BlendDemo():
    name = "Blending modes"
    description = "You can also apply different blending modes to graphics in SGL. "

    def __init__(self):
        self.x = 0
        self.vel = 50

        self.clouds = sgl.load_image("hd-clouds.png")
        self.smiley = sgl.load_image("fireball.png")
        self.modes = [
            sgl.blend.normal, sgl.blend.add, 
            sgl.blend.multiply, sgl.blend.subtract
        ]
        self.mode_index = 0

    def update(self):
        self.x += self.vel * sgl.get_dt()
        if self.x > sgl.get_width()-128: self.vel = -self.vel
        if self.x < 0: self.vel = -self.vel

        if (sgl.on_key_up(sgl.key.up)):
            self.mode_index += 1
            if self.mode_index > len(self.modes)-1:
                self.mode_index = 0

        if (sgl.on_key_up(sgl.key.down)):
            self.mode_index -= 1
            if self.mode_index < 0:
                self.mode_index = len(self.modes)-1

    def draw(self):
        sgl.blit(self.clouds, 0, 0)

        sgl.blit(self.smiley, self.x, 8, blend_mode=self.modes[self.mode_index])

        text = "blending mode: {} (arrow keys)".format(sgl.blend.convert(self.mode_index))
        sgl.set_fill(0)
        sgl.draw_text(text, 8+1, (sgl.get_height() - 3*8) +1) 
        sgl.set_fill(1.0)
        sgl.draw_text(text, 8, sgl.get_height() - 3*8) 

class MusicDemo():
    name = "Music and sound"
    description = "Use the arrow keys to change what song is playing, and click to make a sound effect play."

    def __init__(self):
        self.clouds = sgl.load_image("hd-clouds.png")
        self.sound = sgl.load_sound("shoot.wav")
        self.songs = [
            "chased.mid", "past.ogg", "susp.xm", "dd-susp.xm"
        ]
        self.song_index = 0
        self.update_song()

    def __del__(self):
        try:
            sgl.stop_music()
        except:
            pass

    def update_song(self):
        sgl.play_music(self.songs[self.song_index])

    def update(self):
        if (sgl.on_key_up(sgl.key.up)):
            self.song_index += 1
            if self.song_index > len(self.songs)-1:
                self.song_index = 0
            self.update_song()

        if (sgl.on_key_up(sgl.key.down)):
            self.song_index -= 1
            if self.song_index < 0:
                self.song_index = len(self.songs)-1
            self.update_song()

        if sgl.on_mouse_down():
            sgl.play_sound(self.sound)

    def draw(self):
        sgl.blit(self.clouds, 0, 0)

        text = "music: {} (up/down)".format(self.songs[self.song_index])
        sgl.set_fill(0)
        sgl.draw_text(text, 8+1, (sgl.get_height() - 3*8) +1) 
        sgl.set_fill(1.0)
        sgl.draw_text(text, 8, sgl.get_height() - 3*8) 


class Game(object):
    def __init__(self):
        self.header = sgl.load_image("header.png")
        self.arrow_black = sgl.load_image("arrow-a.png")
        try:
            self.arrow_white = sgl.invert(self.arrow_black)
        except:
            self.arrow_white = sgl.load_image("arrow-b.png")

        self.app_name = "SGL Demo"

        self.left_arrow_active = False
        self.right_arrow_active = False

        self.demo_name = ""
        self.demo_description_lines = []
        self.demo_surface = sgl.make_surface(320, 167, 0.25)

        self.demo = None
        self.demos = [TestDemo, DrawDemo, AlphaDemo, FlipDemo, 
                      ScaleDemo, RotateDemo, BlendDemo, MusicDemo]
        self.demo_index = 0 #len(self.demos)-1
        self.demo_has_input = False

        self.update_demo()
        
    def update(self):
        sgl.set_title("SGL Core Demo: {} FPS".format(int(sgl.get_fps())))

        if ((sgl.is_key_pressed(sgl.key.left_control) or
            sgl.is_key_pressed(sgl.key.right_control)) or 
            not self.demo_has_input):

            if sgl.is_key_pressed(sgl.key.left):
                self.left_arrow_active = True
            if sgl.on_key_up(sgl.key.left):
                self.previous_demo()

            if sgl.is_key_pressed(sgl.key.right):
                self.right_arrow_active = True
            if sgl.on_key_up(sgl.key.right):
                self.next_demo()

        if sgl.on_key_up(sgl.key.left):
            self.left_arrow_active = False
        if sgl.on_key_up(sgl.key.right):
            self.right_arrow_active = False

        with sgl.with_buffer(self.demo_surface):
            self.demo.update()

    def next_demo(self):
        if self.demo_index < len(self.demos)-1:
            self.demo_index += 1
            self.update_demo()

    def previous_demo(self):
        if self.demo_index > 0:
            self.demo_index -= 1
            self.update_demo()

    def update_demo(self):
        self.demo = None
        self.demo = self.demos[self.demo_index]()
        self.set_demo_text(str(self.demo_index) + ": " + self.demo.name, self.demo.description)

    def set_demo_text(self, name, description):
        self.demo_name = name

        self.demo_description_lines = []
        width = (sgl.get_width()-5) - 68
        line = []
        last_word = ""
        for word in description.split(" "):
            if last_word: 
                line.append(last_word)
                last_word = ""
            line.append(word)

            w = sgl.get_text_width(" ".join(line))
            if w > width:
                last_word = line.pop()
                self.demo_description_lines.append(" ".join(line))
                line = []

        if line != []:
            self.demo_description_lines.append(" ".join(line))

    def draw(self):
        with sgl.with_state():
            sgl.blit(self.header, 0, 0)

            sgl.set_fill(1.0)
            sgl.draw_text(self.app_name, 2, 1)

            arrow = (self.arrow_white 
                     if self.left_arrow_active 
                     else self.arrow_black)
            x1 = sgl.get_text_width(self.app_name)+2
            sgl.blit(arrow, x1, 0)

            arrow = (self.arrow_white 
                     if self.right_arrow_active 
                     else self.arrow_black)
            x2 = sgl.get_width()-16
            sgl.blit(arrow, x2, 0, flip_h=True)

            x1 += 16
            w = sgl.get_text_width(self.demo_name)
            x = x1 + (x2-x1)/2 - w/2
            sgl.draw_text(self.demo_name, x, 1)

            sgl.set_fill(0)
            x = 68
            y = 22
            for line in self.demo_description_lines:
                sgl.draw_text(line, x, y)
                y += sgl.get_text_height("t")-2

        with sgl.with_buffer(self.demo_surface):
            self.demo.draw()

        sgl.blit(self.demo_surface, 0, 73)

if __name__ == "__main__":
    app = Game()
    sgl.run(app.update, app.draw)

import sgl
from sgl.lib.Sprite import Sprite, RectSprite, Scene
import sgl.lib.Time as time
import sgl.lib.Tween as tween
import sgl.lib.Script as script
from sgl.lib.TextSprite import TextSprite

class ScriptTextSprite(TextSprite):
    pause_code = 999

    def __init__(self):
        super(ScriptTextSprite, self).__init__()

        self.type_text = ""
        self.type_index = 0
        self.type_speed = 0
        self.type_speed_wait = 0

        self.clear_after_pause = False

        self.auto_clear = True

        self.interpreter = None

        time.at_fps(60, self.update_typing)

    def update_typing(self):
        if self.type_text == "": return
        if self.type_index >= len(self.type_text): 
            self.type_text = ""
            self.interpreter.advance()
            return

        self.type_speed_wait -= 1
        if self.type_speed_wait > 0: return
       
        start = self.type_text.rfind(" ", 0, self.type_index)+1
        end = self.type_text.find(" ", self.type_index)+1
        if end == 0: end = len(self.type_text)-1

        current_word = self.type_text[start:end]

        self.actual_current_word = current_word
        self.add_text(self.type_text[self.type_index])

        self.type_index += 1
        self.type_speed_wait = self.type_speed

    def add_script_text(self, text, interpreter):
        self.type_text = text
        self.type_index = 0

        interpreter.pause()
        self.interpreter = interpreter

    @script.script_command("paragraph")
    def paragraph(self, interpreter):
        if self.auto_clear:
            self.pause(interpreter)
            self.clear_after_pause = True
        else:
            self.add_text("\n\n")

    @script.script_command("pause")
    def pause(self, interpreter):
        interpreter.pause(self.pause_code)
    
    @script.script_command("wait")
    def wait(self, amount, interpreter):
        interpreter.pause()
        time.set_timeout(amount, lambda: interpreter.advance())

    @script.script_command("speed")
    def set_speed(self, speed):
        self.type_speed = speed

    @script.script_command("new page")
    def new_page(self):
        self.clear()

    @property
    def dialogue_finished(self):
        if self.interpreter:
            return self.interpreter.paused and self.interpreter.pause_code == self.pause_code
        else:
            return False

    @property
    def ctc_position(self):
        x = self.last_line.width
        y = self.get_line_y(self.last_line_index)
        return x, y

    @property
    def ctc_size(self):
        return self.last_line.height

    def advance(self):
        if self.clear_after_pause: 
            self.clear()
            self.clear_after_pause = False

        self.interpreter.advance()

if __name__ == "__main__":
    sgl.init(640, 480, 1)

    test_script = """
[use pretty commands: yes]

[define macro: "=01" "[wait: 1]"]
[define macro: "=02" "[wait: 2]"]
[define macro: "/01" "[speed: 1]"]
[define macro: "/02" "[speed: 2]"]
[define macro: "/03" "[speed: 3]"]
[define macro: "/05" "[speed: 5]"]

@main
    [auto clear: no]

    /03TEST 1=01

    /01What is this, you might ask?=01 This is a test 
    of the script interpreting and text box systems.=01 Specifically, 
    we want to see if it word wraps right.=01

    It appears to.[pause]

    [new page]Press a key here.[pause] Yay, we pasued in the middle.=01

    /05Yaaaaaaaaaaaaay[pause]

    [new page]

    /03TEST 2=01

    [auto clear: yes]

    /01You can also make the text box automatically clear after each 
    line of dialogue.

    ...like this.

    It's pretty convenient for normal type of games, in which we
    usually do not need to have new lines or paragraphs in the middle
    of dialogue.

    [goto: main]
    """

    class ContinueMarker(Sprite):
        def __init__(self):
            super(ContinueMarker, self).__init__()

            self.visible = False

            self.size = 20,20

            surface = sgl.make_surface(self.width, self.height)

            with sgl.with_buffer(surface):
                sgl.set_stroke_weight(2)
                sgl.set_stroke(1.0)
                sgl.draw_line(0, 0, self.width-2, self.height/2)
                sgl.draw_line(self.width-2, self.height/2, 0, self.height-2)
                sgl.draw_line(0, 0, 0, self.height-2)
        
            self.surface = surface

        def show(self, position):
            self.position = position
            self.x += 2

            self.animation = tween.to(
                self, {'x': self.x + 5},
                0.5,
                bounce=True
            )

            self.visible = True

        def hide(self):
            self.visible = False
            self.animation.stop()
            

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            self.text_box = ScriptTextSprite()
            self.text_box.position = 32, 32
            self.text_box.size = sgl.get_width()-32*2, 300
            self.text_box.font = sgl.load_system_font("Arial", 20)
            self.text_box.auto_clear = False

            self.add(self.text_box)

            self.ctc = ContinueMarker()
            self.text_box.add(self.ctc)

            self.interpreter = script.ScriptInterpreter()

            self.interpreter.set_add_text(self.text_box.add_script_text)

            self.interpreter.load_commands(self.text_box)
            self.interpreter.load_commands(self)

            self.interpreter.load_script(test_script)

            self.interpreter.goto_label("main")
            self.interpreter.advance()

        @script.script_command("goto")
        def goto(self, label, interpreter):
            interpreter.goto_label(label)

        @script.script_command("auto clear")
        def auto_clear(self, value, interpreter):
             self.text_box.auto_clear = (value == "yes")

        def update(self):
            super(TestScene, self).update()

            time.update(sgl.get_dt())
            tween.update(sgl.get_dt())

            if self.text_box.dialogue_finished:
                if not self.ctc.visible:
                    self.ctc.show(self.text_box.ctc_position)

                if sgl.on_mouse_up() or sgl.on_key_up(sgl.key.enter):
                    self.text_box.advance()
                    self.ctc.hide()

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)



import sgl
from sgl.lib.Rect import Rect
from sgl.lib.Sprite import Sprite, RectSprite, Scene
import sgl.lib.Time as time
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
    def is_dialogue_waiting(self):
        if self.interpreter:
            return self.interpreter.paused and self.interpreter.pause_code == self.pause_code
        else:
            return False

    def advance(self):
        if self.clear_after_pause: 
            self.clear()
            self.clear_after_pause = False

        self.interpreter.advance()
        
    def update(self):
       if (sgl.on_mouse_up() or sgl.on_key_up(sgl.key.enter)) and self.is_dialogue_waiting:
            self.advance()

if __name__ == "__main__":
    sgl.init(640, 480, 1)

    test_script = """
[define-macro "=01" "[wait 1]"]
[define-macro "=02" "[wait 2]"]
[define-macro "/01" "[speed 1]"]
[define-macro "/02" "[speed 2]"]
[define-macro "/05" "[speed 5]"]

@main

    /01What is this, you might ask?=01 This is a test 
    of the script interpreting and text box systems.=01 Specifically, 
    we want to see if it word wraps right.=01

    It appears to.=01

    Press a key here.[pause] Yay, we pasued in the middle.=01

    /05Yaaaaaaaaaaaaay[pause]
    """

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            bg = RectSprite()

            bg.fill_color = 0
            bg.no_stroke = True
            bg.fill()

            self.add(bg)

            self.text_box = ScriptTextSprite()
            self.text_box.position = 32, 32
            self.text_box.size = sgl.get_width()-32*2, 300
            self.text_box.font = sgl.load_system_font("Arial", 20)
            self.text_box.auto_clear = False

            self.add(self.text_box)

            self.interpreter = script.ScriptInterpreter(test_script, self.text_box.add_script_text)
            self.interpreter.load_commands(self.text_box)
            self.interpreter.goto_label("main")
            self.interpreter.advance()

        def update(self):
            super(TestScene, self).update()

            time.update(sgl.get_dt())

            sgl.set_title("FPS: " + str(sgl.get_fps()))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)



import script_parser as script
import inspect

def is_string(thing):
    """ Returns whether `thing` is a string or not. """

    if 'basestring' not in globals():
        return isinstance(thing, str)
    else:
        return isinstance(thing, basestring)

def script_command(*commands):
    def decorator(function):
        function._commands = commands
        return function
    return decorator

class ScriptInterpreterError(Exception): pass

class CommandCollisionError(ScriptInterpreterError):
    def __init__(self, name):
        self.name = name

class NoSuchCommandError(ScriptInterpreterError):
    def __init__(self, name):
        self.name = name

class PastScriptBoundsError(ScriptInterpreterError): pass


class ScriptInterpreter:
    def __init__(self, text, text_function):
        self.load_script(text)
        self.add_text = text_function
        self.commands = {}
        self.in_command_loop = False

    def load_script(self, text):
        self.script = script.ScriptParser(text).parse()
        self.paused = True
        self.pause_code = -1

    def load_commands(self, instance):
        for item_name in dir(instance):
            # Convert that name to an object
            item = getattr(instance, item_name)

            if hasattr(item, "_commands"):
                for command in item._commands:
                    if command in self.commands:
                        raise CommandCollisionError(command)
                    else:
                        self.commands[command] = item

    def goto_label(self, label):
        self.label = label
        if self.in_command_loop:
            self.index = -1
            # because it will advance to the next command after this
        else:
            self.index = 0

    @property
    def current_body(self):
        return self.script[self.label].body

    @property
    def current_item(self):
        return self.current_body[self.index]

    def is_current_command(self):
        return isinstance(self.current_item, script.Command)

    def is_current_text(self):
        return is_string(self.current_item)

    def advance(self):
        self.paused = False
        self.pause_code = 0

        self.in_command_loop = True 
        while True:
            if self.is_current_text():
                self.handle_text(self.current_item)
            elif self.is_current_command():
                self.handle_command(self.current_item)
            else:
                pass # hell has frozen over

            self.next()

            if self.paused == True: break
        self.in_command_loop = False

    def handle_text(self, text):
        self.add_text(text, interpreter=self)

    def handle_command(self, command):
        if command.name not in self.commands:
            print command.name
            raise NoSuchCommandError(command.name)

        function = self.commands[command.name]

        pos = command.pos_arg

        arguments = inspect.getargspec(function).args
        if "interpreter" in arguments:
            key = command.key_arg.copy()
            key["interpreter"] = self
        else:
            key = command.key_arg
        
        function(*pos, **key)

    def next(self):
        self.index += 1
        if self.index >= len(self.current_body):
            raise PastScriptBoundsError

    def pause(self, code=1):
        self.paused = True
        self.pause_code = code


if __name__ == "__main__":
    text = """
[define-macro "=01" "[wait 1]"]
[define-macro "=02" "[wait 2]"]
[define-macro "/01" "[speed 1]"]
[define-macro "/02" "[speed 2]"]
[define-macro "/05" "[speed 5]"]

@test
   [fade-in]

   ;; play some music and stuff
   [play-music "bob's cool.xm" loop=yes]

   /01
   Hello there.=02/02 This...=01 is a test.=02
   /01 A =01/05cool /01=01test.[pause]

   ;; play some music and stuff
   [play-music "bob's cool.xm" loop=no]

   ;; do other stuff
   /01Wheeeeeeeeeeeeeeeeee[goto hi]

@hi
   /02eeeeeeeeeeeeeeeeeee[pause]

    [goto test2]

@test2
   test2[pause]

    [goto test]

@sdgsdg
   sdgsdg

    [pause]
    """

    import time
    import sys
    
    class StupidTextBox:
        def __init__(self):
            self.speed = 1

        @script_command("speed")
        def set_speed(self, new_speed):
            self.speed = new_speed

        @script_command("paragraph")
        def p(self):
            print " "

        def add(self, text, interpreter):
            for i in text:
                sys.stdout.write(i)
                time.sleep(self.speed/float(30))

    class Graphics:
        @script_command("fade-in", "fdin")
        def fade_in(self, interpreter):
            print "(FADING IN)"

        @script_command("play-music")
        def play_music(self, filename, loop="no"):
            loop = True if loop == "yes" else False
            if loop:
                print "(LOOPING MUSIC " + filename + ")"
            else:
                print "(PLAYING MUSIC " + filename + ")"

    class Time:
        @script_command("wait")
        def fade_in(self, seconds):
            time.sleep(seconds/2.)

        @script_command("pause")
        def pause(self, interpreter):
            interpreter.pause()
            raw_input("(PRESS ENTER)")

        @script_command("goto")
        def goto(self, label, interpreter):
            interpreter.goto_label(label)


    t = StupidTextBox()
    g = Graphics()
    ti = Time()

    i = ScriptInterpreter(text, t.add)
    i.load_commands(t)
    i.load_commands(g)
    i.load_commands(ti)

    i.goto_label("test")
    while True:
        i.advance()

# (compile "python script.py" t)

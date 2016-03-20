# TODO: think of a better f***ing way to do this

class input:
    keyboard = 0
    mouse = 1
    joystick = 2
    # touch = 3
    # digitizer = 4

    @staticmethod
    def convert(item):
        try:
            return ["keyboard", "mouse", "joystick"][item]
        except:
            return item

class abilities:
    software = 0
    numpy = 1
    save_buffer = 2

    @staticmethod
    def convert(item):
        try:
            return ["software", "numpy", "save_buffer"][item]
        except:
            return item

class blend:
    normal = 0
    add = 1
    multiply = 2
    subtract = 3

    @staticmethod
    def convert(item):
        try:
            return ["normal", "add", "multiply", "subtract"][item]
        except:
            return item


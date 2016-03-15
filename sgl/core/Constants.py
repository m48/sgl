class input:
    keyboard = 0
    mouse = 1
    joystick = 2

    @staticmethod
    def convert(item):
        try:
            return ["keyboard", "mouse", "joystick"][item]
        except:
            return item

    # touch = 3
    # digitizer = 4

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


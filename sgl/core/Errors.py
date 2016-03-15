from Constants import *

class sglException(Exception): pass

class UnsupportedBackendError(sglException): pass

class UnsupportedInputError(sglException): 
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return "This backend does not support {} input".format(input.convert(self.item))

class UninitializedInputError(sglException): 
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return "{} input support is currently not turned on".format(input.convert(self.item))

class UnsupportedActionError(sglException): 
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return "Function not supported. This backend does not support \"{}\"".format(abilities.convert(self.item))

class FileNotFoundError(sglException): 
    def __init__(self, item):
        self.item = item

    def __str__(self):
        return "\"{}\" does not exist".format(self.item)

class UnsupportedFormatError(sglException): 
    def __init__(self, file, item):
        self.file = item
        self.item = item

    def __str__(self):
        return "Cannot open \"{}\". This backend does not support \"{}\" files".format(self.file, self.item)

class ArgumentError(sglException): 
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return message

class BackendError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return message


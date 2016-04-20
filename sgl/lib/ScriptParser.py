# To do:
# Get line numbers working correctly

def is_string(thing):
    """ Returns whether `thing` is a string or not. """

    if 'basestring' not in globals():
        return isinstance(thing, str)
    else:
        return isinstance(thing, basestring)

class ParserError(Exception):
    def __init__(self, text, line, char):
        self.text = text
        self.line = line
        self.char = char

class Label():
    def __init__(self, name, body):
        self.name = name
        self.body = body

class Command():
    def __init__(self, name, pos_arg=[], key_arg={}):
        self.name = name
        self.pos_arg = pos_arg
        self.key_arg = key_arg

    def __str__(self):
        result = "[" + self.name

        if self.pos_arg != []:
            for item in self.pos_arg:
                result += " " + repr(item)

        if self.key_arg != {}:
            for key in sorted(list(self.key_arg)):
                result += " {}={!r}".format(key, self.key_arg[key])

        result += "]"

        return result

class Parser():
    def __init__(self, text=""):
        if text: self.load_text(text)

    def load_text(self, text):
        self.text = text
        self.position = 0
        self.line = 0
        self.col = 0
        
    def next(self):
        """ Moves the position onwards, keeping track of the current
        line and column. """

        self.position += 1

        self.col += 1
        if self.position_valid() and self.char == "\n":
            self.line += 1
            self.col = 0

    @property
    def char(self):
        """ Returns the current character. """

        if self.position_valid():
            return self.text[self.position]
        else:
            return ""

    def eat(self, char):
        """ Eats a character, and if it's not what you
        specify, complains. """

        if self.char == char:
            self.next()
        else:
            self.error("expected '" + char + "'")

    @property
    def prev_char(self):
        """ Returns the character before the current one. """

        return self.text[self.position-1]

    @property
    def next_char(self):
        """ Returns the character after the current one. """

        if self.position+1 < len(self.text)-1 :
            return self.text[self.position+1]
        else:
            return ""

    def position_valid(self):
        """ Returns if we're in the document. """

        return self.position < len(self.text)-1 

    def at_line_beginning(self):
        """ Returns if we're at the beginning of the given line. """

        return self.prev_char == "\n"

    def at_content_beginning(self):
        """ Returns if we're at the beginning of the content of the line. """

        position = self.position-1
        line = ""

        # Go backwards until we find the last newline
        while position > 0:
            char = self.text[position]
            if char == "\n": 
                break
            elif char in (" ", "\t"):
                position -= 1
            # If we find a non-whitespace character, fail
            else:
                return False
            
        # Otherwise succeed
        return True

    def error(self, text):
        """ Raises an error and shows the current position
        and stuff. """

        end = self.position+1
        start = self.text.rfind("\n", 0, end)
        if start == -1: start = 0
        print self.text[start:end]

        format_string = "line: {} pos: {} char: '{}'\nerror: \"{}\""
        print format_string.format(self.line, self.position, self.char, text)

        raise ParserError(text, self.line, self.col)

    def at_literal(self):
        return (self.char == "\"" or self.char == "'" or
                self.char.isdigit() or self.char == "-")

    def literal(self):
        """ Reads any arbitrary value. """

        if self.char == "\"" or self.char == "\'":
            item = self.string_literal()
        elif self.char.isdigit() or self.char == "-":
            item = self.number_literal()
        else:
            item = self.symbol()
        return item

    def string_literal(self):
        """ Reads and converts a string literal"""

        result = ""

        starting = self.char
        if starting != "\"" and starting != "'":
            self.error("invalid string literal")
        self.next()

        while True:
            if self.char == "\\":
                self.next()

            if self.char == starting and self.prev_char != "\\":
                break

            result += self.char
            self.next()

        self.next()

        return result

    def number_literal(self):
        """ Reads and converts a number. """

        result = ""
        while not (self.char.isspace() or self.char == "]"):
            result += self.char
            self.next()

        # Okay, this feels dumb, but it works :|
        if result.find(".") != -1:
            return float(result)
        else:
            return int(result)

    def symbol(self):
        """ Reads a symbol name. """

        if self.char.isdigit() or self.char == "-":
            self.error("symbols cannot begin with digits or -s")
        elif self.char == "\"":
            self.error("symbols cannot begin with \"s")

        result = ""
        while self.char not in ["\n", " ", "[", "]", "=", ";"]:
            result += self.char
            self.next()
        return result.lower()

    def whitespace(self, allow_newline=True):
        """ Eats all whitespace. """

        items = [" ", "\t"]
        if allow_newline:
            items.append("\n")

        while self.char in items:
            self.next()

    def newline(self):
        """ Expects a newline at char. """

        if self.char == "\n":
            self.next()
        else:
            self.error("expected newline")

    def line_empty(self):
        """ Peeks ahead to see if the current line is empty or not. """
        position = self.position
        line = ""

        while position < len(self.text)-1:
            if self.text[position] == "\n": break

            line += self.text[position]
            position += 1

        line = line.strip()

        return line == "" or line.startswith(";;")

class ParserSettings(object):
    # A dictionary of macros and replacement text
    macros = {}

    # Whether whitespace between commands in the middle of a paragraph
    # is reproduced. By default, it isn't, which can be handy, but
    # unexpected, since that isn't really how HTML works.
    use_command_whitespace = False

    # Whether commands with no keyword arguments are interpreted as
    # pretty commands ot not
    default_pretty = False

    # Controls paragraph command generation
    add_paragraphs = True
    paragraph_name = "paragraph"

class MacroError(Exception):
    def __init__(self, text):
        self.text = text

class BodyParser(Parser):
    settings = ParserSettings()
    macro_beginnings = []

    def cache_macro_beginnings(self):
        """ Creates a list of the first character of each macro, used
        for parsing. """

        self.macro_beginnings = []

        for macro in self.settings.macros:
            # If the macro is in itself, escape it. This doesn't
            # prevent you from making infinite circular chains of
            # macros, though, so it's kind of pointless. :|
            # Yes, macros can expand each other. I've unintentionally
            # created a monster here.
            if macro in self.settings.macros[macro]:
                self.settings.macros[macro] = self.settings.macros[macro].replace(
                    macro, "\\" + macro)

            begin = macro[0]

            # Technically these work, but they create a bunch of
            # annoying edge cases I don't want to fix.
            if begin in ['\\', '[', '@']:
                raise MacroError(
                    "Macros must not begin with built-in characters")

            # Add first character to handy list!
            if begin not in self.macro_beginnings:
                self.macro_beginnings.append(begin)

    def at_comment(self):
        return self.char == ";" and self.next_char == ";"

    def parse(self):
        result = []
        last_paragraph_blank = True

        # Do cache if it's not already done
        if self.macro_beginnings == []:
            self.cache_macro_beginnings()

        while True:
            # Stop if we reach the end
            if not self.position_valid():
                break

            # Get rid of any whitespace at beginnings of lines
            # Otherwise indenting anything will be impossible
            if self.at_line_beginning():
                self.whitespace()

            # Handle comments. Not sure about the syntax for this.
            # For now I'm using Lisp style comments, except you need
            # two ;s instead of one.
            if self.at_comment():
                self.read_to_end_of_line()
                continue

            # Handle new lines
            if self.char == "\n":
                # If there is just one, skip it
                self.next()

                # If the next line is also empty, though, that means
                # this is a paragraph break
                if self.line_empty():
                    # Eat up whatever excessive amount of blank space
                    # I've put in between my paragraphs :|
                    self.whitespace()

                    # If the previous paragraph actually has anything
                    # in it, replace the newlines with a 'paragraph'
                    # command. This prevents command blocks between
                    # paragraphs from being flanked on both sides
                    # with paragraph commands.
                    if result != [] and not last_paragraph_blank:

                        # Should this turn off the rest of the
                        # paragraph logic too? Hmm.
                        if self.settings.add_paragraphs:
                            result.append(
                                Command(self.settings.paragraph_name)
                            )

                        last_paragraph_blank = True
                
            # Handle commands
            elif self.char == "[":
                result.append(self.command())

            # Handle macros
            # If the current character is the first character of any
            # of the macros...
            elif self.char in self.macro_beginnings:
                # Keep track of whether the macro is used or not.
                macro_used = False

                # Just loop through all the macros :|
                for macro in self.settings.macros:
                    # If the text from this point onwards contains a
                    # macro...
                    if (self.text[self.position:
                                  self.position + len(macro)] == macro):
                        # Make the text equal to:
                        #    text up to macro +
                        #    the macro replacment +
                        #    text after the macro
                        self.text = (self.text[:self.position] + 
                                     self.settings.macros[macro] + 
                                     self.text[self.position 
                                               + len(macro):])
                        # This text will be parsed as if it were part
                        # of the original script, so commands will get
                        # executed and stuff.

                        # Macro is considered 'used' when the
                        # replacement is done
                        macro_used = True

                # If it turns out only the first character was right,
                # put this character into the script literally, so
                # we don't end up in an infinite loop looking for a
                # macro that doesn't exist
                if not macro_used:
                    if isinstance(result[-1], Command):
                        result.append(self.char)
                    else:
                        result[-1] += self.char
                    self.next()

            # If it's not any of those things, it has to be dialogue!
            else:
                at_content_beginning = self.at_content_beginning()

                # Get text, stopping for commands and macros
                text = self.prose()

                # If text is more than stupid whitespace, put it on

                # If you want to allow whitespace within command
                # blocks, use this condition:

                # if text.strip() != "" or not last_paragraph_blank:

                # Work on configuration, to make this an option
                if (text.strip() != "" or 
                    (self.settings.use_command_whitespace and 
                     not last_paragraph_blank)):
                    # If the last thing is a string, just add it to
                    # that one. That way we don't end up with
                    # awkwardly divided text blocks.
                    if len(result) > 0 and is_string(result[-1]):
                        # If we're at the beginning of the line, and
                        # there's no space at the end of the last
                        # block of text
                        if (at_content_beginning and
                            not result[-1][-1].isspace()):
                            result[-1] += " "
                        result[-1] += text

                    # If not, just add it normally
                    else:
                        # If at the beginning of this paragraph, just
                        # add text
                        if last_paragraph_blank:
                            result.append(text)

                        # If at beginning of line, add with space
                        elif (at_content_beginning and 
                            not text[0].isspace()):
                            result.append(" " + text)

                        # Otherwise just add (yes the conditions have
                        # to be like this for it to work. I can't
                        # think of a better way to organize this for
                        # now)
                        else:
                            result.append(text)                            

                    # Mark the last paragraph as actually having stuff
                    last_paragraph_blank = False

        return result

    def has_colon(self):
        """  """

        position = self.position
        line = ""
        limit = 300
        if position+limit < len(self.text)-1:
            end = position+limit
        else:
            end = len(self.text)-1

        while position < end:
            if self.text[position] in ("\"", "\'", "=", "]", ";"): 
                return False
            elif self.text[position] == ":":
                return True

            position += 1

        return False

    def pretty_symbol(self):
        """ """

        if self.char.isdigit() or self.char == "-":
            self.error("symbols cannot begin with digits or -s")
        elif self.char == "\"":
            self.error("symbols cannot begin with \"s")

        result = ""
        while self.char not in ["[", "]", "=", ":", ";"]:
            result += self.char
            self.next()

        if self.char == "]":
            pass
        else:
            self.eat(":")
        self.whitespace()

        return result.lower().replace(" ", "-")
        
    def command(self):
        self.eat("[")

        # Allow whitespace at the beginning for some reason
        self.whitespace()

        # Get command name
        if self.settings.default_pretty or self.has_colon(): 
            name = self.pretty_symbol()
            pretty = True
        else: 
            name = self.symbol()
            pretty = False
        self.whitespace()

        # Everything else is arguments
        pos_args, key_args = self.arguments(pretty)
        self.next()

        return Command(name, pos_args, key_args)

    def arguments(self, pretty=False):
        pos_args = []
        key_args = {}

        # Handle positional arguments
        while self.char != "]":
            # Handle comments
            if self.at_comment():
                self.read_to_end_of_line()
                self.whitespace()
                continue

            # Get value

            # Mark values that are string literals (starting with ")
            # or numbers, so that they do not become "keys" for the
            # keyword arguments
            if self.at_literal():
                bad_key = True

            # If the current value is a normal identifier,
            # do special logic
            else:

                # If this is a pretty style key (e.g., a
                # colon is coming up), get that symbol and move on
                if self.has_colon():
                    first_key = self.pretty_symbol()
                    pretty = True
                    break

                # Otherwise, say this is okay to use as a key
                # (You know, I could just do this the same way as the
                # pretty symbols and save some code...)
                else:
                    bad_key = False

            # Get the positional value
            item = self.literal()
            pos_args.append(item)

            # Move on to the next value
            self.whitespace()

            # If we are now at an equals sign, it means we must switch
            # to parsing keyword arguments
            if self.char == "=":

                # To do this, the last value must not be a string or
                # number literal
                if bad_key:
                    self.error("Key for key args must be symbol")

                # If it's okay, use the last parsed positional
                # argument as the name of the first keyword argument
                else:
                    first_key = pos_args.pop()
                    break
            
            if self.char == "[":
                self.error("Cannot nest commands")

        # Handle keyword arguments
        while self.char != "]":
            # Get the key name

            # If the first key is prespecified, use that
            if first_key:
                key = first_key
                first_key = ""

                # For old-style keyword arguments, we need to eat up
                # the equal sign after this
                if not pretty:
                    self.whitespace()
                    self.eat("=")
                    self.whitespace()
    
            # If we're in the middle, we have to parse stuff
            else:
                # If a colon is coming up, get it new style
                if self.has_colon():
                    key = self.pretty_symbol()

                    if not pretty:
                        self.position -= 1
                        self.error("Do not mix pretty and not pretty styles")

                # Otherwise it's the old style
                else:
                    # Gets the key name
                    key = self.symbol()

                    # Get the equals sign. Do some extra logic to
                    # prevent users from mixing old and new style
                    # commands (technically this works fine, but I
                    # might deprecate the old-style later)
                    self.whitespace()
                    if not pretty:
                        self.eat("=")
                    else:
                        if self.char == "=":
                            self.error("Do not mix pretty and not pretty styles")
                        self.error("Parameter specified without value")
                    self.whitespace()

            # Get the keyword argument's value
            value = self.literal()
            key_args[key] = value

            # Go on to the next one
            self.whitespace()

            # Handle comments
            if self.at_comment():
                self.read_to_end_of_line()
                self.whitespace()
                continue

        return pos_args, key_args

    def prose(self):
        result = ""

        # While we are still even in the document
        while (self.position_valid() and self.char != "\n"):
            if self.at_comment():
                self.read_to_end_of_line()
                continue

            # If we are not escaping anything
            if self.prev_char != "\\":
                # Let commands and macros go through the proper
                # channels
                if (self.char == "[" or 
                    self.char in self.macro_beginnings):
                    break

            # If we are escaping something...
            else:
                # Handle newline literals. (For some reason. I'm not
                # sure this is actually a good idea. I should probably
                # just make people use commands if they want to put new
                # lines in weird places.)
                if self.char == "n":
                    result = result[:-1] + "\n"
                    self.next()
                    continue

                # Just put the same character for command and macro
                # escaping
                elif self.char == "[" or self.char in self.macro_beginnings:
                    # Cut off the \, replace with what we want
                    result = result[:-1] + self.char

                    # Move on
                    self.next()
                    continue

            # The just adding chracters normally case
            result += self.char
            self.next()

        return result

    def read_to_end_of_line(self):
        # Exists for no other reason than to handle comments :|
        result = ""
        while self.position_valid() and self.char not in ["\n"]:
            result += self.char
            self.next()
        return result

class HeaderError(Exception):
    def __init__(self, text):
        self.text = text

class ScriptParser(Parser):
    settings = ParserSettings()

    def reset_settings(self):
        self.settings = ParserSettings()

    def parse(self):
        # Read header
        self.whitespace()
        self.header()

        # Read labels
        result = {}
        while True:
            if self.char == "@":
                label = self.label()
                result[label.name] = label
            else:
                break

        # Return dictionary of labels
        return result

    def header(self):
        # Retrieve and parse all text before the first label
        text = self.body()
        if not text: return

        header = BodyParser(text).parse()

        for item in header:
            # Only allow commands
            if isinstance(item, Command):

                # Handle define macro command
                if item.name in ["defmacro", "define-macro"] and len(item.pos_arg) == 2:
                    self.settings.macros[item.pos_arg[0]] = item.pos_arg[1]

                # Handle define macro command
                elif item.name in ["use-pretty-commands"] and len(item.pos_arg) == 1:
                    self.settings.default_pretty = (item.pos_arg[0] == "yes")

                # Ignore paragraph commands generated by newlines
                elif item.name == self.settings.paragraph_name:
                    pass

                # Complain about anything else
                else:
                    raise HeaderError("only compiler directives allowed in the header")

            # Complain if something that is not a command is found
            else:
                raise HeaderError("no text blocks allowed in the header")

    def label(self):
        # Retrieve label name
        self.eat("@")
        name = self.symbol()
        self.whitespace(False)
        self.newline()

        # Read and parse body
        body_text = self.body()
        parser = BodyParser(body_text)
        parser.settings = self.settings
        body = parser.parse()

        # Return object with those in it 
        return Label(name, body)

    def body(self):
        # Collect stuff until we reach a line starting with @
        result = ""

        while (not (self.char == "@" and self.at_line_beginning()) 
               and self.position_valid()):
            result += self.char
            self.next()

        return result
       
if __name__ == "__main__":
    text = """
[define macro: "=01" "[wait 1]"]
[define macro: "=02" "[wait 2]"]

@test
   [fade in]
   ;; test
   Hello there.
   [pause Hi stuff=1 other-stuff="hi there"]
   [pause: 
    other stuff: "hi there" 
    stuff: 1] 
   This...=02 is a test.[pause]
   ;; safsag

   ;; play some music and stuff
   [play-music;; command
    'bob\\'s cool.xm' ;; lol
    ;; asfasfasf
    loop=no;; lol2
    ] ;; safasgd
    ;; dsfsf

   ;; play some music and stuff
   [play music: ;; command
    'bob\\'s cool.xm' ;; lol
    ;; asfasfasf
    loop: no;; lol2
    ] ;; safasgd
    ;; dsfsf

   [oth-stuff][hahaa]

   ;; do other stuff
   Wheeeeeeeeeeeeeeeeee[pause];;fsafas

    ;; test
    [person] 
    [background]

    I really like[shake] [stuff] cheese


    hi
    there.=01
    im cool

    lol

@hi




   wheeeee [bob]eeeeeee




              eeee

eee

@test2
asgasgasg

@sdgsdg
sdgsdg
    """

    text2 = """
[use pretty commands: yes]

@test
[fade in]

[background: house outside]
Hello there. I'm a person.

[Character: Bob]
Specifically, I'm Bob.

[Character: Bob sad]
And I'm sad.

Really sad.
"""

    def display(result):
        for line in result["test"].body:
            if is_string(line):
                print "TEXT: \"" + str(line) + "\""
            else:
                print "CMND: " + str(line)
                if line.name == "paragraph":
                    print ""

    parser = ScriptParser()
    parser.load_text(text)
    display(parser.parse())

    parser.load_text(text2)
    # parser.settings.default_pretty = True
    display(parser.parse())


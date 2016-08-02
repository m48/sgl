""" This module provides the functionality to parse SGLscript. It is
mainly used behind the scenes to provide :any:`sgl.lib.Script` with
the data it needs to operate, but you may need to interact with this
module for real-time script manipulation. 

An SGLscript file is formatted like follows:

* First, there is a header section. The format of this section is
  documented in :any:`ScriptParser.header`. (Please read that after
  reading this, though---the documentation for that function assumes
  some familiarity with the format of commands.)
* Then, you must specify the beginning of a "label" by having a line
  that begins with ``@``, with the rest of the line consisting of the
  label name. Any line beginning with a ``@`` starts a new label.

  .. warning:: This may be deprecated in favor of just using the
      normal command syntax to define labels in the future. Even if
      that happens, though, it will be possible to replicate the
      current behavior through slightly more configurable macros.
* Every line after that is interpreted as the body of a given
  label. 

In the body, two main rules apply:

* Normal text is interpreted as dialogue that will get output to the
  screen.
* Anything with in square braces (``[`` and ``]``) is interpreted as a
  command.

Commands can consist of three components: 

* All commands must have a *command name.* This determines what
  function is used to handle this command when the script is executed.
* Then, after this, they can have *positional arguments.* These, like
  positional arguments in Python, or arguments that are specified by
  order instead of by name.
* Then, after (or instead of) positional arguments, commands can have
  *keyword arguments.* These are arguments in which their name is
  specified, and then their value. 

There are two syntaxes of commands:

* There are the *old-style commands,* which behave like HTML tags. In
  this syntax, the command name is specified at the beginning, and is
  ended by whitespace. After this whitespace, you can have whitespace
  separated positional arguments, and then whitespace separated
  keyword arguments. Keyword arguments are given in a ``key=value``
  form, and any amount of whitespace is accepted before and after the
  ``=``.

  The type of commands look like this: ``[show-background "tree.png"
  transition="fade-in" fade-time=5]``.

  .. warning:: These types of commands will be deprecated as soon as
     possible. Don't use them. I'm merely documenting them so the source
     code makes more sense.

* There are the *new-style commands,* or *pretty commands.* With this
  syntax, command names are first, but are ended by a colon
  (``:``). Because of this, command names can have spaces in
  them. Then, positional arguments can be specified the same way as
  with the old-style. Then, keyword arguments can be specified, but in
  a ``key: value`` form. Thus, keyword arguments, like command names,
  can also have spaces in their names. This creates some ambiguous
  parsing situations, but these commands are much easier to read.

  These types of commands look like this: ``[show background:
  "tree.png" transition: "fade-in" fade time: 5]``.

  With the sense of commands, command and keyword argument names are
  case insensitive, and can handle arbitrary whitespace in the middle
  of them. As long as you don't misspell them, you can mangle their
  formatting quite a bit and they will parse correctly.

  Todo:
     * Okay, we might have to see about that "arbitrary"
       whitespace... :|

  .. warning:: These types of commands will be what SGLscript uses in
      the future. Positional arguments may be deprecated in the
      future, so please stick to using keyword arguments only if you
      want to play it safe. This will also make your scripts easier to
      read.

Both styles use identical syntax for values for arguments:

* If a value begins with a ``"`` or ``'``, it is a string. These
  behave the same as Python strings---you must escape the other type
  of quote with backslashes.

* If a value begins with a digit or ``-``, it is a
  number. Mathematical expressions are not currently allowed---you
  must just input numbers.

* Anything else is interpreted as a *keyword*---or a single word
  string. This string must have no spaces is in it, and it will be
  converted to lowercase during parsing. This is a shortcut for
  specifying short string arguments without having to type quotes.

  For example, the earlier example could be inputted as ``[show
  background: tree.png transition: fade-in fade time: 5]`` with no
  information being lost.

  .. warning:: Quoteless string values may be deprecated in the
      future. They can create some annoyingly ambiguous parsing situations
      with pretty commands, like ``[show thing: cool transition:
      "dissolve"]``. Is "cool" a positional argument or is the name of
      the keyword argument "cool transition"?

I cannot guarantee the behavior of anything left undescribed here. You
have been warned.

In addition, the parser supports some automatic manipulation of
commands during parsing. This is documented more thoroughly in
:any:`ParserSettings`.
"""

# To do:
# Get line numbers working correctly

def is_string(thing):
    if 'basestring' not in globals():
        return isinstance(thing, str)
    else:
        return isinstance(thing, basestring)

class ParserError(Exception):
    """ This exception handles errors that happened while parsing a
    script. """

    def __init__(self, text, line, char):
        self.text = text
        """ string: A short description of the error. """

        self.line = line
        """ int: The line the error occurred on. """

        self.char = char
        """ int: The index of the character of the error happened
        on. (Or the column number. It's not very consistent on
        this.) 

        Todo:
            * Fix that. Either rename this to ``col`` for actually
              make the :any:`Parser.error` function return the
              character index. """

class Label():
    """ A class to represent labels in the script. """

    def __init__(self, name, body):
        self.name = name
        """ The name of the label. """

        self.body = body
        """ list: A list of the elements inside this level. Each item
        should either be a string or :any:`Command` object."""

class Command():
    """ Represents a single command in a script. Converting this to a
    string should yield a parsable command. 

    Todo:
        * Make that yield a parsable *pretty* command. """

    def __init__(self, name, pos_arg=[], key_arg={}):
        self.name = name
        """ string: The name of the command. Always stored in the
        old form---with dashes instead of spaces. So
        "show background" will be "show-background".

        Todo:
            * Make it the other way around. Only known dependencies on
              this feature---the :any:`ScriptParser.header` function
              and command handling function in the Script module. """

        self.pos_arg = pos_arg
        """ list: A list of the positional arguments. """

        self.key_arg = key_arg
        """ dictionary: A dictionary of the keyword arguments. """

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
    """ A base class for handling recursive descent parsers (possibly
    badly).

    You should definitely not use this class in your own programs, but
    I need to document it for myself, so there. """

    def __init__(self, text=""):
        """ 
        Args:
            text (string): If this argument is specified, it will call
                :any:`load_text` with this text during initialization.
        """

        if text: self.load_text(text)

    def load_text(self, text):
        """ Loads text into the parser, and resets all the position counters. 

        Args:
            text (string): A string containing the text to
                load. Should be able to deal fine with
                Unicode. Should.
        """

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
        specify, raises an error with :any:`error`. 

        Args:
            char (string): The character the current character must be
                equal to. """

        if self.char == char:
            self.next()
        else:
            self.error("expected '" + char + "'")

    @property
    def prev_char(self):
        """ Read-only property returning the character before the
        current one. """

        return self.text[self.position-1]

    @property
    def next_char(self):
        """ Read-only property returning the character after the
        current one. """

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
        """ Returns if we're at the beginning of the content of the
        line. (As in, past the whitespace.) """

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
        """ Raises an error and prints information about the state of
        the parser.

        Args:
           text (string): A short description of the error.

        Raises:
           ParserError: Will always raise this. 

        Todo:
           * Maybe I should be using normal exceptions like a normal
             person? Not really sure how to easily do that while
             keeping track of the line and column position,
             though. """

        end = self.position+1
        start = self.text.rfind("\n", 0, end)
        if start == -1: start = 0
        print self.text[start:end]

        format_string = "line: {} pos: {} char: '{}'\nerror: \"{}\""
        print format_string.format(self.line, self.position, self.char, text)

        raise ParserError(text, self.line, self.col)

    def at_literal(self):
        """ Returns whether we currently at the beginning of a string
        or number literal. """

        return (self.char == "\"" or self.char == "'" or
                self.char.isdigit() or self.char == "-")

    def literal(self):
        """ Reads a string or number literal, and returns the parsed
        value. """

        if self.char == "\"" or self.char == "\'":
            item = self.string_literal()
        elif self.char.isdigit() or self.char == "-":
            item = self.number_literal()
        else:
            item = self.symbol()
        return item

    def string_literal(self):
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
        """ Reads a symbol name. 

        Todo:
           Has a bunch of hardcoded values for SGLscript. Factor out."""

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
        """ Keeps advancing the cursor until reaching non-whitespace characters.

        Args:
            allow_newline (bool): Whether to eat newlines as well. """

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
        """ Peeks ahead to see if the current line has any
        non-whitespace content or not. """

        position = self.position
        line = ""

        while position < len(self.text)-1:
            if self.text[position] == "\n": break

            line += self.text[position]
            position += 1

        line = line.strip()

        return line == "" or line.startswith(";;")

class ParserSettings(object):
    """ An object for holding settings on how the SGLscript parser
    behaves that the user is meant to be able to change. """

    macros = {}
    """ dictionary: A dictionary of macros and their replacement
    text. By default it is empty. 

    Macros are literally just text replacements. Whenever the parser
    encounters a macro, it will replace it with the replacement
    text. This replacement text can contain *anything,* including
    command invocations and other macros. The parser will attempt to
    prevent obvious recursive macros, but you can potentially crash
    the parser by defining macros that reference each other
    infinitely. 

    Todo:
        * More configurable macros, and different types. Like, have
          command alias macros, line macros (so that lines beginning
          and ending with certain characters can be handled
          differently, and that lines in all caps can be handled
          differently, enabling you to use Fountain-like formatting in
          your scripts), and so on.
        * It's probably a bad idea to allow regular expressions for
          these, right? """

    use_command_whitespace = False
    """ bool: Whether whitespace between commands in the middle of a paragraph
    is reproduced. By default, it isn't, which can be useful, but
    unexpected, since that isn't how most markup languages work. """

    default_pretty = False
    """ bool: Whether ambiguous commands (such as ``[wait a bit]``)
    are interpreted as normal commands (the command "wait" with the
    positional arguments "a" and "bit") or pretty commands (the
    command named "wait a bit"). If True, everything will be assumed
    to be a pretty command. Is False by default. """

    # Controls paragraph command generation
    add_paragraphs = True
    """ bool: Whether to automatically add "paragraph" commands after
    paragraphs (one or more blank lines in between blocks of
    text). By default is True. """

    paragraph_name = "paragraph"
    """ string: If :any:`add_paragraphs` is True, the command name to
    use for these paragraph commands. By default is "paragraph." """

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
        """ Returns whether a comment is beginning of the current
        spot. """

        return self.char == ";" and self.next_char == ";"

    def parse(self):
        """ Main function for parsing scripts. """

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
        """ Returns whether there is a colon inside a given
        command. Used to test in advance if a command is a pretty
        command. """

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
        """ Parses a symbol in the pretty command syntax---nearly any
        arbitrary set of characters followed by a colon. """

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
        """ Parses a command and returns a :any:`Command` object. """

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
        """ Parses and returns the arguments of a command. ``pretty``
        determines it does this assuming this is a pretty command or
        not. """

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
        """ Parses and returns plain text, making sure to return
        control to other parts of the program when we reach a other
        script elements. """

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
        """ Eats and returns everything until the end of the
        line. Used for comments. """

        result = ""
        while self.position_valid() and self.char not in ["\n"]:
            result += self.char
            self.next()
        return result

class HeaderError(Exception):
    def __init__(self, text):
        self.text = text

class ScriptParser(Parser):
    """ The object you'll be interacting with the most if you use this
    module. This is what actually lets you take a string, parse it,
    and get back the proper objects. 

    Todo:
        * Trash a good portion of BodyParser.
        * Un-hardcode the concept of labels. Have labels just be
          commands whose position is tracked so they can be quickly
          accessed. 
    """

    settings = ParserSettings()
    """ :any:`ParserSettings`: The object holding this parser's
    settings. Passed by reference to the body parses this object uses.

    By default is a default empty settings object. This is initialized
    in the class header. That's why the documentation says nonsense
    about an object reference. """

    def reset_settings(self):
        """ Resets all parser settings to their default values. """

        self.settings = ParserSettings()

    def parse(self):
        """ Parses a script loaded by :any:`load_text` and returns a
        dictionary of labels.

        Returns:
            dictionary: A dictionary in which the keys are the name of
                a given level, and the value is the corresponding
                :any:`Label` object.

        Todo:
            * :any:`Label` objects also contains the name of the
              label. There has to be a less dumb way to do this. """

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
        """ Parses special commands before the first label. You should
        not be calling this yourself, but the header is strange enough
        to warrant additional documentation.

        Currently, you can only use two commands here: 

        * ``define macro``: This takes two positional arguments. The
          first one is the original text, the second one is what to
          replace that text with. 
        * ``use pretty commands``: This determines whether to parse
          all commands as pretty commands or not. It only takes one
          positional argument, which must be the string or keyword
          "yes" to activate this. 

        If you attempt to use any other commands, or normal body text
        here, it will raise a HeaderError. Comments and all permutations of
        whitespace are fine.

        You can potentially raise a MacroError by defining macros that
        begin with characters that conflict with SGLscript (currently
        ``\\``, ``[``, and ``@``). Don't do this. 

        Both of those types of exceptions only have one parameter,
        ``text``, so I'm not documenting them in detail. """

        text = self.body()
        if not text: return

        header = BodyParser(text).parse()

        for item in header:
            # Only allow commands
            if isinstance(item, Command):

                if item.name in ["defmacro", "define-macro"] and len(item.pos_arg) == 2:
                    self.settings.macros[item.pos_arg[0]] = item.pos_arg[1]

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
        # """ Parses a label and returns a label object. """

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
        # """ Collect stuff until we reach a line starting with @ """
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


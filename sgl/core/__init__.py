import contextlib
import os
import sys
from functools import wraps
from Constants import *
from Errors import *

def needs_input(type):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not Backend.has_input(type): 
                raise UninitializedInputError(type)
            return function(*args, **kwargs)
        return wrapper
    return decorator

def needs_fake_input(type):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not Backend.has_fake_input(type): 
                raise FakeInputError(type)
            return function(*args, **kwargs)
        return wrapper
    return decorator

def needs_ability(ability):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if ability not in Backend.Meta.Abilities: 
                raise UnsupportedActionError(type)
            return function(*args, **kwargs)
        return wrapper
    return decorator

## SYSTEM
Backend = None

def init(width, height, scale=1, backend="pygame"):
    """ 
    init(width, height, scale=1, backend="pygame")

    Must be called before any other SGL functions to initiate the
    drawing surface.

    :param int width, height: Specifies the size of the display
        surface.

    :param int scale: Specifies the scaling factor. Width and height
        will be multiplied by this to form the actual window size.  This
        is useful for working with small resolutions, such as 320x240.

    :param str backend: Which backend to use. Currently, the only
        supported option is "pygame".
    """

    if backend == "pygame":
        import PygameBackend
        global Backend
        Backend = PygameBackend.Backend()
        
    else:
        raise UnsupportedBackendError()

    # Sort of hacky, but the only way I could figure out how to get
    # this to work. If you try doing:
    # 
    #     global key
    #     key = Backend.Meta.KeyCodes
    #     
    # ...and then trying to access "sgl.key.up" or something, it will
    # complain that "sgl.key" has never been defined. I guess this is
    # because the "from core import *" in the parent directory's
    # __init__.py only gets the variable bindings *once,* and never
    # updates them. So we have to manually update it.
    #
    # Only alternative seems to be to change the module structure,
    # which I'm considering.
    sys.modules["sgl"].key = Backend.Meta.KeyCodes

    Backend.init(width, height, scale)

def run(update=None, draw=None):
    """ 
    run(update=None, draw=None)

    Starts an SGL program that automatically manages the event loop.
    SGL will call the specified callbacks every frame, and it is in
    these that you will specify your game logic.

    :param function update: A function to call every frame to update
        your game's state.

    :param function draw: A function to call every frame to draw the
       current frame. Do not put any game logic in this function. No
       backends currently do this, but in the future, some might take
       advantage of the difference between update and draw to, for
       example, pause the game by calling update but not draw.
    """

    if not (update and draw):
        raise ArgumentError("Must specify update and draw")

    Backend.run(update, draw)

@needs_ability(abilities.numpy)
def make_movie(file="", update=None, draw=None, duration=0, fps=24, realtime=False, display=True, **extra):
    """ 
    make_movie(file="", update=None, draw=None, duration=0, fps=24, realtime=False, display=True, **extra)

    Similar to :py:func:`sgl.run`, but uses `MoviePy <http://zulko.github.io/moviepy/>`_ to render each frame of your
    program to a video file or animated GIF.

    :param str file: The filename of the movie you wish to output.

    :param function update, draw: Works the same as with 
        :py:func:`sgl.run`.

    :param number duration: The amount of your program's execution you
        want to record, in seconds.

    :param number fps: What the frame rate of the resulting video will
        be. ``make_movie`` will force your program's frame rate to match
        with :py:func:`sgl.set_fps_limit`.

    :param boolean realtime: If the video renders faster than the
        frame rate you specify, this will slow down the speed of the video
        rendering to match. This is useful when you have "display" enabled
        and you want to, say, use your program while recording it. By
        default it is false.

    :param boolean display: Whether to draw the current frame to the
        screen, in addition to rendering into the video file. Useful if
        you want to interact with your program as it is rendering to video.

    :param various extra: Additional keyword arguments are passed to
        MoviePy's ``write_videofile`` or ``write_gif`` functions. You can use this
        to specify additional settings about which codecs to use and such.
    """

    import moviepy.editor
    import numpy as np

    set_fps_limit(fps)
    Backend.enter_movie_mode(realtime)

    def get_frame(time):
        update()
        draw()
        if display: frame()
 
        array = to_numpy().swapaxes(0,1).copy()
        return array

    clip = moviepy.editor.VideoClip(make_frame=get_frame, duration=duration)

    extension = os.path.splitext(file)[1].lower()
    if extension == ".gif":
        clip.write_gif(file, fps=fps, **extra)
    else:
        clip.write_videofile(file, fps=fps, **extra)        

def frame():
    """ 
    frame()

    Displays the current frame, collects event data, and updates delta
    time. You only need to call this if you're manually managing your
    own event loop. (Although at some point I might allow you to
    customize where the event data is gathered with sgl.run() with
    this. Hmmm.)
    """

    Backend.frame()

def set_fps_limit(fps):
    """ 
    set_fps_limit(fps)

    Sets the highest frame rate your program will allow. More
    specifically, it makes your program assume that the frame rate is
    *always* this value, as opposed to what it is in reality. This can
    make programming animation more convenient, but comes with some
    side effects--such as that, if the frame rate of your program
    drops, it will start running in slow motion.

    :param int fps: The desired framerate. Set to 0 to disable
        framerate limiting.
    """

    Backend.set_fps_limit(fps)

def get_fps_limit():
    """ 
    get_fps_limit()

    Gets the framerate limit. If there is no framerate limiting, will return 0.

    :return: The framerate limit
    :rtype: int
    """
    return Backend.get_fps_limit()

def get_fps():
    """ 
    get_fps()

    Gets the current framerate. This will return the *actual* frame
    rate, even if the limit has been set with :py:func:`sgl.set_fps_limit()`.

    :return: The current framerate 
    :rtype: float
    """

    return Backend.get_fps()

def get_scale():
    """ 
    get_scale()

    Gets the window's scaling factor. SGL automatically takes into
    account the scaling factor when returning, say, mouse coordinates,
    so there shouldn't be any reason to call this--it's just for
    completeness sake.

    Currently, is no setting the scaling factor--if you want to make a
    program in which the scaling factor appears to change, use
    surfaces and end the scaling abilities of :py:func:`sgl.blit` to simulate
    this. This functionality may be added in the future, though.

    :return: The current scaling factor       
    :rtype: int
    """

    return Backend.get_scale()

def has(ability):
    """ 
    has(ability)

    Returns whether the current backend has a given ability. The
    abilities are specified in the enum-like class
    sgl.abilities. There are currently only four abilities you can
    test for:

    * ``sgl.abilities.software``: Whether the current backend is powered
      by software rendering, and thus will be slow at special effects
      such as rotating and scaling.

    * ``sgl.abilities.numpy``: Whether the current backend supports
      exporting and importing surfaces to NumPy arrays.

    * ``sgl.abilities.save_buffer``: Whether the current backend supports
      saving surfaces to image files.

    The Pygame backend supports all of these.

    :param int ability: The ability to test

    :return: Whether the current backend supports this ability
    :rtype: bool
    """

    return ability in Backend.Meta.Abilities

def set_title(title):
    """ 
    set_title(title)

    Sets the text in the title bar of the current window.

    :param str title: The text to put in the title bar
    """

    Backend.set_title(title)

def get_title(title):
    """ 
    get_title(title)

    Gets the text currently in the title bar of the current window.

    :return: The text in the title bar
    :rtype: str
    """

    return Backend.get_title(title)

def get_actual_screen_width():
    """ 
    get_actual_screen_width()

    Gets the width of the current window after applying the scaling
    factor. You should not need to get this. I should probably get rid
    of this function.

    :return: The window width
    :rtype: int
    """

    return Backend.get_actual_screen_width()

def get_actual_screen_height():
    """ 
    get_actual_screen_height()

    Gets the height of the current window after applying the scaling
    factor. You should not need to get this. I should probably get rid
    of this function.

    :return: The window height
    :rtype: int
    """

    return Backend.get_actual_screen_height()

def get_dt():
    """ 
    get_dt()

    Gets *delta time,* or the time that has passed since the last
    frame is been rendered. If you do not have framerate limiting
    enabled for your program, you must multiply every animation value
    by this value if you expect your program to work consistently on
    different types of computers.

    Unlike some other game libraries, this value is returned in
    *seconds,* not milliseconds.

    :return: The time that has passed since the last frame in seconds
    :rtype: float 
    """

    return Backend.get_dt()

def is_running():
    """ 
    is_running()

    Returns whether your program is running. Useful for when you are
    manually managing the event loop, and you want your program to end
    under the same conditions an automatic SGL program would.

    :return: Whether your program is running
    :rtype: Bool
    """

    return Backend.is_running()

def end():
    """ 
    end()

    Halts execution of the program, and closes the window.
    """

    Backend.end()

## AUDIO
def load_sound(file):
    """ 
    load_sound(file)

    Loads a sound file from the hard drive.

    :return: An object representing the loaded sound
    :rtype: SGL sound
    """

    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.SoundTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_sound(file)

def play_sound(sound, volume=1.0, loops=0):
    """ 
    play_sound(sound, volume=1.0, loops=0)

    Plays a previously loaded sound.

    :param sound: The sound object to play 
    :type sound: SGL sound

    :param float volume: The volume to play the sound at, specified as
        a float. (So, 1.0 would be full volume, 0.5 would be half
        volume, and so on.)

    :param int loops: How many times to loop playback of the sound. If
        this is 0, the default, the sound will only play once. If it
        is -1, it will play forever, until :py:obj:`sgl.stop_sound` is
        called on it.
    """

    Backend.play_sound(sound, volume, loops)

def stop_sound(sound):
    """ 
    stop_sound(sound)

    Stops the specified sound.

    :param sound: The sound object to stop
    :type sound: SGL sound
    """

    Backend.stop_sound(sound)

def stop_all_sounds():
    """ 
    stop_all_sounds()

    Stops all currently playing sounds.

    """

    Backend.stop_all_sounds()

def is_sound_playing(sound):
    """ 
    is_sound_playing(sound)

    Determines whether the specified sound is currently playing.

    :param sound: The sound object to query 
    :type sound: SGL sound

    :return: Whether the sound is playing
    :rtype: bool
    """

    return Backend.is_sound_playing(sound)

def play_music(file, volume=1.0, loops=-1):
    """ 
    play_music(file, volume=1.0, loops=-1)

    Plays, by default, infinitely looping background music. Music,
    unlike sounds, do not need to be loaded in advance. They are
    loaded when you call this function. Because of this, only one
    music track can be playing at once.

    :param str file: The filename of the music to play

    :param float volume: The volume to play the music at, specified as
        a float. (So, 1.0 would be full volume, 0.5 would be half
        volume, and so on.)

    :param int loops: How many times to loop playback of the music. 
        By default, this is -1, which will look the music forever,
        until :py:obj:`sgl.stop_music()` is called.
    """

    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.MusicTypes:
        raise UnsupportedFormatError(file, extension)

    Backend.play_music(file, volume, loops)

def pause_music():
    """ 
    pause_music()

    Pauses the currently playing piece of music. This is different from
    :py:obj:`sgl.stop_music()` in that you can later call
    :py:obj:`sgl.resume_music()` to resume the song from the
    exact point at which you paused it. With stopping, you have
    no choice but to restart the song.
    """

    Backend.pause_music()

def resume_music():
    """ 
    resume_music()

    Resumes a piece of music that has been paused with :py:func:`sgl.pause_music`.
    """

    Backend.resume_music()

def set_music_volume(volume):
    """ 
    set_music_volume(volume)

    Sets the volume of the currently playing music.

    :param float volume: The volume to play the music at, specified as
        a float. (So, 1.0 would be full volume, 0.5 would be half
        volume, and so on.)
    """

    Backend.set_music_volume(volume)

def stop_music():
    """ 
    stop_music()

    Stops the currently playing music. This music will not be able to
    be resumed with :py:func:`sgl.pause_music`.
    """

    Backend.stop_music()

def is_music_playing():
    """ 
    is_music_playing()

    Returns whether any music is currently playing.

    :return: Whether any music is playing
    :rtype: bool
    """

    return Backend.is_music_playing()

## GRAPHICS
def set_transparent_color(*color):
    """ 
    set_transparent_color(*color)

    Sets what color will be considered transparent in images without
    an alpha channel. By default, this color is set to (255, 0, 255),
    or "magic magenta."

    """

    Backend.set_transparent_color(*color)

def load_image(file, use_transparent_color=True):
    """ 
    load_image(file, use_transparent_color=True)

    Loads an image without an alpha channel from the hard drive.

    :return: A surface containing the image loaded
    :rtype: SGL surface
    """

    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.ImageTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_image(file, use_transparent_color)

def load_alpha_image(file):
    """ 
    load_alpha_image(file)

    Loads an image with an alpha channel from the hard drive.

    :return: A surface containing the image loaded
    :rtype: SGL surface
    """

    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.ImageTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_alpha_image(file)

def blitf(thing, x, y):
    """ 
    blitf(thing, x, y)

    A lightweight version of :py:obj:`sgl.blit` that does not perform
    any special effects on the surface being drawn. May be slightly
    faster.

    :param thing: The thing that should be drawn to the current
        surface.

    :type thing: SGL surface

    :param int x, y: Specifies the accordance on the current surface
       that ``thing`` should be drawn.
    """

    Backend.blitf(thing, x, y)

def blit(thing, x, y, alpha=255, flip_v=False, flip_h=False, 
         angle=0, width=None, height=None, scale=1, a_x=0, a_y=0, 
         src_x=0, src_y=0, src_width=None, src_height=None, 
         blend_mode=0, pretty=False):    
    """ 
    Draws one surface to another. This function is kind of the
    motherlode of SGL, and provides most of the library's drawing
    functionality.

    Since this function takes so many arguments, it is recommended you
    use keyword arguments for everything beyond ``x`` and ``y``. For
    example, a typical call to this function might look like this::

        sgl.blit(self.player, 16, 16, flip_h=True, angle=45, a_x=0.5, a_y=0.5)

    :param thing: The thing that should be drawn (or `blitted
        <https://en.wikipedia.org/wiki/Bit_blit>`_) to the current
        surface.  

        Is an SGL surface value.

    :type thing: SGL surface

    :param int/float x, y: Specifies the coordinates on the current surface
       that ``thing`` should be drawn.

       Currently, passing in floats will just result in them being
       rounded to integers.

    :param int/float alpha: A number specifying how transparent ``thing`` should
       be drawn. 

       If it is an integer, this should be a value between 0 and 255,
       with 0 being invisible and 255 being completely opaque.

       If it is a float, this should be a value between 0.0 and 1.0,
       with zero being invisible and 1.0 being completely opaque.

    :param bool flip_v, flip_h: Specifies whether ``thing`` should be
       horizontally or vertically flipped. 

       Setting ``width`` or ``height`` to negative values will also
       flip a graphic.

    :param int angle: The angle to which ``thing`` should be
       rotated. The angle should be in degrees, and should be a value
       between 0 to 360 (although the code currently does not check
       this. It probably should). 
    
       Note that on software renderers, such as Pygame, rotation is
       fairly slow. You can rotate a few graphics, such as the player
       graphic, in real time, but it is recommended you cache rotated
       sprites if you plan to rotate many things at once.

    :param int width, height: Specifies the width and height to resize
        ``thing`` to. 
    
        If either of these values is not specified, it will be filled
        in with the original width/height of ``thing``.
    
        If either of these values is 0, ``thing`` will not be drawn.
    
        If either is negative, ``thing`` will be drawn backwards in
        whatever direction resizing it takes.

    :param float scale: Enables you to scale ``thing`` by a ratio,
        keeping its aspect ratio. 1.0, the default, will draw ``thing`` at
        its normal size, 0.5 will draw it half as big, and so on. 
    
        This can be combined with width and height, and is applied
        after those values are calculated.

    :param int/float a_x, a_y: Specifies the anchor point of ``thing``--the
        coordinates of the graphic that is considered (0, 0). Useful
        in conjunction with ``angle`` to rotate about different points
        of the graphic than the top left corner. 
    
        If these values are integers, they will be interpreted as
        exact coordinates on ``thing``.
    
        If these values are floats, they will be interpreted as a
        percentage of the size of ``thing``. (As in, setting both anchor
        points to 0.5 will make the anchor point the center of the
        image.)

    :param int src_x, src_y, src_width, src_height: Makes the function apply to the
        specified rectangle of ``thing``. This is applied before the other
        functions are. This is a convenience to avoid having to do
        :py:obj:`sgl.get_chunk` whatever you want to draw a small chunk of
        a larger image.
    
        On hardware accelerated backends, this may be faster than
        using :py:obj:`sgl.get_chunk`.

    :param int blend_mode: Specifies the blending mode to use when
        drawing ``thing``. Should be a constant from ``sgl.blend``.
    
        Currently, the only available blending values are:
    
        * ``sgl.blend.add`` - Adds the colors of ``thing``'s pixels to
          the pixels behind it. So, black pixels will become
          transparent, white pixels will stay white, and everything
          in between will make the image behind slightly brighter.

        * ``sgl.blend.subtract`` - Subtracts the colors of ``thing``'s
          pixels from the pixels behind it. So, black pixels will
          become transparent, and white pixels will invert the
          background to certain degree.

        * ``sgl.blend.multiply`` - Multiply the colors of ``thing``'s
          pixels from the pixels behind it. So, white pixels will
          become transparent, black pixels will stay black, and
          everything else will be make the image behind slightly
          darker.

    :param boolean pretty: Specifies whether the results of scaling
        and/or rotating ``thing`` should be smoothed out or not. 
    
        This will slow down rendering in most cases.
    """

    Backend.blit(thing, x, y, alpha, flip_v, flip_h, 
                 angle, width, height, scale, 
                 a_x, a_y, 
                 src_x, src_y, src_width, src_height, 
                 blend_mode, pretty)

## DRAWING
def set_smooth(smooth):
    """ 
    set_smooth(smooth)

    Sets whether lines for shapes should be anti-aliased or
    not. Currently no backend supports this.

    :param bool smooth: Whether anti-aliasing should be enabled
    """

    Backend.set_smooth(smooth)

def get_smooth():
    """ 
    get_smooth()

    Returns whether anti-aliasing is enabled or not.

    :return: Whether anti-aliasing is enabled
    :rtype: bool
    """

    return Backend.get_smooth()

def set_fill(*color):
    """ 
    set_fill(*color)

    Sets the color with which shapes are filled. Also affects what color
    fonts are rendered in.

    """

    Backend.set_fill(*color)

def get_fill():
    """ 
    get_fill()

    Gets the current fill color.

    :return: The current fill color, or ``None`` if fill is disabled
    :rtype: tuple
    """

    return Backend.get_fill()

def set_stroke(*color):
    """ 
    set_stroke(*color)

    Sets the color in which shapes are outlined.

    """

    Backend.set_stroke(*color)

def get_stroke():
    """ 
    get_stroke()

    Gets the current stroke color.

    :return: The current stroke color, or ``None`` if stroke is disabled
    :rtype: tuple
    """

    return Backend.get_stroke()

def set_stroke_weight(weight):
    """ 
    set_stroke_weight(weight)

    Sets how thick the lines outlining shapes will be. Setting this to
    0 will disable stroke rendering.

    """

    Backend.set_stroke_weight(weight)

def get_stroke_weight():
    """ 
    get_stroke_weight()

    Gets the current stroke weight.

    :return: The current fill weight
    :rtype: int
    """

    return Backend.get_stroke_weight()

def no_stroke():
    """ 
    no_stroke()

    Turns off stroke rendering.

    """

    Backend.no_stroke()

def no_fill():
    """ 
    no_fill()

    Turns off fill rendering.

    """

    Backend.no_fill()

def clear(*color):
    """ 
    clear(*color)

    Completely fills the current surface with the specified color.

    """

    Backend.clear(*color)

def draw_line(x1, y1, x2, y2):
    """ 
    draw_line(x1, y1, x2, y2)

    Draw the line between the specified coordinates.

    """

    Backend.draw_line(x1, y1, x2, y2)

def draw_rect(x, y, width, height):
    """ 
    draw_rect(x, y, width, height)

    Draws a rectangle in the specified area.

    """

    Backend.draw_rect(x, y, width, height)

def draw_ellipse(x, y, width, height, from_center=False):
    """ 
    draw_ellipse(x, y, width, height, from_center=False)

    Draws an ellipse in the specified area.

    """

    Backend.draw_ellipse(x, y, width, height, from_center)

def draw_circle(x, y, radius, from_center=True):
    """ 
    draw_circle(x, y, radius, from_center=True)

    Draws a circle in the specified area.

    """

    Backend.draw_circle(x, y, radius, from_center)
    
## TEXT
def set_font_smooth(smooth):
    """ 
    set_font_smooth(smooth)

    Specifies whether text is anti-aliased or not.

    """

    Backend.set_font_smooth(smooth)

def get_font_smooth():
    """ 
    get_font_smooth()

    Returns whether text is anti-aliased or not.

    :return: Whether font antialiasing is enabled
    :rtype: bool
    """

    return Backend.get_font_smooth()

def load_font(file, size):
    """ 
    load_font(file, size)

    Loads a font from a font file in your program folder.

    :return: The loaded font
    :rtype: SGL font object
    """

    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.FontTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_font(file, size)

def load_system_font(font_name, size):
    """ 
    load_system_font(font_name, size)

    Loads a font from the user's system via the font's name.

    :return: The loaded font
    :rtype: SGL font object
    """

    return Backend.load_system_font(font_name, size)

def set_font(font):
    """ 
    set_font(font)

    Sets what font is used for all future drawing operations.

    """

    Backend.set_font(font)

def draw_text(text, x, y):
    """ 
    draw_text(text, x, y)

    Draws the specified text at the specified coordinates.

    """

    Backend.draw_text(text, x, y)

def get_text_width(text):
    """ 
    get_text_width(text)

    Gets how wide the specified string will be when rendered in the current font.

    :return: The width of the rendered text
    :rtype: int
    """

    return Backend.get_text_width(text)

def get_text_height(text=""):
    """ 
    get_text_height(text="")

    Gets how tall the specified string will be when rendered in the
    current font. Usually will just return the height of the current
    font.

    :return: The height of the text
    :rtype: int
    """

    return Backend.get_text_height(text)

## SURFACES
def pop():
    """ 
    pop()

    Pops the current graphics state from the stack. This will make all
    the drawing settings return to what they were the last time
    :py:obj:`sgl.push` was called.
    """


    Backend.pop()

def push():
    """ 
    push()

    Pushes the current graphics state to the stack. So, the next time
    you call :py:obj:`sgl.pop`, it will restore this state. You can
    use this to change the drawing colors and what current surface is,
    and reset them later.
    """

    Backend.push()

def make_surface(width, height, *color):
    """ 
    make_surface(width, height, *color)

    Makes a new blank surface of the specified color. If no color
    specified, the new surface will be blank and transparent.

    :return: The created surface
    :rtype: SGL surface 
    """

    return Backend.make_surface(width, height, *color)

def get_chunk(x, y, width, height):
    """ 
    get_chunk(x, y, width, height)

    Takes a chunk out of the current surface and returns it as a new
    copy surface. Useful for separating out, say, individual frames
    from spritesheets.

    :param int x, y: The coordinates to start extracting

    :param int width, height: The width and height of the rectangle
        to extract

    :return: The extracted surface
    :rtype: SGL surface 
    """

    return Backend.get_chunk(x, y, width, height)

def set_buffer(surface):
    """ 
    set_buffer(surface)

    Sets which surface is the *drawing buffer*--the surface on which
    all future drawing operations will take place. You can also think
    of this as the "current surface," and many parts of the
    documentation refer to it like this).

    :param surface: The surface that will become the current surface
    :type surface: SGL surface
    """

    Backend.set_buffer(surface)

def reset_buffer():
    """ 
    reset_buffer()

    Sets the drawing buffer to refer to the screen buffer. If you
    manage the stack correctly, you shouldn't need to use this, but this
    is here just in case.
    """

    Backend.reset_buffer()

def get_width():
    """ 
    get_width()

    Gets the width of the current surface.

    :return: The width of the current surface, in pixels
    :rtype: int
    """

    return Backend.get_width()

def get_height():
    """ 
    get_height()

    Gets the height of the current surface.

    :return: The height of the current surface, in pixels
    :rtype: int
    """

    return Backend.get_height()

def set_clip_rect(x, y, width, height):
    """ 
    set_clip_rect(x, y, width, height)

    Sets the clipping rectangle--makes it so all future rendering
    operations will only affect the specified rectangle of the current
    surface.
    """

    return Backend.set_clip_rect(x, y, width, height)

def no_clip_rect():
    """ 
    no_clip_rect()

    Turns off rendering clipping.
    """

    return Backend.no_clip_rect()


def get_clip_rect():
    """ 
    get_clip_rect()

    Returns the size of the current clipping rectangle.

    :return: A four element tuple, or None
    :rtype: tuple
    """

    return Backend.get_clip_rect()

def invert(surface=None):
    """ 
    invert(surface=None)

    Inverts the colors of either the current surface or whatever surface is passed in.

    :return: A new surface, with the effect applied, or nothing
    :rtype: SGL surface
    """

    return Backend.invert(surface)

def grayscale(surface=None):
    """ 
    grayscale(surface=None)

    Turns to grayscale either the current surface or whatever surface is passed in.

    :return: A new surface, with the effect applied, or nothing
    :rtype: SGL surface
    """

    return Backend.grayscale(surface)

@needs_ability(abilities.save_buffer)
def save_image(file):
    """ 
    save_image(file)

    Saves the image in the current surface to the specified filename.

    :param str file: The filename of the image to save to. The
        extension will determine the file type.
    """

    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.ImageSaveTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.save_image(file)

@needs_ability(abilities.numpy)
def to_numpy():
    """ 
    to_numpy()

    Exports the current surface as a NumPy array. On some back ends,
    such as Pygame, this might return a "live" NumPy array that is
    linked the original surface--as in changing the array will
    instantly change the surface. This is much more efficient than the
    alternative, but can be unexpected.

    :return: The pixel data of the current surface, in a three-dimensional array
    :rtype: NumPy array
    """

    return Backend.to_numpy()

@needs_ability(abilities.numpy)
def from_numpy(array):
    """ 
    from_numpy(array)

    Creates a new surface from a NumPy array.

    :param array: A three-dimensional array consisting of RGB values.
    :type array: NumPy array

    :return: The surface represented by the array
    :rtype: SGL surface
    """

    return Backend.from_numpy(array)

## FAKE INPUT
def add_fake_input(type):
    """ Adds a fake input. There must not be an equivalent real input defined. """

    Backend.add_fake_input(type)

@needs_fake_input(input.keyboard)
def got_key_down(key):
    """ 
    got_key_down(key)

    Simulates a key on the keyboard being pressed down.
    """

    Backend.got_key_down(key)

@needs_fake_input(input.keyboard)
def got_key_up(key):
    """ 
    got_key_up(key)

    Simulates a key on the keyboard being released. If you do not call
    this function, SGL will think the key has been pressed down
    forever.
    """

    Backend.got_key_up(key)

@needs_fake_input(input.mouse)
def got_mouse_move(x, y):
    """
    got_mouse_move(x, y)

    Simulates the mouse moving to a new point.
    """

    Backend.got_mouse_move(x, y)

@needs_fake_input(input.mouse)
def got_mouse_down(button=1):
    """
    got_mouse_down(button=1)

    Simulates a mouse button being pressed.
    """

    Backend.got_mouse_down(button)

@needs_fake_input(input.mouse)
def got_mouse_up(button=1):
    """
    got_mouse_up(button=1)

    Simulates a mouse button being released. Similarly to
    :py:func:`sgl.got_key_up`, this is necessary for SGL to ever
    consider a mouse button released.
    """

    Backend.got_mouse_up(button)

## INPUT
def add_input(type):
    """ 
    add_input(type)

    Initializes support for a specified type of input.

    :param int type: The type of input to add. Should be a
        constant from ``sgl.input``.
    """

    if type not in Backend.Meta.InputTypes:
        raise UnsupportedInputError(type)

    Backend.add_input(type)

def supports_input(type):
    """
    supports_input(type)

    Returns whether the backend supports the specified input
    type. Might be integrated into :py:func:`sgl.has` later.

    :param int type: The type of input to test. Should be a
        constant from ``sgl.input``.

    :return: Whether the specified type of input is supported by this backend
    :rtype: bool
    """

    return type in Backend.Meta.InputTypes


def remove_input(type):
    """
    remove_input(type)

    Removes support for a specified type of input. It does not matter
    whether this input is real or fake--it will remove it regardless.

    :param int type: The type of input to remove. Should be a
        constant from ``sgl.input``.
    """

    Backend.remove_input(type)

def has_input(type):
    """
    has_input(type)

    Returns whether a specified input type is handled or
    not. Intentionally does not distinguish between real and fake
    inputs.

    :param int type: The type of input to test. Should be a
        constant from ``sgl.input``.

    :return: Whether the specified type of input is currently handled
    :rtype: bool
    """

    return Backend.has_input(type)

@needs_input(input.keyboard)
def on_key_down(key):
    """
    on_key_down(key)

    Briefly returns `True` on the frame a keyboard key is pressed down.

    :param int key: The key code of the key to test. Should be a
        constant from ``sgl.key``.

    :return: Whether a key has just been pressed down
    :rtype: bool
    """

    return Backend.on_key_down(key)

@needs_input(input.keyboard)
def on_key_up(key):
    """
    on_key_up(key)

    Briefly returns `True` on the frame a keyboard key is released.

    :param int key: The key code of the key to test. Should be a
        constant from ``sgl.key``.

    :return: Whether a key has just been released
    :rtype: bool
    """

    return Backend.on_key_up(key)

@needs_input(input.keyboard)
def is_key_pressed(key):
    """
    is_key_pressed(key)

    Returns `True` if the specified keyboard key is currently pressed.

    :param int key: The key code of the key to test. Should be a
        constant from ``sgl.key``.

    :return: Whether a key is currently down
    :rtype: bool
    """

    return Backend.is_key_pressed(key)

@needs_input(input.keyboard)
def get_keys_pressed():
    """
    get_keys_pressed()

    Returns a list of all the keyboard keys currently pressed.

    :return: A list of all pressed keys
    :rtype: list of ints
    """

    return Backend.get_keys_pressed()

@needs_input(input.keyboard)
def get_letters_pressed():
    """
    get_letters_pressed()

    Returns a string containing all the characters typed in the last
    frame. Handles capitalizing letters and changing characters when
    shift is pressed.

    :return: The text typed in the last frame
    :rtype: str
    """

    return Backend.get_letters_pressed()

@needs_input(input.mouse)
def show_mouse():
    """
    show_mouse()

    Shows the system mouse cursor.

    """

    Backend.show_mouse()

@needs_input(input.mouse)
def hide_mouse():
    """
    hide_mouse()

    Hides the system mouse cursor.

    """

    Backend.hide_mouse()

@needs_input(input.mouse)
def get_prev_mouse_x():
    """
    get_prev_mouse_x()

    Returns what the mouse cursor's x position was on the previous
    frame. Exists for convenience and because when managing the event
    loop automatically, it is impossible for your program to retrieve
    this value manually.

    :return: The mouse's x coordinates on the previous frame
    :rtype: int
    """

    return Backend.get_prev_mouse_x()

@needs_input(input.mouse)
def get_prev_mouse_y():
    """
    get_prev_mouse_y()

    Returns what the mouse cursor's y position was on the previous
    frame. 

    :return: The mouse's y coordinates on the previous frame
    :rtype: int
    """

    return Backend.get_prev_mouse_y()

@needs_input(input.mouse)
def get_mouse_x():
    """
    get_mouse_x()

    Returns what the mouse cursor's x position on the current frame.

    :return: The mouse's x coordinates
    :rtype: int
    """

    return Backend.get_mouse_x()

@needs_input(input.mouse)
def get_mouse_y():
    """
    get_mouse_y()

    Returns what the mouse cursor's y position on the current frame.

    :return: The mouse's y coordinates
    :rtype: int
    """

    return Backend.get_mouse_y()

@needs_input(input.mouse)
def on_mouse_down(button=1):
    """
    on_mouse_down(button=1)

    Briefly returns `True` on the frame the specified mouse button is
    pressed down. By default, it tests for the left mouse
    button--button #1. Does not intelligently determine what the left
    mouse button is if the user has used their system settings to swap
    the functions of the mouse buttons.

    :param int button: The number of the mouse button to test. Is 1 by
        default.

    :return: Whether a mouse button has just been pressed down
    :rtype: bool
    """

    return Backend.on_mouse_down(button)

@needs_input(input.mouse)
def on_mouse_up(button=1):
    """
    on_mouse_up(button=1)

    Briefly returns `True` on the frame the specified mouse button is
    released. 

    :param int button: The number of the mouse button to test. Is 1 by
        default.

    :return: Whether a mouse button has just been released
    :rtype: bool
    """

    return Backend.on_mouse_up(button)

@needs_input(input.mouse)
def is_mouse_pressed(button=1):
    """
    is_mouse_pressed(button=1)

    Returns `True` if the specified mouse button is
    currently pressed down. 

    :param int button: The number of the mouse button to test. Is 1 by
        default.

    :return: Whether a mouse button is pressed
    :rtype: bool
    """

    return Backend.is_mouse_pressed(button)

@needs_input(input.mouse)
def get_mouse_buttons_pressed():
    """
    get_mouse_buttons_pressed()

    Returns a list of all the currently pressed mouse buttons. 

    :return: A list of all the pressed mouse buttons
    :rtype: list of ints
    """

    return Backend.get_mouse_buttons_pressed()

@needs_input(input.joystick)
def on_joy_down(button):
    """
    on_joy_down(button)

    Briefly returns `True` on the frame the specified joystick button is
    pressed down. 

    :param int button: The number of the joystick button to test

    :return: Whether a joystick button has just been pressed down
    :rtype: bool
    """

    return Backend.on_joy_down(button)

# todo: implement hat/dpad as button=sgl.joy.down or something?

@needs_input(input.joystick)
def on_joy_up(button):
    """
    on_joy_up(button)

    Briefly returns `True` on the frame the specified joystick button is
    released. 

    :param int button: The number of the joystick button to test

    :return: Whether a joystick button has just been pressed released
    :rtype: bool
    """

    return Backend.on_joy_up(button)

@needs_input(input.joystick)
def is_joy_pressed(button):
    """
    is_joy_pressed(button)

    Returns `True` if the specified joystick button is
    currently pressed down. 

    :param int button: The number of the joystick button to test

    :return: Whether a joystick button is pressed
    :rtype: bool
    """

    return Backend.is_joy_pressed(button)

@needs_input(input.joystick)
def get_joy_buttons_pressed():
    """
    get_joy_buttons_pressed()

    Returns a list of all the currently pressed joystick buttons. 

    :return: A list of all the pressed joystick buttons
    :rtype: list of ints
    """

    return Backend.get_joy_buttons_pressed()

@needs_input(input.joystick)
def get_joy_axis(axis):
    """
    get_joy_axis(axis)

    Returns the value of a joystick's given "axis". There is usually a
    separate axis for each direction of each stick. For example, there
    might be an axis for the horizontal motion of the left stick, the
    vertical motion of the left stick, and axes for both on right
    stick. Some joysticks, however, use axes for other things as well,
    such as pressure sensitive buttons. Experiment to figure out which
    is which.

    :param int axis: The axis to get the value from

    :return: The value reported by the current axis
    :rtype: float
    """    

    return Backend.get_joy_axis(axis)

@needs_input(input.joystick)
def get_joy_num_axes():
    """
    get_joy_num_axes()

    Returns the amount of axes this joystick reports having.

    :return: The number of axes on this joystick
    :rtype: int
    """    

    return Backend.get_joy_num_axes()

## HELPER
@contextlib.contextmanager
def with_buffer(buffer):
    """ 
    with_buffer(buffer)

    A `context manager
    <https://docs.python.org/2/reference/compound_stmts.html#with>`_
    that makes all enclosed drawing operations apply to a given
    buffer. Useful to avoid manually dealing with the stack.

    :param buffer: The buffer to draw on
    :type buffer: SGL buffer
    """

    push()
    set_buffer(buffer)
    yield
    pop()

@contextlib.contextmanager
def with_state():
    """ 
    with_state()

    A `context manager
    <https://docs.python.org/2/reference/compound_stmts.html#with>`_
    that saves the current drawing state and restores it when the
    enclosed operations are finished. Useful to avoid manually having
    to call :py:obj:`sgl.push` and :py:obj:`sgl.pop`.
    """

    push()
    yield
    pop()

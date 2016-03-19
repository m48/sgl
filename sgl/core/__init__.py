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
    if not (update and draw):
        raise ArgumentError("Must specify update and draw")

    Backend.run(update, draw)

@needs_ability(abilities.numpy)
def make_movie(file="", update=None, draw=None, duration=0, fps=24, width=0, height=0, realtime=False, display=True, **extra):
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
    Backend.frame()

def set_fps_limit(fps):
    Backend.set_fps_limit(fps)

def get_fps_limit():
    return Backend.get_fps_limit()

def get_fps():
    return Backend.get_fps()

def get_scale():
    return Backend.get_scale()

def has(ability):
    return ability in Backend.Meta.Abilities

def set_title(title):
    Backend.set_title(title)

def get_title(title):
    return Backend.get_title(title)

def get_actual_screen_width():
    return Backend.get_actual_screen_width()

def get_actual_screen_height():
    return Backend.get_actual_screen_height()

def get_dt():
    return Backend.get_dt()

def is_running():
    return Backend.is_running()

def end():
    Backend.end()

## AUDIO
def load_sound(file):
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.SoundTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_sound(file)

def play_sound(sound, volume=1.0, loops=0):
    Backend.play_sound(sound, volume, loops)

def stop_sound(sound):
    Backend.stop_sound(sound)

def stop_all_sounds():
    Backend.stop_all_sounds()

def is_sound_playing(sound):
    return Backend.is_sound_playing(sound)

def play_music(file, volume=1.0, loops=-1):
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.MusicTypes:
        raise UnsupportedFormatError(file, extension)

    Backend.play_music(file, volume, loops)

def pause_music():
    Backend.pause_music()

def resume_music():
    Backend.resume_music()

def set_music_volume(volume):
    Backend.set_music_volume(volume)

def stop_music():
    Backend.stop_music()

def is_music_playing():
    return Backend.is_music_playing()

## GRAPHICS
def set_transparent_color(*color):
    Backend.set_transparent_color(*color)

def load_image(file, use_transparent_color=True):
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.ImageTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_image(file, use_transparent_color)

def load_alpha_image(file):
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.ImageTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_alpha_image(file)

def blitf(thing, x, y):
    Backend.blitf(thing, x, y)

def blit(thing, x, y, alpha=255, flip_v=False, flip_h=False, 
         angle=0, width=None, height=None, scale=1, a_x=0, a_y=0, 
         src_x=0, src_y=0, src_width=None, src_height=None, 
         blend_mode=0, pretty=False):    
    Backend.blit(thing, x, y, alpha, flip_v, flip_h, 
                 angle, width, height, scale, 
                 a_x, a_y, 
                 src_x, src_y, src_width, src_height, 
                 blend_mode, pretty)

## DRAWING
def set_smooth(smooth):
    Backend.set_smooth(smooth)

def get_smooth():
    return Backend.get_smooth()

def set_fill(*color):
    Backend.set_fill(*color)

def get_fill():
    return Backend.get_fill()

def set_stroke(*color):
    Backend.set_stroke(*color)

def get_stroke():
    return Backend.get_stroke()

def set_stroke_weight(weight):
    Backend.set_stroke_weight(weight)

def get_stroke_weight():
    return Backend.get_stroke_weight()

def no_stroke():
    Backend.no_stroke()

def no_fill():
    Backend.no_fill()

def clear(*color):
    Backend.clear(*color)

def draw_line(x1, y1, x2, y2):
    Backend.draw_line(x1, y1, x2, y2)

def draw_rect(x, y, width, height):
    Backend.draw_rect(x, y, width, height)

def draw_ellipse(x, y, width, height, from_center=False):
    Backend.draw_ellipse(x, y, width, height, from_center)

def draw_circle(x, y, radius, from_center=True):
    Backend.draw_circle(x, y, radius, from_center)
    
## TEXT
def set_font_smooth(smooth):
    Backend.set_font_smooth(smooth)

def get_font_smooth():
    return Backend.get_font_smooth()

def load_font(file, size):
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.FontTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.load_font(file, size)

def load_system_font(font_name, size):
    return Backend.load_system_font(font_name, size)

def set_font(font):
    Backend.set_font(font)

def draw_text(text, x, y):
    Backend.draw_text(text, x, y)

def get_text_width(text):
    return Backend.get_text_width(text)

def get_text_height(text):
    return Backend.get_text_height(text)

## SURFACES
def pop():
    Backend.pop()

def push():
    Backend.push()

def make_surface(width, height, *color):
    return Backend.make_surface(width, height, *color)

def get_chunk(x, y, width, height):
    return Backend.get_chunk(x, y, width, height)

def set_buffer(surface):
    Backend.set_buffer(surface)

def reset_buffer():
    Backend.reset_buffer()

def get_width():
    return Backend.get_width()

def get_height():
    return Backend.get_height()

@needs_ability(abilities.save_buffer)
def save_image(file):
    extension = os.path.splitext(file)[1].lower()
    if extension not in Backend.Meta.ImageSaveTypes:
        raise UnsupportedFormatError(file, extension)

    return Backend.save_image(file)

@needs_ability(abilities.numpy)
def to_numpy():
    return Backend.to_numpy()

@needs_ability(abilities.numpy)
def from_numpy(array):
    return Backend.from_numpy(array)

## FAKE INPUT
def add_fake_input(type):
    """ Adds a fake input. There must not be an equivalent real input defined. """

    Backend.add_fake_input(type)

@needs_fake_input(input.keyboard)
def got_key_down(key):
    Backend.got_key_down(key)

@needs_fake_input(input.keyboard)
def got_key_up(key):
    Backend.got_key_up(key)

@needs_fake_input(input.mouse)
def got_mouse_move(x, y):
    Backend.got_mouse_move(x, y)

@needs_fake_input(input.mouse)
def got_mouse_down(button):
    Backend.got_mouse_down(button)

@needs_fake_input(input.mouse)
def got_mouse_up(button):
    Backend.got_mouse_up(button)

## INPUT
def add_input(type):
    """ Initializes support for a specified type of input. """

    if type not in Backend.Meta.InputTypes:
        raise UnsupportedInputError(type)

    Backend.add_input(type)

def supports_input(type):
    """Returns whether the backend supports the specified input
type. Might be integrated into `has` later."""

    return type in Backend.Meta.InputTypes


def remove_input(type):
    """Removes support for a specified type of input. It does not matter
whether this input is real or fake--it will remove it regardless."""

    Backend.remove_input(type)

def has_input(type):
    """Returns whether a specified input type is handled or
not. Intentionally does not distinguish between real and fake
inputs."""

    return Backend.has_input(type)

@needs_input(input.keyboard)
def on_key_down(key):
    return Backend.on_key_down(key)

@needs_input(input.keyboard)
def on_key_up(key):
    return Backend.on_key_up(key)

@needs_input(input.keyboard)
def is_key_pressed(key):
    return Backend.is_key_pressed(key)

@needs_input(input.keyboard)
def get_keys_pressed():
    return Backend.get_keys_pressed()

@needs_input(input.keyboard)
def get_letters_pressed():
    return Backend.get_letters_pressed()

@needs_input(input.mouse)
def show_mouse():
    Backend.show_mouse()

@needs_input(input.mouse)
def hide_mouse():
    Backend.hide_mouse()

@needs_input(input.mouse)
def get_mouse_x():
    return Backend.get_mouse_x()

@needs_input(input.mouse)
def get_mouse_y():
    return Backend.get_mouse_y()

@needs_input(input.mouse)
def on_mouse_down(button=1):
    return Backend.on_mouse_down(button)

@needs_input(input.mouse)
def on_mouse_up(button=1):
    return Backend.on_mouse_up(button)

@needs_input(input.mouse)
def is_mouse_pressed(button=1):
    return Backend.is_mouse_pressed(button)

@needs_input(input.mouse)
def get_mouse_buttons_pressed():
    return Backend.get_mouse_buttons_pressed()

@needs_input(input.joystick)
def on_joy_down(button):
    return Backend.on_joy_down(button)

# todo: implement hat/dpad as button=sgl.joy.down or something?

@needs_input(input.joystick)
def on_joy_up(button):
    return Backend.on_joy_up(button)

@needs_input(input.joystick)
def is_joy_pressed(button):
    return Backend.is_joy_pressed(button)

@needs_input(input.joystick)
def get_joy_buttons_pressed():
    return Backend.get_joy_buttons_pressed()

@needs_input(input.joystick)
def get_joy_axis(axis):
    return Backend.get_joy_axis(axis)

@needs_input(input.joystick)
def get_joy_num_axes():
    return Backend.get_joy_num_axes()

## HELPER
@contextlib.contextmanager
def with_buffer(buffer):
    push()
    set_buffer(buffer)
    yield
    pop()

@contextlib.contextmanager
def with_state():
    push()
    yield
    pop()

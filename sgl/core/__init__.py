import contextlib

class sglException(Exception): pass
class UnsupportedBackendError(sglException): pass

## SYSTEM
backend = None

def init(width, height, scale=1, back_end="pygame"):
    if back_end == "pygame":
        import sgl_pygame
        global backend
        backend = sgl_pygame.Backend()
    else:
        raise UnsupportedBackendError()

    backend.init(width, height, scale)

def frame():
    backend.frame()

def set_fps(fps):
    backend.set_fps(fps)

def use_joystick():
    backend.use_joystick()

def use_mouse():
    backend.use_mouse()

def show_mouse():
    backend.show_mouse()

def hide_mouse():
    backend.hide_mouse()

def set_title(title):
    backend.set_title(title)

def get_actual_screen_width():
    return backend.get_actual_screen_width()

def get_actual_screen_height():
    return backend.get_actual_screen_height()

def get_dt():
    return backend.get_dt()

def is_running():
    return backend.is_running()

def end():
    backend.end()

## AUDIO
def load_sound(file):
    return backend.load_sound(file)

def play_sound(sound, volume=1.0, loops=0):
    backend.play_sound(sound, volume, loops)

def stop_sound(sound):
    backend.stop_sound(sound)

def stop_all_sounds():
    backend.stop_all_sounds()

def is_sound_playing(sound):
    return backend.is_sound_playing(sound)

def play_music(file, volume=1.0, loops=-1):
    backend.play_music(file, volume, loops)

def pause_music():
    backend.pause_music()

def resume_music():
    backend.resume_music()

def set_music_volume(volume):
    backend.set_music_volume(volume)

def stop_music():
    backend.stop_music()

def is_music_playing():
    return backend.is_music_playing()

## GRAPHICS
def set_transparent_color(*color):
    backend.set_transparent_color(*color)

def load_image(file, transparent=True):
    return backend.load_image(file, transparent)

def load_alpha_image(file):
    return backend.load_alpha_image(file)

def blitf(thing, x, y):
    backend.blitf(thing, x, y)

def blit(thing, x, y, alpha=255, flip_v=False, flip_h=False):
    backend.blit(thing, x, y, alpha, flip_v, flip_h)

## DRAWING
def set_fill(*color):
    backend.set_fill(*color)

def set_stroke(*color):
    backend.set_stroke(*color)

def set_stroke_weight(weight):
    backend.set_stroke_weight(weight)

def no_stroke():
    backend.no_stroke()

def no_fill():
    backend.no_fill()

def clear(*color):
    backend.clear(*color)

def draw_line(x1, y1, x2, y2):
    backend.draw_line(x1, y1, x2, y2)

def draw_rect(x, y, width, height):
    backend.draw_rect(x, y, width, height)

def draw_ellipse(x, y, width, height, from_center=False):
    backend.draw_ellipse(x, y, width, height, from_center)

def draw_circle(x, y, radius, from_center=True):
    backend.draw_circle(x, y, radius, from_center)
    
## TEXT
def load_font(font_name, size):
    return backend.load_font(font_name, size)

def set_font(font):
    backend.set_font(font)

def draw_text(text, x, y):
    backend.draw_text(text, x, y)

def get_text_width(text):
    return backend.get_text_width(text)

def get_text_height(text):
    return backend.get_text_height(text)

## SURFACES
def pop():
    backend.pop()

def push():
    backend.push()

def make_surface(width, height, *color):
    return backend.make_surface(width, height, *color)

def get_chunk(x, y, width, height):
    return backend.get_chunk(x, y, width, height)

def set_buffer(surface):
    backend.set_buffer(surface)

def reset_buffer():
    backend.reset_buffer()

def get_buffer_width():
    return backend.get_buffer_width()

def get_buffer_height():
    return backend.get_buffer_height()

## INPUT
def on_key_down(key):
    return backend.on_key_down(key)

def on_key_up(key):
    return backend.on_key_up(key)

def is_key_pressed(key):
    return backend.is_key_pressed(key)

def get_keys_pressed():
    return backend.get_keys_pressed()

def get_mouse_x():
    return backend.get_mouse_x()

def get_mouse_y():
    return backend.get_mouse_y()

def on_mouse_down(button=1):
    return backend.on_mouse_down(button)

def on_mouse_up(button=1):
    return backend.on_mouse_up(button)

def is_mouse_pressed(button=1):
    return backend.is_mouse_pressed(button)

def get_mouse_buttons_pressed():
    return backend.get_mouse_buttons_pressed()

def on_joy_down(button):
    return backend.on_joy_down(button)

# todo: implement hat/dpad as button=sgl.joy.down or something

def on_joy_up(button):
    return backend.on_joy_up(button)

def is_joy_pressed(button):
    return backend.is_joy_pressed(button)

def get_joy_buttons_pressed():
    return backend.get_joy_buttons_pressed()

def get_joy_axis(axis):
    return backend.get_joy_axis(axis)

def get_joy_num_axes():
    return backend.get_joy_num_axes()

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

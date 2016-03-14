import pygame
import os

class BackendError(Exception):
    def __init__(self, message):
        self.message = message

class Backend:
    screen_width = 0
    screen_height = 0
    scale = 0

    window = None               # The raw display surface
    display = None              # The one actually drawn on

    clock = None
    fps = 0
    dt = 0

    running = False

    keys_down = []
    keys_just_down = []
    keys_just_up = []

    mouse_down = []
    mouse_just_down = []
    mouse_just_up = []

    joy_down = []
    joy_just_down = []
    joy_just_up = []

    joystick = None

    class gfx_state:
        transparent_color = (255,0,255)

        fill_color = (255,255,255)
        stroke_color = (100,100,100)
        stroke_weight = 1

        font = None

        buffer = None

    gfx_stack = []

    def resolve_color(self, color):
        if color == None: return None

        if len(color) == 1:
            return (color[0], color[0], color[0])
        elif len(color) == 2:
            return (color[0], color[0], color[0], color[1])
        elif len(color) == 3:
            return (color[0], color[1], color[2])
        elif len(color) == 4:
            return (color[0], color[1], color[2], color[3])

    ## SYSTEM
    def init(self, width, height, scale=1):
        self.screen_width = width
        self.screen_height = height
        self.scale = scale

        # centers window in middle of screen
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        pygame.init()
        self.window = pygame.display.set_mode(
            (self.screen_width * self.scale, 
             self.screen_height * self.scale)
        )
        self.display = pygame.Surface(
            (self.screen_width, self.screen_height)
        )
        self.gfx_state.buffer = self.display

        pygame.mixer.quit()
        pygame.mixer.init(44100)

        self.clock = pygame.time.Clock()

        self.running = True

    def frame(self):
        if self.scale == 1:
            self.window.blit(self.display, (0,0))
        else:
            pygame.transform.scale(
                self.display,        # source
                (self.screen_width * self.scale, 
                 self.screen_height * self.scale),   # size
                self.window          # destination
            )

        pygame.display.flip()

        self.keys_just_down = []
        self.keys_just_up = []

        self.mouse_just_down = []
        self.mouse_just_up = []

        self.joy_just_down = []
        self.joy_just_up = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end()

            if event.type == pygame.KEYDOWN:
                self.keys_just_down.append(event.key)
                self.keys_down.append(event.key)

            if event.type == pygame.KEYUP:
                self.keys_just_up.append(event.key)
                if event.key in self.keys_down:
                    self.keys_down.remove(event.key)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_just_down.append(event.button)
                self.mouse_down.append(event.button)

            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_just_up.append(event.button)
                if event.button in self.mouse_down:
                    self.mouse_down.remove(event.button)

            if event.type == pygame.JOYBUTTONDOWN:
                self.joy_just_down.append(event.button)
                self.joy_down.append(event.button)

            if event.type == pygame.JOYBUTTONUP:
                self.joy_just_up.append(event.button)
                if event.button in self.joy_down:
                    self.joy_down.remove(event.button)

        self.dt = self.clock.tick(self.fps) / 1000.0

    def use_joystick(self):
        self.joystick = pygame.joystick.Joystick(0)

    def use_mouse(self):
        pass

    def show_mouse(self):
        pygame.mouse.set_visible(True)

    def hide_mouse(self):
        pygame.mouse.set_visible(False)

    def set_fps(self, fps):
        self.fps = fps

    def set_title(self, title):
        pygame.display.set_caption(title)

    def get_actual_screen_width(self):
        return self.screen_width * self.scale

    def get_actual_screen_height(self):
        return self.screen_height * self.scale

    def get_dt(self):
        return self.dt

    def is_running(self):
        return self.running

    def end(self):
        self.running = False

    ## AUDIO
    def load_sound(self, file):
        sound = pygame.mixer.Sound(file)
        return sound

    def play_sound(self, sound, volume=1.0, loops=0):
        sound.set_volume(volume)
        sound.play(loops)

    def stop_sound(self, sound):
        sound.stop()

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def is_sound_playing(self, sound):
        return sound.get_num_channels() > 0

    def play_music(self, file, volume=1.0, loops=-1):
        pygame.mixer.music.load(file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.stop()

    def is_music_playing(self):
        pygame.mixer.music.get_busy() # returns true for pausing

    ## GRAPHICS
    def set_transparent_color(self, *color):
        self.gfx_state.transparent_color = resolve_color(color)

    def load_image(self, file, transparent=True):
        image = pygame.image.load(file)
        image = image.convert()
        if transparent: 
            image.set_colorkey(self.gfx_state.transparent_color)
        return image

    def load_alpha_image(self, file):
        image = pygame.image.load(file)
        image = image.convert_alpha()
        return image

    def blitf(self, thing, x, y):
        self.gfx_state.buffer.blit(thing, (x, y))

    def blit(self, thing, x, y, alpha=255, flip_v=False, flip_h=False):
        new_thing = None

        if flip_h or flip_v:
            new_thing = pygame.transform.flip(thing, flip_h, flip_v)

        thing_to_blit = new_thing if new_thing else thing
        
        # AFF setting alpha makes this true. use diff test
        if pygame.SRCALPHA & thing_to_blit.get_flags():
            thing_to_blit.set_alpha(alpha)
            if alpha != 255:
                background = self.get_chunk(
                    x, y, 
                    thing_to_blit.get_width(), 
                    thing_to_blit.get_height()
                ) 
                if pygame.SRCALPHA & background.get_flags():
                    raise BackendError("Pygame can't handle drawing alpha onto alpha")

                self.gfx_state.buffer.blit(thing_to_blit, (x, y))

                background.set_alpha(255 - alpha)
                self.gfx_state.buffer.blit(background, (x, y))
            else:
                self.gfx_state.buffer.blit(thing_to_blit, (x, y))
        else:
            thing_to_blit.set_alpha(alpha)

            self.gfx_state.buffer.blit(thing_to_blit, (x, y))

         # ( angle=0, width=0, height=0, scale=1, 
         #   src_x=0, src_y=0, src_width=0, src_height=0,
         #   a_x=0, a_y=0)

    ## DRAWING
    def set_fill(self, *color):
        self.gfx_state.fill_color = self.resolve_color(color)

    def set_stroke(self, *color):
        self.gfx_state.stroke_color = self.resolve_color(color)

    def set_stroke_weight(self, weight):
        self.gfx_state.stroke_weight = weight

    def no_stroke(self):
        self.gfx_state.stroke_weight = 0

    def no_fill(self):
        self.gfx_state.fill_color = None

    def clear(self, *color):
        self.gfx_state.buffer.fill(self.resolve_color(color))

    def draw_line(self, x1, y1, x2, y2):
        if self.gfx_state.stroke_color != None and self.gfx_state.stroke_weight > 0:
            pygame.draw.line(
                self.gfx_state.buffer, 
                self.gfx_state.stroke_color, 
                (x1, y1), 
                (x2, y2), 
                self.gfx_state.stroke_weight
            )

    def draw_rect(self, x, y, width, height):
        if self.gfx_state.fill_color != None:
            pygame.draw.rect(
                self.gfx_state.buffer, 
                self.gfx_state.fill_color, 
                ((x, y), (width, height)),
                0
            )

        if self.gfx_state.stroke_color != None and self.gfx_state.stroke_weight > 0:
            pygame.draw.rect(
                self.gfx_state.buffer, 
                self.gfx_state.stroke_color, 
                ((x, y), (width, height)),
                self.gfx_state.stroke_weight
            )

    def draw_ellipse(self, x, y, width, height, from_center=False):
        if from_center:
            x -= width / 2
            y -= height / 2

        if self.gfx_state.fill_color != None:
            pygame.draw.ellipse(
                self.gfx_state.buffer, 
                self.gfx_state.fill_color, 
                ((x, y), (width, height)),
                0
            )

        if self.gfx_state.stroke_color != None and self.gfx_state.stroke_weight > 0:
            pygame.draw.ellipse(
                self.gfx_state.buffer, 
                self.gfx_state.stroke_color, 
                ((x, y), (width, height)),
                self.gfx_state.stroke_weight
            )

    def draw_circle(self, x, y, radius, from_center=True):
        self.draw_ellipse(x, y, radius, radius, from_center)

    ## TEXT
    def load_font(self, font_name, size):
        return pygame.font.Font(font_name, size)

    def set_font(self, font):
        self.gfx_state.font = font

    def draw_text(self, text, x, y):
        surface = self.gfx_state.font.render(text, 1, self.gfx_state.fill_color)
        self.blitf(surface, x, y)

    def get_text_width(self, text):
        return self.gfx_state.font.size(text)[0]

    def get_text_height(self, text):
        return self.gfx_state.font.get_linesize()
        # return self.gfx_state.font.get_height()
        # return self.gfx_state.font.size(text)[1]

        # not sure which one is best :|

    ## SURFACES
    def pop(self):
        self.gfx_state.__dict__ = self.gfx_stack.pop()

    def push(self):
        self.gfx_stack.append(self.gfx_state.__dict__.copy())

    def make_surface(self, width, height, *color):
        color = self.resolve_color(color)

        if color == None:
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            return surface
        elif len(color) == 3:
            surface = pygame.Surface((width, height))
        elif len(color) == 4:
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

        surface.fill(color)

        return surface

    def get_chunk(self, x, y, width, height):
        surface = pygame.Surface((width, height))
        surface.blit(self.gfx_state.buffer, (0,0), pygame.Rect(x, y, width, height))
        return surface

    def set_buffer(self, surface):
        self.gfx_state.buffer = surface

    def reset_buffer(self):
        self.gfx_state.buffer = self.display

    def get_buffer_width(self):
        return self.gfx_state.buffer.get_width()

    def get_buffer_height(self):
        return self.gfx_state.buffer.get_height()

    ## INPUT
    def on_key_down(self, key):
        return key in self.keys_just_down

    def on_key_up(self, key):
        return key in self.keys_just_up

    def is_key_pressed(self, key):
        return key in self.keys_down

    def get_keys_pressed(self):
        return self.keys_down

    def get_mouse_x(self):
        return pygame.mouse.get_pos()[0] / self.scale

    def get_mouse_y(self):
        return pygame.mouse.get_pos()[1] / self.scale

    def on_mouse_down(self, button):
        return button in self.mouse_just_down

    def on_mouse_up(self, button):
        return button in self.mouse_just_up

    def is_mouse_pressed(self, button):
        return button in self.mouse_down

    def get_mouse_buttons_pressed(self):
        return self.mouse_down

    def on_joy_down(self, button):
        return button in self.joy_just_down

    # todo: implement hat/dpad as button=sgl.joy.down or something

    def on_joy_up(self, button):
        return button in self.joy_just_up

    def is_joy_pressed(self, button):
        return button in self.joy_down

    def get_joy_buttons_pressed(self):
        return self.joy_down

    def get_joy_axis(self, axis):
        return self.joystick.get_axis(axis)

    def get_joy_num_axes(self):
        return self.joystick.get_numaxes()


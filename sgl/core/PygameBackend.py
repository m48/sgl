import pygame

try:
    import pygame.gfxdraw
    has_gfxdraw = True
except:
    has_gfxdraw = False

try:
    import pygame.freetype
    has_freetype = True
except:
    has_freetype = False

try:
    import numpy as np
    has_numpy = True
except:
    has_numpy = False

import os
from Constants import *
from Errors import *
import Util

class Backend:
    class Meta:
        Abilities = [abilities.software, 
                     abilities.numpy, 
                     abilities.save_buffer]

        InputTypes = [input.keyboard,
                      input.mouse,
                      input.joystick]

        if pygame.image.get_extended():
            ImageTypes = [".jpg", ".jpeg", ".png", ".gif", ".bmp",
                          ".pcx", ".tga", ".tif", ".tiff", ".lbm",
                          ".pbm", ".pgm", ".ppm", ".xpm"]
        else:
            ImageTypes = [".bmp"]

        ImageSaveTypes = [".bmp", ".tga", ".png", ".jpeg"]
        SoundTypes = [".ogg", ".wav"]
        MusicTypes = [".xm", ".it", ".s3m", ".mod", 
                       ".mid", ".midi", ".mp3", 
                       ".ogg", ".wav"]
        FontTypes = [".ttf"]

        class KeyCodes:
            # Standard control keys
            backspace = pygame.K_BACKSPACE
            tab = pygame.K_TAB
            clear = pygame.K_CLEAR
            enter = pygame.K_RETURN
            pause = pygame.K_PAUSE
            escape = pygame.K_ESCAPE

            # Symbols
            space = pygame.K_SPACE
            exclamation_point = pygame.K_EXCLAIM
            quote = pygame.K_QUOTEDBL
            number_sign = pygame.K_HASH
            dollar_sign = pygame.K_DOLLAR
            ampersand = pygame.K_AMPERSAND
            apostrophe = pygame.K_QUOTE
            left_paren = pygame.K_LEFTPAREN
            right_paren = pygame.K_RIGHTPAREN
            asterick = pygame.K_ASTERISK
            plus = pygame.K_PLUS
            comma = pygame.K_COMMA
            minus = pygame.K_MINUS
            period = pygame.K_PERIOD
            slash = pygame.K_SLASH

            # Numbers
            num_0 = pygame.K_0
            num_1 = pygame.K_1
            num_2 = pygame.K_2
            num_3 = pygame.K_3
            num_4 = pygame.K_4
            num_5 = pygame.K_5
            num_6 = pygame.K_6
            num_7 = pygame.K_7
            num_8 = pygame.K_8
            num_9 = pygame.K_9

            # More symbols
            colon = pygame.K_COLON
            semicolon = pygame.K_SEMICOLON
            less_than = pygame.K_LESS
            equal_sign = pygame.K_EQUALS         
            greater_than = pygame.K_GREATER        
            question_mark = pygame.K_QUESTION       
            at_sign = pygame.K_AT             
            left_square = pygame.K_LEFTBRACKET    
            backslash = pygame.K_BACKSLASH      
            right_square = pygame.K_RIGHTBRACKET   
            caret = pygame.K_CARET          
            underscore = pygame.K_UNDERSCORE     
            backtick = pygame.K_BACKQUOTE      

            # Letters
            a = pygame.K_a              
            b = pygame.K_b              
            c = pygame.K_c              
            d = pygame.K_d              
            e = pygame.K_e              
            f = pygame.K_f              
            g = pygame.K_g              
            h = pygame.K_h              
            i = pygame.K_i              
            j = pygame.K_j              
            k = pygame.K_k              
            l = pygame.K_l              
            m = pygame.K_m              
            n = pygame.K_n              
            o = pygame.K_o              
            p = pygame.K_p              
            q = pygame.K_q              
            r = pygame.K_r              
            s = pygame.K_s              
            t = pygame.K_t              
            u = pygame.K_u              
            v = pygame.K_v              
            w = pygame.K_w              
            x = pygame.K_x              
            y = pygame.K_y              
            z = pygame.K_z              

            # The delete key
            delete = pygame.K_DELETE         

            # Numpad
            numpad_0 = pygame.K_KP0            
            numpad_1 = pygame.K_KP1                
            numpad_2 = pygame.K_KP2                
            numpad_3 = pygame.K_KP3                
            numpad_4 = pygame.K_KP4                
            numpad_5 = pygame.K_KP5                
            numpad_6 = pygame.K_KP6                
            numpad_7 = pygame.K_KP7                
            numpad_8 = pygame.K_KP8                
            numpad_9 = pygame.K_KP9         
            numpad_period = pygame.K_KP_PERIOD   
            numpad_divide = pygame.K_KP_DIVIDE   
            numpad_multiply = pygame.K_KP_MULTIPLY 
            numpad_minus = pygame.K_KP_MINUS    
            numpad_plus = pygame.K_KP_PLUS     
            numpad_enter = pygame.K_KP_ENTER    
            numpad_equal_sign = pygame.K_KP_EQUALS   

            # Arrow keys
            up = pygame.K_UP          
            down = pygame.K_DOWN               
            right = pygame.K_RIGHT              
            left = pygame.K_LEFT               

            # Stuff above arrow keys
            insert = pygame.K_INSERT             
            home = pygame.K_HOME               
            end = pygame.K_END                
            page_up = pygame.K_PAGEUP             
            page_down = pygame.K_PAGEDOWN           

            # Function keys
            f1 = pygame.K_F1                 
            f2 = pygame.K_F2                 
            f3 = pygame.K_F3                 
            f4 = pygame.K_F4                 
            f5 = pygame.K_F5                 
            f6 = pygame.K_F6                 
            f7 = pygame.K_F7                 
            f8 = pygame.K_F8                 
            f9 = pygame.K_F9                 
            f10 = pygame.K_F10                
            f11 = pygame.K_F11                
            f12 = pygame.K_F12                
            f13 = pygame.K_F13                
            f14 = pygame.K_F14                
            f15 = pygame.K_F15                

            # The locks
            num_lock = pygame.K_NUMLOCK            
            caps_lock = pygame.K_CAPSLOCK           
            scroll_lock = pygame.K_SCROLLOCK          

            # Normal modifier keys
            right_shift = pygame.K_RSHIFT             
            left_shift = pygame.K_LSHIFT             
            right_control = pygame.K_RCTRL              
            left_control = pygame.K_LCTRL              
            right_alt = pygame.K_RALT               
            left_alt = pygame.K_LALT               

            # Weird modifier keys
            right_meta = pygame.K_RMETA              
            left_meta = pygame.K_LMETA              
            right_super = pygame.K_LSUPER             
            less_super = pygame.K_RSUPER             

            # Please don't ever use these in your game
            mode_shift = pygame.K_MODE               
            help = pygame.K_HELP               
            print_screen = pygame.K_PRINT              
            system_request = pygame.K_SYSREQ             
            system_break = pygame.K_BREAK
            menu = pygame.K_MENU               
            power = pygame.K_POWER              
            euro = pygame.K_EURO               

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

    letters_pressed = ""

    mouse_down = []
    mouse_just_down = []
    mouse_just_up = []

    mouse_x = 0
    mouse_y = 0

    p_mouse_x = 0
    p_mouse_y = 0

    joy_down = []
    joy_just_down = []
    joy_just_up = []

    joy_axes = {}

    joystick = None

    movie_mode = False
    movie_realtime = False

    class gfx_state:
        transparent_color = (255,0,255)

        fill_color = (255,255,255)
        stroke_color = (100,100,100)
        stroke_weight = 1

        smooth = False
        font_smooth = True

        font = None

        buffer = None

        clip_rect = None

    gfx_stack = []

    ## SYSTEM
    def init(self, width, height, scale=1, fullscreen=False):
        self.screen_width = width
        self.screen_height = height
        self.scale = scale

        # centers window in middle of screen
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        if fullscreen:
            flags = pygame.FULLSCREEN
        else:
            flags = 0

        pygame.init()
        self.window = pygame.display.set_mode(
            (self.screen_width * self.scale, 
             self.screen_height * self.scale),
            flags
        )
        self.display = pygame.Surface(
            (self.screen_width, self.screen_height)
        )
        self.gfx_state.buffer = self.display

        pygame.mixer.quit()
        pygame.mixer.init(44100)

        self.clock = pygame.time.Clock()

        self.real_inputs = [input.keyboard, input.mouse]
        self.fake_inputs = []

        self.running = True

    def run(self, update, draw):
        while self.is_running():
            update()
            draw()
            self.frame()        

    def enter_movie_mode(self, realtime):
        self.movie_mode = True
        self.movie_realtime = realtime
 
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

        self.letters_pressed = ""

        self.mouse_just_down = []
        self.mouse_just_up = []

        self.joy_just_down = []
        self.joy_just_up = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end()

            if self.has_real_input(input.keyboard):
                if event.type == pygame.KEYDOWN:
                    self.got_key_down(event.key, event)

                if event.type == pygame.KEYUP:
                    self.got_key_up(event.key)

            if self.has_real_input(input.mouse):
                if event.type == pygame.MOUSEMOTION:
                    self.got_mouse_move(event.pos[0]/self.scale, event.pos[1]/self.scale)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.got_mouse_down(event.button)

                if event.type == pygame.MOUSEBUTTONUP:
                    self.got_mouse_up(event.button)

            if self.has_real_input(input.joystick):
                if event.type == pygame.JOYAXISMOTION:
                    self.got_joy_axis_move(event.axis, event.value)

                if event.type == pygame.JOYHATMOTION:
                    pass
                    # todo: implement hat/dpad as button=sgl.joy.down or something
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    self.got_joy_down(event.button)

                if event.type == pygame.JOYBUTTONUP:
                    self.got_joy_up(event.button)

        if self.movie_mode == True and self.movie_realtime == False: return

        self.dt = self.clock.tick(self.fps) / 1000.0

    def add_input(self, type):
        if type not in self.real_inputs:
            if type == input.joystick:
                pygame.joystick.init()
                if pygame.joystick.get_count() == 0:
                    raise InputHardwareError(type)
                self.joystick = pygame.joystick.Joystick(0)

            elif type in (input.keyboard, input.mouse):
                pass

            self.real_inputs.append(type)

            if type in self.fake_inputs: 
                del self.fake_inputs[self.fake_inputs.index(type)]

        else:
            pass

    def add_fake_input(self, type):
        if type not in self.real_inputs:
            self.fake_inputs.append(type)
        else:
            raise FakeInputError(type)

    def remove_input(self, type):
        if type in self.real_inputs: 
            del self.real_inputs[self.real_inputs.index(type)]
        if type in self.fake_inputs: 
            del self.fake_inputs[self.fake_inputs.index(type)]

    def has_input(self, type):
        return (type in self.real_inputs 
                or type in self.fake_inputs)

    def has_real_input(self, type):
        return (type in self.real_inputs)

    def has_fake_input(self, type):
        return (type in self.fake_inputs)

    def set_fps_limit(self, fps):
        self.fps = fps

    def get_fps_limit(self, fps):
        return self.fps

    def get_fps(self):
        return self.clock.get_fps()

    def get_scale(self):
        return self.scale

    def set_title(self, title):
        pygame.display.set_caption(title)

    def get_title(self):
        return pygame.display.get_caption()[0]

    def get_actual_screen_width(self):
        return self.screen_width * self.scale

    def get_actual_screen_height(self):
        return self.screen_height * self.scale

    def get_dt(self):
        if self.fps == 0:
            return self.dt
        else:
            return 1./self.fps

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
    def set_smooth(self, smooth):
        self.gfx_state.smooth = smooth

    def get_smooth(self):
        return self.gfx_state.smooth

    def set_transparent_color(self, *color):
        self.gfx_state.transparent_color = Util.resolve_color(color)

    def load_image(self, file, use_transparent_color=True):
        image = pygame.image.load(file)
        image = image.convert()
        if use_transparent_color: 
            image.set_colorkey(self.gfx_state.transparent_color)
        return image

    def load_alpha_image(self, file):
        image = pygame.image.load(file)
        image = image.convert_alpha()
        return image

    def blitf(self, thing, x, y):
        self.gfx_state.buffer.blit(thing, (x, y))

    def blit(self, thing, x, y, alpha=255, flip_v=False, flip_h=False, 
             angle=0, width=None, height=None, scale=1, a_x=0, a_y=0, 
             src_x=0, src_y=0, src_width=None, src_height=None, 
             blend_mode=0, pretty=False):

        if src_width or src_height:
            new_surface = pygame.Surface((width, height))
            new_surface.blit(
                thing, (0,0), 
                pygame.Rect(src_x, src_y, src_width, src_height)
            )
            thing = new_surface

        # Store original values
        orig_width = thing.get_width()
        orig_height = thing.get_height()

        if isinstance(a_x, float): a_x = orig_width * a_x
        if isinstance(a_y, float): a_y = orig_height * a_y

        # Handle scaling
        if width or height or scale != 1:
            # If either size is zero, just don't draw it
            if width == 0 or height == 0: return

            # If user leaves out one of the values, it's just the
            # original value
            if not width: width = thing.get_width()
            if not height: height = thing.get_height()

            # Apply scaling for both dimensions
            if scale: 
                width = int(width*scale)
                height = int(height*scale)

            # Make sure the anchor point is still in the right spot
            x_ratio = (width/float(orig_width))
            y_ratio = (height/float(orig_height))
            a_x = int(a_x*x_ratio)
            a_y = int(a_y*y_ratio)

            # Flip graphic with negative values
            if width < 0:
                width = -width
                x -= width
                flip_h = not flip_h
            if height < 0:
                height = -height
                y -= height
                flip_v = not flip_v

            # Actually do scaling
            if pretty:
                thing = pygame.transform.smoothscale(thing, (width, height))
            else:
                thing = pygame.transform.scale(thing, (width, height))

        else:
            x_ratio, y_ratio = 1, 1

        # Handle flipping
        if flip_h or flip_v:
            thing = pygame.transform.flip(thing, flip_h, flip_v)

        # Handle rotating
        if angle != 0:
            # First, make a surface twice as big as the one we want
            # to draw
            w = thing.get_width()
            h = thing.get_height()
            new_surface = self.make_surface(w*2, h*2)
            # (Possibly make it more dynamic than just twice as big?
            # Like, we really don't need to make any additional
            # surface if the anchor point is in the middle. And if the
            # anchor point is really distant from the image, then this
            # isn't big enough.)

            # You can visualize the surface with this code
            # pygame.draw.rect(new_surface, (255,0,0), (0,0,w*2,h*2))

            # Then, draw the original surface at a point that will
            # make the anchor point at the center
            nx = w - a_x
            ny = h - a_y
            new_surface.blit(thing, (nx, ny))

            # You can visualize where the anchor point is with
            # this code
            # a_x += nx
            # a_y += ny
            # pygame.draw.rect(new_surface, (0,255,0), (a_x-2,a_y-2,4,4))

            # Draw this surface instead of the original
            thing = new_surface

            # Actually do rotation
            if pretty:
                scale = 1.0
                thing = pygame.transform.rotozoom(thing, angle, scale)
            else:
                thing = pygame.transform.rotate(thing, angle)
            # (Possibly use rotozoom to scale when you have pretty on
            # and the aspect ratio is kept?)

            # Then draw the expanded surface at the center
            x -= thing.get_width()/2
            y -= thing.get_height()/2

        # If we're not rotating, apply anchor point in normal way
        else:
            x -= a_x
            y -= a_y

        thing_to_blit = thing # new_thing if new_thing else thing

        if blend_mode == blend.add: 
            flag = pygame.BLEND_ADD
        elif blend_mode == blend.multiply: 
            flag = pygame.BLEND_MULT
        elif blend_mode == blend.subtract: 
            flag = pygame.BLEND_SUB
        else:
            flag = 0

        # Handle alpha
        # ARGH, setting alpha makes this true. Find different test
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

                self.gfx_state.buffer.blit(thing_to_blit, (x, y), special_flags=flag)

                background.set_alpha(255 - alpha)
                self.gfx_state.buffer.blit(background, (x, y))
            else:
                self.gfx_state.buffer.blit(thing_to_blit, (x, y), special_flags=flag)
        else:
            thing_to_blit.set_alpha(alpha)

            self.gfx_state.buffer.blit(thing_to_blit, (x, y), special_flags=flag)
         
    ## DRAWING
    def set_fill(self, *color):
        self.gfx_state.fill_color = Util.resolve_color(color)

    def get_fill(self):
        return self.gfx_state.fill_color

    def set_stroke(self, *color):
        self.gfx_state.stroke_color = Util.resolve_color(color)

    def get_stroke(self):
        return self.gfx_state.stroke_color

    def set_stroke_weight(self, weight):
        self.gfx_state.stroke_weight = weight

    def get_stroke_weight(self):
        return self.gfx_state.stroke_weight

    def no_stroke(self):
        self.gfx_state.stroke_weight = 0
        self.gfx_state.stroke_color = None

    def no_fill(self):
        self.gfx_state.fill_color = None

    def clear(self, *color):
        self.gfx_state.buffer.fill(Util.resolve_color(color))

    def draw_line(self, x1, y1, x2, y2):
        if self.gfx_state.stroke_color != None and self.gfx_state.stroke_weight > 0:
            # By default Pygame can't draw transparent shapes
            # correctly, so we have to help it out :|
            if Util.is_color_alpha(self.gfx_state.stroke_color):

                # Separate out color and alpha (for convenience)
                color = self.gfx_state.stroke_color[0:3]
                alpha = self.gfx_state.stroke_color[3]

                # Store where we need to draw the surface
                x, y = x1, y1

                # Shifts the line coordinates so they start at zero
                x2, y2, x1, y1 = x2-x1, y2-y1, 0, 0

                # If line goes backwards in x direction
                if x2 < 0: 
                    x = x2          # Shift drawing offset
                    x2 = -x2        # Make coordinates positive
                    x2, x1 = x1, x2 # Flip points

                # If line goes backwards in y direction
                if y2 < 0: 
                    y = y2
                    y2 = -y2
                    y2, y1 = y1, y2

                # Make temporary surface to draw line on
                destination = self.make_surface(x2, y2)

                # Draw line on that surface as not transparent
                pygame.draw.line(
                    destination, 
                    color, 
                    (x1, y1), 
                    (x2, y2), 
                    self.gfx_state.stroke_weight
                )
    
                # Draw that surface on the screen with transparency
                self.blit(destination, x, y, alpha=alpha)
            else:
                pygame.draw.line(
                    self.gfx_state.buffer, 
                    self.gfx_state.stroke_color, 
                    (x1, y1), 
                    (x2, y2), 
                    self.gfx_state.stroke_weight
                )

    def draw_rect(self, x, y, width, height):
        if width < 0: width = -width; x -= width
        if height < 0: height = -height; y -= height

        if self.gfx_state.fill_color != None:

            if Util.is_color_alpha(self.gfx_state.fill_color):

                surface = self.make_surface(width, height, 
                    self.gfx_state.fill_color)
                self.blitf(surface, x, y)

            else:
                # pygame.draw.rect(
                #     self.gfx_state.buffer, 
                #     self.gfx_state.fill_color, 
                #     ((x, y), (width, height)),
                #     0
                # )

                # Apparently this is more optimized
                self.gfx_state.buffer.fill(
                    self.gfx_state.fill_color,
                    ((x, y), (width, height))
                )

        if self.gfx_state.stroke_color != None and self.gfx_state.stroke_weight > 0:
            if Util.is_color_alpha(self.gfx_state.stroke_color):
    
                # Expand the temporary surface to fit thicker lines
                weight = self.gfx_state.stroke_weight
                x -= weight
                y -= weight
                surface = self.make_surface(
                    width+weight*2, height+weight*2)

                pygame.draw.rect(
                    surface, 
                    self.gfx_state.stroke_color[0:3], 
                    ((weight, weight), (width, height)),
                    self.gfx_state.stroke_weight
                )
    
                self.blit(surface, x, y, 
                          alpha=self.gfx_state.stroke_color[3])
    
            else:
                pygame.draw.rect(
                    self.gfx_state.buffer, 
                    self.gfx_state.stroke_color, 
                    ((x, y), (width, height)),
                    self.gfx_state.stroke_weight
                )

    def draw_ellipse(self, x, y, width, height, from_center=False):
        if from_center:
            if width < 0: width = -width
            if height < 0: height = -height

            x -= width / 2
            y -= height / 2

        else:
            if width < 0: width = -width; x -= width
            if height < 0: height = -height; y -= height
    
        if self.gfx_state.fill_color != None:

            if Util.is_color_alpha(self.gfx_state.fill_color):
                surface = self.make_surface(width, height)

                pygame.draw.ellipse(
                    surface, 
                    self.gfx_state.fill_color[0:3], 
                    ((0, 0), (width, height)),
                    0
                )

                self.blit(surface, x, y, alpha=self.gfx_state.fill_color[3])

            else:
                pygame.draw.ellipse(
                    self.gfx_state.buffer, 
                    self.gfx_state.fill_color, 
                    ((x, y), (width, height)),
                    0
                )

        if self.gfx_state.stroke_color != None and self.gfx_state.stroke_weight > 0:

            if Util.is_color_alpha(self.gfx_state.stroke_color):
    
                # Expand the temporary surface to fit thicker lines
                weight = self.gfx_state.stroke_weight
                x -= weight
                y -= weight
                surface = self.make_surface(
                    width+weight*2, height+weight*2)

                pygame.draw.ellipse(
                    surface, 
                    self.gfx_state.stroke_color[0:3], 
                    ((weight, weight), (width, height)),
                    self.gfx_state.stroke_weight
                )
    
                self.blit(surface, x, y, 
                          alpha=self.gfx_state.stroke_color[3])

            else:
                pygame.draw.ellipse(
                    self.gfx_state.buffer, 
                    self.gfx_state.stroke_color, 
                    ((x, y), (width, height)),
                    self.gfx_state.stroke_weight
                )

    def draw_circle(self, x, y, radius, from_center=True):
        self.draw_ellipse(x, y, radius, radius, from_center)

    ## TEXT
    def set_font_smooth(self, smooth):
        self.gfx_state.font_smooth = smooth

    def get_font_smooth(self):
        return self.gfx_state.font_smooth

    def load_font(self, font_name, size):
        return pygame.font.Font(font_name, size)

    def load_system_font(self, font_name, size):
        return pygame.font.SysFont(font_name, size)

    def set_font(self, font):
        self.gfx_state.font = font

    def draw_text(self, text, x, y):
        surface = self.gfx_state.font.render(
            text, 
            self.gfx_state.font_smooth, 
            self.gfx_state.fill_color
        )
        self.blitf(surface, x, y)

    def get_text_width(self, text):
        return self.gfx_state.font.size(text)[0]

    def get_text_height(self, text):
        return self.gfx_state.font.get_ascent()
        # return self.gfx_state.font.get_linesize()
        # return self.gfx_state.font.get_height()
        # return self.gfx_state.font.size(text)[1]

        # not sure which one is best :|

    ## SURFACES
    def pop(self):
        self.gfx_state.__dict__ = self.gfx_stack.pop()
        self.gfx_state.buffer.set_clip(self.gfx_state.clip_rect)

    def push(self):
        self.gfx_stack.append(self.gfx_state.__dict__.copy())

    def make_surface(self, width, height, *color):
        color = Util.resolve_color(color)

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
        surface = pygame.Surface((width, height), self.gfx_state.buffer.get_flags())

        transparent_color = self.gfx_state.buffer.get_colorkey()
        if transparent_color:
            surface.set_colorkey(transparent_color)
            self.gfx_state.buffer.set_colorkey(None)
            
        surface.blit(self.gfx_state.buffer, (0,0), pygame.Rect(x, y, width, height))

        if transparent_color:
            self.gfx_state.buffer.set_colorkey(transparent_color)

        return surface

    def set_buffer(self, surface):
        self.gfx_state.buffer = surface

    def reset_buffer(self):
        self.gfx_state.buffer = self.display

    def get_width(self):
        return self.gfx_state.buffer.get_width()

    def get_height(self):
        return self.gfx_state.buffer.get_height()

    def set_clip_rect(self, *args):
        self.gfx_state.clip_rect = args
        self.gfx_state.buffer.set_clip(*args)

    def get_clip_rect(self, *args):
        return self.gfx_state.clip_rect

    def no_clip_rect(self):
        self.gfx_state.clip_rect = None
        self.gfx_state.buffer.set_clip(None)

    def invert(self, surface):
        if not has_numpy:
            raise BackendError("NumPy is required for this effect")

        if surface == None: 
            surface = self.gfx_state.buffer
            modify = True
        else:
            surface = surface.copy()
            modify = False

        # Taken from:
        # http://stackoverflow.com/questions/5891808/how-to-invert-colors-of-an-image-in-pygame
        pixels = pygame.surfarray.pixels2d(surface)
        pixels ^= 2 ** 32 - 1
        del pixels

        if modify:
            return
        else:
            return surface

    def grayscale(self, surface):
        if not has_numpy:
            raise BackendError("NumPy is required for this effect")

        if surface == None: 
            surface = self.gfx_state.buffer
            modify = True
        else:
            surface = surface.copy()
            modify = False

        # Taken from:
        # http://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
        pixels = pygame.surfarray.pixels3d(surface)
        new = np.dot(pixels[...,:3], [0.299, 0.587, 0.114])
        new = np.expand_dims(new, 2)
        pixels[:] = new
        del pixels

        if modify:
            return
        else:
            return surface

    def save_image(self, file):
        pygame.image.save(self.gfx_state.buffer, file)

    def to_numpy(self):
        return pygame.surfarray.pixels3d(self.gfx_state.buffer)

    def from_numpy(self, array):
        return pygame.surfarray.make_surface(array)

    ## INPUT
    def got_key_down(self, key, raw_event=None):
        if key >= 32 and key <= 255:
            if raw_event:
                self.letters_pressed += raw_event.unicode
            else:
                # does not work for 3 -> # and stuff. Maybe make a
                # generic way to fix that
                if (self.is_key_pressed(301) 
                    or self.is_key_pressed(303) 
                    or self.is_key_pressed(304)): 
                    self.letters_pressed += chr(key).upper()
                else:
                    self.letters_pressed += chr(key)
                
        self.keys_just_down.append(key)
        self.keys_down.append(key)

    def got_key_up(self, key):
        self.keys_just_up.append(key)
        if key in self.keys_down:
            self.keys_down.remove(key)

    def got_mouse_move(self, x, y):
        self.p_mouse_x = self.mouse_x
        self.p_mouse_y = self.mouse_y
        self.mouse_x = x
        self.mouse_y = y

    def got_mouse_down(self, button):
        self.mouse_just_down.append(button)
        self.mouse_down.append(button)

    def got_mouse_up(self, button):
        self.mouse_just_up.append(button)
        if button in self.mouse_down:
            self.mouse_down.remove(button)

    def got_joy_axis_move(axis, value):
        self.joy_axes[axis] = value

    def got_joy_down(self, button):
        self.joy_just_down.append(button)
        self.joy_down.append(button)

    def got_joy_up(self, button):
        self.joy_just_up.append(event.button)
        if event.button in self.joy_down:
            self.joy_down.remove(event.button)

    def on_key_down(self, key):
        return key in self.keys_just_down

    def on_key_up(self, key):
        return key in self.keys_just_up
        
    def is_key_pressed(self, key):
        return key in self.keys_down

    def get_keys_pressed(self):
        return self.keys_down

    def get_letters_pressed(self):
        return self.letters_pressed

    def show_mouse(self):
        pygame.mouse.set_visible(True)

    def hide_mouse(self):
        pygame.mouse.set_visible(False)

    def get_prev_mouse_x(self):
        return self.p_mouse_x

    def get_prev_mouse_y(self):
        return self.p_mouse_y

    def get_mouse_x(self):
        return self.mouse_x

    def get_mouse_y(self):
        return self.mouse_y

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

    def on_joy_up(self, button):
        return button in self.joy_just_up

    def is_joy_pressed(self, button):
        return button in self.joy_down

    def get_joy_buttons_pressed(self):
        return self.joy_down

    def get_joy_axis(self, axis):
        return self.joy_axes.get(axis, 0)

    def get_joy_num_axes(self):
        return self.joystick.get_numaxes()


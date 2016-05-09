import sgl
from sgl.lib.Rect import Rect

# Todo:
# * Some type of event propagation (so you can stop mouse clicking from happening to overlapped things)
# * Effects

class Sprite(object):
    def __init__(self, graphic=None):
        # Initialize properties
        # Whether SpriteGroups will call "draw" on this object
        self.visible = True

        # Whether SpriteGroups will call "update" on this object    
        self.active = True
    
        # Whether SpriteGroups will automatically delete this object
        # on the next frame
        self.to_be_deleted = False
   
        # Store world coordinates
        self.x, self.y = 0, 0      

        # Store previous world coordinates
        self.prev_x, self.prev_y = 0, 0

        # Store anchor point
        self.a_x, self.a_y = 0,0

        # Store screen coordinates
        # (you shouldn't change these manually)
        self.screen_x, self.screen_y = 0,0

        # Size
        self.width, self.height = 0,0

        # List of sprites inside this one
        self.subsprites = []

        # A rectangle, in screen coordinates, outside of which no
        # subsprites will be drawn.
        self.view_rect = None

        # Store this object's "parent". This will be the containing
        # SpriteGroup or Scene or something. This is used to calculate
        # the screen coordinates, and to help to reverse your scene.
        self.parent = None

        # A link to the scene in particular, for convenience
        self.scene = None

        # What to divide position by for parallax effects
        self.parallax = 1

        # If this is true, object will be in a fixed position, and
        # not be affected by camera movement and stuff
        self.fixed = False

        # This is the bounding box. Don't change it manually.
        self._rect = Rect()

        # 
        self.solid = True

        # 
        self._collision_rect = None

        # Loads the graphic
        if graphic: 
            self.load_surface(graphic)
        else:
            self.surface = None

    def add(self, sprite):
        sprite.parent = self
        self.subsprites.append(sprite)
        sprite.on_add()

        return sprite

    def on_add(self):
        pass

    # User facing access
    @property
    def rect(self):
        real_anchor = self.real_anchor

        self._rect.x = self.x - real_anchor[0]
        self._rect.y = self.y - real_anchor[1]
        self._rect.width = self.width
        self._rect.height = self.height
        return self._rect

    @property
    def screen_rect(self):
        real_anchor = self.real_anchor

        self._rect.x = self.screen_x - real_anchor[0]
        self._rect.y = self.screen_y - real_anchor[1]
        self._rect.width = self.width
        self._rect.height = self.height
        return self._rect

    @property
    def collision_rect(self):
        if self._collision_rect:
            return self._collision_rect
        else:
            return Rect(0, 0, self.width, self.height)

    @collision_rect.setter
    def collision_rect(self, value):
        if isinstance(value, Rect):
            self._collision_rect = value
        else:
            self._collision_rect = Rect(*value)

    @property
    def world_collision_rect(self):
        real_anchor = self.real_anchor
        rect = Rect()

        rect.x = self.x + self.collision_rect.x - real_anchor[0]
        rect.y = self.y + self.collision_rect.y - real_anchor[1]
        rect.width = self.collision_rect.width
        rect.height = self.collision_rect.height
        
        return rect

    @property
    def screen_collision_rect(self):
        real_anchor = self.real_anchor
        rect = Rect()

        rect.x = self.screen_x + self.collision_rect.x - real_anchor[0]
        rect.y = self.screen_y + self.collision_rect.y - real_anchor[1]
        rect.width = self.collision_rect.width
        rect.height = self.collision_rect.height
        
        return rect

    def is_colliding_with(self, other):
        if not self.solid or not other.solid:
            return False

        return other.is_being_collided(self)

    def is_being_collided(self, other):
        return self.world_collision_rect.is_in(
            other.world_collision_rect
        )

    # Internally, positions are stored as x and y values, but you can
    # deal with them as tuples if you want
    @property
    def screen_position(self):
        return (self.screen_x, self.screen_y)

    @property
    def position(self):
        return (self.x, self.y)
    
    @position.setter
    def position(self, new_value):
        self.x, self.y = new_value

    @property
    def prev_position(self):
        return (self.screen_x, self.screen_y)

    # Converts the anchor point to real coordinates from the
    # scaling type
    @property
    def real_anchor(self):
        a_x, a_y = self.a_x, self.a_y
        if isinstance(a_x, float): a_x = self.width * a_x
        if isinstance(a_y, float): a_y = self.height * a_y

        return (a_x, a_y)

    @property
    def anchor(self):
        return (self.a_x, self.a_y)
    
    @position.setter
    def anchor(self, new_value):
        self.a_x, self.a_y = new_value

    @property
    def size(self):
        return (self.width, self.height)
    
    @size.setter
    def size(self, new_value):
        self.width, self.height = new_value

    def is_mouse_over(self):
        return self.screen_rect.is_in(
            sgl.get_mouse_x(), sgl.get_mouse_y()
        )

    def world_to_screen(self, x, y):
        screen_x = self.x
        screen_y = self.y

        if self.parent and not self.fixed:

            if hasattr(self.parent, "camera"):
                screen_x, screen_y = (
                    self.parent.camera.world_to_screen(
                        self.x, self.y, self.parallax)
                )

            screen_x += self.parent.screen_x
            screen_y += self.parent.screen_y

        return screen_x, screen_y

    def update_screen_positions(self):
        self.screen_x, self.screen_y = self.world_to_screen(*self.position)
        for sprite in self.subsprites:
            sprite.update_screen_positions()

    def preupdate(self):
        self.prev_x, self.prev_y = self.position

        # Because we might need to know in update()
        self.screen_x, self.screen_y = self.world_to_screen(*self.position)

    def update(self):
        for index, sprite in enumerate(self.subsprites):
            sprite.preupdate()

            if sprite.active: 
                sprite.update()

            if sprite.to_be_deleted:
                del self.subsprites[index]

    def draw(self):
        if not self.visible: return

        # Because update might have changed things, and we want to
        # draw it in the right place
        # self.screen_x, self.screen_y = self.world_to_screen(*self.position)

        self.draw_self()
        self.draw_children()

    def draw_self(self):
        if self.surface:
            a_x, a_y = self.real_anchor
            sgl.blitf(
                self.surface, 
                self.screen_x - a_x, self.screen_y - a_y
            )

            # sgl.blit(
            #     self.surface, 
            #     self.screen_x, self.screen_y, 
            #     a_x=self.a_x, a_y=self.a_y
            # )

    def draw_children(self):
        if self.subsprites == []: return
        # Most accurate way, but slower
        # Use this if things get stupid again
        # self.update_screen_positions()

        for sprite in self.subsprites:
            sprite.screen_x, sprite.screen_y = sprite.world_to_screen(*sprite.position)

            if self.view_rect:
                if (sprite.screen_rect.is_in(self.view_rect)):
                    sprite.draw()
            else:
                sprite.draw()

    # Load surface and sets size accordingly.
    def load_surface(self, surface):
        self.surface = surface
        self.autosize()

    def autosize(self):
        if self.surface:
            with sgl.with_buffer(self.surface):
                self.width = sgl.get_width()
                self.height = sgl.get_height()
        else:
            self.width, self.height = 0,0         

    def fill(self):
        self.anchor = 0, 0
        self.position = 0, 0
        if self.parent:
            self.size = self.parent.size
        else:
            self.size = sgl.get_width(), sgl.get_height()

    def center(self):
        self.anchor = 0.5, 0.5
        
        if self.parent:
            self.position = self.parent.width/2, self.parent.height/2
        else:
            self.position = sgl.get_width()/2, sgl.get_height()/2

    def centre(self):
        # In honor of wxWidgets
        self.center()

    def kill(self):
        self.to_be_deleted = True

class AnimatedSprite(Sprite):
    frames = []
    animations = {}

    def __init__(self):
        super(AnimatedSprite, self).__init__()

        self.anim_time = 0
        self.anim_next_frame_time = 0
        self.anim_index = 0
        self.anim_name = ""

        self.anim_def_frame_length = 1.0/15.0
        self.anim_frame_length = 0

        self.anim_playing = False

    @property
    def anim_current_frame(self):
        return self.animations[self.animation][self.anim_index]

    @property
    def anim_length(self):
        return len(self.animations[self.animation])

    @property
    def animation(self):
        return self.anim_name

    @animation.setter
    def animation(self, value):
        self.anim_reset()
        self.anim_name = value

    @property
    def playing(self):
        return self.anim_playing

    def anim_reset(self):
        self.anim_time = 0
        self.anim_next_frame_time = 0
        self.anim_index = 0

    def play(self):
        self.anim_playing = True
        self.anim_update_frame()

    def pause(self):
        self.anim_playing = False

    def stop(self):
        self.anim_reset()
        self.anim_playing = False

    def anim_update_frame(self):
        self.anim_time = 0

        frame = self.anim_current_frame
        complex_frame = isinstance(frame, dict)
        length = self.anim_frame_length or self.anim_def_frame_length

        if complex_frame:
            if "frame" not in frame:
                self.anim_frame_length = frame["default_length"]
                self.anim_index += 1
                self.anim_update_frame()
                return

            self.surface = self.frames[frame["frame"]]
            self.anim_next_frame_time = frame.get("length", length)

        else:
            self.surface = self.frames[frame]
            self.anim_next_frame_time = length
       
    def preupdate(self):
        super(AnimatedSprite, self).preupdate()

        if not self.anim_playing: return
        
        self.anim_time += sgl.get_dt()

        if self.anim_time >= self.anim_next_frame_time:
            self.anim_index += 1
            if self.anim_index >= self.anim_length:
                self.anim_index = 0
                # loop restricting/callback logic here?

            self.anim_update_frame()
        # maybe awkward that this does not attempt to make up for
        # lost time like sgl.lib.Time does?

class ShapeSprite(Sprite):
    def __init__(self):
        super(ShapeSprite, self).__init__()
        
        self.no_stroke = False
        self.stroke_color = 1.0
        self.stroke_weight = 1

        self.no_fill = False
        self.fill_color = 0.75

    def draw_shape(self):
        pass

    def draw_self(self):
        with sgl.with_state():
            if self.no_stroke:
                sgl.no_stroke()
            else:
                sgl.set_stroke(self.stroke_color)
                sgl.set_stroke_weight(self.stroke_weight)

            if self.no_fill:
                sgl.no_fill()
            else:
                sgl.set_fill(self.fill_color)

            self.draw_shape()

class RectSprite(ShapeSprite):
    def draw_shape(self):
        sgl.draw_rect(*self.screen_rect.to_tuple())

class EllipseSprite(ShapeSprite):
    def draw_shape(self):
        sgl.draw_ellipse(*self.screen_rect.to_tuple())
                
# Special object to store camera stuff
class Camera(object):
    def __init__(self):
        self.x, self.y = 0,0

    @property
    def position(self):
        return (self.x, self.y)
    
    @position.setter
    def position(self, new_value):
        self.x, self.y = new_value

    def world_to_screen(self, x, y, parallax=1):
        if parallax == 1:
            return (x + self.x, y + self.y) 
        else:
            return (x + self.x/parallax, y + self.y/parallax)             

    def screen_to_world(self, x, y, parallax=1):
        return (x - self.x*parallax, y - self.y*parallax) 

# Specialized types of groups
class Scene(Sprite):
    def __init__(self):
        super(Scene, self).__init__()

        self.view_rect = Rect(
            0, 0, 
            sgl.get_width(), sgl.get_height()
        )

        self.background_color = 0

        self.size = sgl.get_width(), sgl.get_height()

        self.camera = Camera()

    def add(self, sprite):
        sprite.scene = self
        return super(Scene, self).add(sprite)

    def draw(self):
        sgl.clear(self.background_color)

        super(Scene, self).draw()

class Viewport(Sprite):
    def __init__(self):
        super(Viewport, self).__init__()

        self.camera = Camera()

    def draw(self):
        if not self.visible: return

        with sgl.with_state():
            self.view_rect = self.screen_rect
            sgl.set_clip_rect(*self.screen_rect.to_tuple())
            self.draw_children()

        self.draw_self()

if __name__ == "__main__":
    # sgl.init(320, 240, 2)
    sgl.init(640, 480, 1)
    # sgl.init(1280, 720, 1)

    def make_field(scale, parallax):
        field = RectSprite()

        field.no_fill = True
        field.stroke_weight = 3
        field.stroke_color = (1/parallax, 0, 0)

        field.size = (sgl.get_width() * scale, 
                      sgl.get_height() * scale)
        field.center()

        field.parallax = parallax

        return field

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            self.background_color = 0.5

            blackness = RectSprite()

            blackness.no_stroke = True
            blackness.fill_color = 0

            blackness.parallax = 3

            blackness.fill()

            self.add(blackness)

            self.add(AnimatedCircleThingy())

            self.add(make_field(0.75, 1.5))
            self.add(make_field(0.85, 1.25))
            self.add(make_field(1.0, 1.0))

            self.add(CircleThingy(0.25, 0.75))
            self.add(CircleThingy(0.00, 0.50))
            self.add(CircleThingy(0.75, 0.25))

        def update(self):
            super(TestScene, self).update()

            v = 200

            if sgl.is_key_pressed(sgl.key.down): 
                self.camera.y -= v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.up): 
                self.camera.y += v * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.right): 
                self.camera.x -= v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.left): 
                self.camera.x += v * sgl.get_dt()

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    def make_circle(radius, *color):
        surface = sgl.make_surface(radius, radius)
        with sgl.with_buffer(surface):
            sgl.no_stroke()
            sgl.set_fill(*color)
            sgl.draw_circle(0, 0, radius, False)

        return surface

    class AnimatedCircleThingy(AnimatedSprite):
        frames = [
            make_circle(256, 0.25),
            make_circle(256, 0.40),
            make_circle(256, 0.50),
            make_circle(256, 0.65),
            make_circle(256, 0.80),
        ]

        animations = {
            "pulse": [
                {"default_length": 0.25/2},
                {"frame": 0, "length": 1},
                1,2,3,
                {"frame": 4, "length": 1},
                3,2,1,
            ],
            "crazy": range(4),
        }

        def __init__(self):
            super(AnimatedCircleThingy, self).__init__()

            self.animation = "pulse"
            self.play()

            self.center()
            self.autosize()

            self.parallax = 2

            self.highlight = False

        def update(self):
            if self.is_mouse_over(): 
                if sgl.on_mouse_down():
                    self.highlight = True
                if sgl.on_mouse_up():
                    self.highlight = False
                    if self.playing: self.pause()
                    else: self.play()

            if sgl.on_key_up(sgl.key.space):
                self.animation = ("crazy" 
                                  if self.animation == "pulse" 
                                  else "pulse")

        def draw(self):
            super(AnimatedCircleThingy, self).draw()
            if self.highlight: 
                with sgl.with_state():
                    sgl.no_fill()
                    if not self.playing: sgl.set_stroke(0, 1.0, 0)
                    else: sgl.set_stroke(1.0, 0, 0)
                    sgl.draw_rect(*self.screen_rect.to_tuple())

            

    class CircleThingy(Sprite):
        # These are all like static variables, since they are defined
        # up here

        # So there's only one set of graphics for all circle
        # thingies ever

        radius = sgl.get_width()/10
        normal_circle = make_circle(radius, 1.0)
        red_circle = make_circle(radius, 1.0, 0, 0)

        def __init__(self, x=0, y=0.5):
            super(CircleThingy, self).__init__()

            self.load_surface(self.normal_circle)

            self.position = sgl.get_width()*x, sgl.get_height()*y
            self.anchor = 0, 0.5

            self.vel = 150

        def update(self):
            self.x += self.vel * sgl.get_dt()

            if self.x > sgl.get_width() - self.width: 
                self.vel = -self.vel
                self.x = sgl.get_width() - self.width
            if self.x < 0: 
                self.vel = -self.vel
                self.x = 0

            # Make circle red when mouse is inside of it
            if self.is_mouse_over():
                self.surface = self.red_circle
            else:
                self.surface = self.normal_circle

    scene = TestScene()

    sgl.run(scene.update, scene.draw)


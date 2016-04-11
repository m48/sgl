import sgl
from sgl.lib.Rect import Rect

class Sprite(object):
    def __init__(self, graphic=None):
        # Loads the graphic
        self.load_surface(graphic)

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

        # Store anchor point
        self.a_x, self.a_y = 0,0

        # Store screen coordinates
        # (you shouldn't change these manually)
        self.screen_x, self.screen_y = 0,0

        # Store this object's "parent". This will be the containing
        # SpriteGroup or Scene or something. This is used to calculate
        # the screen coordinates, and to help to reverse your scene.
        self.parent = None

        # A link to the scene in particular, for convenience
        self.scene = None

        # If this is true, object will be in a fixed position, and
        # not be affected by camera movement and stuff
        self.fixed = False

        # This is the bounding box. Don't change it manually.
        self._rect = Rect()

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
    
    @position.setter
    def size(self, new_value):
        self.width, self.height = new_value

    def world_to_screen(self, x, y):
        if self.parent and not self.fixed:

            if hasattr(self.parent, "camera"):
                screen_x, screen_y = (
                    self.parent.camera.world_to_screen(
                        *self.position)
                )

            else:
                screen_x = self.parent.screen_x + self.x
                screen_y = self.parent.screen_y + self.y

        else:
            screen_x = self.x
            screen_y = self.y

        return screen_x, screen_y

    def preupdate(self):
        self.screen_x, self.screen_y = self.world_to_screen(*self.position)

    def update(self):
        pass

    # I don't think this is useful for anything
    def postupdate(self):
        pass

    # Add effects eventually
    def draw(self):
        sgl.blit(
            self.surface, 
            self.screen_x, self.screen_y, 
            a_x=self.a_x, a_y=self.a_y
        )

    # Load surface and sets size accordingly.
    def load_surface(self, surface):
        self.surface = surface
        if self.surface:
            with sgl.with_buffer(self.surface):
                self.width = sgl.get_width()
                self.height = sgl.get_height()
        else:
            self.width, self.height = 0,0         

    def kill(self):
        self.to_be_deleted = True

# Base class for any group of sprites
class SpriteGroup(Sprite):
    def __init__(self):
        super(SpriteGroup, self).__init__()

        self.sprites = []
        self.view_rect = Rect(
            0, 0, 
            sgl.get_width(), sgl.get_height()
        )

    def add(self, sprite):
        sprite.parent = self
        self.sprites.append(sprite)

    def update(self):
        for index, sprite in enumerate(self.sprites):
            if sprite.active: 
                sprite.preupdate()
                sprite.update()
                sprite.postupdate()

            if sprite.to_be_deleted:
                self.sprites[index] = None

    def draw(self):
        for index, sprite in enumerate(self.sprites):
            if (sprite.visible 
                and sprite.screen_rect.is_in(self.view_rect)):
                sprite.draw()

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

    def world_to_screen(self, x, y):
        return (x + self.x, y + self.y) 

    def screen_to_world(self, x, y):
        return (x - self.x, y - self.y) 

# Specialized types of groups
class Scene(SpriteGroup):
    def __init__(self):
        super(Scene, self).__init__()

        self.camera = Camera()

    def add(self, sprite):
        sprite.scene = self
        super(Scene, self).add(sprite)

class CompositeSprite(SpriteGroup):
    def __init__(self, graphic=None):
        super(Scene, self).__init__(graphic)

if __name__ == "__main__":
    sgl.init(640, 480, 1)

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            self.add(Sprite(sgl.make_surface(640, 480, 0)))
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

            sgl.set_title("FPS: " + str(sgl.get_fps()))

        def draw(self):
            # Make it so there's no weird trailing when the camera
            # goes off the field
            sgl.clear(0.5)

            super(TestScene, self).draw()

    class CircleThingy(Sprite):
        # These are all like static variables, since they are defined
        # up here

        # So there's only one set of graphics for all circle
        # thingies ever

        def make_circle(radius, *color):
            surface = sgl.make_surface(radius, radius)
            with sgl.with_buffer(surface):
                sgl.no_stroke()
                sgl.set_fill(*color)
                sgl.draw_circle(0, 0, radius, False)
    
            return surface

        normal_circle = make_circle(64, 1.0)
        red_circle = make_circle(64, 1.0, 0, 0)

        def __init__(self, x=0, y=0.5):
            super(CircleThingy, self).__init__()

            self.load_surface(self.normal_circle)

            self.position = int(sgl.get_width()*x), int(sgl.get_height()*y)
            self.anchor = 0, 0.5

            self.vel = 150

        def update(self):
            self.x += self.vel * sgl.get_dt()

            if self.x > sgl.get_width() - self.width: 
                self.vel = -self.vel
            if self.x < 0: 
                self.vel = -self.vel

            # Make circle red when mouse is inside of it
            if self.screen_rect.is_in(sgl.get_mouse_x(), sgl.get_mouse_y()):
                self.surface = self.red_circle
            else:
                self.surface = self.normal_circle

    scene = TestScene()

    sgl.run(scene.update, scene.draw)


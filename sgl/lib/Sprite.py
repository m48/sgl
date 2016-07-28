""" Sprite Module

This module provides the bulk of the functionality of
`sgl.lib`. Nearly every other class in `sgl.lib` inherits from or uses
:any:`sgl.lib.Sprite` somehow.
"""

import sgl
from sgl.lib.Rect import Rect

def is_string(thing):
    """ Returns whether `thing` is a string or not. """

    if 'basestring' not in globals():
        return isinstance(thing, str)
    else:
        return isinstance(thing, basestring)

class Sprite(object):
    """ Provides a class to represent drawable objects. """

    def __init__(self, graphic=None):
        """ 
        Args:
            graphic (SGL Surface): A graphic that will be loaded by
            :any:`Sprite.load_surface` during initialization.
        """

        # Private attributes (will be named properly later)

        self.to_be_deleted = False
        # """ bool: Whether parent sprites will automatically delete
        # this object on the next frame """
        
        self.view_rect = None
        # """ :any:`sgl.lib.Rect.Rect`: A rectangle, in screen
        # coordinates, that specifies where child sprites will be
        # allowed to be drawn. """

        # The object's collision bounding box. Combined with property
        # to provide sane default. Documented there.
        self._collision_rect = None

        # The drawing bounding box. Don't change it manually.
        self._rect = Rect()

        self.x = 0      
        # """ number: The X position of the sprite in local
        # coordinates. """

        self.y = 0      
        # """ number: The Y position of the sprite in local
        # coordinates. """

        self.prev_x = 0      
        # """ number: The X position of the sprite on the previous
        # frame in local coordinates. """

        self.prev_y = 0      
        # """ number: The Y position of the sprite on the previous
        # frame in local coordinates. """

        self.a_x = 0      
        # """ number: The X position of the anchor point of the
        # sprite. If a float, will consider it to be a percentage of
        # the sprite size. (So 0.5 would be the middle of the sprite.)
        # """

        self.a_y = 0      
        # """ number: The Y position of the anchor point of the
        # sprite. If a float, will consider it to be a percentage of
        # the sprite size. (So 0.5 would be the middle of the sprite.)
        # """

        self.screen_x = 0      
        # """ int: The X position of the sprite after taking into
        # account transformations by the camera and parent
        # sprites. Should not be changed manually. """

        self.screen_y = 0      
        # """ int: The Y position of the sprite after taking into
        # account transformations by the camera and parent
        # sprites. Should not be changed manually. """

        self.width = 0      
        # """ number: The width of the visible portion of the
        # sprite. """

        self.height = 0      
        # """ number: The height of the visible portion of the
        # sprite. """

        # Public attributes

        self.visible = True
        """ bool: Whether parent sprites will call "draw" on this
        object. """

        self.active = True
        """ bool: Whether parent sprites will call "update" on this
        object. """
    
        self.infinite_space = False
        """ bool: Whether this object should be assumed to exist
        everywhere by the drawing functions (for example, for a group
        containing objects that spread across a large area) """
   
        self.subsprites = []
        """ list: A list of child sprites inside this one. """

        self.parent = None
        """ :any:`Sprite`: A reference to this sprite's parent
        sprite. """

        self.scene = None
        """ :any:`Scene`: A reference to the scene object this sprite
        is part of. """

        self.app = None
        """ :any:`App`: A reference to the application object this
        sprite is part of. Useful for, say, switching to a different
        scene. """

        self.parallax = 1
        """ number: What this sprite's local position will be divided
        by when transformed by camera movements. """

        self.fixed = False
        """ bool: If True, will prevent sprite from being transformed
        by camera movements. Useful for, say, HUD items. """

        self.cancel_parent_transform = False
        """ bool: If True, will prevent sprite from being transformed
        by *anything,* including parent sprites. """

        self.solid = True
        """ bool: Whether collision functions will bother with this
        sprite. """

        # Same effects as sgl.blit

        self.flip_h = False
        """ bool: Whether to flip this sprite's surface
        horizontally. (Does not propagate to child sprites.) """

        self.flip_v = False
        """ bool: Whether to flip this sprite's surface
        vertically. (Does not propagate to child sprites.) """

        self.alpha = 255
        """ number: How transparent the surface of this sprite should
        be drawn. (Does not propagate to child sprites.) """

        self.angle = 0
        """ number: The angle to which the surface of this sprite
        should be rotated. (Does not propagate to child sprites.) """

        self.pretty = False
        """ bool: Whether the rotation effect should be smoothed
        out. (Does not propagate to child sprites.) """

        # Loads the graphic
        if graphic: 
            self.load_surface(graphic)
        else:
            self.surface = None
            """ SGL Surface: The graphic of this sprite. If `None`,
            will depend on child sprites or an overriden
            :any:`Sprite.draw_self` to draw anything to the
            screen. """

    def add(self, sprite):
        """ Adds a child sprite to this end of this sprite's sprite
        list.

        Args:
            sprite (:any:`Sprite`): A :any:`Sprite` instance to
                add. """

        sprite.parent = self
        sprite.scene = self.scene
        sprite.app = self.app
        self.subsprites.append(sprite)
        sprite.on_add()

        return sprite

    def on_add(self):
        """ Exectued when a sprite is added. It's recommended to put
        initialization code here instead of ``__init__``, so that the
        sprite will have proper access to its parent elements during
        and after initialization. (Not all the examples have been
        updated to work like this, though.) """

        pass

    # User facing access
    @property
    def rect(self):
        """ :any:`sgl.lib.Rect.Rect`: Read-only property returning the
        bounding box of this sprite in local coordinates. """

        real_anchor = self.real_anchor

        self._rect.x = self.x - real_anchor[0]
        self._rect.y = self.y - real_anchor[1]
        self._rect.width = self.width
        self._rect.height = self.height
        return self._rect

    @property
    def screen_rect(self):
        """ :any:`sgl.lib.Rect.Rect`: Read-only property returning the
        bounding box of this sprite in screen coordinates (after
        camera and parent transformations have been applied). """

        real_anchor = self.real_anchor

        self._rect.x = self.screen_x - real_anchor[0]
        self._rect.y = self.screen_y - real_anchor[1]
        self._rect.width = self.width
        self._rect.height = self.height
        return self._rect

    @property
    def collision_rect(self):
        """ :any:`sgl.lib.Rect.Rect`: The bounding box that the
        collision functions will use to determine when this sprite is
        overlapping with others. If none is specified, it will assume
        you want the entire sprite to be collidable. """

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
        """ :any:`sgl.lib.Rect.Rect`: Read-only property returning the
        bounding box of this sprite in world coordinates (after
        parent, but not camera transformations have been applied).

        Todo:
            * Make this property only disregard camera
              transformations, instead of all of them. """

        real_anchor = self.real_anchor
        rect = Rect()

        rect.x = self.x + self.collision_rect.x - real_anchor[0]
        rect.y = self.y + self.collision_rect.y - real_anchor[1]
        rect.width = self.collision_rect.width
        rect.height = self.collision_rect.height
        
        return rect

    @property
    def screen_collision_rect(self):
        """ :any:`sgl.lib.Rect.Rect`: Read-only property returning the
        bounding box of this sprite in screen coordinates (after
        parent and camera transformations have been applied). """

        real_anchor = self.real_anchor
        rect = Rect()

        rect.x = self.screen_x + self.collision_rect.x - real_anchor[0]
        rect.y = self.screen_y + self.collision_rect.y - real_anchor[1]
        rect.width = self.collision_rect.width
        rect.height = self.collision_rect.height
        
        return rect

    def is_colliding_with(self, other):
        """ Returns whether this sprite is colliding with another
        one. Currently just passes responsibility to the other sprite
        by calling its :any:`Sprite.is_being_collided` function.

        Args:
            sprite (:any:`Sprite`): Another :any:`Sprite` instance to
                test.

        Returns: 
            bool: Whether this sprite is colliding with the other
                  one. """

        if not self.solid or not other.solid:
            return False

        return other.is_being_collided(self)

    def is_being_collided(self, other):
        """ Returns whether this sprite is colliding with another one.

        Args:
            sprite (:any:`Sprite`): Another :any:`Sprite` instance to
                 test.

        Returns: 
            bool: Whether this sprite is colliding with the other
                one. """

        return self.world_collision_rect.is_in(
            other.world_collision_rect
        )

    # Internally, positions are stored as x and y values, but you can
    # deal with them as tuples if you want
    @property
    def screen_position(self):
        """ tuple: Read-only property returning the screen position of
        this sprite (after parent and camera transformations have been
        applied). Can also be accessed through the ``screen_x`` and
        ``screen_y`` attributes. """

        return (self.screen_x, self.screen_y)

    @property
    def position(self):
        """ tuple: The local position of this sprite (before any
        transformations have been applied).

        Can also be accessed through the ``x`` and ``y``
        attributes. """

        return (self.x, self.y)
    
    @position.setter
    def position(self, new_value):
        self.x, self.y = new_value

    @property
    def prev_position(self):
        """ tuple: Read-only property returning the local position of
        this sprite on the previous frame.

        Can also be accessed through the ``prev_x`` and ``prev_y``
        attributes. """

        return (self.prev_x, self.prev_y)

    @property
    def anchor(self):
        """ tuple: The position of the anchor point of this
        sprite. This determines the coordinates that is considered (0,
        0) for this sprite, and impacts which point it is rotated
        around if you use that effect. 

        If either dimension is a floating-point number, they'll be
        interpreted as a percentage of the sprite's width or
        height. So, setting the anchor point to (0.5, 0.5) will placed
        in the center of the sprite's graphic.

        Can also be accessed through the ``a_x`` and ``a_y``
        attributes. """

        return (self.a_x, self.a_y)
    
    @anchor.setter
    def anchor(self, new_value):
        self.a_x, self.a_y = new_value

    # Converts the anchor point to real coordinates from the
    # scaling type
    @property
    def real_anchor(self):
        """ tuple: Read-only property returning the position of the
        anchor point of this sprite after percentage values (such as
        0.5) have been converted to real coordinates. """

        a_x, a_y = self.a_x, self.a_y
        if isinstance(a_x, float): a_x = self.width * a_x
        if isinstance(a_y, float): a_y = self.height * a_y

        return (a_x, a_y)

    @property
    def size(self):
        """ tuple: The size of this sprite. Used for positioning the
        anchor point, determining whether a sprite is visible and
        should be drawn, and as a default size for the sprite's
        collision bounding box. """

        return (self.width, self.height)
    
    @size.setter
    def size(self, new_value):
        self.width, self.height = new_value

    def is_mouse_over(self):
        """ Returns whether the mouse cursor is currently inside this
        sprite's bounding box.

        Returns: 
            bool: Whether the mouse is inside. """

        return self.screen_rect.is_in(
            sgl.get_mouse_x(), sgl.get_mouse_y()
        )

    def world_to_screen(self, x, y):
        """ Converts local coordinates in this sprite's space to
        screen coordinates.

        Args:
            x (number): The x coordinates to convert.
            y (number): The y coordinates to convert.

        Returns: 
            tuple: The new coordinates. """

        screen_x = self.x
        screen_y = self.y

        if self.parent and not self.cancel_parent_transform:

            if hasattr(self.parent, "camera") and not self.fixed:
                screen_x, screen_y = (
                    self.parent.camera.world_to_screen(
                        self.x, self.y, self.parallax)
                )

            screen_x += self.parent.screen_x
            screen_y += self.parent.screen_y

        return screen_x, screen_y

    def update_screen_positions(self):
        """ Screen positions are slightly broken. By default, screen
        coordinates are only updated in the :any:`Sprite.preupdate`
        function. This means that sometimes they will update a frame
        late if you change a parent sprite's position during its
        :any:`Sprite.update` phase. In addition, even when it does
        update, sometimes position changes will not propagate through
        the hierarchy correctly.

        This function can help you work around that by forcing all of
        this sprite and all of its child sprites to recursively update
        their screen coordinates to the correct value. If you see
        child sprites behaving strangely, try adding a call to this in
        the parent sprite's code.

        I realize this is a bit of a hack, but it is the lesser
        evil. I tried to update all screen positions on every frame,
        but that slowed the sprite system down significantly and
        created new positioning problems that, unlike these, could not
        be solved with a single extra function call. """

        self.screen_x, self.screen_y = self.world_to_screen(*self.position)
        for sprite in self.subsprites:
            sprite.update_screen_positions()

    def preupdate(self):
        """ Called before this sprite updates. Currently, contains
        logic to save the previous position and update the screen
        position. """

        self.prev_x, self.prev_y = self.position

        # Because we might need to know in update()
        self.screen_x, self.screen_y = self.world_to_screen(*self.position)

    def update(self):
        """ Called every frame to update this sprite and its child
        sprites' logic. To define logic for your sprite, override this
        function. If you want child sprite updating to work properly,
        though, make sure to call the :any:`Sprite` base classes'
        update function before yours. """

        for index, sprite in enumerate(self.subsprites):
            sprite.preupdate()

            if sprite.active: 
                sprite.update()

            if sprite.to_be_deleted:
                del self.subsprites[index]

    def draw(self):
        """ Handle drawing this sprite and its children. Should not be
        overwritten to define custom drawing logic, unless you want to
        break drawing child sprites. Instead, override
        :any:`Sprite.draw_self`. """

        if not self.visible: return

        # Because update might have changed things, and we want to
        # draw it in the right place
        # self.screen_x, self.screen_y = self.world_to_screen(*self.position)

        self.draw_self()
        self.draw_children()

    def draw_self(self):
        """ Handle drawings this sprite. If you want to customize how
        sprite drawing works, override this function."""

        if self.surface:
            if (not (self.flip_h or self.flip_v) 
                and self.alpha == 255 or self.alpha == 1.0
                and self.angle == 0):
                a_x, a_y = self.real_anchor
                sgl.blitf(
                    self.surface, 
                    self.screen_x - a_x, self.screen_y - a_y
                )
            else:
                sgl.blit(
                    self.surface, 
                    self.screen_x, self.screen_y, 
                    a_x=self.a_x, a_y=self.a_y,
                    angle=self.angle, pretty=self.pretty,
                    flip_h=self.flip_h, flip_v=self.flip_v,
                    alpha=self.alpha
                )

    def draw_children(self):
        """ Loops through and draws child sprites. Ideally, should not
        be called manually.

        Currently, this updates each sprite's screen position one more
        time, to make them slightly more predictable. """

        if self.subsprites == []: return
        # Most accurate way, but slower
        # Use this if things get stupid again
        # self.update_screen_positions()

        for sprite in self.subsprites:
            sprite.screen_x, sprite.screen_y = sprite.world_to_screen(*sprite.position)

            if self.view_rect and not sprite.infinite_space:
                if (sprite.screen_rect.is_in(self.view_rect)):
                    sprite.draw()
            else:
                sprite.draw()

    # Load surface and sets size accordingly.
    def load_surface(self, surface):
        """ Sets the graphic for this sprite, and makes the size match
        the size of this graphic.

        Args:
            surface (SGL Surface): A surface containing the graphic
                you want this sprite to draw.
        """        

        self.surface = surface
        self.autosize()

    def autosize(self):
        """ Updates this sprite's size to match the size of its
        surface. Automatically called by :any:`Sprite.load_surface`
        and when sprites are initialized with surfaces. """

        if self.surface:
            with sgl.with_buffer(self.surface):
                self.width = sgl.get_width()
                self.height = sgl.get_height()
        else:
            self.width, self.height = 0,0         

    def fill(self):
        """ Utility function to make this sprite completely fill its
        parent sprite. If it has no parent sprite, it will fill the
        screen. """

        self.anchor = 0, 0
        self.position = 0, 0
        if self.parent:
            self.size = self.parent.size
        else:
            self.size = sgl.get_width(), sgl.get_height()

    def center(self):
        """ Utility function to place this sprite in the center of its
        parent sprite. If it has no parent sprite, it will be placed
        in the center of the screen. """

        self.anchor = 0.5, 0.5
        
        if self.parent:
            self.position = self.parent.width/2, self.parent.height/2
        else:
            self.position = sgl.get_width()/2, sgl.get_height()/2

    def centre(self):
        """ Like :any:`center`, but British. """

        # In honor of wxWidgets
        self.center()

    def kill(self):
        """ Marks this sprite to be deleted on the next frame. """

        self.to_be_deleted = True

class AnimatedSprite(Sprite):
    """ A subclass of :any:`Sprite` that provides extra functions
    useful for managing frame-based animations. """
    
    frames = []
    """ list: A list of SGL Surfaces that will provide all the
    possible frames this sprite can use in its animations. 

    It is recommended you initialize this value in the header of your
    class, so that these frames will be shared across all instances.

    If you change this attribute while an animation is running, you
    may cause glitches. """

    animations = {}
    """ dictionary of lists: A dictionary specifying all the different
    animations that can use these frames.

    The *keys* of this dictionary should be *strings* specifying the names
    of the animations. These strings will be used to refer to these
    animations in other parts of your code.

    The *values* of this dictionary should be *lists* that specify which
    frames should be played when. 

    There are multiple rules that determine how the items of this list
    will be interpreted.

    If an item of the frame list is an *integer,* that means that the
    frame of that index (from :any:`frames`) will be shown for the
    default frame length (:any:`anim_def_frame_length`).

    This means that, if you're okay with each frame of your sprite's
    animations being shown for the same amount of time, your animation
    definitions can be nothing but a list of numbers::

        animations = {
            "stand": [0],
            "walk": [1,2,3,4],
            "punch": [5,6,7],
        }

    In fact, if you know an animation will consist of nothing but
    contiguous frames, there's nothing stopping you from using
    :any:`range` to construct animations::

        animations = {
            "stand": [0],
            "walk": list(range(1,5)),
            "punch": list(range(5,8)),
        }

    (The :any:`list` is there just for Python 3 compatibility, so that
    the animation is not set to be an iterator. If you are using
    Python 2, it will work without that.)

    Todo:
        * Maybe it would be useful to support iterators for
          animations? That could allow animations of potentially
          infinite length, which could be fun.

    If an item of the frame list is a *dictionary,* it can do multiple
    things, depending on which keys are specified:

    * If a ``"frame"`` item is specified, this will determine which
      frame index to show at that point.
    * If a ``"time"`` item is specified, this will make just that
      frame be shown for ``"time"`` amount of time. (A ``"frame"``
      item must be specified for this to work.)
    * If a ``"callback"`` item is specified, this class will call the
      function specified in the value as soon as this frame is
      reached. This value can either be a string, containing the name of
      a method of your class, or a function reference, which can point
      to anything. (You can also use ``"callback"`` without specifying a
      frame to show, enabling you to, among other things, call callbacks
      `after` a frame is shown.)
    
    Todo:
        * Currently, you cannot pass arguments to these
          functions. That would probably be handy.

    * If ``"default_length"`` is specified, from that point onward, the
      default frame length for `just this animation` will be set to the
      value you specify. (This should always be used in a dictionary on
      its own, without any other keys specified.)

    Todo:
        * The ability to provide custom anchor points for each frame
          may also be useful.
        * The ability to provide arbitrary rectangles for each frame
          may be useful for things like fighting games, in which it is
          common to have separate hitboxes for each body part. I'll
          add this when I figure out how to gracefully pass references
          to these rectangles to the collision library. Making
          rectangles always point to the same memory address, even
          when they are not being used, sounds... a bit painful.

    For example, a more complicated animation definition may
    look like this::

        animations = {
            "pulse": [
                {"default_length": 1/8},
                {"frame": 0, "length": 1},
                1,2,3,
                {"frame": 4, "length": 1, "callback": "do_stuff"},
                3,2,1,
                {"callback": "animation_over"},
            ],
        }

    It is recommended you initialize this value in the header of your
    class, so that these animations will be shared across all instances.

    If you change this attribute while an animation is running, you
    will definitely cause glitches.
    """

    def __init__(self):
        super(AnimatedSprite, self).__init__()

        self.anim_time = 0
        self.anim_next_frame_time = 0
        self.anim_index = 0
        self.anim_name = ""

        self.anim_def_frame_length = 1.0/15.0
        """ number: Specifies (in seconds) the amount of time each
        frame will be displayed if you do not specify any custom times
        in your animation. By default, this is set to display each
        frame for a 15th of a second---in other words, it will play
        your animations at 15 frames per second. """

        self.anim_frame_length = 0

        self.anim_playing = False

    @property
    def anim_current_frame(self):
        # """ Internal use only. Returns current int or dict for frame. """

        return self.animations[self.animation][self.anim_index]

    @property
    def anim_length(self):
        # """ Read-only property returning the amount of items in the current animation. """

        return len(self.animations[self.animation])

    @property
    def animation(self):
        """ string: Property containing the name of the currently
        playing animation. This name should correspond to one of the
        keys in :any:`animations`.

        If you set this property, it will immediately switch to the
        animation of that name. The current playing state (whether
        this sprite is playing whatever the current animation is, or
        paused), however, will remain unchanged. """

        return self.anim_name

    @animation.setter
    def animation(self, value):
        self.anim_reset()
        self.anim_name = value
        self.anim_update_frame()

    @property
    def playing(self):
        """ bool: Returns whether this sprite is currently playing
        whatever the active animation is. """

        return self.anim_playing

    def anim_reset(self):
        # """ Internal function. Resets the playhead to the first
        # frame, and resets state variables. """

        self.anim_time = 0
        self.anim_next_frame_time = 0
        self.anim_index = 0

    def play(self):
        """ Starts playing the active animation. """
        
        self.anim_playing = True

    def pause(self):
        """ Pauses playment that the current point. You can call
        :any:`play` to resume playment from this point. """

        self.anim_playing = False

    def stop(self):
        """ Stops playment. This is the same as calling
        :any:`pause`, except the animation is reset to
        the first frame before stopping. """

        self.anim_reset()
        self.anim_playing = False

    def do_callback(self, value):
        # """ Internal function. Calls the function specified in
        # ``value``, accounting for various different formats this
        # could take. """

        if is_string(value):
            getattr(self, value)()
        elif hasattr(value, "__call__"):
            value()
        else:
            getattr(self, value[0])(*value[1:])

    def anim_update_frame(self):
        # """ Internal use only. When the current frame's time has
        # expired, this will move to the next frame and execute any
        # special commands on the way. """

        if self.anim_index >= self.anim_length: return

        self.anim_time = 0

        frame = self.anim_current_frame
        complex_frame = isinstance(frame, dict)
        length = self.anim_frame_length or self.anim_def_frame_length

        if complex_frame:
            if "frame" not in frame:
                if "default_length" in frame:
                    self.anim_frame_length = frame["default_length"]

                if "callback" in frame:
                    self.do_callback(frame["callback"])

                self.anim_index += 1
                self.anim_update_frame()
                return

            self.surface = self.frames[frame["frame"]]
            self.anim_next_frame_time = frame.get("length", length)

            if "callback" in frame:
                self.do_callback(frame["callback"])

        else:
            self.surface = self.frames[frame]
            self.anim_next_frame_time = length
       
    def preupdate(self):
        """ Overridden to handle animation logic, in addition to what
        :any:`Sprite.preupdate` doas. 

        Todo:
            * It might be useful to be able to restrict how many times
              an animation can loop, so you can, say, only play an
              animation once. Currently you can simulate this
              callbacks, but that's a little cumbersome.
            * Maybe make this attempt to make up for lost time, like
              :any:`sgl.lib.Time` does. """

        super(AnimatedSprite, self).preupdate()

        if not self.anim_playing: return
        
        self.anim_time += sgl.get_dt()

        if self.anim_time >= self.anim_next_frame_time:
            self.anim_index += 1
            if self.anim_index >= self.anim_length:
                self.anim_index = 0
                # loop restricting logic here?

            self.anim_update_frame()
        # maybe awkward that this does not attempt to make up for
        # lost time like sgl.lib.Time does?

# Might be an object later
def Spritesheet(surface, frame_width=0, frame_height=0):
    """ Takes a surface containing a spritesheet and extracts each
    individual frame from it. Often necessary to use
    :any:`AnimatedSprite` effectively.

    Args:
        surface (SGL Surface): A graphic containing a spritesheet with
            equally sized frames starting from (0,0). This function
            does not do anything in regards to transparency. You must
            load your graphic with :any:`sgl.set_transparent_color` or
            :any:`sgl.load_alpha_image` for transparency to work.
        frame_width (int): How wide each frame is.
        frame_height (int): How high each frame is.

    Returns:
        list: A list of each frame in this spritesheet.

    Todo:
        * This may eventually be a class, so that spritesheets can
          blit chunks from a single surface instead of initializing
          possibly hundreds of tiny little surfaces for each frame. I
          think that will be more efficient, particularly with
          hardware accelerated backends. I'll try to make this class
          behave identically to a list in most cases, but keep in mind
          that code depending on modifying the frames of a spritesheet
          like a list could break when this change happens. """

    with sgl.with_buffer(surface):
        frames = []
        x = 0
        y = 0
        width = sgl.get_width()
        height = sgl.get_height()

        while True:
            chunk = sgl.get_chunk(x, y, frame_width, frame_height)
            frames.append(chunk)
            
            x += frame_width
            if x + frame_width > width:
                x = 0
                y += frame_height
                if y + frame_height > height:
                    break

        return frames

class ShapeSprite(Sprite):
    """ A subclass of :any:`Sprite` designed to handle shapes drawn
    with the SGL drawing commands instead of blitting surfaces to the
    screen. 

    This will often be faster than drawing the equivalent surface. """

    def __init__(self):
        super(ShapeSprite, self).__init__()
        
        self.no_stroke = False
        """ bool: Whether strokes should be turned off when drawing the
        shape. (See :any:`sgl.no_stroke`.) """

        self.stroke_color = 1.0
        """ number or tuple: What color the strokes of the shape
        should be. (See :any:`sgl.set_stroke`.)

        This class will attempt to mix this color value with the
        :any:`alpha` value, so you can accurately set the
        transparency of sprites with this property. Keep in mind that
        under Pygame this is quite slow. """

        self.stroke_weight = 1
        """ number: How thick the strokes of the shape should be. (See
        :any:`sgl.set_stroke_weight`.) """

        self.no_fill = False
        """ bool: Whether fills should be turned off when drawing the
        shape. (See :any:`sgl.no_fill`.) """

        self.fill_color = 0.75
        """ number or tuple: What color the fill of the shape
        should be. (See :any:`sgl.set_fill`.)

        This class will attempt to mix this color value with the
        :any:`alpha` value, so you can accurately set the
        transparency of sprites with this property. Keep in mind that
        under Pygame this is quite slow. """

    def draw_shape(self):
        """ Override this function to specify what shape this sprite
        should draw. The stroke and fill properties will have already
        been set by the other functions of this class, and will
        automatically be restored to their previous values after this
        function has been executed. """

        pass

    def set_color_alpha(self, color):
        if self.alpha == 255 or self.alpha == 1.0:
            return color

        try:
            len(color)
        except:
            return (color, self.alpha)

        if len(color) == 1:
            return (color[0], self.alpha)
        elif len(color) == 2:
            return (color[0], color[1]-self.alpha)
        elif len(color) == 3:
            return (color[0], color[1], color[2], self.alpha)
        elif len(color) == 4:
            return (color[0], color[1], color[2], color[3]-self.alpha)

    def draw_self(self):
        with sgl.with_state():
            if self.no_stroke:
                sgl.no_stroke()
            else:
                sgl.set_stroke(self.set_color_alpha(self.stroke_color))
                sgl.set_stroke_weight(self.stroke_weight)

            if self.no_fill:
                sgl.no_fill()
            else:
                sgl.set_fill(self.set_color_alpha(self.fill_color))

            self.draw_shape()

class RectSprite(ShapeSprite):
    """ A subclass of :any:`ShapeSprite` that draws a rectangle in the
    bounding box of the sprite. """

    def draw_shape(self):
        sgl.draw_rect(*self.screen_rect.to_tuple())

class EllipseSprite(ShapeSprite):
    """ A subclass of :any:`ShapeSprite` that draws an ellipse (or
    circle, if :any:`width` and :any:`height` are the same) in the
    bounding box of the sprite. """

    def draw_shape(self):
        sgl.draw_ellipse(*self.screen_rect.to_tuple())
                
# Special object to store camera stuff
class Camera(object):
    """ A small object to hold the coordinates of the camera in a
    given scene. """

    def __init__(self):
        self.x, self.y = 0,0

    @property
    def position(self):
        """ tuple: The position of the camera---or, in other words,
        the coordinates in the scene that will be displayed at the top
        left corner of the window.

        Can also be accessed through the ``x`` and ``y``
        attributes. """

        return (self.x, self.y)
    
    @position.setter
    def position(self, new_value):
        self.x, self.y = new_value

    def world_to_screen(self, x, y, parallax=1):
        if parallax == 1:
            return (x - self.x, y - self.y) 
        else:
            return (x - self.x/parallax, y - self.y/parallax)             

    def screen_to_world(self, x, y, parallax=1):
        return (x + self.x*parallax, y + self.y*parallax) 

# Specialized types of groups
class SpriteGroup(Sprite):
    """ A subclass of :any:`Sprite` designed to do nothing but hold
    other sprites. 

    Identical to a plain :any:`Sprite`, except :any:`infinite_space`
    is turned on by default."""

    def __init__(self):
        super(SpriteGroup, self).__init__()
        
        self.infinite_space = True

class PerspectiveGroup(SpriteGroup):
    def __init__(self):
        super(PerspectiveGroup, self).__init__()

        self.max_level = 100
        self.recursion_level = 0

    def draw_children(self):
        # Just re-implementing most of draw_children. Involves little
        # more copy+paste than I'd like, but I can't think of a better
        # way to do it

        if self.subsprites == []: return
        # Most accurate way, but slower
        # Use this if things get stupid again
        # self.update_screen_positions()

        subsprites = sorted(self.get_subsprites(self), key = lambda o: o.y)

        for sprite in subsprites:
            sprite.screen_x, sprite.screen_y = sprite.world_to_screen(*sprite.position)

            if (hasattr(sprite, "no_perspective") 
                and sprite.no_perspective):
                draw_function = sprite.draw
            else:
                draw_function = sprite.draw_self

            if self.view_rect and not sprite.infinite_space:
                if (sprite.screen_rect.is_in(self.view_rect)):
                    draw_function()
            else:
                draw_function()

    def get_subsprites(self, sprite):
        subsprites = sprite.subsprites[:]
        for item in sprite.subsprites:
            if ((hasattr(item, "no_perspective") 
                 and item.no_perspective) or 
                self.recursion_level >= self.max_level):
                subsprites.append(item)
                if item.subsprites:
                    item.no_perspective = True

            else:
                self.recursion_level += 1
                subsprites += self.get_subsprites(item)
                self.recursion_level -= 1

        return subsprites

class App(object):
    def __init__(self, first_scene):
        self.switch_scene(first_scene)

    def switch_scene(self, scene):
        self.scene = scene
        scene.app = self

    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw()
    
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

        self.scene = self

    def draw(self):
        sgl.clear(self.background_color)

        super(Scene, self).draw()

class Viewport(Sprite):
    def __init__(self):
        super(Viewport, self).__init__()

        self.camera = Camera()

        self.background_color = None

    def draw(self):
        if not self.visible: return

        with sgl.with_state():
            self.view_rect = self.screen_rect

            existing_rect = sgl.get_clip_rect()
            if existing_rect:
                existing_rect = Rect(*existing_rect)
                new_rect = existing_rect.intersect(self.screen_rect)
                if new_rect:
                    sgl.set_clip_rect(*new_rect.to_tuple())
                else:
                    return
            else:
                sgl.set_clip_rect(*self.screen_rect.to_tuple())

            if self.background_color != None:
                sgl.clear(self.background_color)
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
                self.camera.y += v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.up): 
                self.camera.y -= v * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.right): 
                self.camera.x += v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.left): 
                self.camera.x -= v * sgl.get_dt()

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
                {"default_length": 1/8},
                {"frame": 0, "length": 1},
                1,2,3,
                {"frame": 4, "length": 1},#, "callback": "pause"},
                3,2,1,
            ],
            "crazy": list(range(4)),
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

            self.alpha = 200

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

    app = App(TestScene())

    sgl.run(app.update, app.draw)


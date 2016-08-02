""" This module mainly provides one class, :any:`FlowLayout`, that
lets one arrange sprite similarly to the automatic layout functions of
some GUI frameworks. This can be useful for laying out game GUIs in a
resolution independent way. """

import sgl
from sgl.lib.Rect import Rect
from sgl.lib.Sprite import Sprite, EllipseSprite, RectSprite, Scene, App
import sgl.lib.Time as time

class FlowLayout(Sprite):
    """ A Sprite that provides similar functionality to `wxWidget's BoxSizer <http://docs.wxwidgets.org/trunk/overview_sizer.html#overview_sizer_box>`_. """

    def __init__(self, horizontal=False):
        """ 
        Args:
            horizontal (bool): Whether this layout runs horizontally
                or not. If this is False, the default, it will run
                vertically. This can be set later with the
                :any:`horizontal` property.
        """

        super(FlowLayout, self).__init__()

        self.margin = 0
        """ How much space will be between the borders of this sprite
        and the items placed inside of it."""

        self.spacing = 0
        """ How much space each item in this layout will have between
        them. """

        self.size = 0,0

        self._horizontal = horizontal

        self.has_stretchy = False

        self.draw_debug = False
        """ Mostly for internal use, but could be useful for normal
        development as well. If this is True, the layout, the items
        inside, and the margin will have green rectangles drawn around
        them. """

        self.min_width = 0
        """ The minimum width this layout can be without causing
        visual artifacts. """

        self.min_height = 0
        """ The minimum height this layout can be without causing
        visual artifacts. 

        Todo: 
            These are not entirely accurate yet. They do not take into
            account the size of stretchy elements at the smallest size
            to accommodate the non-stretchy elements. I will fix this
            later, but for now, keep in mind these are just general
            values that will at least prevent your layout from
            completely folding in on itself. """


    @property
    def horizontal(self):
        """ Whether this layout runs horizontally or not. If this is
        False, the default, it will run vertically. """

        return self._horizontal

    @horizontal.setter
    def horizontal(self, value):
        self._horizontal = value

        for sprite in self.subsprites:
            sprite.width = sprite.original_width
            sprite.height = sprite.original_height

    def add(self, sprite, proportion=0.0, 
            proportion_other_way=0.0, align=0.0):
        """ Behaves similarly to :any:`Sprite.add`, but with
        additional parameters to determine how the added sprite will
        be fit into the layout.

        Args:
            sprite (:any:`Sprite`): A :any:`Sprite` instance to
                add.
            proportion (float): The amount of space this sprite will
                take up in *the direction that the layout flows*
                (which is set by :any:`horizontal`). If this value is
                0, this sprite will merely take up its original
                size. If it is anything else, its size will be
                calculated relative to the size of the layout and the
                other sprites.

                Basically, the way it works is this: take all of the
                sprites with proportion values, and add those numbers
                up. That will be the *total proportion value.* The
                size of each sprite will be its own proportion value
                over the total proportion value.

                So, if the proportion value is 1 for every sprite in a
                layout, their sizes will be distributed evenly across
                the layout.

                If one of those sprites has a proportion value of 2,
                however, it will be twice as large as the other ones,
                and the other sprites' sizes will be twice as
                small. It all balances out in the end. 

                It would be equally valid to set the larger sprite's
                proportion value to 1, and the smaller sprites' to 0.5
                for this---the exact values do not matter as much as
                how the proportion values relate to *each other.* This
                is slightly different from wxWidgets, in which
                proportion values must be whole numbers.

                It may make it easier to understand certain layouts if
                you specify proportion values as fractions (such as
                0.25), and make sure they add up to 1.0 in the end.

                It is also important to note that the space taken into
                account for proportioned sprites is *the space left
                behind by non-proportioned sprites.* So, if you have a
                layout with a few non-proportioned sprites, and add a
                sprite with a proportion value of 1 to that layout, it
                will not fill the entire layout---it will take up the
                entire space left behind by the other sprites.

                This gives you many possibilities for positioning
                non-proportioned sprites. If you have two normal
                sprites and put a sprites with a proportion value of 1
                between them, for example, you will force both normal
                sprites to be on opposite ends of the layout. If you
                want to distribute normal sprites equally across an
                area, you can space them out with proportion 1
                spaces. And so on.

                Proportion values are slightly difficult to
                understand, but once you get them, they will open up
                many possibilities for layout.
            proportion_other_way (float): This argument is much easier
                to understand than the proportion value.

                It is a percentage value specifying how much space the
                sprite will take up on the axis perpendicular to the
                direction the layout flows. So, if the layout flows
                *vertically,* this specifies how a sprite's
                *horizontal* size will be affected by it.

                Usually, you will either want this value to be 0,
                which will leave the sprite's size in that direction
                untouched, or 1.0, which will make the sprite
                completely fill the layout in that direction. Anything
                in between will leave the sprite somewhere in the
                middle of that. (Or, more accurately, the size of the
                layout in that direction times this value.)
            align (float): If ``proportion_other_way`` leaves any
                breathing room for the sprite, this specifies how that
                sprite should be *positioned* in the layout.

                If this is 0, the sprite will rest along the left or
                top edge of the layout. If this is 0.5, it will be
                centered along that direction. If this is 1.0, it will
                be bottom or right aligned. And other values will be
                somewhere inbetween.

                You will not need to set this argument in most
                cases. If you do, 0.5 will likely be the most common
                value you'll use for it.
        """

        super(FlowLayout, self).add(sprite)
        sprite.flow_proportion = proportion
        sprite.flow_other_proportion = proportion_other_way
        sprite.flow_align = align
        
        sprite.original_width = sprite.width
        sprite.original_height = sprite.height

        if proportion: self.has_stretchy = True

    def clear(self):
        """ Removes everything in this layout. 

        Todo:
            Is this a method of :any:`Sprite`? If it isn't, why not? """

        self.subsprites = []
        self.has_stretchy = False

    def reflow(self):
        """ Repositions and resizes the elements inside to adhere to
        the layout rules. Must always be *manually called* to update
        the objects inside, even after adding new objects. (I tried
        having it automatically update the layouts, and the annoyance
        of having sprites move around at unpredictable times
        outweighed the benefits.)

        Is a potentially expensive function. If there are proportioned
        sprites in the layout, it must run two passes through the
        objects inside. In most cases, is recommended to call this
        function once---after this layout has been positioned and
        sized correctly, and after all of its items have been added.

        If any sprites inside this layout have a ``reflow`` method, it
        will call it. This is useful for embedding layouts
        hierarchically, or specifying custom logic for sprites when
        they are resized. """

        # Figure out sizes along the right axes. Throughout this
        # function, size refers to the direction the layout flows
        # along, and other_size refers to the perpendicular
        # direction. These generic names are used to reuse code for
        # layouts flowing horizontally and vertically.
        self_size = (self.width if self.horizontal else self.height) - self.margin*2
        self_other_size = (self.height if self.horizontal else self.width) - self.margin*2

        # If there are proportioned elements, calculate the total
        # proportion and the amount of leftover space from
        # non-proportioned sprites.
        # 
        # There might be a way to do this in same pass as
        # positioning, but it's probably a nightmare.
        if self.has_stretchy:
            total_size = 0
            stretchy_total = 0
            stretchy_amount = 0
            last_stretchy = None

            for sprite in self.subsprites:
                if sprite.flow_proportion:
                    stretchy_total += sprite.flow_proportion
                    stretchy_amount += 1
                    last_stretchy = sprite
                else:
                    total_size += (sprite.width if self.horizontal else sprite.height) + self.spacing

            leftover = (self_size - total_size)
            if leftover < 0: leftover = 0
               
        # Specifies position. Initialize at margin
        offset = self.margin

        # For collecting values for min_width/height
        total_size = 0
        total_other_size = 0

        # Actually move sprites around
        for sprite in self.subsprites:

            # Move to right position
            if self.horizontal:
                sprite.x = int(offset)
            else:
                sprite.y = int(offset)

            # Collect size
            size = sprite.width if self.horizontal else sprite.height
            other_size = sprite.height if self.horizontal else sprite.width
    
            # Resize proportioned sprites
            if sprite.flow_proportion:
                # Calculate size
                size = (
                    (leftover / stretchy_total) 
                    * sprite.flow_proportion
                ) 

                # Make sure to take into account spacing, otherwise
                # size will be too big 
                # (I wish I remembered how the math worked here)
                if self.spacing:
                    size -= (self.spacing - 
                             (self.spacing/stretchy_amount))

                # Avoid negative values
                if size < 0: size = 0

                # Actually set size
                if self.horizontal:
                    sprite.width = int(size)+1
                    # The "+1" helps avoid one pixel gap

                    # Help collect minimum size
                    # (That may be a separate function later)
                    if hasattr(sprite, "min_width"):
                        total_size += sprite.min_width
                    else:
                        total_size += 1

                # Same for vertical
                else:
                    sprite.height = int(size)+1

                    if hasattr(sprite, "min_height"):
                        total_size += sprite.min_height
                    else:
                        total_size += 1

                # Call reflow function if exists
                if (hasattr(sprite, "reflow") 
                    and hasattr(sprite.reflow, "__call__")):
                    sprite.reflow()

            # For non-proportioned sprites
            else:
                if self.horizontal:
                    total_size += sprite.width
                else:
                    total_size += sprite.height

            # Resize other way. Basically same as other
            if sprite.flow_other_proportion:
                new_size = self_other_size * sprite.flow_other_proportion

                if self.horizontal:
                    sprite.height = int(new_size)
                else:
                    sprite.width = int(new_size)

                if (hasattr(sprite, "reflow") 
                    and hasattr(sprite.reflow, "__call__")):
                    sprite.reflow()

                if self.horizontal:
                    if hasattr(sprite, "min_height"):
                        total_other_size += sprite.min_height
                else:
                    if hasattr(sprite, "min_width"):
                        total_other_size += sprite.min_width

            # For normal sprites that way around
            else:
                if self.horizontal:
                    if sprite.height > total_other_size:
                        total_other_size = sprite.height
                else:
                    if sprite.width > total_other_size:                    
                        total_other_size = sprite.width

            # Move sprite to special place if align specified
            if sprite.flow_align:
                other_offset = (
                    self_other_size * sprite.flow_align
                    - other_size * sprite.flow_align
                ) + self.margin

                if self.horizontal:
                    sprite.y = int(other_offset)
                    if sprite.y < self.margin: 
                        sprite.y = int(self.margin)
                else:
                    sprite.x = int(other_offset)
                    if sprite.x < self.margin: 
                        sprite.x = int(self.margin)

            # If align not specified
            else:
                if self.horizontal:
                    sprite.y = int(self.margin)
                else:
                    sprite.x = int(self.margin)

            # Increment position values
            offset += size + self.spacing
            total_size += self.spacing

        # When done, collect minimum sizes
        if self.horizontal:
            self.min_width = total_size
            self.min_height = total_other_size
        else:
            self.min_height = total_size
            self.min_width = total_other_size
    
    def draw(self):
        super(FlowLayout, self).draw()
        
        if self.draw_debug:
            with sgl.with_state():
                sgl.no_fill()

                sgl.set_stroke(0, 0.5, 0)
                sgl.draw_rect(self.screen_x + self.margin,
                              self.screen_y + self.margin,
                              self.width - self.margin*2,
                              self.height - self.margin*2)

                sgl.set_stroke(0, 1.0, 0)
                sgl.draw_rect(*self.screen_rect.to_tuple())

class Spacer(object):
    """ A dummy object you can add to :any:`FlowLayout` instead of a
    :any:`Sprite` when you want to have an invisible spacer sprite to
    affect the positioning of other sprites.

    Provides the absolute minimum amount of data required of an object
    to interact with the sprite system. """

    def __init__(self, width=0, height=0):
        """
        Args:
            width (int): The width of the spacer, if you do not plan
                 to have it controlled by a proportion value.
            height (int): The height of the spacer, if you do not plan
                 to have it controlled by a proportion value.
        """

        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

        self.position = 0,0

        self.active = False
        self.visible = False
        self.to_be_deleted = False

    def world_to_screen(self, x, y):
        return 0, 0 

    def on_add(self):
        pass

    def preupdate(self):
        pass

    def draw(self):
        pass
        
if __name__ == "__main__":
    sgl.init(640, 480, 1)

    def make_circle(color):
        circle = EllipseSprite()

        circle.no_stroke = True
        circle.fill_color = color

        circle.size = 32, 32

        return circle

    def make_rect(color):
        circle = RectSprite()

        circle.no_stroke = True
        circle.fill_color = color

        circle.size = 32, 32

        return circle

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            self.flow_rect = RectSprite()

            self.flow_rect.size = 0,0

            self.flow_rect.no_stroke = True
            self.flow_rect.fill_color = 0.25

            self.add(self.flow_rect)

            self.flow = FlowLayout(False)

            self.flow.position = 32,32
            self.flow.size = sgl.get_width()-32-32, 32

            self.flow.spacing = 5

            self.flow.add(make_circle(1.0), 0, 0, 0)
            self.flow.add(make_circle(1.0), 0, 0, 0.75)
            self.flow.add(make_circle(1.0), 0, 0, 1.00)
            self.flow.add(make_rect(0.50), 0.25, 0.75, 0.5)

            self.flow2 = FlowLayout(True)
            self.flow2.size = 50, 200

            self.flow2.add(make_rect(0.75), 1.0, 1.0, 0)            
            self.flow2.add(make_circle(1.0), 0, 0, 0.5)
            self.flow2.add(make_circle(1.0), 0, 0, 0.5)
            self.flow2.add(make_rect(0.75), 1.0, 1.0, 0)

            self.flow.add(self.flow2, 1.0, 1.0, 0)

            self.flow.add(make_rect(0.50), 0.25, 0.75, 0.5)
            self.flow.add(make_circle(1.0), 0, 0, 1.00)
            self.flow.add(make_circle(1.0), 0, 0, 0.75)
            self.flow.add(make_circle(1.0), 0, 0, 0)

            # self.flow.add(make_rect((0, 0.5, 0)), 2.0, 1.0)
            # self.flow.add(make_circle(0.5), 0, 0, 1.0)
            # self.flow.add(make_rect((0, 0.5, 0)), 1.0, 0.5, 0.5)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0, 0, 0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_rect((0, 0.8, 0)), 1.0)
            # self.flow.add(make_circle(0.25))

            self.flow.reflow()

            self.add(self.flow)

        def update(self):
            super(TestScene, self).update()

            x = sgl.get_mouse_x()
            y = sgl.get_mouse_y()

            w = x - self.flow.x
            h = y - self.flow.y

            if w > self.flow.min_width +20:
                self.flow.width = w
            else:
                self.flow.width = self.flow.min_width+20

            if h > self.flow.min_height:
                self.flow.height = h
            else:
                self.flow.height = self.flow.min_height

            self.flow_rect.position = self.flow.position
            self.flow_rect.size = self.flow.size

            if sgl.is_key_pressed(sgl.key.right 
                                  if self.flow.horizontal 
                                  else sgl.key.down):
                self.flow.spacing += 10 * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.left 
                                  if self.flow.horizontal 
                                  else sgl.key.up):
                if self.flow.spacing > 0:
                    self.flow.spacing -= 10 * sgl.get_dt()
                    if self.flow.spacing < 0: self.flow.spacing = 0

            if sgl.is_key_pressed(sgl.key.down 
                                  if self.flow.horizontal 
                                  else sgl.key.right):
                self.flow.margin += 10 * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.up
                                  if self.flow.horizontal 
                                  else sgl.key.left):
                if self.flow.margin > 0:
                    self.flow.margin -= 10 * sgl.get_dt()
                    if self.flow.margin < 0: self.flow.margin = 0

            if sgl.on_mouse_up():
                self.flow.horizontal = not self.flow.horizontal
                self.flow.reflow()

            self.flow.reflow()

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    app = App(TestScene())

    sgl.run(app.update, app.draw)


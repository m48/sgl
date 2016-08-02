""" This module provides some functions for working with bounding box
based collisions. It is fairly basic, and not very optimized, but for
most use cases, it works out of the box and does not let objects
randomly get stuck in and fall through each other, something a
disturbing amount of game engines lack. """

import sgl
from sgl.lib.Sprite import *
from sgl.lib.Rect import Rect

import inspect
import math

class CollisionChecker(object):
    """ An object that checks whether sprites are overlapping every
    frame, and takes user-specified action as a result.

    This is mostly used by the backend of
    :any:`sgl.lib.Collision`. From an end user's perspective, this
    class will mostly be used to stop and resume collision
    checking. """

    def __init__(self, object1, object2, callback):
        self.object1 = object1
        self.object2 = object2
        self.callback = callback

        if callback:
            args = inspect.getargspec(callback).args
            self.callback_args = len(args)
            if args[0] == "self":
                self.callback_args -= 1
        else:
            self.callback_args = -1

        self.to_be_deleted = False
        self.active = True

    def stop(self):
        """ Stops a collision checker entirely by deleting the
        object. """

        self.to_be_deleted = True

    def pause(self):
        """ Temporarily pauses this collision checker, without
        deleting it. """

        self.active = False

    def resume(self):
        """ Resumes a previously paused collision checker. """

        self.active = True

    def do_callback(self, this, other):
        if self.callback_args == 0:
            self.callback()

        elif self.callback_args == 1:
            self.callback(other)

        elif self.callback_args == 2:
            self.callback(this, other)

        elif self.callback_args >= 2:
            intersection = this.rect.intersect(other.rect)
            self.callback(this, other, intersection)

    def update(self):
        if self.active:
            self.check_collision(True)

    def check_collision(self, do_callback=False):
        # Only check collision against the other sprite's rectangle if
        # it has a display surface. If it doesn't, that means it's a
        # group, and we don't want to test the rectangle of the whole
        # group
        if True:
            if self.object1.is_colliding_with(self.object2):
                if do_callback:
                    self.do_callback(self.object1, self.object2)
                return True
        
        # Check collision against subsprites, if it's a group
        for sprite in self.object2.subsprites:
            if self.object1.is_colliding_with(sprite):
                if do_callback:
                    self.do_callback(self.object1, sprite)
                return True

        return False

class SlidingCollisionChecker(CollisionChecker):
    """ Identical to a normal :any:`CollisionChecker`, except that its
    update function provides additional logic to move objects outside
    of each other. """

    def do_callback(self, direction=[]):
        if self.callback_args == 0:
            self.callback()

        elif self.callback_args == 1:
            self.callback(direction)

    def update(self):
        if not self.active: return

        # Collect previous and current position
        px = self.object1.prev_x
        py = self.object1.prev_y
        x = self.object1.x
        y = self.object1.y

        # If object has not moved, don't do anything
        if px == x and py == y: return

        # Set dx and dy based on what direction the object is moving
        if x > px: dx = 1
        elif x < px: dx = -1
        else: dx = 0

        if y > py: dy = 1
        elif y < py: dy = -1
        else: dy = 0

        # Place object at the previous position
        self.object1.position = px, py

        # Slide the object towards its destination x value

        x_colliding = False

        # Loop only runs if the object is moving in that direction
        # (I'm just using dx as the condition to make sure the
        # object's moving in that direction before looping. I could
        # use a surrounding if statement for that, I guess :| )
        while dx:
            self.object1.x += dx
            x_colliding = self.check_collision()

            # If it collides against something, slide it back, stop
            if x_colliding: 
                self.object1.x -= dx
                break

            # If we are at or past our destination, stop
            if ((dx > 0 and self.object1.x >= x) or
                (dx < 0 and self.object1.x <= x)):
                self.object1.x = x
                break
        
        # Slide the object towards its destination y value
        y_colliding = False
        while dy:
            self.object1.y += dy
            y_colliding = self.check_collision()

            # If it collides against something, slide it back, stop
            if y_colliding: 
                self.object1.y -= dy
                break

            # If we are at or past our destination, stop
            if ((dy > 0 and self.object1.y >= y) or
                (dy < 0 and self.object1.y <= y)):
                self.object1.y = y
                break

        # Moving down or right leaves a one pixel gap between this and
        # other object. This is because SGL converts decimal
        # coordinates to integers with int() when drawing, which
        # always rounds down. We can correct that by rounding up any
        # decimal coordinates if the object is moving in those
        # directions.
        if x_colliding and dx > 0:
            self.object1.x = math.ceil(self.object1.x)

        if y_colliding and dy > 0:
            self.object1.y = math.ceil(self.object1.y)

        # Handle calling the callback.
        if x_colliding or y_colliding:
            if self.callback_args == 0:
                self.do_callback()
            elif self.callback_args == 1:
                direction = []
                if dx < 0 and x_colliding: direction.append("left")
                if dx > 0 and x_colliding: direction.append("right")
                if dy < 0 and y_colliding: direction.append("top")
                if dy > 0 and y_colliding: direction.append("bottom")
                self.do_callback(direction)

class CollisionManager(object):
    def __init__(self):
        self.checkers = []

    def add(self, object1, object2, callback=None):
        self.checkers.append(
            CollisionChecker(object1, object2, callback)
        )
        return self.checkers[-1]

    def add_sliding(self, object1, object2, callback=None):
        self.checkers.append(
            SlidingCollisionChecker(object1, object2, callback)
        )
        return self.checkers[-1]

    def update(self):
        for index, checker in enumerate(self.checkers):
            if checker.to_be_deleted:
                del self.checkers[index]
                continue

            checker.update()

manager = CollisionManager()

def add(object1, object2, callback):
    """ Creates a basic collision checker, which will call a callback
    on every frame two objects overlap.

    Will use a sprite's visible rectangle for collisions, unless a
    Sprite has a custom :any:`Sprite.collision_rect` defined.

    Args:
        object1 (:any:`Sprite`): The first object to
             test. This must be a single sprite---subsprites will not
             be tested for collision.
        object2 (:any:`Sprite`): The second object to
             test. This can be any kind of sprite, and subsprites will
             be tested for collision.
        callback (function): The function to call when the objects
             overlap. This function will have different information
             passed to it depending on how many arguments it accepts.

             * If it accepts no arguments, nothing special will be
               passed to it.
             * If it accepts 1 argument, it will be passed a reference
               to the subsprite of ``object2`` that ``object1``
               collided with on that frame.
             * If it accepts 2 arguments, it will be passed a
               reference to ``object1``, and then the subsprite of
               ``object2`` that ``object1`` collided with on that
               frame.
             * If it accepts 3 arguments, it will be passed all of the
               above, and then a :any:`sgl.lib.Rect.Rect` representing
               the intersected area between the two sprites.

    Returns:
        :any:`CollisionChecker`: An object that can
             be used to pause or stop this collision checking if
             necessary.
"""

    return manager.add(object1, object2, callback)

def add_sliding(object1, object2, callback=None):
    """ Creates a sliding collision checker, which will prevent
    ``object1`` from going inside any of the sprites of ``object2``.
    It is called a "sliding" collision checker because if an object is
    moving diagonally, it will continue to move in the free direction
    even if it collides against a wall. Because the collision
    algorithms are bounding box based, though, diagonal obstacles are
    not supported.

    The sliding collision algorithm checks every pixel position
    between ``object1``'s position on the current and previous frame
    to check collision, so object should not be of the slide through
    each other when they are moving fast or if the frame rate gets
    low. A consequence of this, however, is that this means manual
    position updates are subject to collision checking as well--if you
    want to teleport an object through a wall, you must temporarily
    turn off sliding collision checking for that to work.

    Because of this, it's recommended you always save a reference to
    the :any:`SlidingCollisionChecker` object this function returns.

    Will use a sprite's visible rectangle for collisions, unless a
    Sprite has a custom :any:`Sprite.collision_rect` defined.

    Args:
        object1 (:any:`Sprite`): The first object to
             test. This must be a single sprite---subsprites will not
             be tested for collision.
        object2 (:any:`Sprite`): The second object to
             test. This can be any kind of sprite, and subsprites will
             be tested for collision.
        callback (function): The function to call when the objects
             overlap. This function will have different information
             passed to it depending on how many arguments it accepts.

             * If it accepts no arguments, nothing special will be
               passed to it.
             * If it accepts 1 argument, it will be passed a list of
               strings that can contain various permutations of
               ``"left"``, ``"right"``, ``"top"``, and
               ``"bottom"``. The strings present in this list will
               tell you on what sides ``object1`` was hit before its
               position was corrected by the collision checker.

    Returns:
        :any:`SlidingCollisionChecker`: An object that can
             be used to pause or stop this collision checking if
             necessary.
    """

    return manager.add_sliding(object1, object2, callback)

def update():
    """ Must be called every frame for any of the collision checkers
    to work. 

    Todo:
        * It might be handy to have this and the other continuously
          executing libraries (tween, time...) automatically inject
          themselves into the SGL event loop instead of making the
          user manually call their update functions every
          frame. Currently it is slightly annoying that one has to
          plan out a way to make sure these update functions are
          called *exactly* once every frame in their entire
          program. I'm not sure if handling this automatically is too
          "magic," though... """

    manager.update()

if __name__ == "__main__":
    import random

    sgl.init(640, 480, 1)
    # Enable this to test how it handles frame skipping
    # sgl.set_fps_limit(10)
    # On Windows, you can also move the window while holding down
    # arrow keys to force it to not update for a while
    sgl.set_font(sgl.load_system_font("Arial", 20))

    def make_circle(radius, *color):
        surface = sgl.make_surface(radius, radius)#, 0.25)
        with sgl.with_buffer(surface):
            sgl.no_stroke()
            sgl.set_fill(*color)
            sgl.draw_circle(0, 0, radius, False)

        return surface

    class Enemy(Sprite):
        def __init__(self):
            super(Enemy, self).__init__()

            self.load_surface(make_circle(32, (1.0, 0.5, 0.5)))
            self.collision_rect = (0, 32-8, 32, 8)
            self.anchor = 0, 1.0

    class Obstacle(RectSprite):
        def __init__(self):
            super(RectSprite, self).__init__()

            self.no_stroke = True
            self.fill_color = 0.5

    class Player(Sprite):
        def __init__(self):
            super(Player, self).__init__()

            self.load_surface(make_circle(32, 1.0))
            self.collision_rect = (0, 32-8, 32, 8)
            self.anchor = 0, 1.0
            self.position = 0,32

        def update(self):
            super(Player, self).update()

            v = 200

            if sgl.is_key_pressed(sgl.key.down): 
                self.y += v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.up): 
                self.y -= v * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.right): 
                self.x += v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.left): 
                self.x -= v * sgl.get_dt()

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            self.collision_rectangle = None

            self.persp = PerspectiveGroup()
            self.add(self.persp)

            self.player = Player()
            self.persp.add(self.player)

            self.enemy_group = SpriteGroup()
            self.persp.add(self.enemy_group)

            self.obstacle_group = SpriteGroup()
            self.persp.add(self.obstacle_group)

            self.add_obstacles()
            self.add_enemies()

            # To test exactness of sliding collision, enable this
            # line. If the sliding collision is working correctly,
            # the enemy killing callback should never activate.
            # add_sliding(self.player, self.enemy_group)
            self.enemy_checker = add(self.player, self.enemy_group, self.collision)
            add_sliding(self.player, self.obstacle_group) # , self.print_direction)

        def add_enemies(self):
            for i in range(10):
                enemy = Enemy()

                while True:
                    x = random.randrange(0, self.width)
                    y = random.randrange(0, self.height)
                    enemy.position = x, y

                    for i in self.obstacle_group.subsprites:
                        if enemy.is_colliding_with(i):
                            colliding = True
                            break
                        else:
                            colliding = False

                    if not colliding: break

                self.enemy_group.add(enemy)

        def add_obstacles(self):
            for i in range(10):
                x = random.randrange(0, self.width)
                y = random.randrange(0, self.height)
                width = random.randrange(1, self.width/2)
                height = random.randrange(1, self.height/2)

                while Rect(x, y, width, height).is_in(self.player.rect):
                    x = random.randrange(0, self.width)
                    y = random.randrange(0, self.height)
                    width = random.randrange(1, self.width/2)
                    height = random.randrange(1, self.height/2)

                obstacle = Obstacle()
                obstacle.position = x, y
                obstacle.size = width, height

                self.obstacle_group.add(obstacle)

        def collision(self, o1, o2, rect):
            o2.kill()
            # print "hit", rect.to_tuple()
            # self.collision_rectangle = rect.to_tuple()

        def print_direction(self, direction):
            print direction

        def draw(self):
            super(TestScene, self).draw()

            # if self.collision_rectangle:
            #     sgl.draw_rect(*self.collision_rectangle)

        def update(self):
            super(TestScene, self).update()

            # tween.update(sgl.get_dt())
            # time.update(sgl.get_dt())

            if sgl.on_key_up(sgl.key.space):
                self.obstacle_group.subsprites = []
                self.enemy_group.subsprites = []
                self.add_obstacles()
                self.add_enemies()

            if sgl.on_key_up(sgl.key.d):
                if self.enemy_checker.active:
                    self.enemy_checker.pause()
                else:
                    self.enemy_checker.resume()

            update()

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    app = App(TestScene())

    sgl.run(app.update, app.draw)


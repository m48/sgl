import sgl
from sgl.lib.Sprite import Sprite, AnimatedSprite, RectSprite, Scene
from sgl.lib.Rect import Rect

import inspect

class CollisionChecker(object):
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
        self.check_collision(True)

    def check_collision(self, do_callback=False):
        if self.object2.surface:
            if self.object1.rect.is_in(self.object2.rect):
                if do_callback:
                    self.do_callback(self.object1, self.object2)
                return True
        
        for sprite in self.object2.subsprites:
            if self.object1.rect.is_in(sprite.rect):
                if do_callback:
                    self.do_callback(self.object1, sprite)
                return True

        return False

class SlidingCollisionChecker(CollisionChecker):
    def update(self):
        px = int(self.object1.prev_x)
        py = int(self.object1.prev_y)
        x = int(self.object1.x)
        y = int(self.object1.y)
        orig_x = self.object1.x
        orig_y = self.object1.y

        if px == x and py == y: return

        if x > px: dx = 1
        elif x < px: dx = -1
        else: dx = 0

        if y > py: dy = 1
        elif y < py: dy = -1
        else: dy = 0

        self.object1.position = px, py

        # slide along x
        while True:
            self.object1.x += dx
            x_colliding = self.check_collision()
            if x_colliding: 
                self.object1.x -= dx
                break
            elif self.object1.x == x:
                break

        if not x_colliding:
            self.object1.x = orig_x

        # slide along y
        while True:
            self.object1.y += dy
            y_colliding = self.check_collision()
            if y_colliding: 
                self.object1.y -= dy
                break
            elif self.object1.y == y:
                break

        if not y_colliding:
            self.object1.y = orig_y

        # self.check_collision(True)

class CollisionManager(object):
    def __init__(self):
        self.checkers = []

    def add(self, object1, object2, callback):
        self.checkers.append(
            CollisionChecker(object1, object2, callback)
        )
        return self.checkers[-1]

    def add_sliding(self, object1, object2):
        self.checkers.append(
            SlidingCollisionChecker(object1, object2, None)
        )
        return self.checkers[-1]

    def update(self):
        for checker in self.checkers:
            checker.update()

manager = CollisionManager()

def add(object1, object2, callback):
    manager.add(object1, object2, callback)

def add_sliding(object1, object2):
    manager.add_sliding(object1, object2)

def update():
    manager.update()

if __name__ == "__main__":
    import random

    sgl.init(640, 480, 1)
    sgl.set_font(sgl.load_system_font("Arial", 20))

    def make_circle(radius, *color):
        surface = sgl.make_surface(radius, radius)
        with sgl.with_buffer(surface):
            sgl.no_stroke()
            sgl.set_fill(*color)
            sgl.draw_circle(0, 0, radius, False)

        return surface

    class Enemy(Sprite):
        def __init__(self):
            super(Enemy, self).__init__()

            self.load_surface(make_circle(32, (1.0, 0.5, 0.5)))

    class Obstacle(RectSprite):
        def __init__(self):
            super(RectSprite, self).__init__()

            self.no_stroke = True
            self.fill_color = 0.5

    class Player(Sprite):
        def __init__(self):
            super(Player, self).__init__()

            self.load_surface(make_circle(32, 1.0))

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

            blackness = RectSprite()

            blackness.no_stroke = True
            blackness.fill_color = 0
            blackness.fixed = True
            blackness.fill()

            self.add(blackness)

            self.enemy_group = Sprite()
            self.enemy_group.fill()

            self.add_enemies()

            self.add(self.enemy_group)

            self.obstacle_group = Sprite()
            self.obstacle_group.fill()

            self.add(self.obstacle_group)

            self.player = Player()
            self.add(self.player)

            self.add_obstacles()

            add(self.player, self.enemy_group, self.collision)
            add_sliding(self.player, self.obstacle_group)

        def add_enemies(self):
            for i in range(10):
                x = random.randrange(0, self.width)
                y = random.randrange(0, self.height)

                enemy = Enemy()
                enemy.position = x, y

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
            # self.collision_rectangle = rect.to_tuple()

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
                self.add_obstacles()
                # self.add_enemies()

            update()

            sgl.set_title("FPS: " + str(int(sgl.get_fps())))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)

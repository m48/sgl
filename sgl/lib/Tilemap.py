import sgl
from sgl.lib.Sprite import Sprite, AnimatedSprite, RectSprite, Scene
from sgl.lib.Rect import Rect

class Tilemap(Sprite):
    tiles = []

    map = [[]]
    collision = [[]]
    default_collision = {}

    map_size = 0,0
    tile_size = 0,0

    to_update = []
    
    def __init__(self):
        super(Tilemap, self).__init__()

    def make_blank_map(self, width, height, tile=0):
        self.map = []
        self.collision = []

        for row in range(height):
            self.map.append(
                [tile for i in range(width)]
            )

            self.collision.append(
                [self.default_collision.get(tile, 0) 
                 for i in range(width)]
            )

        self.update_map_sizes()
        self.update_to_update()

    def set_tile(self, tile, x, y):
        self.map[y][x] = tile
        self.collision[y][x] = self.default_collision.get(tile, 0)

    def get_tile(self, x, y):
        return self.map[y][x]

    def set_collision(self, collision, x, y):
        self.collision[y][x] = collision

    def get_collision(self, x, y):
        return self.collision[y][x]

    def update_map_sizes(self):
        height = len(self.map)
        width = len(self.map[0])

        self.map_size = width, height

        self.width = width * self.tile_size[0]
        self.height = height * self.tile_size[1]

    def update_to_update(self):
        self.to_update = [i for i in self.tiles if isinstance(i, Sprite)]

    def coords_at_rect(self, rect, screen=True):
        rect.make_positive()

        x1, y1 = self.coords_at(rect.x, rect.y, screen)
        x2, y2 = self.coords_at(rect.x2, rect.y2, screen)

        return Rect(x1, y1, x2-x1, y2-y1)

    def collision_in(self, rect):
        x1, y1, x2, y2 = self.coords_at_rect(rect).to_tuple(True)

        if not (self.in_bounds(y1, x1) and self.in_bounds(y2, x2)):
            return True

        for row in range(y1, y2+1):
            for column in range(x1, x2+1):
                if self.collision[row][column]:
                    return True

        return False

    def coords_at(self, x, y, screen=True):
        if screen:
            x -= int(self.screen_x)
            y -= int(self.screen_y)
        return x / self.tile_size[0], y / self.tile_size[1]

    def in_bounds(self, row, column):
        if column < 0 or column >= self.map_size[0]:
            return False

        if row < 0 or row >= self.map_size[1]:
            return False

        return True

    def tile_at(self, x, y):
        column, row = self.coords_at(x, y)
        if self.in_bounds(row, column):
            return self.map[row][column]
        else:
            return -1
            
    def collision_at(self, x, y):
        column, row = self.coords_at(x, y)
        if self.in_bounds(row, column):
            return self.collision[row][column]
        else:
            return -1

    def update(self):
        super(Tilemap, self).update()

        for item in self.to_update:
            item.preupdate()
            item.update()

    def draw_self(self):
        start_x = int(self.screen_x)
        start_y = int(self.screen_y)

        first_column, first_row, last_column, last_row = (
            self.coords_at_rect(
                Rect(-start_x, -start_y, self.parent.width, self.parent.height),
                False
            ).to_tuple(True)
        )
        width = -(first_column - last_column)
        height = -(first_row - last_row)

        if first_column > 0:
            start_x += first_column * self.tile_size[0]

        if first_column < 0:
            first_column = 0
            last_column = width

        if last_column >= self.map_size[0]-1:
            last_column = self.map_size[0]-1

        if first_row > 0:
            start_y += first_row * self.tile_size[1]

        if first_row < 0:
            first_row = 0
            last_row = height

        if last_row >= self.map_size[1]-1:
            last_row = self.map_size[1]-1

        x = start_x
        y = start_y

        for row in range(first_row, last_row+1):
            for column in range(first_column, last_column+1):
                tile = self.tiles[self.map[row][column]]
                if isinstance(tile, Sprite):
                    tile.position = x, y
                    tile.update_screen_positions()
                    tile.draw()
                else:
                    sgl.blitf(tile, x, y)

                x += self.tile_size[0]

            y += self.tile_size[1]
            x = start_x

class AnimatedTile(AnimatedSprite):
    def __init__(self, frames, speed, animation=[]):
        super(AnimatedTile, self).__init__()

        self.frames = frames
        self.anim_def_frame_length = speed

        if animation:
            self.animations = {
                "anim": animation
            }
        else:
            self.animations = {
                "anim": range(len(self.frames))
            }

        self.animation = "anim"
        self.play()


if __name__ == "__main__":
    import random

    sgl.init(640, 480, 1)
    sgl.set_font(sgl.load_system_font("Arial", 20))

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            blackness = RectSprite()

            blackness.no_stroke = True
            blackness.fill_color = 0
            blackness.fixed = True
            blackness.fill()

            self.add(blackness)

            self.map = Tilemap()

            grass = sgl.make_surface(32, 32, (0,1.0,0))
            with sgl.with_buffer(grass):
                for i in range(100):
                    x = random.randrange(0,32)
                    y = random.randrange(0,32)
                    sgl.no_stroke()
                    sgl.set_fill(0, 0.50, 0)
                    sgl.draw_rect(x, y, 1, 4)
                    sgl.set_fill(0, 0.75, 0)
                    sgl.draw_rect(x, y, 1, 2)

            wall = sgl.make_surface(32, 32, (0.5,0,0.25))
            with sgl.with_buffer(wall):
                sgl.no_fill()
                sgl.set_stroke(0.25,0,0)
                sgl.draw_rect(0, 0, 32, 32)
            
            self.map.tiles = [
                grass,
                AnimatedTile(
                    [sgl.make_surface(32, 32, (0,0,1.0)),
                     sgl.make_surface(32, 32, (0.25,0.25,1.0)),
                     sgl.make_surface(32, 32, (0.5,0.5,1.0)),
                     sgl.make_surface(32, 32, (0.25,0.25,1.0)),
                    ],
                    0.5,
                ),
                wall,
            ]

            self.map.default_collision = {
                1: 1, 2: 1,
            }

            self.map.tile_size = 32, 32

            width = 30
            height = 20

            self.map.make_blank_map(width, height)

            for i in range(width):
                if i != width/2:
                    self.map.set_tile(2, i, 0)

            for i in range(1,height):
                self.map.set_tile(2, 0, i)
                self.map.set_tile(2, width-1, i)

            for i in range(5,height-5):
                for j in range(3, width-3):
                    self.map.set_tile(1, j, i)

            for i in range(width):
                self.map.set_tile(2, i, height-1)

            self.add(self.map)

            self.selection_box = RectSprite()

            self.selection_box.fill_color = 1.0, 0, 0, 0.5
            self.selection_box.visible = False
            self.selection_box.fixed = True

            self.add(self.selection_box)

        def draw(self):
            super(TestScene, self).draw()

        def update(self):
            super(TestScene, self).update()

            # tween.update(sgl.get_dt())
            # time.update(sgl.get_dt())

            mx, my = sgl.get_mouse_x(), sgl.get_mouse_y()
            x, y = self.map.coords_at(mx, my)
            map_text = "({}, {}) Tile: {} Collision: {}".format(
                x, y,
                self.map.tile_at(mx, my),
                self.map.collision_at(mx, my),
            )

            v = 200

            if sgl.is_key_pressed(sgl.key.down): 
                self.camera.y -= v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.up): 
                self.camera.y += v * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.right): 
                self.camera.x -= v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.left): 
                self.camera.x += v * sgl.get_dt()

            if sgl.on_mouse_down():
                self.selection_box.visible = True
                self.selection_box.x = sgl.get_mouse_x()
                self.selection_box.y = sgl.get_mouse_y()

            if sgl.is_mouse_pressed():
                self.selection_box.width = sgl.get_mouse_x() - self.selection_box.x
                self.selection_box.height = sgl.get_mouse_y() - self.selection_box.y
                if self.map.collision_in(self.selection_box.screen_rect):
                    self.selection_box.fill_color = 1.0, 0, 0, 0.5
                else:
                    self.selection_box.fill_color = 0, 1.0, 0, 0.5

            if sgl.on_mouse_up():
                self.selection_box.visible = False
                
            sgl.set_title(map_text + " FPS: " + str(int(sgl.get_fps())))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)

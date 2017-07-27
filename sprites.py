from palettes import *
from random import randint

class Sprite:
    BLOCK_SIZE = 0
    surface = None

    @staticmethod
    def initialize(block_size, surface):
        Sprite.BLOCK_SIZE = block_size
        Sprite.surface = surface
        ObjectSprite.init()
        AnimationSprite.init()

    @staticmethod
    def render():
        ObjectSprite.render()
        AnimationSprite.render()

    @staticmethod
    def gen(sequence, n):
        length = len(sequence)
        i = 0  # 下标
        _n = 0  # 当前图像已经持续了的时间
        while True:
            yield sequence[i]
            _n += 1
            if _n == n:
                i = (i + 1) % length
                _n = 0


class AnimationSprite(Sprite):
    @staticmethod
    def init():
        ExplosionSprite.init()
        StarSprite.init()

    @staticmethod
    def render():
        ExplosionSprite.render()
        StarSprite.render()


class ExplosionSprite(AnimationSprite):
    image = None
    explosion_sprites = []

    @staticmethod
    def init():
        ExplosionSprite.image = pygame.image.load("explosions.png")

    @staticmethod
    def render():
        for explosion_sprite in ExplosionSprite.explosion_sprites:
            explosion_sprite.renders()

    def __init__(self, object_x, object_y, orders):     # orders的长相应该类似于((1,10), (2,10), (3,10), (4,10), (5,10))这样
        AnimationSprite.__init__(self)
        self.x, self.y = object_x * Sprite.BLOCK_SIZE, object_y * Sprite.BLOCK_SIZE
        self.orders = orders
        self.current = -1
        self.left = 0
        ExplosionSprite.explosion_sprites.append(self)

    def renders(self):
        block_size = Sprite.BLOCK_SIZE
        if self.left == 0:
            self.current += 1
            if self.current == len(self.orders):  # 画完了，可以休息了
                    ExplosionSprite.explosion_sprites.remove(self)
                    return
            self.left = self.orders[self.current][1]    # 没画完，则获取下一帧图像的持续时间
        self.left -= 1
        current_image = self.orders[self.current][0]
        img = ExplosionSprite.image
        x, y = self.x, self.y
        if current_image <= 3:
            size = block_size
            _x, _y = current_image, 0
        else:
            size = 2 * block_size
            _x, _y = 2 * (current_image-4), 1
        x, y = x-size/2, y-size/2
        Sprite.surface.blit(img, (x, y), (_x*block_size, _y*block_size, size, size))


class StarSprite(AnimationSprite):
    image = None
    star_sprites = []

    @staticmethod
    def init():
        StarSprite.image = pygame.image.load("stars.png")

    @staticmethod
    def render():
        for star_sprite in StarSprite.star_sprites:
            star_sprite.renders()

    def __init__(self, object_x, object_y, orders):     # orders的长相应该类似于((1,10), (2,10), (3,10), (4,10), (5,10))这样
        AnimationSprite.__init__(self)
        self.x, self.y = object_x * Sprite.BLOCK_SIZE, object_y * Sprite.BLOCK_SIZE
        self.orders = orders
        self.current = -1
        self.left = 0
        StarSprite.star_sprites.append(self)

    def renders(self):
        block_size = Sprite.BLOCK_SIZE
        if self.left == 0:
            self.current += 1
            if self.current == len(self.orders):  # 画完了，可以休息了
                    StarSprite.star_sprites.remove(self)

                    return
            self.left = self.orders[self.current][1]    # 没画完，则获取下一帧图像的持续时间
        self.left -= 1
        current_image = self.orders[self.current][0]
        img = StarSprite.image
        x, y = self.x, self.y
        _x = current_image
        _y = 0
        size = block_size
        Sprite.surface.blit(img, (x, y), (_x*block_size, _y*block_size, size, size))


class ObjectSprite(Sprite):
    @staticmethod
    def init():
        BlockSprite.init()
        ItemSprite.init()
        TankSprite.init()
        EagleSprite.init()
        MissileSprite.init()

    @staticmethod
    def render():
        BlockSprite.render_low()
        TankSprite.render()
        BlockSprite.render_high()
        BlockSprite.river_keep -= 1
        if BlockSprite.river_keep <= 0:
            BlockSprite.river_keep = 60
            BlockSprite.river_symbol = 1 - BlockSprite.river_symbol
        ItemSprite.render()
        EagleSprite.render()
        MissileSprite.render()

    def __init__(self, object):
        Sprite.__init__(self)
        self.object = object


class BlockSprite(ObjectSprite):
    image = None
    low_block_sprites = []
    high_block_sprites = []
    river_symbol = 0
    river_keep = 0

    @staticmethod
    def init():
        BlockSprite.image = pygame.image.load("blocks.png").convert_alpha()

    @staticmethod
    def render_low():
        for low_block_sprite in BlockSprite.low_block_sprites:
            if low_block_sprite.object is None:
                BlockSprite.low_block_sprites.remove(low_block_sprite)
        for low_block_sprite in BlockSprite.low_block_sprites:
            low_block_sprite.renders()

    @staticmethod
    def render_high():
        for high_block_sprite in BlockSprite.high_block_sprites:
            if high_block_sprite.object is None:
                BlockSprite.high_block_sprites.remove(high_block_sprite)
        for high_block_sprite in BlockSprite.high_block_sprites:
            high_block_sprite.renders()

    def __init__(self, block):
        # block_type : 0, 1, 2, 3, 4, 5 = 空地、砖墙、草丛、冰面、铁墙、河流
        ObjectSprite.__init__(self, block)
        block_type = block.block_type
        self.block_type = block_type
        if block_type in (3, 5):
            BlockSprite.low_block_sprites.append(self)
        elif block_type in (1, 2, 4):
            BlockSprite.high_block_sprites.append(self)

    def renders(self):
        if self.object is None:
            return
        block_type = self.object.block_type
        size = ObjectSprite.BLOCK_SIZE / 2
        img = BlockSprite.image
        x, y = self.object.x*size, self.object.y*size
        _x = block_type - 1 + (BlockSprite.river_symbol if block_type == 5 else 0)
        _y = 0
        if block_type != 1:  # 砖墙
            Sprite.surface.blit(img, (x, y), (_x*size, _y*size, size, size))
        else:
            for i in range(4):
                if self.object.status[i]:
                    _size = size/2
                    __x, __y = i % 2, int(i/2)
                    __x, __y = __x * _size, __y * _size
                    Sprite.surface.blit(img, (x+__x, y+__y), (_x*size+__x, _y*size+__y, _size, _size))


class TankSprite(ObjectSprite):
    image = None
    tank_sprites = []

    @staticmethod
    def init():
        TankSprite.image = pygame.image.load("tanks.png").convert_alpha()

    @staticmethod
    def render():
        for tank_sprite in TankSprite.tank_sprites:
            tank_sprite.renders()

    def __init__(self, tank):
        ObjectSprite.__init__(self, tank)
        self.track_symbol = 0
        self.image_sequence = self.get_image_sequence()
        TankSprite.tank_sprites.append(self)

    def get_image_sequence(self):
        def get_image(tank):
            block_size = Sprite.BLOCK_SIZE
            _y = 4*(1-bool(tank.player_id)) + tank.level if tank.level != 4 else 3
            return TankSprite.image.copy().subsurface((0, _y * block_size, 8 * block_size, block_size))
        sequence = [get_image(self.object)]
        if self.object.player_id:
            n = 1
            change_palette(sequence[0], WHITE, (YELLOW, GREEN)[self.object.player_id - 1])
        elif self.object.is_red:
            n = 10
            sequence.append(get_image(self.object))
            change_palette(sequence[1], WHITE, RED)
        else:
            n = 1
            armor = self.object.armor
            if armor == 1:  # 两层护甲是黄绿色
                change_palette(sequence[0], WHITE, mix(GREEN, YELLOW))
            elif armor == 2:  # 三层护甲是白黄色
                change_palette(sequence[0], WHITE, mix(WHITE, YELLOW))
            elif armor == 3:  # 四层护甲是白绿色
                change_palette(sequence[0], WHITE, mix(WHITE, GREEN))
        return Sprite.gen(sequence, n)

    def renders(self):
        if self.object is None:
            TankSprite.tank_sprites.remove(self)
            return
        block_size = Sprite.BLOCK_SIZE
        tank = self.object
        img = next(self.image_sequence)
        x, y, t = tank.x*block_size, tank.y*block_size, tank.towards
        _x = self.track_symbol + 2*t
        _y = 0
        Sprite.surface.blit(img, (x, y), (_x*block_size, _y*block_size, block_size, block_size))


class EagleSprite(ObjectSprite):
    image = None
    eagle_sprites = []

    @staticmethod
    def init():
        EagleSprite.image = pygame.image.load("eagle.png").convert_alpha()

    @staticmethod
    def render():
        for eagle_sprite in EagleSprite.eagle_sprites:
            eagle_sprite.renders()

    def __init__(self, eagle):
        ObjectSprite.__init__(self, eagle)
        EagleSprite.eagle_sprites.append(self)

    def renders(self):
        size = Sprite.BLOCK_SIZE
        img = EagleSprite.image
        x, y = self.object.x*size, self.object.y*size
        _x, _y = self.object.dead, 0
        Sprite.surface.blit(img, (x, y), (_x*size, _y*size, size, size))


class MissileSprite(ObjectSprite):
    image = None
    missile_sprites = []

    @staticmethod
    def init():
        MissileSprite.image = pygame.image.load("missiles.png").convert_alpha()

    @staticmethod
    def render():
        for missile_sprite in MissileSprite.missile_sprites:
            missile_sprite.renders()

    def __init__(self, missile):
        ObjectSprite.__init__(self, missile)
        MissileSprite.missile_sprites.append(self)

    def renders(self):
        if self.object is None:
            MissileSprite.missile_sprites.remove(self)
            return
        block_size = Sprite.BLOCK_SIZE
        img = MissileSprite.image
        x, y = self.object.x * block_size, self.object.y * block_size
        _x = self.object.towards
        _y = 0
        size = block_size / 4
        Sprite.surface.blit(img, (x, y), (_x*size, _y*size, size, size))


class ItemSprite(ObjectSprite):
    image = None
    item_sprites = []

    @staticmethod
    def init():
        ItemSprite.image = pygame.image.load("items.png").convert_alpha()

    @staticmethod
    def render():
        for item_sprite in ItemSprite.item_sprites:
            item_sprite.renders()

    def __init__(self, item):
        ObjectSprite.__init__(self, item)
        self.keep = 0
        self.symbol = 0
        ItemSprite.item_sprites.append(self)

    def renders(self):
        if self.object is None:
            ItemSprite.item_sprites.remove(self)
            return
        self.keep -= 1
        if self.keep <= 0:
            self.keep = 15
            self.symbol = 1 - self.symbol
        if self.symbol:
            size = Sprite.BLOCK_SIZE
            img = ItemSprite.image
            x , y = self.object.x * size, self.object.y * size
            _x = self.object.item_type
            _y = 0
            Sprite.surface.blit(img, (x, y), (_x*size, _y*size, size, size))

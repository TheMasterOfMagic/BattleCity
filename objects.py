from sprites import *
from random import randint, random


def new_enemy_tank(x=-1, y=-1, ):
    w, h = Object.WIDTH, Object.HEIGHT
    if x == -1:
        x = randint(0, w-1)
    if y == -1:
        y = randint(0, h-1)
    player_id = 0
    is_red = random() <= 0.2
    level = randint(0, 3)
    armor = 3 if level == 3 else randint(0, 2)
    towards, status, keep = 0, 0, 0
    star_orders = tuple((i, 8) for i in (0, 1, 2, 3, 2, 1, )*2+(0,))
    StarSprite(x, y, star_orders)
    delay_task = {'func': Tank, 'time': 104, 'args': (x, y, player_id, is_red, towards, armor, level, status, keep)}
    Object.delay_tasks.append(delay_task)
    #print("new", tank, "at", x, y, "with armor", armor, "level", level)


def new_player_tank(player_id=1):
    global delay_tasks
    x = (4, 8)[player_id-1]
    y = 12
    towards = 0
    is_red = False
    level = 1
    armor = 0
    status, keep = -1, 0
    star_orders = tuple((i, 8) for i in (0, 1, 2, 3, 2, 1, )*2+(0,))
    StarSprite(x, y, star_orders)
    delay_task = {'func': Tank, 'time': 104, 'args': (x, y, player_id, is_red, towards, armor, level, status, keep)}
    Object.delay_tasks.append(delay_task)


def new_eagle(x=-1, y=-1):
    w, h = Object.WIDTH, Object.HEIGHT
    if x == -1:
        x = randint(0, w-1)
    if y == -1:
        y = randint(0, h-1)
    Eagle(x, y)


def del_enemy_tank():
    i = randint(0, len(Tank.tanks)-1)
    Tank.tanks[i].explode()


def new_group_block(block_type=-1, x=-1, y=-1):
    w, h = Object.WIDTH, Object.HEIGHT
    if x == -1:
        x = randint(0, w-1)
    if y == -1:
        y = randint(0, h-1)
    if block_type == -1:
        block_type = randint(0, 5)
    #成组放置
    area = tuple((_x, _y) for _x in (round(2 * x), round(2 * x + 1)) for _y in (round(2 * y), round(2 * y + 1)))
    for _x, _y in area:
        if type(Object.Map[_x][_y]) is not Block:
            block = Block(_x, _y, block_type)
            # block_type : 0, 1, 2, 3, 4, 5 = 空地、砖墙、草丛、冰面、铁墙、河流


def new_block(block_type=-1, x=-1, y=-1):
    w, h = Object.WIDTH, Object.HEIGHT
    if x == -1:
        x = randint(0, w-1)
    if y == -1:
        y = randint(0, h-1)
    if block_type == -1:
        block_type = randint(0, 5)
    Block(x, y, block_type)


def new_item(item_type=-1, x=-1, y=-1):
    w, h = Object.WIDTH, Object.HEIGHT
    if x == -1:
        x = randint(0, w-1)
    if y == -1:
        y = randint(0, h-1)
    if item_type == -1:
        item_type = (1, 2, 3, 5)[randint(0, 3)]  # 0船 1时钟 2手枪 3星星 4钢盔 5炸弹 6铁铲 7坦克
    Item(x, y, item_type)


class Object:
    WIDTH, HEIGHT = 0, 0
    Map = None
    ItemMap = None
    delay_tasks = None
    clock_symbol = -1
    clock_keep = 0
    blade_symbol = -1
    blade_keep = 0
    # sounds
    shoot_wav = None

    @staticmethod
    def initialize(width, height, m, delay_tasks):
        Object.WIDTH, Object.HEIGHT = width, height
        Object.Map = m
        Object.ItemMap = m
        Object.delay_tasks = delay_tasks

    @staticmethod
    def update(m):
        Object.Map = m
        Object.ItemMap = list(list(None for y in range(2 * Object.HEIGHT)) for x in range(2 * Object.WIDTH))
        # 更新clock
        if Object.clock_keep > 0:
            Object.clock_keep -= 1
            if Object.clock_keep == 0:
                Object.clock_symbol = -1
        Eagle.update()
        Block.update()
        Item.update()
        Tank.update()
        Missile.update()  # 在这里做撞击判定

    def __init__(self):
        self.sprite = None


class Block(Object):
    blocks = []

    @staticmethod
    def update():
        for block in Block.blocks:
            block.updates()

    def __init__(self, x, y, block_type):
        # block_type : 0, 1, 2, 3, 4, 5 = 空地、砖墙、草丛、冰面、铁墙、河流
        Object.__init__(self)
        self.x, self.y = x, y
        self.block_type = block_type
        if self.block_type == 1:
            self.status = 1, 1, 1, 1
        self.sprite = BlockSprite(self)
        Block.blocks.append(self)

    def updates(self):
        Object.Map[self.x][self.y] = self

    def movable(self):
        return self.block_type in (0, 2, 3)

    def can_be_hit_by(self, missile):
        if self.block_type == 4:
            return True
        elif self.block_type == 1:
            lu, ru, ld, rd = self.status
            up, right, down, left = lu or ru, ru or rd, ld or rd, lu or ld
            t = missile.towards
            _x, _y = round(2*missile.x), round(2*missile.y)
            horizontal, vertical = _x - self.x, _y - self.y  # horizontal 0左1右 vertical 0上1下
            if t in (0, 2):  # 上 下
                neighbor = Object.Map[self.x+1][self.y] if horizontal else Object.Map[self.x-1][self.y]
                if type(neighbor) is Block and neighbor.block_type == 1:
                    lu, ru, ld, rd = neighbor.status
                    _up, _right, _down, _left = lu or ru, ru or rd, ld or rd, lu or ld
                    if t == 0 and not down and _down or t == 2 and not up and _up:
                        return False
                elif type(neighbor) is Block and neighbor.block_type == 4:
                    if t == 0 and not down or t == 2 and not up:
                        return False
                return right if horizontal else left
            elif t in (1, 3):  # 右 左
                neighbor = Object.Map[self.x][self.y+1] if vertical else Object.Map[self.x][self.y-1]
                if type(neighbor) is Block and neighbor.block_type == 1:
                    lu, ru, ld, rd = neighbor.status
                    _up, _right, _down, _left = lu or ru, ru or rd, ld or rd, lu or ld
                    if t == 1 and not left and _left or t == 3 and not right and _right:
                        return False
                elif type(neighbor) is Block and neighbor.block_type == 4:
                    if t == 1 and not left or t == 3 and not right:
                        return False
                return down if vertical else up

    def get_hit_by(self, missile):
        if self.block_type == 1:  # 砖墙
            if missile.damage == 2:
                self.sprite.object = None
                Block.blocks.remove(self)
            elif missile.damage == 1:
                lu, ru, ld, rd = self.status
                up, right, down, left = lu or ru, ru or rd, ld or rd, lu or ld
                t = missile.towards
                lu *= 0 if t in (1, 2) or t == 0 and not down or t == 3 and not right else 1
                ru *= 0 if t in (2, 3) or t == 1 and not left or t == 0 and not down else 1
                rd *= 0 if t in (3, 0) or t == 2 and not up or t == 1 and not left else 1
                ld *= 0 if t in (0, 1) or t == 3 and not right or t == 2 and not up else 1
                if not (lu or ru or ld or rd):
                    self.sprite.object = None
                    Block.blocks.remove(self)
                    return
                self.status = lu, ru, ld, rd
        elif self.block_type == 4:  # 铁墙
            if missile.damage == 2:
                self.sprite.object = None
                Block.blocks.remove(self)


class Tank(Object):
    tanks = []
    born_tanks = 0
    player_tanks = {}

    @staticmethod
    def update():
        # 先更新所有坦克的位置
        for tank in Tank.tanks:
            x, y = tank.x, tank.y
            for _y in (round(2*y), round(2*y+1)):
                for _x in (round(2*x), round(2*x+1)):
                    Object.Map[_x][_y] = tank
        # 再判断他们是否可以移动
        for tank in Tank.tanks:
            tank.updates()

    def __init__(self, x, y, player_id, is_red, towards, armor, level, status, keep):
        speed = 0.03 if player_id else 0.04 if level == 1 else 0.01 if level == 3 else 0.015
        is_red = False if player_id else is_red
        armor = 1 if player_id else armor
        Object.__init__(self)
        self.x, self.y = x, y
        self.player_id = player_id
        self.is_red = is_red
        self.armor = armor
        self.level = level
        self.towards, self.speed = towards, speed
        self.status, self.keep = status, keep
        self.sprite = TankSprite(self)
        self.stuck_time = 0
        self.missile_left = 1
        self.cool_down = 0
        Tank.tanks.append(self)
        if player_id > 0:
            Tank.player_tanks[player_id] = self
        else:
            self.has_star = False

    def updates(self):
        #处理冷却
        if self.cool_down > 0:
            self.cool_down -= 1
        # 处理冰面（仅针对玩家）
        if self.player_id:
            if not self.movable():
                self.status = -1
                self.keep = 0
            if self.status >= 0:
                self.move(self.status, True)
                self.keep -= 1
                if self.keep == 0:
                    self.status = -1
            return
        #处理移动
        self.move(self.status)
        #处理状态
        min_keep, max_keep = 50, 450
        self.keep -= 1
        if self.keep <= 0:
            self.keep = randint(min_keep, max_keep)
            self.status = 2 if random() <= 0.75 else randint(0, 3)
        if self.movable():
            self.stuck_time = 0
        else:
            self.stuck_time += 1
            if self.stuck_time >= min_keep:
                self.stuck_time = 0
                self.keep = randint(min_keep, max_keep)
                self.status = randint(0, 3)
        #处理开火
        if self.missile_left > 0 and self.cool_down == 0 and random() <= 0.03:
            self.shoot()

    def move(self, direction, force=False):
        if Object.clock_symbol >= 0 and bool(self.player_id) != bool(Object.clock_symbol):
            return
        if self.player_id and self.status >= 0 and not force:
            return
        self.towards = direction
        self.x = round(2*self.x)/2 if direction in (0, 2) else self.x
        self.y = round(2*self.y)/2 if direction in (1, 3) else self.y
        x, y = self.x, self.y
        if self.movable():
            t, v = self.towards, self.speed
            x += v * (1 if t == 1 else -1 if t == 3 else 0)
            y += v * (1 if t == 2 else -1 if t == 0 else 0)
        self.x, self.y = x, y
        to_get = None
        for _y in (round(2*y), round(2*y+1)):
            for _x in (round(2*x), round(2*x+1)):
                unit = Object.Map[_x][_y]
                item_unit = Object.ItemMap[_x][_y]
                if type(unit) is Block and unit.block_type == 3 and self.keep == 0:    # 冰面
                    self.status = self.towards
                    self.keep = 40
                if type(item_unit) is Item:
                    to_get = item_unit
        if to_get is not None:
            to_get.get_by(self)
        self.sprite.track_symbol = 1 - self.sprite.track_symbol

    def movable(self):
        x, y, t = self.x, self.y, self.towards
        d = 0.25
        x += d * (1 if t == 1 else -1 if t == 3 else 0)
        y += d * (1 if t == 2 else -1 if t == 0 else 0)
        if not -d < x < Object.WIDTH-1+d or not -d < y < Object.HEIGHT-1+d:
            return False
        x, y = round(2*x), round(2*y)
        _x, _y = round(2*self.x), round(2*self.y)
        m = Object.Map
        to_judge = set()
        if t == 0 and y != _y:
            to_judge.add(m[x][y])
            to_judge.add(m[x+1][y])
        elif t == 1 and _x != x:
            to_judge.add(m[x+1][y])
            to_judge.add(m[x+1][y+1])
        elif t == 2 and _y != y:
            to_judge.add(m[x][y+1])
            to_judge.add(m[x+1][y+1])
        elif t == 3 and _x != x:
            to_judge.add(m[x][y])
            to_judge.add(m[x][y+1])

        result = True
        for unit in to_judge:
            if type(unit) is Tank:
                result *= unit is self
            elif type(unit) is Block:
                result *= unit.movable()
            elif type(unit) is Eagle:
                result *= 0
        return result

    def shoot(self):
        if not bool(self.player_id) and Object.clock_symbol == 1:
            return
        if self.missile_left > 0 and self.cool_down == 0:
            self.missile_left -= 1
            Missile(self)

    def explode(self):
        self.sprite.object = None
        explosion_sprite_order = tuple((n, 6) for n in (1, 2, 3, 4, 5, 2))
        ExplosionSprite(self.x+0.5, self.y+0.5, explosion_sprite_order)
        Tank.tanks.remove(self)
        if self.player_id:
            delay_task = {'func': new_player_tank(self.player_id), 'args': (), 'time': 40}
            Tank.player_tanks[self.player_id] = None
        else:
            Tank.born_tanks -= 1

    def get_hit_by(self, missile):
        if self.player_id:
            if self.level == 3 and abs(self.towards - missile.towards) == 2:
                self.level -= 1
                self.sprite.image_sequence = self.sprite.get_image_sequence()
            else:
                self.explode()
                return
        elif self.is_red:  # 如果是红坦克，就产生道具，然后以一定几率变成普通坦克
            new_item()  # 在地图上产生新道具
            if random() <= 0.75:
                self.is_red = False
                self.sprite.image_sequence = self.sprite.get_image_sequence()
        else:  # 如果不是红坦克
            if self.armor == 0:
                self.explode()
                return
            else:
                self.armor -= 1
                self.sprite.image_sequence = self.sprite.get_image_sequence()


class Eagle(Object):
    eagles = []

    @staticmethod
    def update():
        for eagle in Eagle.eagles:
            eagle.updates()

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.dead = False
        self.sprite = EagleSprite(self)
        Eagle.eagles.append(self)
        print("new",self,"at",x, y)

    def updates(self):
        x, y = self.x, self.y
        area = set((_x, _y) for _x in (round(2*x), round(2*x+1)) for _y in (round(2*y), round(2*y+1)))
        for _x, _y in area:
            Object.Map[_x][_y] = self

    def get_hit_by(self, missile):
        self.explode()

    def explode(self):
        explosion_sprite_order = tuple((n, 6) for n in (1, 2, 3, 4, 5, 2))
        ExplosionSprite(self.x+0.5, self.y+0.5, explosion_sprite_order)
        self.dead = True


class Missile(Object):
    missiles = []

    @staticmethod
    def update():
        for missile in Missile.missiles:
            missile.updates()
        pass

    def __init__(self, tank):
        Object.__init__(self)
        self.tank = tank
        self.speed = 0.12 if tank.level+bool(tank.player_id) >= 2 else 0.08
        self.damage = 2 if tank.player_id and tank.level == 3 or tank.level == 4 or not tank.player_id and tank.has_star else 1
        self.towards = tank.towards
        t = self.towards
        offset = 0.4
        x, y = tank.x+offset, tank.y+offset
        x += offset * (1 if t == 1 else -1 if t == 3 else 0)
        y += offset * (1 if t == 2 else -1 if t == 0 else 0)
        self.x, self.y = x, y
        self.sprite = MissileSprite(self)
        Missile.missiles.append(self)

    def updates(self):
        w, h = Object.WIDTH, Object.HEIGHT
        t, v = self.towards, self.speed
        if not (0 < self.x < w and 0 < self.y < h):
            self.explode()
            return
        # 判断是否击中什么东西
        x, y = self.x, self.y

        area = set((_x, _y) for _x in (round(2*x-0.5), round(2*x))for _y in (round(2*y-0.5), round(2*y)) if 0 <= _x < 2*w and 0 <= _y < 2*h)
        to_get_hit = set()  # 待处理名单
        for _x, _y in area:
            unit = Object.Map[_x][_y]
            if type(unit) is Missile and bool(unit.tank.player_id) != bool(self.tank.player_id) and (unit.x == self.x or unit.y == self.y or abs(unit.x-self.x)+abs(unit.y-self.y)<0.1):
                to_get_hit.add(Object.Map[_x][_y])  # 将当前目标添加进待处理名单
            elif type(unit) is Tank and bool(unit.player_id) != bool(self.tank.player_id):
                to_get_hit.add(Object.Map[_x][_y])
            elif type(unit) is Block and unit.can_be_hit_by(self):
                to_get_hit.add(Object.Map[_x][_y])
            elif type(unit) is Eagle and not unit.dead:
                to_get_hit.add(Object.Map[_x][_y])
        for object in to_get_hit:  # 挨个处理每个目标
                object.get_hit_by(self)
        if len(to_get_hit) > 0:
            self.explode()  # 处理完后自己爆炸
            return
        else:
            for _x, _y in area:
                if Object.Map[_x][_y] is None:
                    Object.Map[_x][_y] = self
        self.x += v * (1 if t == 1 else -1 if t == 3 else 0)
        self.y += v * (1 if t == 2 else -1 if t == 0 else 0)

    def explode(self):
        self.sprite.object = None
        t, v = self.towards, self.speed
        self.x += v * (1 if t == 1 else -1 if t == 3 else 0)
        self.y += v * (1 if t == 2 else -1 if t == 0 else 0)
        explosion_sprite_order = tuple((n, 4) for n in (1, 2, 3))
        ExplosionSprite(self.x+0.1, self.y+0.1, explosion_sprite_order)
        self.tank.missile_left += 1
        self.tank.cool_down = 12
        Missile.missiles.remove(self)

    def get_hit_by(self, missile):
        self.explode()
        return


class Item(Object):
    items = []

    @staticmethod
    def update():
        for item in Item.items:
            item.updates()

    def __init__(self, x, y, item_type):
        Object.__init__(self)
        self.x, self.y = x, y
        self.item_type = item_type  # 0船 1时钟 2手枪 3星星 4钢盔 5炸弹 6铁铲 7坦克
        self.sprite = ItemSprite(self)
        Item.items.append(self)

    def updates(self):
        x, y = self.x, self.y
        area = set((_x, _y) for _x in (round(2*x), round(2*x+1)) for _y in (round(2*y), round(2*y+1)))
        for _x, _y in area:
            Object.ItemMap[_x][_y] = self

    def get_by(self, tank):
        Item.items.remove(self)
        self.sprite.object = None
        item_type = self.item_type
        # 0船 1时钟 2手枪 3星星 4钢盔 5炸弹 6铁铲 7坦克

        if item_type == 1:
            Object.clock_symbol = bool(tank.player_id)
            Object.clock_keep = 200
        elif item_type == 2:  # 手枪
            tank.level = 3 + (not tank.player_id)
            if not tank.player_id:
                tank.armor = 3
                tank.level = 4
                tank.speed = 0.01
                tank.is_red = False
            tank.sprite.image_sequence = tank.sprite.get_image_sequence()
        elif item_type == 3:  # 星星
            if tank.player_id and tank.level < 3:  # 如果是玩家，而且玩家等级没满，那就升一级
                tank.level += 1
                tank.sprite.image_sequence = tank.sprite.get_image_sequence()
            else:  # 否则如果是敌人，那就让当前所有敌人的子弹升级
                for tank in Tank.tanks:
                    tank.has_star = True
        elif item_type == 5:
            to_explodes = []
            for _tank in Tank.tanks:
                if bool(tank.player_id) != bool(_tank.player_id):
                    to_explodes.insert(0, _tank)
            for to_explode in to_explodes:
                to_explode.explode()
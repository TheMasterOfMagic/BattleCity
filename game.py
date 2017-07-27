from objects import *
import time

def refresh_map():
    global Map, WIDTH, HEIGHT
    Map = list(list(None for y in range(2*HEIGHT))for x in range(2*WIDTH))


def render_map(surface):
    global Map, WIDTH, HEIGHT
    for y in range(2*HEIGHT):
        for x in range(2*WIDTH):
            _value = Map[x][y]
            c = BLUE_COLOR if type(_value) is Missile else DARK_RED_COLOR
            rect = (x*BLOCK_SIZE/2, y*BLOCK_SIZE/2, BLOCK_SIZE/2, BLOCK_SIZE/2)
            width = 0 if type(_value) in (Tank, Block) else 1
            pygame.draw.rect(surface, c, rect, width)


def is_pressing(k):
    return k in pressing_keys and pressing_keys[k] is True


def player_act(player_id, keys):
    if player_id in Tank.player_tanks and Tank.player_tanks[player_id] is not None:
        player = Tank.player_tanks[player_id]
    else:
        return
    up, right, down, left, fire = keys
    if is_pressing(right) != is_pressing(left):
        player.move(1 if is_pressing(right) else 3)
    elif is_pressing(down):
        player.move(2)
    elif is_pressing(up):
        player.move(0)
    if is_pressing(fire):
        player.shoot()


def solve_delay_tasks():
    orders = list(range(len(delay_tasks)-1))
    orders.reverse()
    for i in orders:
        if delay_tasks[i]['time'] == 0:
            del(delay_tasks[i])
    for delay_task in delay_tasks:
        delay_task['time'] -= 1
        if delay_task['time'] == 0:
            func = delay_task['func']
            args = delay_task['args']
            func(*args)


def produce_enemy_tank():
    produce_pos = (0, 0), (6, 0), (12, 0)
    pos_id = 0
    while True:
        x, y = produce_pos[pos_id]
        pos_id += 1
        pos_id %= 3
        Tank.born_tanks += 1
        yield new_enemy_tank(x, y)


def map_initialize():
    new_eagle(6, 12)
    # block_type : 0, 1, 2, 3, 4, 5 = 空地、砖墙、草丛、冰面、铁墙、河流
    empty, brick, jungle, ice, iron, river = 0, 1, 2, 3, 4, 5
    for x, y in tuple((j, 23) for j in range(11, 15))+((11, 24), (11, 25))+((14, 24), (14, 25)):
        new_block(brick, x, y)
    list(new_group_block(brick, x, y) for x in (1, 3, 9, 11) for y in (1, 2, 3, 4, 8, 9, 10, 11))
    list(new_group_block(brick, x, y) for x in (5, 7) for y in (1, 2, 3, 5, 7, 8, 9))
    list(new_group_block(brick, x, y) for x in (2, 3, 9, 10) for y in (6,))
    list(new_group_block(brick, x, y) for x, y in ((0, 6), (6, 7.5), (12, 6)))
    list(new_block(iron, x, y) for x in (0, 1, 24, 25) for y in (13,))
    new_group_block(iron, 6, 2.5)
WIDTH, HEIGHT = 13, 13
BLOCK_SIZE = 32
Map = []
pressing_keys = {}
delay_tasks = []
#初始化
pygame.init()


screen = pygame.display.set_mode((WIDTH*BLOCK_SIZE, HEIGHT*BLOCK_SIZE))
refresh_map()
Object.initialize(WIDTH, HEIGHT, Map, delay_tasks)
Sprite.initialize(BLOCK_SIZE, screen)
map_initialize()
PLAYER1_KEYS = (K_w, K_d, K_s, K_a, K_k)
PLAYER2_KEYS = (K_UP, K_RIGHT, K_DOWN, K_LEFT, K_RETURN)
new_player_tank(1)
new_player_tank(2)
TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER, 10)
producer = produce_enemy_tank()
number_of_tanks = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type in (KEYDOWN, KEYUP):
            key = event.key
            value = event.type == KEYDOWN
            pressing_keys[key] = value
            if event.type == KEYDOWN:
                #如果是想增加实体
                if is_pressing(K_EQUALS):
                    # 1随机敌方坦克，2随机地块
                    if key == K_1:
                        if is_pressing(K_LSHIFT):
                            for i in range(10):
                                new_enemy_tank()
                        else:
                            new_enemy_tank()
                    elif key == K_2:
                        if is_pressing(K_LSHIFT):
                            for i in range(10):
                                new_group_block()
                        else:
                            new_block()
                    elif key == K_3:
                        new_item()
                #如果是删除实体
                if is_pressing(K_MINUS):
                    if key == K_1:
                        del_enemy_tank()
        elif event.type == TIMER:
            if Tank.born_tanks < 6:
                next(producer)
            solve_delay_tasks()
            refresh_map()
            Object.update(Map)
            player_act(1,PLAYER1_KEYS)
            player_act(2,PLAYER2_KEYS)
            "——绘制画面——"
            screen.fill(BLACK_COLOR)
            # render_map(screen)
            Sprite.render()
            pygame.display.update()

import sys
import pygame
from pygame.locals import *


YELLOW = ((248, 216, 120), (255, 160, 68), (172, 124, 1))
GREEN = ((184, 248, 216), (0, 168, 69), (1, 103, 0))
WHITE = ((248, 248, 248), (188, 188, 188), (0, 64, 88))
RED = ((248, 248, 248), (248, 56, 0), (148, 30, 132))
GRAY = ((180, 180, 180), (100, 100, 100), (0, 0, 0))

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
LIGHT_YELLOW_COLOR = (255, 255, 128)
BLUE_COLOR = (0, 0, 255)
DARK_RED_COLOR = (64, 0, 0)


def mix(palette1, palette2):
    def mix_color(color1, color2):
        return tuple((color1[j] + color2[j]) / 2 // 1 for j in range(3))
    return tuple((mix_color(palette1[j], palette2[j])) for j in range(3))


def change_color(surface, color1, color2):
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            temp = surface.get_at((x, y))[:len(color1)]
            if temp == color1:
                surface.set_at((x, y), color2)


def change_palette(surface, palette1, palette2):
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            temp = surface.get_at((x, y))
            temp, alpha = temp[:3], temp[3]
            for j in range(3):
                if temp == palette1[j][:3]:
                    surface.set_at((x, y), palette2[j][:3] + (alpha,))
                    break


def remove_background(surface, _color):
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            temp = surface.get_at((x, y))[:len(_color)]
            if temp == _color:
                surface.set_at((x, y), temp[:3] + (0,))


def fast_palette(mid_color, a=2):
    r, g, b = mid_color
    return (
        (255 - (255 - r) / a, 255 - (255 - g) / a, 255 - (255 - b) / a),
        mid_color, (r / a, g / a, b / a))


if 0:
    pygame.init()
    screen = pygame.display.set_mode((544, 544))
    result = pygame.Surface((52, 52)).convert_alpha()
    image = pygame.image.load("brick_map.jpg").convert()
    for y in range(52):
        for x in range(52):
            color = image.get_at((x,y))
            if color[0] <= 127:
                _color = (0,0,0)
            else:
                _color = (255,255,255)
            image.set_at((x,y),_color)
    result.blit(image,(0,0))
    pygame.image.save(image,"brick_map.png")
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(DARK_RED_COLOR)
        screen.blit(result, (0, 0))
        pygame.display.update()

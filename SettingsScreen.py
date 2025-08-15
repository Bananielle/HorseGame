import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
)

# Colours
GOLD = (255, 184, 28)
PINK = (170, 22, 166)
RED = (255, 0, 0)
WHITE = (255, 255, 255)


class Settings_header(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Settings_header, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/SETTINGS_header.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.surf_center = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            ((self.SCREEN_HEIGHT * 0.15) - self.surf.get_height())
        )

class MenuItem:  # For creating different parameters
    def __init__(self, text):
        self.text = text
        self.location = (400,250)
        self.y = 0
        self.x = 0
        self.font = pygame.font.SysFont('ariel', 26, bold=True, )
        self.surface = self.font.render(self.text, True, WHITE)


class settingMain():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams):
        super(settingMain, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.font = pygame.font.SysFont('ariel', 35, bold=True, )
        self.settingsFont = pygame.font.SysFont('ariel', 26, bold=True, )
        self.text_item = "↑/↓: Select   ←/→: Change   ENTER: Edit/Confirm   SPACE: Back"
        self.instructions = self.settingsFont.render(self.text_item, True, WHITE)
        self.location = (SCREEN_WIDTH / 3, SCREEN_HEIGHT / 4)
        self.gameParams = gameParams
        self.items = []
        self.add_item(MenuItem("Number of trials: "))
        self.starting_position_item_x = (self.SCREEN_WIDTH / 3)
        self.starting_position_item_y = (self.SCREEN_HEIGHT/4)

    def add_item(self, item: MenuItem):
        self.location = self.location

        self.items.append(item)
        return item


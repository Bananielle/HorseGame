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
    def __init__(self, text, value):
        self.text = text
        self.location = 0
        self.font = pygame.font.SysFont('ariel', 26, bold=True, )
        self.surface = self.font.render(self.text, True, WHITE)
        self.value = value

class ToggleItem(MenuItem):
    def __init__(self, text, value=False):
        super().__init__(text, value)
        self.value = bool(value)

    def toggle(self):
        self.value = not self.value
        print(self.value)


class settingMain():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams):
        super(settingMain, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.font = pygame.font.SysFont('ariel', 35, bold=True, )
        self.settingsFont = pygame.font.SysFont('ariel', 26, bold=True, )
        self.text_item = "up/down: Select   left/right: Change   ENTER: Edit/Confirm   SPACE: Back"
        self.instructions = self.settingsFont.render(self.text_item, True, PINK)
        self.location = (SCREEN_WIDTH / 3.7, SCREEN_HEIGHT / 4)
        self.gameParams = gameParams
        self.selected_index = 0  # For which item is selected.
        self.items = []

        # Add new menu items here.
        self.add_item(MenuItem("Number of trials: ",5))
        self.add_item(ToggleItem("Fullscreen","OFF"))
        self.add_item(MenuItem("Task duration (s)",5))

    def add_item(self, item: MenuItem):
        self.location = self.location
        base_x = self.SCREEN_WIDTH / 3.5
        base_y = self.SCREEN_HEIGHT / 3
        offset_y = len(self.items) * 50  # 50 pixels between items
        item.location = (base_x, base_y + offset_y)
        self.items.append(item)
        return item

import pygame,pygame_textinput

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
            ((self.SCREEN_HEIGHT * 0.3) - self.surf.get_height())
        )



class GametimeText():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT,gameParams):
        super(GametimeText, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.font = pygame.font.SysFont('ariel', 35, bold=True, )
        self.settingsFont = pygame.font.SysFont('ariel', 26, bold=True, )
        self.text_gameTime = "Game time (s): "
        self.gameTimeSetting = self.settingsFont.render(self.text_gameTime, True, PINK)
        self.location = (SCREEN_WIDTH/3, SCREEN_HEIGHT/2)
        self.gameParams = gameParams

        self.text_seconds = str(gameParams.currentTime_s)
        self.gameTimeSetting_seconds = self.settingsFont.render(self.text_seconds, True, PINK)
        self.location_seconds = ((SCREEN_WIDTH/2), SCREEN_HEIGHT/2)
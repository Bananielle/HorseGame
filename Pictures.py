import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
)


class PressSpace(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(PressSpace, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/press_space.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.surf_center = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            ((self.SCREEN_HEIGHT * 0.8) - self.surf.get_height())
        )


class AnimalPicture(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT,mounttype):
        super(AnimalPicture, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.mountType = "big" + str(mounttype)
        self.filename = "Resources/" + str(self.mountType) + ".png"
        self.surf = pygame.image.load(self.filename).convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.location = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            (self.SCREEN_HEIGHT * 0.55 - self.surf.get_height())
        )

class TimeOfDayPicture(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT,timeofday):
        super(TimeOfDayPicture, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.timeofday = timeofday
        self.filename = "Resources/" + str(self.timeofday) + ".png"
        self.surf = pygame.image.load(self.filename).convert_alpha()
        self.surf.set_alpha(200)
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.location = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            (self.SCREEN_HEIGHT * 0.55 - self.surf.get_height() - 100)
        )

class Title(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Title, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/Run_and_jump.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.location = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            (self.SCREEN_HEIGHT * 0.3 - self.surf.get_height())
        )


class Settings(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Settings, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/credits.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.location = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            ((self.SCREEN_HEIGHT * 0.95) - self.surf.get_height())
        )

class ReadyToJump():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(ReadyToJump, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/readytojump.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.surf_center = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2.5,
            ((self.SCREEN_HEIGHT * 0.7) - self.surf.get_height())
        )
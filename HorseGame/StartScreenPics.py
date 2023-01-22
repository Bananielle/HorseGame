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


class Fish(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Fish, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/bighorse.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.location = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            (self.SCREEN_HEIGHT * 0.5 - self.surf.get_height())
        )


class FishAdventure(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(FishAdventure, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/Horse-adventure.png").convert_alpha()
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

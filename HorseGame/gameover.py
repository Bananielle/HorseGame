import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
)

class GameOver(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH,SCREEN_HEIGHT):
        super(GameOver, self).__init__()
        self.surf = pygame.image.load("Resources/gameover.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        # Put the center of surf at the center of the display
        self.surf_center = (
            (SCREEN_WIDTH - self.surf.get_width()) / 2,
            (SCREEN_HEIGHT - self.surf.get_height()) / 2.8
        )


class PressSpaceToReplay(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH,SCREEN_HEIGHT):
        super(PressSpaceToReplay, self).__init__()
        self.surf = pygame.image.load("Resources/replay.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        # Put the center of surf at the center of the display
        self.surf_center = (
            (SCREEN_WIDTH - self.surf.get_width()) / 2,
            (SCREEN_HEIGHT - self.surf.get_height()) / 1.5
        )


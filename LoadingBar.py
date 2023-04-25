import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
)

class LoadingBar(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH,SCREEN_HEIGHT,gameParams):
        super(LoadingBar, self).__init__()
        self.gameParams = gameParams
        self.SCREEN_WIDTH =SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load('Resources/loadingbar0.png')
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)   # Set
        self.rect = self.surf.get_rect()

        # Set up the loading bar
        self.bar_width = 127
        self.bar_height = 15
        self.bar_fill = 0
        self.fill_rate = self.bar_width / (gameParams.duration_TASK_s * gameParams.FPS)

        # Put the center of surf at the left corner of the display
        self.surf_center = (30,20)
        self.barfilling_x = 37
        self.barfilling_y = 35


    def resetLoadingBar(self):
        self.bar_fill = 0

    def fillLoadingBar(self):
        if self.bar_fill < self.bar_width:
            self.bar_fill += self.fill_rate
            #print('Fill rate: ', self.fill_rate, ', Bar fill: ', self.bar_fill)

    # def updateImage(self):
    #     self.surf.set_colorkey((0, 0, 0), RLEACCEL)
    #
    # def updateLoadingBar(self, percent):
    #     if percent == 0:
    #         self.surf = pygame.image.load("Resources/loadingbar0.png").convert()
    #     elif percent == 1:
    #         self.surf = pygame.image.load("Resources/loadingbar1.png").convert()
    #     elif percent == 2:
    #         self.surf = pygame.image.load("Resources/loadingbar2.png").convert()
    #     elif percent == 3:
    #         self.surf = pygame.image.load("Resources/loadingbar3.png").convert()
    #     elif percent == 4:
    #         self.surf = pygame.image.load("Resources/loadingbar4.png").convert()
    #     elif percent == 5:
    #         self.surf = pygame.image.load("Resources/loadingbar5.png").convert()
    #
    #     self.updateImage()
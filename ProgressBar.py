import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
)

class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH,SCREEN_HEIGHT,gameParams):
        super(ProgressBar, self).__init__()
        self.gameParams = gameParams
        self.SCREEN_WIDTH =SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load('Resources/loadingbar0.png').convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)   # Set
        self.rect = self.surf.get_rect()


        # Set up the loading bar
        self.bar_width = 130
        self.bar_height = 15
        self.bar_fill = 0
        self.fill_rate_task = self.bar_width / ((gameParams.duration_TASK_s - 0) * gameParams.FPS)
        self.fill_rate_rest = self.bar_width / ((gameParams.duration_REST_s - 0 ) * gameParams.FPS) # -1 because the the rest bar otherwise does't fill up completely...

        # Put the center of surf at the left corner of the display
        #self.surf_center = (30,20)
        self.bar_x = 200
        self.bar_y = SCREEN_HEIGHT/2 + 50
        self.surf_center = (self.bar_x,self.bar_y)
        self.barfilling_x = self.bar_x + 7
        self.barfilling_y = self.bar_y  + 15


    def resetProgressBar(self):
        self.bar_fill = 0

    def fillProgressBar(self, task):
        if self.bar_fill < self.bar_width:
            if task: # If loading bar of task:
                self.bar_fill += self.fill_rate_task
                #print('Fill rate task: ', self.fill_rate_task, ', Bar fill: ', self.bar_fill)
            else: # If loading bar of rest:
                self.bar_fill += self.fill_rate_rest
                # print('Fill rate rest: ', self.fill_rate_rest, ', Bar fill: ', self.bar_fill)
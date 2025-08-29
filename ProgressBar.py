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
        self.bar_width = float(130.0) # Use floats to avoid rounding errors.
        self.bar_height = float(15.0)
        self.bar_fill = float(0.0)

        norm_task = min(1.0, gameParams.get_deltaTime() / gameParams.duration_TASK_s) # Min(a,b) always returns the smallest of the two values. So here a value between 0 and 1.0
        norm_rest = min(1.0, gameParams.get_deltaTime() / gameParams.duration_REST_s)

        self.fill_rate_task = self.bar_width * norm_task
        self.fill_rate_rest = self.bar_width * norm_rest
        self.current_jittered_rest_duration = 1.0 # Will be updated each rest period to take the jitter into account

        self.bar_x = 200
        self.bar_y = SCREEN_HEIGHT/2 + 50
        self.surf_center = (self.bar_x,self.bar_y)
        self.barfilling_x = self.bar_x + 7
        self.barfilling_y = self.bar_y  + 15

    def set_fill_rate_task(self):
        norm_task = min(1.0, self.gameParams.get_deltaTime() / self.gameParams.duration_TASK_s)  # Min(a,b) always returns the smallest of the two values. So here a value between 0 and 1.0
        self.fill_rate_task = self.bar_width * norm_task
       # print("Progress bar task duration: " + str(duration_task_s))

        return  self.fill_rate_task

    def set_fill_rate_rest(self):
        norm_rest = min(1.0, self.gameParams.get_deltaTime() / self.current_jittered_rest_duration)
        self.fill_rate_rest = self.bar_width * norm_rest

       # print("Progress bar rest duration: " + str(self.current_jittered_rest_duration))

        return self.fill_rate_rest

    def resetProgressBar(self,current_jittered_rest_duration):
        self.current_jittered_rest_duration = current_jittered_rest_duration
        self.set_fill_rate_rest() # Set the jittered rest duration for the current rest period

        self.bar_fill = 0

    def fillProgressBar(self, task):
        if self.bar_fill < self.bar_width:
            if task: # If loading bar of task:

                self.bar_fill += self.set_fill_rate_task()
                #print('Fill rate task: ', self.fill_rate_task, ', Bar fill: ', self.bar_fill)
            else: # If loading bar of rest:
                self.bar_fill += self.set_fill_rate_rest()
                # print('Fill rate rest: ', self.fill_rate_rest, ', Bar fill: ', self.bar_fill)

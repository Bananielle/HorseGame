import pygame, random
import math

# Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
)

# Define the enemy object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Coin(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH, SCREEN_HEIGHT,gameParams, startingPosition_y,rank):
        super(Coin, self).__init__()
        self.gameParams = gameParams
        if gameParams.gameDifficulty == 1:
            self.surf = pygame.image.load("Resources/coin_bronze.png").convert_alpha()
        if gameParams.gameDifficulty == 2:
            self.surf = pygame.image.load("Resources/coin_silver.png").convert_alpha()
        if gameParams.gameDifficulty == 3:
            self.surf = pygame.image.load("Resources/coin_gold.png").convert_alpha()

        if gameParams.boringMode:
            self.surf.set_alpha(0)

        self.surf.set_colorkey((0, 0, 0), RLEACCEL)

        self.startingSizeOfCoin = self.surf.get_width()

        self.startingPosition_y = startingPosition_y
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH,startingPosition_y))

        print("T=", self.gameParams.currentTime_s, ": New coin added. Width: ", self.rect.width, " Height: ", self.rect.height)

        self.speed_in_pixels_per_sec = float(200.0 * gameParams.velocity) # Keep it as float (otherwise rounding errors)

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGTH = SCREEN_HEIGHT
        self.movedUpCounter = 0
        self.reachedFinalSpot = False
        self.endSpot = int(self.SCREEN_WIDTH / 1.6)
        self.coinAnimation = 0
        self.rank = rank

    def updateImage(self):
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)


    # Move the enemy based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):

        dt = self.gameParams.deltaTime # Seconds since last frame

        # If coin has not yet reached its endspot
        if self.rect.right > self.endSpot: # If coin has not yet reached its endspot
            self.rect.move_ip(-self.speed_in_pixels_per_sec * dt, 0) # Keep moving to the left
        else: # Otherwise make coinstop on a random spot somewhere on the right side of the screen
            self.reachedFinalSpot = True
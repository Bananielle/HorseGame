import pygame, random
import math

# Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
)

# Define the enemy object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Coin(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH, SCREEN_HEIGHT,gameParams, startingPosition_y):
        super(Coin, self).__init__()
        self.gameParams = gameParams
        self.surf = pygame.image.load("Resources/coin.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)

        self.startingSizeOfCoin = self.surf.get_width()
        # The starting position is randomly generated, as is the speed
        self.startingPosition_y = startingPosition_y
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH,startingPosition_y
            )
        )
        self.speed = 3 * gameParams.velocity * gameParams.deltaTime

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGTH = SCREEN_HEIGHT
        self.movedUpCounter = 0
        self.reachedFinalSpot = False
        self.endSpot = int(self.SCREEN_WIDTH / 1.6)
        self.coinAnimation = 0

    def updatePulsatingCoinAnimation(self):
        if self.coinAnimation == 0:
            self.surf = pygame.image.load("Resources/coin.png").convert()
        elif self.coinAnimation == 1:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_110.png").convert()
        elif self.coinAnimation == 2:
            self.surf = pygame.image.load("Resources/coin.png").convert()
        elif self.coinAnimation == 3:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_95.png").convert()
        elif self.coinAnimation == 4:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_90.png").convert()
        elif self.coinAnimation == 5:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_85.png").convert()
        elif self.coinAnimation == 6:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_80.png").convert()
        elif self.coinAnimation == 7:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_85.png").convert()
        elif self.coinAnimation == 8:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_90.png").convert()
        elif self.coinAnimation == 9:
            self.surf = pygame.image.load("Resources/goldcoin_scaled_95.png").convert()

        self.updateImage()

        self.coinAnimation = self.coinAnimation + 1
        if self.coinAnimation > 9:  # Reset animation
            self.coinAnimation = 0

    def updateImage(self):
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)


    # Move the enemy based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        if self.movedUpCounter < 20:
            self.rect.move_ip(0, -self.speed/5) # Move down
        else:
            self.rect.move_ip(0, self.speed/5) # Move up
            if self.movedUpCounter > 37:
                self.movedUpCounter = 0

        self.movedUpCounter += 1

        #self.updatePulsatingCoinAnimation()


        # If coin has not yet reached its endspot
        if self.rect.right > self.endSpot: # If coin has not yet reached its endspot
            self.rect.move_ip(-self.speed, 0) # Keep moving to the left
        else: # Otherwise make coinstop on a random spot somewhere on the right side of the screen
            self.reachedFinalSpot = True

            #self.pulsate()



    # DOESN"T WORK.
    # def pulsate(self):
    #     maxSize = self.startingSizeOfCoin * 1.1
    #     pulseSpeed = 200 # The higher the number the slower the pulsation
    #
    #     # Calculate the size of the image based on a sine wave
    #     pulsate = (math.sin(pygame.time.get_ticks() / pulseSpeed) + 1) / 2
    #     size = int(pulsate * self.startingSizeOfCoin + maxSize)
    #
    #     self.surf = pygame.transform.scale(self.surf, (size, size))
    #     self.rect = self.surf.get_rect(center=self.rect.center)

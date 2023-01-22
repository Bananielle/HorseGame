import pygame, random

# Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

# Define the enemy object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Coin(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH, SCREEN_HEIGHT,gameParams):
        super(Coin, self).__init__()
        self.gameParams = gameParams
        self.surf = pygame.image.load("Resources/coin.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT - 400),
            )
        )
        self.rect = self.surf.get_rect(
            center=(random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),200))
        self.minSpeed = 1 * gameParams.velocity * gameParams.deltaTime
        self.maxSpeed = 2 * gameParams.velocity * gameParams.deltaTime
        self.speed = random.randint(self.minSpeed, self.maxSpeed)
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGTH = SCREEN_HEIGHT
        self.movedUpCounter = 0
        self.reachedFinalSpot = False
        self.endSpot = random.randint(int(self.SCREEN_WIDTH / 1.5), int(self.SCREEN_WIDTH / 1.5))



    # Move the enemy based on speed
    # Remove it when it passes the left edge of the screen
    def update(self):
        if self.movedUpCounter < 20:
            self.rect.move_ip(0, -self.speed) # Move down
        else:
            self.rect.move_ip(0, self.speed) # Move up
            if self.movedUpCounter > 40:
                self.movedUpCounter = 0

        self.movedUpCounter += 1


        # If jellyfish has not yet reached its endspot
        if self.rect.right > self.endSpot: # If jellyfish has not yet reached its endspot
            self.rect.move_ip(-self.speed, 0) # Keep moving to the left
        else: # Otherwise make jelly fish stop on a random spot somewhere on the right side of the screen
            self.reachedFinalSpot = True


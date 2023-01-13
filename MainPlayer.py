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


# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class MainPlayer(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH, SCREEN_HEIGHT, gameParams, soundSystem):
        super(MainPlayer, self).__init__()
        self.gameParams = gameParams
        self.surf = pygame.image.load("Resources/fish.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.surf = pygame.transform.scale(self.surf, (self.surf.get_width() * 2,self.surf.get_height() * 2)) # But this greatly reduces the image quality...
        self.rect = self.surf.get_rect(center=(
            random.randint(20, 60),
            random.randint(SCREEN_HEIGHT - (int(SCREEN_HEIGHT/2)), SCREEN_HEIGHT - (int(SCREEN_HEIGHT/20)))))
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.soundSystem = soundSystem
        self.playerSpeed = 10


    # Move the sprite based on keypresses
    def update(self, pressed_keys,brainKeyPress, useBCIinput):

        # Make sure player speed is framrate independent
        self.playerSpeed = 15 * self.gameParams.velocity * self.gameParams.deltaTime

        # Also allow for BCI input to make player move up and down if True
        if useBCIinput:
            if brainKeyPress == K_UP:
                self.moveUp()
            if brainKeyPress == K_DOWN:
                self.moveDown()

        # Actual keyboard presses
        if pressed_keys[K_UP]:
            self.moveUp()
        if pressed_keys[K_DOWN]:
            self.moveDown()
        if pressed_keys[K_LEFT]:
            self.moveLeft()
        if pressed_keys[K_RIGHT]:
            self.moveRight()

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.SCREEN_WIDTH:
            self.rect.right = self.SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= self.SCREEN_HEIGHT:
            self.rect.bottom = self.SCREEN_HEIGHT


    def moveUp(self):
        self.rect.move_ip(0, self.playerSpeed * -1)
        #self.soundSystem.playBubbleSound(self.soundSystem.move_up_sound)

    def moveDown(self):
        self.rect.move_ip(0, self.playerSpeed)
       # self.soundSystem.playBubbleSound(self.soundSystem.move_down_sound)

    def moveLeft(self):
        self.rect.move_ip(self.playerSpeed * -1, 0)

    def moveRight(self):
        self.rect.move_ip(self.playerSpeed, 0)
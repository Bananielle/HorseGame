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
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/Horse.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.surf = pygame.transform.scale(self.surf, (self.surf.get_width() * 2,self.surf.get_height() * 2)) # But this greatly reduces the image quality...
        self.lowerLimitYpositionPlayer = self.SCREEN_HEIGHT-75
        self.startingPosition_x = 280
        self.rect = self.surf.get_rect(center=(self.startingPosition_x,self.lowerLimitYpositionPlayer))

        self.soundSystem = soundSystem
        self.playerSpeed = 15
        self.RidingAnimation = 0
        self.JumpingAnimation = 0
        self.HorseIsJumping = False
        self.HorseIsJumpingUp = False
        self.HorseIsJumpingDown = False


    def setPlayerSpeed(self):
        self.playerSpeed = self.playerSpeed * self.gameParams.velocity * self.gameParams.deltaTime

    def updateImage(self):
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.surf = pygame.transform.scale(self.surf, (
        self.surf.get_width() * 2, self.surf.get_height() * 2))  # But this greatly reduces the image quality...

    def changeHorseAnimation(self):
        if self.RidingAnimation == 0:
            self.surf = pygame.image.load("Resources/Walk1.png").convert()
        elif self.RidingAnimation == 1:
            self.surf = pygame.image.load("Resources/Walk2.png").convert()
        elif self.RidingAnimation == 2:
            self.surf = pygame.image.load("Resources/Walk3.png").convert()
        elif self.RidingAnimation == 3:
            self.surf = pygame.image.load("Resources/Walk4.png").convert()
        elif self.RidingAnimation == 4:
            self.surf = pygame.image.load("Resources/Walk5.png").convert()
        elif self.RidingAnimation == 5:
            self.surf = pygame.image.load("Resources/Walk6.png").convert()

        self.updateImage()


        self.RidingAnimation = self.RidingAnimation + 1
        if self.RidingAnimation > 5: # Reset animation
            self.RidingAnimation = 0

    # Move the sprite based on keypresses
    def update(self, pressed_keys,brainKeyPress, useBCIinput):

        # Make sure player speed is framrate independent
        self.playerSpeed = 5 * self.gameParams.velocity * self.gameParams.deltaTime

        # Also allow for BCI input to make player move up and down if True
        if useBCIinput:
            if brainKeyPress == K_UP:
                self.moveUp()
            if brainKeyPress == K_DOWN:
                self.moveDown()


        if pressed_keys[K_UP]:
            self.HorseIsJumping = True
            self.HorseIsJumpingUp = True

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

        # Keep horse on the path
        elif self.rect.bottom >= self.lowerLimitYpositionPlayer+30:
            self.rect.bottom = self.lowerLimitYpositionPlayer+30

    def jumpUp(self):
        if self.RidingAnimation == 0:
            self.moveRight()
            self.surf = pygame.image.load("Resources/Jump1.png").convert()
        elif self.RidingAnimation == 1:
            self.surf = pygame.image.load("Resources/Jump2.png").convert()
        elif self.RidingAnimation == 2:
            self.surf = pygame.image.load("Resources/Jump2.png").convert()
        elif self.RidingAnimation == 3:
            self.surf = pygame.image.load("Resources/Jump3.png").convert()
        elif self.RidingAnimation == 4:
            self.surf = pygame.image.load("Resources/Jump3.png").convert()
        elif self.RidingAnimation == 5:
            self.surf = pygame.image.load("Resources/Jump4.png").convert()
        elif self.RidingAnimation == 6:
            self.surf = pygame.image.load("Resources/Jump5.png").convert()
        elif self.RidingAnimation == 7:
            self.surf = pygame.image.load("Resources/Jump6.png").convert()

        self.updateImage()
        self.moveRight()
        self.moveUp()

        self.RidingAnimation = self.RidingAnimation + 1
        if self.RidingAnimation > 4:  # Reset animation
            self.RidingAnimation = 4

    def jumpDown(self):
        if self.RidingAnimation == 0:
            self.surf = pygame.image.load("Resources/Jump4.png").convert()
        elif self.RidingAnimation == 1:
            self.surf = pygame.image.load("Resources/Jump4.png").convert()
        elif self.RidingAnimation == 2:
            self.surf = pygame.image.load("Resources/Jump5.png").convert()
        elif self.RidingAnimation == 3:
            self.surf = pygame.image.load("Resources/Jump5.png").convert()
        elif self.RidingAnimation == 4:
            self.surf = pygame.image.load("Resources/Jump5.png").convert()
        elif self.RidingAnimation == 5:
            self.surf = pygame.image.load("Resources/Jump6.png").convert()
        elif self.RidingAnimation == 6:
            self.surf = pygame.image.load("Resources/Jump6.png").convert()
        elif self.RidingAnimation == 7:
            self.surf = pygame.image.load("Resources/Jump6.png").convert()

        self.updateImage()
        self.moveRight()
        self.moveDown()


        self.RidingAnimation = self.RidingAnimation + 1
        if self.RidingAnimation > 7:  # Reset animation
            self.RidingAnimation = 0


    def moveUp(self):
        self.rect.move_ip(0, self.playerSpeed * -1)
       # print('Moving up.')
        #self.soundSystem.playBubbleSound(self.soundSystem.move_up_sound)

    def moveDown(self):
        self.rect.move_ip(0, self.playerSpeed)
      #  print('Moving down.')
       # self.soundSystem.playBubbleSound(self.soundSystem.move_down_sound)

    def moveLeft(self):
        self.rect.move_ip(self.playerSpeed * -1, 0)
      #  print('Moving left.')

    def moveRight(self):
        self.rect.move_ip(self.playerSpeed, 0)
        #print('Moving right.')
import pygame, random

# Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class MainPlayer(pygame.sprite.Sprite):
    def __init__(self,SCREEN_WIDTH, SCREEN_HEIGHT, gameParams, soundSystem):
        super(MainPlayer, self).__init__()
        self.borderOfPathForHorse = None
        self.rect = None
        self.startingPosition_x = None
        self.lowerLimitYpositionPlayer = None
        self.imageScaleFactor = None
        self.gameParams = gameParams
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.mount_folder = "Resources/Horse/"
        self.surf = pygame.image.load(self.mount_folder + "Walk1.png").convert()

        self.prepareImage()

        self.lowerLimitYpositionPlayer = self.SCREEN_HEIGHT-(self.SCREEN_HEIGHT/10)
        self.startingPosition_x = 280
        self.rect = self.surf.get_rect(center=(self.startingPosition_x,self.lowerLimitYpositionPlayer))
        self.borderOfPathForHorse = self.lowerLimitYpositionPlayer - 1


        #print(' Width player: ', self.rect.width, ' Height player: ', self.rect.height)

        self.soundSystem = soundSystem
        self.playerSpeed = 25
        self.RidingAnimation = 0
        self.JumpingAnimation = 0
        self.HorseIsJumping = False
        self.HorseIsJumpingUp = False
        self.HorseIsJumpingDown = False

    def prepareImage(self):
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.imageScaleFactor = int(3)
        self.surf = pygame.transform.scale(self.surf, (self.surf.get_width() * self.imageScaleFactor,
                                                       self.surf.get_height() * self.imageScaleFactor))  # But this greatly reduces the image quality...

    def setPlayerSpeed(self):
        self.playerSpeed = self.playerSpeed * self.gameParams.velocity * self.gameParams.deltaTime

    def ridingHorseAnimation(self):
        if self.RidingAnimation == 0:
            self.surf = pygame.image.load(self.mount_folder + "Walk1.png").convert()
        elif self.RidingAnimation == 1:
            self.surf = pygame.image.load(self.mount_folder + "Walk2.png").convert()
        elif self.RidingAnimation == 2:
            self.surf = pygame.image.load(self.mount_folder + "Walk3.png").convert()
        elif self.RidingAnimation == 3:
            self.surf = pygame.image.load(self.mount_folder + "Walk4.png").convert()
        elif self.RidingAnimation == 4:
            self.surf = pygame.image.load(self.mount_folder + "Walk5.png").convert()
        elif self.RidingAnimation == 5:
            self.surf = pygame.image.load(self.mount_folder + "Walk6.png").convert()

        self.prepareImage()


        self.RidingAnimation = self.RidingAnimation + 1
        if self.RidingAnimation > 5: # Reset animation
            self.RidingAnimation = 0

    # Move the sprite based on keypresses
    def update(self, pressed_keys,brainKeyPress, useBCIinput):


        # Also allow for BCI input to make player move up and down if True
        # if useBCIinput:
        #     if brainKeyPress == K_UP:
        #         self.moveUp()
        #     if brainKeyPress == K_DOWN:
        #         self.moveDown()


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
       # elif self.rect.bottom >= self.SCREEN_HEIGHT:
        #    self.rect.bottom = self.SCREEN_HEIGHT

        # Keep horse on the path
        self.keepHorseOnPath()


    def keepHorseOnPath(self):
        if self.rect.bottom >= self.borderOfPathForHorse:
            self.rect.bottom = self.borderOfPathForHorse

    def calculate_jump_position(self, achieved_NF_level):
        #
        # achieved_NF_level = 0.1
        # while achieved_NF_level < 1.1:
        #     jump_position = (0 + self.SCREEN_HEIGHT * 0.2) + (self.SCREEN_HEIGHT * (1 - achieved_NF_level))
        #     print("=====achieved NF level: " + str(achieved_NF_level), ", jump position: " + str(jump_position))
        #     achieved_NF_level += 0.1

        # NF should not be zero or negative
        if achieved_NF_level <= 0:
            print("NF signal is below zero:  ", str(achieved_NF_level))
            achieved_NF_level = 0.2

        # # Calculate the jump position based on the maximum jump height
        # jump_position = (0 + self.SCREEN_HEIGHT * 0.2) + (self.SCREEN_HEIGHT * (1 - achieved_NF_level))
        #
        # # Jump should not be higher than 4/5 of the screen
        # if jump_position < self.SCREEN_HEIGHT * 0.2:
        #     print("Jump position is higher than screen limit:  ", str(jump_position))
        #     jump_position = 0 + self.SCREEN_HEIGHT * 0.2

        jump_lower_bound = 4 / 10  # Lower bound of the jump position range
        jump_upper_bound = 10 / 10  # Upper bound of the jump position range

        # Map the neurofeedback signal to the jump position range
        jump_position = jump_lower_bound + (jump_upper_bound - jump_lower_bound) * achieved_NF_level
        jump_position = int(self.SCREEN_HEIGHT * (1 - jump_position))

        #print("Jump position = ", str(jump_position))


        return jump_position

    def performJumpSequence(self, NF_level_reached):
        if self.HorseIsJumping:
            if self.HorseIsJumpingUp:
                #if self.rect.top > 0 + (self.SCREEN_HEIGHT * 0.4):

                if self.rect.top >  self.calculate_jump_position(NF_level_reached):  # todo: this needs to be dependent on the NF max value (which is a value between 1 and 0)
                    self.jumpUp()
                    #print(T=",self.gameParams.currentTime_s,": Horse is jumping up. NF_level reached: " + str(int(NF_level_reached*100)) + "%, Achieved jump position = " + str(self.calculate_jump_position(NF_level_reached)))

                else:
                    self.HorseIsJumpingUp = False
                    self.HorseIsJumpingDown = True
            if self.HorseIsJumpingDown:
                if self.rect.bottom <= self.borderOfPathForHorse-1:
                    self.jumpDown()
                    #print("Horse is jumping down. Screen height = ", str(self.SCREEN_HEIGHT), "  Horse bottom = ",
                          #str(self.rect.bottom), " borderOfScreenForHorse = ", str(self.borderOfPathForHorse))
                else:
                    self.HorseIsJumpingDown = False
                    self.HorseIsJumping = False

        else:
            self.ridingHorseAnimation()
            if self.rect.centerx > self.startingPosition_x:  # Move horse back to starting point
                #print("T=",self.gameParams.currentTime_s,": Horse is moving back to starting point.")
                self.moveLeft()
                self.moveLeft()

    def jumpUp(self):
        if self.RidingAnimation == 0:
            self.moveRight()
            self.surf = pygame.image.load(self.mount_folder + "Jump1.png").convert()
        elif self.RidingAnimation == 1:
            self.surf = pygame.image.load(self.mount_folder + "Jump2.png").convert()
        elif self.RidingAnimation == 2:
            self.surf = pygame.image.load(self.mount_folder + "Jump2.png").convert()
        elif self.RidingAnimation == 3:
            self.surf = pygame.image.load(self.mount_folder + "Jump3.png").convert()
        elif self.RidingAnimation == 4:
            self.surf = pygame.image.load(self.mount_folder + "Jump3.png").convert()
        elif self.RidingAnimation == 5:
            self.surf = pygame.image.load(self.mount_folder + "Jump4.png").convert()
        elif self.RidingAnimation == 6:
            self.surf = pygame.image.load(self.mount_folder + "Jump5.png").convert()
        elif self.RidingAnimation == 7:
            self.surf = pygame.image.load(self.mount_folder + "Jump6.png").convert()


        self.moveRight()
        self.moveUp()
        self.prepareImage()

        self.RidingAnimation = self.RidingAnimation + 1
        if self.RidingAnimation > 4:  # Reset animation
            self.RidingAnimation = 4

    def jumpDown(self):
        if self.RidingAnimation == 0:
            self.surf = pygame.image.load(self.mount_folder + "Jump4.png").convert()
        elif self.RidingAnimation == 1:
            self.surf = pygame.image.load(self.mount_folder + "Jump4.png").convert()
        elif self.RidingAnimation == 2:
            self.surf = pygame.image.load(self.mount_folder + "Jump5.png").convert()
        elif self.RidingAnimation == 3:
            self.surf = pygame.image.load(self.mount_folder + "Jump5.png").convert()
        elif self.RidingAnimation == 4:
            self.surf = pygame.image.load(self.mount_folder + "Jump5.png").convert()
        elif self.RidingAnimation == 5:
            self.surf = pygame.image.load(self.mount_folder + "Jump6.png").convert()
        elif self.RidingAnimation == 6:
            self.surf = pygame.image.load(self.mount_folder + "Jump6.png").convert()
        elif self.RidingAnimation == 7:
            self.surf = pygame.image.load(self.mount_folder + "Jump6.png").convert()


        self.moveRight()
        self.moveDown()
        self.prepareImage()


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


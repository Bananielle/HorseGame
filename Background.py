import pygame

class MainGame_background(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH,SCREEN_HEIGHT,gameParams):
        super(MainGame_background, self).__init__()
        self.gameParams = gameParams
        self.background_far = pygame.image.load('Resources/country-platform-back.png')
        self.background_far = pygame.transform.scale(self.background_far,
                                                     (SCREEN_WIDTH, self.background_far.get_height() * 3))
        self.bgX_far = 0
        self.bgX2_far = self.background_far.get_width()

        self.background_middle = pygame.image.load('Resources/country-platform-forest.png')
        self.background_middle = pygame.transform.scale(self.background_middle, (SCREEN_WIDTH, SCREEN_HEIGHT - int((SCREEN_HEIGHT/10)))) # Make sure it's an integer because the fucntion doesn't accept floats
        self.bgX_middle = 0
        self.bgX2_middle = self.background_middle.get_width()

        self.background_foreground = pygame.image.load('Resources/country-platform-tiles-example.png')
        self.background_foreground = pygame.transform.scale(self.background_foreground,
                                                            (SCREEN_WIDTH + (int(SCREEN_WIDTH/3)), SCREEN_HEIGHT )) # Make sure this is an integer, because it doesn't accept floats
        self.bgX_foreground = 0
        self.bgX2_foreground = self.background_foreground.get_width()

        self.backgroundSpeed =  gameParams.velocity * gameParams.deltaTime

    def updateBackGrounds(self):
        self.bgX_far, self.bgX2_far = self.move_background(1.4 * self.backgroundSpeed, self.background_far.get_width(), self.bgX_far,
                                                           self.bgX2_far)
        self.bgX_middle, self.bgX2_middle = self.move_background(1.8 * self.backgroundSpeed, self.background_middle.get_width(),
                                                                 self.bgX_middle, self.bgX2_middle)
        self.bgX_foreground, self.bgX2_foreground = self.move_background(2 * self.backgroundSpeed, self.background_foreground.get_width(),
                                                                         self.bgX_foreground,
                                                                         self.bgX2_foreground)

    def move_background(self, speed, backgroundWidth, bgX, bgX2):
        # Make the background move
        bgX -= speed  # Move both background images back
        bgX2 -= speed

        if bgX < (backgroundWidth-3) * -1:  # If our bg is at the -width then reset its position (-3 to make the transition more seemless)
            bgX = backgroundWidth

        if bgX2 < (backgroundWidth-3) * -1:
            bgX2 = backgroundWidth

        return bgX, bgX2

import pygame

class MainGame_background(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH,SCREEN_HEIGHT,gameParams):
        super(MainGame_background, self).__init__()
        self.gameParams = gameParams
        self.SCREEN_WIDTH =SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.background_far = pygame.image.load('Resources/country-platform-back.png')
        self.background_far = pygame.transform.scale(self.background_far,
                                                     (SCREEN_WIDTH, self.background_far.get_height() * 3))
        self.bgX_far = 0 # first image
        self.bgX2_far = self.background_far.get_width() # second image (you're basically glueing both of them together to make a smooth transition

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

        self.transitionToNewBackground = False
        self.pathBackgroundStatus = 0 # 0 = deactivated, 1 = start, 2 = middle, 3 = end

    def startPathBackground(self):
        self.pathBackgroundStatus = 1;
        print('Starting path background.')

    def endPathBackground(self):
        self.pathBackgroundStatus = 3
        print('Ending path background.')

    def changeToPathBackground_start(self):
        self.background_foreground = pygame.image.load('Resources/country_withRocks_start.png')
        self.scaleBackground_foreground()
        self.pathBackgroundStatus = 2
        print('Changing to path background: start.')

    def changeToPathBackground_middle(self):
        self.background_foreground = pygame.image.load('Resources/country_withRocks_middle.png')
        self.scaleBackground_foreground()
        print('Changing to path background: middle.')

    def changeToPathBackground_end(self):
        self.background_foreground = pygame.image.load('Resources/country_withRocks_end.png')
        self.scaleBackground_foreground()
        self.pathBackgroundStatus = 0
        print('Changing to path background: end.')

    def changeToDefaultBackground(self):
        self.background_foreground = pygame.image.load('Resources/country-platform-tiles-example.png')
        self.scaleBackground_foreground()

    def scaleBackground_foreground(self):
        self.background_foreground = pygame.transform.scale(self.background_foreground,
                                                            (self.SCREEN_WIDTH + (int(self.SCREEN_WIDTH / 3)),
                                                             self.SCREEN_HEIGHT))  # Make sure this is an integer, because it doesn't accept floats

    def updateBackGrounds(self):
        self.bgX_far, self.bgX2_far = self.move_background(1.4 * self.backgroundSpeed, self.background_far.get_width(), self.bgX_far,
                                                           self.bgX2_far)
        self.bgX_middle, self.bgX2_middle = self.move_background(1.8 * self.backgroundSpeed, self.background_middle.get_width(),
                                                                 self.bgX_middle, self.bgX2_middle)
        self.bgX_foreground, self.bgX2_foreground = self.move_background(2 * self.backgroundSpeed, self.background_foreground.get_width(),
                                                                         self.bgX_foreground,
                                                                         self.bgX2_foreground)
        print('bgX = ', int(self.bgX_foreground), ' bgX2 = ', int(self.bgX2_foreground))

    def move_background(self, speed, backgroundWidth, bgX, bgX2):
        # Make the background move
        bgX -= speed  # Move both background images back
        bgX2 -= speed


        if bgX < (backgroundWidth-4) * -1:  # If our bg is at the -width then reset its position (-4 to make the transition more seemless)
            bgX = backgroundWidth
            print('Going to background statemachine 1.')
            if self.pathBackgroundStatus == 1:
                self.changeToPathBackground_start()
            elif self.pathBackgroundStatus == 2:
                self.changeToPathBackground_middle()
            elif self.pathBackgroundStatus == 3:
                self.changeToPathBackground_end()
            elif self.pathBackgroundStatus == 0:
                self.changeToDefaultBackground()


        if bgX2 < (backgroundWidth-4) * -1:
            bgX2 = backgroundWidth
            print('Going to background statemachine 2.')




        return bgX, bgX2

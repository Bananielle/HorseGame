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

        self.background_foreground_current = pygame.image.load('Resources/country_default.png')
        self.background_foreground_current = pygame.transform.scale(self.background_foreground_current,
                                                                    (SCREEN_WIDTH + (int(SCREEN_WIDTH/3.2)), SCREEN_HEIGHT -25)) # Make sure this is an integer, because it doesn't accept floats
        self.background_foreground_upcoming = self.background_foreground_current # A copy, but will be used for background transitions

        self.background_path = pygame.image.load('Resources/path_start.png')
        self.background_path = pygame.transform.scale(self.background_path, (self.background_path.get_width(),SCREEN_HEIGHT - 25))  # Make sure this is an integer, because it doesn't accept floats
        self.bgX_path = 0
        self.bgX2_path = self.background_path.get_width() -10

        self.bgX_foreground = 0
        self.bgX2_foreground = self.background_foreground_upcoming.get_width()-100

        self.backgroundSpeed =  gameParams.velocity * gameParams.deltaTime +1

        self.transitionToNewBackground = False
        self.pathBackgroundStatus = 0 # 0 = deactivated, 1 = start, 2 = middle, 3 = end
        self.foregroundNrThatIsActive = 1
        self.transition_bgX = False
        self.transition_bgX2 = False

        self.backgroundQueue = list()

        # Create a semi-transparent grey surface to overlay on top of the background
        WINDOWSIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
        print('Window size: ', WINDOWSIZE)
        transparency = 90
        self.overlay_greysurface = pygame.Surface(WINDOWSIZE)
        self.overlay_greysurface.set_alpha(transparency)
        self.overlay_greysurface.fill((transparency, transparency, transparency))

    def startPathBackground(self):
        self.pathBackgroundStatus = 1;
        #print('Starting path background.')

    def endPathBackground(self):
        self.pathBackgroundStatus = 3
        #print('Ending path background.')

    def changeToPathBackground_start(self):
        #self.background_foreground_upcoming = pygame.image.load('Resources/country_withRocks_start.png')
        temp = pygame.image.load('Resources/country_withRocks_start.png')
        #self.scaleBackground_foreground()
        self.backgroundQueue.append(temp)
        self.pathBackgroundStatus = 2
        #print('Changing to path background: start.')

    def changeToPathBackground_middle(self):
        #self.background_foreground_upcoming = pygame.image.load('Resources/country_withRocks_middle.png')
        #elf.scaleBackground_foreground()
        temp = pygame.image.load('Resources/country_withRocks_middle.png')
        self.backgroundQueue.append(temp)
        self.pathBackgroundStatus = 2 # Keep in this loop until instructed otherwise

       # print('Changing to path background: middle.')

    def changeToPathBackground_end(self):
        #self.background_foreground_upcoming = pygame.image.load('Resources/country_withRocks_end.png')
        #self.scaleBackground_foreground()

        temp = pygame.image.load('Resources/country_withRocks_end.png')
        self.backgroundQueue.append(temp)
        self.pathBackgroundStatus = 0
       # print('Changing to path background: end.')

    def changeToDefaultBackground(self):
        #self.background_foreground_upcoming = pygame.image.load('Resources/country-platform-tiles-example.png')
        #self.scaleBackground_foreground()
        temp = pygame.image.load('Resources/country_default.png')
        self.backgroundQueue.append(temp)
        #print('Changing to default background.')


    def updateAllBackGrounds(self):
        isForeground = False
        self.bgX_far, self.bgX2_far = self.move_background(isForeground,1.4 * self.backgroundSpeed, self.background_far.get_width(), self.bgX_far,
                                                           self.bgX2_far)
        self.bgX_middle, self.bgX2_middle = self.move_background(isForeground,1.8 * self.backgroundSpeed, self.background_middle.get_width(),
                                                                 self.bgX_middle, self.bgX2_middle)

        self.move_foregrounds()
        self.move_paths()

        #print('bgX = ', int(self.bgX_foreground), ' bgX2 = ', int(self.bgX2_foreground))

    def move_foregrounds(self):
        isForeground = True
        self.bgX_foreground, self.bgX2_foreground = self.move_background(isForeground,2 * self.backgroundSpeed,
                                                                         self.background_foreground_upcoming.get_width(),
                                                                         self.bgX_foreground,
                                                                         self.bgX2_foreground)

    def move_paths(self):
        isForeground = True
        self.bgX_path, self.bgX2_path = self.move_background(isForeground, 2 * self.backgroundSpeed,
                                                                         self.background_path.get_width(),
                                                                         self.bgX_path,
                                                                         self.bgX2_path)


    def move_background(self,isForeground, speed, backgroundWidth, bgX, bgX2):
        # Make the background move
        bgX -= speed  # Move both background images back
        bgX2 -= speed


        if isForeground: # Th
            # Current background image
            if bgX < (backgroundWidth-6) * -1:  # If our bg is at the -width then reset its position (-4 to make the transition more seemless)
               # print('bgX = ', str(bgX), ' < ',str((backgroundWidth-4) * -1))
                bgX = backgroundWidth-200
               # print('bgX = ', str(bgX),'. Going to background statemachine 1. BackgroundStatus = ', str(self.pathBackgroundStatus))
                self.transition_bgX = True
                self.changeBackground_current()

            # Upcoming background image
            if bgX2 < (backgroundWidth-6) * -1:
            #    print('bgX2 = ', str(bgX2), ' < ', str((backgroundWidth - 4) * -1))
                bgX2 = backgroundWidth-210
                self.transition_bgX2 = True
             #   print('bgX2 = ', str(bgX2),'. Going to background statemachine 2. BackgroundStatus = ', str(self.pathBackgroundStatus))
                self.changeBackground_upcoming()

        else: # This is only for the backgrounds further away. They don't change.
            if bgX < (backgroundWidth - 15) * -1:  # If our bg is at the -width then reset its position (-4 to make the transition more seemless)
                bgX = backgroundWidth
            if bgX2 < (backgroundWidth - 15) * -1:  # If our bg is at the -width then reset its position (-4 to make the transition more seemless)
                bgX2 = backgroundWidth

        return bgX, bgX2

    def changeBackground_upcoming(self):
            if self.pathBackgroundStatus == 1:
                self.changeToPathBackground_start() # Immediately add start and middle to the list
                #self.changeToPathBackground_middle()
            elif self.pathBackgroundStatus == 2:
                self.changeToPathBackground_middle()
            elif self.pathBackgroundStatus == 3:
                self.changeToPathBackground_end()
            elif self.pathBackgroundStatus == 0:
                self.changeToDefaultBackground()

            # Get upcoming background from the queue
            firstItemOnList = self.backgroundQueue[0]

            # Put upcoming background to upcoming one and scale
            self.background_foreground_upcoming = firstItemOnList
            self.background_foreground_upcoming = pygame.transform.scale(self.background_foreground_upcoming,
                                                                        (self.SCREEN_WIDTH + (
                                                                            int(self.SCREEN_WIDTH / 3.2)),
                                                                         self.SCREEN_HEIGHT-25))  # Make sure this is an integer, because it doesn't accept floats

            self.backgroundQueue.remove(firstItemOnList)  # Remove background from queue
            #print("Background queue: " + self.backgroundQueue)

    def changeBackground_current(self):
            if self.pathBackgroundStatus == 1:
                self.changeToPathBackground_start() # Immediately add start and middle to the list
                #self.changeToPathBackground_middle()
            elif self.pathBackgroundStatus == 2:
                self.changeToPathBackground_middle()
            elif self.pathBackgroundStatus == 3:
                self.changeToPathBackground_end()
            elif self.pathBackgroundStatus == 0:
                self.changeToDefaultBackground()

            # Get upcoming background from the queue
            firstItemOnList = self.backgroundQueue[0]

            # Put upcoming background to current one and scale
            self.background_foreground_current = firstItemOnList
            self.background_foreground_current = pygame.transform.scale(self.background_foreground_current,
                                                                        (self.SCREEN_WIDTH + (
                                                                            int(self.SCREEN_WIDTH / 3.2)),
                                                                         self.SCREEN_HEIGHT-25))  # Make sure this is an integer, because it doesn't accept floats

            self.backgroundQueue.remove(firstItemOnList)  # Remove background from queue
            #print("Background queue: " + self.backgroundQueue)


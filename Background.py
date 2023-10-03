import pygame

class MainGame_background(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH,SCREEN_HEIGHT,gameParams, mounttype):
        super(MainGame_background, self).__init__()
        self.gameParams = gameParams
        self.SCREEN_WIDTH =SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.MountType = mounttype

        # Let the mount type background be determined by based on what the player choose in the starting screen.
        if self.MountType == 'horse':
            self.folder = "Resources/Horse/"
        elif self.MountType == 'turtle':
            self.folder = "Resources/Turtle/"
        elif self.MountType == 'camel':
            self.folder = "Resources/Camel/"
        elif self.MountType == 'bear':
            self.folder = "Resources/Bear/"

        class BackgroundTemplate:
            def __init__(self, imagePath):
                self.image = pygame.image.load(imagePath)
                self.bgX = 0 # First image
                self.bgX2 = self.image.get_width() # second image (you're basically glueing both of them together to make a smooth transition
                self.width = self.image.get_width()
                print("Image " +imagePath + ": width: ", self.width)
            def scaleImage(self,x,y):
                self.image = pygame.transform.scale(self.image, (x, y))
                self.width = self.image.get_width() # Update width
                self.bgX2 = self.width # Update bgX2

            def moveBackground(self,speed,a,overlapBuffer):

                self.bgX -= speed  # Move both background images back
                self.bgX2 -= speed

                if self.bgX < (self.width - a) * -1:  # If our bg is at the -width then reset its position (-a to make the transition more seemless)
                   # print("bgX = ", str(self.bgX), " < ", str((self.width - a) * -1) + " . Reset background.")
                    self.bgX = self.width - overlapBuffer

                if self.bgX2 < (self.width - a) * -1:  # If our bg is at the -width then reset its position (-a to make the transition more seemless)
                   # print("bgX2 = ", str(self.bgX2), " < ", str((self.width - a) * -1) + " . Reset background.")
                    self.bgX2 = self.width - overlapBuffer


        # FAR BACKGROUND
        self.background_far = BackgroundTemplate(self.folder + 'background.png')
        self.background_far.scaleImage(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.background_far.bgX2 = self.background_far.width - 10  # Otherwise there is a gap between the two images

        # MIDDLE BACKGROUND
        self.background_middle = BackgroundTemplate(self.folder + 'middleground.png')
        self.background_middle.scaleImage(SCREEN_WIDTH, SCREEN_HEIGHT - int((SCREEN_HEIGHT/10))) # Make sure it's an integer because the fucntion doesn't accept floats

        # FOREGROUND
        self.background_foreground = BackgroundTemplate(self.folder + 'foreground.png',)
        self.background_foreground.scaleImage(SCREEN_WIDTH + (int(SCREEN_WIDTH / 3.2)), SCREEN_HEIGHT - 0) # Make sure this is an integer, because it doesn't accept floats
        self.background_foreground.bgX2 = self.background_foreground.width - 40 # Otherwise there is a gap between the two images

        # PATH BACKGROUND
        self.background_path = pygame.image.load('Resources/path_start.png')
        self.background_path = pygame.transform.scale(self.background_path, (self.background_path.get_width(),SCREEN_HEIGHT - 25))  # Make sure this is an integer, because it doesn't accept floats
        self.bgX_path = 0
        self.bgX2_path = self.background_path.get_width()


        # OTHER
        self.backgroundSpeed =  gameParams.velocity * gameParams.deltaTime + 2
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


    def updateAllBackGrounds(self):

        self.background_far.moveBackground(speed=1.4 * self.backgroundSpeed,a=6,overlapBuffer=6)# Use 5 because otherwise there is a gap between the two images
        self.background_middle.moveBackground(speed=1.8 * self.backgroundSpeed, a=6,overlapBuffer=0)
        self.background_foreground.moveBackground(speed=2 * self.backgroundSpeed, a=1,overlapBuffer=100) # Use 100 because otherwise there is a gap between the two images

        #print('bgX = ', int(self.bgX_foreground), ' bgX2 = ', int(self.bgX2_foreground))






    # PATH BACKGROUND FUNCTIONS

    def move_paths(self):
        isForeground = True
        self.bgX_path, self.bgX2_path = self.move_background(isForeground, 2 * self.backgroundSpeed,
                                                             self.background_path.get_width(),
                                                             self.bgX_path,
                                                             self.bgX2_path)

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
            self.background_foreground = firstItemOnList
            self.background_foreground = pygame.transform.scale(self.background_foreground,
                                                                (self.SCREEN_WIDTH + (
                                                                            int(self.SCREEN_WIDTH / 3.2)),
                                                                         self.SCREEN_HEIGHT-0))  # Make sure this is an integer, because it doesn't accept floats

            self.backgroundQueue.remove(firstItemOnList)  # Remove background from queue
            #print("Background queue: " + self.backgroundQueue)

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
        temp = pygame.image.load(self.folder + 'foreground.png')
        self.backgroundQueue.append(temp)
        #print('Changing to default background.')

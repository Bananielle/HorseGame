import pygame

class MainGame_background(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH,SCREEN_HEIGHT,gameParams, mounttype):
        super(MainGame_background, self).__init__()
        self.gameParams = gameParams
        self.SCREEN_WIDTH =SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.MountType = mounttype

        print ("MainGame_background created. Mount type = ", self.MountType)

        # Let the mount type background be determined by based on what the player choose in the starting screen.
        if self.MountType == 'horse':
            self.folder = "Resources/Horse/"
        elif self.MountType == 'turtle':
            self.folder = "Resources/Turtle/"
        elif self.MountType == 'camel':
            self.folder = "Resources/Camel/"
        elif self.MountType == 'bear':
            self.folder = "Resources/Bear/"

        class BackgroundTemplate (pygame.sprite.Sprite):
            def __init__(self, imagePath, scalefactor_x, scalefactor_y):
                super(BackgroundTemplate, self).__init__()
                self.surf = pygame.image.load(imagePath)
                self.surf = pygame.transform.scale(self.surf, (scalefactor_x, scalefactor_y))
                #print("Scaling image to ", scalefactor_x, scalefactor_y)
                self.rect = self.surf.get_rect()
                self.bgX = 0 # First image
                self.bgX2 = self.surf.get_width() # second image (you're basically glueing both of them together to make a smooth transition
                self.width = self.surf.get_width()
                self.height = self.surf.get_height()
                print("Image " +imagePath + ": width: ", self.width, " height: ", self.surf.get_height())


            def moveBackground(self,speed,a,overlapBuffer):

                self.bgX -= speed  # Move both background images back
                self.bgX2 -= speed

                if self.bgX < (self.width - a) * -1:  # If our bg is at the -width then reset its position (-a to make the transition more seemless)
                   self.bgX = self.width - overlapBuffer

                if self.bgX2 < (self.width - a) * -1:  # If our bg is at the -width then reset its position (-a to make the transition more seemless)
                   self.bgX2 = self.width - overlapBuffer


        # DEFAULT FAR BACKGROUND
        self.background_far = BackgroundTemplate(self.folder + 'background.png',SCREEN_WIDTH,SCREEN_HEIGHT)
        self.background_far.bgX2 = self.background_far.width - 10  # Otherwise there is a gap between the two images

        # DEFAULT MIDDLE BACKGROUND
        self.background_middle = BackgroundTemplate(self.folder + 'middleground.png',SCREEN_WIDTH,SCREEN_HEIGHT - int((SCREEN_HEIGHT/10)))# Make sure it's an integer because the fucntion doesn't accept floats

        # DEFAULT FOREGROUND
        self.background_foreground = BackgroundTemplate(self.folder + 'foreground.png',SCREEN_WIDTH + (int(SCREEN_WIDTH / 3.2)), SCREEN_HEIGHT - 0) # Make sure this is an integer, because it doesn't accept floats

        self.background_foreground.bgX2 = self.background_foreground.width - 40 # Otherwise there is a gap between the two images

        # OTHER
        self.backgroundSpeed =  gameParams.velocity * gameParams.deltaTime + 2
        self.defaultBackgroundList =  [self.background_far, self.background_middle, self.background_foreground]

        # FANCY BACKGROUNDs]
        self.timeOfDay = 'Day'
        self.timeOfDay = 'Night'

        x = 2.2  # Scale factor for the background images
        y = 1.7

        self.folder = "Resources/" + mounttype.capitalize() + "/" + self.timeOfDay + "/"
        print("Using folder: ", self.folder)

        # All backgrounds have at least 6 layers
        self.background1 = BackgroundTemplate(self.folder + 'Layer 01.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*(y)) # Don't scale the sky background
        self.background2 = BackgroundTemplate(self.folder + 'Layer 02.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y)
        self.background3 = BackgroundTemplate(self.folder + 'Layer 03.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y)
        self.background4 = BackgroundTemplate(self.folder + 'Layer 04.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y)
        self.background5 = BackgroundTemplate(self.folder + 'Layer 05.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y)
        self.background6 = BackgroundTemplate(self.folder + 'Layer 06.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y)

        if mounttype is not 'turtle':
            self.background7 = BackgroundTemplate(self.folder + 'Layer 07.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*(y))
            self.background8 = BackgroundTemplate(self.folder + 'Layer 08.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y)# Layer where the animal walks on.
            self.background9 = BackgroundTemplate(self.folder + 'Layer 09.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y) # Layer where the animal walks on.

        if self.folder == "Resources/Horse/Day/" or self.folder == "Resources/Bear/Night/":
            self.background10 = BackgroundTemplate(self.folder + 'Layer 10.png',SCREEN_WIDTH*x,SCREEN_HEIGHT*y) # Layer where the animal walks on.

        if self.folder == "Resources/Horse/Night/":
            self.background11 = BackgroundTemplate(self.folder + 'Layer 11.png', SCREEN_WIDTH * x,SCREEN_HEIGHT * y)  # Layer where the animal walks on.


        # Create a semi-transparent grey surface to overlay on top of the background
        WINDOWSIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
        print('Window size: ', WINDOWSIZE)
        transparency = 90
        self.overlay_greysurface = pygame.Surface(WINDOWSIZE)
        self.overlay_greysurface.set_alpha(transparency)
        self.overlay_greysurface.fill((transparency, transparency, transparency))


    def updateAllBackGrounds(self):

        if self.gameParams.useFancyBackground:
            self.background1.moveBackground(speed=0.1 * self.backgroundSpeed,a=6,overlapBuffer=6)
            self.background2.moveBackground(speed=0.5 * self.backgroundSpeed, a=6, overlapBuffer=6)
            self.background3.moveBackground(speed=0.6 * self.backgroundSpeed, a=6, overlapBuffer=6)

            if self.MountType is 'turtle': # Let this layer move faster, because it is the foreground layer.
                self.background4.moveBackground(speed=2 * self.backgroundSpeed, a=6, overlapBuffer=6)
                self.background5.moveBackground(speed=3 * self.backgroundSpeed, a=6, overlapBuffer=6)
                self.background6.moveBackground(speed=4 * self.backgroundSpeed, a=6, overlapBuffer=6)
            else:
                self.background4.moveBackground(speed=0.7 * self.backgroundSpeed, a=6, overlapBuffer=6)
                self.background5.moveBackground(speed=1.2 * self.backgroundSpeed, a=6, overlapBuffer=6)
                self.background6.moveBackground(speed=1.4 * self.backgroundSpeed, a=6, overlapBuffer=6)

            if self.MountType is not 'turtle':
                self.background7.moveBackground(speed=1.5 * self.backgroundSpeed, a=6, overlapBuffer=6)
                self.background8.moveBackground(speed=1.6 * self.backgroundSpeed, a=6, overlapBuffer=6)
                self.background9.moveBackground(speed=3 * self.backgroundSpeed, a=6, overlapBuffer=6)
            if self.folder == "Resources/Horse/Day/" or self.folder == "Resources/Bear/Night/":
                self.background10.moveBackground(speed=4 * self.backgroundSpeed, a=6, overlapBuffer=6)
            if self.folder == "Resources/Horse/Night/":
                self.background11.moveBackground(speed=4 * self.backgroundSpeed, a=6, overlapBuffer=6)
        else:
            self.background_far.moveBackground(speed=3 * self.backgroundSpeed,a=6,overlapBuffer=6)# Use 5 because otherwise there is a gap between the two images
            self.background_middle.moveBackground(speed=3.5 * self.backgroundSpeed, a=6,overlapBuffer=0)
            self.background_foreground.moveBackground(speed=4 * self.backgroundSpeed, a=1,overlapBuffer=100) # Use 100 because otherwise there is a gap between the two images

        #print('bgX = ', int(self.bgX_foreground), ' bgX2 = ', int(self.bgX2_foreground))


import pygame

# Colours

GOLD = (255, 184, 28)
PINK = (170, 22, 166)

class GameParameters():
    def __init__(self,player,SCREEN_WIDTH,SCREEN_HEIGHT,):

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        # Adjustable parameters
        self.gameTimeCounter_s = 0 # How long you want to one game run to last (in seconds)
        self.durationGame_s = 40
        self.useBCIinput = True # If true, then player will be controlled by BCI input next to keyboard presses
        self.FPS = 60 # Frame rate. # Defines how often the the while loop is run through. E.g., an FPS of 60 will go through the while loop 60 times per second).
        # Create custom events for adding a new sprites (sharks and jellyfish)

        self.ADDCOIN = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADDCOIN, 500) # Define how quickly new jellyfish are added (e.g., every 4000ms)
        self.NrOfCoins = 1

        self.HORSEANIMATION = pygame.USEREVENT + 3
        pygame.time.set_timer(self.HORSEANIMATION, 100)  # Define how quickly new jellyfish are added (e.g., every 4000ms)

        self.NEWTASKTRIAL = pygame.USEREVENT + 4
        pygame.time.set_timer(self.NEWTASKTRIAL,10000)

        self.POST_TASK_REST = pygame.USEREVENT + 5
        pygame.time.set_timer(self.POST_TASK_REST, 15000) # 5s after task

        self.NEW_COINS_DURING_REST = pygame.USEREVENT + 6
        pygame.time.set_timer(self.POST_TASK_REST, 25000)  # 10s after task


        # Time
        self.velocity = 1 # Determines general speed of all sprites (to ensure frame-rate independence)
        self.deltaTime = 1

        self.counterText = str('-').rjust(3)
        self.mainFont = pygame.font.SysFont('herculanum', 35, bold=True, )
        self.jellyfishCollectedFont = pygame.font.SysFont('herculanum', 45, bold=True, )
        self.gameTimeCounterText = self.mainFont.render(self.counterText, True, PINK)

        self.nrCoinsCollected = 0
        self.nrCoinsCollectedText = self.mainFont.render(self.counterText, True, GOLD)

        self.scoreSaved = False

        # Create the sprites
        self.player = player
        print('Player created')
        self.sharks = pygame.sprite.Group()  # - sharks is used for collision detection and position updates
        self.coin = pygame.sprite.Group()  # - enemies is used for collision detection and position updates
        self.messages = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()  # - all_sprites isused for rendering
        self.all_sprites.add(self.player)

        # Counter ( for countin down the seconds until game over)
        self.SECOND_HAS_PASSED = pygame.USEREVENT
        pygame.time.set_timer(self.SECOND_HAS_PASSED, 1000) # in ms
        self.startingPosition_y = (SCREEN_HEIGHT - 350)

        self.task = False
        self.rest = False

    def resetCoinStartingPosition(self):
        self.startingPosition_y = (self.SCREEN_HEIGHT - 300)

    def reset(self):
        self.all_sprites.empty()

    def run(self):
        print('test')




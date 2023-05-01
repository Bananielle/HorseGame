import pygame

# Colours

GOLD = (255, 184, 28)
PINK = (170, 22, 166)

class GameParameters():
    def __init__(self,player,SCREEN_WIDTH,SCREEN_HEIGHT,):

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        # ADJUSTABLE PARAMETERS
        # paradigm
        self.folder = 'Bear'
        self.duration_TASK_s = 5
        self.duration_REST_s = 5
        self.totalNum_TRIALS = 5  # Set the number of times Task should occur
        self.duration_BASELINE_s = 5
        self.durationGame_s = (self.duration_TASK_s + self.duration_REST_s ) * self.totalNum_TRIALS + self.duration_BASELINE_s #How long you want to one game run to last (in seconds)
        #Other
        self.useBCIinput = True # If true, then player will be controlled by BCI input next to keyboard presses
        self.FPS = 30 # Frame rate. # Defines how often the the while loop is run through. E.g., an FPS of 60 will go through the while loop 60 times per second).

        # Background markers for task and rest periods
        self.useExclamationMark = True # Shows a bright exclamation mark when a task starts
        self.useGreyOverlay = False # Overlays the screen with a grey overlay when a task starts
        self.usePath = False # If true, then a path will appear during the task trial
        self.useLoadingBar = True # If true, then a loading bar will appear during the task trial

        self.currentTime_s = 0  #

        # Paradigm parameters - constants
        self.TASK_counter = 0    # Set the initial values for the event counters
        self.REST_counter = 0
        self.startTime_TASK = 0  # Set the start time for event A
        self.startTime_REST = 0

        self.ADDCOIN = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADDCOIN, 600) # Define how quickly new jellyfish are added (e.g., every 4000ms)
        self.NrOfCoins = 4

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

        # Create counter text
        self.counterText = str('-').rjust(3)
        self.mainFont = pygame.font.SysFont('herculanum', 30, bold=True, )
        self.jellyfishCollectedFont = pygame.font.SysFont('herculanum', 40, bold=True, )
        self.gameTimeCounterText = self.mainFont.render(self.counterText, True, PINK)
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)

        self.nrCoinsCollected = 0
        self.coinAlreadyBeingAdded = False
        self.nrCoinsCollectedText = self.mainFont.render(self.counterText, True, GOLD)
        self.coinOriginalStartingPosition_y = (SCREEN_HEIGHT - 200)
        self.coinStartingPosition_y = self.coinOriginalStartingPosition_y

        self.scoreSaved = False

        # Create the sprites
        self.player = player
        print('Player created')
        self.coin = pygame.sprite.Group()  # - enemies is used for collision detection and position updates
        self.messages = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()  # - all_sprites isused for rendering
        self.all_sprites.add(self.player)

        # Counter ( for countin down the seconds until game over)
        self.SECOND_HAS_PASSED = pygame.USEREVENT
        pygame.time.set_timer(self.SECOND_HAS_PASSED, 1000) # in ms


        self.task = False
        self.rest = True

        self.mainGame_background = 0

    def update_Taskcounter(self):
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)

    def resetCoinStartingPosition(self):
        self.coinStartingPosition_y = self.coinOriginalStartingPosition_y

    def reset(self):
        self.all_sprites.empty()





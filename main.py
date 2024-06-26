# Main script
"""
Author: Danielle Evenblij
Email: d.evenblij@maastrichtuniversity.nl
Created: June 2022
Last updated: October 2022

------------------------------------------------------------------------------------------------------------------------
Notes for potential problem solving:
- Use Python 3.7.5 as your interpreter (needed for expyriment)
- When successfully pip installing expyriment (in a Python 3.7.5. environment), pygame is also immediately installed.
- You may need to to pip install simpleaudio manually.
- If you get problems with the pygame mixer library, then toggle off USE_BACKGROUND_MUSIC in SoundSystem.py.
------------------------------------------------------------------------------------------------------------------------

Most important parameters you can adjust:

In main:
- You can toggle fullscreen on/off in main.

In GameParameters:
- You can adjust how long the game lasts (in seconds) with gameTimeCounter_s.
- You can adjust how often new sharks and jellyfish appear.
- You can adjust the speed of all sprites with 'velocity'.

In SoundSystem
- USE_BACKGROUND_MUSIC toggles the background music on/off (note, the background music makes use of the pygame mixer).

------------------------------------------------------------------------------------------------------------------------
"""

import pygame, random, os
from pylsl import StreamInfo, StreamOutlet # import required classes

import SettingsScreen
from BrainComputerInterface import BrainComputerInterface
from GameParameters import GameParameters
from Coin import Coin
from Background import MainGame_background
from SettingsScreen import Settings_header

from SoundSystem import SoundSystem
from gameover import GameOver, PressSpaceToReplay
from StartScreenPics import PressSpace, Horse, FishAdventure, Settings, ReadyToJump
from MainPlayer import MainPlayer


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Starting up Horse Game...')
    print_hi('Developed by Danielle Evenblij, 2023')
    print(os.getcwd())
    print('test')

    # Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
    from pygame.locals import (
        RLEACCEL,
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_SPACE, K_l, K_s, K_p, KEYDOWN, QUIT,
    )

    # Configure fullscreen. If you don't want fullscreen, set to 0 instead. Otherwise set to pygame.FULLSCREEN
    FULLSCREEN = 0  # pygame.FULLSCREEN

    # Colour constants
    GOLD = (255, 184, 28)
    PINK = (170, 22, 166)
    RED = (255, 0, 0)

    # Timing stuff
    prev_time = 0

    # Brain input variables
    fakeBrainInput = 0

    print('test')


    def getBrainInput(fakeBrainInput):
        fakeBrainInput += 1
        return fakeBrainInput


    # Used to cycle through different game states with a statemachine
    class GameStates:
        STARTSCREEN = 'StartScreen'
        SETTINGS = 'Settings'
        LOCALIZER = 'Localizer'
        STARTNEWGAME = 'StartNewGame'
        MAINGAME = 'MainGame'
        GAMEOVER = 'GameOver'
        SCOREBOARD = 'Scoreboard'
        QUITGAME = 'QuitGame'

        def setGameState(self, gamestate):
            print('Going to state: ' + gamestate)
            return gamestate


    class Scoreboard():
        def __init__(self):
            self.scoresList = []
            self.font = pygame.font.SysFont('herculanum', 35, bold=True, )

        def addScoretoScoreBoard(self, score):
            if not gp.scoreSaved:
                self.scoresList.append(score)
                gp.scoreSaved = True  # This will reset when the player goes back to the start screen
                print('Score ', score, ' saved to score list. Is now: ', str(self.scoresList))

        def makePinkFont(self, string):
            text = self.font.render(string, True, PINK)  # Pink colour
            return text

        def displayScoreboard(self):

            scoreboard = self.makePinkFont('Scoreboard')
            screen.blit(scoreboard,
                        ((SCREEN_WIDTH / 2) - (SCREEN_WIDTH * 0.11), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.40)))

            currentScoreAlreadyDisplayed = False
            newPosition = 30
            count = 1
            sortedScores = sorted(self.scoresList, reverse=True)

            # Put each score on the screen in descending order
            for score in sortedScores:
                count_str = str(count) + '.'
                if score == gp.nrCoinsCollected and not currentScoreAlreadyDisplayed:  # Colour the currently achieved score GOLD
                    scores_text = self.font.render(str(score) + ' coins collected', True, GOLD)
                    count_text = self.font.render(count_str, True, GOLD)
                    currentScoreAlreadyDisplayed = True
                else:
                    scores_text = self.makePinkFont(str(score) + ' coins collected')
                    count_text = self.makePinkFont(count_str)

                # Put score on screen
                screen.blit(count_text,
                            ((SCREEN_WIDTH / 2.6) - 80, (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
                screen.blit(scores_text,
                            ((SCREEN_WIDTH / 2.6), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
                newPosition += 30
                count += 1
                # print('score ', score, ' printed')

    def startTaskTrigger():
        outlet.push_sample(x=[2])  # Task trigger
        print('Started task trigger.')

    def startRestTrigger():
        outlet.push_sample(x=[1])  # Rest trigger
        print('Started Rest trigger.')


    # GAME STATE FUNCTIONS
    def startANewGame():
        print('Starting a new game.')
        gamestate = GameState.setGameState(GameState.MAINGAME)

        player = MainPlayer(SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem)

        gameParameters = GameParameters(player, SCREEN_WIDTH, SCREEN_HEIGHT)
        player.gameParams = gameParameters  # So that player also has access to game parameters
        player.setPlayerSpeed() # to make this independent of frame rate

        mainGameBackGround = MainGame_background(SCREEN_WIDTH, SCREEN_HEIGHT, gameParameters)

        return gamestate, gameParameters, mainGameBackGround  # Reinitialize game parameters and background


    def runStartScreen():
        gamestate = GameState.STARTSCREEN

        screen.fill([0, 0, 0])  # Set black background

        # Create elements to be put on screen
        startscreen = PressSpace(SCREEN_WIDTH, SCREEN_HEIGHT)
        horse = Horse(SCREEN_WIDTH, SCREEN_HEIGHT)
        fishadventure_text = FishAdventure(SCREEN_WIDTH, SCREEN_HEIGHT)
        credits = Settings(SCREEN_WIDTH, SCREEN_HEIGHT)

        string = "Press L for test environment!"
        font = pygame.font.SysFont('herculanum', 20, bold=True, )
        textestEnvironment_txtt = font.render(string, True, PINK)  # Pink colour
        testEnvironment_txt = font.render("(Press 'L' for test environment)", True, (255, 255, 255))


        # Display on screen
        screen.blit(startscreen.surf, startscreen.surf_center)
        screen.blit(horse.surf, horse.location)
        screen.blit(credits.surf, credits.location)
        screen.blit(fishadventure_text.surf, fishadventure_text.location)
        screen.blit(testEnvironment_txt, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT - 100))

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If space to start
                if event.key == K_SPACE:
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.STARTNEWGAME)

                if event.key == K_l:
                    startscreen.kill()
                    startANewGame()
                    gamestate = GameState.setGameState(GameState.LOCALIZER)

                if event.key == K_s:  # When you press 's'
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.SETTINGS)

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate


    def runSettings():
        gamestate = GameState.SETTINGS
        screen.fill([0, 0, 0])  # Set black background

        gameSetting = SettingsScreen.GametimeText(SCREEN_WIDTH, SCREEN_HEIGHT, gp)

        settings_header = Settings_header(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen.blit(settings_header.surf, settings_header.surf_center)
        screen.blit(gameSetting.gameTimeSetting, gameSetting.location)
        screen.blit(gameSetting.gameTimeSetting_seconds, gameSetting.location_seconds)

        # Create TextInput-object
        # textinput = pygame_textinput.TextInputVisualizer()
        # screen.blit(textinput.surface, (10, 10))

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If space to start
                if event.key == K_SPACE:
                    # startscreen.kill()
                    gamestate = GameState.setGameState(GameState.STARTSCREEN)

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate

    def runLocalizer():
        gamestate = GameState.LOCALIZER
        readyToJump = ReadyToJump(SCREEN_WIDTH, SCREEN_HEIGHT)
        mainGame_background.updateAllBackGrounds()
        displayBackgroundsOnScreen()

        for event in pygame.event.get():
            # Did the user hit a key?

            # Update horse riding animation
            if event.type == gp.HORSEANIMATION:
                gp.player.changeHorseAnimation()

            # Start the path if p is pressed
            if event.type == KEYDOWN:
                # If space to start
                if event.key == K_p:
                    gp.mainGame_background.startPathBackground()
                if event.key == K_SPACE:
                    gp.mainGame_background.endPathBackground()

            # PARADIGM
            runLocalizerParadigm() # Duration of task and rest can be changed in GameParameters.py

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            gamestate = didPlayerPressQuit(gamestate, event)

            # Get user input
            keyboard_input = pygame.key.get_pressed()  # Get the set of keyboard keys pressed from user
            gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)

        # Draw all our sprites
        for entity in gp.all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Draw game time counter text
        screen.blit(gp.gameTimeCounterText, (SCREEN_WIDTH - 70, 20))
        screen.blit(gp.nrCoinsCollectedText, (SCREEN_WIDTH - 70, 50))
        screen.blit(gp.nrTrialsCompletedText, (20, 20))

        if gp.task and gp.useExclamationMark:
            screen.blit(readyToJump.surf, readyToJump.surf_center)

        return gamestate


    def runMainGame():
        soundSystem.playMaintheme_slow()
        gamestate = GameState.MAINGAME
        readyToJump = ReadyToJump(SCREEN_WIDTH, SCREEN_HEIGHT)
        BCI_input = 0


        mainGame_background.updateAllBackGrounds()
        displayBackgroundsOnScreen()

        for event in pygame.event.get():
            # Did the user hit a key?
            # print("check1")

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            if event.type == BCI.GET_TURBOSATORI_INPUT:
                BCI_input = BCI.getKeyboardPressFromBrainInput()  # Check for BCI-based keyboard presses


            # EXPERIMENT EVENTS
            # Baseline
            if gp.currentTime_s == 1:
                gp.resetCoinStartingPosition()
                gp.NrOfCoins = 1

            runMainGameParadigm()  # Duration of task and rest can be changed in GameParameters.py

            # Add new coin if counter has passed
            if event.type == gp.ADDCOIN:
                if gp.NrOfCoins < 3:
                    gp.startingPosition_y += 60
                    new_coin = Coin(SCREEN_WIDTH, SCREEN_HEIGHT, gp, gp.startingPosition_y)
                    gp.coin.add(new_coin)
                    gp.all_sprites.add(new_coin)
                    gp.NrOfCoins += 1
                    print("New coin with starting position_y = ", str(gp.startingPosition_y),
                          "  added at (game time counter) = " + str(gp.currentTime_s))

            # Update horse riding animation
            if event.type == gp.HORSEANIMATION:
                if gp.player.HorseIsJumping:
                    if gp.player.HorseIsJumpingUp:
                        if gp.player.rect.top > 0 + (SCREEN_HEIGHT * 0.5):
                            gp.player.jumpUp()
                            print("Horse is jumping up.")
                        else:
                            gp.player.HorseIsJumpingUp = False
                            gp.player.HorseIsJumpingDown = True
                    if gp.player.HorseIsJumpingDown:
                        if gp.player.rect.bottom < SCREEN_HEIGHT -50:
                            gp.player.jumpDown()
                            print("Horse is jumping down. Screen height = ", str(SCREEN_HEIGHT), "  Horse bottom = ", str(gp.player.rect.bottom))
                        else:
                            gp.player.HorseIsJumpingDown = False
                            gp.player.HorseIsJumping = False

                else:
                    gp.player.changeHorseAnimation()
                    if gp.player.rect.left > gp.player.startingPosition_x: # Move horse back to starting point
                        print("Horse is moving back to starting point.")
                        gp.player.moveLeft()
                        gp.player.moveLeft()

            gamestate = didPlayerPressQuit(gamestate, event)

        # Get user input
        keyboard_input = pygame.key.get_pressed()  # Get the set of keyboard keys pressed from user
        gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)

        # Update the position of our enemies and clouds
        gp.coin.update()
       # gameParams.messages.update()

        # Draw all our sprites
        for entity in gp.all_sprites:
            screen.blit(entity.surf, entity.rect)


            # Check if any coins have collided with the player
        for coin in gp.coin:
            if coin.rect.colliderect(gp.player.rect):
                coin.kill()
                soundSystem.jellyfishCollected.play()
                gp.nrCoinsCollected += 1  # Extra points for jellyfish!
                # Show the player how much coins have been collected
                text = str(gp.nrCoinsCollected).rjust(3)
                gp.nrCoinsCollectedText = gp.jellyfishCollectedFont.render(text, True, RED)

        # Draw game time counter text
        screen.blit(gp.gameTimeCounterText, (SCREEN_WIDTH - 70, 20))
        screen.blit(gp.nrCoinsCollectedText, (SCREEN_WIDTH - 70, 50))

        if gp.task:
            if gp.useExclamationMark and not gp.player.HorseIsJumping:
                screen.blit(readyToJump.surf, readyToJump.surf_center)

        return gamestate


    def runGameOver():
        gamestate = GameState.GAMEOVER

        # Sounds
        soundSystem.fadeIntoGameOverMusicTheme()
        soundSystem.playedStartScreenSound = False

        gameover = GameOver(SCREEN_WIDTH, SCREEN_HEIGHT)
        replay = PressSpaceToReplay(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen.blit(gameover.surf, gameover.surf_center)
        screen.blit(replay.surf, replay.surf_center)

        # Save the score for the player
        scoreboard.addScoretoScoreBoard(gp.nrCoinsCollected)

        for event in pygame.event.get():

            if event.type == KEYDOWN:

                if event.key == K_SPACE:
                    gamestate = GameState.setGameState(GameState.SCOREBOARD)

                    # Reset game parameters if you want to restart a game
                    gp.reset()

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate


    def runScoreboard():
        gamestate = GameState.SCOREBOARD

        displayBackgroundsOnScreen()
        replay = PressSpaceToReplay(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen.blit(replay.surf, replay.surf_center)
        scoreboard.displayScoreboard()

        for event in pygame.event.get():
            if event.type == KEYDOWN:

                if event.key == K_SPACE:
                    gamestate = GameState.setGameState(GameState.STARTSCREEN)
                    soundSystem.stopGameOverMusicTheme()

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate

    def runMainGameParadigm():
        if isItTimeForTaskEvent():
            initiateBasicTaskEvent()

        if isItTimeForRestEvent():
            gp.resetCoinStartingPosition()
            gp.NrOfCoins = 1
            initiateBasicRestEvent()

    def runLocalizerParadigm():
        # PARADIGM
        # Check if it's time for event TASK
        if isItTimeForTaskEvent():
           initiateBasicTaskEvent()

        # Check if it's time for event REST
        if isItTimeForRestEvent():
           initiateBasicRestEvent()


    def resetTaskandRestTime():
        gp.startTime_TASK = gp.currentTime_s  # Reset the start time for event TASK
        gp.startTime_REST = gp.currentTime_s  # Set the start time for event REST


    def isItTimeForTaskEvent():
        return gp.currentTime_s - gp.startTime_TASK >= gp.duration_TASK_s and gp.TASK_counter < gp.totalNum_TRIALS and gp.task == False


    def isItTimeForRestEvent():
        return gp.currentTime_s - gp.startTime_REST >= gp.duration_REST_s and gp.REST_counter < gp.totalNum_TRIALS and gp.rest == False


    def initiateBasicTaskEvent():
        gp.task = True
        gp.rest = False
        startTaskTrigger()
        if gp.usePath:
            mainGame_background.startPathBackground()

        resetTaskandRestTime()
        gp.TASK_counter += 1  # Increment the counter for event TASK
        gp.update_Taskcounter()
        print("Event TASK " + gp.TASK_counter.__str__() + " of " + gp.totalNum_TRIALS.__str__())


    def initiateBasicRestEvent():
        gp.task = False
        gp.rest = True
        startRestTrigger()
        if gp.usePath:
            mainGame_background.endPathBackground()

        resetTaskandRestTime()
        gp.REST_counter += 1  # Increment the counter for event B
        print("Event REST")



    def showHowMuchTimeHasPassed(gamestate):

        # Show the player how much time has passed
        if gp.currentTime_s == gp.durationGame_s:
            gamestate = GameState.GAMEOVER
            gp.player.kill()
        else:
            gp.currentTime_s += 1
            text = str(gp.currentTime_s).rjust(3)
            gp.gameTimeCounterText = scoreboard.makePinkFont(text)
            print("Seconds: " + text)
            if (
                    gp.currentTime_s == gp.durationGame_s - 10):  # speed up the main theme if less than 10 seconds left
                # soundSystem.drum.play()
                soundSystem.speedupMaintheme()
            if (
                    gp.currentTime_s == gp.durationGame_s - 3):  # Play countdown if only 3 seconds left
                soundSystem.countdownSound.play()

        return gamestate


    # OTHER FUNCTIONS
    def displayBackgroundsOnScreen():

        screen.fill((0, 0, 0))  # black
        screen.blit(mainGame_background.background_far, [mainGame_background.bgX_far, 0])
        screen.blit(mainGame_background.background_far, [mainGame_background.bgX2_far, 0])
        screen.blit(mainGame_background.background_middle, [mainGame_background.bgX_middle, 20])
        screen.blit(mainGame_background.background_middle, [mainGame_background.bgX2_middle, 20])
        screen.blit(mainGame_background.background_foreground_current, [mainGame_background.bgX_foreground, 40])
        screen.blit(mainGame_background.background_foreground_upcoming, [mainGame_background.bgX2_foreground, 40])

        if not gp.task and gp.useGreyOverlay:
            screen.blit(mainGame_background.overlay_greysurface, (0, 0))# Draw the grey overlay surface on top of the background

        if gp.task and gp.usePath:
            screen.blit(mainGame_background.background_path, [mainGame_background.bgX_foreground, 40])
            screen.blit(mainGame_background.background_path, [mainGame_background.bgX2_foreground, 40])



        # return mainGame_background


    def didPlayerPressQuit(gamestate, event):

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                gamestate = GameState.setGameState(GameState.QUITGAME)

        if event.type == pygame.QUIT:
            gamestate = GameState.setGameState(GameState.QUITGAME)
            print("Clicked quit.")

        return gamestate


    # INITIALIZE MAIN GAME SCREEN
    pygame.init()  # Initialize pygame

    infoObject = pygame.display.Info()
    # pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

    if FULLSCREEN == 0:
        SCREEN_WIDTH = infoObject.current_w - int(infoObject.current_w / 3)
        SCREEN_HEIGHT = infoObject.current_h - int(infoObject.current_h / 3)
    else:  # If fullscreen is selected, adjust all size parameters to fullscreen
        SCREEN_WIDTH = infoObject.current_w
        SCREEN_HEIGHT = infoObject.current_h

    print('Screen width = ' + str(SCREEN_WIDTH) + ', screen height = ' + str(SCREEN_HEIGHT))

    # Clock
    clock = pygame.time.Clock()  # Set up the clock for tracking time

    # Screen
    SURFACE = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
    # Create the screen object. The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                     FULLSCREEN)  # WARNING: WITH fullscreen using an external screen may cause problems (tip: it helps if you don't have pycharm in fullscreen already)

    # Setup sounds
    pygame.mixer.init()  # Setup for sounds, defaults are good

    soundSystem = SoundSystem()

    BCI = BrainComputerInterface()

    # Set up trigger straem
    info = StreamInfo(name='Triggerstream', type='Markers', channel_count=1, channel_format='int32',
                      source_id='Example')  # sets variables for object info
    outlet = StreamOutlet(info)  # initialize stream.

    # Set up gamestates to cycle through in main loop
    GameState = GameStates()

    # Make a scoreboard (will remain throughout the game)
    scoreboard = Scoreboard()

    # Set up a new game (will be refreshed after every replay)
    gamestate, gp, mainGame_background = startANewGame()
    gp.mainGame_background = mainGame_background
    BCI_input = 0

    # ========== GAME STATE MACHINE ==============
    gamestate = GameState.STARTSCREEN
    run = True
    while run:  # Game loop (= one frame)

        if gamestate == GameState.STARTSCREEN:
            gamestate = runStartScreen()

        if gamestate == GameState.SETTINGS:
            gamestate = runSettings()

        if gamestate == GameState.LOCALIZER:
            gamestate = runLocalizer()

        if gamestate == GameState.STARTNEWGAME:
            gamestate, gp, mainGame_background = startANewGame()

        elif gamestate == GameState.MAINGAME:
            gamestate = runMainGame()

        elif gamestate == GameState.GAMEOVER:
            gamestate = runGameOver()

        elif gamestate == GameState.SCOREBOARD:
            gamestate = runScoreboard()

        elif gamestate == GameState.QUITGAME:
            run = False  # quit the while loop

        # Take care of time
        clock.tick(
            gp.FPS)  # Updates the clock using a framerate of x frames per second (so goes through the while loop e.g. 60 times per second).
        now = pygame.time.get_ticks()  # Get current time since pygame started
        gp.deltaTime = int(
            (now - prev_time) / 10)  # Compute delta time... divided by 10 because to make sprite speed more manageble
        prev_time = now

        pygame.display.flip()

    # ====== QUIT GAME =======
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    print('quitting game')

    pygame.quit()

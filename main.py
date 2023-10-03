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
- You may need to pip install simpleaudio manually.
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
from pylsl import StreamInfo, StreamOutlet

#from pylsl import StreamInfo, StreamOutlet  # import required classes

import SettingsScreen
from BrainComputerInterface import BrainComputerInterface
from GameParameters import GameParameters
from Coin import Coin
from Background import MainGame_background
from LoadingBar import LoadingBar
from Rider import Rider
from SettingsScreen import Settings_header

from SoundSystem import SoundSystem
from gameover import GameOver, PressSpaceToReplay
from Pictures import PressSpace, FishAdventure, Settings, ReadyToJump, MountPicture
from MainPlayer import MainPlayer

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting up Horse Game...')
    print('Developed by Danielle Evenblij, 2023')
    print(os.getcwd())

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
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    GREY = (128, 128, 128)

    # Timing stuff
    prev_time = 0


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

        # Used to cycle through different game states with a statemachine


    # Used to cycle through different mounts
    class Mounts:
        HORSE = 'horse'
        TURTLE = 'turtle'
        CAMEL = 'camel'
        BEAR = 'bear'

        def setMount(self, mount):
            print('Set mount to ' + mount)
            return mount


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

    # TRIGGERS
    def startTaskTrigger():
        outlet.push_sample(x=[3])  # Triggers are buggy in Turbo-satori but Aurora they work properly. (0 doesn't exist in TSI, and 1 = rest)
        print('Started task trigger.')

    def startRestTrigger():
        outlet.push_sample(x=[1])  # Rest trigger
        print('Started Rest trigger.')


    # GAME STATE FUNCTIONS
    def startANewGame(mounttype):
        print('Starting a new game.')
        gamestate = GameState.setGameState(GameState.MAINGAME)

        player = MainPlayer(SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem, mounttype)
        rider = Rider(player, SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem)

        gameParameters = GameParameters(player, rider,SCREEN_WIDTH, SCREEN_HEIGHT)
        gameParameters.generate_protocol()
        player.gameParams = gameParameters  # So that player also has access to game parameters
        player.setPlayerSpeed()  # to make this independent of frame rate

        mainGameBackGround = MainGame_background(SCREEN_WIDTH, SCREEN_HEIGHT, gameParameters,mounttype)

        return gamestate, gameParameters, mainGameBackGround  # Reinitialize game parameters and background


    def changeMount(mounttype):

        if mounttype == Mounts.HORSE:
            mounttype = MountType.setMount(Mounts.TURTLE)
        elif mounttype == Mounts.TURTLE:
            mounttype = MountType.setMount(Mounts.CAMEL)
        elif mounttype == Mounts.CAMEL:
            mounttype = MountType.setMount(Mounts.BEAR)
        elif mounttype == Mounts.BEAR:
            mounttype = MountType.setMount(Mounts.HORSE)

        return mounttype


    def runStartScreen(currentMountType):
        gamestate = GameState.STARTSCREEN

        screen.fill([0, 0, 0])  # Set black background

        # Create elements to be put on screen
        startscreen = PressSpace(SCREEN_WIDTH, SCREEN_HEIGHT)
        mountPic = MountPicture(SCREEN_WIDTH, SCREEN_HEIGHT, currentMountType)
        fishadventure_text = FishAdventure(SCREEN_WIDTH, SCREEN_HEIGHT)
        credits = Settings(SCREEN_WIDTH, SCREEN_HEIGHT)

        string = "Press L for test environment!"
        font = pygame.font.SysFont('herculanum', 20, bold=True, )
        textestEnvironment_txtt = font.render(string, True, PINK)  # Pink colour
        testEnvironment_txt = font.render("(Press 'L' for test environment)", True, (255, 255, 255))

        # Display on screen
        screen.blit(startscreen.surf, startscreen.surf_center)
        screen.blit(mountPic.surf, mountPic.location)
        screen.blit(credits.surf, credits.location)
        screen.blit(fishadventure_text.surf, fishadventure_text.location)
        screen.blit(testEnvironment_txt, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT - 100))

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If space to start
                if event.key == K_SPACE:
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.STARTNEWGAME)

                if event.key == K_RIGHT:
                    currentMountType = changeMount(currentMountType)
                    soundSystem.menuSelection.play()

                if event.key == K_l:
                    startscreen.kill()
                    startANewGame(currentMountType)
                    gamestate = GameState.setGameState(GameState.LOCALIZER)

                if event.key == K_s:  # When you press 's'
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.SETTINGS)

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate, currentMountType


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
        mainGame_background.updateAllBackGrounds()
        displayBackgroundsOnScreen()

        for event in pygame.event.get():

            # PARADIGM
            runParadigm()  # Duration of task and rest can be changed in GameParameters.py

            # Update horse riding animation
            if event.type == gp.HORSEANIMATION:
                gp.player.performJumpSequence(NF_level_reached=0.5)  # For localizer, set it to a fixed level. (no feedback during the localizer)
                gp.achieved_jump_height = 0.5 # For displaying debugging text

            showPathBackground(event)

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            gamestate = didPlayerPressQuit(gamestate, event)

            # Get user input
            keyboard_input = pygame.key.get_pressed()  # Get the set of keyboard keys pressed from user
            gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)
            collectTaskTrialData()
            collectRestTrialData()
            gp.rider.update()

        updatePlayerCoinsAndText()
        performTaskRestSpecificActions()

        return gamestate



    def showPathBackground(event):
        # Start the path if p is pressed
        if event.type == KEYDOWN:
            # If space to start
            if event.key == K_p:
                gp.mainGame_background.startPathBackground()
            if event.key == K_SPACE:
                gp.mainGame_background.endPathBackground()

    def draw_game_time_text():
        # Draw game time counter text
        screen.blit(gp.gameTimeCounterText, (SCREEN_WIDTH - 70, 20))
        screen.blit(gp.nrCoinsCollectedText, (SCREEN_WIDTH - 70, 50))
        screen.blit(gp.nrTrialsCompletedText, (20, 60))

    def draw_debugging_text():
        gp.update_y_position_horse_text()
        gp.update_jump_position_text()
        screen.blit(gp.horse_upper_position_text, (20, 100))
        screen.blit(gp.achieved_jump_height_text, (20, 120))

    def updateTimeDataWindow_task():
        if gp.TASK_counter < gp.totalNum_TRIALS:
            start_time_next_task = gp.protocol_file['task_start_times'][gp.TASK_counter+1] # +1 because the first trial is 0
            gp.datawindow_task_start_time = start_time_next_task + gp.hemodynamic_delay
            gp.datawindow_task_end_time = gp.datawindow_task_start_time + gp.datawindow_task_duration

            print("T=",gp.currentTime_s,": Next data time window TASK: " + str(gp.datawindow_task_start_time), "Datawindow end time TASK: " + str(gp.datawindow_task_end_time))

    def updateTimeDataWindow_rest():
        if gp.TASK_counter < gp.totalNum_TRIALS:
            start_time_next_rest = gp.protocol_file['rest_start_times'][gp.TASK_counter+1] # +1 because the first trial is 0
            gp.datawindow_rest_start_time = start_time_next_rest + gp.hemodynamic_delay #todo: at what time do I start measuring the baseline?
            gp.datawindow_rest_end_time = gp.datawindow_rest_start_time + gp.datawindow_rest_duration

            print("T=",gp.currentTime_s,": Next data time window REST: " + str(gp.datawindow_rest_start_time), "Datawindow REST end time: " + str(gp.datawindow_rest_end_time))

    def stopCollectingData():
        print("T=",gp.currentTime_s,": Calculating NF signal...")
        BCI.collectTimewindowData = False
        BCI.resetTimewindowDataArray()

    def collectTaskTrialData():
        # Send time window to BCI
        if gp.datawindow_task_start_time <= gp.currentTime_s <= gp.datawindow_task_end_time:
            BCI.collectTimewindowData = True
            scaled_data = BCI.startMeasuring(task=True)
            print("T=",gp.currentTime_s,": Collecting timewindow data for task. Scaled data: " + str(scaled_data))

        if gp.currentTime_s == gp.datawindow_task_end_time:
            BCI.calculateNFsignal(task=True)
            stopCollectingData()
            PSC = BCI.get_percentage_signal_change()
            print("T=",gp.currentTime_s,": PSC = " + str(PSC))
            updateTimeDataWindow_task()

    def collectRestTrialData():
        # Send time window to BCI
        if gp.datawindow_rest_start_time <= gp.currentTime_s <= gp.datawindow_rest_end_time:
            BCI.collectTimewindowData = True
            scaled_data = BCI.startMeasuring(task=False)
            print("T=",gp.currentTime_s,": Collecting timewindow data for rest. Scaled data: " + str(scaled_data))

        if gp.currentTime_s == gp.datawindow_rest_end_time:
            BCI.calculateNFsignal(task=False)
            stopCollectingData()
            updateTimeDataWindow_rest()



    def runMainGame():
        soundSystem.playMaintheme_slow()
        gamestate = GameState.MAINGAME
        BCI_input = 0

        mainGame_background.updateAllBackGrounds()
        displayBackgroundsOnScreen()

        for event in pygame.event.get():
            # Did the user hit a key?

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            if event.type == BCI.GET_TURBOSATORI_INPUT:
                BCI_input = BCI.getKeyboardPressFromBrainInput()  # Check for BCI-based keyboard presses
                collectTaskTrialData()
                collectRestTrialData()

            runParadigm()  # Duration of task and rest can be changed in GameParameters.py

            # Update horse riding animation
            if event.type == gp.HORSEANIMATION:
                gp.achieved_jump_height = BCI.get_achieved_NF_level()
                gp.player.performJumpSequence(NF_level_reached=gp.achieved_jump_height)

            gamestate = didPlayerPressQuit(gamestate, event)

        updatePlayerCoinsAndText()
        performTaskRestSpecificActions()

        return gamestate

    def performTaskRestSpecificActions():

        readyToJump = ReadyToJump(SCREEN_WIDTH, SCREEN_HEIGHT)

        if gp.task:
            if gp.useLoadingBar:
                screen.blit(loadingBar.surf, loadingBar.surf_center)
                updateLoadingBar_task(loadingBar)
            if gp.useExclamationMark and not gp.player.HorseIsJumping:
                screen.blit(readyToJump.surf, readyToJump.surf_center)

        if gp.rest:
            if gp.useLoadingBar:
                screen.blit(loadingBar.surf, loadingBar.surf_center)
                updateLoadingBar_rest(loadingBar)


    def updatePlayerCoinsAndText():
        # Get user input
        keyboard_input = pygame.key.get_pressed()  # Get the set of keyboard keys pressed from user
        gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)

        gp.coin.update()  # Update the position of coins
        checkForCoinCollision()  # Check if any coins have collided with the player

        # Draw all our sprites
        for entity in gp.all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Draw game time counter text
        draw_game_time_text()
        draw_debugging_text()


    def checkForCoinCollision():
        for coin in gp.coin:
            if coin.rect.colliderect(gp.player.rect):
                coin.kill()
                soundSystem.coinCollected.play()
                gp.nrCoinsCollected += 1

                if coin.rank == 8:
                    print("T=",gp.currentTime_s,": Highest coin collected! Killing all coins.")
                    soundSystem.coin_sound.play() # Play extra sound
                    killAllCoins()
                    break

                # Show the player how many coins have been collected
                text = str(gp.nrCoinsCollected).rjust(3)
                gp.nrCoinsCollectedText = gp.jellyfishCollectedFont.render(text, True, RED)


    def killAllCoins():
        for coin in gp.coin:
            coin.kill()
            soundSystem.coinCollected.play()
            gp.nrCoinsCollected += 1
            # Show the player how many coins have been collected
            text = str(gp.nrCoinsCollected).rjust(3)
            gp.nrCoinsCollectedText = gp.jellyfishCollectedFont.render(text, True, RED)


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

        if not gp.printedNFdata:
            print("NFsignals stored: " + str(BCI.NFsignal))
            BCI.calculate_NF_max_threshold()
            gp.printedNFdata = True

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


    def runParadigm():

        if gp.currentTime_s >= gp.duration_BASELINE_s:
            gp.baseline = False
            if isItTimeForTaskEvent():
                initiateBasicTaskEvent()
                deleteExistingCoins()
                coinEvent()
                resetRestStartTime()

            if isItTimeForRestEvent():
                if gp.REST_counter > 0: # Only let the horse jump after the first task event occured (otherwise it will jump at the start of the game).
                    gp.player.HorseIsJumping = True
                    gp.player.HorseIsJumpingUp = True
                resetTaskStartTime()
                initiateBasicRestEvent()


    def updateLoadingBar_task(loadingBar):
        loadingBar.fillLoadingBar(task=True)
        pygame.draw.rect(screen, GREEN,
                         [loadingBar.barfilling_x, loadingBar.barfilling_y, loadingBar.bar_fill, loadingBar.bar_height])


    def updateLoadingBar_rest(loadingBar):

        loadingBar.fillLoadingBar(task=False)
        pygame.draw.rect(screen, GREY,
                         [loadingBar.barfilling_x, loadingBar.barfilling_y, loadingBar.bar_fill, loadingBar.bar_height])

    def resetTaskStartTime():
        gp.startTime_TASK = gp.currentTime_s  + gp.duration_REST_s# Reset the start time for event TASK

    def resetRestStartTime():
        gp.startTime_REST = gp.currentTime_s + gp.duration_TASK_s  # Reset the start time for event TASK

    def resetTaskandRestTime():
        gp.startTime_TASK = gp.currentTime_s  # Reset the start time for event TASK
        gp.startTime_REST = gp.currentTime_s  # Set the start time for event REST


    def isItTimeForTaskEvent():
        if gp.task:
            return False

        if gp.TASK_counter >= gp.totalNum_TRIALS:
            return False

        if gp.currentTime_s >= gp.startTime_TASK:
            return True

        #return gp.currentTime_s - gp.startTime_TASK >= gp.duration_TASK_s and gp.TASK_counter < gp.totalNum_TRIALS and gp.task == False


    def isItTimeForRestEvent():
        if gp.rest:
            return False

        if gp.currentTime_s >= gp.startTime_REST:
            return True


        #return gp.currentTime_s - gp.startTime_REST >= gp.duration_REST_s and gp.REST_counter < gp.totalNum_TRIALS and gp.rest == False


    def initiateBasicTaskEvent():
        gp.task = True
        gp.rest = False
        loadingBar.resetLoadingBar()
        startTaskTrigger()
        if gp.usePath:
            mainGame_background.startPathBackground()

        #resetTaskandRestTime()
        #resetTaskStartTime()
        gp.TASK_counter += 1  # Increment the counter for event TASK
        gp.update_Taskcounter()
        print("T=",gp.currentTime_s,": Event TASK " + gp.TASK_counter.__str__() + " of " + gp.totalNum_TRIALS.__str__())


    def deleteExistingCoins():
        for coin in gp.coin:
            coin.kill()


    def coinEvent():
        gp.coinStartingPosition_y -= 0
        addNewCoin(1, gp.coinStartingPosition_y,1)
        addNewCoin(1, gp.coinStartingPosition_y - 50,2)
        addNewCoin(1, gp.coinStartingPosition_y - 100,3)
        addNewCoin(1, gp.coinStartingPosition_y - 150,4)
        addNewCoin(1, gp.coinStartingPosition_y - 200,5)
        addNewCoin(1, gp.coinStartingPosition_y - 250,6)
        addNewCoin(1, gp.coinStartingPosition_y - 300,7)
        addNewCoin(1, gp.coinStartingPosition_y - 350,8)


    def addNewCoin(coinType, y_position,rank):
        new_coin = Coin(SCREEN_WIDTH, SCREEN_HEIGHT, gp, y_position, rank)
        gp.coin.add(new_coin)
        gp.all_sprites.add(new_coin)
        gp.NrOfCoins += 1


    def initiateBasicRestEvent():
        gp.task = False
        gp.rest = True
        startRestTrigger()
        if gp.usePath:
            mainGame_background.endPathBackground()

        loadingBar.resetLoadingBar()
        resetRestStartTime()
        gp.REST_counter += 1  # Increment the counter for event B
        print("T=",gp.currentTime_s,": Event REST")


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

        if gp.player.mount_folder == "Resources/Bear/":  # Need to change position of background because the trees need to reach all the way to the top of the screen
            y = 0
            screen.blit(mainGame_background.background_middle, [mainGame_background.bgX_middle, 0])
            screen.blit(mainGame_background.background_middle, [mainGame_background.bgX2_middle, 0])
        if gp.player.mount_folder == "Resources/Camel/":  # Need to change position of background because the trees need to reach all the way to the top of the screen
            y = 20
        else:
            y = 40
        screen.blit(mainGame_background.background_middle, [mainGame_background.bgX_middle, 20])
        screen.blit(mainGame_background.background_middle, [mainGame_background.bgX2_middle, 20])
        screen.blit(mainGame_background.background_foreground_current, [mainGame_background.bgX_foreground, y])
        screen.blit(mainGame_background.background_foreground_upcoming, [mainGame_background.bgX2_foreground, y])

        if not gp.task and gp.useGreyOverlay:
            screen.blit(mainGame_background.overlay_greysurface,
                        (0, 0))  # Draw the grey overlay surface on top of the background

        if gp.task and gp.usePath:
            screen.blit(mainGame_background.background_path, [mainGame_background.bgX_foreground, 40])
            screen.blit(mainGame_background.background_path, [mainGame_background.bgX2_foreground, 40])

        # return mainGame_background

        if gp.draw_grid:
            # Draw the grid
            for x in range(0, SCREEN_WIDTH, grid_size):
                pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
                label = font.render(str(x), True, grid_color)
                screen.blit(label, (x, 0))
            for y in range(0, SCREEN_HEIGHT, grid_size):
                label = font.render(str(y), True, grid_color)
                screen.blit(label, (0, y))
                pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))


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
        SCREEN_HEIGHT = infoObject.current_h - int(infoObject.current_h /3)
    else:  # If fullscreen is selected, adjust all size parameters to fullscreen
        SCREEN_WIDTH = infoObject.current_w
        SCREEN_HEIGHT = infoObject.current_h

    print('Screen width = ' + str(SCREEN_WIDTH) + ', screen height = ' + str(SCREEN_HEIGHT))

    # Clock
    clock = pygame.time.Clock()  # Set up the clock for tracking time

    # Screen
    SURFACE = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
    ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    # Create the screen object. The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.RESIZABLE,
                                     FULLSCREEN,
                                     display=0)  # WARNING: WITH fullscreen using an external screen may cause problems (tip: it helps if you don't have pycharm in fullscreen already)

    # Grid configuration
    grid_size = int(SCREEN_HEIGHT/10)  # Size of each grid cell
    grid_color = (0, 0, 0)  # Color of the grid lines
    font = pygame.font.SysFont(None, 18)  # Font for the position labels

    # Setup sounds
    pygame.mixer.init()  # Setup for sounds, defaults are good

    soundSystem = SoundSystem()

    BCI = BrainComputerInterface()
    BCI.scaleOxyData()

    # Set up trigger stream (note that you need to exactly write "TriggerStream', otherwise Aurora and Turbo-Satori won't recognize it!
    info = StreamInfo(name='TriggerStream', type='Markers', channel_count=1, channel_format='int32',
                      source_id='Example')  # sets variables for object info
    outlet = StreamOutlet(info)  # initialize stream.

    # Set up gamestates to cycle through in main loop
    GameState = GameStates()
    MountType = Mounts() # Set up mount types to cycle through
    mounttype = MountType.setMount(Mounts.HORSE)
    print("Starting mount set to ", mounttype)


    # Make a scoreboard (will remain throughout the game)
    scoreboard = Scoreboard()

    # Set up a new game (will be refreshed after every replay)
    gamestate, gp, mainGame_background = startANewGame(mounttype)
    gp.mainGame_background = mainGame_background
    BCI_input = 0
    loadingBar = LoadingBar(SCREEN_WIDTH, SCREEN_HEIGHT, gp)

    # ========== GAME STATE MACHINE ==============
    gamestate = GameState.STARTSCREEN
    run = True
    while run:  # Game loop (= one frame)

        if gamestate == GameState.STARTSCREEN:
            gamestate, mounttype = runStartScreen(mounttype)

        if gamestate == GameState.SETTINGS:
            gamestate = runSettings()

        if gamestate == GameState.LOCALIZER:
            gamestate = runLocalizer()

        if gamestate == GameState.STARTNEWGAME:
            gamestate, gp, mainGame_background = startANewGame(mounttype)

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

       # print('frame rate = ',clock.get_fps())

    # ====== QUIT GAME =======
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    print('quitting game')

    pygame.quit()

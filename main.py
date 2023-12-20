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
import csv

import pygame, random, os, sys
from pylsl import StreamInfo, StreamOutlet

#from pylsl import StreamInfo, StreamOutlet  # import required classes

import SettingsScreen
import datetime
from ParadigmAndTriggerManager import ParadigmAndTriggerManager
from BrainComputerInterface import BrainComputerInterface
from GameParameters import GameParameters
from Coin import Coin
from Background import MainGame_background
from ProgressBar import ProgressBar
from Rider import Rider
from SettingsScreen import Settings_header
from CSVwriter import CSVwriter

from SoundSystem import SoundSystem
from gameover import GameOver, PressSpaceToReplay
from Pictures import PressSpace, Title, Settings, ReadyToJump, AnimalPicture, TimeOfDayPicture
from MainPlayer import MainPlayer

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting up Horse Game... ')
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

    # Saves the output from the console to a logfile.
    allowLogSaving = False

    if allowLogSaving:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        log_file_path = f"Data/PyCharm Logs/logfile_{current_date}.txt"  # Specify the file path where you want to save the log
        log_file = open(log_file_path,'w')  # Open the file in write mode, this will also create the file if it doesn't exist

        sys.stdout = log_file                              # Redirect stdout and stderr to the log file
        sys.stderr = log_file

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
            self.runList = []
            self.runNr = 1
            self.font = pygame.font.SysFont('herculanum', 35, bold=True, )
            self.coinsPerTrialPerRuns = []

        def addScoretoScoreBoard(self, score):
            if not gp.scoreSaved:
                self.scoresList.append(score)
                self.runList = self.runNr
                self.runNr =+ 1
                gp.scoreSaved = True  # This will reset when the player goes back to the start screen
                print('Score ', score, ' saved to score list. Is now: ', str(self.scoresList))
                self.save_scoresPerRun_to_csv()
                print('Coins per trial: ' + str(gp.nrCoinsPerTrial))
                self.coinsPerTrialPerRuns.append(gp.nrCoinsPerTrial)
                print('Coins per trial per run: ' + str(self.coinsPerTrialPerRuns))


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
                if score == gp.nrCoinsCollectedThroughoutRun and not currentScoreAlreadyDisplayed:  # Colour the currently achieved score GOLD
                    scores_text = self.font.render(str(score) + ' coins collected', True, BLACK)
                    count_text = self.font.render(count_str, True, BLACK)
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
    # CSV writer
        def save_scoresPerRun_to_csv(self):

            ScoresDictionary = {"Coins collected": self.scoresList}
            fieldnames = ["Coins collected"]

            current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
            filename = f"Scoreboard_{current_date}.csv"

            csvWriter = CSVwriter()
            csvWriter.save_dict_to_csv(filename, fieldnames, ScoresDictionary)


    # GAME STATE FUNCTIONS
    def startANewGame(mounttype,gametype,timeofday):
        print('Starting a new game.')
        if gametype == 'maingame':
            gamestate = GameState.setGameState(GameState.MAINGAME)
        if gametype == 'localizer':
            gamestate = GameState.setGameState(GameState.LOCALIZER)

        player = MainPlayer(SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem, mounttype)
        rider = Rider(player, SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem)

        gameParameters = GameParameters(player, rider,SCREEN_WIDTH, SCREEN_HEIGHT)
        gameParameters.generate_protocol()
        gameParameters.generate_dataCollection_protocol()
        paradigmManager = ParadigmAndTriggerManager(SCREEN_WIDTH, SCREEN_HEIGHT, gameParameters)
        player.gameParams = gameParameters  # So that player also has access to game parameters
        player.setPlayerSpeed()  # to make this independent of frame rate
        BCI = BrainComputerInterface(gametype,gameParameters)

        print("Time of day input variable = " + timeofday)
        mainGameBackGround = MainGame_background(SCREEN_WIDTH, SCREEN_HEIGHT, gameParameters,mounttype,timeofday)

        return gamestate, gameParameters, mainGameBackGround,paradigmManager, BCI  # Reinitialize game parameters and background


    def changeMount_right(mounttype):

        if mounttype == Mounts.HORSE:
            mounttype = MountType.setMount(Mounts.TURTLE)
        elif mounttype == Mounts.TURTLE:
            mounttype = MountType.setMount(Mounts.CAMEL)
        elif mounttype == Mounts.CAMEL:
            mounttype = MountType.setMount(Mounts.BEAR)
        elif mounttype == Mounts.BEAR:
            mounttype = MountType.setMount(Mounts.HORSE)

        return mounttype

    def changeMount_left(mounttype):

        if mounttype == Mounts.HORSE:
            mounttype = MountType.setMount(Mounts.BEAR)
        elif mounttype == Mounts.TURTLE:
            mounttype = MountType.setMount(Mounts.HORSE)
        elif mounttype == Mounts.CAMEL:
            mounttype = MountType.setMount(Mounts.TURTLE)
        elif mounttype == Mounts.BEAR:
            mounttype = MountType.setMount(Mounts.CAMEL)

        return mounttype

    def setTimeOfDay(time):
        timeOfDay = time
        print("Time of day set to: ", timeOfDay)

        return timeOfDay



    def runStartScreen(currentMountType, timeofday):
        gamestate = GameState.STARTSCREEN
        gametype = 'maingame'

        screen.fill([0, 0, 0])  # Set black background

        # Create elements to be put on screen
        startscreen = PressSpace(SCREEN_WIDTH, SCREEN_HEIGHT)
        mountPic = AnimalPicture(SCREEN_WIDTH, SCREEN_HEIGHT, currentMountType)
        timeofdayPic = TimeOfDayPicture(SCREEN_WIDTH, SCREEN_HEIGHT, timeofday)
        fishadventure_text = Title(SCREEN_WIDTH, SCREEN_HEIGHT)
        credits = Settings(SCREEN_WIDTH, SCREEN_HEIGHT)

        string = "(Press L for localizer)"
        font = pygame.font.SysFont('ariel', 23, bold=False, )
        testEnvironment_txt = font.render(string, True, (255, 255, 255))

        # Display on screen
        screen.blit(startscreen.surf, startscreen.surf_center)
        screen.blit(mountPic.surf, mountPic.location)
        screen.blit(timeofdayPic.surf, timeofdayPic.location)
        screen.blit(credits.surf, credits.location)
        screen.blit(fishadventure_text.surf, fishadventure_text.location)
        screen.blit(testEnvironment_txt, (SCREEN_WIDTH / 2 - 90, SCREEN_HEIGHT - 90))



        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If space to start
                if event.key == K_SPACE:
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.STARTNEWGAME)
                    gametype = 'maingame'

                if event.key == K_RIGHT:
                    currentMountType = changeMount_right(currentMountType)
                    soundSystem.menuSelection.play()

                if event.key == K_LEFT:
                    currentMountType = changeMount_left(currentMountType)
                    soundSystem.menuSelection.play()

                if event.key == K_UP:
                    timeofday = setTimeOfDay('Day')
                    soundSystem.menuSelection.play()

                if event.key == K_DOWN:
                    timeofday = setTimeOfDay('Night')
                    soundSystem.menuSelection.play()

                if event.key == K_l:
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.STARTNEWGAME)
                    gametype = 'localizer'

                if event.key == K_s:  # When you press 's'
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.SETTINGS)

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate, currentMountType, gametype,timeofday


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
                gp.achievedNFlevel = 0.5  # For displaying debugging text
                gp.maxJumpHeightAchieved = gp.player.performJumpSequence(NF_level_reached=0.5)  # For localizer, set it to a fixed level. (no feedback during the localizer)

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            gamestate = didPlayerPressQuit(gamestate, event)

            if event.type == BCI.GET_TURBOSATORI_INPUT:
                if BCI.saveIncomingData:
                    BCI.continuousMeasuring(trialNr=gp.trial_counter)  # Do a continous measurement to get oxy data of the whole run
                BCI_input = BCI.getKeyboardPressFromBrainInput()  # Check for BCI-based keyboard presses
                collectTaskTrialData()
                if gp.collectDataDuringRest:
                    collectRestTrialData()


            # # Get user input
            # keyboard_input = pygame.key.get_pressed(l)  # Get the set of keyboard keys pressed from user
            # gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)
            # collectTaskTrialData()
            # collectRestTrialData()
            # gp.rider.update()

        updatePlayerCoinsAndText()
        performTaskRestSpecificActions()

        if mounttype == 'turtle': # Do this at the very last so that part of the backgroundw ill move in FRONT of the turle
            y = SCREEN_HEIGHT - mainGame_background.background2.surf.get_height()  # Use background layer 2 for height reference
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX, y])
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX2, y])

        return gamestate



    def draw_game_time_text():
        # Draw game time counter text
        screen.blit(gp.gameTimeCounterText, (SCREEN_WIDTH - 70, 20))
        screen.blit(gp.nrCoinsCollectedText, (SCREEN_WIDTH - 70, 50))
        screen.blit(gp.nrTrialsCompletedText, (20, 20))

    def draw_debugging_text():
        gp.update_y_position_horse_text()
        gp.update_jump_position_text()
        screen.blit(gp.horse_upper_position_text, (20, 60))
        screen.blit(gp.achieved_jump_height_text, (20, 80))

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
        print("T=",gp.currentTime_s,": Stop collecting data. Calculating NF signal...")
        BCI.collectTimewindowData = False
        BCI.resetTimewindowDataArray()

    # Protocol generated. Task start times are:{7, 16} and rest start times are: { 2, 11, 20}

    def collectTaskTrialData():
        # Send time window to BCI
        if gp.protocol_file['datawindow_task_start_times'][gp.trialCounter_task] <= gp.currentTime_s < gp.protocol_file['datawindow_task_end_times'][gp.trialCounter_task]:
            BCI.collectTimewindowData = True
            scaled_data = BCI.startMeasuring(task=True,simulatedData=gp.signalValue_simulated,trialNr=gp.trial_counter)
            print("T=",gp.currentTime_s,": Collecting timewindow data for task. Start time task: " + str(gp.datawindow_task_start_time) + ", Scaled data: " + str(scaled_data))

        if gp.currentTime_s == gp.protocol_file['datawindow_task_end_times'][gp.trialCounter_task]: # Don't measure rest data while the task trial has already started
            if gp.trialCounter_task > len(BCI.NFsignal["NFsignal_mean_TASK"]) and gp.trialCounter_task <= gp.totalNum_TRIALS: # Check if NF signal has already been measured:
                BCI.calculateNFsignal(task=True)
                stopCollectingData()
                #PSC = BCI.get_percentage_signal_change()
                #print("T=",gp.currentTime_s,": PSC = " + str(PSC))
                updateTimeDataWindow_task()
                gp.trialCounter_task +=1
                if gp.trialCounter_task >= gp.totalNum_TRIALS:
                    gp.trialCounter_task = gp.totalNum_TRIALS # Then you've reached the end of the task trials (and since this counter is used for indexing it shouldn't exceed its max)
            else:
                print("NF signal task already calculated.")

    def resetCoinsPerTrialCount():
        print("Resetting coinsCollectedInCurrentTrial (was " + str(gp.coinsCollectedInCurrentTrial) + " to 0.")
        gp.coinsCollectedInCurrentTrial = 0  # Rest the counter

    def collectRestTrialData():
        # Send time window to BCI

        if gp.protocol_file['datawindow_rest_start_times'][gp.trialCounter_rest] <= gp.currentTime_s <  gp.protocol_file['datawindow_rest_end_times'][gp.trialCounter_rest]:
            BCI.collectTimewindowData = True
            scaled_data = BCI.startMeasuring(task=False,simulatedData=gp.signalValue_simulated,trialNr=gp.trial_counter)
            print("T=",gp.currentTime_s,": Collecting timewindow data for rest. Rest start time: "+ str(gp.datawindow_rest_start_time) + " ,rest end time: "+ str(gp.datawindow_rest_end_time) + ", Scaled data: " + str(scaled_data))

        if gp.currentTime_s == gp.protocol_file['datawindow_rest_end_times'][gp.trialCounter_rest]: # Don't measure rest data while the task trial has already started
            if gp.trialCounter_rest > len(BCI.NFsignal["NFsignal_mean_REST"]) and gp.trialCounter_rest <= gp.totalNum_TRIALS+1:  # Check if NF signal has already been measured: (+1 because we have one extra rest trial)
                BCI.calculateNFsignal(task=False)
                stopCollectingData()
                updateTimeDataWindow_rest()
                gp.trialCounter_rest += 1
                if gp.trialCounter_rest >= gp.totalNum_TRIALS:
                    gp.trialCounter_rest = gp.totalNum_TRIALS # Then you've reached the end of the rest trials (and since this counter is used for indexing it shouldn't exceed its max)
            else:
                print("NF signal rest already calculated.")



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
                if BCI.saveIncomingData:
                    BCI.continuousMeasuring(trialNr=gp.trial_counter)  # Do a continous measurement to get oxy data of the whole run
                BCI_input = BCI.getKeyboardPressFromBrainInput()  # Check for BCI-based keyboard presses
                collectTaskTrialData()
                if gp.collectDataDuringRest:
                    collectRestTrialData()

            runParadigm()  # Duration of task and rest can be changed in GameParameters.py

            # Update horse riding animation
            if event.type == gp.HORSEANIMATION:
                gp.achievedNFlevel = BCI.get_achieved_NF_level()
                gp.maxJumpHeightAchieved = gp.player.performJumpSequence(NF_level_reached=gp.achievedNFlevel)

            gamestate = didPlayerPressQuit(gamestate, event)

        updatePlayerCoinsAndText()
        performTaskRestSpecificActions()

        if mounttype == 'turtle':  # Do this at the very last so that part of the backgroundw ill move in FRONT of the turle
            y = SCREEN_HEIGHT - mainGame_background.background2.surf.get_height()  # Use background layer 2 for height reference
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX, y])
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX2, y])

        return gamestate

    def performTaskRestSpecificActions():

        readyToJump = ReadyToJump(SCREEN_WIDTH, SCREEN_HEIGHT)

        if gp.task:
            if gp.useProgressBar:
                screen.blit(progressBar.surf, progressBar.surf_center)
                updateProgressBar_task(progressBar)
            if gp.useExclamationMark and not gp.player.HorseIsJumping:
                screen.blit(readyToJump.surf, readyToJump.surf_center)

        if gp.rest:
            if gp.useProgressBar:
                screen.blit(progressBar.surf, progressBar.surf_center)
                updateProgressBar_rest(progressBar)


    def  updatePlayerCoinsAndText():
        # Get user input
        keyboard_input = pygame.key.get_pressed()  # Get the set of keyboard keys pressed from user
        gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)

        gp.coin.update()  # Update the position of coins
        checkForCoinCollision()  # Check if any coins have collided with the player

        # Coins counting management during each trial -> send to logger (that will save it to a csv file for later)
        if gp.coinsBeingCounted:
            BCI.addCoinsCollectedDuringCurrentTrial(gp.coinsCollectedInCurrentTrial)  # Add the number of coins collected during the current trial to the BCI object
            BCI.addAchievedNFlevel(gp.achievedNFlevel)
            BCI.addMaxJumpHeightAchieved(gp.maxJumpHeightAchieved)
            resetCoinsPerTrialCount()  # Reset the counter for the number of coins collected during the current trial
            gp.coinsBeingCounted = False

        # Draw all our sprites
        for entity in gp.all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Draw game time counter text
        draw_game_time_text()
        draw_debugging_text()


    def  checkForCoinCollision():
        for coin in gp.coin:
            if coin.rect.colliderect(gp.player.rect):
                coin.kill()
                soundSystem.coinCollected.play()
                gp.nrCoinsCollectedThroughoutRun += 1
                gp.coinsCollectedInCurrentTrial += 1
                gp.nrCoinsPerTrial[gp.TASK_counter-1] += 1 #-1 because indexing is at 0

                if coin.rank == gp.totalNumCoins:
                    print("T=",gp.currentTime_s,": Highest coin collected! Killing all coins.")
                    soundSystem.coin_sound.play() # Play extra sound
                    killAllCoins()
                    break

                # Show the player how many coins have been collected
                text = str(gp.nrCoinsCollectedThroughoutRun).rjust(3)
                gp.nrCoinsCollectedText = gp.coinsCollectedFont.render(text, True, RED)


    def killAllCoins():
        for coin in gp.coin:
            coin.kill()
            soundSystem.coinCollected.play()
            gp.nrCoinsCollectedThroughoutRun += 1
            gp.coinsCollectedInCurrentTrial += 1
            # Show the player how many coins have been collected
            text = str(gp.nrCoinsCollectedThroughoutRun).rjust(3)
            gp.nrCoinsCollectedText = gp.coinsCollectedFont.render(text, True, RED)


    def runGameOver():
        gamestate = GameState.GAMEOVER

        # Sounds
        soundSystem.fadeIntoGameOverMusicTheme()
        soundSystem.playedStartScreenSound = False
        gp.useProgressBar = False # Turn off progress bar

        gameover = GameOver(SCREEN_WIDTH, SCREEN_HEIGHT)
        replay = PressSpaceToReplay(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen.blit(gameover.surf, gameover.surf_center)
        screen.blit(replay.surf, replay.surf_center)

        # Save the score for the player
        scoreboard.addScoretoScoreBoard(gp.nrCoinsCollectedThroughoutRun)

        if not gp.printedNFdata: # If you didn't print the data yet (needs to happen only once)
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
            if paradigmManager.isItTimeForTaskEvent():
                paradigmManager.initiateBasicTaskEvent()
                progressBar.resetProgressBar()
                deleteExistingCoins()
                coinEvent()
                paradigmManager.resetRestStartTime()

                if gp.usePath:
                    mainGame_background.startPathBackground()

            if paradigmManager.isItTimeForRestEvent():
                paradigmManager.resetTaskStartTime()
                paradigmManager.initiateBasicRestEvent()
                progressBar.resetProgressBar()

            # if gp.REST_counter == 1:
                #    paradigmManager.resetJumpStartTime() # Do this the first time the rest event occurs

            # Check if time for horse jump
            if gp.REST_counter > 0 and gp.TASK_counter > 0 and isItTimeForJumpEvent():  # Only let the horse jump after the first task event occured (otherwise it will jump at the start of the game).
                print("Horse jumping = True")
                gp.player.HorseIsJumping = True
                gp.freezeCoins = True # Make the coins stop moving, so that the achieved NF level and horse jump height always amounts to the exact same amount of coins collected.
                gp.player.HorseIsJumpingUp = True
                paradigmManager.resetJumpStartTime()

                if gp.usePath:
                    mainGame_background.endPathBackground()

    def isItTimeForJumpEvent():
        timeforjump = False
        if gp.rest:
            #print("Horsejump counter: " + str(gp.horseJumpCounter) + " Task counter: " + str(gp.TASK_counter))
            if gp.horseJumpCounter == gp.TASK_counter:
                if gp.currentTime_s >= gp.protocol_file['jump_start_times'][gp.TASK_counter]:  #gp.currentTime_s >= gp.startTime_JUMP + gp.timeUntilJump_s and not gp.task:
                    gp.horseJumpCounter += 1
                    print("Time for jump event. Horse jump counter raised to = " + str(gp.horseJumpCounter))
                    print("NF level = " + str(gp.achievedNFlevel))
                    timeforjump = True
        return timeforjump


    def updateProgressBar_task(loadingBar):
        loadingBar.fillProgressBar(task=True)
        pygame.draw.rect(screen, GREEN,
                         [loadingBar.barfilling_x, loadingBar.barfilling_y, loadingBar.bar_fill, loadingBar.bar_height])


    def updateProgressBar_rest(loadingBar):

        loadingBar.fillProgressBar(task=False)
        pygame.draw.rect(screen, GREY,
                         [loadingBar.barfilling_x, loadingBar.barfilling_y, loadingBar.bar_fill, loadingBar.bar_height])


    def deleteExistingCoins():
        for coin in gp.coin:
            coin.kill()


    def coinEvent():
        gp.coinStartingPosition_y -= 0
        stepSize = 0

        # add all the coins
        for coinNr in range(gp.totalNumCoins):
            addNewCoin(1, gp.coinStartingPosition_y - stepSize, coinNr+1) # +1 because indexing starts at 0
            print("Coin nr " + str(coinNr) + " added at y position " + str(gp.coinStartingPosition_y - stepSize))

            stepSize += 50


    def addNewCoin(coinType, y_position,rank):
        new_coin = Coin(SCREEN_WIDTH, SCREEN_HEIGHT, gp, y_position, rank)
        gp.coin.add(new_coin)
        gp.all_sprites.add(new_coin)
        gp.NrOfCoins += 1




    # BASICALLY MY TIMER CLASS
    def showHowMuchTimeHasPassed(gamestate):

        # Show the player how much time has passed
        if gp.currentTime_s == gp.durationGame_s:
            gamestate = GameState.GAMEOVER
            gp.player.kill()
            progressBar.kill()
            progressBar.update()

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

            # SIMULATED CONDITIONS AND DATA
            if gp.useSimulatedData:
                condition_simulated = paradigmManager.getCurrentSimulatedCondition() # Get the current simulated condition
                gp.signalValue_simulated = paradigmManager.getCurrentSimulatedSignalValue() # Get the current simulated signal value

        return gamestate


    # OTHER FUNCTIONS
    def displayBackgroundsOnScreen():

        screen.fill((0, 0, 0))  # black

        if gp.useFancyBackground:
            y = SCREEN_HEIGHT - mainGame_background.background2.surf.get_height() # Use background layer 2 for height reference

            screen.blit(mainGame_background.background1.surf, [mainGame_background.background1.bgX, y+100]) # To fit the moon better on to the screen (it lowers it a little bit)
            screen.blit(mainGame_background.background1.surf, [mainGame_background.background1.bgX2, y+100])
            screen.blit(mainGame_background.background2.surf, [mainGame_background.background2.bgX, y-40])
            screen.blit(mainGame_background.background2.surf, [mainGame_background.background2.bgX2, y-40])
            screen.blit(mainGame_background.background3.surf, [mainGame_background.background3.bgX, y-40])
            screen.blit(mainGame_background.background3.surf, [mainGame_background.background3.bgX2, y-40])
            screen.blit(mainGame_background.background4.surf, [mainGame_background.background4.bgX, y])
            screen.blit(mainGame_background.background4.surf, [mainGame_background.background4.bgX2, y])
            screen.blit(mainGame_background.background5.surf, [mainGame_background.background5.bgX, y])
            screen.blit(mainGame_background.background5.surf, [mainGame_background.background5.bgX2, y])
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX, y])
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX2, y])

            if mounttype == 'horse' or mounttype == 'camel' or mounttype == 'bear':
                screen.blit(mainGame_background.background7.surf, [mainGame_background.background7.bgX, y]) # To put the cacti a bit higher
                screen.blit(mainGame_background.background7.surf, [mainGame_background.background7.bgX2, y])
                screen.blit(mainGame_background.background8.surf, [mainGame_background.background8.bgX, y])
                screen.blit(mainGame_background.background8.surf, [mainGame_background.background8.bgX2, y])
                screen.blit(mainGame_background.background9.surf, [mainGame_background.background9.bgX, y])
                screen.blit(mainGame_background.background9.surf, [mainGame_background.background9.bgX2, y])

            if mainGame_background.folder == "Resources/Horse/Day/" or mainGame_background.folder == "Resources/Bear/Night/":
                screen.blit(mainGame_background.background10.surf, [mainGame_background.background10.bgX, y])
                screen.blit(mainGame_background.background10.surf, [mainGame_background.background10.bgX2, y])

            if mainGame_background.folder == "Resources/Horse/Night/":
                screen.blit(mainGame_background.background11.surf, [mainGame_background.background11.bgX, y])
                screen.blit(mainGame_background.background11.surf, [mainGame_background.background11.bgX2, y])
        else:
            # Default background drawing parameters
            y=40
            screen.blit(mainGame_background.background_far.surf, [mainGame_background.background_far.bgX, 0])
            screen.blit(mainGame_background.background_far.surf, [mainGame_background.background_far.bgX2, 0])
            screen.blit(mainGame_background.background_middle.surf, [mainGame_background.background_middle.bgX, 20])
            screen.blit(mainGame_background.background_middle.surf, [mainGame_background.background_middle.bgX2, 20])
            screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX, y])
            screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX2, y])


            # Adjust some of the background drawing parameters based on the mount background
            if gp.player.mount_folder == "Resources/Bear/":  # Need to change position of background because the trees need to reach all the way to the top of the screen
                y = 0
                screen.blit(mainGame_background.background_middle.surf, [mainGame_background.background_middle.bgX, 0])
                screen.blit(mainGame_background.background_middle.surf, [mainGame_background.background_middle.bgX2, 0])
                screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX, y])
                screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX2, y])
            if gp.player.mount_folder == "Resources/Camel/":  # Need to change position of background because the trees need to reach all the way to the top of the screen
                y = 20
                screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX, y])
                screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX2, y])
            if gp.player.mount_folder == "Resources/Turtle/":
                y = 20
                screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX, y])
                screen.blit(mainGame_background.background_foreground.surf, [mainGame_background.background_foreground.bgX2, y])



        if not gp.task and gp.useGreyOverlay:
            screen.blit(mainGame_background.overlay_greysurface,
                        (0, 0))  # Draw the grey overlay surface on top of the background


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
                if gamestate == GameState.STARTSCREEN:
                    gamestate = GameState.setGameState(GameState.QUITGAME)
                else:
                    gamestate = GameState.setGameState(GameState.STARTSCREEN)

        if event.type == pygame.QUIT:
            gamestate = GameState.setGameState(GameState.QUITGAME)
            print("Clicked quit.")

        return gamestate


    # INITIALIZE MAIN GAME SCREEN
    pygame.init()  # Initialize pygame

    infoObject = pygame.display.Info()
    # pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

    # Get the monitor screen size information
    if FULLSCREEN == 0:
        #SCREEN_WIDTH = infoObject.current_w - int(infoObject.current_w / 3) #  Adjust the screen size to the monitor size
        #SCREEN_HEIGHT = infoObject.current_h - int(infoObject.current_h /3) #
        SCREEN_WIDTH = 1280 # Hard code this into the game, so that it stays the same on all monitors
        SCREEN_HEIGHT = 720
    else:  # If fullscreen is selected, adjust all size parameters to fullscreen
        SCREEN_WIDTH = infoObject.current_w
        SCREEN_HEIGHT = infoObject.current_h

    print('Screen width = ' + str(SCREEN_WIDTH) + ', screen height = ' + str(SCREEN_HEIGHT))

    # Clock
    clock = pygame.time.Clock()  # Set up the clock for tracking time

    ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    # Create the screen object. The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                     FULLSCREEN,
                                     display=0)  # WARNING: WITH fullscreen using an external screen may cause problems (tip: it helps if you don't have pycharm in fullscreen already)

    # Grid configuration
    grid_size = int(SCREEN_HEIGHT/10)  # Size of each grid cell
    grid_color = (0, 0, 0)  # Color of the grid lines
    font = pygame.font.SysFont(None, 18)  # Font for the position labels

    # Setup sounds
    pygame.mixer.init()  # Setup for sounds, defaults are good

    soundSystem = SoundSystem()

    # Set up gamestates to cycle through in main loop
    GameState = GameStates()
    MountType = Mounts() # Set up mount types to cycle through
    mounttype = MountType.setMount(Mounts.HORSE)
    timeofday = 'Day' # Default background is daytime
    print("Starting mount set to ", mounttype)


    # Make a scoreboard (will remain throughout the game)
    scoreboard = Scoreboard()

    # Set up a new game (will be refreshed after every replay)
    gametype = 'maingame'
    gamestate, gp, mainGame_background,paradigmManager,BCI = startANewGame(mounttype,gametype,timeofday)
    gp.mainGame_background = mainGame_background
    BCI_input = 0
    progressBar = ProgressBar(SCREEN_WIDTH, SCREEN_HEIGHT, gp)

    BCI = BrainComputerInterface(gametype,gp)
    BCI.scaleOxyData()




    # ========== GAME STATE MACHINE ==============
    gamestate = GameState.STARTSCREEN
    run = True
    while run:  # Game loop (= one frame)

        if gamestate == GameState.STARTSCREEN:
            gamestate, mounttype, gametype, timeofday = runStartScreen(mounttype,timeofday)

        if gamestate == GameState.SETTINGS:
            gamestate = runSettings()

        if gamestate == GameState.LOCALIZER:
            gamestate = runLocalizer()

        if gamestate == GameState.STARTNEWGAME:
            gamestate, gp, mainGame_background,paradigmManager, BCI = startANewGame(mounttype,gametype,timeofday)

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

    # Close the console log file when done
    if allowLogSaving:
        log_file.close()

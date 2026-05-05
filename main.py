# Main script
"""
Author: Danielle Evenblij
Email: d.evenblij@maastrichtuniversity.nl
Created: June 2022
Last updated: May 2025

------------------------------------------------------------------------------------------------------------------------
Notes for potential problem solving:
- You can use runandjump.yml for your (mini)conda interpreter. It should have all the necessary libraries.

Otherwise:
- Use Python 3.7.5 as your interpreter (needed for expyriment)
- When successfully pip installing expyriment (in a Python 3.7.5. environment), pygame is also immediately installed.
- You may need to pip install simpleaudio (used in Soundsystem.py) manually.
- If you get problems with the pygame mixer library, then toggle off USE_BACKGROUND_MUSIC in SoundSystem.py (is OFF by default).
------------------------------------------------------------------------------------------------------------------------

Notes for the start menu keys when you start the game:
- "Space bar" starts a neurofeedback run.
-"L" starts a localizer run.
- With arrowkeys left and right you can switch between animals.
- With arrowkeys up and down you can switch between a day and night background.

------------------------------------------------------------------------------------------------------------------------

Most important parameters you can adjust:

In main:
- You can toggle fullscreen on/off in main.

In BrainComputerInterface you can adjust:
- The neurofeedback threshold. (NF_maxLevel_based_on_localizer)
- What aspect of the incoming data you want to use that is measured in the timewindow (mean value, max value or latest data point) that i

In GameParameters, you can adjust:
- The duration of the baseline, resting period and task period (in seconds)
- The amount of trials.
- Participant information (will be used for filenaming)
- Whether you want to use t-values or beta values as input for neurofeedback (dataType)
- Game difficulty: changes coin colour and NF threshold
- Whether you want to run the game using simulated data from TSI or not (usePreMadeProtoco = True. Needs TSI to be running in simulation mode and needs a matching protocol file in the "Protocol for simulation" folder!)
- The frame rate. (currently at 20 FPS)
- The speed of all sprites with 'velocity'.

In ParadigmAndTriggerManager you can adjust:
- The name for the triggerestream used with LSL and Aurora (must be the same as specified in Aurora!)

In SoundSystem
- USE_BACKGROUND_MUSIC toggles the background music on/off (note, the background music makes use of the pygame mixer).

------------------------------------------------------------------------------------------------------------------------
"""
import json
import csv
import pygame

pygame.font.init()

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
from PRTwriter import PRTwriter
from Scoreboard import Scoreboard

from SoundSystem import SoundSystem
from gameover import GameOver, PressSpaceToReplay
from Pictures import PressSpace, Title, Credits, ReadyToJump, AnimalPicture, TimeOfDayPicture, GameType_pic
from MainPlayer import MainPlayer

# make relative paths resolve next to the executable (or source, in dev)
import os, sys
from pathlib import Path

if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).resolve().parent)
else:
    os.chdir(Path(__file__).resolve().parent)

# Saves the output from the console to a logfile.
allowLogSaving = True

neurofeedback_threshold = float(1.0)

if allowLogSaving:  # Note that this means there won't be any visibile output in the console anymore - that's put into a logfile instead.
    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    os.makedirs("Data/Logs", exist_ok=True)  # Make the folder if it doesn[t exist yet.
    log_file_path = f"Data/Logs/logfile_{current_date}.txt"  # Specify the file path where you want to save the log
    log_file = open(log_file_path,
                    'w')  # Open the file in write mode, this will also create the file if it doesn't exist

    sys.stdout = log_file  # Redirect stdout and stderr to the log file
    sys.stderr = log_file



ARIAL_FONT_PATH = "Resources/fonts/Arial.ttf"
ARIAL_BOLD_FONT_PATH = "Resources/fonts/Arial Bold.ttf"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting up Horse Game... ')
    print('Developed by Danielle Evenblij, 2023')
    print(os.getcwd())

    # Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
    from pygame.locals import (
        RLEACCEL,
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_SPACE, K_l, K_s, K_p, K_t, KEYDOWN, QUIT,
    )

    # Colour constants
    GOLD = (255, 184, 28)
    PINK = (170, 22, 166)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    GREY = (128, 128, 128)

    # Timing parameters (for the game clock)
    prev_time = 0


    # Used to cycle through different game states with a statemachine
    class GameStates:
        STARTSCREEN = 'StartScreen'
        STARTUPPROMPT = 'StartupPrompt'
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


    # GAME STATE FUNCTIONS
    def startANewGame(mounttype, gametype, timeofday, testing_mode=False):
        print('Starting a new game.')
        if gametype == 'maingame':
            gamestate = GameState.setGameState(GameState.MAINGAME)
        if gametype == 'localizer':
            gamestate = GameState.setGameState(GameState.LOCALIZER)

        player = MainPlayer(SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem, mounttype)
        rider = Rider(player, SCREEN_WIDTH, SCREEN_HEIGHT, 0, soundSystem)

        # Read gamesettings.json to get parameters
        with open("GameSettings.json") as f:
            settings = json.load(f)
            number_of_trials = settings["num_trials"]
            task_duration_s = settings["task_duration_s"]
            rest_duration_s = settings["rest_duration_s"]
            baseline_duration_s = settings["baseline_duration_s"]
            jitter_s = settings["jitter_s"]
            simulation_mode = settings["simulation_mode"]
            debugging = settings["debugging"]
            data_input_type = settings["data_input_type"]
            chromophore = settings["chromophore"]
            neurofeedback_threshold_t_value = settings["neurofeedback_threshold_t_value"]
            neurofeedback_threshold_beta = settings["neurofeedback_threshold_beta"]
            datawindow_duration_after_task_end_s = settings["datawindow_duration_after_task_end_s"]
            datawindow_duration_before_task_end_s = settings["datawindow_duration_before_task_end_s"]
            framerate = settings["framerate"]
            boring_mode = settings["boring_mode"]
            differential_feedback = settings["differential_feedback"]
            minimal_nr_of_coins = settings["minimal_nr_of_coins"]
            port = settings["port"]

        print("New game started: Number of trials from settings file: " + str(settings["num_trials"]))

        gameParameters = GameParameters(player, rider, SCREEN_WIDTH, SCREEN_HEIGHT, number_of_trials, task_duration_s,
                                        rest_duration_s, baseline_duration_s, jitter_s, data_input_type, chromophore,
                                        neurofeedback_threshold_t_value, neurofeedback_threshold_beta,
                                        datawindow_duration_after_task_end_s, datawindow_duration_before_task_end_s,
                                        simulation_mode, debugging, framerate, boring_mode, differential_feedback,
                                        minimal_nr_of_coins)
        gameParameters.tsi_port = port
        if gameParameters.performingSimulation:
            BCI = BrainComputerInterface(gametype, gameParameters)
            if BCI.TSIconnectionFound:
                samplingRate = BCI.tsi.get_sampling_rate()[0]
            else:
                samplingRate = 10
            gameParameters.read_premade_protocol(samplingRate)
            gameParameters.apply_parameters_premadeprotocol_to_settings()

        gameParameters.generate_protocol()
        gameParameters.gameType = gametype
        gameParameters.TESTING_MODE = testing_mode
        gameParameters.generate_dataCollection_protocol()
        paradigmManager = ParadigmAndTriggerManager(SCREEN_WIDTH, SCREEN_HEIGHT, gameParameters)
        player.gp = gameParameters  # So that player also has access to game parameters
        player.setPlayerSpeed()  # to make this independent of frame rate
        BCI = BrainComputerInterface(gametype, gameParameters)

        print("Time of day input variable = " + timeofday)
        mainGameBackGround = MainGame_background(SCREEN_WIDTH, SCREEN_HEIGHT, gameParameters, mounttype, timeofday)

        return gamestate, gameParameters, mainGameBackGround, paradigmManager, BCI  # Reinitialize game parameters and background

    def changeGameTypeIcon_right(gametype):
        if gametype == 0:
            print("Maingame")
            gametype = 1
        elif gametype == 1:
            print("Localizer")
            gametype = 2
        elif gametype == 2:
            print("Testing")
            gametype = 0

        return gametype

    def changeGameTypeIcon_left(gametype):
        if gametype == 0:
            print("Maingame")
            gametype = 2
        elif gametype == 2:
            print("Testing")
            gametype = 1
        elif gametype == 1:
            print("Localizer")
            gametype = 0

        return gametype


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
        testing_mode = False

        screen.fill([0, 0, 0])  # Set black background

        # Create elements to be put on screen
        startscreen = PressSpace(SCREEN_WIDTH, SCREEN_HEIGHT)
        mountPic = AnimalPicture(SCREEN_WIDTH, SCREEN_HEIGHT, currentMountType)
        timeofdayPic = TimeOfDayPicture(SCREEN_WIDTH, SCREEN_HEIGHT, timeofday)
        fishadventure_text = Title(SCREEN_WIDTH, SCREEN_HEIGHT)
        credits = Credits(SCREEN_WIDTH, SCREEN_HEIGHT)

        string = "(Press 'S' for settings)"
        string2 = "(Change animal: left/right key, change day/night: up/down key)"
        font = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 18)
        s_for_settings = font.render(string, True, PINK)
        instructions_txt = font.render(string2, True, (255, 255, 255))

        # Check for turbo-satori connection
        if not BCI.TSIconnectionFound:
            text = font.render('Turbo-Satori connection not found using port ' + str(gp.tsi_port) + '! (default is 55556)', True, RED)
            screen.blit(text, (SCREEN_WIDTH * 0.25, 10))

        # Display on screen
        screen.blit(startscreen.surf, startscreen.surf_center)
        if not gp.boringMode:
            screen.blit(mountPic.surf, mountPic.location)
            screen.blit(timeofdayPic.surf, timeofdayPic.location)
            screen.blit(fishadventure_text.surf, fishadventure_text.location)
        screen.blit(credits.surf, credits.location)
        screen.blit(s_for_settings, (SCREEN_WIDTH / 2.4, SCREEN_HEIGHT - 100))
        screen.blit(instructions_txt, (SCREEN_WIDTH / 3.7, SCREEN_HEIGHT - 130))

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If space to start
                if event.key == K_SPACE:
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.STARTUPPROMPT)

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

                if event.key == K_s:  # When you press 's'
                    startscreen.kill()
                    gamestate = GameState.setGameState(GameState.SETTINGS)


            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate, currentMountType, gametype, timeofday, testing_mode

    def runStartupPrompt(gametype_choice, prompt_selected_index, diff_feedback_value):
        gamestate = GameState.STARTUPPROMPT
        gametype  = "maingame"
        testing_mode = False

        # Row 1 (diff feedback) only exists when Neurofeedback is selected
        num_rows = 2 if gametype_choice == 0 else 1
        if prompt_selected_index >= num_rows:
            prompt_selected_index = 0

        startscreen = PressSpace(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen.fill([0, 0, 0])



        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    gamestate = GameState.setGameState(GameState.STARTNEWGAME)

                if event.key == K_UP:
                    prompt_selected_index = (prompt_selected_index - 1) % num_rows
                if event.key == K_DOWN:
                    prompt_selected_index = (prompt_selected_index + 1) % num_rows

                if event.key == K_RIGHT:
                    if prompt_selected_index == 0:
                        gametype_choice = changeGameTypeIcon_right(gametype_choice)
                        soundSystem.menuSelection.play()
                    elif prompt_selected_index == 1:
                        diff_feedback_value = (diff_feedback_value + 1) % 3
                        with open("GameSettings.json") as f:
                            _s = json.load(f)
                        _s["differential_feedback"] = diff_feedback_value
                        with open("GameSettings.json", "w") as f:
                            json.dump(_s, f, indent=2)

                if event.key == K_LEFT:
                    if prompt_selected_index == 0:
                        gametype_choice = changeGameTypeIcon_left(gametype_choice)
                        soundSystem.menuSelection.play()
                    elif prompt_selected_index == 1:
                        diff_feedback_value = (diff_feedback_value - 1) % 3
                        with open("GameSettings.json") as f:
                            _s = json.load(f)
                        _s["differential_feedback"] = diff_feedback_value
                        with open("GameSettings.json", "w") as f:
                            json.dump(_s, f, indent=2)

            gamestate = didPlayerPressQuit(gamestate, event)

        if gametype_choice == 0:
            gametype_displaytext = "Neurofeedback"
            gametype = "maingame"
        elif gametype_choice == 1:
            gametype_displaytext = "Localizer"
            gametype = "localizer"
        elif gametype_choice == 2:
            gametype_displaytext = "Debug"
            testing_mode = True
        else:
            gametype_displaytext = "Neurofeedback"

        diff_value_labels = {0: "OFF", 1: "A-B", 2: "B-A"}
        prompt_font = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 18)
        row_x = SCREEN_WIDTH / 3.7
        row_w = SCREEN_WIDTH * 0.4
        row_h = 26

        if gametype_choice == 0:
            row_y = SCREEN_HEIGHT / 2
            if prompt_selected_index == 1:
                pygame.draw.rect(screen, PINK, pygame.Rect(int(row_x - 6), int(row_y), int(row_w), row_h))
            label_surf = prompt_font.render("Differential feedback:", True, WHITE)
            value_surf = prompt_font.render(diff_value_labels[diff_feedback_value], True, WHITE)
            value_rect = value_surf.get_rect()
            value_rect.top = int(row_y)
            value_rect.right = int(row_x - 6 + row_w - 10)
            screen.blit(label_surf, (row_x, row_y))
            screen.blit(value_surf, value_rect)

        gametype_pic = GameType_pic(SCREEN_WIDTH, SCREEN_HEIGHT, gametype_displaytext)
        screen.blit(startscreen.surf, startscreen.surf_center)
        screen.blit(gametype_pic.surf, gametype_pic.location)

        return gamestate, gametype_choice, prompt_selected_index, diff_feedback_value, gametype, testing_mode


    def runSettings():
        gamestate = GameState.SETTINGS

        # Create the settings screen class and header
        settingMain = SettingsScreen.settingsMain(SCREEN_WIDTH, SCREEN_HEIGHT, gp)
        setting_header = Settings_header(SCREEN_WIDTH, SCREEN_HEIGHT)

        for item_to_be_displayed in settingMain.items:
            screen.blit(item_to_be_displayed.surface, item_to_be_displayed.location)

        running = True
        while running:
            for event in pygame.event.get():

                if event.type == KEYDOWN:

                    if event.type == pygame.QUIT:
                        return didPlayerPressQuit(gamestate, event)
                        break

                    # leave settings on SPACE
                    if event.key == K_ESCAPE:
                        with open("GameSettings.json") as f:
                            settings = json.load(f)
                            gp.boringMode = settings["boring_mode"] # Immmediately update this so that the startscreen is also properly updated when boring mode is on or off
                        gamestate = GameState.setGameState(GameState.STARTSCREEN)
                        running = False
                        break
                    # Navigating items
                    if event.key in (pygame.K_UP, pygame.K_w):
                        # Move selection UP by 1
                        settingMain.selected_index = (settingMain.selected_index - 1) % len(
                            settingMain.items)  # Use modulo to get a circular menu
                        print("Selected item ", settingMain.items[settingMain.selected_index].text)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        # Move selection DOWN by 1
                        settingMain.selected_index = (settingMain.selected_index + 1) % len(settingMain.items)
                        print("Selected item ", settingMain.items[settingMain.selected_index].text)
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        # Get the currently selected item from the list
                        item = settingMain.items[settingMain.selected_index]
                        # If that item is a ToggleItem (ON/OFF type)...
                        if isinstance(item, SettingsScreen.ToggleItem):
                            item.toggle()  # ...then switch it to the opposite value
                        if isinstance(item, SettingsScreen.NumericalItem_int) or isinstance(item,
                                                                                            SettingsScreen.NumericalItem_float):
                            item.decrease() if event.key == pygame.K_LEFT else item.increase()

            # --- draw ---
            screen.fill(BLACK)
            screen.blit(setting_header.surf, setting_header.surf_center)
            screen.blit(settingMain.instructions, settingMain.location)

            # draw each item (label)
            base_x = SCREEN_WIDTH / 3.5
            base_y = SCREEN_HEIGHT / 3

            # Draw all settings items, their value, and the highlight bar
            for i, item in enumerate(settingMain.items):

                # selected highlight
                if i == settingMain.selected_index:
                    pygame.draw.rect(
                        screen, (PINK),
                        pygame.Rect(item.location[0] - 6, item.location[1] - 0, SCREEN_WIDTH * 0.55, 26))

                # Show item (left)
                screen.blit(item.surface, (item.location))

                # right-aligned value (if any)
                val = item.value_text()
                if val is not None:
                    value_surface = item.font.render(val, True, WHITE)
                    value_rect = value_surface.get_rect()
                    value_rect.top = item.location[1]  # align vertically with label
                    value_rect.right = item.location[0] - 10 + SCREEN_WIDTH * 0.55  # inside the box, 10px padding
                    screen.blit(value_surface, value_rect)

            pygame.display.flip()
            clock.tick(gp.get_FPS())

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
                gp.set_achieved_NF_level(0.1)  # For displaying debugging text
                gp.maxJumpHeightAchieved = gp.player.performJumpSequence(
                    gp.achievedNFlevel)  # For localizer, set it to a fixed level. (no feedback during the localizer)

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            gamestate = didPlayerPressQuit(gamestate, event)

            if event.type == BCI.GET_TURBOSATORI_INPUT:
                if BCI.saveIncomingData:
                    volume_timepoint = BCI.continuousMeasuring(
                        trialNr=gp.trial_counter)  # Do a continous measurement to get oxy data of the whole run

                if gp.performingSimulation:
                    if BCI.TSIconnectionFound:
                        volume_timepoint = BCI.tsi.get_current_time_point()[0]
                        currentCondition = gp.checkIfTaskOrRestCondition_PreMadeProtocol(volume_timepoint)
                        collectTaskTrialData_fromPreMadeProtocol(currentCondition, volume_timepoint)
                else:
                    collectTaskTrialData()

        updatePlayerCoinsAndText()
        performTaskRestSpecificActions()

        if not gp.boringMode:
            if mounttype == 'turtle':  # Do this at the very last so that part of the backgroundw ill move in FRONT of the turle
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
        no_channel_warning = gp.debuggingFont.render("", True, RED)

        if gp.debuggingText:
            gp.update_trial_nr_text()
            gp.display_exp_parameters(get_current_jitter_duration())
            gp.update_y_position_horse_text()
            gp.update_jump_position_text()
            gp.update_retrieved_signal_value_text()
            if BCI.TSIconnectionFound:
                gp.show_selected_channels(BCI.selectedChannels)
                gp.update_NF_target_value_text(BCI.NF_neurofeedack_threshold)
                gp.update_current_beta_value_text(BCI.getBetas(gp.trial_counter, 0))
                #gp.update_current_t_value_text(BCI.getTvalues(gp.trial_counter, 0))
                gp.update_data_window_info(BCI.collectTimewindowData)  # True of False
                if not BCI.tsi.get_selected_channels()[0]:
                    no_channel_warning = gp.debuggingFont.render("WARNING: NO CHANNEL SELECTED!!!", True, RED)

            gp.update_gametype_text(gametype)

            # screen.blit(gp.horse_upper_position_text, (20, 60))
            screen.blit(gp.nrTrialsCompletedText_debug, (20,60))
            screen.blit(gp.exp_parameters_text, (20, 80))
            screen.blit(gp.NF_target_value_text, (20, 100))
            screen.blit(gp.signal_value_retrieved_text, (20, 120))
            if gp.gameType == 'maingame':  # Dont show achieved NF level during localizer (because no NF is given)
                screen.blit(gp.achieved_jump_height_text, (20, 140))
            screen.blit(gp.current_beta_value_text, (20, 160))
            #screen.blit(gp.current_tvalue_text, (20, 180))
            screen.blit(gp.data_window_info_text, (20, 200))
            screen.blit(gp.selected_channels_text, (20, 220))
            screen.blit(gp.gametype_text, (20,240))
            screen.blit(no_channel_warning, (20,260))



    def updateTimeDataWindow_task():
        if gp.TASK_counter < gp.totalNum_TRIALS:
            start_time_next_task = gp.protocol_file['datawindow_task_start_times'][
                gp.TASK_counter + 1]  # +1 because the first trial is 0
            gp.datawindow_task_start_time = start_time_next_task
            gp.datawindow_task_end_time = gp.datawindow_task_start_time + gp.datawindow_task_duration

            print("T=", gp.currentTime_s, ": Next data time window TASK: " + str(gp.datawindow_task_start_time),
                  "Datawindow end time TASK: " + str(gp.datawindow_task_end_time))


    def updateTimeDataWindow_rest():
        if gp.TASK_counter < gp.totalNum_TRIALS:
            start_time_next_rest = gp.protocol_file['rest_start_times'][
                gp.TASK_counter + 1]  # +1 because the first trial is 0
            gp.datawindow_rest_start_time = start_time_next_rest + gp.hemodynamic_delay  # todo: at what time do I start measuring the baseline?
            gp.datawindow_rest_end_time = gp.datawindow_rest_start_time + gp.datawindow_rest_duration

            print("T=", gp.currentTime_s, ": Next data time window REST: " + str(gp.datawindow_rest_start_time),
                  "Datawindow REST end time: " + str(gp.datawindow_rest_end_time))


    def stopCollectingData():
        print("T=", gp.currentTime_s, ": Stop collecting data. Calculating NF signal...")
        BCI.collectTimewindowData = False
        BCI.resetTimewindowDataArray()


    # Protocol generated. Task start times are:{7, 16} and rest start times are: { 2, 11, 20}

    def collectTaskTrialData_fromPreMadeProtocol(currentCondition, current_volume_timepoint):
        if currentCondition > 0:  # Only after baseline
            sampling_rate = BCI.tsi.get_sampling_rate()[0]
            hemodynamic_delay_volumes = gp.hemodynamic_delay * sampling_rate
            prestimulusonset_volumes = gp.datawindow_prestimulusonset_s * sampling_rate
            start_window = gp.start_volumes[
                               currentCondition - 1] + prestimulusonset_volumes  # minus one because current condition is one higher; offset matches real-time mode
            end_window = gp.end_volumes[currentCondition - 1] + hemodynamic_delay_volumes
            print("Collect data when between volumes " + str(start_window) + " and " + str(end_window))

            if current_volume_timepoint >= start_window and current_volume_timepoint < end_window:
                BCI.collectTimewindowData = True
                scaled_data = BCI.startMeasuring(task=True, simulatedData=gp.signalValue_simulated,
                                                 trialNr=currentCondition)
                print("T=", gp.currentTime_s,
                      ": Collecting timewindow data for task (PREMADE PROTOCOL). Scaled data: " + str(scaled_data))

            # Calculate NF data when measuring window is over
            if current_volume_timepoint > end_window:
                if BCI.timewindow_task:  # if not empty
                    BCI.calculateNFsignal(task=True)
                    stopCollectingData()

                    gp.trialCounter_task += 1
                    if gp.trialCounter_task >= gp.totalNum_TRIALS:
                        gp.trialCounter_task = gp.totalNum_TRIALS  # Then you've reached the end of the task trials (and since this counter is used for indexing it shouldn't exceed its max)
                #else:
                    # print("NF signal task already calculated.")


    def collectTaskTrialData():
        # Send time window to BCI
        if gp.protocol_file['datawindow_task_start_times'][gp.trialCounter_task] <= gp.currentTime_s < \
                gp.protocol_file['datawindow_task_end_times'][gp.trialCounter_task]:
            BCI.collectTimewindowData = True
            scaled_data = BCI.startMeasuring(task=True, simulatedData=gp.signalValue_simulated,
                                             trialNr=gp.trial_counter)
            print("T=", gp.currentTime_s, ": Collecting timewindow data for task. Start time task: " + str(
                gp.protocol_file['datawindow_task_start_times'][gp.trialCounter_task]) + ", Scaled data: " + str(
                scaled_data))

        if gp.currentTime_s >= gp.protocol_file['datawindow_task_end_times'][
            gp.trialCounter_task]:  # Don't measure rest data while the task trial has already started
            if gp.trialCounter_task > len(BCI.NFsignal[
                                              "NFsignal_mean_TASK"]) and gp.trialCounter_task <= gp.totalNum_TRIALS:  # Check if NF signal has already been measured:
                BCI.calculateNFsignal(task=True)
                stopCollectingData()
                # PSC = BCI.get_percentage_signal_change()
                # print("T=",gp.currentTime_s,": PSC = " + str(PSC))
                updateTimeDataWindow_task()
                gp.trialCounter_task += 1
                if gp.trialCounter_task >= gp.totalNum_TRIALS:
                    gp.trialCounter_task = gp.totalNum_TRIALS  # Then you've reached the end of the task trials (and since this counter is used for indexing it shouldn't exceed its max)
            else:
                print("NF signal task already calculated.")


    def resetCoinsPerTrialCount():
        print("Resetting coinsCollectedInCurrentTrial (was " + str(gp.coinsCollectedInCurrentTrial) + " to 0.")
        gp.coinsCollectedInCurrentTrial = 0  # Rest the counter



    def runMainGame():
        soundSystem.playMaintheme_slow()
        gamestate = GameState.MAINGAME

        mainGame_background.updateAllBackGrounds()
        displayBackgroundsOnScreen()

        for event in pygame.event.get():
            # Did the user hit a key?

            # Show the player how much time has passed
            if event.type == gp.SECOND_HAS_PASSED:
                gamestate = showHowMuchTimeHasPassed(gamestate)

            if event.type == BCI.GET_TURBOSATORI_INPUT:
                if BCI.saveIncomingData:
                    volume_timepoint = BCI.continuousMeasuring(
                        trialNr=gp.trial_counter)  # Do a continous measurement to get oxy data of the whole run

                if gp.performingSimulation:
                    if BCI.TSIconnectionFound:
                        volume_timepoint = BCI.tsi.get_current_time_point()[0]
                        currentCondition = gp.checkIfTaskOrRestCondition_PreMadeProtocol(volume_timepoint)
                        collectTaskTrialData_fromPreMadeProtocol(currentCondition, volume_timepoint)
                else:
                    collectTaskTrialData()

            runParadigm()  # Duration of task and rest can be changed in GameParameters.py

            # Update horse riding animation
            if event.type == gp.HORSEANIMATION:
                achievedNFlevel, gp.signal_value_retrieved = BCI.get_achieved_NF_level()
                if gp.TESTING_MODE:
                    achievedNFlevel = min((gp.TASK_counter - 1) * 0.1, 1.0)
                    gp.signal_value_retrieved = achievedNFlevel
                gp.set_achieved_NF_level(achievedNFlevel)
                gp.maxJumpHeightAchieved = gp.player.performJumpSequence(NF_level_reached=gp.achievedNFlevel)

            gamestate = didPlayerPressQuit(gamestate, event)

        updatePlayerCoinsAndText()
        performTaskRestSpecificActions()

        if not gp.boringMode:
            if mounttype == 'turtle':  # Do this at the very last so that part of the backgroundw ill move in FRONT of the turle
                y = SCREEN_HEIGHT - mainGame_background.background2.surf.get_height()  # Use background layer 2 for height reference
                screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX, y])
                screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX2, y])

        return gamestate


    def performTaskRestSpecificActions():

        readyToJump = ReadyToJump(SCREEN_WIDTH, SCREEN_HEIGHT)

        if gp.task:
            if gp.boringMode:
                gp.player.updateDotColour_green()
            if gp.useProgressBar:
                screen.blit(progressBar.surf, progressBar.surf_center)
                updateProgressBar_task(progressBar)
            if gp.useExclamationMark and not gp.player.HorseIsJumping:
                screen.blit(readyToJump.surf, readyToJump.surf_center)

        if gp.rest:
            if gp.boringMode:
                gp.player.updateDotColour_grey()
            if gp.useProgressBar:
                screen.blit(progressBar.surf, progressBar.surf_center)
                updateProgressBar_rest(progressBar)


    def updatePlayerCoinsAndText():
        # Get user input
        keyboard_input = pygame.key.get_pressed()  # Get the set of keyboard keys pressed from user
        gp.player.update(keyboard_input, BCI_input, gp.useBCIinput)

        gp.coin.update()  # Update the position of coins
        checkForCoinCollision()  # Check if any coins have collided with the player

        # Coins counting management during each trial -> send to logger (that will save it to a csv file for later)
        if gp.coinsBeingCounted:
            BCI.addCoinsCollectedDuringCurrentTrial(
                gp.coinsCollectedInCurrentTrial)  # Add the number of coins collected during the current trial to the BCI object
            BCI.addAchievedNFlevel(gp.achievedNFlevel)
            BCI.addMaxJumpHeightAchieved(gp.maxJumpHeightAchieved)
            resetCoinsPerTrialCount()  # Reset the counter for the number of coins collected during the current trial
            gp.coinsBeingCounted = False

        # Draw all our sprites
        for entity in gp.all_sprites:
            screen.blit(entity.surf, entity.rect)

        # Draw game time counter text
        if not gp.boringMode:
            draw_game_time_text()

        draw_debugging_text()


    def coinCollectionAdmin():
        if not gp.boringMode:
            soundSystem.coinCollected.play()

        gp.nrCoinsCollectedThroughoutRun += 1
        gp.coinsCollectedInCurrentTrial += 1
        gp.nrCoinsPerTrial[gp.TASK_counter - 1] += 1  # -1 because indexing is at 0


    def checkForCoinCollision():
        # During the jump: collect all eligible coins simultaneously when the horse reaches
        # the x position of the coin column AND the height of the highest eligible coin
        if gp.player.HorseIsJumping:
            eligible_coins = [coin for coin in gp.coin if coin.rank <= gp.coins_to_collect_this_jump]
            if eligible_coins:
                top_coin = min(eligible_coins, key=lambda c: c.rect.centery)
                # Collect all eligible coins the moment the horse reaches the coin column x.

                if gp.player.rect.right >= top_coin.rect.left:
                    for coin in eligible_coins:
                        coin.kill()
                        coinCollectionAdmin()
                    gp.startCountingCoins()

                    # Show the player how many coins have been collected
                    text = str(gp.nrCoinsCollectedThroughoutRun).rjust(3)
                    gp.nrCoinsCollectedText = gp.coinsCollectedFont.render(text, True, RED)

                    if gp.coins_that_should_be_collected == gp.totalNumCoins:
                        print("T=", gp.currentTime_s, ": Highest coin collected! Killing all coins.")
                        if not gp.boringMode:
                            soundSystem.all_coins_collected_sound.play()  # You can potentially play an extra sound here.
            return



    def runGameOver():
        gamestate = GameState.GAMEOVER

        # Sounds
        soundSystem.fadeIntoGameOverMusicTheme()
        soundSystem.playedStartScreenSound = False
        gp.useProgressBar = False  # Turn off progress bar

        gameover = GameOver(SCREEN_WIDTH, SCREEN_HEIGHT)
        replay = PressSpaceToReplay(SCREEN_WIDTH, SCREEN_HEIGHT)
        screen.blit(replay.surf, replay.surf_center)

        # Save the score for the player
        # print("Adding scores to scoreboard.")
        scoreboard.addScoretoScoreBoard(gp.nrCoinsCollectedThroughoutRun)

        if not gp.printedNFdata:  # If you didn't print the data yet (needs to happen only once)
            print("NFsignals stored: " + str(BCI.NFsignal))
            BCI.calculate_NF_max_threshold()
            gp.printedNFdata = True

            # Also write and finish the PRT file only once.
            PRT_writer.finish_PRT_file()  # Finish the PRT file

            # And save a settings file for this run
            with open("GameSettings.json") as f:
                settings = json.load(f)  # Open settings file (json)
            current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            with open("Data/Logs/config_" + str(current_date) + ".csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Key', 'Value'])  # Header
                for key, value in settings.items():
                    writer.writerow([key, value])

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

        # Display the scoreboard
        scoreboard_text = scoreboard.makePinkFont('Scoreboard')
        screen.blit(scoreboard_text,
                    ((SCREEN_WIDTH / 2) - (SCREEN_WIDTH * 0.11), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.40)))

        sortedScores, sortedTasks = scoreboard.sortScores()

        displayScoreboard()

        # Check for user input
        for event in pygame.event.get():
            if event.type == KEYDOWN:

                if event.key == K_SPACE:
                    gamestate = GameState.setGameState(GameState.STARTSCREEN)
                    soundSystem.stopGameOverMusicTheme()

            gamestate = didPlayerPressQuit(gamestate, event)

        return gamestate


    def displayScoreboard():
        # print("Displaying score board...")
        newPosition = 15
        scoresText_list, taskText_list, bonusText_list = scoreboard.prepareScoreBoardText()

        for i in range(len(scoresText_list)):
            screen.blit(bonusText_list[i],
                        ((SCREEN_WIDTH / 3.8), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
            newPosition += 25
            screen.blit(scoresText_list[i],
                        ((SCREEN_WIDTH / 3.8), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
            screen.blit(taskText_list[i],
                        ((SCREEN_WIDTH / 2.2) - 80, (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
            newPosition += 25


    def get_current_jitter_duration():  # todo: This could be coded less rickety...
        if gp.REST_counter >= len(gp.jittered_rest_list):
            return gp.duration_REST_s
        else:
            current_jittered_rest_duration = gp.jittered_rest_list[
                gp.REST_counter]  # -1 because the jitter list starts at index 0
            # print("Progress bar. Rest number: " + str(gp.REST_counter) + ", jitter: " + str(
            # current_jittered_rest_duration))

            return current_jittered_rest_duration


    def runParadigm():

        if gp.currentTime_s >= gp.duration_BASELINE_s:
            gp.baseline = False
            if paradigmManager.isItTimeForTaskEvent():
                soundSystem.startsound.play()
                paradigmManager.initiateBasicTaskEvent()
                current_time_point = BCI.getCurrentTimePoint_TSI()
                PRT_writer.addTaskStartEvent(current_time_point)
                current_jitter_duration = get_current_jitter_duration()
                progressBar.resetProgressBar(current_jitter_duration)
                deleteExistingCoins()
                coinEvent()
                paradigmManager.resetRestStartTime()

            if paradigmManager.isItTimeForRestEvent():
                if gp.firstRestTrial and not gp.performingSimulation: # Simulation doesn't count the first rest trial so skip
                    gp.firstRestTrial = False
                else:
                    soundSystem.stopsound.play()
                    current_time_point = BCI.getCurrentTimePoint_TSI()
                    PRT_writer.addTaskEndEvent(current_time_point)
                    paradigmManager.resetDurationRest()
                paradigmManager.resetTaskStartTime()
                paradigmManager.initiateBasicRestEvent()

                current_jitter_duration = get_current_jitter_duration()
                progressBar.resetProgressBar(current_jitter_duration)

            # if gp.REST_counter == 1:
            #    paradigmManager.resetJumpStartTime() # Do this the first time the rest event occurs

            # Check if time for horse jump
            if gp.REST_counter > 0 and gp.TASK_counter > 0 and isItTimeForJumpEvent():  # Only let the horse jump after the first task event occured (otherwise it will jump at the start of the game).
                print("Horse jumping = True")
                gp.player.HorseIsJumping = True
                gp.freezeCoins = True  # Make the coins stop moving, so that the achieved NF level and horse jump height always amounts to the exact same amount of coins collected.
                gp.player.HorseIsJumpingUp = True
                gp.coins_to_collect_this_jump = gp.coins_that_should_be_collected  # Freeze coin target at jump start
                gp.coinsCollectedInCurrentTrial = 0  # Reset trial counter so safety-net math is correct

                if gp.usePath:
                    mainGame_background.endPathBackground()


    def isItTimeForJumpEvent():
        timeforjump = False
        # print("gp.rest = "+ str(gp.rest) + ", horseJumpCounter = " + str(gp.horseJumpCounter) + ", gp.TASK_counter = " + str(gp.TASK_counter) + ', gp.horseHasJumpedThisTrial = ' + str(gp.horseHasJumpedThisTrial))
        # print("gp.timeUntilJump_s: " + str(gp.timeUntilJump_s) + ", gp.samplingRATE: " + str(BCI.getSamplingRate()))
        if gp.rest:
            # print("Horsejump counter: " + str(gp.horseJumpCounter) + " Task counter: " + str(gp.TASK_counter))
            if gp.horseJumpCounter == gp.TASK_counter:
                if gp.performingSimulation:
                    current_volume_timepoint = BCI.getCurrentTimePoint_TSI()
                    if current_volume_timepoint >= gp.end_volumes[gp.current_condition - 1] + (
                            gp.timeUntilJump_s * BCI.getSamplingRate()) and not gp.horseHasJumpedThisTrial:
                        timeforjump = signalTimeForJump()

                else:  # Use in-game protocol parameters
                    if gp.currentTime_s >= gp.protocol_file['jump_start_times'][
                        gp.TASK_counter]:  # gp.currentTime_s >= gp.startTime_JUMP + gp.timeUntilJump_s and not gp.task:
                        timeforjump = signalTimeForJump()
                        print("!!!!!!!======3454=35========== Jump start time reached: " + str(
                            gp.protocol_file['jump_start_times'][gp.TASK_counter]))
                        print("Jump start times: " + str(gp.protocol_file['jump_start_times']))
        return timeforjump


    def signalTimeForJump():
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
            addNewCoin(gp.coinStartingPosition_y - stepSize, coinNr + 1)  # +1 because indexing starts at 0
            print("Coin nr " + str(coinNr) + " added at y position " + str(gp.coinStartingPosition_y - stepSize))

            stepSize += 50


    def addNewCoin(y_position, rank):
        new_coin = Coin(SCREEN_WIDTH, SCREEN_HEIGHT, gp, y_position, rank)
        gp.coin.add(new_coin)
        gp.all_sprites.add(new_coin)
        gp.NrOfCoins += 1


    # BASICALLY MY TIMER CLASS
    def showHowMuchTimeHasPassed(gamestate):

        # Show the player how much time has passed
        if gp.currentTime_s >= gp.durationGame_s:
            print("Game time is over. Current time: " + str(gp.currentTime_s) + ", total game duration limit: " + str(
                gp.durationGame_s))
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

        return gamestate


    # OTHER FUNCTIONS
    def displayBackgroundsOnScreen():

        # screen.fill((0, 0, 0))  # black
        screen.fill((105, 105, 105))  # grey

        if not gp.boringMode:

            y = SCREEN_HEIGHT - mainGame_background.background2.surf.get_height()  # Use background layer 2 for height reference

            screen.blit(mainGame_background.background1.surf, [mainGame_background.background1.bgX,
                                                               y + 100])  # To fit the moon better on to the screen (it lowers it a little bit)
            screen.blit(mainGame_background.background1.surf, [mainGame_background.background1.bgX2, y + 100])
            screen.blit(mainGame_background.background2.surf, [mainGame_background.background2.bgX, y - 40])
            screen.blit(mainGame_background.background2.surf, [mainGame_background.background2.bgX2, y - 40])
            screen.blit(mainGame_background.background3.surf, [mainGame_background.background3.bgX, y - 40])
            screen.blit(mainGame_background.background3.surf, [mainGame_background.background3.bgX2, y - 40])
            screen.blit(mainGame_background.background4.surf, [mainGame_background.background4.bgX, y])
            screen.blit(mainGame_background.background4.surf, [mainGame_background.background4.bgX2, y])
            screen.blit(mainGame_background.background5.surf, [mainGame_background.background5.bgX, y])
            screen.blit(mainGame_background.background5.surf, [mainGame_background.background5.bgX2, y])
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX, y])
            screen.blit(mainGame_background.background6.surf, [mainGame_background.background6.bgX2, y])

            if mounttype == 'horse' or mounttype == 'camel' or mounttype == 'bear':
                screen.blit(mainGame_background.background7.surf,
                            [mainGame_background.background7.bgX, y])  # To put the cacti a bit higher
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

            if not gp.task and gp.useGreyOverlay:
                screen.blit(mainGame_background.overlay_greysurface,
                            (0, 0))  # Draw the grey overlay surface on top of the background

        if gp.draw_grid:
            # Draw the grid
            font = pygame.font.Font(ARIAL_FONT_PATH, 16)
            for x in range(0, SCREEN_WIDTH, grid_size):
                pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
                label = font.render(str(x), True, grid_color)
                screen.blit(label, (x, 0))
            for y in range(0, SCREEN_HEIGHT, grid_size):
                label = font.render(str(y), True, grid_color)
                screen.blit(label, (0, y))
                pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))

        if gp.performingSimulation:
            font = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 16)
            text = font.render('Using simulated data (tip: don\'t forget to adjust your data-collection window!)', True, BLACK)
            screen.blit(text, (SCREEN_WIDTH / 4, 10))


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
    # SCREEN_WIDTH = infoObject.current_w - int(infoObject.current_w / 3) #  Adjust the screen size to the monitor size
    # SCREEN_HEIGHT = infoObject.current_h - int(infoObject.current_h /3) #
    SCREEN_WIDTH = 1280  # Hard code this into the game, so that it stays the same on all monitors
    SCREEN_HEIGHT = 720

    print('Screen width = ' + str(SCREEN_WIDTH) + ', screen height = ' + str(SCREEN_HEIGHT))

    # Clock
    clock = pygame.time.Clock()  # Set up the clock for tracking time

    ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    # Create the screen object. The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                     display=0)  # WARNING: WITH fullscreen using an external screen may cause problems (tip: it helps if you don't have pycharm in fullscreen already)

    # Grid configuration
    grid_size = int(SCREEN_HEIGHT / 10)  # Size of each grid cell
    grid_color = (0, 0, 0)  # Color of the grid lines
    font = pygame.font.Font(ARIAL_FONT_PATH, 16)

    # Setup sounds
    pygame.mixer.init()  # Setup for sounds, defaults are good

    soundSystem = SoundSystem()

    # Set up gamestates to cycle through in main loop
    GameState = GameStates()
    MountType = Mounts()  # Set up mount types to cycle through
    mounttype = MountType.setMount(Mounts.HORSE)
    timeofday = 'Day'  # Default background is daytime
    print("Starting mount set to ", mounttype)

    # Set up a new game (will be refreshed after every replay)
    gametype = 'maingame'
    testing_mode = False
    gamestate, gp, mainGame_background, paradigmManager, BCI = startANewGame(mounttype, gametype, timeofday,
                                                                             testing_mode)
    gp.mainGame_background = mainGame_background
    BCI_input = 0
    progressBar = ProgressBar(SCREEN_WIDTH, SCREEN_HEIGHT, gp)

    # Make a scoreboard (will remain throughout the game)
    scoreboard = Scoreboard(gp)

    # Setup BCI interface
   # BCI = BrainComputerInterface(gametype, gp)
    #BCI.scaleOxyData()
    gp.setSamplingRate(BCI.getSamplingRate)

    PRT_writer = PRTwriter(gp)
    PRT_writer.create_PRT_template()

    # ========== GAME STATE MACHINE ==============
    gamestate = GameState.STARTSCREEN
    gametype_choice = 0
    prompt_selected_index = 0
    with open("GameSettings.json") as f:
        diff_feedback_value = json.load(f)["differential_feedback"]
    run = True
    while run:  # Game loop (= one frame)

        if gamestate == GameState.STARTSCREEN:
            gamestate, mounttype, gametype, timeofday, testing_mode = runStartScreen(mounttype, timeofday)
            gametype_choice = 0
            prompt_selected_index = 0

        if gamestate == GameState.STARTUPPROMPT:
            gamestate, gametype_choice, prompt_selected_index, diff_feedback_value, gametype, testing_mode = runStartupPrompt(gametype_choice, prompt_selected_index, diff_feedback_value)
            gp.DIFFERENTIAL_FEEDBACK = diff_feedback_value
            if BCI.TSIconnectionFound:
                if not BCI.tsi.get_selected_channels()[0]:
                    no_channel_warning = gp.debuggingFont.render("WARNING: NO CHANNEL SELECTED!!!", True, RED)
                    screen.blit(no_channel_warning, (SCREEN_WIDTH * 0.25, 10))
            if gp.PRT_error:
                PRT_error_warning = gp.mainFont.render("ERROR: Protocol file could not be read.", True, RED)
                screen.blit(PRT_error_warning, (SCREEN_WIDTH * 0.25, 80))

        if gamestate == GameState.SETTINGS:
            gamestate = runSettings()

        if gamestate == GameState.LOCALIZER:
            gamestate = runLocalizer()

        if gamestate == GameState.STARTNEWGAME:
            gamestate, gp, mainGame_background, paradigmManager, BCI = startANewGame(mounttype, gametype, timeofday,
                                                                                     testing_mode)

            progressBar = ProgressBar(SCREEN_WIDTH, SCREEN_HEIGHT,
                                      gp)  # Create new progress bar (with corret fill rates)
            scoreboard.gp.scoreSaved = False  # Allow scoreboard to save a new score
            pygame.event.clear(gp.SECOND_HAS_PASSED)  # Reset this timer event
            pygame.time.set_timer(gp.SECOND_HAS_PASSED, 1000)  # Reset this timer event
            PRT_writer = PRTwriter(gp)  # Also make a new prt file for the next run
            PRT_writer.create_PRT_template()
            print("Current time when starting new game: " + str(gp.currentTime_s))

        elif gamestate == GameState.MAINGAME:
            gamestate = runMainGame()

        elif gamestate == GameState.GAMEOVER:
            gamestate = runGameOver()

        elif gamestate == GameState.SCOREBOARD:
            if not gp.boringMode:
                gamestate = runScoreboard()
            else:
                gamestate = GameState.STARTSCREEN

        elif gamestate == GameState.QUITGAME:
            run = False  # quit the while loop

        # Take care of time
        dt = clock.tick(
            gp.get_FPS()) / 1000.0  # clock.tick returns the time since last call, in ms. Divide by 1000 to get it in seconds.
        if dt > 0.05:  # cap at 50 ms (20 FPS floor) # to aboid one-off spikes
            dt = 0.05
        gp.deltaTime = dt
        gp.deltaTime = dt  # keep it as a float

        pygame.display.flip()

    # print('frame rate = ',clock.get_fps())

    # ====== QUIT GAME =======


    pygame.mixer.music.stop()
    pygame.mixer.quit()
    print('Quitting game now.')

    pygame.quit()

    # Close the console log file when done
    if allowLogSaving:
        log_file.close()

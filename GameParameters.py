import pygame
import random
import json
# Colours

# make relative paths resolve next to the executable (or source, in dev)
import os, sys
from pathlib import Path

if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).resolve().parent)
else:
    os.chdir(Path(__file__).resolve().parent)

GOLD = (255, 184, 28)
PINK = (170, 22, 166)
RED = (255, 0, 0)

# Fonts
HERC_FONT_PATH = "Resources/fonts/Herculanum.ttf"  # add the file to your repo
ARIAL_FONT_PATH = "Resources/fonts/Arial.ttf"  # add the file to your repo

class GameParameters():
    def __init__(self, player, rider, SCREEN_WIDTH, SCREEN_HEIGHT, number_of_trials, task_duration_s, rest_duration_s, baseline_duration_s, jitter_s, data_input_type, chromophore, nf_threshold_t_value, nf_threshold_beta,
                 datawindow_poststimulusonset_s, datawindow_prestimulusonset_s, simulation_mode, debugging, framerate, boring_mode, differential_feedback, minimal_nr_of_coins):

        self.nochannel_warning = None
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.chromophore = chromophore # 1 = oxy and 0 is deoxy


        # ADJUSTABLE PARAMETERS
        # To simulate or not simulate
        self.boringMode = boring_mode
        self.performingSimulation = simulation_mode  # Put your protocol file in the "Protocol for simulation" folder and the game. Note: this mode only works when you have a simulaion in TBV running@
        self.protocol_file_path = 'Protocol for simulation/PRT_for_simulation.prt'
        self.saveIncomingData = False # Don't save all values unless debugging

        self.DIFFERENTIAL_FEEDBACK = differential_feedback

        self.totalNumCoins = 10
        self.minimal_nr_of_coins = minimal_nr_of_coins
        self.TESTING_MODE = False  # When True, NF levels are overridden with a predefined 0.1..1.0 sequence



        # Time
        self.velocity = 1  # Determines general speed of all sprites (to ensure frame-rate independence)
        self.deltaTime = 1
        self.FPS = framerate  # Frame rate. # Defines how often the the while loop is run through. E.g., an FPS of 60 will go through the while loop 60 times per second).
        # Note that you can check the computer's FPS by using clock.getFPS(). If it is lower than the FPS you specify here, the game might not work properly. (15 needed over windows FPN connection?)

        # Background markers for task and rest periods
        self.useExclamationMark = False  # Shows a bright exclamation mark when a task starts
        self.useGreyOverlay = False  # Overlays the screen with a grey overlay when a task starts
        self.usePath = False  # If true, then a path will appear during the task trial
        if self.boringMode:
            self.useProgressBar = False  # If true, then a loading bar will appear during the task trial
        else:
            self.useProgressBar = True
        self.debuggingText = debugging
        self.draw_grid = False  # For debugging purposes

        # paradigm
        self.folder = 'Horse'

        self.neurofeedback_threshold_t_value = nf_threshold_t_value
        self.neurofeedback_threshold_beta = float(nf_threshold_beta)

        if data_input_type == 0:
            self.neurofeedback_threshold = self.neurofeedback_threshold_beta
        if data_input_type == 1:
            self.neurofeedback_threshold = self.neurofeedback_threshold_t_value

        self.duration_TASK_s = task_duration_s
        self.duration_REST_s = rest_duration_s
        self.totalNum_TRIALS = number_of_trials  # Set the number of times Task should occur #TODO For simulation mode: shouldn't be dependent on this for the game to finish!
        self.duration_BASELINE_s = baseline_duration_s # Should be 25s for our experiment
        self.jitter_s = jitter_s

        self.protocol_file = {
            'task_start_times': {},
            'rest_start_times': {},
            'jump_start_times': {},
            'datawindow_task_start_times': {},
            'datawindow_task_end_times': {},
            'datawindow_rest_start_times': {},
            'datawindow_rest_end_times': {},
        }

        self.noChannelSelectedWarning = False

        # Participant information (will be used to correctly name the protocol file for each run)
        self.taskUsed = ''
        self.participantNr = ''
        self.sessionNr = ''
        self.runType = ''
        self.runNr = ''

        self.dataType = data_input_type # 0 = beta's, 1 = t-values (used for neurofeedback input)

        self.gameDifficulty = 3 # 1 = easy (with bronze coins), 2 = medium (silver coins0, 3 = hard (gold coins). The higher the difficulty, the higher the max NF THRESHOLD, but the more points you get for collecting a coin.

        self.PRT_error = False
        self.gameType = ' ' # 'maingame' (NF) or 'localizer' (will be selected during start menu)
        self.duration_datawindow_rest = 6
        self.timeUntilRestDataCollection_s = 11 #self.protocol_file['duration_REST_s'] - 6 # Only start measuring the last 6 seconds before the new trial



        self.durationGame_s = self.calculate_duration_game()

        self.tsi_port = '55556' # default

        self.datawindow_prestimulusonset_s = datawindow_prestimulusonset_s
        self.datawindow_duration_after_task_end_s = datawindow_poststimulusonset_s - self.duration_TASK_s

        self.hemodynamic_delay = self.datawindow_duration_after_task_end_s #todo: this is basically datawindow_duration_after_task_end_s
        self.timeUntilJump_s = self.hemodynamic_delay + 1   # todo: add plus 1 because otherwise the horse jumps too soon without the NF signal being calculated (and will then use previous trial data)

        self.datawindow_task_start_time = self.duration_BASELINE_s + self.duration_REST_s - datawindow_prestimulusonset_s # for first trial - Add 3 seconds to account for the hemodynamic delay?
        self.datawindow_task_duration = self.duration_TASK_s  #6s to fully capture the peak of the hemodynamic response
        self.datawindow_task_end_time = self.datawindow_task_start_time + self.datawindow_task_duration + datawindow_poststimulusonset_s

        self.datawindow_rest_start_time = self.duration_BASELINE_s   # No hemodynamic delay!
        self.datawindow_rest_duration = self.duration_REST_s
        self.datawindow_rest_end_time = self.datawindow_rest_start_time + self.datawindow_rest_duration

        self.samplingRate = 0 # dependent on what TSI inputs

        self.currentTime_s = 0  #
        self.firstRestTrial = True

        self.useBCIinput = True  # If true, then player will be controlled by BCI input next to keyboard presses
        self.collectDataDuringRest = False  # (No longer used in our current experimental setup)

        # Paradigm parameters - constants
        self.trialCounter_task = 1 # For NF measuring
        self.trialCounter_rest = 1 # For NF measuring
        self.TASK_counter = 0    # Set the initial values for the event counters
        self.REST_counter = 0
        self.trial_counter = 0
        self.startTime_TASK = self.duration_BASELINE_s  + self.duration_REST_s# Set the start time for event A
        self.startTime_REST = self.duration_BASELINE_s
        self.startTime_JUMP = self.startTime_TASK + self.duration_TASK_s # The start after the first rest + task period

        self.jittered_rest_list = []



        self.ADDCOIN = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADDCOIN, 600) # Define how quickly new jellyfish are added (e.g., every 4000ms)
        self.NrOfCoins = 4

        self.HORSEANIMATION = pygame.USEREVENT + 3
        pygame.time.set_timer(self.HORSEANIMATION, 70)  # Define how quickly new jellyfish are added (e.g., every 4000ms)


        # Create the sprites
        self.player = player
        print('Player created')
        self.rider = rider
        self.coin = pygame.sprite.Group()  # - enemies is used for collision detection and position updates
        self.messages = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()  # - all_sprites isused for rendering
        self.all_sprites.add(self.player)

        # Create counter text
        self.counterText = str('-').rjust(3)
        self.mainFont = pygame.font.Font(HERC_FONT_PATH, 30) # BOLD?
        self.debuggingFont = pygame.font.Font(ARIAL_FONT_PATH, 15) # 15?
        self.coinsCollectedFont = pygame.font.Font(HERC_FONT_PATH, 40) # BOLD?
        self.gameTimeCounterText = self.mainFont.render(self.counterText, True, PINK)
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)
        self.nrTrialsCompletedText_debug = self.debuggingFont.render(self.nrTrials_string, True, [0,0,0])
        self.horse_upper_position_text = self.debuggingFont.render("Y_position horse = " + str(self.player.rect.top), True, [0,0,0])
        self.signal_value_retrieved_text = self.debuggingFont.render("Beta value of current trial = 0", True, [0,0,0])
        self.NF_target_value_text = self.debuggingFont.render("Neurofeedback threshold = 0", True, [0,0,0])
        self.current_beta_value_text =self.debuggingFont.render("(realtime) Beta = 0", True, [0,0,0])
        self.current_tvalue_text = self.debuggingFont.render("(realtime) T-value = 0", True, [0,0,0])
        self.data_window_info_text = self.debuggingFont.render(" " , True, [0,0,0])
        self.selected_channels_text = self.debuggingFont.render(" " , True, [0,0,0])
        self.gametype_text = self.debuggingFont.render("Neurofeedback", True, [0, 0, 0])


        #self.achieved_jump_position = "Achieved NF signal = " + str(self.player.ju)

        self.nrCoinsPerTrial = [0] * self.totalNum_TRIALS
        self.coinsCollectedInCurrentTrial = 0
        self.coinCollectedCounter = 0
        self.nrCoinsCollectedThroughoutRun = 0
        self.coinAlreadyBeingAdded = False
        self.nrCoinsCollectedText = self.mainFont.render(self.counterText, True, GOLD)
        self.coinOriginalStartingPosition_y = (SCREEN_HEIGHT - (SCREEN_HEIGHT*0.4) +60)
        self.coinStartingPosition_y = self.coinOriginalStartingPosition_y
        self.coinsBeingCounted = False
        self.freezeCoins = False

        self.scoreSaved = False
        self.printedNFdata = False

        self.achievedNFlevel = 1
        self.coins_that_should_be_collected = 3
        self.coins_to_collect_this_jump = 3  # Frozen at jump start to avoid mid-jump NF updates changing the target
        self.check_for_coin_collision = False
        self.signal_value_retrieved = 0
        self.maxJumpHeightAchieved = 0

        # Counter ( for countin down the seconds until game over)
        self.SECOND_HAS_PASSED = pygame.USEREVENT
        pygame.time.set_timer(self.SECOND_HAS_PASSED, 1000) # in ms


        self.task = False
        self.rest = False
        self.baseline = True
        self.horseJumpCounter = 1

        self.mainGame_background = 0

        self.signalValue_simulated =0


        # Reading premade protocol variables
        self.reachedTheTrials = False
        self.NrOfTrials = 0
        self.NrOfConditions = 0
        self.start_volumes = []
        self.end_volumes = []
        self.current_condition = 0
        self.timeForTaskEvent = False
        self.timeForRestEvent = False
        self.timeForJumpEvent = False
        self.horseHasJumpedThisTrial = False

    def get_FPS(self):
        return self.FPS

    def calculate_duration_game(self):

        n = self.totalNum_TRIALS

        print("Baseline duration: ", str(self.duration_BASELINE_s))
        print("Task duration: ", str(self.duration_TASK_s))
        print("Rest duration: ", str(self.duration_REST_s))
        print("Total nr of trial: " + str(n))

        duration_game_s = + self.duration_BASELINE_s + ((n+1) * self.duration_TASK_s) + ((n+1) * self.duration_REST_s) + 6 #How long you want to one game run to last (in seconds)
        # Other

        if self.performingSimulation:
            duration_game_s = duration_game_s + self.duration_REST_s # Add one extra rest trial duration, because otherwise the run ends too quickly

        print("Duration game (s): ", str(duration_game_s))

        return duration_game_s

    def get_deltaTime(self): # Get the current delta time
        return self.deltaTime

    def set_achieved_NF_level(self, achieved_NF_level):
        self.achievedNFlevel = achieved_NF_level

        # also immediately set the nr of coins that should be collected
        self.coins_that_should_be_collected = round(achieved_NF_level*10)
        if self.coins_that_should_be_collected < self.minimal_nr_of_coins:
            self.coins_that_should_be_collected = self.minimal_nr_of_coins # keep the minimum of coins collected to 3

    def setSamplingRate(self, samplingRate):
        self.samplingRate = samplingRate

    def startCountingCoins(self):
        self.coinsBeingCounted = True

    def display_exp_parameters(self, current_jittered_rest_duration):
        self.exp_parameters_text = self.debuggingFont.render("Task: " + str(self.duration_TASK_s) + "s, current rest: "+ str(current_jittered_rest_duration) + "s, jitter: "+ str(self.jitter_s) + "s",
                                                                   True, [0, 0, 0])

    def update_y_position_horse_text(self):
        self.horse_upper_position_text = self.debuggingFont.render("Y_position horse = " + str(self.player.rect.top),
                                                                   True, [0, 0, 0])

    def update_trial_nr_text(self):
        self.nrTrialsCompletedText_debug = self.debuggingFont.render("Trial " + str(self.trial_counter) + "/" + str(self.totalNum_TRIALS),
                                                                   True, [0, 0, 0])

    def update_jump_position_text(self):

        self.achieved_jump_height_text = self.debuggingFont.render(
            "Achieved NF level = " + str('{:.0f}%'.format(self.achievedNFlevel * 100)),
            True, [0, 0, 0]
        )

    def update_gametype_text(self, gametype):
        if gametype == "maingame":
            gametype = "neurofeeback"
            if self.DIFFERENTIAL_FEEDBACK > 0:
                self.gametype_text = self.debuggingFont.render(
                    "Game type: " + str(gametype) + " with differntial feedback", True, [0, 0, 0])

        else:
            self.gametype_text = self.debuggingFont.render(
            "Game type: " + str(gametype), True, [0, 0, 0])

        if self.TESTING_MODE:
            self.gametype_text = self.debuggingFont.render(
                "Game type: TESTING MODE", True, [0, 0, 0])


    def show_selected_channels(self,selected_channels):

        if self.DIFFERENTIAL_FEEDBACK == 0: # so if 0 or 1
            self.selected_channels_text = self.debuggingFont.render("Selected channel index: " + str(selected_channels[0] + 1), #todo: Note that I added +1 to make it more intuitive for users!
                                                                    True, [0, 0, 0])
        if len(selected_channels) > 1:
            if self.DIFFERENTIAL_FEEDBACK == 1: # so if 0 or 1
                self.selected_channels_text = self.debuggingFont.render("Selected channel indices: a=" + str(selected_channels[0] + 1) + " - b=" + str(selected_channels[1] + 1), #todo: Note that I added +1 to make it more intuitive for users!
                                                                        True, [0, 0, 0])
            if self.DIFFERENTIAL_FEEDBACK == 2:
                self.selected_channels_text = self.debuggingFont.render("Selected channel indices: b=" + str(selected_channels[1] + 1) + " - a=" + str(selected_channels[0] + 1), # Reverse the order
                                                                        True, [0, 0, 0])
        else:
            self.selected_channels_text = self.debuggingFont.render(
                "Selected channel index: " + str(selected_channels[0] + 1),
                True, [0, 0, 0])

    def update_retrieved_signal_value_text(self):
        if self.chromophore == 1:
            self.signal_value_retrieved_text = self.debuggingFont.render(("Beta " if self.dataType == 0 else "T-") +  "value (HbO) of current trial = " + str('{:.2f}'.format(self.signal_value_retrieved)),
                                                                   True, [0, 0, 0])
        if self.chromophore == 0:
            self.signal_value_retrieved_text = self.debuggingFont.render(("Beta " if self.dataType == 0 else "T-") + "value (Hb) of current trial = " + str('{:.2f}'.format(self.signal_value_retrieved)),
                                                                    True, [0, 0, 0])

    def update_NF_target_value_text(self,NF_maxLevel_based_on_localizer):
        self.NF_target_value_text = self.debuggingFont.render("NF target value = " + str('{:.2f}'.format(NF_maxLevel_based_on_localizer)),
                                                                   True, [0, 0, 0])
    def update_current_beta_value_text(self, current_beta):
        self.current_beta_value_text = self.debuggingFont.render("(realtime) Beta " + ("(HbO)" if self.chromophore == 1 else "(Hb)") + " = " + str('{:.2f}'.format(current_beta)),
                                                                   True, [0, 0, 0])
    def update_current_t_value_text(self,t_value):

        self.current_tvalue_text = self.debuggingFont.render("(realtime) T-value " + ("(HbO)" if self.chromophore == 1 else "(Hb)") + " = " + str('{:.2f}'.format(t_value)),
                                                                   True, [0, 0, 0])

    def update_data_window_info(self,collectTimewindowData):
        self.data_window_info_text= self.debuggingFont.render(("Collecting NF data! " if collectTimewindowData else " "),
                                                                   True, [0, 0, 0])




    def update_Taskcounter(self):
        self.trial_counter = self.trial_counter + 1  # Increase trial counter needed for timewindow beta measurements
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)

    def resetCoinStartingPosition(self):
        self.coinStartingPosition_y = self.coinOriginalStartingPosition_y

    def reset(self):
        self.all_sprites.empty()

    def change_settings_file(self, parameter, value):
        with open("GameSettings.json") as f:
            settings = json.load(f)  # Open settings file (json)
            # update and save back
            settings[parameter] = value  # Change the paramater

        with open("GameSettings.json", "w") as f:  # Save changes
            json.dump(settings, f, indent=2)

        print("Parameter " + parameter + " changed to: " + str(settings[parameter]))
    def apply_parameters_premadeprotocol_to_settings(self):
      #  self.change_settings_file("num_trials",self.totalNum_TRIALS)
       # self.change_settings_file("task_duration_s",self.duration_TASK_s)
        #self.change_settings_file("rest_duration_s",self.duration_REST_s)
        #self.change_settings_file("baseline_duration_s",self.duration_BASELINE_s)
        #self.change_settings_file("jitter_s",0) # todo: set to 0 for now, because it jsut affects the progress bar, not the datawindow

        print("Simulation mode: Calculating duration game based on read protocol file.")
        print("Baseline duration: ", str(self.duration_BASELINE_s))
        print("Task duration: ", str(self.duration_TASK_s))
        print("Rest duration: ", str(self.duration_REST_s))
        print("Total nr of trial: " + str(self.totalNum_TRIALS))

        self.durationGame_s = self.calculate_duration_game() # Recalculate this with the updated parameters
        self.nrCoinsPerTrial = [0] * self.totalNum_TRIALS  # Resize to match trial count from protocol file
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)

        #todo  Also got to adapt to jitter? or just always set to 0?




    def read_premade_protocol(self,samplingRate):
        time_resolution = 0 # 0 = volumes, 1= seconds

        print("READING PREMADE PROTOCOL FILE. ===========")
        try:
            with open(self.protocol_file_path, 'r') as file:
                lines = file.readlines()
                # print(lines)

            for line in lines:
                stripped_line = line.strip()
                # print(line)

                if stripped_line.startswith("ResolutionOfTime:"):
                    print(stripped_line)
                    temp = stripped_line.split(":")[1].strip()
                    print(temp)
                    if temp == "Volumes":
                        time_resolution = 0
                        print(" Time resolution PRT is in volumes.")
                    if temp == "Seconds":
                        time_resolution = 1
                        print(" Time resolution PRT is in seconds.")

                if stripped_line.startswith("NrOfConditions"):
                    self.NrOfConditions = int(stripped_line.split(":")[1].strip())
                    print("Number of Conditions: ", self.NrOfConditions)

                elif stripped_line.startswith("Color:"):
                    continue
                    # We ignore the Color lines for this task

                elif stripped_line.isdigit():
                    # print("Nr of trials: " + stripped_line)
                    # If the line is a single number, it's the number of trials for the current condition
                    self.NrOfTrials = int(stripped_line)
                    self.reachedTheTrials = True


                elif " " in stripped_line and self.reachedTheTrials:

                    if time_resolution == 0: # If in volumes:
                        # print("Trial: " + stripped_line)
                        tokens = stripped_line.split()  # split at the space
                        print(tokens)

                        if tokens[0].isdigit():
                            self.start_volumes.append(int(tokens[0]))
                        if tokens[1].isdigit():
                            self.end_volumes.append(int(tokens[1]))

                        print("Start volumes: ", str(self.start_volumes))
                        print("End volumes: ", str(self.end_volumes))

                        self.samplingRate = samplingRate
                       # print("Sampling rate: ", str(samplingRate[0]))


                        # convert to seconds
                        start_times_s = [v / self.samplingRate for v in self.start_volumes]
                        end_times_s = [v / self.samplingRate for v in self.end_volumes]

                    if time_resolution == 1: # if in seconds:
                        tokens = stripped_line.split()  # split at the space
                        #print(tokens)

                        if tokens[0].isdigit():
                            self.start_volumes.append(int(tokens[0]))
                        if tokens[1].isdigit():
                            self.end_volumes.append(int(tokens[1]))

                        print("Start times(s): ", str(self.start_volumes))
                        print("End times(s): ", str(self.end_volumes))

                        start_times_s = self.start_volumes
                        end_times_s = self.end_volumes



            # task durations
            task_durations = [end - start for start, end in zip(start_times_s, end_times_s)]

            rest_durations = [
                start_times_s[i + 1] - end_times_s[i]
                for i in range(len(end_times_s) - 1)
            ]
            print("Task durations: ", str(task_durations))
            print("Rest durations: ", str(rest_durations))

            # Set task and rest duration based on read PRT file
            self.duration_TASK_s = round(task_durations[0])
            self.duration_REST_s = round(rest_durations[0])
            self.duration_BASELINE_s = start_times_s[0] - self.duration_REST_s #

            print("Baseline duration: ", str(self.duration_BASELINE_s))
            print("Task duration: ", str(self.duration_TASK_s))
            print("Rest duration: ", str(self.duration_REST_s))

            trials_found = len(task_durations)
            if self.NrOfConditions < trials_found: # Means that the trials in the PRT are under 1 condition only
                print("Adjusting Nr of Conditions, because number of trials found was higher. Is now: ", + trials_found)
                self.NrOfConditions = trials_found

            if self.performingSimulation:  # only do this when actually in simulation mode
                self.totalNum_TRIALS = self.NrOfConditions  # todo: Update the total nr of trial based on the conditions found in the protocol file (each trial should be its own condition)
        except Exception as e:
            print(f"PRT ERROR: Something went wrong with reading the PRT for simulation! {e}")
            self.PRT_error = True

        return self.start_volumes, self.end_volumes, self.NrOfConditions

    def checkIfTaskOrRestCondition_PreMadeProtocol(self, current_volume_timepoint):
        if current_volume_timepoint is not None:
           # print("Current volume timepoint: " + str(current_volume_timepoint))
            if current_volume_timepoint < self.start_volumes[0]:
                self.current_condition = 0 # If the volume timepoint is before the first task, then it is the baseline condition
                #print("Baseline condition.") todo: turn these back on for debugging of simulation mode!
            else:
                if self.current_condition < self.totalNum_TRIALS:
                    # Check for start of new task
                    if current_volume_timepoint >= self.start_volumes[self.current_condition] and current_volume_timepoint < self.end_volumes[self.current_condition]:
                        self.current_condition += 1
                       # print("PREMADE PROTOCOL: New condition! Is now: " + str(self.current_condition))
                        self.timeForTaskEvent = True
                        self.horseHasJumpedThisTrial = False # Rest horse jump counter
                if self.current_condition <= self.totalNum_TRIALS:
                    # Check for end of task (and start of rest)
                    if current_volume_timepoint >= self.end_volumes[self.current_condition-1]:
                      #  print("PREMADE PROTOCOL: End of task condition " + str(self.current_condition) + ". Now rest period.") todo: turn these back on for debugging of simulation mode!
                        self.timeForRestEvent = True
                       # if current_volume_timepoint >= self.end_volumes[self.current_condition-1] + (self.timeUntilJump_s * self.samplingRate) and not self.player.HorseIsJumping:
                           #self.timeForJumpEvent = True

                           #print("PREMADE PROTOCOL: Time for jump event.")
            #print("Current trial: " + str(self.current_condition))

            return self.current_condition
        else:
            return 0


    def generate_protocol(self):
        task_duration = self.duration_TASK_s
        rest_duration_without_jitter = self.duration_REST_s
        baseline_duration = self.duration_BASELINE_s
        total_num_trials = self.totalNum_TRIALS

        min_rest_duration = rest_duration_without_jitter - self.jitter_s
        max_rest_duration = rest_duration_without_jitter + self.jitter_s

        task_start_times = {}
        rest_start_times = {}
        jump_start_times = {}
        previous_rest_start_time = baseline_duration + 0
        jittered_rest_duration = 0

        for trial_number in range(1, total_num_trials + 1):

            if trial_number == 1: # The first trial rest period is right after the baseline.
                rest_start_time = previous_rest_start_time
                jittered_rest_duration = rest_duration_without_jitter # No jitter for the first rest period
                self.jittered_rest_list.append(jittered_rest_duration)
                print('Jittered rest duration right after baseline = ', str(jittered_rest_duration))
                jittered_rest_duration = random.randint(min_rest_duration, max_rest_duration)  # Generate a new jittered rest duration for the next iteration
            else:
                self.jittered_rest_list.append(jittered_rest_duration)
                print('Jittered rest duration = ', str(jittered_rest_duration))
                rest_start_time = previous_rest_start_time + task_duration + jittered_rest_duration

                jittered_rest_duration = random.randint(min_rest_duration, max_rest_duration) # Generate a new jittered rest duration for the next iteration

            previous_rest_start_time = rest_start_time # update the previous_rest_start_time

            rest_start_times[trial_number] = rest_start_time
            if trial_number > 1:
                jump_start_times[trial_number-1] = rest_start_time + self.timeUntilJump_s

            task_start_time = rest_start_time + jittered_rest_duration
            task_start_times[trial_number] = task_start_time

            print("   Rest start time, trial " + str(trial_number) + " = " + str(rest_start_time))
            print("     Task start time, trial " + str(trial_number) + " = " + str(task_start_time))

        # Add the last rest period
        rest_start_time = previous_rest_start_time + task_duration + jittered_rest_duration
        rest_start_times[total_num_trials +1] = rest_start_time

        # Add the last jump period
        jump_start_times[total_num_trials] = rest_start_times[total_num_trials+1] + self.timeUntilJump_s

        print("Jittered rest list = " + str(self.jittered_rest_list))

        self.protocol_file['task_start_times'] = task_start_times
        self.protocol_file['rest_start_times'] = rest_start_times
        self.protocol_file['jump_start_times'] = jump_start_times

        print('Protocol generated. Task start times are:' + str(self.protocol_file['task_start_times']) + " and rest start times are: " + str(rest_start_times) + " and jump start times are: " + str(jump_start_times))

    def generate_dataCollection_protocol(self):
        datawindow_task_start_times = {}
        datawindow_task_end_times = {}
        datawindow_rest_start_times = {}
        datawindow_rest_end_times = {}

        task_duration = self.duration_TASK_s
        rest_duration = self.duration_REST_s
        total_num_trials = self.totalNum_TRIALS

        for trial_number in range(1, total_num_trials+1):
            datawindow_task_start_times[trial_number] = self.protocol_file['task_start_times'][trial_number] + self.datawindow_prestimulusonset_s
            datawindow_task_end_times[trial_number] = self.protocol_file['task_start_times'][trial_number] + task_duration + self.hemodynamic_delay

            #datawindow_rest_end_times[trial_number] = (self.protocol_file['task_start_times'][trial_number]) - 1
          #  datawindow_rest_start_times[trial_number] = datawindow_rest_end_times[trial_number] - self.duration_datawindow_rest

            self.protocol_file['datawindow_task_start_times'] = datawindow_task_start_times
            self.protocol_file['datawindow_task_end_times'] = datawindow_task_end_times
          #  self.protocol_file['datawindow_rest_start_times'] = datawindow_rest_start_times
          #  self.protocol_file['datawindow_rest_end_times'] = datawindow_rest_end_times

        print('Protocol for datacollection timings generated. Datawindow task start times are:' + str(
        datawindow_task_start_times) +  ", datawindow task end times are: " + str(datawindow_task_end_times) + ", datawindow rest start times are: " + str(
        datawindow_rest_start_times) + " and datawindow rest end times are: " + str(datawindow_rest_end_times))

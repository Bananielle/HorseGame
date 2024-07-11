import pygame
import random
# Colours

GOLD = (255, 184, 28)
PINK = (170, 22, 166)

class GameParameters():
    def __init__(self,player,rider,SCREEN_WIDTH,SCREEN_HEIGHT,):

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        # ADJUSTABLE PARAMETERS
        # paradigm
        self.folder = 'Horse'
        self.protocol_file = {
            'duration_TASK_s': 6,
            'duration_REST_s': 16,
            'totalNum_TRIALS': 10, # Set the number of times Task should occur
            'duration_BASELINE_s': 25, # Should be 25s
            'task_start_times': {},
            'rest_start_times': {},
            'jitter_s': 0
        }

        self.gameDifficulty = 3# 1 = easy (with bronze coins), 2 = medium (silver coins0, 3 = hard (gold coins). The higher the difficulty, the higher the max NF THRESHOLD, but the more points you get for collecting a coin.

        # Participant information
        self.taskUsed = 'Fingertapping'
        self.participantNr = 'P02'
        self.sessionNr = 'S02'
        self.runType = 'Localizer'
        self.runNr = '01'

        self.useSimulatedData = False
        self.usePreMadeProtocol = True
        self.saveIncomingData= True

        self.collectDataDuringRest = False

        self.draw_grid = False # For debugging purposes
        self.useFancyBackground = True

        self.totalNumCoins = 10

        self.gameType = ' ' # 'maingame' (NF) or 'localizer'
        self.duration_datawindow_rest = 6
        self.timeUntilRestDataCollection_s = 11 #self.protocol_file['duration_REST_s'] - 6 # Only start measuring the last 6 seconds before the new trial
        self.hemodynamic_delay = 3
        self.timeUntilJump_s = self.hemodynamic_delay + 1 # todo: note that this should be dependent on when the data window task collection ends
        self.duration_TASK_s = self.protocol_file['duration_TASK_s']
        self.duration_REST_s = self.protocol_file['duration_REST_s']
        self.totalNum_TRIALS = self.protocol_file['totalNum_TRIALS']
        self.duration_BASELINE_s = self.protocol_file['duration_BASELINE_s']
        self.durationGame_s = (self.protocol_file['duration_TASK_s'] + self.protocol_file['duration_REST_s'] ) * (self.protocol_file['totalNum_TRIALS']+1) + self.protocol_file['duration_BASELINE_s'] #How long you want to one game run to last (in seconds)
        # Other
        self.datawindow_task_start_time = self.duration_BASELINE_s + self.duration_REST_s+ self.hemodynamic_delay # for first trial - Add 3 seconds to account for the hemodynamic delay?
        self.datawindow_task_duration = self.duration_TASK_s  #6s to fully capture the peak of the hemodynamic response
        self.datawindow_task_end_time = self.datawindow_task_start_time + self.datawindow_task_duration

        self.datawindow_rest_start_time = self.duration_BASELINE_s   # No hemodynamic delay!
        self.datawindow_rest_duration = self.duration_REST_s
        self.datawindow_rest_end_time = self.datawindow_rest_start_time + self.datawindow_rest_duration

        self.samplingRate = 0 # dependent on what TSI inputs
        self.useBCIinput = True # If true, then player will be controlled by BCI input next to keyboard presses
        self.FPS = 20 # Frame rate. # Defines how often the the while loop is run through. E.g., an FPS of 60 will go through the while loop 60 times per second).
        # Note that you can check the computer's FPS by using clock.getFPS(). If it is lower than the FPS you specify here, the game might not work properly. (15 needed over windows FPN connection?)

        # Background markers for task and rest periods
        self.useExclamationMark = False # Shows a bright exclamation mark when a task starts
        self.useGreyOverlay = False # Overlays the screen with a grey overlay when a task starts
        self.usePath = False # If true, then a path will appear during the task trial
        self.useProgressBar = True # If true, then a loading bar will appear during the task trial
        self.debuggingText = True # If true, then debugging text will appear during the task trial

        self.currentTime_s = 0  #
        self.firstRestTrial = True

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



        # Time
        self.velocity = 1 # Determines general speed of all sprites (to ensure frame-rate independence)
        self.deltaTime = 1

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
        self.mainFont = pygame.font.SysFont('herculanum', 30, bold=True, )
        self.debuggingFont = pygame.font.SysFont('arial', 15, bold=False, )
        self.coinsCollectedFont = pygame.font.SysFont('herculanum', 40, bold=True, )
        self.gameTimeCounterText = self.mainFont.render(self.counterText, True, PINK)
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)
        self.horse_upper_position_text = self.debuggingFont.render("Y_position horse = " + str(self.player.rect.top), True, [0,0,0])
        #self.achieved_jump_position = "Achieved NF signal = " + str(self.player.ju)

        self.nrCoinsPerTrial = [0] * self.totalNum_TRIALS
        self.coinsCollectedInCurrentTrial = 0
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


    def setSamplingRate(self, samplingRate):
        self.samplingRate = samplingRate

    def startCountingCoins(self):
        self.coinsBeingCounted = True


    def update_y_position_horse_text(self):
        self.horse_upper_position_text = self.debuggingFont.render("Y_position horse = " + str(self.player.rect.top),
                                                                   True, [0, 0, 0])

    def update_jump_position_text(self):
        self.achieved_jump_height_text = self.debuggingFont.render("Achieved NF level = " + str('{:.2f}'.format(self.achievedNFlevel)),
                                                                   True, [0, 0, 0])

    def update_Taskcounter(self):
        self.trial_counter = self.trial_counter + 1  # Increase trial counter needed for timewindow beta measurements
        self.nrTrials_string = "Trial = " + str(self.TASK_counter) + "/" + str(self.totalNum_TRIALS)
        self.nrTrialsCompletedText = self.mainFont.render(self.nrTrials_string, True, PINK)

    def resetCoinStartingPosition(self):
        self.coinStartingPosition_y = self.coinOriginalStartingPosition_y

    def reset(self):
        self.all_sprites.empty()

    def generate_dataCollection_protocol(self):
        datawindow_task_start_times = {}
        datawindow_task_end_times = {}
        datawindow_rest_start_times = {}
        datawindow_rest_end_times = {}

        task_duration = self.protocol_file['duration_TASK_s']
        rest_duration = self.protocol_file['duration_REST_s']
        total_num_trials = self.protocol_file['totalNum_TRIALS']

        for trial_number in range(1, total_num_trials+1):
            datawindow_task_start_times[trial_number] = self.protocol_file['task_start_times'][trial_number] + self.hemodynamic_delay
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

    def read_premade_protocol(self):
        file_path = 'Protocol for replay/NFrun6trials.prt'
        print("READING PREMADE PROTOCOL FILE. ===========")
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # print(lines)

        for line in lines:
            stripped_line = line.strip()
            # print(line)

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
                # print("Trial: " + stripped_line)
                start_and_end_volume = stripped_line.split(" ")  # split at the space

                if start_and_end_volume[0].isdigit() and int(start_and_end_volume[
                                                                 0]) > 10:  # Check if a digit and larger than 10 (because we are working in volumes, so number will be in the hundreds)
                    self.start_volumes.append(int(start_and_end_volume[0]))
                if start_and_end_volume[1].isdigit():
                    if int(start_and_end_volume[1]) > 10:
                        self.end_volumes.append(int(start_and_end_volume[1]))
                elif start_and_end_volume[2].isdigit():
                    self.end_volumes.append(int(start_and_end_volume[2]))

        print("Start volumes: ", str(self.start_volumes))
        print("End volumes: ", str(self.end_volumes))

        return self.start_volumes, self.end_volumes, self.NrOfConditions

    def getCurrentConditionFromProtocol(self,current_volume_timepoint):
        if current_volume_timepoint is not None:
           # print("Current volume timepoint: " + str(current_volume_timepoint))
            if current_volume_timepoint < self.start_volumes[0]:
                self.current_condition = 0 # If the volume timepoint is before the first task, then it is the baseline condition
                print("Baseline condition.")
            else:
                if self.current_condition < self.totalNum_TRIALS:
                    # Check for start of new task
                    if current_volume_timepoint >= self.start_volumes[self.current_condition] and current_volume_timepoint < self.end_volumes[self.current_condition]:
                        self.current_condition += 1
                        print("PREMADE PROTOCOL: New condition! Is now: " + str(self.current_condition))
                        self.timeForTaskEvent = True
                        self.horseHasJumpedThisTrial = False # Rest horse jump counter
                    # Check for end of task (and start of rest)
                    if current_volume_timepoint >= self.end_volumes[self.current_condition-1]:
                        print("PREMADE PROTOCOL: End of task condition " + str(self.current_condition) + ". Now rest period.")
                        self.timeForRestEvent = True
                       # if current_volume_timepoint >= self.end_volumes[self.current_condition-1] + (self.timeUntilJump_s * self.samplingRate) and not self.player.HorseIsJumping:
                           #self.timeForJumpEvent = True

                           #print("PREMADE PROTOCOL: Time for jump event.")
            #print("Current trial: " + str(self.current_condition))

            return self.current_condition
        else:
            return 0


    def generate_protocol(self):
        task_duration = self.protocol_file['duration_TASK_s']
        rest_duration_without_jitter = self.protocol_file['duration_REST_s']
        baseline_duration = self.protocol_file['duration_BASELINE_s']
        total_num_trials = self.protocol_file['totalNum_TRIALS']

        min_rest_duration = rest_duration_without_jitter - self.protocol_file['jitter_s']
        max_rest_duration = rest_duration_without_jitter + self.protocol_file['jitter_s']

        task_start_times = {}
        rest_start_times = {}
        jump_start_times = {}
        previous_rest_start_time = baseline_duration + 0
        jittered_rest_duration= 0

        for trial_number in range(1, total_num_trials + 1):

            if trial_number == 1: # The first trial rest period is right after the baseline.
                rest_start_time = previous_rest_start_time
                jittered_rest_duration = rest_duration_without_jitter # No jitter for the first rest period
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

        print('Protocol generated. Task start times are:' + str(task_start_times) + " and rest start times are: " + str(rest_start_times) + " and jump start times are: " + str(jump_start_times))

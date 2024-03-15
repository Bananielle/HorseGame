import pygame
import _turbosatorinetworkinterface as tsi  # handles getting data from TSI
import numpy as np
import CSVwriter
import datetime
import matplotlib.pyplot as plt

from pygame.locals import (
    K_UP,
    K_DOWN,

)

class BrainComputerInterface():
    def __init__(self,typeOfRun,gameParameters):


        self.useMean = False # Use the mean amplitude for NF calculation
        self.useMax = False # Use the max amplitude for NF calculation
        self.useLatestDataPoint = True # Use the latest data point for NF calculation

        self.NF_maxLevel_based_on_localizer = 0.24  # This is the max level for the NF signal that people can reach

        self.NFsignal_mean = 1
        self.NFsignal_max = self.NF_maxLevel_based_on_localizer/2 # Starter values
        self.NFSignal_median =1
        self.NFSignal_latestValue = 1

        self.gp = gameParameters
        self.saveIncomingData = self.gp.saveIncomingData
        self.typeOfRun = typeOfRun # localizer or maingame (NF) run
        self.simulatedData_filepath = "Data/"
        self.previousRetrievedTimePoint = 0
        self.currentRetrievedTimePoint = 0
        self.testDataList = []
        self.timepointList = []
        self.reactionTimeList = []
        self.incomingDataList_betas = []
        self.incomingDataList_oxy = []
        self.incomingDataList_condition = []
        self.currentInput = 0
        self.previousInput = 0
        self.fakeInput = 0
        self.TSIconnectionFound = True
        self.timeBetweenSamples_ms = 1000
        self.collectTimewindowData= False
        self.timewindow_task = []
        self.timewindow_rest = []
        self.startTimeMeasurement = 0
        self.NFsignal = {"Trials": [], "NFsignal_mean_TASK": [], "NFsignal_max_TASK": [], "NFsignal_median_TASK": [],
                         "NFsignal_latestValue_TASK": [], "NF_MaxThresholdUsed": [],
                         "AchievedNFLevel": [], "MaxJumpHeightAchieved": [], "CoinsCollected":[]}

        self.currentTask_signal = 1
        self.currentRest_signal = 1

        # CSV file preparation
        # Define the field names (header) for your CSV file
        #self.field_names = ['Trials','NFsignal_mean_TASK', 'NFsignal_max_TASK', 'NFSignal_median_TASK', 'NFsignal_mean_REST', 'NFsignal_max_REST',
        #               'NFSignal_median_REST', 'NF_MaxThreshold',"CoinsCollected"]

        self.field_names = ['Trials', 'NFsignal_mean_TASK', 'NFsignal_max_TASK','NFsignal_median_TASK','NFsignal_latestValue_TASK',
                             'NF_MaxThresholdUsed', "AchievedNFLevel", "MaxJumpHeightAchieved", "CoinsCollected"] #TODO rest values are removed here, because we're currently not using them.

        # Look for a connection to turbo-satori
        try:
            self.tsi = tsi.TurbosatoriNetworkInterface("127.0.0.1", 55556)
            print("Turbo satori connection successful.")
        except:
            # None found? Let the user know
            self.TSIconnectionFound = False
            print("Turbo satori connection not found.")

        if self.TSIconnectionFound:
            self.timeBetweenSamples_ms = 200  # self.establishTimeInBetweenSamples() todo NOTE THAT IT DATA IS NOW COLLECTED ONLY EVERY SECOND

        self.GET_TURBOSATORI_INPUT = pygame.USEREVENT + 7
        pygame.time.set_timer(self.GET_TURBOSATORI_INPUT, self.timeBetweenSamples_ms) #self.timeBetweenSamples_ms) # I have to give it integers... todo: NOTE THAT IT DATA IS NOW COLLECTED ONLY EVERY SECOND

    # Do a continous measurement to get oxy data of the whole run
    def continuousMeasuring(self,trialNr):
        if self.saveIncomingData and self.TSIconnectionFound:
            currentTimePoint = self.tsi.get_current_time_point()[0]

            self.getNewData(trialNr)
            #betas = self.getBetas(trialNr)
            #oxy = self.scaleOxyData()
            #condition = self.tsi.get_protocol_condition(currentTimePoint - 1)[0] # Because it requires a buffer of 4 bytes?

            #self.saveIncomingDataToList_betas(betas)
            #self.saveIncomingDataToList_oxy(oxy)
            #self.saveIncomingDataToList_condition(condition)
            #print("Current condition: " + str(condition))

    def startMeasuring(self, task, simulatedData,trialNr):
        scaled_data = 0
        if self.TSIconnectionFound:
            scaled_data = self.getBetas(trialNr)
            #scaled_data = self.scaleOxyData()
            #scaled_data = self.getNewDataForNF()
        elif simulatedData is not 0: # But use simulated data instead if it's available
            scaled_data = simulatedData

        if self.collectTimewindowData:
            if task:
                self.timewindow_task.append(scaled_data)
            else:
                self.timewindow_rest.append(scaled_data)

       # if self.saveIncomingData:
         #   self.saveIncomingDataToList(scaled_data)

        return scaled_data

    def saveIncomingDataToList_betas(self, data):
        self.incomingDataList_betas.append(data)

    def saveIncomingDataToList_oxy(self, data):
        self.incomingDataList_oxy.append(data)

    def saveIncomingDataToList_condition(self, data):
        self.incomingDataList_condition.append(data)

    def resetTimewindowDataArray(self):
        self.timewindow_task = []
        self.timewindow_rest = []

    def addCoinsCollectedDuringCurrentTrial(self,coinsCollectedInCurrentTrial):
        self.NFsignal["CoinsCollected"].append(coinsCollectedInCurrentTrial)  # Save the number of coins collected for each trial
        print("Coins collected for this trial: " + str(coinsCollectedInCurrentTrial))
        print("NFsignal dictionary: " + str(self.NFsignal))

    def addAchievedNFlevel(self, achievedNFLevel):
        self.NFsignal["AchievedNFLevel"].append(achievedNFLevel)  # Save the number of coins collected for each trial

    def addMaxJumpHeightAchieved(self, maxJumpHeightAchieved):
        self.NFsignal["MaxJumpHeightAchieved"].append(maxJumpHeightAchieved)  # Save the number of coins collected for each trial

    def calculateNFsignal(self, task):

        if task:
            NFsignal_raw = np.array(self.timewindow_task) # Array of all incoming oxy values.
        else: # If measurement is from the rest period
            NFsignal_raw = np.array(self.timewindow_rest)

        self.NFsignal_mean = np.mean(NFsignal_raw)
        self.NFsignal_max = np.max(NFsignal_raw)
        self.NFSignal_median = np.median(NFsignal_raw)
        self.NFSignal_latestValue = NFsignal_raw[-1] # The latest value of the array

        print("NFsignal_raw: " + str(NFsignal_raw))
        print("NFsignal_mean: " + str(self.NFsignal_mean) + ", NFsignal_max: " + str(self.NFsignal_max) + ", NFSignal_median: " + str(self.NFSignal_median) + ", NFSignal_latestValue: " + str(self.NFSignal_latestValue))

        # Save the variables to a dictionary
        if task:
            self.currentTask_signal = self.NFsignal_mean # Save the current task signal for PSC calculation

            self.NFsignal["NFsignal_mean_TASK"].append(self.NFsignal_mean)
            self.NFsignal["NFsignal_max_TASK"].append(self.NFsignal_max)
            self.NFsignal["NFsignal_median_TASK"].append(self.NFSignal_median)
            self.NFsignal["NFsignal_latestValue_TASK"].append(self.NFSignal_latestValue)

        print("NFsignals stored: " + str(self.NFsignal))


    def get_achieved_NF_level(self):

        if self.useMean:
            achieved_NF_signal = self.NFsignal_mean / self.NF_maxLevel_based_on_localizer
        if self.useMax:
            achieved_NF_signal = self.NFsignal_max / self.NF_maxLevel_based_on_localizer
        if self.useLatestDataPoint: # takes the latest data point for each trial
            achieved_NF_signal = self.NFSignal_latestValue / self.NF_maxLevel_based_on_localizer
        #print("achieved_NF_signal: " + str(achieved_NF_signal))

        # Add a ceiling and floor to the achieved NF signal
        if achieved_NF_signal > 1:
            achieved_NF_signal = 1
        if achieved_NF_signal < 0:
            achieved_NF_signal = 0

        return achieved_NF_signal

    def calculate_NF_max_threshold(self):
        # Calculate the mean of the NFsignal_mean values in the NFsignal dictionary
        NFsignal_mean = np.mean((self.NFsignal["NFsignal_mean_TASK"]))
        NFsignal_max = np.mean((self.NFsignal["NFsignal_max_TASK"]))
        NFSignal_median = np.mean((self.NFsignal["NFsignal_median_TASK"]))
        NFSignal_mean_latestValue = np.mean((self.NFsignal["NFsignal_latestValue_TASK"])) # Mean of the all latest value of each trial
        maxtrials = len(self.NFsignal["NFsignal_mean_TASK"]) + 1  # +2 because Python starts at 0 for the array
        trialIndex = list(range(1, maxtrials))
        self.NFsignal["Trials"] = trialIndex

        # Print the mean of the NFsignal_mean values
        print("End of run. NFsignal_mean_TASK: " + str(NFsignal_mean) + ", NFsignal_max_TASK: " + str(
            NFsignal_max) + ", NFsignal_median_TASK: " + str(NFSignal_median) + ", NFsignal_mean_latestValue: " + str(NFSignal_mean_latestValue))

        print("Max signal amplitude reached of max betas: " + str(NFsignal_max))
        print("Mean signal amplitude reached of mean betas: " + str(NFsignal_mean))
        print("Mean signal amplitude reached of latest beta data point: " + str(NFSignal_mean_latestValue))

        # Save NF values to CSV files
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        print(current_date)
        self.NFsignal["NF_MaxThresholdUsed"].append(self.NF_maxLevel_based_on_localizer)
        self.save_NFdatalog_to_csv()

        # Save the incoming data (both oxy and betas) from the whole run to a csv file
        #filename = f"betavalues_{current_date}.csv"
        #self.save_list_to_csv(list(zip(self.incomingDataList_condition, self.incomingDataList_betas)), filename)

        #filename = f"oxyvalues{current_date}.csv"
        #self.save_list_to_csv(list(zip(self.incomingDataList_condition, self.incomingDataList_oxy)), filename)

        #filename = f"reactiontimes{current_date}.csv"
        #self.save_list_to_csv(self.reactionTimeList, filename)

        print(self.testDataList)
        filename = f"RunRecording_betas_{current_date}.csv"
        data = list(zip(self.timepointList,self.testDataList,self.reactionTimeList))
        print(data)
        self.save_list_to_csv(data, filename)

       # filename = f"timepointlist{current_date}.csv"
       # self.save_list_to_csv(self.timepointList, filename)

        # Show boxplot of the NFsignal_mean and NFsignal_max values
        #self.show_boxplot(self.NFsignal["NFsignal_mean_TASK"], "Mean amplitude")
        #self.show_boxplot(self.NFsignal["NFsignal_max_TASK"], "Max amplitude")

    def show_boxplot(self, data, ylabel):
        fig, ax = plt.subplots()
        ax.boxplot(data, showfliers=True)

        # Overlay individual data points using swarmplot
        plt.scatter([1] * len(data), data, color='blue', alpha=0.7)

        # Add labels and title
        ax.set_xlabel('Localizer')
        ax.set_ylabel(ylabel)
        title = [ylabel + " across localizer trials."]
        ax.set_title(title)

        plt.show()

    def getCurrentTimePoint(self):
        currentTimePoint, rt = self.tsi.get_current_time_point()
        #print("Current time point: " + str(currentTimePoint) + ", rt: " + str(rt))

        return currentTimePoint,rt

    def didNewDataArrive(self):
        self.previousRetrievedTimePoint = self.currentRetrievedTimePoint
        self.currentRetrievedTimePoint = self.getCurrentTimePoint()

        if self.currentRetrievedTimePoint != self.previousRetrievedTimePoint:
            return True
        else:
            return False

    def getNewData(self,trialNr):
        if self.didNewDataArrive():
            timepoint,rt = self.getCurrentTimePoint()
            sampling_rate = self.tsi.get_sampling_rate()[0]

            # Get oxy
            selectedChannels = self.tsi.get_selected_channels()[0]
            oxy = self.tsi.get_data_oxy(selectedChannels[0], timepoint-1)[0]

            # Apply scale factor to oxy
            scalefactor = self.tsi.get_oxy_data_scale_factor()  # Turbo-Satori's default is 200 as a scale factor
            scaled_data = float(oxy) * float(scalefactor[0])  # Because for some reason you're getting two values for TSI's scacefactor

            scaled_data = self.getBetas(trialNr)

            self.testDataList.append(scaled_data)
            self.timepointList.append(timepoint)
            self.reactionTimeList.append(rt)

            print("New data arrived! Timepoint: " + str(timepoint) + ", rt: " + str(rt), ", oxy = " + str(scaled_data) + ", sampling rate = " + str(sampling_rate))

            return scaled_data

    def getNewDataForNF(self):
        timepoint, rt = self.getCurrentTimePoint()
        sampling_rate = self.tsi.get_sampling_rate()[0]

        # Get oxy
        selectedChannels = self.tsi.get_selected_channels()[0]
        oxy = self.tsi.get_data_oxy(selectedChannels[0], timepoint - 1)[0]

        # Apply scale factor to oxy
        scalefactor = self.tsi.get_oxy_data_scale_factor()  # Turbo-Satori's default is 200 as a scale factor
        scaled_data = float(oxy) * float(
            scalefactor[0])  # Because for some reason you're getting two values for TSI's scacefactor


        print("New data arrived! Timepoint: " + str(timepoint) + ", rt: " + str(rt),
              ", oxy = " + str(scaled_data) + ", sampling rate = " + str(sampling_rate))

        return scaled_data


    def set_NF_max_threshold(self,NFsignal_max):
        self.NF_maxLevel_based_on_localizer = NFsignal_max
        print("NF_maxLevel set to: " + str(self.NF_maxLevel_based_on_localizer))

    def getCurrentOxyInput(self):
        if self.TSIconnectionFound:
            currentTimePoint = self.tsi.get_current_time_point()[0]
            selectedChannels = self.tsi.get_selected_channels()[0]
            oxy = self.tsi.get_data_oxy(selectedChannels[0], currentTimePoint - 1)[0] # -1 Because timepoint var starts at 1
            input = oxy
            #print("Current time point: " + str(currentTimePoint), ", selected channels: " + str(Selected) + " , oxy: " + str(oxy))

        else:
            input = 0

        return input

    # The trial number gets the predictor for each trial (trial 1 for first predictor, trial 2 for second predictor etc)
    def getBetas(self,trialNr):
        if self.TSIconnectionFound:

            selectedChannels = self.tsi.get_selected_channels()[0]
            print('Selected channel = ' + str(selectedChannels[0]))
            betas = self.tsi.get_beta_of_channel(selectedChannels[0],beta=trialNr-1, chromophore=1)[0] # -1 Because trial starts at 1 but indexing starts at 0 # doesn't need a timepoint because it just checks the latest betas
            print("Betas (condition per trial): " + str(betas), " for trial: " + str(trialNr))

            # For debugging
           # betas_one = self.tsi.get_beta_of_channel(selectedChannels[0], beta=0, chromophore=1)[0]  #  Only get the beta's for all trials as one condition
           # print("Betas (one condition): " + str(betas_one), " for trial: " + str(trialNr))

            return betas



    def scaleOxyData(self):
        if self.TSIconnectionFound:
            oxy = self.getCurrentOxyInput()
            scalefactor = self.tsi.get_oxy_data_scale_factor() # Turbo-Satori's default is 200 as a scale factor

            scaled_data = float(oxy) * float(scalefactor[0]) # Because for some reason you're getting two values for TSI's scacefactor

        #print("Scaled oxy: " + str(scaled_data) + ", scalefactor: " + str(scalefactor[0]))

        else:
            scaled_data = 0

        return scaled_data

    def getKeyboardPressFromBrainInput(self):
        scaledOxyData = self.scaleOxyData()

        self.previousInput = self.currentInput
        self.currentInput = scaledOxyData

       # print("Current input: " + str(self.currentInput) + ", previous input: " + str(self.previousInput))

        keyboardPress = self.translateToKeyboardPress(self.currentInput, self.previousInput)

        return keyboardPress

    def translateToKeyboardPress(self, currentInput, previousInput):
        keyboardPress = 0
        if currentInput > previousInput:
            keyboardPress = K_UP
        if currentInput < previousInput:
            keyboardPress = K_DOWN
        if currentInput == previousInput:
            keyboardPress = False

        return keyboardPress

    # with current data its 7.8125 samples per second. So a sample every 128ms.
    def establishTimeInBetweenSamples(self):
        samplingRate = self.tsi.get_sampling_rate()
        timeBetweenSamples_ms = int(1000 / samplingRate[0])
        print("Sampling rate = "+  str(self.tsi.get_sampling_rate()) + ", so " + str(timeBetweenSamples_ms) + "ms inbetween samples.")

        return timeBetweenSamples_ms

# =============================  MAIN LOG for NF and game data
    # CSV writer
    def save_NFdatalog_to_csv(self):
        csvWriter = CSVwriter.CSVwriter()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if self.typeOfRun == "localizer":
            filename = f"NF_datalog_localizer_{current_date}.csv"
        else:
            filename = f"NF_datalog_NFrun_{current_date}.csv"
        csvWriter.save_dict_to_csv(filename, self.field_names, self.NFsignal)

    def save_list_to_csv(self, data,filename):

        csvWriter = CSVwriter.CSVwriter()
        csvWriter.save_list_to_csv(data, filename)


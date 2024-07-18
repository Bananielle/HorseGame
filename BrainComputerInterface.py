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

        self.NF_maxLevel_based_on_localizer = 1.06  # This is the max level for the NF signal that people can reach

        self.NFsignal_mean = 1
        self.NFsignal_max = self.NF_maxLevel_based_on_localizer/2 # Starter values
        self.NFSignal_median =1
        self.NFSignal_latestValue = 1
        self.NFSignal_latestValue_t_value = 1

        self.gp = gameParameters
        self.saveIncomingData = self.gp.saveIncomingData
        self.typeOfRun = typeOfRun # localizer or maingame (NF) run
        self.simulatedData_filepath = "Data/"
        self.previousRetrievedTimePoint = 0
        self.currentRetrievedTimePoint = 0
        self.recordedBetas = []
        self.timepointList = [] # Not used anymore
        self.reactionTimeList = [] # Not used anymore
        self.incomingDataList_betas = []
        self.incomingDataList_oxy = []
        self.incomingDataList_condition = []
        self.currentInput = 0
        self.previousInput = 0
        self.fakeInput = 0
        self.TSIconnectionFound = True
        self.timeBetweenSamples_ms = 1000 # So 1 second!
        self.collectTimewindowData= False
        self.timewindow_task = []
        self.timewindow_task_tvalues = []
        self.timewindow_task_betas = []
        self.timewindow_rest = []
        self.startTimeMeasurement = 0
        self.nrOfChannels = 10
        self.timewindow_allChannels_data = {}
        self.allChannels_latestBetaValue = []
        for channel in range (0,self.nrOfChannels):
            self.timewindow_allChannels_data[channel] = []



        self.NFsignal = {"Trials": [], "NFsignal_mean_TASK": [], "NFsignal_max_TASK": [], "NFsignal_median_TASK": [],
                         "NFsignal_latestValue_TASK": [], "NFsignal_latestValue_TASK_t_value":[], "NFsignal_latestValue_TASK_beta":[], "NF_MaxCalculatedThreshold_Q3_120": [], "NF_MaxThresholdUsed": [],
                         "AchievedNFLevel": [], "MaxJumpHeightAchieved": [], "CoinsCollected":[]}

        self.currentTask_signal = 1
        self.currentRest_signal = 1

        # CSV file preparation
        # Define the field names (header) for your CSV file
        #self.field_names = ['Trials','NFsignal_mean_TASK', 'NFsignal_max_TASK', 'NFSignal_median_TASK', 'NFsignal_mean_REST', 'NFsignal_max_REST',
        #               'NFSignal_median_REST', 'NF_MaxThreshold',"CoinsCollected"]

        self.field_names = ['Trials', 'NFsignal_mean_TASK', 'NFsignal_max_TASK','NFsignal_median_TASK','NFsignal_latestValue_TASK', "NFsignal_latestValue_TASK_t_value", "NFsignal_latestValue_TASK_beta",
                             'NF_MaxThresholdUsed',"NF_MaxCalculatedThreshold_Q3_120", "AchievedNFLevel", "MaxJumpHeightAchieved", "CoinsCollected"] #TODO rest values are removed here, because we're currently not using them.

        # Look for a connection to turbo-satori
        try:
            self.tsi = tsi.TurbosatoriNetworkInterface("127.0.0.1", 55556)
            print("Turbo satori connection successful.")
        except:
            # None found? Let the user know
            self.TSIconnectionFound = False
            print("Turbo satori connection not found.")

        #if self.TSIconnectionFound:
          #  self.timeBetweenSamples_ms = self  # self.establishTimeInBetweenSamples() todo NOTE THAT IT DATA IS NOW COLLECTED ONLY EVERY SECOND

        self.GET_TURBOSATORI_INPUT = pygame.USEREVENT + 7
        pygame.time.set_timer(self.GET_TURBOSATORI_INPUT, self.timeBetweenSamples_ms) #self.timeBetweenSamples_ms) # I have to give it integers... todo: NOTE THAT IT DATA IS NOW COLLECTED ONLY EVERY SECOND


    def getSamplingRate(self):
        if self.TSIconnectionFound:
            return self.tsi.get_sampling_rate()[0]
        else:
            return 0

    def getCurrentTimePoint_TSI(self):

        if self.TSIconnectionFound:
            current_time_point = self.tsi.get_current_time_point()
        else:
            current_time_point = self.gp.currentTime_s

        return current_time_point

    # Do a continous measurement to get oxy data of the whole run
    def continuousMeasuring(self,trialNr):
        if self.saveIncomingData and self.TSIconnectionFound:
            volume_timepoint = self.getNewData(trialNr)
            #betas = self.getBetas(trialNr)
            #oxy = self.scaleOxyData()
            #condition = self.tsi.get_protocol_condition(currentTimePoint - 1)[0] # Because it requires a buffer of 4 bytes?

            #self.saveIncomingDataToList_betas(betas)
            #self.saveIncomingDataToList_oxy(oxy)
            #self.saveIncomingDataToList_condition(condition)
            #print("Current condition: " + str(condition))
            return volume_timepoint
        else:
            return None


    def startMeasuring(self, task, simulatedData,trialNr):
        scaled_data = 0
        if self.TSIconnectionFound:
            betas = self.getBetas(trialNr)
            t_values = self.getTvalues(trialNr)
            #all_data = self.getBetasForAllChannels(trialNr)sf sfdfs
            #print(all_data)
            #scaled_data = self.scaleOxyData()
            #scaled_data = self.getNewDataForNF()

            scaled_data = betas

        elif simulatedData is not 0: # But use simulated data instead if it's available
            scaled_data = simulatedData

        if self.collectTimewindowData:
            if task:
                self.timewindow_task.append(scaled_data)
                self.timewindow_task_tvalues.append(t_values)
                self.timewindow_task_betas.append(betas)
                print("Appending scaled data to timewindow_task..." + str(scaled_data))

                # Also collect data from other channels (needed for NF threshold calculation during the Motor Imagery Localizer)
                for channel in range(0,self.nrOfChannels):
                    channel_betas = self.getBetasForAllChannels(channel,trialNr)
                    self.timewindow_allChannels_data[channel].append(channel_betas)
            else:
                self.timewindow_rest.append(scaled_data)

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
            NFsignal_raw_tvalues = np.array(self.timewindow_task_tvalues)
            NFsignal_raw_betas = np.array(self.timewindow_task_betas)
            NFsignal_allChannels_raw = self.timewindow_allChannels_data
            print("All Channels: "+ str(self.timewindow_allChannels_data))
        else: # If measurement is from the rest period
            NFsignal_raw = np.array(self.timewindow_rest)

        print("Timewindow task = " + str(self.timewindow_task))

        # Channel of Interest
        self.NFsignal_mean = round(np.mean(NFsignal_raw),2)
        self.NFsignal_max = round(np.max(NFsignal_raw),2)
        self.NFSignal_median = round(np.median(NFsignal_raw),2)
        self.NFSignal_latestValue = round(NFsignal_raw[-1],2) # The latest value of the array

        # Get latest beta-value
        self.NFSignal_latestValue_beta = round(NFsignal_raw_betas[-1], 2)

        # Get latest t-value
        self.NFSignal_latestValue_t_value = round(NFsignal_raw_tvalues[-1],2)

        # All Channels
        for channel in range(0,self.nrOfChannels):
            self.allChannels_latestBetaValue.append(NFsignal_allChannels_raw[channel][-1])

        print("All Channels latest beta value: " + str(self.allChannels_latestBetaValue))

        print("NFsignal_raw: " + str(NFsignal_raw))
        print("NFsignal_mean: " + str(self.NFsignal_mean) + ", NFsignal_max: " + str(self.NFsignal_max) + ", NFSignal_median: "
              + str(self.NFSignal_median) + ", NFSignal_latestValue: " + str(self.NFSignal_latestValue)
              + ", NFSignal_latestValue_t_value: " + str(self.NFSignal_latestValue_t_value) + ", NFSignal_latestValue_beta:" + str(self.NFSignal_latestValue_beta))


        # Save the variables to a dictionary
        if task:
            self.currentTask_signal = self.NFsignal_mean # Save the current task signal for PSC calculation

            self.NFsignal["NFsignal_mean_TASK"].append(self.NFsignal_mean)
            self.NFsignal["NFsignal_max_TASK"].append(self.NFsignal_max)
            self.NFsignal["NFsignal_median_TASK"].append(self.NFSignal_median)
            self.NFsignal["NFsignal_latestValue_TASK"].append(self.NFSignal_latestValue)
            self.NFsignal["NFsignal_latestValue_TASK_t_value"].append(self.NFSignal_latestValue_t_value)
            self.NFsignal["NFsignal_latestValue_TASK_beta"].append(self.NFSignal_latestValue_t_value)

        print("NFsignals stored: " + str(self.NFsignal))


    def get_achieved_NF_level(self):

        signal_value_used = 0

        if self.useMean:
            achieved_NF_signal = self.NFsignal_mean / self.NF_maxLevel_based_on_localizer
            signal_value_retrieved =  self.NFsignal_mean
        if self.useMax:
            achieved_NF_signal = self.NFsignal_max / self.NF_maxLevel_based_on_localizer
            signal_value_retrieved =  self.NFsignal_max

        if self.useLatestDataPoint: # takes the latest data point for each trial
            achieved_NF_signal = self.NFSignal_latestValue / self.NF_maxLevel_based_on_localizer
            signal_value_used = self.NFSignal_latestValue
        #print("achieved_NF_signal: " + str(achieved_NF_signal))

        # Add a ceiling and floor to the achieved NF signal
        if achieved_NF_signal > 1:
            achieved_NF_signal = 1
        if achieved_NF_signal < 0:
            achieved_NF_signal = 0

        return round(achieved_NF_signal,2),round(signal_value_used,2)

    def calculate_NF_max_threshold(self):
        # Calculate the mean of the NFsignal_mean values in the NFsignal dictionary
        NFsignal_mean = round(np.mean((self.NFsignal["NFsignal_mean_TASK"])),2)
        NFsignal_max = round(np.mean((self.NFsignal["NFsignal_max_TASK"])),2)
        NFSignal_median = round(np.mean((self.NFsignal["NFsignal_median_TASK"])),2)
        NFSignal_mean_latestValue = round(np.mean((self.NFsignal["NFsignal_latestValue_TASK"])),2) # Mean of the all latest value of each trial
        NFSignal_Q3_latestValue = round(np.percentile((self.NFsignal["NFsignal_latestValue_TASK"]), 75),2) # Third quartile of the latest value of each trial
        NFSignal_Q3_120 = round((NFSignal_Q3_latestValue * 1.2),2)
        # C


        maxtrials = len(self.NFsignal["NFsignal_mean_TASK"]) + 1  # +2 because Python starts at 0 for the array
        trialIndex = list(range(1, maxtrials))
        self.NFsignal["Trials"] = trialIndex

        # Print the mean of the NFsignal_mean values
        print("End of run. NFsignal_mean_TASK: " + str(NFsignal_mean) + ", NFsignal_max_TASK: " + str(
            NFsignal_max) + ", NFsignal_median_TASK: " + str(NFSignal_median) + ", NFsignal_mean_latestValue: " + str(NFSignal_mean_latestValue))

        print("Max signal amplitude reached of max betas: " + str(NFsignal_max))
        print("Mean signal amplitude reached of mean betas: " + str(NFsignal_mean))
        print("Mean signal amplitude reached of latest beta data points: " + str(NFSignal_mean_latestValue))
        print("Third quartile of latest beta data points: "  + str(NFSignal_Q3_latestValue))
        print("NF threshold based on Q3 * 120%: " + str(NFSignal_Q3_120))

        # Save NF values to CSV files
        self.NFsignal["NF_MaxCalculatedThreshold_Q3_120"].append(NFSignal_Q3_120)
        self.NFsignal["NF_MaxThresholdUsed"].append(self.NF_maxLevel_based_on_localizer)
        self.save_NFdatalog_to_csv()

        self.save_continousMeasurementDataToCSV()


    def getCurrentTimePoint(self):
        currentTimePoint, rt = self.tsi.get_current_time_point()
        #print("Current time point: " + str(currentTimePoint) + ", rt: " + str(rt))

        return currentTimePoint,rt

    def didNewDataArrive(self):
        self.previousRetrievedTimePoint = self.currentRetrievedTimePoint
        self.currentRetrievedTimePoint = self.getCurrentTimePoint()[0]

        if self.currentRetrievedTimePoint != self.previousRetrievedTimePoint:
            return True
        else:
            return False

    def getNewData(self,trialNr):
        if self.didNewDataArrive():
            timepoint,rt = self.getCurrentTimePoint()
            sampling_rate = self.tsi.get_sampling_rate()[0]

            # Get oxy
           # selectedChannels = self.tsi.get_selected_channels()[0]
           # oxy = self.tsi.get_data_oxy(selectedChannels[0], timepoint-1)[0]

            # Apply scale factor to oxy
          #  scalefactor = self.tsi.get_oxy_data_scale_factor()  # Turbo-Satori's default is 200 as a scale factor
          #  scaled_data = float(oxy) * float(scalefactor[0])  # Because for some reason you're getting two values for TSI's scacefactor

            betas = self.getBetas(trialNr)
            t_values = self.getTvalues(trialNr)

            self.recordedBetas.append(betas)
            self.timepointList.append(timepoint)
            self.reactionTimeList.append(rt)

            print("New data arrived! Timepoint: " + str(timepoint) + ", rt: " + str(rt), "beta  = " + str(betas) + " ,t-value: " + str(t_values) + ", sampling rate = " + str(sampling_rate) + ", trial = " + str(trialNr))

            return timepoint



    def set_NF_max_threshold(self,NFsignal_max):
        self.NF_maxLevel_based_on_localizer = NFsignal_max
        print("NF_maxLevel set to: " + str(self.NF_maxLevel_based_on_localizer))

    def getCurrentOxyInput(self):
        input = 0
        if self.TSIconnectionFound:
            currentTimePoint = self.tsi.get_current_time_point()[0]
            selectedChannels = self.tsi.get_selected_channels()[0]
#            oxy = self.tsi.get_data_oxy(selectedChannels[0], currentTimePoint - 1)[0] # -1 Because timepoint var starts at 1
           # input = oxy
            #print("Current time point: " + str(currentTimePoint), ", selected channels: " + str(Selected) + " , oxy: " + str(oxy))

        else:
            input = 0

        return input

    # The trial number gets the predictor for each trial (trial 1 for first predictor, trial 2 for second predictor etc)
    def getBetas(self,trialNr):
        if self.TSIconnectionFound:

            selectedChannels = self.tsi.get_selected_channels()[0]
           # print('Selected channel = ' + str(selectedChannels[0]))
            betas = self.tsi.get_beta_of_channel(selectedChannels[0],beta=trialNr-1, chromophore=1)[0] # -1 Because trial starts at 1 but indexing starts at 0 # doesn't need a timepoint because it just checks the latest betas
           # print("Betas (condition per trial): " + str(betas), " for trial: " + str(trialNr))

            # For debugging
           # betas_one = self.tsi.get_beta_of_channel(selectedChannels[0], beta=0, chromophore=1)[0]  #  Only get the beta's for all trials as one condition
           # print("Betas (one condition): " + str(betas_one), " for trial: " + str(trialNr))

            return betas

    def getTvalues(self,trialNr):
        if self.TSIconnectionFound:
            selectedChannels = self.tsi.get_selected_channels()[0]
            #print("Selected channel: "+  str(selectedChannels))
            contrast = [0,0,0,0,0,0,0,0,0,0]
            if trialNr > 0:
                contrast[trialNr-1] = 1 # Change the contrast depnding on which trial it is (because we use a separate condition for each trial)
            t_values = self.tsi.get_tvalue_of_channel(selectedChannels[0],chromophore=1,contrast=contrast) # 1 is oxy, 0 is deoxy

            #print("T-value: " + str(t_values))

            return t_values[0]

    def getBetasForAllChannels(self,channel,trialNr):

        if self.TSIconnectionFound:
                beta = self.tsi.get_beta_of_channel(channel,beta=trialNr-1, chromophore=1)[0]
               # print("Beta channel " + str(channel) + " = " + str(beta))

                return beta



    def scaleOxyData(self):
        if self.TSIconnectionFound:
            oxy = self.getCurrentOxyInput()
            scalefactor = self.tsi.get_oxy_data_scale_factor() # Turbo-Satori's default is 200 as a scale factor

            scaled_data = float(oxy) * float(scalefactor[0]) # Because for some reason you're getting two values for TSI's scacefactor

        #print("Scaled oxy: " + str(scaled_data) + ", scalefactor: " + str(scalefactor[0]))

        else:
            scaled_data = 0

        return scaled_data



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

    def save_continousMeasurementDataToCSV(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        print(current_date)
        print(self.recordedBetas)
        filename = f"RunRecording_betas_{current_date}.csv"
        data = list(zip(self.recordedBetas))
        print(data)
        self.save_list_to_csv(data, filename)
        print("Data saved to " + filename)


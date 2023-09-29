import pygame
import _turbosatorinetworkinterface as tsi  # handles getting data from TSI
import numpy as np

from pygame.locals import (
    K_UP,
    K_DOWN,

)

class BrainComputerInterface():
    def __init__(self):
        self.currentInput = 0
        self.previousInput = 0
        self.fakeInput = 0
        self.TSIconnectionFound = True
        self.timeBetweenSamples_ms = 100000
        self.collectTimewindowData= False
        self.timewindow_task = []
        self.timewindow_rest = []
        self.startTimeMeasurement = 0
        self.NFsignal = {"NFsignal_mean": [], "NFsignal_max": [], "NFSignal_median": [], "NFsignal_mean_REST": [], "NFsignal_max_REST": [], "NFSignal_median_REST": []}

        self.NF_maxLevel_based_on_localizer = 0.3  # This is the max level for the NF signal that people can reach

        self.NFsignal_mean = 1
        self.NFsignal_max = self.NF_maxLevel_based_on_localizer/2 # Starter values
        self.NFSignal_median =1

        self.currentTask_signal = 1
        self.currentRest_signal = 1


        # Look for a connection to turbo-satori
        try:
            self.tsi = tsi.TurbosatoriNetworkInterface("127.0.0.1", 55556)
        except:
            # None found? Let the user know
            self.TSIconnectionFound = False
            print("Turbo satori connection not found.")

        if self.TSIconnectionFound:
            self.timeBetweenSamples_ms = self.establishTimeInBetweenSamples()

        self.GET_TURBOSATORI_INPUT = pygame.USEREVENT + 7
        pygame.time.set_timer(self.GET_TURBOSATORI_INPUT, self.timeBetweenSamples_ms) # I have to give it integers...

    def startMeasuring(self, task):
        scaled_data = self.scaleOxyData()
        #print("     Scaled oxy: " + str(scaled_data))
        if self.collectTimewindowData:
            if task:
                self.timewindow_task.append(scaled_data)
            else:
                self.timewindow_rest.append(scaled_data)

        return scaled_data

    def resetTimewindowDataArray(self):
        self.timewindow_task = []
        self.timewindow_rest = []

    def calculateNFsignal(self,task):
        if task:
            NFsignal_raw = np.array(self.timewindow_task)
        else: # If measurement is from the rest period
            NFsignal_raw = np.array(self.timewindow_rest)

        self.NFsignal_mean = np.mean(NFsignal_raw)
        self.NFsignal_max = np.max(NFsignal_raw)
        self.NFSignal_median = np.median(NFsignal_raw)

        print("NFsignal_raw: " + str(NFsignal_raw))
        print("NFsignal_mean: " + str(self.NFsignal_mean) + ", NFsignal_max: " + str(self.NFsignal_max) + ", NFSignal_median: " + str(self.NFSignal_median))

        # Save the variables to a dictionary
        if task:
            self.currentTask_signal = self.NFsignal_mean # Save the current task signal for PSC calculation

            self.NFsignal["NFsignal_mean"].append(self.NFsignal_mean)
            self.NFsignal["NFsignal_max"].append(self.NFsignal_max)
            self.NFsignal["NFSignal_median"].append(self.NFSignal_median)



        else: # If measurement is from the rest period
            self.currentRest_signal = self.NFsignal_mean # Save the current rest signal for PSC calculation

            self.NFsignal["NFsignal_mean_REST"].append(self.NFsignal_mean)
            self.NFsignal["NFsignal_max_REST"].append(self.NFsignal_max)
            self.NFsignal["NFSignal_median_REST"].append(self.NFSignal_median)


        print("NFsignals stored: " + str(self.NFsignal))

    def get_percentage_signal_change(self):
        # PSC = (T-B_/B*100%
        T = self.currentTask_signal
        B = self.currentRest_signal
        #PSC = (T-B)/B*100
        PSC = T-B # Task signal - rest signal (just like the Turbo-satori software describes in the manual)
        print(      "Task = " + str(T) + ", Rest = " + str(B) + ", PSC = " + str(PSC))
        return PSC


    def get_achieved_NF_level(self):
        achieved_NF_signal = self.NFsignal_max / self.NF_maxLevel_based_on_localizer
        #print("achieved_NF_signal: " + str(achieved_NF_signal))

        # Add a ceiling to the achieved NF signal
        if achieved_NF_signal > 1:
            achieved_NF_signal = 1

        return achieved_NF_signal


    def calculate_NF_max_threshold(self):
    # Calculate the mean of the NFsignal_mean values in the NFsignal dictionary
        NFsignal_mean = np.mean((self.NFsignal["NFsignal_mean"]))
        NFsignal_max = np.mean((self.NFsignal["NFsignal_max"]))
        NFSignal_median = np.mean((self.NFsignal["NFSignal_median"]))

        # Print the mean of the NFsignal_mean values
        print("End of run. NFsignal_mean: " + str(NFsignal_mean) + ", NFsignal_max: " + str(NFsignal_max) + ", NFSignal_median: " + str(NFSignal_median))

        self.set_NF_max_threshold(NFsignal_max)

    def set_NF_max_threshold(self,NFsignal_max):
        self.NF_maxLevel_based_on_localizer = NFsignal_max
        print("NF_maxLevel set to: " + str(self.NF_maxLevel_based_on_localizer))

    def getCurrentInput(self):
        if self.TSIconnectionFound:
            currentTimePoint = self.tsi.get_current_time_point()[0]
            Selected = self.tsi.get_selected_channels()[0]
            oxy = self.tsi.get_data_oxy(Selected[0], currentTimePoint - 1)[0]
            input = oxy
            #print("Current time point: " + str(currentTimePoint), ", selected channels: " + str(Selected) + " , oxy: " + str(oxy))

        else:
            input = 0

        return input

    def scaleOxyData(self):
        if self.TSIconnectionFound:
            oxy = self.getCurrentInput()
            scalefactor = self.tsi.get_oxy_data_scale_factor()

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
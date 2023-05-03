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
        self.timewindow = []
        self.startTimeMeasurement = 0

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

    def startMeasuringTask(self):
        scaled_data = 2 #self.scaleOxyData()
        if self.collectTimewindowData:
            self.timewindow.append(scaled_data)
        else:
            self.timewindow = [] # Reset the timewindow

    def calculateNFsignal(self):
        NFsignal_raw = np.array(self.timewindow)
        NFsignal_mean = np.mean(NFsignal_raw)
        NFsignal_max = np.max(NFsignal_raw)
        NFSignal_median = np.median(NFsignal_raw)

        print("NFsignal_raw: " + str(NFsignal_raw))
        print("NFsignal_mean: " + str(NFsignal_mean) + ", NFsignal_max: " + str(NFsignal_max) + ", NFSignal_median: " + str(NFSignal_median))


    def getCurrentInput(self):

        if self.TSIconnectionFound:
            currentTimePoint = self.tsi.get_current_time_point()[0]
            Selected = self.tsi.get_selected_channels()[0]
            oxy = self.tsi.get_data_oxy(Selected[0], currentTimePoint - 1)[0]
            input = oxy
            print("Current time point: " + str(currentTimePoint), ", selected channels: " + str(Selected) + " , oxy: " + str(oxy))

        else:
            input = 0

        return input

    def scaleOxyData(self):
        if self.TSIconnectionFound:
            oxy = self.getCurrentInput()
            scalefactor = self.tsi.get_oxy_data_scale_factor()

            scaled_data = float(oxy) * float(scalefactor[0]) # Because for some reason you're getting two values for TSI's scacefactor

            print("Scaled oxy: " + str(scaled_data) + ", scalefactor: " + str(scalefactor[0]))
        else:
            scaled_data = 0

        return scaled_data

    def getKeyboardPressFromBrainInput(self):
        scaledOxyData = self.scaleOxyData()

        self.previousInput = self.currentInput
        self.currentInput = scaledOxyData

        print("Current input: " + str(self.currentInput) + ", previous input: " + str(self.previousInput))

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
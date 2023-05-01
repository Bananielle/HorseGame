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

        # Look for a connection to turbo-satori
        try:
            self.tsi = tsi.TurbosatoriNetworkInterface("127.0.0.1", 55556)
        except:
            # None found? Let the user know
            self.TSIconnectionFound = False
            print("Turbo satori connection not found.")

        if self.TSIconnectionFound:
            self.timeBetweenSamples_ms = self.establishTimeInBetweenSamples()

        self.GET_TURBOSATORI_INPUT = pygame.USEREVENT + 5
        pygame.time.set_timer(self.GET_TURBOSATORI_INPUT, self.timeBetweenSamples_ms) # I have to give it integers...

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

    def scaleOxyData(self):\

        oxy = self.getCurrentInput()
        scalefactor = self.tsi.get_oxy_data_scale_factor()

        scaled_data = oxy * scalefactor


        # window_size = 10
        # fnirs_window = np.zeros(window_size)
        # fnirs_window[:-1] = fnirs_window[1:] # [:-1] selects all the elements of the array except for the last one. [1:] is all elements except for the first one.
        # fnirs_window[-1] = oxy # Insert the new value at the end of the array
        #
        # scaled_data = (fnirs_window - np.min(fnirs_window)) / (np.max(fnirs_window) - np.min(fnirs_window)) # Perform min-max scaling on the windowed data
        #
        # # Sanity test: example array of fNIRS data and Min-max scaling
        # fnirs_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        # scaled_data = (fnirs_data - np.min(fnirs_data)) / (np.max(fnirs_data) - np.min(fnirs_data))
        # print("SCALING FACTOR SANITY TEST:")
        # print(scaled_data)

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
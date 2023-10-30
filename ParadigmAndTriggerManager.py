import pygame
from pylsl import StreamInfo, StreamOutlet
import pandas as pd
import numpy as np

class ParadigmAndTriggerManager():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParamaters):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.gp = gameParamaters
        self.dataInputFolder = "SimulatedData/"

        # For simulated protocl and data input
        self.protocol_array = [] # Array that contains the protocol (0=rest, 1=task) for each second
        self.simulatedData_array = [] # Array that contains a signal value (e.g., oxy or betas) for each second

        # Set up trigger stream (note that you need to exactly write "TriggerStream', otherwise Aurora and Turbo-Satori won't recognize it!
        self.info = StreamInfo(name='TriggerStream', type='Markers', channel_count=1, channel_format='int32',
                      source_id='Example')  # sets variables for object info
        self.outlet = StreamOutlet(self.info)  # initialize stream.

        self.retrieveProtocol("LocalizerAline_Protocol.csv")
        self.retrieveSimulatedData("LocalizerAline_BetaValues.csv")


    # Retrieves protocol data that is specified for each second.
    def retrieveProtocol(self, file_name):
        file_path = self.dataInputFolder + file_name
        df = pd.read_csv(file_path, header=None)
        conditions = df.iloc[:,0].values # Get the values of the first column
        print("Simulated protocol retrieved (specified for each second). 0=rest, 1=task.")
        print(conditions)

        self.protocol_array = conditions

    def getCurrentSimulatedCondition(self):
        print("Current simulated condition (0=rest, 1-10=task): " + self.protocol_array[self.gp.currentTime_s].__str__())
        try:
            condition = self.protocol_array[self.gp.currentTime_s]
        except:
            print("Ran out of data.") # If you run out of simulated data, just return 0.
            condition = 0

        return condition

    def getCurrentSimulatedSignalValue(self):
        #print("T= " + str(self.gp.currentTime_s) +  ": Current simulated signal value: " + self.simulatedData_array[self.gp.currentTime_s].__str__())
        try:
            data = self.simulatedData_array[self.gp.currentTime_s]
        except:
            print("Ran out of data.") # If you run out of data, just return 0.
            data = 0

        return  data

    def retrieveSimulatedData(self, file_name):
        file_path = self.dataInputFolder + file_name
        df = pd.read_csv(file_path, header=None,dtype=float)
        data = df.iloc[:,0].values
        print("Simulated data retrieved (specified for each second).")
        print(data)
        self.simulatedData_array = data


    def resetTaskStartTime(self):
        self.gp.startTime_TASK = self.gp.currentTime_s  + self.gp.duration_REST_s# Reset the start time for event TASK

    def resetRestStartTime(self):
        self.gp.startTime_REST = self.gp.currentTime_s + self.gp.duration_TASK_s  # Reset the start time for event TASK

    def resetJumpStartTime(self):
        self.gp.startTime_JUMP = self.gp.currentTime_s + self.gp.duration_TASK_s

    def resetTaskandRestTime(self):
        self.gp.startTime_TASK = self.gp.currentTime_s  # Reset the start time for event TASK
        self.gp.startTime_REST = self.gp.currentTime_s  # Set the start time for event REST


    def isItTimeForTaskEvent(self):
        if self.gp.task:
            return False

        if self.gp.TASK_counter >= self.gp.totalNum_TRIALS:
            return False

        if self.gp.currentTime_s >= self.gp.startTime_TASK:
            return True


    def isItTimeForRestEvent(self):
        if self.gp.rest:
            return False

        if self.gp.currentTime_s >= self.gp.startTime_REST:
            return True


    def initiateBasicTaskEvent(self):
        self.gp.task = True
        self.gp.rest = False
        self.startTaskTrigger()

        self.gp.TASK_counter += 1  # Increment the counter for event TASK
        self. gp.update_Taskcounter()
        print("T=",self.gp.currentTime_s,": Event TASK " + self.gp.TASK_counter.__str__() + " of " + self.gp.totalNum_TRIALS.__str__())



    def initiateBasicRestEvent(self):
        self. gp.task = False
        self. gp.rest = True
        self.startRestTrigger()

        self.resetRestStartTime()
        self.gp.REST_counter += 1  # Increment the counter for event B
        print("T=",self.gp.currentTime_s,": Event REST")



    # TRIGGERS
    def startTaskTrigger(self):
        self.outlet.push_sample(x=[3])  # Triggers are buggy in Turbo-satori but Aurora they work properly. (0 doesn't exist in TSI, and 1 = rest)
        print('Started task trigger.')

    def startRestTrigger(self):
        self.outlet.push_sample(x=[1])  # Rest trigger
        print('Started Rest trigger.')
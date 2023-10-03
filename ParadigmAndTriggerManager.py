import pygame
from pylsl import StreamInfo, StreamOutlet

class ParadigmAndTriggerManager():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParamaters):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.gp = gameParamaters

        # Set up trigger stream (note that you need to exactly write "TriggerStream', otherwise Aurora and Turbo-Satori won't recognize it!
        self.info = StreamInfo(name='TriggerStream', type='Markers', channel_count=1, channel_format='int32',
                      source_id='Example')  # sets variables for object info
        self.outlet = StreamOutlet(self.info)  # initialize stream.



    def resetTaskStartTime(self):
        self.gp.startTime_TASK = self.gp.currentTime_s  + self.gp.duration_REST_s# Reset the start time for event TASK

    def resetRestStartTime(self):
        self.gp.startTime_REST = self.gp.currentTime_s + self.gp.duration_TASK_s  # Reset the start time for event TASK

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
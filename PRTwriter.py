import datetime

class PRTwriter():
    def __init__(self, gameParamaters):
        self.gp = gameParamaters
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.prt_file_oneCond = None
        self.prt_file_multipleCond = None
        self.dataOutputFolder = "Data/PRTs/"
        self.run_type = ''
        self.extra = ''
        self.extra2 = ''
        if self.gp.gameType == 'maingame':
            self.run_type = "NF"
        if self.gp.gameType == 'localizer':
            self.run_type = 'localizer'
        if self.gp.boringMode:
            self.extra2 = ' basicmode_'
        if self.gp.performingSimulation:
            self.extra = 'simulated_'
        if self.gp.TESTING_MODE:
            self.extra = 'debugmode_'
       # self.file_name = self.gp.participantNr + '_' + self.gp.sessionNr + '_' + self.gp.runNr + '_' + self.gp.runType + '_' + self.gp.taskUsed + '_' + self.current_date + '.prt'
        self.file_name_multipleCond = 'PRT_' + self.run_type + '_' + self.extra + self.extra2 + 'MultipleCond_' + self.current_date + '.prt'
        self.file_name_oneCond =  'PRT_' + self.run_type + '_' + self.extra + self.extra2 + 'OneCond_' + self.current_date + '.prt'
        self.file_path_multipleCond = ('')
        self.file_path_oneCond = ('')

    def create_PRT_template_multipleCond(self):

        print("Writing PRT multipleCond file: " + self.file_name_multipleCond)

        self.file_path_multipleCond = self.dataOutputFolder + self.file_name_multipleCond

        self.prt_file_multipleCond = open(self.file_path_multipleCond, 'w')  # Open the file in write mode
        self.prt_file_multipleCond.write('FileVersion: 2\n')
        self.prt_file_multipleCond.write('\n')
        self.prt_file_multipleCond.write('ResolutionOfTime: Volumes\n')
        self.prt_file_multipleCond.write('\n')
        self.prt_file_multipleCond.write('Experiment: BCI_4_kids\n')
        self.prt_file_multipleCond.write('\n')
        self.prt_file_multipleCond.write('BackgroundColor: 0 0 0\n')
        self.prt_file_multipleCond.write('TextColor: 255 255 255\n')
        self.prt_file_multipleCond.write('TimeCourseColor: 255 255 30\n')
        self.prt_file_multipleCond.write('TimeCourseThick: 2\n')
        self.prt_file_multipleCond.write('ReferenceFuncColor: 30 200 30\n')
        self.prt_file_multipleCond.write('ReferenceFuncThick: 2\n')
        self.prt_file_multipleCond.write('\n')


        self.prt_file_multipleCond.write('NrOfConditions: ' + str(self.gp.totalNum_TRIALS) + '\n')  # One condition for all trials


        # Timings will be added during the experiment

        self.prt_file_multipleCond.close()

        # For testing purposes, read the file
        self.read_PRT_template_multipleCond()

    def create_PRT_template_oneCond(self) :

        print("Writing PRT file: " + self.file_name_oneCond)

        self.file_path_oneCond = self.dataOutputFolder + self.file_name_oneCond

        self.prt_file_oneCond = open(self.file_path_oneCond, 'w') # Open the file in write mode
        self.prt_file_oneCond.write('FileVersion: 2\n')
        self.prt_file_oneCond.write('\n')
        self.prt_file_oneCond.write('ResolutionOfTime: Volumes\n')
        self.prt_file_oneCond.write('\n')
        self.prt_file_oneCond.write('Experiment: BCI_4_kids\n')
        self.prt_file_oneCond.write('\n')
        self.prt_file_oneCond.write('BackgroundColor: 0 0 0\n')
        self.prt_file_oneCond.write('TextColor: 255 255 255\n')
        self.prt_file_oneCond.write('TimeCourseColor: 255 255 30\n')
        self.prt_file_oneCond.write('TimeCourseThick: 2\n')
        self.prt_file_oneCond.write('ReferenceFuncColor: 30 200 30\n')
        self.prt_file_oneCond.write('ReferenceFuncThick: 2\n')
        self.prt_file_oneCond.write('\n')

        self.prt_file_oneCond.write('NrOfConditions: 1\n') # One condition for all trials

        self.prt_file_oneCond.write('\n')
        self.prt_file_oneCond.write('Condition1\n')
        self.prt_file_oneCond.write(str(self.gp.totalNum_TRIALS) + '\n') # Number of trials


        # Timings will be added during the experiment

        # For testing purposes, read the file
        self.read_PRT_template_oneCond()
        print(self.prt_file_oneCond.read())

        self.prt_file_oneCond.close()


    def read_PRT_template_oneCond(self):
        self.prt_file_oneCond = open(self.file_path_oneCond, 'r')
        print(self.prt_file_oneCond.read())


    def read_PRT_template_multipleCond(self):
        self.prt_file_multipleCond = open(self.file_path_multipleCond, 'r')
        print(self.prt_file_multipleCond.read())


    def addTaskStartEvent_oneCond(self, current_time_point):
        self.prt_file_oneCond = open(self.file_path_oneCond, 'a')
        self.prt_file_oneCond.write('   ' + str(current_time_point))

        self.prt_file_oneCond.close()

    def addTaskEndEvent_oneCond(self, current_time_point):
        self.prt_file_oneCond = open(self.file_path_oneCond, 'a')
        self.prt_file_oneCond.write('   ' + str(current_time_point) + '\n')

        self.prt_file_oneCond.close()

    def addTaskStartEvent_multipleCond(self, current_time_point):
        self.prt_file_multipleCond = open(self.file_path_multipleCond, 'a')

        self.prt_file_multipleCond.write('\nNFtrial' + str(self.gp.trial_counter) + '\n')
        self.prt_file_multipleCond.write('1\n')
        self.prt_file_multipleCond.write('   ' + str(current_time_point))

        self.prt_file_multipleCond.close()

    def addTaskEndEvent_multipleCond(self, current_time_point):
        self.prt_file_multipleCond = open(self.file_path_multipleCond, 'a')

        self.prt_file_multipleCond.write('   ' + str(current_time_point) + '\n')
        self.prt_file_multipleCond.write('Color: 255 0 0\n')

        self.prt_file_multipleCond.close()


    def finish_PRT_file_oneCond(self):
        self.prt_file_oneCond = open(self.file_path_oneCond, 'a')
        self.prt_file_oneCond.write('\nColor: 255 0 0')

        self.prt_file_oneCond.close()


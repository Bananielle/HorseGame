import datetime

class PRTwriter():
    def __init__(self, gameParamaters):
        self.gp = gameParamaters
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.prt_file = None
        self.dataOutputFolder = "Data/PRTs/"
        self.run_type = ''
        self.extra = ''
        self.extra2 = ''
        if self.gp.gameType == 'maingame':
            self.run_type = "NF"
        if self.gp.gameType == 'localizer':
            self.run_type = 'localizer'
        if self.gp.boringMode:
            self.extra2 = ' basicmode'
        if self.gp.performingSimulation:
            self.extra = 'simulated'
        if self.gp.TESTING_MODE:
            self.extra = 'debugmode'
       # self.file_name = self.gp.participantNr + '_' + self.gp.sessionNr + '_' + self.gp.runNr + '_' + self.gp.runType + '_' + self.gp.taskUsed + '_' + self.current_date + '.prt'
        self.file_name = 'PRT_' + self.run_type + '_' + self.extra + self.extra2 + '_'+  self.current_date + '.prt'
        self.file_path = ('')



    def create_PRT_template(self) :

        print("Writing PRT file: " + self.file_name)

        self.file_path = self.dataOutputFolder + self.file_name

        self.prt_file = open(self.file_path, 'w') # Open the file in write mode
        self.prt_file.write('FileVersion: 2\n')
        self.prt_file.write('\n')
        self.prt_file.write('ResolutionOfTime: Volumes\n')
        self.prt_file.write('\n')
        self.prt_file.write('Experiment: BCI_4_kids\n')
        self.prt_file.write('\n')
        self.prt_file.write('BackgroundColor: 0 0 0\n')
        self.prt_file.write('TextColor: 255 255 255\n')
        self.prt_file.write('TimeCourseColor: 255 255 30\n')
        self.prt_file.write('TimeCourseThick: 2\n')
        self.prt_file.write('ReferenceFuncColor: 30 200 30\n')
        self.prt_file.write('ReferenceFuncThick: 2\n')
        self.prt_file.write('\n')

        if self.gp.gameType == 'maingame':
            self.prt_file.write('NrOfConditions: ' + str(self.gp.totalNum_TRIALS) + '\n')  # One condition for all trials

        if self.gp.gameType == 'localizer':
            self.prt_file.write('NrOfConditions: 1\n') # One condition for all trials

            self.prt_file.write('\n')
            self.prt_file.write('Condition1\n')
            self.prt_file.write(str(self.gp.totalNum_TRIALS) + '\n') # Number of trials


        # Timings will be added during the experiment

        self.prt_file.close()

        # For testing purposes, read the file
        self.read_PRT_template()

    def read_PRT_template(self):
        self.prt_file = open(self.file_path, 'r')
        print(self.prt_file.read())

    def addTaskStartEvent(self, current_time_point):

        self.prt_file = open(self.file_path, 'a')

        if self.gp.gameType == 'maingame':
            self.prt_file.write('\nNFtrial' + str(self.gp.trial_counter) + '\n')
            self.prt_file.write('1\n')
            self.prt_file.write('   ' + str(current_time_point))
        if self.gp.gameType == 'localizer':
            self.prt_file.write('   ' + str(current_time_point))


        self.prt_file.close()

    def addTaskEndEvent(self, current_time_point):
        self.prt_file = open(self.file_path, 'a')

        if self.gp.gameType == 'maingame':
            self.prt_file.write('   ' + str(current_time_point) + '\n')
            self.prt_file.write('Color: 255 0 0\n')
        if self.gp.gameType == 'localizer':
            self.prt_file.write('   ' + str(current_time_point) + '\n')

        self.prt_file.close()

    def finish_PRT_file(self):
        self.prt_file = open(self.file_path, 'a')

        if self.gp.gameType == 'localizer':
            self.prt_file.write('\nColor: 255 0 0')

        self.prt_file.close()

    def rename_PRT_file(self):
        print('Renaming PRT file to ' + self.prt_file)

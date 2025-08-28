import pygame

# Colour constants
GOLD = (255, 184, 28)
PINK = (170, 22, 166)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)

ARIAL_FONT_PATH = "Resources/fonts/Arial.ttf"
ARIAL_BOLD_FONT_PATH = "Resources/fonts/Arial Bold.ttf"
HERC_FONT_PATH = "Resources/fonts/Herculanum.ttf"

class Scoreboard():
    def __init__(self, gameParameters):
        self.taskList = []
        self.scoresList = []
        self.runList = []
        self.task_coins_dictionary = {}
        self.runNr = 1
        self.font =  pygame.font.Font(HERC_FONT_PATH, 35)
        self.coinsPerTrialPerRuns = []
        self.gp = gameParameters
        self.sortedScores = []
        self.sortedTasks = []

    def addScoretoScoreBoard(self, score):
        if not self.gp.scoreSaved:
            self.scoresList.append(score)
            self.taskList.append(self.gp.taskUsed)
            self.runList = self.runNr
            self.runNr = + 1
            self.gp.scoreSaved = True  # This will reset when the player goes back to the start screen
            print('Score ', score, ' saved to score list. Is now: ', str(self.scoresList))
            print('Coins per trial: ' + str(self.gp.nrCoinsPerTrial))
            self.coinsPerTrialPerRuns.append(self.gp.nrCoinsPerTrial)
            print('Coins per trial per run: ' + str(self.coinsPerTrialPerRuns))

            self.task_coins_dictionary[self.gp.taskUsed] = score  #Dictionary of task used and it's associated run score

    def makePinkFont(self, string):
        text = self.font.render(string, True, PINK)  # Pink colour
        return text

    def makeGoldFont(self, string):
        text = self.font.render(string, True, GOLD)  # Pink colour
        return text

    def sortScores(self):
        self.sortedScores = sorted(self.scoresList, reverse=True)
        sortedDictionary = dict(sorted(self.task_coins_dictionary.items()))
        self.sortedTasks = list(sortedDictionary)

        return self.sortedScores, self.sortedTasks

    def prepareScoreBoardText(self):
        currentScoreAlreadyDisplayed = False
        newPosition = 30
        count = 1
        scoresText_list = []
        taskText_list = []
        bonusText_list = []

        for score in self.sortedScores:
            bonus_text = pygame.Surface((0, 0))

            # Adjust the coin vallue based on the difficulty level:
            bonus = 0
            if self.gp.gameDifficulty == 2:
                bonus = int((score * 1.2) - score)
            if self.gp.gameDifficulty == 3:
                bonus = int((score * 1.2 * 1.2) - score)

            i = 0

            count_str = '(Run ' + str(count) + '. ' + self.sortedTasks[i] + ')'  # Get the task name from the dictionary
            # print('count_str: ', count_str)

            final_score_text = str(score) + ' coins. '

            if score == self.gp.nrCoinsCollectedThroughoutRun and not currentScoreAlreadyDisplayed:  # Colour the currently achieved score GOLD
                scores_text = self.font.render(final_score_text, True, BLACK)
                task_text = self.font.render(count_str, True, BLACK)
                currentScoreAlreadyDisplayed = True
            else:
                scores_text = self.makePinkFont(final_score_text)
                task_text = self.makePinkFont(count_str)

            scoresText_list.append(scores_text)
            taskText_list.append(task_text)

            i = i + 1  # For iteration through the tasks

            # Put score on screen
            if self.gp.gameDifficulty == 2 or self.gp.gameDifficulty == 3:
                if self.gp.gameDifficulty == 2:
                    bonus_text = self.makeGoldFont('Silver bonus: ' + str(bonus) + ' coin(s)')
                if self.gp.gameDifficulty == 3:
                    self.bonus_text = self.makeGoldFont('Gold bonus: ' + str(bonus) + ' coin(s)')

                bonusText_list.append(bonus_text)

            count += 1

        return scoresText_list, taskText_list, bonusText_list


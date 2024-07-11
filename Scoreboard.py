import pygame

# Colour constants
GOLD = (255, 184, 28)
PINK = (170, 22, 166)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)


class Scoreboard():
    def __init__(self, gameParameters):
        self.taskList = []
        self.scoresList = []
        self.runList = []
        self.task_coins_dictionary = {}
        self.runNr = 1
        self.font = pygame.font.SysFont('herculanum', 35, bold=True, )
        self.coinsPerTrialPerRuns = []
        self.gp = gameParameters

    def addScoretoScoreBoard(self, score):
        if not self.gp.scoreSaved:
            self.scoresList.append(score)
            self.taskList.append(gp.taskUsed)
            self.runList = self.runNr
            self.runNr = + 1
            self.gp.scoreSaved = True  # This will reset when the player goes back to the start screen
            print('Score ', score, ' saved to score list. Is now: ', str(self.scoresList))
            self.save_scoresPerRun_to_csv()
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

    def displayScoreboard(self):

        scoreboard = self.makePinkFont('Scoreboard')
        screen.blit(scoreboard,
                    ((SCREEN_WIDTH / 2) - (SCREEN_WIDTH * 0.11), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.40)))

        currentScoreAlreadyDisplayed = False
        newPosition = 30
        count = 1
        sortedScores = sorted(self.scoresList, reverse=True)
        sortedDictionary = dict(sorted(self.task_coins_dictionary.items()))
        #print('sortedDictionary: ', sortedDictionary)
        #print('sortedScores: ', sortedScores)

        # Put each score on the screen in descending order
        for score in sortedScores:

            # Adjust the coin vallue based on the difficulty level:
            bonus = 0
            if self.gp.gameDifficulty == 2:
                bonus = int((score * 1.2) - score)
            if self.gp.gameDifficulty == 3:
                bonus = int((score * 1.2 * 1.2) - score)

            i = 0
            sortedTasks = list(sortedDictionary)
            count_str = '(Run ' + str(count) + '. ' + sortedTasks[i] + ')'  # Get the task name from the dictionary
            #print('count_str: ', count_str)

            final_score_text = str(score) + ' coins. '

            if score == gp.nrCoinsCollectedThroughoutRun and not currentScoreAlreadyDisplayed:  # Colour the currently achieved score GOLD
                scores_text = self.font.render(final_score_text, True, BLACK)
                task_text = self.font.render(count_str, True, BLACK)
                currentScoreAlreadyDisplayed = True
            else:
                scores_text = self.makePinkFont(final_score_text)
                task_text = self.makePinkFont(count_str)

            i = i + 1  # For iteration through the tasks

            # Put score on screen
            if self.gp.gameDifficulty == 2 or gp.gameDifficulty == 3:
                if self.gp.gameDifficulty == 2:
                    bonus_text = self.makeGoldFont('Silver bonus: ' + str(bonus) + ' coin(s)')
                if self.gp.gameDifficulty == 3:
                    self.bonus_text = self.makeGoldFont('Gold bonus: ' + str(bonus) + ' coin(s)')
                screen.blit(bonus_text,
                            ((SCREEN_WIDTH / 3.8), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
                newPosition += 35
            screen.blit(scores_text,
                        ((SCREEN_WIDTH / 3.8), (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
            screen.blit(task_text,
                        ((SCREEN_WIDTH / 2.2) - 80, (SCREEN_HEIGHT / 2) - (SCREEN_HEIGHT * 0.35) + newPosition))
            newPosition += 35
            count += 1

            # print('score ', score, ' printed')

    # CSV writer
    def save_scoresPerRun_to_csv(self):

        ScoresDictionary = {"Coins collected": self.scoresList, "Task": gp.taskUsed}
        fieldnames = ["Coins collected"]

        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"Scoreboard_{current_date}.csv"

        csvWriter = CSVwriter()
        csvWriter.save_dict_to_csv(filename, fieldnames, ScoresDictionary)

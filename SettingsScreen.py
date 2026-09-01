import pygame
import json

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
)

# Colours
GOLD = (255, 184, 28)
PINK = (170, 22, 166)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

ARIAL_FONT_PATH = "Resources/fonts/Arial.ttf"
ARIAL_BOLD_FONT_PATH = "Resources/fonts/Arial Bold.ttf"

class SettingNames:
    FULLSCREEN = "Fullscreen:"
    NUM_TRIALS = "Number of trials:"
    TASK_DURATION = "Task duration (seconds):"
    REST_DURATION = "Rest duration (seconds):"
    BASELINE_DURATION = "Initial baseline duration (seconds):"
    JITTER = "Jitter duration (seconds):"
    NF_THRESHOLD_TVALUE = "Neurofeedback threshold (t-value):"
    NF_THRESHOLD_BETA = "Neurofeedback threshold (beta):"
    NF_THRESHOLD_OXYDEOXY =  "Neurofeedback threshold (mean oxy/deoxy):"
    DATA_INPUT_TYPE = "Data input type (0 = beta's, 1 = t-values, 2 = mean oxy/deoxy):"
    CHROMOPHORE = "Use chromophore (1 = HbO, 0 = Hb):"
    SIMULATION_MODE = "Simulation mode:"
    DEBUGGING = "Debugging:"
    DATAWINDOW_DURATION_AFTER_TASK_END = "Datawindow (s) end (from stimulus onset):" # after task ends
    DATAWINDOW_DURATION_BEFORE_TASK_END = "Datawindow (s) start (from stimulus onset):" # before task ends
    FRAMERATE = "Frame rate (Hz):"
    BORING_MODE = "Basic mode:"
    DIFFERENTIAL_FEEDBACK = "Differential feedback (0=off, 1=a-b, 2=b-a):"
    MINIMAL_NR_OF_COINS = "Minimal coins per trial (0-3):"
    PORT = "Tsi port (restart game if changed):"
    SHOW_COIN_COUNT = "Show mean % of coins (0) or sum of coins (1) in scoreboard:"
    PRACTICE_FIRST_TRIAL = "First trial = practice (no NF, unscored) (0=off, 1=on):"

class Settings_header(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Settings_header, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.surf = pygame.image.load("Resources/SETTINGS_header.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()

        self.surf_center = (
            (self.SCREEN_WIDTH - self.surf.get_width()) / 2,
            ((self.SCREEN_HEIGHT * 0.15) - self.surf.get_height()))


class MenuItem:  # For creating different parameters
    def __init__(self, text, value):
        self.text = text
        self.var = ''
        self.location = 0
        self.font = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 15)
        self.surface = self.font.render(self.text, True, WHITE)
        self.value = value

    def value_text(self):
        """You can override this in subclasses; return a string or None if no value."""
        return None

#test

    def change_settings_file(self, parameter, value):
        with open("GameSettings.json") as f:
            settings = json.load(f)  # Open settings file (json)
            # update and save back
            if parameter == SettingNames.NF_THRESHOLD_BETA:
                value = round(value,2) #Make sure it's a float rounded down to 1 decimal after the comma


            settings[parameter] = value  # Change the paramater

        with open("GameSettings.json", "w") as f:  # Save changes
            json.dump(settings, f, indent=2)

        print("Parameter " + parameter + " changed to: " + str(settings[parameter]))


class ToggleItem(MenuItem):
    def __init__(self, text, value):
        super().__init__(text, bool(value))
        self.value = bool(value)

    def toggle(self):
        self.value = not self.value
        print(self.value)

        if self.text == SettingNames.SIMULATION_MODE:
            self.change_settings_file("simulation_mode", self.value)
        if self.text == SettingNames.DEBUGGING:
            self.change_settings_file("debugging", self.value)
        if self.text == SettingNames.BORING_MODE:
            self.change_settings_file("boring_mode", self.value)

    def value_text(self):
        return "ON" if self.value else "OFF"


class NumericalItem_int(MenuItem):
    def __init__(self, text, value=0, minimum=None, maximum=None, step=1):
        super().__init__(text, int(value))
        self.value = int(value)
        self.min = minimum
        self.max = maximum
        self.step = step

    def updateSettings(self):
        if self.text == SettingNames.NUM_TRIALS:
            self.change_settings_file("num_trials", self.value)
        if self.text == SettingNames.TASK_DURATION:
            self.change_settings_file("task_duration_s", self.value)
        if self.text == SettingNames.REST_DURATION:
            self.change_settings_file("rest_duration_s", self.value)
        if self.text == SettingNames.BASELINE_DURATION:
            self.change_settings_file("baseline_duration_s", self.value)
        if self.text == SettingNames.JITTER:
            self.change_settings_file("jitter_s", self.value)
        if self.text == SettingNames.DATA_INPUT_TYPE:
            self.change_settings_file("data_input_type", self.value)
        if self.text == SettingNames.CHROMOPHORE:
            self.change_settings_file("chromophore", self.value)
        if self.text == SettingNames.NF_THRESHOLD_TVALUE:
            self.change_settings_file("neurofeedback_threshold_t_value", self.value)
        if self.text == SettingNames.NF_THRESHOLD_BETA:
            self.change_settings_file("neurofeedback_threshold_beta", self.value)
        if self.text == SettingNames.NF_THRESHOLD_OXYDEOXY:
            self.change_settings_file("neurofeedback_threshold_oxydeoxy", self.value)
        if self.text == SettingNames.DATAWINDOW_DURATION_AFTER_TASK_END:
            self.change_settings_file("datawindow_duration_after_task_end_s", self.value)
        if self.text == SettingNames.DATAWINDOW_DURATION_BEFORE_TASK_END:
            self.change_settings_file("datawindow_duration_before_task_end_s", self.value)
        if self.text == SettingNames.FRAMERATE:
            self.change_settings_file("framerate", self.value)
        if self.text == SettingNames.DIFFERENTIAL_FEEDBACK:
            self.change_settings_file("differential_feedback", self.value)
        if self.text == SettingNames.MINIMAL_NR_OF_COINS:
            self.change_settings_file("minimal_nr_of_coins", self.value)
        if self.text == SettingNames.PORT:
            self.change_settings_file("port", self.value)
        if self.text == SettingNames.SHOW_COIN_COUNT:
            self.change_settings_file("show_coin_count", self.value)
        if self.text == SettingNames.PRACTICE_FIRST_TRIAL:
            self.change_settings_file("practice_first_trial", self.value)


    def increase(self):
        if self.value < self.max:
            self.value += self.step
            print(self.value)

            self.updateSettings()

    def decrease(self):
        if self.value > self.min:
            self.value -= self.step
            print(self.value)

            self.updateSettings()

    def value_text(self):  # Return the numerical value as a string.
        # if step is fractional, show one decimal; otherwise integer
        if isinstance(self.step, float) and not self.step.is_integer():
            print("Neurofeedback threshold (beta): " + str(self.value))
            return f"{self.value:1f}"



        return str(int(self.value)) # Otherwise just return as an integer

class NumericalItem_float(MenuItem):
    def __init__(self, text, value=0.0, minimum=None, maximum=None, step=1):
        super().__init__(text, float(value))
        self.value = float(value)
        self.min = minimum
        self.max = maximum
        self.step = step

    def increase(self):
        if self.value < self.max:
            self.value += self.step
            self.value = round(self.value, 2)
            print(self.value)

        # Floats
        if self.text == SettingNames.NF_THRESHOLD_BETA:
            self.change_settings_file("neurofeedback_threshold_beta", self.value)

        if self.text == SettingNames.NF_THRESHOLD_OXYDEOXY:
            self.change_settings_file("neurofeedback_threshold_beta", self.value)


    def decrease(self):
        if self.value > self.min:
            self.value -= self.step
            self.value = round(self.value,2)
            print(self.value)

        # Floats
        if self.text == SettingNames.NF_THRESHOLD_BETA:
            self.change_settings_file("neurofeedback_threshold_beta", self.value)

        if self.text == SettingNames.NF_THRESHOLD_OXYDEOXY:
            self.change_settings_file("neurofeedback_threshold_beta", self.value)

    def value_text(self):  # Return the numerical value as a string.
        # if step is fractional, show one decimal;
        return str(round(self.value,2)) #



class settingsMain():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams):
        super(settingsMain, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.settingsFont = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 18)
        self.text_item = "Select: UP/DOWN:        Change: LEFT/RIGHT:        Back: ESC"
        self.instructions = self.settingsFont.render(self.text_item, True, PINK)
        self.location = (SCREEN_WIDTH / 3.6, SCREEN_HEIGHT / 4)
        self.gameParams = gameParams
        self.selected_index = 0  # For which item is selected.
        self.items = []

        # Read gamesettings.json to get parameters
        with open("GameSettings.json") as f:
            settings = json.load(f)
            number_of_trials = settings["num_trials"]
            task_duration_s = settings["task_duration_s"]
            rest_duration_s = settings["rest_duration_s"]
            baseline_duration_s = settings["baseline_duration_s"]
            jitter_s = settings ["jitter_s"]
            data_input_type = settings["data_input_type"]
            neurofeedback_threshold_t_value = settings["neurofeedback_threshold_t_value"]
            neurofeedback_threshold_beta = settings["neurofeedback_threshold_beta"]
            neurofeedback_threshold_oxydeoxy = settings["neurofeedback_threshold_oxydeoxy"]
            simulation_mode = settings["simulation_mode"]
            chromophore = settings["chromophore"]
            debugging = settings["debugging"]
            datawindow_duration_after_task_end_s = settings["datawindow_duration_after_task_end_s"]
            datawindow_duration_before_task_end_s = settings["datawindow_duration_before_task_end_s"]
            framerate = settings["framerate"]
            boring_mode = settings["boring_mode"]
            differential_feedback = settings["differential_feedback"]
            minimal_nr_of_coins = settings["minimal_nr_of_coins"]
            port = settings["port"]
            show_coin_count = settings["show_coin_count"]
            practice_first_trial = settings["practice_first_trial"]



        # Add new menu items here.
        self.add_item(NumericalItem_int(SettingNames.NUM_TRIALS, number_of_trials, 1, 100, 1))
        self.add_item(NumericalItem_int(SettingNames.TASK_DURATION, task_duration_s, 1, 3600, 1))
        self.add_item(NumericalItem_int(SettingNames.REST_DURATION, rest_duration_s, 1, 3600, 1))
        self.add_item(NumericalItem_int(SettingNames.BASELINE_DURATION, baseline_duration_s, 1, 3600, 1))
        self.add_item(NumericalItem_int(SettingNames.JITTER, jitter_s, 0, 360, 1))
        self.add_item(NumericalItem_int(SettingNames.DATA_INPUT_TYPE, data_input_type, 0, 2, 1))
        self.add_item(NumericalItem_int(SettingNames.CHROMOPHORE, chromophore,0,1,1))
        self.add_item(NumericalItem_int(SettingNames.NF_THRESHOLD_TVALUE, neurofeedback_threshold_t_value, 0, 100, 1))
        self.add_item(NumericalItem_float(SettingNames.NF_THRESHOLD_BETA, neurofeedback_threshold_beta, 0, 100, 0.1))
        self.add_item(NumericalItem_float(SettingNames.NF_THRESHOLD_OXYDEOXY, neurofeedback_threshold_oxydeoxy, 0, 100, 0.1))
        self.add_item(NumericalItem_int(SettingNames.DATAWINDOW_DURATION_BEFORE_TASK_END, datawindow_duration_before_task_end_s, 0, 100, 1))
        self.add_item(NumericalItem_int(SettingNames.DATAWINDOW_DURATION_AFTER_TASK_END, datawindow_duration_after_task_end_s, 1, 100, 1))
        self.add_item(ToggleItem(SettingNames.DEBUGGING, debugging))
        self.add_item(ToggleItem(SettingNames.SIMULATION_MODE, simulation_mode))
        self.add_item(NumericalItem_int(SettingNames.FRAMERATE, framerate, 10, 80, 1))
        self.add_item(ToggleItem(SettingNames.BORING_MODE, boring_mode))
        self.add_item(NumericalItem_int(SettingNames.DIFFERENTIAL_FEEDBACK, differential_feedback,0,2,1))
        self.add_item(NumericalItem_int(SettingNames.MINIMAL_NR_OF_COINS, minimal_nr_of_coins, 0, 3, 1))
        self.add_item(NumericalItem_int(SettingNames.PORT, port, 55550, 55560, 1))
        self.add_item(NumericalItem_int(SettingNames.SHOW_COIN_COUNT,show_coin_count,0,1,1))
        self.add_item(NumericalItem_int(SettingNames.PRACTICE_FIRST_TRIAL,int(practice_first_trial),0,1,1))

    def add_item(self, item: MenuItem):
        self.location = self.location
        base_x = self.SCREEN_WIDTH / 4.5
        base_y = self.SCREEN_HEIGHT / 3
        offset_y = len(self.items) * 24  # space between items
        item.location = (base_x, base_y + offset_y)
        self.items.append(item)
        return item


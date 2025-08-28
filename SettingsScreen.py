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
            ((self.SCREEN_HEIGHT * 0.15) - self.surf.get_height())
        )


class MenuItem:  # For creating different parameters
    def __init__(self, text, value):
        self.text = text
        self.location = 0
        self.font = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 18)
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
            if parameter == "neurofeedback_threshold":
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

        if self.text == "Debugging:":
            self.change_settings_file("debugging", self.value)

    def value_text(self):
        return "ON" if self.value else "OFF"


class NumericalItem_int(MenuItem):
    def __init__(self, text, value=0, minimum=None, maximum=None, step=1):
        super().__init__(text, int(value))
        self.value = int(value)
        self.min = minimum
        self.max = maximum
        self.step = step

    def increase(self):
        if self.value < self.max:
            self.value += self.step
            print(self.value)

        if self.text == "Number of trials:":
            self.change_settings_file("num_trials", self.value)
        if self.text == "Task duration (seconds):":
            self.change_settings_file("task_duration_s", self.value)
        if self.text == "Rest duration (seconds):":
            self.change_settings_file("rest_duration_s", self.value)
        if self.text == "Baseline duration (seconds):":
            self.change_settings_file("baseline_duration_s", self.value)
        if self.text == "Jitter duration (seconds):":
            self.change_settings_file("jitter_s", self.value)
        if self.text == "Data input type (0 = beta's, 1 = t-values):":
            self.change_settings_file("data_input_type", self.value)
        if self.text == "Neurofeedback threshold:":
            self.change_settings_file("neurofeedback_threshold", self.value)
        if self.text == "Duration datawindow after task ends (seconds):":
            self.change_settings_file("datawindow_duration_after_task_end_s", self.value)
        if self.text == "Duration datawindow before task ends (seconds):":
            self.change_settings_file("datawindow_duration_before_task_end_s", self.value)

    def decrease(self):
        if self.value > self.min:
            self.value -= self.step
            print(self.value)

        if self.text == "Number of trials: ":
            self.change_settings_file("num_trials", self.value)
        if self.text == "Task duration (seconds):":
            self.change_settings_file("task_duration_s", self.value)
        if self.text == "Rest duration (seconds):":
            self.change_settings_file("rest_duration_s", self.value)
        if self.text == "Baseline duration (seconds):":
            self.change_settings_file("baseline_duration_s", self.value)
        if self.text == "Jitter duration (seconds):":
            self.change_settings_file("jitter_s", self.value)
        if self.text == "Data input type (0 = beta's, 1 = t-values):":
            self.change_settings_file("data_input_type", self.value)
        if self.text == "Neurofeedback threshold:":
            self.change_settings_file("neurofeedback_threshold", self.value)
        if self.text == "Duration datawindow after task ends (seconds):":
            self.change_settings_file("datawindow_duration_after_task_end_s", self.value)
        if self.text == "Duration datawindow before task ends (seconds):":
            self.change_settings_file("datawindow_duration_before_task_end_s", self.value)

    def value_text(self):  # Return the numerical value as a string.
        # if step is fractional, show one decimal; otherwise integer
        if isinstance(self.step, float) and not self.step.is_integer():
            print("Neurofeedback threshold 2: " + str(self.value))
            return f"{self.value:1f}"
        return str(int(self.value)) # Otherwise just return as an integer

class NumericalItem_float(MenuItem):
    def __init__(self, text, value=0, minimum=None, maximum=None, step=1):
        super().__init__(text, float(value))
        self.value = float(value)
        self.min = minimum
        self.max = maximum
        self.step = step

    def increase(self):
        if self.value < self.max:
            self.value += self.step
            print(self.value)

        if self.text == "Neurofeedback threshold:":
            self.change_settings_file("neurofeedback_threshold", self.value)


    def decrease(self):
        if self.value > self.min:
            self.value -= self.step
            print(self.value)

        if self.text == "Neurofeedback threshold:":
            self.change_settings_file("neurofeedback_threshold", self.value)

    def value_text(self):  # Return the numerical value as a string.
        # if step is fractional, show one decimal;
        return str(round(self.value,2)) #



class settingsMain():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams):
        super(settingsMain, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.font =  pygame.font.Font(ARIAL_BOLD_FONT_PATH, 30)
        self.settingsFont = pygame.font.Font(ARIAL_BOLD_FONT_PATH, 18)
        self.text_item = "Select: UP/DOWN:        Change: LEFT/RIGHT:        Back: ESC"
        self.instructions = self.settingsFont.render(self.text_item, True, PINK)
        self.location = (SCREEN_WIDTH / 3.2, SCREEN_HEIGHT / 4)
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
            neurofeedback_threshold = settings["neurofeedback_threshold"]
            debugging = settings["debugging"]
            datawindow_duration_after_task_end_s = settings["datawindow_duration_after_task_end_s"]
            datawindow_duration_before_task_end_s = settings["datawindow_duration_before_task_end_s"]



        # Add new menu items here.
        self.add_item(NumericalItem_int("Number of trials: ", number_of_trials, 1, 100, 1))
        self.add_item(NumericalItem_int("Task duration (seconds):", task_duration_s, 1, 3600, 1))
        self.add_item(NumericalItem_int("Rest duration (seconds):", rest_duration_s, 1, 3600, 1))
        self.add_item(NumericalItem_int("Baseline duration (seconds):", baseline_duration_s, 1, 3600, 1))
        self.add_item(NumericalItem_int("Jitter duration (seconds):", jitter_s, 0, 360, 1))
        self.add_item(NumericalItem_int("Data input type (0 = beta's, 1 = t-values):", data_input_type, 0, 1, 1))
        self.add_item(NumericalItem_float("Neurofeedback threshold:", neurofeedback_threshold, 0, 10, 0.1))
        print("Neurofeedback threshold = " + str(neurofeedback_threshold))
        self.add_item(NumericalItem_int("Duration datawindow after task ends (seconds):", datawindow_duration_after_task_end_s, 0, 60, 1))
        self.add_item(NumericalItem_int("Duration datawindow before task ends (seconds):", datawindow_duration_before_task_end_s, 0, 60, 1))
        self.add_item(ToggleItem("Debugging:", debugging))

    def add_item(self, item: MenuItem):
        self.location = self.location
        base_x = self.SCREEN_WIDTH / 3.5
        base_y = self.SCREEN_HEIGHT / 3
        offset_y = len(self.items) * 34  # 50 pixels between items
        item.location = (base_x, base_y + offset_y)
        self.items.append(item)
        return item


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
        self.font = pygame.font.SysFont('ariel', 26, bold=True, )
        self.surface = self.font.render(self.text, True, WHITE)
        self.value = value

    def value_text(self):
        """You can override this in subclasses; return a string or None if no value."""
        return None

    def change_settings_file(self, parameter, value):
        with open("GameSettings.json") as f:
            settings = json.load(f)  # Open settings file (json)
            # update and save back
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


class NumericalItem(MenuItem):
    def __init__(self, text, value=0, minimum=None, maximum=None, step=1):
        super().__init__(text, int(value))
        self.value = int(value)
        self.min = minimum
        self.max = maximum
        self.step = step

    def increase(self):
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

    def decrease(self):
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

    def value_text(self):  # Return the numerical value as a string.
        return str(self.value)


class settingsMain():
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams):
        super(settingsMain, self).__init__()
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.font = pygame.font.SysFont('ariel', 35, bold=True, )
        self.settingsFont = pygame.font.SysFont('ariel', 26, bold=True, )
        self.text_item = "Select: UP/DOWN:        Change: LEFT/RIGHT:        Back: ESC"
        self.instructions = self.settingsFont.render(self.text_item, True, PINK)
        self.location = (SCREEN_WIDTH / 3.2, SCREEN_HEIGHT / 4)
        self.gameParams = gameParams
        self.selected_index = 0  # For which item is selected.
        self.items = []

        # Add new menu items here.
        self.add_item(NumericalItem("Number of trials: ", 5, 1, 100, 1))
        self.add_item(ToggleItem("Fullscreen:", "OFF",))
        self.add_item(NumericalItem("Task duration (seconds):", 5, 1, 3600, 1))
        self.add_item(NumericalItem("Rest duration (seconds):", 5, 1, 3600, 1))
        self.add_item(NumericalItem("Baseline duration (seconds):", 5, 1, 3600, 1))
        self.add_item(ToggleItem("Debugging:", False))

    def add_item(self, item: MenuItem):
        self.location = self.location
        base_x = self.SCREEN_WIDTH / 3.5
        base_y = self.SCREEN_HEIGHT / 3
        offset_y = len(self.items) * 50  # 50 pixels between items
        item.location = (base_x, base_y + offset_y)
        self.items.append(item)
        return item

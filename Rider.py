import pygame, random

# Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

class Rider(pygame.sprite.Sprite):
    def __init__(self, mount, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams, soundSystem):
        pygame.sprite.Sprite.__init__(self)
        self.rider_folder = "Resources/Riders/Graverobber/"
        self.surf = pygame.image.load(self.rider_folder + "Walk1.png").convert()
        self.rect = self.surf.get_rect()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.RiderAnimation = 0

        self.y_position_rider = 0
        self.mount = mount
        self.y_position_rider = mount.lowerLimitYpositionPlayer - 20

    def prepareRiderImage(self,mount):
        self.mount = mount
        self.y_position_rider = mount.lowerLimitYpositionPlayer - 20
    def update(self):
        self.rect.centerx = self.mount.rect.centerx  # Update rider's x position
        self.rect.centery = self.mount.rect.centery - 20  # Update rider's y position (adjust as needed)


    def RiderAnimation(self):
        if self.RiderAnimation == 0:
            self.surf = pygame.image.load(self.rider_folder + "Walk1.png").convert()
        elif self.RiderAnimation == 1:
            self.surf = pygame.image.load(self.rider_folder + "Walk2.png").convert()
        elif self.RiderAnimation == 2:
            self.surf = pygame.image.load(self.rider_folder + "Walk3.png").convert()
        elif self.RiderAnimation == 3:
            self.surf = pygame.image.load(self.rider_folder + "Walk4.png").convert()
        elif self.RiderAnimation == 4:
            self.surf = pygame.image.load(self.rider_folder + "Walk5.png").convert()
        elif self.RiderAnimation == 5:
            self.surf = pygame.image.load(self.rider_folder + "Walk6.png").convert()

        self.rider_surf.set_colorkey((0, 0, 0), RLEACCEL)

        self.RiderAnimation = self.RiderAnimation + 1
        if self.RiderAnimation > 5:  # Reset animation
            self.RiderAnimation = 0


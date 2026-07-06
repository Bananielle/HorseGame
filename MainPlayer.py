import pygame, math

# Import pygame.locals for easier access to key coordinates. Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class MainPlayer(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, gameParams, soundSystem, mounttype):
        super(MainPlayer, self).__init__()
        self.borderOfPathForHorse = None
        self.rect = None
        self.startingPosition_x = None
        self.lowerLimitYpositionPlayer = None
        self.imageScaleFactor = None
        self.gp = gameParams
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.MountType = mounttype

        # Let the mount type be determined by based on what the player choose in the starting screen.

        if self.MountType == 'horse':
            self.mount_folder = "Resources/Horse/"
        elif self.MountType == 'turtle':
            self.mount_folder = "Resources/Turtle/"
        elif self.MountType == 'camel':
            self.mount_folder = "Resources/Camel/"
        elif self.MountType == 'bear':
            self.mount_folder = "Resources/Bear/"

        # Preload the animal animation images for running
        self.animal_images_walking = [pygame.image.load(self.mount_folder + 'Walk1.png'),
                                      pygame.image.load(self.mount_folder + 'Walk2.png'),
                                      pygame.image.load(self.mount_folder + 'Walk3.png'),
                                      pygame.image.load(self.mount_folder + 'Walk4.png'),
                                      pygame.image.load(self.mount_folder + 'Walk5.png'),
                                      pygame.image.load(self.mount_folder + 'Walk6.png')]
        for image in self.animal_images_walking:
            image.convert()
            # image.set_colorkey((0,0,0))  #pygame.RLEACCEL in the set_colorkey() method instructs pygame to process [compile] the resulting image taking into account the transparency color so that it will be blitted faster in the future.

        self.surf = self.animal_images_walking[0]  # Starter image

        self.taskPeriod_dot = False

        self.scaleImage()

        self.lowerLimitYpositionPlayer = self.SCREEN_HEIGHT - (self.SCREEN_HEIGHT / 10)
        self.startingPosition_x = 280
        self.rect = self.surf.get_rect(center=(self.startingPosition_x, self.lowerLimitYpositionPlayer))
        self.borderOfPathForHorse = self.lowerLimitYpositionPlayer
        self.rect.bottom = self.borderOfPathForHorse  # To make sure the horse is in the correct y position ( on the path)

        # print(' Width player: ', self.rect.width, ' Height player: ', self.rect.height)

        self.soundSystem = soundSystem
        self.playerSpeed_base = 1250.0
        self.playerSpeed = self.playerSpeed_base
        self.RidingAnimation = 0
        self.JumpingAnimation = 0
        self.HorseIsJumping = False
        self.HorseIsJumpingUp = False
        self.HorseIsJumpingDown = False

        # Physics jump state
        self.jump_initialized = False
        self.jump_start_ticks = 0  # pygame.time.get_ticks() at jump start
        self.jump_start_centerx = 0
        self.jump_start_centery = 0
        self.jump_vx = 0.0  # horizontal velocity (px/s)
        self.jump_vy0 = 0.0  # initial vertical velocity (px/s, negative = upward)
        self.jump_g = 0.0  # gravity (px/s², positive = downward)
        self.jump_flight_duration = 0.0  # total arc duration (seconds)

    def updateDotColour_green(self):
        self.taskPeriod_dot = True

    def updateDotColour_grey(self):
        self.taskPeriod_dot = False

    # Makes sure that each image, be that horse, turtle, camel or bear, is scaled to the exact same size, so that
    # when it jumps, the exact same jump height is achieved across all animals and the same amount of coins is always collected.
    def scaleImage(self):
        self.animal_height = self.SCREEN_HEIGHT / 4  # 3.5 # Mac,  Or hardcoded: 192
        self.animal_width = (self.SCREEN_WIDTH / 10)  # 6.5) - 30, Mac # Or hardcoded: 125
        self.surf = pygame.transform.scale(self.surf, (int(self.animal_height), int(self.animal_width)))
        # print("Size of animal image: ", self.surf.get_width(), ",", self.surf.get_height())

    def setPlayerSpeed(self):
        self.playerSpeed = self.playerSpeed_base * float(self.gp.velocity)

    def ridingHorseAnimation(self):

        if self.gp.boringMode:
            self.mount_folder = "Resources/Dot/"
            if self.taskPeriod_dot:
                self.surf = pygame.image.load(self.mount_folder + 'dot_green.png')
                # Else it will stick to a grey dot
            else:
                self.surf = pygame.image.load(self.mount_folder + 'dot_grey.png')

            # Scale image
            self.scaleImage()
        else:

            if self.RidingAnimation == 0:
                self.surf = self.animal_images_walking[0]
            elif self.RidingAnimation == 1:
                self.surf = self.animal_images_walking[1]
            elif self.RidingAnimation == 2:
                self.surf = self.animal_images_walking[2]
            elif self.RidingAnimation == 3:
                self.surf = self.animal_images_walking[3]
            elif self.RidingAnimation == 4:
                self.surf = self.animal_images_walking[4]
            elif self.RidingAnimation == 5:
                self.surf = self.animal_images_walking[5]

            self.scaleImage()

            self.RidingAnimation = self.RidingAnimation + 1
            if self.RidingAnimation > 5:  # Reset animation
                self.RidingAnimation = 0

    # Move the sprite based on keypresses
    def update(self, pressed_keys, brainKeyPress, useBCIinput):

        if pressed_keys[K_UP]:
            self.HorseIsJumping = True
            self.HorseIsJumpingUp = True

        # Actual keyboard presses
        if pressed_keys[K_UP]:
            self.moveUp()
        if pressed_keys[K_DOWN]:
            self.moveDown()
        if pressed_keys[K_LEFT]:
            self.moveLeft()
        if pressed_keys[K_RIGHT]:
            self.moveRight()

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.SCREEN_WIDTH:
            self.rect.right = self.SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        # elif self.rect.bottom >= self.SCREEN_HEIGHT:
        #    self.rect.bottom = self.SCREEN_HEIGHT

        # Keep horse on the path
        self.keepHorseOnPath()

    def keepHorseOnPath(self):
        if self.rect.bottom >= self.borderOfPathForHorse:
            # print("Horse being kept on path")
            # self.rect.bottom = self.borderOfPathForHorse
            self.rect.move_ip(0,
                              -5 * self.gp.get_deltaTime())  # Gently move horse up (instead of instantly changing horse to new position, which can create weird distortions)

    def calculate_jump_position(self, achieved_NF_level):
        """
        Calculate jump position based on achieved neurofeedback level.
        The jump height is directly proportional to the number of coins that should be collected.

        Args:
            achieved_NF_level: Neurofeedback performance (0.0 to 1.0)

        Returns:
            int: Y-position for the jump peak (lower values = higher jumps)
        """
        return self._calculate_jump_position_from_nf(achieved_NF_level)

    def _calculate_jump_position_from_nf(self, achieved_NF_level):
        """
        Internal method to calculate jump position from NF level.
        """
        # Clamp NF level to valid range
        achieved_NF_level = max(0.0, min(1.0, achieved_NF_level))

        # Calculate the number of coins that should be collected (same logic as GameParameters)
        coins = round(achieved_NF_level * 10)
        if coins < self.gp.minimal_nr_of_coins:
            coins = self.gp.minimal_nr_of_coins

        return self._calculate_jump_position_from_coins(coins)

    def _calculate_jump_position_from_coins(self, coins):
        """
        Calculate jump position directly from number of coins.
        This creates a direct, understandable relationship between coins and jump height.
        The jump height is precisely calculated to ensure the horse can reach exactly
        the number of coins specified.

        Args:
            coins: Number of coins to be collected

        Returns:
            int: Y-position for the jump peak
        """
        # Get the coin positions to ensure our jump height matches exactly
        # This creates a consistent 1:1 relationship between jump height and coins collected
        coin_positions = self._get_coin_positions()

        if coin_positions and len(coin_positions) > 0:
            # Sort descending so index 0 = lowest coin on screen (largest y = closest to ground = easiest to reach)
            # Coin rank 1 = lowest coin (easiest to reach), rank 10 = highest coin (hardest to reach)
            coin_positions.sort(reverse=True)  # Now [492, 442, ..., 42] - lowest to highest on screen

            # Ensure we don't try to access more coins than exist
            coins = min(coins, len(coin_positions))

            if coins == 0:
                return int(self.borderOfPathForHorse)  # No jump: stay at ground level

            # The jump height should reach the position of the coin with rank = coins
            # Coin ranks: 1 = lowest coin (easiest), 10 = highest coin (hardest)
            target_coin_index = coins - 1  # Convert to 0-based index (always >= 0 here)

            if target_coin_index < len(coin_positions):
                # Jump to just above the target coin position
                target_position = coin_positions[target_coin_index]
                # Add a small offset to ensure the horse clears the coin
                jump_position = int(target_position - (self.rect.height * 0.5))
                return max(jump_position, 1)  # Clamp so target is always reachable (never above screen)

        # Fallback to the original calculation if no coins are positioned yet
        # Map coins to jump height using a direct proportional relationship
        # More intuitive: fewer coins = lower jump (easier), more coins = higher jump (harder)
        if coins == 0:
            return int(self.borderOfPathForHorse)  # No jump: stay at ground level

        min_coins = self.gp.minimal_nr_of_coins
        max_coins = self.gp.totalNumCoins

        # Normalize coin count to [0, 1] range
        normalized_coins = (coins - min_coins) / (max_coins - min_coins)

        # Calculate jump position as fraction of screen height
        # Fewer coins = lower jump (higher y-position, easier)
        # More coins = higher jump (lower y-position, harder)
        min_jump_fraction = 0.75  # 75% from top (for minimum coins - easiest)
        max_jump_fraction = 0.25  # 25% from top (for maximum coins - hardest)
        jump_fraction = min_jump_fraction - (min_jump_fraction - max_jump_fraction) * normalized_coins

        # Convert to pixel position
        jump_position = int(self.SCREEN_HEIGHT * jump_fraction)

        return jump_position

    def _get_coin_positions(self):
        """
        Get the current y-positions of all coins.

        Returns:
            list: List of coin y-positions, sorted from top to bottom
        """
        coin_positions = []
        if hasattr(self.gp, 'coin') and self.gp.coin:
            for coin in self.gp.coin:
                coin_positions.append(coin.rect.centery)
        return coin_positions

    def get_jump_height_for_coin_count(self, coins):
        """
        Get the jump height for a specific coin count (for visualization/debugging).

        Args:
            coins: Number of coins

        Returns:
            int: Jump height in pixels
        """
        return self._calculate_jump_position_from_coins(coins)

    def performJumpSequence(self, NF_level_reached):
        maxJumpHeightAchieved = self.calculate_jump_position(NF_level_reached)

        if self.HorseIsJumping:
            self.gp.horseHasJumpedThisTrial = True
            if not self.jump_initialized:
                self._init_parametric_jump(NF_level_reached)
            if self._update_parametric_jump():
                self._land_horse()
        else:
            self.ridingHorseAnimation()
            if self.rect.centerx > self.startingPosition_x:
                self.moveLeft()
                if self.rect.centerx < self.startingPosition_x:
                    self.rect.centerx = self.startingPosition_x

        return maxJumpHeightAchieved

    # ── Parametric jump helpers ────────────────────────────────────────────────

    def _init_parametric_jump(self, NF_level_reached):
        """Calculate and store physics arc parameters at the moment the jump starts."""
        peak_top = self.calculate_jump_position(NF_level_reached)
        ground_centery = self.borderOfPathForHorse - self.rect.height / 2
        peak_centery = peak_top + self.rect.height / 2
        peak_height = max(ground_centery - peak_centery, 10)  # px above ground

        # Horizontal: horse right edge reaches the coin column during the arc
        coin_col_left = int(self.SCREEN_WIDTH / 1.6)
        h_dist = coin_col_left - self.rect.right + self.rect.width

        self.jump_start_centerx = self.rect.centerx
        self.jump_start_centery = ground_centery

        g = 800.0  # gravity (px/s²)
        vy0 = math.sqrt(2 * g * peak_height)  # initial upward speed (px/s)
        flight_time = 2 * vy0 / g

        self.jump_vy0 = -vy0  # negative = upward in screen coords
        self.jump_g = g
        self.jump_vx = max(h_dist / flight_time, 50.0)
        self.jump_flight_duration = flight_time
        self.jump_start_ticks = pygame.time.get_ticks()
        self.jump_initialized = True
        self.HorseIsJumpingUp = True
        self.HorseIsJumpingDown = False

    def _update_parametric_jump(self):
        """Move the horse along the physics arc and animate. Returns True when landed."""
        t = (pygame.time.get_ticks() - self.jump_start_ticks) / 1000.0
        t = min(t, self.jump_flight_duration)

        new_cx = self.jump_start_centerx + self.jump_vx * t
        new_cy = self.jump_start_centery + self.jump_vy0 * t + 0.5 * self.jump_g * t * t
        vy_now = self.jump_vy0 + self.jump_g * t

        self.rect.centerx = int(new_cx)
        self.rect.centery = int(new_cy)
        self.HorseIsJumpingUp = vy_now < 0
        self.HorseIsJumpingDown = not self.HorseIsJumpingUp

        if self.HorseIsJumpingUp:
            self.jumpUp(move_position=False)
        else:
            self.jumpDown(move_position=False)

        # Time-based landing: the physics formula returns the horse exactly to
        # ground_centery at t == flight_duration, so no rect.bottom check needed.
        landed = t >= self.jump_flight_duration
        if landed:
            self.rect.bottom = int(self.borderOfPathForHorse)
        return landed

    def _land_horse(self):
        """Shared landing logic for all jump styles."""
        self.HorseIsJumping = False
        self.HorseIsJumpingUp = False
        self.HorseIsJumpingDown = False
        self.jump_initialized = False
        self.gp.freezeCoins = False
        self.gp.horseJumpEvent = False
        self.gp.startCountingCoins()  # Log the trial at landing, even if 0 coins were collected — otherwise the trial is silently dropped from the run mean/sum
        self.rect.bottom = int(self.borderOfPathForHorse)
        # Don't snap centerx — the idle branch trots the horse back gradually.
        print(f"T= {self.gp.currentTime_s}: Horse landed successfully")

    def jumpUp(self, move_position=True):
        if self.gp.boringMode:
            if move_position:
                self.moveUp()
                self.moveRight()
            self.scaleImage()
        else:
            if self.RidingAnimation == 0:
                self.surf = self.animal_images_walking[0]
            elif self.RidingAnimation == 1:
                self.surf = self.animal_images_walking[1]
            elif self.RidingAnimation == 2:
                self.surf = self.animal_images_walking[1]
            elif self.RidingAnimation == 3:
                self.surf = self.animal_images_walking[2]
            elif self.RidingAnimation == 4:
                self.surf = self.animal_images_walking[2]
            elif self.RidingAnimation == 5:
                self.surf = self.animal_images_walking[3]
            elif self.RidingAnimation == 6:
                self.surf = self.animal_images_walking[4]
            elif self.RidingAnimation == 7:
                self.surf = self.animal_images_walking[5]

            if move_position:
                self.moveUp()
                self.moveRight()
            self.scaleImage()

            self.RidingAnimation = self.RidingAnimation + 1
            if self.RidingAnimation > 4:
                self.RidingAnimation = 4

    def jumpDown(self, move_position=True):
        if self.gp.boringMode:
            if move_position:
                self.moveDown()
                self.moveRight()
            self.scaleImage()
        else:
            if self.RidingAnimation == 0:
                self.surf = self.animal_images_walking[3]
            elif self.RidingAnimation == 1:
                self.surf = self.animal_images_walking[3]
            elif self.RidingAnimation == 2:
                self.surf = self.animal_images_walking[4]
            elif self.RidingAnimation == 3:
                self.surf = self.animal_images_walking[4]
            elif self.RidingAnimation == 4:
                self.surf = self.animal_images_walking[4]
            elif self.RidingAnimation == 5:
                self.surf = self.animal_images_walking[5]
            elif self.RidingAnimation == 6:
                self.surf = self.animal_images_walking[5]
            elif self.RidingAnimation == 7:
                self.surf = self.animal_images_walking[5]

            if move_position:
                self.moveDown()
                self.moveRight()
            self.scaleImage()

            self.RidingAnimation = self.RidingAnimation + 1
            if self.RidingAnimation > 7:
                self.RidingAnimation = 0

    def moveUp(self):
        self.rect.move_ip(0, (self.playerSpeed * -1) * self.gp.get_deltaTime())

    # print('Moving up.')
    # self.soundSystem.playBubbleSound(self.soundSystem.move_up_sound)

    def moveDown(self):
        # if self.rect.bottom + self.playerSpeed >= self.borderOfPathForHorse:
        #    print("Bottom horse = " + str(self.rect.bottom), " ,borderOfPathForHorse = " + str(self.borderOfPathForHorse))
        #    # print("Horse being kept on path")
        #    move_by = self.borderOfPathForHorse - self.rect.bottom +10
        #    self.rect.move_ip(0,move_by)
        # else:
        self.rect.move_ip(0, (self.playerSpeed - 1) * self.gp.get_deltaTime())

    #  print('Moving down.')
    # self.soundSystem.playBubbleSound(self.soundSystem.move_down_sound)

    def moveLeft(self):
        self.rect.move_ip((self.playerSpeed * -1) * self.gp.get_deltaTime(), 0)

    #  print('Moving left.')

    def moveRight(self):
        self.rect.move_ip(self.playerSpeed * self.gp.get_deltaTime(), 0)
        # print('Moving right.')


import os, simpleaudio
from pygame import mixer  # Only use this one for the main theme


# Use a different module for sounds, because the pygame soundsystem didn't work together with  python 2.7.5.
# (which was needed for exypriment...)

USE_BACKGROUND_MUSIC = False # toggles the background music on/off (note, the background music makes use of the pygame mixer)

# Set up the sounds
class SoundSystem():
    def __init__(self):

        #  self.collision_sound = pygame.mixer.Sound("Collision.ogg")
        self.coin_sound = simpleaudio.WaveObject.from_wave_file("Resources/collectedJellyfish.wav")
        self.coinCollected = simpleaudio.WaveObject.from_wave_file("Resources/coin.wav")
        self.countdownSound = simpleaudio.WaveObject.from_wave_file("Resources/countdown.wav")
        self.menuSelection = simpleaudio.WaveObject.from_wave_file("Resources/menu_selection.wav")
        # self.maintheme_slow = simpleaudio.WaveObject.from_wave_file("Resources/maintheme_slow.wav")
        # self.maintheme_fast = simpleaudio.WaveObject.from_wave_file("Resources/maintheme_fast.wav")
        self.drum = simpleaudio.WaveObject.from_wave_file("Resources/drum.wav")
        self.galop = simpleaudio.WaveObject.from_wave_file("Resources/galop.wav")
        self.turtle_run = simpleaudio.WaveObject.from_wave_file("Resources/turtle_run.wav")
        self.horse_snort = simpleaudio.WaveObject.from_wave_file("Resources/horse_snort.wav")
        self.horse_cry = simpleaudio.WaveObject.from_wave_file("Resources/horse_cry.wav")


       # self.playingBubbleSound = self.move_up_sound.play()
        self.playedStartScreenSound =False

        if USE_BACKGROUND_MUSIC:
            # Pygame mixer
            mixer.init()
            self.channel1 = mixer.Channel(0)
            self.maintheme_slow = mixer.Sound("Resources/maintheme_slow.wav")
            self.maintheme_slow.set_volume(0.3)
            self.maintheme_slowIsPlaying = False

            self.channel2 = mixer.Channel(1)
            self.maintheme_fast = mixer.Sound("Resources/maintheme_fast.wav")
            self.maintheme_fast.set_volume(0.3)

            self.channel3 = mixer.Channel(2)
            self.gameoverSound = mixer.Sound("Resources/gameoverSound.wav")

            self.channel4 = mixer.Channel(3)
            self.maintheme_gameover = mixer.Sound("Resources/maintheme_gameover.wav")
            self.maintheme_gameover.set_volume(0.3)

            self.gameoverSoundIsPlaying = False
            self.gameoverThemeIsPlaying = False

  #  def playStartScreenSound(self):
   ###       self.playedStartScreenSound = True

    # The bubble sound sounds terrible if they overlap,  first check whether something else is playing. Otherwise you can play the sound
   # def playBubbleSound(self, sound):
    ##       self.playingBubbleSound = 1 #sound.play()

    def playMaintheme_slow(self):
        if USE_BACKGROUND_MUSIC:
            if not self.maintheme_slowIsPlaying:
                self.channel3.fadeout(0)  # incase game over theme was still playing
                self.channel1.play(self.maintheme_slow)
                self.maintheme_slowIsPlaying = True

    def speedupMaintheme(self):
        if USE_BACKGROUND_MUSIC:
            self.channel2.play(self.maintheme_fast)
            self.channel1.fadeout(1400)

    def fadeIntoGameOverMusicTheme(self):
        if USE_BACKGROUND_MUSIC:
            if not self.gameoverSoundIsPlaying:
                self.channel1.fadeout(1400)  # incase slow main theme is still playing
                self.channel2.fadeout(1400)
                self.channel3.play(self.gameoverSound)
                self.gameoverSoundIsPlaying = True
            if not self.gameoverThemeIsPlaying:
                if not mixer.Channel(2).get_busy():
                    self.channel4.play(self.maintheme_gameover)
                    self.gameoverThemeIsPlaying = True

    def stopGameOverMusicTheme(self):
        if USE_BACKGROUND_MUSIC:
            self.channel4.fadeout(0)
            self.gameoverThemeIsPlaying = False
            self.gameoverSoundIsPlaying = False
            self.maintheme_slowIsPlaying = False

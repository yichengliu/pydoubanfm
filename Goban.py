import pygame, time

# set up the mixer
#freq = 44100     # audio CD quality
#bitsize = 16    # unsigned 16 bit
#channels = 2     # 1 is mono, 2 is stereo
#buffer = 4096    # number of samples (experiment to get right sound)
#pygame.mixer.init(freq, bitsize, channels, buffer)
pygame.mixer.init()
#pygame.init()

# optional volume 0 to 1.0
#pygame.mixer.music.set_volume(0.75)

pygame.mixer.music.load('/tmp/a.mp3')
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
	time.sleep(0.1)

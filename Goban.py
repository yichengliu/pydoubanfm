import pygame
import urllib2
import urllib
import json
import time
import locale
import codecs
import threading
import sys
import os
import termios

empty = threading.Semaphore(5)
full = threading.Semaphore(0)
queue = []

TERMIOS = termios
def getch():
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
	new[6][TERMIOS.VMIN] = 1
	new[6][TERMIOS.VTIME] = 0
	termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
	c = None
	try:
		c = os.read(fd, 1)
	finally:
		termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
	return c

def Output(s):
	sys.stdout.write(s + ' ' * (70 - len(s)))
	sys.stdout.flush()

def ClearLine():
	sys.stdout.write('\r')
	sys.stdout.flush()

def play(filename):
	pygame.mixer.music.load(filename)
	pygame.mixer.music.play()

	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)

def showDownloadProcess(blocks, block_size, total_size):
	percent = 30.0 * blocks * block_size / total_size

	percent = int(percent)

	if percent > 30:
		percent = 30
	
	#ClearLine()
	#Output('[' + '=' * percent + '>' * (1 if percent < 30 else 0) + ' ' * (29 - percent) + ']' + '   ' + ('Downloading' if percent < 30 else 'Done'))

def play_worker():
	try:
		while True:
			full.acquire()
			song, f = queue.pop(0)

			#ClearLine()
			#Output((song['title'] + ' <<' + song['albumtitle'] + '>> -- ' + song['artist']).encode('utf_8'))
			#Output('\n')
			print((song['title'] + ' <<' + song['albumtitle'] + '>> -- ' + song['artist']).encode('utf_8'))

			play(f)
			empty.release()
	finally:
		pygame.mixer.music.stop()

def download_worker():
	try:
		while True:
			playListURL = r'http://douban.fm/j/mine/playlist?type=n'
			channelURL = r'&channel=' + str(channel)
			fromURL = r'&from=mainsite'
	
			url = playListURL + channelURL + fromURL

			page_source = urllib.urlopen(url)
			pageData = page_source.read()
			jsonData = json.loads(pageData)
			songList = jsonData['song']

			for song_info in songList:
				empty.acquire()
				filename = '/tmp/' + song_info['url'].split('/')[-1]

				f, h = urllib.urlretrieve(song_info['url'], filename, showDownloadProcess)
				queue.append((song_info, filename))
				full.release()
	finally:
		pass

locale.setlocale(locale.LC_ALL,"")
pygame.mixer.init()
volume_cache = -1

if len(sys.argv) < 2:
	print('Provide channel')
	exit()

channel = int(sys.argv[1])
print('Playing channel ' + str(channel))

player = threading.Thread(target=play_worker)
downloader = threading.Thread(target=download_worker)

player.daemon = True
downloader.daemon = True

player.start()
downloader.start()

while True:
	c = getch()

	if c == 'q':
		break

	if c == 'n':
		pygame.mixer.music.stop()

	if c == 'm':
		if volume_cache == -1:
			volume_cache = pygame.mixer.music.get_volume()
			pygame.mixer.music.set_volume(0)
		else:
			pygame.mixer.music.set_volume(volume_cache)
			volume_cache = -1

print('Bye')

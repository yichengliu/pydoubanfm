import pygame
import urllib2
import urllib
import json
import time
import curses
import locale
import codecs
import threading
import sys

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
	
	ClearLine()
	Output('[' + '=' * percent + '>' * (1 if percent < 30 else 0) + ' ' * (29 - percent) + ']' + '   ' + ('Downloading' if percent < 30 else 'Playing'))

def worker():
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

			for song in songList:
				ClearLine() #Clear privious status line
				Output((song['title'] + ' <<' + song['albumtitle'] + '>> -- ' + song['artist']).encode('utf_8'))
				Output('\n')

				donotClear = True
			
				#f, h = urllib.urlretrieve(r'http://mr4.douban.com/201210241519/0527423da2934ca66aa4c6aa00a04e69/view/song/small/p15413.mp3', '/tmp/a.mp3')
				#print(song['title'])
				f, h = urllib.urlretrieve(song['url'], '/tmp/a.mp3', showDownloadProcess)
				play(f)

	finally:
		pygame.mixer.music.stop()

locale.setlocale(locale.LC_ALL,"")
pygame.mixer.init()

if len(sys.argv) < 2:
	print('Provide channel')
	exit()

channel = int(sys.argv[1])
print('Playing channel ' + str(channel))

worker()

pygame.mixer.music.stop()

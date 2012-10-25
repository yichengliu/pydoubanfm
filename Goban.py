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

empty = threading.Semaphore(5)
full = threading.Semaphore(0)
queue = []

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

if len(sys.argv) < 2:
	print('Provide channel')
	exit()

channel = int(sys.argv[1])
print('Playing channel ' + str(channel))

threading.Thread(target=play_worker).start()
threading.Thread(target=download_worker).start()

pygame.mixer.music.stop()

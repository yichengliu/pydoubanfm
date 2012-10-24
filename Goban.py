import pygame
import urllib
import json
import time
import curses
import locale
import codecs

def play(filename):
	pygame.mixer.init()
	pygame.mixer.music.load(filename)
	pygame.mixer.music.play()

	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)

def getPlayList():
	playListURL = r'http://douban.fm/j/mine/playlist?type=n&channel=1&from=mainsite'
	channelURL = r'&channel=' + str(1)
	fromURL = r'&from=mainsite'
	
	url = playListURL + channelURL + fromURL
	
	page_source = urllib.urlopen(url)
	pageData = page_source.read()
	jsonData = json.loads(pageData)
	songList = jsonData['song']

	return songList

def showDownloadProcess(blocks, block_size, total_size):
	percent = 30.0 * blocks * block_size / total_size

	percent = int(percent)

	if percent > 30:
		percent = 30
	
	stdscr.addstr(21, 50, '[' + '=' * percent + '>' * (1 if percent < 30 else 0) + ' ' * (29 - percent) + ']' + '   ' + ('Downloading' if percent < 30 else 'Playing'))
	stdscr.refresh()


locale.setlocale(locale.LC_ALL,"")
stdscr = curses.initscr()
stdscr.border(0)

try:
	while True:
		songList = getPlayList()

		for song in songList:
			stdscr.addstr(20, 50, ' ' * 100)
			stdscr.addstr(20, 50, (song['title'] + ' <<' + song['albumtitle'] + '>> -- ' + song['artist']).encode('utf_8'))
			stdscr.refresh()
			
			#f, h = urllib.urlretrieve(r'http://mr4.douban.com/201210241519/0527423da2934ca66aa4c6aa00a04e69/view/song/small/p15413.mp3', '/tmp/a.mp3')
			#print(song['title'])
			f, h = urllib.urlretrieve(song['url'], '/tmp/a.mp3', showDownloadProcess)
			play(f)
finally:
	curses.endwin()

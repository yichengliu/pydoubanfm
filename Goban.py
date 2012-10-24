import pygame
import urllib
import json
import time
import curses
import locale
import codecs
import threading

def play(filename):
	pygame.mixer.init()
	pygame.mixer.music.load(filename)
	pygame.mixer.music.play()

	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)

def showDownloadProcess(blocks, block_size, total_size):
	percent = 30.0 * blocks * block_size / total_size

	percent = int(percent)

	if percent > 30:
		percent = 30
	
	stdscr.addstr(21, 50, ' ' * 50)
	stdscr.addstr(21, 50, '[' + '=' * percent + '>' * (1 if percent < 30 else 0) + ' ' * (29 - percent) + ']' + '   ' + ('Downloading' if percent < 30 else 'Playing'))
	stdscr.refresh()

def worker():
	try:
		while True:
			if quit==True:
				break

			cc = False

			stdscr.addstr(18, 50, ' ' * 50)
			stdscr.addstr(18, 50, 'Channel ' + str(channel))
			stdscr.refresh()

			playListURL = r'http://douban.fm/j/mine/playlist?type=n'
			channelURL = r'&channel=' + str(channel)
			fromURL = r'&from=mainsite'
	
			url = playListURL + channelURL + fromURL
	
			#stdscr.addstr(2,10, url)
			#stdscr.refresh()

			page_source = urllib.urlopen(url)
			pageData = page_source.read()
			jsonData = json.loads(pageData)
			songList = jsonData['song']

			for song in songList:
				if quit==True:
					break

				if cc==True:
					break

				stdscr.addstr(20, 50, ' ' * 50)
				stdscr.addstr(20, 50, (song['title'] + ' <<' + song['albumtitle'] + '>> -- ' + song['artist']).encode('utf_8'))
				stdscr.refresh()
			
				#f, h = urllib.urlretrieve(r'http://mr4.douban.com/201210241519/0527423da2934ca66aa4c6aa00a04e69/view/song/small/p15413.mp3', '/tmp/a.mp3')
				#print(song['title'])
				f, h = urllib.urlretrieve(song['url'], '/tmp/a.mp3', showDownloadProcess)
				play(f)
	finally:
		pass

locale.setlocale(locale.LC_ALL,"")
stdscr = curses.initscr()
stdscr.border(0)
quit = False
cc = False
channel = 1

t = threading.Thread(target=worker)
t.start()

command = -1

while command != ord('q'):
	command = stdscr.getch()

	if ord('1') <= command <= ord('5'):
		channel = command - ord('0')
		cc = True
		pygame.mixer.music.stop()

quit = True
pygame.mixer.music.stop()
curses.endwin()
print('Bye')
